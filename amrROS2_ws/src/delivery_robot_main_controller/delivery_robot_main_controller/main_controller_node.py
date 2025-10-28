import rclpy
from rclpy.node import Node
from enum import Enum, auto
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration
from rclpy.action import ActionClient
from custom_interface.action import Autodock
from std_srvs.srv import SetBool
from .generate_agv_path_from_building_yaml import compute_path_poses
import tf2_ros
import tf2_geometry_msgs 


from tf_transformations import euler_from_quaternion, quaternion_from_euler, quaternion_multiply
import time
#import requests
import json

from sensor_msgs.msg import BatteryState

from . import api_client

import signal
from .rpc_server import RPCServer
from .rpc_fnc import door_command, echo, dock_command_service, configure_rpc_access

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
        self._should_dock = False #สำหรับเรียกเข้า dock และ undock แบบ manual
        self._should_undock = False
        self.current_pose = PoseStamped()
        
        #self.get_logger().info(f"Initial state: {RobotState.MOVE}")
        #api_client.update_robot_status((RobotState.MOVE).name)
        #return
        # Initialize robot state
        self.state = RobotState.STANDBY
        self.dockstate = DockState.IDLE
        self.chargestate = ChargeState.NOT_CHARGE
        self.target_station = ""
        self.retry_move_no = 0
        self.status_id = None

        self.get_logger().info(f"Initial state: {self.state.name}")
        
        self.get_system_parameters_from_api()

        # Example publisher (placeholder for /cmd_vel or similar)
        # self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Example timer to periodically print state (can remove later)
        self.batt_percentage = 80  # battery state of charge

        # Subscribe to /battery topic
        self.create_subscription(
            BatteryState,
            "/battery",
            self.battery_callback,
            10
        )
        self.smooth_path = True
        self.navigator = BasicNavigator()
        time.sleep(1)
        if not self.navigator.initial_pose_received:
            self.get_logger().info("Waiting for Nav2 system...")
            self.navigator.waitUntilNav2Active()

        #timer
        self.create_timer(1.0, self.state_monitor) #ตรวจสอบสถานะ state ประตู box ของหุ่นยนต์
        self.create_timer(2.0, self.battery_status_monitor)  # update แบตเตอรี่ทุก 2 วินาที
        self.create_timer(2.0, self.on_standby_loop) #ตรวจสอบ condition ใน state standby

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.get_current_robot_pose)

        


        
        self.autodock_client = ActionClient(self, Autodock, 'autodock')

        # Add dock_command service for external dock/undock requests
        self.dock_command_srv = self.create_service(SetBool, 'dock_command', self.handle_dock_command)

        #time.sleep(2.0)
        #self.send_goal_pose(1.0,0.0,0.0) #test
        self.on_standby()

        # TODO: Add action clients / services / subscribers as needed

    def get_current_robot_pose(self):
        try:
            # Lookup the transform from 'map' to 'base_link'
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link', rclpy.time.Time()
            )
            # Create a PoseStamped message from the transform
            current_pose = PoseStamped()
            current_pose.header.frame_id = 'map'
            current_pose.header.stamp = self.get_clock().now().to_msg()
            current_pose.pose.position.x = transform.transform.translation.x
            current_pose.pose.position.y = transform.transform.translation.y
            current_pose.pose.position.z = transform.transform.translation.z
            current_pose.pose.orientation = transform.transform.rotation
            self.current_pose =  current_pose
            self.get_logger().info(f"Current Pose: x={current_pose.pose.position.x}, y={current_pose.pose.position.y}")
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
            self.battery_status_monitor()

        except Exception as e:
            self.get_logger().error(f"Battery callback exception: {e}")
    
    def state_monitor(self):
        # Periodic task to monitor or report state
        self.get_robot_status_from_api()
        self.get_logger().info(f"Current state: {self.state.name}, dock_state {self.dockstate.name}, charge_state {self.chargestate.name}")

    def get_state_from_api(self):
        try:
            params = api_client.get_robot_status()
            data = params.get("data", [])
            # ใช้ข้อมูล เช่น:
            if data and isinstance(data, list):
                current_status = data[0]
                status_id = current_status.get("_id") or current_status.get("id")
                if status_id:
                    self.status_id = status_id
                state_value = current_status.get("status", "")
            
                # ถ้า state เป็น dict เช่น {"name": "STANDBY"} ให้ดึงชื่อออกมา
                if isinstance(state_value, dict):
                    state_str = state_value.get("status", "")
                else:
                    state_str = state_value

                state = getattr(RobotState, state_str, RobotState.STANDBY)
                return state
            else:
                self.get_logger().warn("Invalid system current status format: 'data' is empty or not a list")
                return None
        
        except Exception as e:
            self.get_logger().error(f"current status API request failed: {e}")
            return None

    def get_robot_status_from_api(self):
        try:
            #url = 'http://localhost:8080/api/robotstatus/list'  # URL ของ API ที่เชื่อมกับ MongoDB
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
                #self.change_state(state)
                status_id = current_status.get('_id') or current_status.get('id')
                if status_id:
                    self.status_id = status_id
                else:
                    self.get_logger().warn('Robot status id missing from API response.')
                self.location = current_status.get('position','N/A')
                self.charging = current_status.get('charging','Not Charge')
                self.door1 = current_status.get('door1','N/A')
                self.door2 = current_status.get('door2','N/A')
                self.door3 = current_status.get('door3','N/A')
                self.door4 = current_status.get('door4','N/A')
                self.door5 = current_status.get('door5','N/A')
                self.door6 = current_status.get('door6','N/A')
                self.door7 = current_status.get('door7','N/A')
                self.door8 = current_status.get('door8','N/A')
                self.box1 = current_status.get('box1','N/A')
                self.box2 = current_status.get('box2','N/A')
                self.box3 = current_status.get('box3','N/A')
                self.box4 = current_status.get('box4','N/A')
                self.box5 = current_status.get('box5','N/A')
                self.box6 = current_status.get('box6','N/A')
                self.box7 = current_status.get('box7','N/A')
                self.box8 = current_status.get('box8','N/A')
                self.box9 = current_status.get('box9','N/A')
            else:
                self.get_logger().warn("Invalid system current status format: 'data' is empty or not a list")
        except Exception as e:
            self.get_logger().error(f"current status API request failed: {e}")
    
    def update_box_status(self, box_name: str, status: str):
        try:
            payload = {
                "box": box_name,
                "value": status
            }
            status_id = self._get_status_id_for('box status update')
            api_client.update_robot_box(status_id, payload)
            self.get_logger().info(f"Updated box status: {box_name} = {status}")
        except Exception as e:
            self.get_logger().error(f"Failed to update box status: {e}")

    def update_door_status(self, door_name: str, status: str):
        try:
            payload = {
                "door": door_name,
                "value": status
            }
            status_id = self._get_status_id_for('door status update')
            api_client.update_robot_door(status_id, payload)
            self.get_logger().info(f"Updated door status: {door_name} = {status}")
        except Exception as e:
            self.get_logger().error(f"Failed to update door status: {e}")

    def get_system_parameters_from_api(self):
        try:
            #url = "http://localhost:8080/api/params/list"
            #response = requests.get(url, timeout=3)
            #response.raise_for_status()
            #params = response.json()
            #data = params.get("data", [])
            params = api_client.get_system_parameters()
            data = params.get("data", [])
            if data and isinstance(data, list):
                config = data[0]
                self.setting_autoHomeWaitTime = config.get("autoHomeWaitTime", 0)
                self.setting_batteryLowToCharge = config.get("batteryLowToCharge", 20)
                self.setting_batteryChargingLimitUpper = config.get("batteryChargingLimitUpper", 100)
                self.setting_batteryChargingLimitLower = config.get("batteryChargingLimitLower", 95)
                self.setting_batteryLevelCanWork = config.get("batteryLevelCanWork", 50)
                self.setting_isSoundAlarmForRequest = config.get("isSoundAlarmForRequest", 0)
                self.setting_isSoundAlarmForDelivery = config.get("isSoundAlarmForDelivery", 0)
                self.setting_isLightAlarmForRequest = config.get("isLightAlarmForRequest", 0)
                self.setting_isLightAlarmForDelivery = config.get("isLightAlarmForDelivery", 0)
                self.setting_isSoundAlarmForObstacle = config.get("isSoundAlarmForObstacle", 0)
                self.setting_isEnableStationPassword = config.get("isEnableStationPassword", 0)
                self.setting_adminPassword = config.get("adminPassword", "")
                self.setting_waitLoadinTimeout = config.get("waitLoadinTimeout", 5)
                self.setting_waitLoadoutTimeout = config.get("waitLoadoutTimeout", 30)
                self.setting_doorOpenTimeout = config.get("doorOpenTimeout", 30)
                self.setting_startPoseX = config.get("startPoseX", 0)
                self.setting_startPoseY = config.get("startPoseY", 0)
                self.setting_startPoseYaw = config.get("startPoseYaw", 0)

                self.get_logger().info(f"setting_batteryLowToCharge: {self.setting_batteryLowToCharge}")
            else:
                self.get_logger().warn("Invalid system parameter format: 'data' is empty or not a list")
        except Exception as e:
            self.get_logger().error(f"Failed to get system parameters: {e}")


    def get_pending_queue_from_api(self):
        try:
            #url = "http://localhost:8080/api/queue/list"
            #response = requests.get(url, timeout=3)
            #response.raise_for_status()
            #data = response.json()
            data = api_client.get_pending_queue()
            queue_list = data.get("data", [])
            if isinstance(queue_list, list) and len(queue_list) > 0:
                self.get_logger().info(f"{len(queue_list)} pending queues ")
                return queue_list[0]
            else:
                self.get_logger().info("No pending queue found or unexpected format.")
                return None
        except Exception as e:
            self.get_logger().error(f"Failed to get queue: {e}")
            return None
    
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
        status_id = self._get_status_id_for('state of charge update')
        try:
            api_client.update_soc(status_id, self.batt_percentage)
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

        self.get_logger().info(f"State change: {self.state.name} -> {new_state.name}")
        self.state = new_state

        status_id = self._get_status_id_for('robot status update')
        if status_id:
            try:
                api_client.update_robot_status(status_id, new_state.name)
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
        elif self.state == RobotState.LOAD_OUT:
            self.on_load_out()
        elif self.state == RobotState.DOCK:
            self.on_dock()
       
    def change_dock_state(self, new_state: DockState):
        if not isinstance(new_state, DockState):
            self.get_logger().error(f"Invalid dock state requested. {new_state}")
            return
        if self.dockstate == new_state:
            return

        self.get_logger().info(f"Dock State change: {self.dockstate.name} -> {new_state.name}")
        self.dockstate = new_state

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

        if self.smooth_path:
            self.navigator.goThroughPoses(path_poses)
        else:
            self.navigator.followWaypoints(path_poses)
        
        self.change_state(RobotState.MOVE)

    def on_standby(self):
        self.get_logger().info("Robot is in STANDBY mode.")

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
            yaw = heading * 3.141592 / 180.0
            #self.send_goal_pose(x, y, yaw, after)
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
                result = self.go_to_station("Home",RobotState.DOCK)
            return

        if self._should_undock:
            self._should_undock = False
            if (self.dockstate == DockState.DOCKED):
                self.change_state(RobotState.DOCK)
            return
        
        #ตรวจสอบแบตเตอรี่ก่อน (จะไป Home เฉพาะถ้าไม่ได้อยู่ใน DOCK)
        if self.batt_percentage < self.setting_batteryLowToCharge:
            if (self.dockstate != DockState.DOCKED):
                self.get_logger().warn(f"Battery low ({self.batt_percentage}%), heading to Home for docking.")
                self.retry_move_no = 0
                #self.return_home_position(RobotState.DOCK)
                result = self.go_to_station("Home",RobotState.DOCK)
            else:
                if (self.chargestate == ChargeState.NOT_CHARGE):
                    self.change_charge_state(ChargeState.CHARGING)

        #ตรวจสอบแบตเตอรี่ให้หยุดชาร์จเมื่อถึง limit
        if self.batt_percentage >= self.setting_batteryChargingLimitUpper:
            if (self.chargestate == ChargeState.CHARGING):
                self.change_charge_state(ChargeState.NOT_CHARGE)         

        # ตรวจสอบ queue
        task = self.get_pending_queue_from_api()
        if task:
            target_station = task.get("target")
            if (self.dockstate == DockState.DOCKED):
                self._should_undock = True
                return
            self.retry_move_no = 0
            action = task.get("action", "Request")
            self.get_logger().info(f"Queue action: {action}")
            if action == "Delivery":
                result = self.go_to_station(target_station,RobotState.LOAD_OUT)
            else: #action == "Request"
                result = self.go_to_station(target_station,RobotState.STANDBY)

            if (result == False):
                if task:
                    self.remove_queue_by_id(task["_id"])
                    self.get_logger().info(f"Remove queue : {action}, target {target_station}")

    
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
           # if feedback and i % 5 == 0:
              #  print(
              #      'Estimated time of arrival: '
              #      + '{0:.0f}'.format(
              #          Duration.from_msg(feedback.estimated_time_remaining).nanoseconds
              #          / 1e9
              #      )
              #      + ' seconds.'
              #  )
                
                # Some navigation timeout to demo cancellation
              #  if Duration.from_msg(feedback.navigation_time) > Duration(seconds=600.0):
              #      self.navigator.cancelTask()

        # Do something depending on the return code
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            if self.target_station != "":
                status_id = self._get_status_id_for('position update')
                try:
                    api_client.update_robot_position(status_id, self.target_station)
                except Exception as e:
                    self.get_logger().error(f'Failed to update robot position: {e}')
                self.target_station = ""
            self.get_logger().info('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            self.get_logger().info('Goal was canceled!')
        elif result == TaskResult.FAILED:
            if (self.retry_move_no < 2):
                self.retry_move_no += 1
                self.get_logger().info('Goal failed! retrying...{0}'.format(self.retry_move_no))
                self.go_to_station(self.target_station,self.goal_after_state)
                return
            else:
                self.get_logger().info('Goal failed! after retry {0} times'.format(self.retry_move_no))
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

        task = self.get_pending_queue_from_api()
        if task:
            #self.remove_queue_by_id(task["_id"])
            action = task.get("action", "Request")
            self.get_logger().info(f"Post-move action is: {action}")

            if action == "Request":
                self.remove_queue_by_id(task["_id"])
                self.get_logger().info(f"Waiting {self.setting_waitLoadinTimeout}s for LOAD_IN command...")
                self._loadin_timeout_end = time.time() + self.setting_waitLoadinTimeout
                self._loadin_timer = self.create_timer(0.5, self.wait_for_load_in_loop)
                return

            elif action == "Delivery":
                self.change_state(RobotState.LOAD_OUT)
            else:
                self.get_logger().warn("Unknown action after move, returning to STANDBY.")
                self.change_state(RobotState.STANDBY)

        else:
            self.get_logger().info("No task found after move.")
            self.change_state(RobotState.STANDBY)

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

    def on_load_out(self):
        self.get_logger().info(f"Waiting {self.setting_waitLoadoutTimeout}s for LOAD_OUT action...")

        self._loadout_timeout_end = time.time() + self.setting_waitLoadoutTimeout
        self._loadout_timer = self.create_timer(0.5, self.wait_for_load_out_loop)

    def wait_for_load_out_loop(self):
        state = self.get_state_from_api()
        self.get_logger().info(f"load out loop state :{state.name}")
        if (state != RobotState.LOAD_OUT):
            self.change_state(state)
            self.get_logger().info(f"State changed to {self.state.name} during wait.")
            self._loadout_timer.cancel()
            return 
        
        if self.state != RobotState.LOAD_OUT:
            self.get_logger().info(f"State changed to {self.state.name} during LOAD_OUT wait.")
            self._loadout_timer.cancel()
            return

        # Replace with actual condition for detecting user-triggered load out
        #if False:  # Example placeholder
        #    self.get_logger().info("LOAD_OUT action received.")
        #    self._loadout_timer.cancel()
        #    # Optionally perform additional logic here
        #    self.change_state(RobotState.STANDBY)
        #    return

        if time.time() > self._loadout_timeout_end:
            self.get_logger().info("No LOAD_OUT received. Returning to STANDBY.")
            self._loadout_timer.cancel()
            self.change_state(RobotState.STANDBY)

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
    server = RPCServer(host="0.0.0.0", port=6000, authkey=b"secret")
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
    
  