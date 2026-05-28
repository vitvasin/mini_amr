#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from std_msgs.msg import Bool

class LocalizationMonitor(Node):
    def __init__(self):
        super().__init__('localization_monitor')
        
        # Parameters
        self.declare_parameter('covariance_threshold', 0.4)
        self.declare_parameter('check_interval', 1.0)
        self.declare_parameter('pose_timeout', 60.0)
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        
        self.covariance_threshold = self.get_parameter('covariance_threshold').value
        self.pose_timeout = self.get_parameter('pose_timeout').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        
        self.last_pose_time = None
        self.localization_lost = False
        
        # Movement Tracking to prevent false timeouts when stationary
        self.is_moving = False
        self.last_movement_time = self.get_clock().now()
        
        # Subscriptions
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/pose',
            self.pose_callback,
            10
        )
        
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            cmd_vel_topic,
            self.cmd_vel_callback,
            10
        )
        
        # Publisher
        self.status_pub = self.create_publisher(
            Bool,
            '/localization_status',
            10
        )
        
        # Timer to check pose timeout
        self.timer = self.create_timer(
            self.get_parameter('check_interval').value,
            self.check_localization
        )
        
        self.get_logger().info('Localization Monitor Started (Basic Logic + Stationary Timeout Fix)')

    def cmd_vel_callback(self, msg: Twist):
        moving = (abs(msg.linear.x) > 0.001 or 
                  abs(msg.linear.y) > 0.001 or 
                  abs(msg.angular.z) > 0.001)
        
        if moving:
            self.is_moving = True
            self.last_movement_time = self.get_clock().now()
        else:
            self.is_moving = False

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        self.last_pose_time = self.get_clock().now()
        
        cov_x = msg.pose.covariance[0]
        cov_y = msg.pose.covariance[7]
        cov_yaw = msg.pose.covariance[35]
        max_cov = max(abs(cov_x), abs(cov_y), abs(cov_yaw))
        
        # Basic if/else logic
        if max_cov > self.covariance_threshold:
            if not self.localization_lost:
                self.localization_lost = True
                self.get_logger().error(f'⚠️ LOCALIZATION LOST! High covariance: {max_cov:.4f}')
                self.notify_user()
        else:
            if self.localization_lost:
                self.localization_lost = False
                self.get_logger().info('✅ Localization recovered (covariance low)')
        
        # Publish status
        status_msg = Bool()
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def check_localization(self):
        status_msg = Bool()
        now = self.get_clock().now()
        
        # Suspend timeout if stationary for > 5s
        time_since_last_movement = (now - self.last_movement_time).nanoseconds / 1e9
        if not self.is_moving and time_since_last_movement > 5.0:
            if self.last_pose_time is not None:
                self.last_pose_time = now
        
        if self.last_pose_time is None:
            status_msg.data = True
            self.status_pub.publish(status_msg)
            return
        
        elapsed = (now - self.last_pose_time).nanoseconds / 1e9
        
        if elapsed > self.pose_timeout:
            if not self.localization_lost:
                self.localization_lost =  True
                self.get_logger().error(f'⚠️ LOCALIZATION LOST! Pose timeout: {elapsed:.1f}s')
                self.notify_user()
        
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def notify_user(self):
        self.get_logger().error('=' * 50)
        self.get_logger().error('LOCALIZATION FAILED! Relocalization triggered.')
        self.get_logger().error('=' * 50)

def main(args=None):
    rclpy.init(args=args)
    node = LocalizationMonitor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
