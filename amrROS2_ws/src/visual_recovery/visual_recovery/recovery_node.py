#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
import time

from std_srvs.srv import Trigger
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
        
        # New Parameters for switching and Fiducial Marker localization
        self.declare_parameter('recovery_method', 'marker')  # Options: 'marker', 'ai', 'hybrid'
        self.declare_parameter('request_marker_image_topic', '/marker_localization/image_request')
        self.declare_parameter('response_marker_pose_topic', '/marker_localization/pose_response')

        cmd_vel_topic = self.get_parameter('cmd_vel_topic').get_parameter_value().string_value
        self.camera_topic = self.get_parameter('camera_topic').get_parameter_value().string_value
        request_image_topic = self.get_parameter('request_image_topic').get_parameter_value().string_value
        self.response_pose_topic = self.get_parameter('response_pose_topic').get_parameter_value().string_value
        initialpose_topic = self.get_parameter('initialpose_topic').get_parameter_value().string_value
        self.timeout_seconds = self.get_parameter('timeout_seconds').get_parameter_value().double_value
        
        self.recovery_method = self.get_parameter('recovery_method').get_parameter_value().string_value
        request_marker_image_topic = self.get_parameter('request_marker_image_topic').get_parameter_value().string_value
        self.response_marker_pose_topic = self.get_parameter('response_marker_pose_topic').get_parameter_value().string_value

        # Callback Groups
        self.service_cb_group = MutuallyExclusiveCallbackGroup()
        self.sub_cb_group = MutuallyExclusiveCallbackGroup()

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.image_req_pub = self.create_publisher(Image, request_image_topic, 10)
        self.marker_image_req_pub = self.create_publisher(Image, request_marker_image_topic, 10)
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

        # Trigger Service
        self.trigger_srv = self.create_service(
            Trigger,
            '~/trigger_recovery',
            self.trigger_callback,
            callback_group=self.service_cb_group
        )

        self.get_logger().info(f'Visual Recovery Node initialized with method: [{self.recovery_method}]. Manual recovery only.')

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
        # We check if it is a valid pose (non-empty)
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation
        if p.x == 0.0 and p.y == 0.0 and p.z == 0.0 and o.x == 0.0 and o.y == 0.0 and o.z == 0.0 and o.w == 0.0:
            self.get_logger().warn('Received empty/unsuccessful pose response.')
            return

        if self.received_pose is None:
            self.get_logger().info('Received a valid pose from the localization pipeline.')
            self.received_pose = msg

    def trigger_callback(self, request, response):
        success, message = self.run_recovery_sequence()
        response.success = success
        response.message = message
        return response

    def request_and_wait_pose(self, request_pub, response_topic, timeout_val):
        """Helper to request a pose from a localizer node and block/wait with a timeout."""
        self.received_pose = None
        
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            response_topic,
            self.pose_callback,
            10,
            callback_group=self.sub_cb_group
        )

        self.get_logger().info(f'Publishing captured image request to [{request_pub.topic}]...')
        request_pub.publish(self.captured_image)

        self.get_logger().info(f'Waiting up to {timeout_val} seconds for the pose response on [{response_topic}]...')
        time_waited = 0.0
        while self.received_pose is None and time_waited < timeout_val:
            time.sleep(0.1)
            time_waited += 0.1

        # Clean up subscription
        self.destroy_subscription(self.pose_sub)
        self.pose_sub = None

        return self.received_pose

    def run_recovery_sequence(self):
        if self.recovery_in_progress:
            msg = 'Recovery sequence already in progress.'
            self.get_logger().warn(msg)
            return False, msg

        self.recovery_in_progress = True
        self.captured_image = None
        self.received_pose = None

        # Fetch latest recovery method from parameters dynamically
        self.recovery_method = self.get_parameter('recovery_method').get_parameter_value().string_value
        method = self.recovery_method.lower()

        self.get_logger().info(f'=== Starting Recovery Sequence ({method.upper()} Method) ===')

        # 1. Halt Movement
        self.halt_movement()

        # 2. Capture Image from camera
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

        # 3. Trigger requested localization node
        pose_result = None
        if method == 'marker':
            pose_result = self.request_and_wait_pose(self.marker_image_req_pub, self.response_marker_pose_topic, 10.0)
        
        elif method == 'ai':
            pose_result = self.request_and_wait_pose(self.image_req_pub, self.response_pose_topic, self.timeout_seconds)
        
        elif method == 'hybrid':
            self.get_logger().info('Attempting fast Fiducial Marker localization first...')
            pose_result = self.request_and_wait_pose(self.marker_image_req_pub, self.response_marker_pose_topic, 5.0)
            if pose_result is None:
                self.get_logger().warn('Marker localization failed or returned no pose. Falling back to heavy 3D AI localization...')
                pose_result = self.request_and_wait_pose(self.image_req_pub, self.response_pose_topic, self.timeout_seconds)
        
        else:
            msg = f'Unknown recovery method: {self.recovery_method}. Aborting.'
            self.get_logger().error(msg)
            self.recovery_in_progress = False
            return False, msg

        if pose_result is None:
            msg = 'All relocalization pipelines failed to return a valid pose. Aborting.'
            self.get_logger().error(msg)
            self.recovery_in_progress = False
            return False, msg

        # 4. Pose Injection
        self.get_logger().info('Injecting 6DoF pose into AMCL/Slam-toolbox via /initialpose...')
        self.initialpose_pub.publish(pose_result)

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
