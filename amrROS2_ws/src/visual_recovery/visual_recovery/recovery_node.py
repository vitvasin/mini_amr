#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
import time

from std_srvs.srv import Trigger
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from nav2_msgs.srv import ClearEntireCostmap

class RecoveryNode(Node):
    def __init__(self):
        super().__init__('visual_recovery_node')

        # Parameters
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('camera_topic', '/image_raw')
        self.declare_parameter('request_image_topic', '/visual_localization/image_request')
        self.declare_parameter('response_pose_topic', '/visual_localization/pose_response')
        self.declare_parameter('initialpose_topic', '/initialpose')
        self.declare_parameter('timeout_seconds', 60.0)

        cmd_vel_topic = self.get_parameter('cmd_vel_topic').get_parameter_value().string_value
        self.camera_topic = self.get_parameter('camera_topic').get_parameter_value().string_value
        request_image_topic = self.get_parameter('request_image_topic').get_parameter_value().string_value
        response_pose_topic = self.get_parameter('response_pose_topic').get_parameter_value().string_value
        initialpose_topic = self.get_parameter('initialpose_topic').get_parameter_value().string_value
        self.timeout_seconds = self.get_parameter('timeout_seconds').get_parameter_value().double_value

        # Callback Groups
        self.service_cb_group = MutuallyExclusiveCallbackGroup()
        self.sub_cb_group = MutuallyExclusiveCallbackGroup()

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.image_req_pub = self.create_publisher(Image, request_image_topic, 10)
        self.initialpose_pub = self.create_publisher(PoseWithCovarianceStamped, initialpose_topic, 10)

        # Action Client to cancel Nav2 goals
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Costmap Clearing Clients
        self.clear_local_costmap_client = self.create_client(ClearEntireCostmap, '/local_costmap/clear_entirely_local_costmap')
        self.clear_global_costmap_client = self.create_client(ClearEntireCostmap, '/global_costmap/clear_entirely_global_costmap')

        # Subscribers (initialized dynamically when triggered)
        self.camera_sub = None
        self.pose_sub = None

        # State Variables
        self.captured_image = None
        self.received_pose = None
        self.recovery_in_progress = False
        self.last_recovery_time = 0.0

        # Trigger Service
        self.trigger_srv = self.create_service(
            Trigger,
            '~/trigger_recovery',
            self.trigger_callback,
            callback_group=self.service_cb_group
        )

        # Automatic recovery trigger subscription is disabled per user request (manual recovery only)
        # self.status_sub = self.create_subscription(
        #     Bool,
        #     '/localization_status',
        #     self.localization_status_callback,
        #     10,
        #     callback_group=self.sub_cb_group
        # )

        self.get_logger().info('Visual Recovery Node has been initialized. Auto-recovery is disabled (Manual recovery only).')

    def halt_movement(self):
        self.get_logger().info('Halting robot movement...')
        
        # Publish zero velocities
        stop_twist = Twist()
        stop_twist.linear.x = 0.0
        stop_twist.linear.y = 0.0
        stop_twist.linear.z = 0.0
        stop_twist.angular.x = 0.0
        stop_twist.angular.y = 0.0
        stop_twist.angular.z = 0.0
        self.cmd_vel_pub.publish(stop_twist)

        # Try to cancel Nav2 goals if action server is available
        if self.nav_action_client.server_is_ready():
            self.get_logger().info('Canceling Nav2 goals...')
            try:
                # Asynchronously cancel goals; we don't wait for the result here to keep it non-blocking
                self.nav_action_client._cancel_goal_async(None)
            except Exception as e:
                self.get_logger().warn(f'Nav2 goal cancellation bypassed or failed: {e}')
        else:
            self.get_logger().info('Nav2 Action server not ready. Relying on cmd_vel stop.')


    def camera_callback(self, msg: Image):
        if self.captured_image is None:
            self.get_logger().info('Captured one frame from the webcam.')
            self.captured_image = msg

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        if self.received_pose is None:
            self.get_logger().info('Received 6DoF pose from visual localization pipeline.')
            self.received_pose = msg

    # def localization_status_callback(self, msg: Bool):
    #     if not msg.data:
    #         current_time = time.time()
    #         # Safety cooldown of 30 seconds between auto-recovery attempts
    #         if not self.recovery_in_progress and (current_time - self.last_recovery_time > 30.0):
    #             self.last_recovery_time = current_time
    #             self.get_logger().warn('Localization lost detected via /localization_status. Triggering auto-recovery sequence...')
    #             import threading
    #             threading.Thread(target=self.run_recovery_sequence, daemon=True).start()

    def trigger_callback(self, request, response):
        success, message = self.run_recovery_sequence()
        response.success = success
        response.message = message
        return response

    def run_recovery_sequence(self):
        if self.recovery_in_progress:
            msg = 'Recovery sequence already in progress.'
            self.get_logger().warn(msg)
            return False, msg

        self.recovery_in_progress = True
        self.captured_image = None
        self.received_pose = None

        self.get_logger().info('=== Starting Recovery Sequence ===')

        # 2. Halt Movement
        self.halt_movement()

        # 3. Capture Image
        self.get_logger().info(f'Subscribing to {self.camera_topic} to capture an image...')
        self.camera_sub = self.create_subscription(
            Image,
            self.camera_topic,
            self.camera_callback,
            qos_profile_sensor_data,
            callback_group=self.sub_cb_group
        )

        # Wait until an image is captured
        capture_timeout = 5.0
        time_waited = 0.0
        while self.captured_image is None and time_waited < capture_timeout:
            time.sleep(0.1)
            time_waited += 0.1

        # Unsubscribe from camera
        self.destroy_subscription(self.camera_sub)
        self.camera_sub = None

        if self.captured_image is None:
            msg = 'Failed to capture image from webcam within timeout. Aborting.'
            self.get_logger().error(msg)
            self.recovery_in_progress = False
            return False, msg

        # 4. Asynchronous Pose Request
        self.get_logger().info('Sending image to visual localization pipeline...')
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            self.get_parameter('response_pose_topic').get_parameter_value().string_value,
            self.pose_callback,
            10,
            callback_group=self.sub_cb_group
        )

        self.image_req_pub.publish(self.captured_image)

        self.get_logger().info(f'Waiting up to {self.timeout_seconds} seconds for the 6DoF pose...')
        time_waited = 0.0
        while self.received_pose is None and time_waited < self.timeout_seconds:
            time.sleep(0.1)
            time_waited += 0.1

        # Unsubscribe from pose
        self.destroy_subscription(self.pose_sub)
        self.pose_sub = None

        if self.received_pose is None:
            msg = 'Visual localization pipeline failed to return a pose within timeout. Aborting.'
            self.get_logger().warn(msg)
            self.recovery_in_progress = False
            return False, msg

        # 5. Pose Injection
        # Simple validation: Check if position and orientation are all perfectly 0 (likely garbage/uninitialized data)
        p = self.received_pose.pose.pose.position
        o = self.received_pose.pose.pose.orientation
        if p.x == 0.0 and p.y == 0.0 and p.z == 0.0 and o.x == 0.0 and o.y == 0.0 and o.z == 0.0 and o.w == 0.0:
            msg = 'Received empty/garbage pose data. Aborting recovery sequence.'
            self.get_logger().warn(msg)
            self.recovery_in_progress = False
            return False, msg

        self.get_logger().info('Injecting 6DoF pose into AMCL/Slam-toolbox via /initialpose...')
        # Ensure header frame is consistent, or rely on what visual pipeline sent
        # Here we just forward it.
        self.initialpose_pub.publish(self.received_pose)

        # Give the system a brief moment to process the pose update
        time.sleep(0.5)

        # Clear costmaps to remove "ghost obstacles" from the old location
        self.get_logger().info('Clearing costmaps...')
        if self.clear_local_costmap_client.wait_for_service(timeout_sec=1.0):
            self.clear_local_costmap_client.call_async(ClearEntireCostmap.Request())
        else:
            self.get_logger().warn('Local costmap clear service not available.')
            
        if self.clear_global_costmap_client.wait_for_service(timeout_sec=1.0):
            self.clear_global_costmap_client.call_async(ClearEntireCostmap.Request())
        else:
            self.get_logger().warn('Global costmap clear service not available.')

        self.recovery_in_progress = False
        msg = 'Recovery sequence completed successfully.'
        self.get_logger().info(msg)
        return True, msg

def main(args=None):
    rclpy.init(args=args)
    node = RecoveryNode()
    
    # We use a MultiThreadedExecutor so the async service callback 
    # doesn't block the executor from running subscriber callbacks.
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
