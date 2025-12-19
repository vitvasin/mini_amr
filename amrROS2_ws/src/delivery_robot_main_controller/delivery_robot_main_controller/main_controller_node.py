import rclpy
from rclpy.node import Node
from enum import Enum, auto
from geometry_msgs.msg import PoseStamped, Vector3
from .robot_navigator import BasicNavigator, NavigationResult
from rclpy.duration import Duration
from rclpy.action import ActionClient
from custom_interface.action import Autodock
from std_srvs.srv import SetBool
from .generate_agv_path_from_building_yaml import compute_path_poses
import tf2_ros
import tf2_geometry_msgs 

from std_msgs.msg import String, Int16, Int8
from math import degrees, hypot, radians


from tf_transformations import euler_from_quaternion, quaternion_from_euler, quaternion_multiply
import time
#import requests
import json

from sensor_msgs.msg import BatteryState

from . import api_client

import signal
from .rpc_server import RPCServer
from .rpc_fnc import door_command, echo, dock_command_service, configure_rpc_access, process_rpc_requests

TaskResult = NavigationResult

FUNCS = {
    "door_command": door_command,
    "echo": echo,
    "dock_command": dock_command_service
}


class RobotState(Enum):
    NONE = auto()
    STANDBY = auto()
    MOVE = auto()
    AFTER_MOVE = auto()
    LOAD_IN = auto()
    LOAD_OUT = auto()
    WAIT_LOAD_OUT = auto()
    DOCK = auto()
    MANUAL = auto()

class DockState(Enum):
    IDLE = auto()
    DOCKING = auto()
    DOCKED = auto()
    UNDOCKING = auto()

class ChargeState(Enum):
    NOT_CHARGE = auto()
    CHARGING = auto()


class DeliveryRobotMainController(Node):
    def __init__(self):
        super().__init__('delivery_robot_main_controller')
        self.get_logger().info("Delivery Robot Main Controller Node started.")
        configure_rpc_access(self)
        # Pump RPC service queue so RPC calls can trigger ROS service clients
        self.create_timer(0.05, process_rpc_requests)
        self._should_dock = False #สำหรับเรียกเข้า dock และ undock แบบ manual
        self._should_undock = False
        self.current_pose = PoseStamped()
        self.current_speed = 0.0
        self._path_tracking = None
        self._waypoint_tolerance = 0.3
        self.manual_nav_target = Vector3()
        self.manual_nav_go_state = 0
        self.manual_x = None
        self.manual_y = None
        self.manual_yaw = None
        self._manual_monitor_timer = None
        self.toggle_manual = False
        
        #self.get_logger().info(f"Initial state: {RobotState.MOVE}")
        #api_client.update_robot_status((RobotState.MOVE).name)
        #return
        # Initialize robot state
        self.state = RobotState.STANDBY
        try:
            api_client.update_robot_status(self.state.name)
        except Exception as e:
            self.get_logger().error(f'Failed to update robot status: {e}')

        self.dockstate = DockState.IDLE
        self.chargestate = ChargeState.NOT_CHARGE
        self.target_station = ""
        self.current_station = None
        self.current_task = None
        self.retry_move_no = 0
        self.status_id = None
        self.load_out_loop_counter = 0

        self.get_logger().info(f"Initial state: {self.state.name}")

        self._cached_system_parameters = None
        self._system_param_poll_interval = 5.0  # seconds
        self.get_system_parameters_from_api(report_changes=False)
        self._system_param_poll_timer = self.create_timer(
            self._system_param_poll_interval, self.poll_system_parameters
        )

        # Example publisher (placeholder for /cmd_vel or similar)
        # self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Example timer to periodically print state (can remove later)
        self.batt_percentage = 80  # battery state of charge
        self._last_activity_time = self.get_clock().now()

        # Subscribe to /ir_charge_state topic
        self.create_subscription(
            Int16,
            "ir_charge_state",
            self.charge_state_callback,
            2
        )
        # Subscribe to /battery topic
        self.create_subscription(
            BatteryState,
            "battery",
            self.battery_callback,
            1
        )
        self.create_subscription(
            Vector3,
            "manual_nav/setpoint",
            self.manual_nav_setpoint_callback,
            10
        )
        self.create_subscription(
            Int8,
            "manual_nav/go",
            self.manual_nav_go_callback,
            10
        )
        self.create_subscription(
            String,
            "manual_nav/named_target",
            self.manual_nav_named_target_callback,
            10
        )

        self.create_subscription(
            String,
            "drive_fault_state",
            self.drive_fault_callback,
            10
        )

        self.smooth_path = True
        self.navigator = BasicNavigator()
        time.sleep(1)
        if not self.navigator.initial_pose_received:
            self.get_logger().info("Waiting for Nav2 system...")
            self.navigator.waitUntilNav2Active()

        #timer
        self.create_timer(1.0, self.state_monitor) #ตรวจสอบสถานะ state 
        self.create_timer(2.0, self.battery_status_monitor)  # update แบตเตอรี่ทุก 2 วินาที
        self.create_timer(2.0, self.on_standby_loop) #ตรวจสอบ condition ใน state standby

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.create_timer(1.0, self.get_current_robot_pose)
        
        self.autodock_client = ActionClient(self, Autodock, 'autodock')

        # Add dock_command service for external dock/undock requests
        self.dock_command_srv = self.create_service(SetBool, 'dock_command', self.handle_dock_command)

        # Add sound publisher
        self.sound_publisher = self.create_publisher(String, '/robot_sound_command', 10)
        #time.sleep(2.0)
        #self.send_goal_pose(1.0,0.0,0.0) #test
        self.on_standby()

        # TODO: Add action clients / services / subscribers as needed
    
    @staticmethod
    def _parameter_to_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip().lower() in ('1', 'true', 'yes', 'on')
        return bool(value)

    def touch_activity(self): 
        self._last_activity_time = self.get_clock().now() 
    
    def get_current_robot_pose(self):
        try:
            # Lookup the transform from 'map' to 'base_link'
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link', rclpy.time.Time()
            )
            now = self.get_clock().now()
            # Create a PoseStamped message from the transform
            current_pose = PoseStamped()
            current_pose.header.frame_id = 'map'
            current_pose.header.stamp = self.get_clock().now().to_msg()
            current_pose.pose.position.x = transform.transform.translation.x
            current_pose.pose.position.y = transform.transform.translation.y
            current_pose.pose.position.z = transform.transform.translation.z
            current_pose.pose.orientation = transform.transform.rotation
            self.current_pose =  current_pose
            #status_id = self._get_status_id_for('update robot pose')
            api_client.update_status('pose_x',current_pose.pose.position.x)
            api_client.update_status('pose_y',current_pose.pose.position.y)
            yaw = degrees(self.calculate_heading(current_pose.pose))
            api_client.update_status('pose_yaw',yaw)

             # คำนวณความเร็วเชิงเส้น (m/s)
            prev_pose = getattr(self, "_prev_pose", None)
            prev_time = getattr(self, "_prev_time", None)
            if prev_pose and prev_time:
                dt = (now - prev_time).nanoseconds / 1e9
                if dt > 0:
                    dx = current_pose.pose.position.x - prev_pose.pose.position.x
                    dy = current_pose.pose.position.y - prev_pose.pose.position.y
                    speed = (dx**2 + dy**2) ** 0.5 / dt
                    self.current_speed = speed
                    api_client.update_status('vel_x',speed)
                    #self.get_logger().info(f"Robot speed: {speed:.3f} m/s")
            
            self._prev_pose = current_pose
            self._prev_time = now
            #self.get_logger().info(f"Current Pose: x={current_pose.pose.position.x}, y={current_pose.pose.position.y}")
        except tf2_ros.TransformException as ex:
            self.get_logger().warn(f'Could not transform "base_link" to "map": {ex}')
            

    def battery_callback(self, msg: BatteryState):
        try:
            self.batt_voltage = msg.voltage
            self.batt_current = msg.current
            self.batt_temperature = msg.temperature
            self.batt_capacity = msg.capacity
            self.batt_charge = msg.charge
            self.batt_percentage = msg.percentage
            self.batt_design_capacity = msg.design_capacity
            self.batt_power_supply_status = msg.power_supply_status
            self.batt_power_supply_health = msg.power_supply_health
            self.batt_power_supply_technology = msg.power_supply_technology
            self.batt_present = self._parameter_to_bool(msg.present)
            self.battery_status_monitor()

        except Exception as e:
            self.get_logger().error(f"Battery callback exception: {e}")
    
    def charge_state_callback(self, msg: Int16):
        """Update cached charge/dock state from IR charge sensor feedback."""
        try:
            charge_code = int(msg.data)
            if charge_code == 11:
                self.chargestate = ChargeState.CHARGING
            else:
                self.chargestate = ChargeState.NOT_CHARGE
            api_client.update_status('charge_state',self.chargestate.name)
            
            if (self.dockstate != DockState.DOCKED)and(charge_code in (10, 11)):
                self.change_dock_state(DockState.DOCKED)
               

        except Exception as e:
            self.get_logger().error(f"ChargeState callback exception: {e}")

    def manual_nav_named_target_callback(self, msg: String):
        station_name = msg.data.strip()
        if not station_name:
            self.get_logger().warn("Manual navigation target received with empty station name.")
            return
        self.touch_activity()
        self.target_station = station_name
        x, y, heading = self.get_station_position(station_name)
        if x is None or y is None or heading is None:
            self.manual_x = None
            self.manual_y = None
            self.manual_yaw = None
            self.get_logger().warn(f"Manual navigation station '{station_name}' not found.")
            return
        self.manual_x = float(x)
        self.manual_y = float(y)
        self.manual_yaw = radians(float(heading))
        self.get_logger().info(
            f"Manual navigation target '{station_name}' resolved to x={self.manual_x:.3f}, "
            f"y={self.manual_y:.3f}, yaw={self.manual_yaw:.3f} rad"
        )

    def manual_nav_setpoint_callback(self, msg: Vector3):
        self.manual_nav_target = msg
        self.manual_x = float(msg.x)
        self.manual_y = float(msg.y)
        self.manual_yaw = float(msg.z)
        self.touch_activity()
        self.get_logger().info(
            f"Manual navigation setpoint updated: x={self.manual_x:.3f}, "
            f"y={self.manual_y:.3f}, yaw={self.manual_yaw:.3f}"
        )

    def manual_nav_go_callback(self, msg: Int8):
        command = int(msg.data)
        self.manual_nav_go_state = command
        self.touch_activity()
        self.get_logger().info(f"Manual navigation go command received: {command}")
        if command <= 0:
            self.get_logger().info("Manual navigation go command ignored because value <= 0.")
            return
        if self.manual_x is None or self.manual_y is None or self.manual_yaw is None:
            self.get_logger().warn("Manual navigation go command received without a valid target pose.")
            return
        self.send_goal_pose_agv(self.manual_x, self.manual_y, self.manual_yaw, RobotState.MANUAL)

    def drive_fault_callback(self, msg: String):
        drive_status = msg.data.strip()
        old_drive_status = api_client.get_robot_status_by_name('is_derive_fault')
        
        if drive_status != old_drive_status:
            if drive_status == 'No Fault':
                api_client.update_status("is_derive_fault", 0)
            else:
                api_client.update_status("is_derive_fault", 1)

        if drive_status != 'No Fault': 
                self.get_logger().info(
                    f"Drive Status Fault = {drive_str}"   
                )    

    def state_monitor(self):
        # Periodic task to monitor or report state
        self.get_robot_status_from_api()
        self.get_logger().info(f"Current state: {self.state.name}, dock_state {self.dockstate.name}, charge_state {self.chargestate.name}")

    def get_state_from_api(self):
        try:
            #params = api_client.get_robot_status()
            state_value = api_client.get_robot_status_by_name('status')
            state = getattr(RobotState, state_value, RobotState.STANDBY)
            if state == RobotState.MANUAL:
                    self.toggle_manual = True
            else:
                    self.toggle_manual = False
            return state
            #data = params.get("data", [])
            # ใช้ข้อมูล เช่น:
            #if data and isinstance(data, list):
            #    current_status = data[0]
            #    status_id = current_status.get("_id") or current_status.get("id")
            #    if status_id:
            #        self.status_id = status_id
            #    state_value = current_status.get("status", "")
            
                # ถ้า state เป็น dict เช่น {"name": "STANDBY"} ให้ดึงชื่อออกมา
            #if isinstance(state_value, dict):
            #    state_str = state_value.get("status", "")
            #    else:
            #        state_str = state_value

            #    state = getattr(RobotState, state_str, RobotState.STANDBY)
            #    return state
            #else:
            #    self.get_logger().warn("Invalid system current status format: 'data' is empty or not a list")
            #    return None
        
        except Exception as e:
            self.get_logger().error(f"current status API request failed: {e}")
            return None

    def get_robot_status_from_api(self):
        try:
            #url = 'http://localhost:8080/api/robotstatus/list'  # URL ของ API ที่เชื่อมกับ SQLite
            #response = requests.get(url, timeout=5)
            #response.raise_for_status()
            #params = response.json()
            #data = params.get("data", [])
            #self.get_logger().info(f"Received task data: {data}")
            params = api_client.get_robot_status()
            data = params.get("data", [])
            # ใช้ข้อมูล เช่น:
            if data and isinstance(data, list):
                current_status = data[0]
                state_str = current_status.get("status", "STANDBY")
                state = getattr(RobotState, state_str, RobotState.STANDBY)
               # if state == RobotState.MANUAL:
               #     self.toggle_manual = True
               # else:
               #     self.toggle_manual = False
                #self.change_state(state)
                status_id = current_status.get('_id') or current_status.get('id')
                if status_id:
                    self.status_id = status_id
                else:
                    self.get_logger().warn('Robot status id missing from API response.')

                current_station = current_status.get('current_station')
                if isinstance(current_station, dict):
                    current_station = current_station.get('value') or current_station.get('name')
                if current_station:
                    self.current_station = current_station
                
                #test_param = api_client.get_robot_status_by_name('dock_state')
                #self.get_logger().info(f"dock_state = {test_param}")
                #self.target_station = current_status.get('target_station','')
                #self.dock_state = current_status.get('dock_state','')
                #self.charge_state = current_status.get('charge_state','Not Charge')
                #self.pose_x = current_status.get('pose_x', 0.0)
                #self.pose_y = current_status.get('pose_y',0.0)
                #self.pose_yaw = current_status.get('pose_yaw', 0.0)
                #self.target_x = current_status.get('pose_x', 0.0)
                #self.target_y = current_status.get('pose_y', 0.0)
                #self.target_yaw = current_status.get('pose_yaw',0.0)
                #self.vel_x = current_status.get('vel_x', 0.0)
                #self.vel_y = current_status.get('vel_y', 0.0)
                #self.ang_vel_yaw = current_status.get('ang_vel_yaw',0.0)
                #self.estimate_arrival_time = current_status.get('estimate_arrival_time',0.0)
                ### add more for use in future
            else:
                self.get_logger().warn("Invalid system current status format: 'data' is empty or not a list")
        except Exception as e:
            self.get_logger().error(f"current status API request failed: {e}")
    
    def update_box_status(self, box_name: str, status: str):
        try:
            #status_id = self._get_status_id_for('box status update')
            api_client.update_status( box_name, status)
            self.get_logger().info(f"Updated box status: {box_name} = {status}")
        except Exception as e:
            self.get_logger().error(f"Failed to update box status: {e}")

    def update_door_status(self, door_name: str, status: str):
        try:
            #status_id = self._get_status_id_for('door status update')
            api_client.update_status( door_name, status)
            self.get_logger().info(f"Updated door status: {door_name} = {status}")
        except Exception as e:
            self.get_logger().error(f"Failed to update door status: {e}")

    def poll_system_parameters(self):
        self.get_system_parameters_from_api()

    def _normalize_system_parameters(self, config: dict) -> dict:
        return {
            "autoHomeWaitTime": config.get("autoHomeWaitTime", 0),
            "batteryLowToCharge": config.get("batteryLowToCharge", 20),
            "batteryChargingLimitUpper": config.get("batteryChargingLimitUpper", 100),
            "batteryChargingLimitLower": config.get("batteryChargingLimitLower", 95),
            "batteryLevelCanWork": config.get("batteryLevelCanWork", 50),
            "soundLevel": config.get("soundLevel", 50),
            "isSoundAlarmForRequest": self._parameter_to_bool(config.get("isSoundAlarmForRequest", 0)),
            "isSoundAlarmForDelivery": self._parameter_to_bool(config.get("isSoundAlarmForDelivery", 0)),
            "isLightAlarmForRequest": self._parameter_to_bool(config.get("isLightAlarmForRequest", 0)),
            "isLightAlarmForDelivery": self._parameter_to_bool(config.get("isLightAlarmForDelivery", 0)),
            "isSoundAlarmForObstacle": self._parameter_to_bool(config.get("isSoundAlarmForObstacle", 0)),
            "isEnableStationPassword": self._parameter_to_bool(config.get("isEnableStationPassword", 0)),
            "adminPassword": config.get("adminPassword", ""),
            "waitLoadinTimeout": config.get("waitLoadinTimeout", 5),
            "waitLoadoutTimeout": config.get("waitLoadoutTimeout", 30),
            "doorOpenTimeout": config.get("doorOpenTimeout", 30),
            "startPoseX": config.get("startPoseX", 0),
            "startPoseY": config.get("startPoseY", 0),
            "startPoseYaw": config.get("startPoseYaw", 0),
        }

    def _apply_system_parameters(self, settings: dict):
        self.setting_autoHomeWaitTime = settings["autoHomeWaitTime"]
        self.setting_batteryLowToCharge = settings["batteryLowToCharge"]
        self.setting_batteryChargingLimitUpper = settings["batteryChargingLimitUpper"]
        self.setting_batteryChargingLimitLower = settings["batteryChargingLimitLower"]
        self.setting_batteryLevelCanWork = settings["batteryLevelCanWork"]
        self.setting_soundLevel = settings["soundLevel"]
        self.setting_isSoundAlarmForRequest = settings["isSoundAlarmForRequest"]
        self.setting_isSoundAlarmForDelivery = settings["isSoundAlarmForDelivery"]
        self.setting_isLightAlarmForRequest = settings["isLightAlarmForRequest"]
        self.setting_isLightAlarmForDelivery = settings["isLightAlarmForDelivery"]
        self.setting_isSoundAlarmForObstacle = settings["isSoundAlarmForObstacle"]
        self.setting_isEnableStationPassword = settings["isEnableStationPassword"]
        self.setting_adminPassword = settings["adminPassword"]
        self.setting_waitLoadinTimeout = settings["waitLoadinTimeout"]
        self.setting_waitLoadoutTimeout = settings["waitLoadoutTimeout"]
        self.setting_doorOpenTimeout = settings["doorOpenTimeout"]
        self.setting_startPoseX = settings["startPoseX"]
        self.setting_startPoseY = settings["startPoseY"]
        self.setting_startPoseYaw = settings["startPoseYaw"]
        self.get_logger().info(f"setting_batteryLowToCharge: {self.setting_batteryLowToCharge}")

    def get_system_parameters_from_api(self, report_changes: bool = True):
        try:
            #url = "http://localhost:8080/api/params/list"
            #response = requests.get(url, timeout=3)
            #response.raise_for_status()
            #params = response.json()
            #data = params.get("data", [])
            params = api_client.get_system_parameters()
            data = params.get("data", [])
            if data and isinstance(data, list):
                raw_config = data[0]
                settings = self._normalize_system_parameters(raw_config)
                cached = self._cached_system_parameters
                if cached != settings:
                    if cached and report_changes:
                        for key, new_value in settings.items():
                            old_value = cached.get(key)
                            if old_value != new_value:
                                self.get_logger().info(
                                    f"System parameter '{key}' changed from {old_value} to {new_value}"
                                )
                    self._apply_system_parameters(settings)
                    self._cached_system_parameters = settings
            else:
                self.get_logger().warn("Invalid system parameter format: 'data' is empty or not a list")
        except Exception as e:
            self.get_logger().error(f"Failed to get system parameters: {e}")


    def get_pending_queue_from_api(self, return_all: bool = False, status: str = None):
        try:
            #url = "http://localhost:8080/api/queue/list"
            #response = requests.get(url, timeout=3)
            #response.raise_for_status()
            #data = response.json()
            data = api_client.get_pending_queue()
            queue_list = data.get("data", [])
            if isinstance(queue_list, str):
                queue_list = json.loads(queue_list)

            if not isinstance(queue_list, list):
                self.get_logger().info("No pending queue found or unexpected format.")
                return [] if return_all else None

            if len(queue_list) == 0:
                self.get_logger().info("No pending queue found or unexpected format.")
                return [] if return_all else None

            self.get_logger().info(f"{len(queue_list)} pending queues ")
            if return_all:
                return queue_list
            if status:
                status_lower = status.lower()
                for queue in queue_list:
                    queue_status = str(queue.get("status", "")).lower()
                    if queue_status == status_lower:
                        return queue
                self.get_logger().info(f"No pending queue found with status '{status}'.")
                return None
            return queue_list[0]
        except Exception as e:
            self.get_logger().error(f"Failed to get queue: {e}")
            return [] if return_all else None
    
    def get_active_queue_id(self):
        """Return the first queue identifier with status 'active', if any."""
        queue_list = self.get_pending_queue_from_api(return_all=True)
        if not queue_list:
            return None

        for queue in queue_list:
            status = str(queue.get("status", "")).lower()
            if status == "active":
                queue_id = queue.get("_id") or queue.get("id")
                if queue_id:
                    return queue_id
        return None
    
    def get_queue_count(self):
        """Return the count of current queues from the API."""
        queue_list = self.get_pending_queue_from_api(return_all=True)
        return len(queue_list) if queue_list else 0
    
    def move_active_queue_to_end(self, queue_list=None):
        """Requeue entries with status 'active' by duplicating them as 'queued' and removing the originals."""
        if queue_list is None:
            queue_list = self.get_pending_queue_from_api(return_all=True)

        if not queue_list:
            return []

        relocated = 0
        for queue in list(queue_list):
            status = str(queue.get("status", "")).lower()
            if status != "active":
                continue

            queue_id = queue.get("_id") or queue.get("id")
            payload = {k: v for k, v in queue.items() if k not in ("_id", "id")}
            payload["status"] = "queued"

            try:
                api_client.add_queue(payload)
            except Exception as e:
                self.get_logger().error(f"Failed to append active queue {queue_id} to tail: {e}")
                continue

            if queue_id:
                try:
                    api_client.remove_queue_by_id(queue_id)
                    relocated += 1
                except Exception as e:
                    self.get_logger().error(f"Failed to remove original active queue {queue_id}: {e}")
            else:
                self.get_logger().warn("Active queue missing identifier; cannot remove original entry.")

        updated_list = self.get_pending_queue_from_api(return_all=True)
        if isinstance(queue_list, list):
            queue_list[:] = updated_list

        self.get_logger().info(f"Requeued {relocated} active queue(s) to queue tail.")
        return updated_list
    
    def remove_queue_by_id(self, queue_id):
        try:
            #url = "http://localhost:8080/api/queue/remove"
            #headers = {"Content-Type": "application/json"}
            #payload = {"id": queue_id}
            #response = requests.post(url, headers=headers, json=payload, timeout=3)
            #response.raise_for_status()
            api_client.remove_queue_by_id(queue_id)
            self.get_logger().info(f"Successfully removed queue ID: {queue_id}")
        except Exception as e:
            self.get_logger().error(f"Failed to remove queue ID {queue_id}: {e}")

    def get_station_position(self, name):
        try:
            #url = "http://localhost:8080/api/station/list"
            #response = requests.get(url, timeout=3)
            #response.raise_for_status()
            station_data = api_client.get_station_list()
            stations = station_data.get("data", [])
            
            if isinstance(stations, str):
                stations = json.loads(stations)

            for s in stations:
                if s["name"] == name:
                    x = float(s["x"])
                    y = float(s["y"])
                    heading = float(s["heading"])
                    return x, y, heading
        except Exception as e:
            self.get_logger().error(f"Failed to get station list: {e}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
            self.get_logger().error(f"Invalid station format: {e}")
        return None, None, None

    def battery_status_monitor(self):
        #self.get_logger().info(f"Current battery SOC: {self.batt_percentage}%")
        status_id = self._get_status_id_for('battery status')
        try:
            api_client.update_soc(status_id, self.batt_percentage)
            api_client.update_status("voltage", self.batt_voltage)
            api_client.update_status("temperature", self.batt_temperature)
            api_client.update_status("current", self.batt_current)
            api_client.update_status("charge", self.batt_charge)
            api_client.update_status("capacity", self.batt_capacity)
            api_client.update_status("percentage", self.batt_percentage)
            api_client.update_status("design_capacity", self.batt_design_capacity)
            api_client.update_status("power_supply_status", self.batt_power_supply_status)
            api_client.update_status("power_supply_health", self.batt_power_supply_health)
            api_client.update_status("power_supply_technology", self.batt_power_supply_technology)
            api_client.update_status("present", self.batt_present)
        except Exception as e:
            self.get_logger().error(f'Failed to update robot SOC: {e}')
        
    def _get_status_id_for(self, action: str):
        status_id = getattr(self, 'status_id', None)
        if status_id:
            return status_id
        self.get_logger().warn(f'Robot status id missing; refreshing before {action}.')
        self.get_robot_status_from_api()
        status_id = getattr(self, 'status_id', None)
        if status_id:
            return status_id
        self.get_logger().warn(f'Using default status id 1 for {action}.')
        return 1

    def change_state(self, new_state: RobotState):
        if not isinstance(new_state, RobotState):
            self.get_logger().error(f"Invalid state requested. {new_state}")
            return
        if self.state == new_state:
            return
        if self.state == RobotState.MANUAL and new_state != RobotState.MANUAL:
            self._cancel_manual_monitor_timer()

        self.get_logger().info(f"State change: {self.state.name} -> {new_state.name}")
        self.state = new_state

        status_id = self._get_status_id_for('robot status update')
        if status_id:
            try:
                api_client.update_robot_status(new_state.name)
            except Exception as e:
                self.get_logger().error(f'Failed to update robot status: {e}')

        # Placeholder for state entry logic
        if self.state == RobotState.STANDBY:
            self.on_standby()
        elif self.state == RobotState.MOVE:
            self.on_move()
        elif self.state == RobotState.AFTER_MOVE:
            self.on_after_move()
        elif self.state == RobotState.LOAD_IN:
            self.on_load_in()
        elif self.state == RobotState.WAIT_LOAD_OUT:
            self.on_wait_load_out()
        elif self.state == RobotState.LOAD_OUT:
            self.on_load_out()
        elif self.state == RobotState.DOCK:
            self.on_dock()
        elif self.state == RobotState.MANUAL:
            self.on_manual()
    
    def on_manual(self):
        self.touch_activity()
        if self._manual_monitor_timer is None:
            self._manual_monitor_timer = self.create_timer(0.5, self._manual_monitor_loop)
        self.get_logger().info("Robot is in MANUAL mode. Monitoring toggle state.")

    def _manual_monitor_loop(self):
        state = self.get_state_from_api()
        if not self.toggle_manual:
            self.get_logger().info("Manual toggle disabled; switching to STANDBY.")
            self.change_state(RobotState.STANDBY)
            self._cancel_manual_monitor_timer()
            return

    def _cancel_manual_monitor_timer(self):
        if self._manual_monitor_timer is not None:
            self._manual_monitor_timer.cancel()
            self._manual_monitor_timer = None


    def change_dock_state(self, new_state: DockState):
        if not isinstance(new_state, DockState):
            self.get_logger().error(f"Invalid dock state requested. {new_state}")
            return
        if self.dockstate == new_state:
            return

        self.get_logger().info(f"Dock State change: {self.dockstate.name} -> {new_state.name}")
        self.dockstate = new_state
        api_client.update_status('dock_state',self.dockstate.name)

        # Placeholder for state entry logic
        if self.dockstate == DockState.IDLE:
            self.on_dock_idle()
        elif self.dockstate == DockState.DOCKING:
            self.on_dock_docking()
        elif self.dockstate == DockState.DOCKED:
            self.on_dock_docked()
        elif self.dockstate == DockState.UNDOCKING:
            self.on_dock_undocking()

    def on_dock_idle(self):
        return
    
    def on_dock_docking(self):
        return
    
    def on_dock_docked(self):
        return
    
    def on_dock_undocking(self):
        return

    def change_charge_state(self, new_state: ChargeState):
        if not isinstance(new_state, ChargeState):
            self.get_logger().error(f"Invalid charge state requested. {new_state}")
            return
        if self.chargestate == new_state:
            return

        self.get_logger().info(f"Charge State change: {self.chargestate.name} -> {new_state.name}")
        self.chargestate = new_state

        # Placeholder for state entry logic
        if self.chargestate == ChargeState.NOT_CHARGE:
            self.on_charge_nocharge()
        elif self.chargestate == ChargeState.CHARGING:
            self.on_charge_charging()

    def on_charge_nocharge(self):
        return
    
    def on_charge_charging(self):
        return
    

    def calculate_heading(self, pose):
        quant = pose.orientation
        orie_list = [quant.x,quant.y,quant.z,quant.w]
        (roll, pitch, yaw) = euler_from_quaternion(orie_list)
        #self.get_logger().info('current head='+ '{:.2f}'.format(yaw))
        return yaw

    def calculate_quaternion_from_yaw(self, yaw):
        quat = quaternion_from_euler(0.0, 0.0, yaw)
        # quat is [x, y, z, w]
        return quat[3]  # return w component

    def _euclidean_distance(self, p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return hypot(dx, dy)

    def _initialize_path_tracking(self, path_poses):
        if not path_poses:
            self._path_tracking = None
            return
        now = self.get_clock().now()
        total_distance = 0.0
        start_pose = getattr(self.current_pose, 'pose', None)
        if start_pose is not None:
            total_distance += self._euclidean_distance(start_pose.position, path_poses[0].pose.position)
        for first, second in zip(path_poses[:-1], path_poses[1:]):
            total_distance += self._euclidean_distance(first.pose.position, second.pose.position)
        self._path_tracking = {
            "poses": tuple(path_poses),
            "total_distance": total_distance,
            "current_index": 1 if len(path_poses) > 1 else 0,
            "start_time": now,
            "remaining_distance": total_distance,
        }
        self._update_path_remaining_distance()

    def _update_path_remaining_distance(self):
        if not self._path_tracking:
            return None
        path_info = self._path_tracking
        path_poses = path_info.get("poses") or []
        if not path_poses:
            return None
        current_position = self.current_pose.pose.position
        index = path_info.get("current_index", 1 if len(path_poses) > 1 else 0)
        if index < 0:
            index = 0
        n = len(path_poses)
        while index < n and self._euclidean_distance(current_position, path_poses[index].pose.position) <= self._waypoint_tolerance:
            index += 1
        if index >= n:
            remaining = 0.0
            path_info["current_index"] = n
        else:
            path_info["current_index"] = index
            remaining = self._euclidean_distance(current_position, path_poses[index].pose.position)
            for first, second in zip(path_poses[index:], path_poses[index + 1:]):
                remaining += self._euclidean_distance(first.pose.position, second.pose.position)
        remaining = max(0.0, remaining)
        total = path_info.get("total_distance", 0.0)
        if total > 0.0:
            remaining = min(remaining, total)
        path_info["remaining_distance"] = remaining
        return remaining

    def _estimate_arrival_time(self, remaining_distance):
        if not self._path_tracking:
            return None
        path_info = self._path_tracking
        total_distance = path_info.get("total_distance", 0.0)
        now = self.get_clock().now()
        elapsed = (now - path_info.get("start_time", now)).nanoseconds / 1e9
        distance_travelled = max(total_distance - remaining_distance, 0.0)
        avg_speed = distance_travelled / elapsed if elapsed > 1e-3 else 0.0
        speed = avg_speed if avg_speed > 1e-3 else self.current_speed
        if speed <= 1e-3:
            return None
        return remaining_distance / speed

    def _clear_path_tracking(self):
        self._path_tracking = None

    def send_goal_pose(self, x, y, yaw, after: RobotState = RobotState.STANDBY):
        self.goal_after_state = after
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = self.calculate_quaternion_from_yaw(yaw)
        
        self.navigator.goToPose(goal_pose)
        self.change_state(RobotState.MOVE)

    def send_goal_pose_agv(self, x, y, yaw, after: RobotState = RobotState.STANDBY):
        self.goal_after_state = after
        building_yaml = "/home/smr/workspaces/mini_amr/amrROS2_ws/maps/NECTEC_4th_Floor.building.yaml"
        current_pose = self.current_pose
        start_pos = (current_pose.pose.position.x, current_pose.pose.position.y)
        goal_pos = (x, y)

        self.get_logger().info(f"AGV start_pos: x={start_pos[0]:.2f}, y={start_pos[1]:.2f}")
        self.get_logger().info(f"AGV goal_pos: x={goal_pos[0]:.2f}, y={goal_pos[1]:.2f}")

        path_poses = compute_path_poses(building_yaml, start_pos, goal_pos)

        # Print out each waypoint in the path
        self.get_logger().info("Computed AGV path waypoints:")
        for i, pose in enumerate(path_poses):
            px = pose.pose.position.x
            py = pose.pose.position.y
            self.get_logger().info(f"  Waypoint {i}: x={px:.2f}, y={py:.2f}")

        if len(path_poses) > 0:
            # ✅ คำนวณ quaternion จาก yaw
            quat = quaternion_from_euler(0.0, 0.0, yaw)
            path_poses[-1].pose.orientation.x = quat[0]
            path_poses[-1].pose.orientation.y = quat[1]
            path_poses[-1].pose.orientation.z = quat[2]
            path_poses[-1].pose.orientation.w = quat[3]

        self._initialize_path_tracking(path_poses)

        if self.smooth_path:
            self.navigator.goThroughPoses(path_poses)
        else:
            self.navigator.followWaypoints(path_poses)
        
        self.change_state(RobotState.MOVE)

    def on_standby(self):
        self.get_logger().info("Robot is in STANDBY mode.")
        self.touch_activity()

  #  def return_home_position(self,after: RobotState = RobotState.STANDBY):
  #      x, y, heading = self.get_station_position("Home")
  #      if x is not None:
  #          yaw = heading * 3.141592 / 180.0
  #          #self.send_goal_pose(x, y, yaw, after)
  #          self.target_station = "Home"
  #          self.send_goal_pose_agv(x, y, yaw, after)
  #      else:
  #          self.get_logger().error("Home station not found.")
  #      return
    
    def go_to_station(self,target_station,after: RobotState = RobotState.STANDBY):
        if not target_station:
            self.get_logger().warn("No target station in task.")
            return False
        x, y, heading = self.get_station_position(target_station)
        if x is not None:
            self.target_station = target_station
            api_client.update_status('target_station',target_station)
            yaw = heading * 3.141592 / 180.0
            #self.send_goal_pose(x, y, yaw, after)
            api_client.update_status('target_x',x)
            api_client.update_status('target_y',y)
            api_client.update_status('target_yaw',yaw)
            self.send_goal_pose_agv(x, y, yaw, after)
            return True
        else:
            self.get_logger().warn("Target station not found.")
            return False

    def on_standby_loop(self):
        #self.get_logger().info(f"on_standby_loop : {self.state.name}")
        
        if (self.state != RobotState.STANDBY):
            return
        
        state = self.get_state_from_api()
        
        if self.toggle_manual:
            self.get_logger().info(f"State will be changed to {state.name}")
            self.change_state(RobotState.MANUAL)
            return

        
        if (state == RobotState.LOAD_IN):
            self.change_state(state)
            self.get_logger().info(f"State changed to {state.name}")
            return 
        elif (state == RobotState.LOAD_OUT):
            self.change_state(state)
            self.get_logger().info(f"State changed to {self.state.name}")
            return 

        if (self.dockstate == DockState.DOCKING or self.dockstate == DockState.UNDOCKING):
            return 
       # if self.send_undock_goal_future and not self.send_undock_goal_future.done():
       #     self.get_logger().info("Waiting for UNDOCK to complete...")
       #     return
       # if self.send_goal_future and not self.send_goal_future.done():
       #     self.get_logger().info("Waiting for DOCK to complete...")
       #     return
        


        # External dock/undock commands
        if self._should_dock:
            self._should_dock = False
            if (self.dockstate != DockState.DOCKED):
                self.retry_move_no = 0
                #self.return_home_position(RobotState.DOCK)
                #self.touch_activity()
                result = self.go_to_station("Home",RobotState.DOCK)
            return

        if self._should_undock:
            self._should_undock = False
            if (self.dockstate == DockState.DOCKED):
                #self.touch_activity()
                self.change_state(RobotState.DOCK)
            return
        
        #ตรวจสอบแบตเตอรี่ก่อน (จะไป Home เฉพาะถ้าไม่ได้อยู่ใน DOCK)
        if self.batt_percentage < self.setting_batteryLowToCharge:
            if (self.dockstate != DockState.DOCKED):
                self.get_logger().warn(f"Battery low ({self.batt_percentage}%), heading to Home for docking.")
                self.retry_move_no = 0
                #self.return_home_position(RobotState.DOCK)
                #self.touch_activity()
                result = self.go_to_station("Home",RobotState.DOCK)
            else:
                if (self.chargestate == ChargeState.NOT_CHARGE):
                    self.change_charge_state(ChargeState.CHARGING)

        #ตรวจสอบแบตเตอรี่ให้หยุดชาร์จเมื่อถึง limit #ย้ายไป battery_management package
       # if self.batt_percentage >= self.setting_batteryChargingLimitUpper:
       #     if (self.chargestate == ChargeState.CHARGING):
       #         self.change_charge_state(ChargeState.NOT_CHARGE)         


        # ตรวจสอบ queue
        queue_list = self.get_pending_queue_from_api(return_all=True)
        if queue_list:
            selected_task = None
            if self.current_station:
                for pending in queue_list:
                    action = pending.get("action", "Request")
                    if action == "Request" and pending.get("target") == self.current_station:
                        selected_task = pending
                        break

            if not selected_task:
                for pending in queue_list:
                    status = str(pending.get("status", "")).lower()
                    if status != "failed":
                        selected_task = pending
                        break

            if not selected_task:
                return

            target_station = selected_task.get("target")
            if (self.dockstate == DockState.DOCKED):
                self._should_undock = True
                return
            self.retry_move_no = 0
            action = selected_task.get("action", "Request")
            self.get_logger().info(f"Queue action: {action}")

            self.current_task = selected_task

            if action == "Request" and target_station and self.current_station and target_station == self.current_station:
                self.get_logger().info("Already at target station for Request; handling without navigation.")
                self.change_state(RobotState.AFTER_MOVE)
                return

            if action == "Delivery":
                if selected_task:
                    queue_id = selected_task.get("_id") or selected_task.get("id")
                    if queue_id:
                        api_client.update_queue_status(queue_id,'active')
                result = self.go_to_station(target_station,RobotState.LOAD_OUT)
            else: #action == "Request"
                if selected_task:
                    queue_id = selected_task.get("_id") or selected_task.get("id")
                    if queue_id:
                        api_client.update_queue_status(queue_id,'active')
                result = self.go_to_station(target_station,RobotState.STANDBY)

            if (result == False):
                if selected_task:
                    queue_id = selected_task.get("_id") or selected_task.get("id")
                    if queue_id:
                        api_client.update_queue_status(queue_id,'failed')
                        if action == "Request":
                            self.remove_queue_by_id(queue_id)
                        self.get_logger().info(f"Remove queue : {action}, target {target_station}")
                self.current_task = None
        
        elif (self.setting_autoHomeWaitTime > 0)and(self.dockstate != DockState.DOCKED):#ตรวจสอบว่าเกินเวลา setting_autoHomeWaitTime ให้กลับไป dock
            elapsed = ((self.get_clock().now() - self._last_activity_time).nanoseconds / 1e9) 
            if (elapsed > self.setting_autoHomeWaitTime):
                self.get_logger().info(f"AutoHomeWaitTime reached, go to Home and Dock")
                self.retry_move_no = 0
                #self.touch_activity()
                result = self.go_to_station("Home",RobotState.DOCK)
                return

    

    def on_move(self):
        self.get_logger().info("Robot is MOVING.")
        # TODO: Implement NAV2 or custom movement logic
        i = 0
        
        while not self.navigator.isTaskComplete():
        ################################################
        #
        # Implement some code here for your application!
        #
        ################################################

        # Do something with the feedback
            i = i + 1
            feedback = self.navigator.getFeedback()
            if feedback and i % 10 == 0:
                eta_seconds = None
                remaining_distance = self._update_path_remaining_distance()
                if remaining_distance is not None:
                    eta_seconds = self._estimate_arrival_time(remaining_distance)
                if eta_seconds is None and feedback.estimated_time_remaining is not None:
                    eta_seconds = Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9
                if eta_seconds is None:
                    eta_seconds = 0.0
                eta_seconds = max(0.0, eta_seconds)
                t = '{0:.0f}'.format(eta_seconds)
               # print(
               #     'Estimated time of arrival: '
               #     + t
               #     + ' seconds.'
               # )

                #status_id = self._get_status_id_for('Estimated time of arrival')
                api_client.update_status( "estimate_arrival_time", t)
                self.get_current_robot_pose()

               #  Some navigation timeout to demo cancellation
                #if Duration.from_msg(feedback.navigation_time) > Duration(seconds=600.0):
                state = self.get_state_from_api()
                if self.toggle_manual:
                    self.navigator.cancelTask()

        # Do something depending on the return code
        result = self.navigator.getResult()
        self._clear_path_tracking()
        if result == TaskResult.SUCCEEDED:
            if self.target_station != "":
                status_id = self._get_status_id_for('position update')
                try:
                    api_client.update_robot_current_station(self.target_station)
                    api_client.update_robot_target_station('')
                    api_client.update_status('target_x','')
                    api_client.update_status('target_y','')
                    api_client.update_status('target_yaw','')
                except Exception as e:
                    self.get_logger().error(f'Failed to update robot position: {e}')
                self.current_station = self.target_station
                self.target_station = ""
            self.get_logger().info('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            self.get_logger().info('Goal was canceled!')
            if self.toggle_manual:
                api_client.update_queue_status(self.get_active_queue_id(),'queued')
                self.change_state(RobotState.MANUAL)
            else:
                self.change_state(RobotState.STANDBY)
            return
        elif result == TaskResult.FAILED:
            if (self.retry_move_no < 2):
                self.retry_move_no += 1
                self.get_logger().info('Goal failed! retrying...{0}'.format(self.retry_move_no))
                self.go_to_station(self.target_station,self.goal_after_state)
                return self.on_move()
            else:
                self.get_logger().info('Goal failed! after retry {0} times'.format(self.retry_move_no))
                if (self.get_queue_count() == 1): #ถ้าเป็นงานเดียวที่เหลืออยู่ ให้ใส่สถานะงานว่า failed เพื่อไม่ต้องทำงานซ้ำไม่รู้จบ
                    task = self.get_pending_queue_from_api(status = 'active')
                    if task:
                        action = task.get("action", "Request")
                        queue_id = task.get("_id") or task.get("id")
                        if action == 'Request':
                            if queue_id:
                                api_client.update_queue_status(queue_id,'failed')
                                self.remove_queue_by_id(queue_id)
                        else: #Delivery ไม่ลบคิว ให้ค้างไว้
                            if queue_id:
                                api_client.update_queue_status(queue_id,'failed')
                else:
                    self.move_active_queue_to_end() #ถ้าไม่ใช่คำสั่งเดียวที่เหลืออยู่ ให้ย้ายคิวนี้ไปทำท้ายสุด   
                self.change_state(RobotState.STANDBY)
        else:
            self.get_logger().info('Goal has an invalid return status!')
        
        # กรณีเป็นการ move เพื่อเตรียม Dock (ไม่เกี่ยวกับ queue)
        if self.goal_after_state == RobotState.DOCK:
            if result == TaskResult.SUCCEEDED:
                self.change_state(RobotState.DOCK)
                return
            else:
                self.change_state(RobotState.STANDBY) #กลับไปพยายามเคลื่อนที่ไปยัง Home อีกครั้ง
                return 
        else:
            self.change_state(RobotState.AFTER_MOVE)

    def on_after_move(self):
        self.get_logger().info("Evaluating post-move action...")

        task = self.current_task or self.get_pending_queue_from_api(status="active")
        if task:
            #self.remove_queue_by_id(task["_id"])
            action = task.get("action", "Request")
            self.get_logger().info(f"Post-move action is: {action}")

            if action == "Request":
                if (self.setting_isSoundAlarmForRequest):
                    self.send_sound_command("arrive_target")
                #if (self.setting_isLightAlarmForRequest):
                    #implement light alarm command

                queue_id = task.get("_id") or task.get("id")
                if queue_id:
                    api_client.update_queue_status(queue_id,'completed')
                    self.remove_queue_by_id(queue_id)
                self.get_logger().info(f"Waiting {self.setting_waitLoadinTimeout}s for LOAD_IN command...")
                self._loadin_timeout_end = time.time() + self.setting_waitLoadinTimeout
                self._loadin_timer = self.create_timer(0.5, self.wait_for_load_in_loop)
                self.current_task = None
                return

            elif action == "Delivery":
                self.current_task = None
                self.change_state(RobotState.WAIT_LOAD_OUT)
            else:
                self.get_logger().warn("Unknown action after move, returning to STANDBY.")
                self.current_task = None
                self.change_state(RobotState.STANDBY)

        else:
            self.get_logger().info("No task found after move.")
            self.change_state(RobotState.STANDBY)
        self.current_task = None

    def wait_for_load_in_loop(self):
        state = self.get_state_from_api()
        if (state == RobotState.LOAD_IN):
            self.get_logger().info(f"State changed to {state.name} during wait.")
            self._loadin_timer.cancel()
            self.change_state(RobotState.LOAD_IN)
            return 

        if time.time() > self._loadin_timeout_end:
            self.get_logger().info("No LOAD_IN received. Returning to STANDBY.")
            self._loadin_timer.cancel()
            self.change_state(RobotState.STANDBY) 

    def on_load_in(self):
        self.get_logger().info("Robot is LOADING IN cargo.")
        self._loadin_timeout_end = time.time() + self.setting_waitLoadinTimeout
        self._loadin_timer = self.create_timer(0.5, self.load_in_loop)

        # TODO: Implement load in procedure
    
    def load_in_loop(self):
        state = self.get_state_from_api()
        if (state != RobotState.LOAD_IN):
            self.get_logger().info(f"State changed to {state.name} during LOAD_IN.")
            self._loadin_timer.cancel()
            self.change_state(state)
            return 

       # if time.time() > self._loadin_timeout_end:
       #     self.get_logger().info("Timeout. Returning to STANDBY.")
       #     self._loadin_timer.cancel()
       #     self.change_state(RobotState.STANDBY) 

    def on_wait_load_out(self):
        self.get_logger().info(f"Waiting {self.setting_waitLoadoutTimeout}s for LOAD_OUT action...")
        self.load_out_loop_counter = 0
        self._loadout_timeout_end = time.time() + self.setting_waitLoadoutTimeout
        self._loadout_timer = self.create_timer(0.5, self.wait_for_enter_load_out)

    def wait_for_enter_load_out(self):
        state = self.get_state_from_api()
        if (state == RobotState.LOAD_OUT):
            self.get_logger().info(f"State changed to {state.name} during wait.")
            self._loadout_timer.cancel()
            self.change_state(RobotState.LOAD_OUT)
            return 

        if time.time() > self._loadout_timeout_end:
            self.get_logger().info("No LOAD_OUT received. Returning to STANDBY.")
            self._loadout_timer.cancel()
            self.change_state(RobotState.STANDBY) 

        self.load_out_loop_counter += 1
        if self.load_out_loop_counter == 1 or self.load_out_loop_counter % 20 == 0:
            if (self.setting_isSoundAlarmForDelivery):
                self.send_sound_command("arrive_delivery")
            #if (self.setting_isLightAlarmForDelivery):
                #implement light alarm command

    def on_load_out(self):
        self.get_logger().info("Robot is LOADING OUT cargo.")
        self._loadout_timeout_end2 = time.time() + self.setting_waitLoadoutTimeout
        self._loadout_timer2 = self.create_timer(0.5, self.load_out_loop)

        # TODO: Implement load in procedure
    
    def load_out_loop(self):
        state = self.get_state_from_api()
        if (state != RobotState.LOAD_OUT):
            self.get_logger().info(f"State changed to {state.name} during LOAD_OUT.")
            self._loadout_timer2.cancel()
            self.change_state(state)
            return 
        
        # if time.time() > self._loadout_timeout_end2:
        #     self.get_logger().info("Timeout. Returning to STANDBY.")
        #     self._loadin_timer.cancel()
        #     self.change_state(RobotState.STANDBY) 
   

    def on_dock(self):
        if (self.dockstate == DockState.IDLE):
            self.get_logger().info("Robot move for charging.")

            if not self.autodock_client.wait_for_server(timeout_sec=5.0):
                self.get_logger().error("Autodock action server not available.")
                self.change_state(RobotState.STANDBY)
                return
            
            self.change_dock_state(DockState.DOCKING)
            goal_msg = Autodock.Goal()
            goal_msg.is_dock = True

            self.get_logger().info("Sending autodock goal...")
                
            self.send_goal_future = self.autodock_client.send_goal_async(goal_msg, feedback_callback=self.dock_feedback_callback)
            self.send_goal_future.add_done_callback(self.dock_goal_response_callback)
        
        elif (self.dockstate == DockState.DOCKED):
            self.undock()


    def dock_goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Autodock goal was rejected.")
            self.change_dock_state(DockState.IDLE)
            self.change_state(RobotState.STANDBY)
            return

        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(self.dock_result_callback)

    def dock_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info("Docking successful. Entering CHARGING state.")
            self.change_dock_state(DockState.DOCKED)
        else:
            self.get_logger().warn("Charging failed.")
            self.change_dock_state(DockState.IDLE)
        
        self.change_state(RobotState.STANDBY)
    
    def dock_feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback dock: {0}'.format(feedback.step))

    def on_charging(self):
        self.get_logger().info("Robot is CHARGING...")
        # เริ่ม charging loop ด้วย timer ทุก 2 วินาที
        #self._charging_timer = self.create_timer(2.0, self.charging_loop)


    def undock(self):
        self.get_logger().info("Robot is UNDOCKING.")

        if not self.autodock_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Autodock action server not available.")
            self.change_state(RobotState.STANDBY)
            return
        
        self.change_dock_state(DockState.UNDOCKING)
        goal_msg = Autodock.Goal()
        goal_msg.is_dock = False

        self.get_logger().info("Sending autodock UNDOCK goal...")
        self.send_undock_goal_future = self.autodock_client.send_goal_async(goal_msg, feedback_callback=self.undock_feedback_callback)
        self.get_logger().info("Undock goal sent (future created)")
        self.send_undock_goal_future.add_done_callback(self.undock_goal_response_callback)
        

    def undock_goal_response_callback(self, future):
        self.get_logger().info("Undock goal response callback triggered")
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Undock goal was rejected.")
            #self.change_state(RobotState.STANDBY)
            return

        self.undock_result_future = goal_handle.get_result_async()
        self.undock_result_future.add_done_callback(self.undock_result_callback)

    def undock_result_callback(self, future):
        result = future.result().result
        if result.success:           
            self.get_logger().info("Undock successful. Proceeding to STANDBY.")
            self.change_dock_state(DockState.IDLE)
            self.change_state(RobotState.STANDBY)
        else:
            self.get_logger().warn("Undock failed.")
            #self.change_state(RobotState.STANDBY)
    
    def undock_feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback undock: {0}'.format(feedback.step))

    def handle_dock_command(self, request, response):
        if request.data:
            self.get_logger().info("Queued external DOCK command")
            self._should_dock = True
            response.success = True
            response.message = "Dock command queued."
        else:
            self.get_logger().info("Queued external UNDOCK command")
            self._should_undock = True
            response.success = True
            response.message = "Undock command queued."
        return response
    
    def send_sound_command(self, sound_msg: str):
        msg = String()
        msg.data = sound_msg
        self.sound_publisher.publish(msg)
        self.get_logger().info(f'Published message: "{sound_msg}"')


#def install_signal_handlers(server: RPCServer):
#    def _graceful_shutdown(signum, frame):
#        print(f"\n[MAIN] Caught signal {signum}, shutting down...")
#        server.stop()
#        raise SystemExit(0)
#    for sig in (signal.SIGINT, signal.SIGTERM):
#        signal.signal(sig, _graceful_shutdown)

def main(args=None):
    rclpy.init(args=args)
    node = None
    node = DeliveryRobotMainController()
    # Use localhost by default; override with RPC_HOST / RPC_INTERFACE if needed
    server = RPCServer(host='localhost', port=6000, authkey=b"secret")
    server.register_funcs(FUNCS)
    server.start(daemon=True)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        if node is not None:
            node.get_logger().info("Node stopped by user.")
    finally:
        if node is not None:
            node.destroy_node()
        server.stop()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
    
  
