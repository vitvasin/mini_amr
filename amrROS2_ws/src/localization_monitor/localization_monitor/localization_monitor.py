#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import Bool
import numpy as np

class LocalizationMonitor(Node):
    def __init__(self):
        super().__init__('localization_monitor')
        
        # Thresholds - tune these values
        self.declare_parameter('covariance_threshold', 0.4)
        self.declare_parameter('check_interval', 1.0)
        
        self.covariance_threshold = self.get_parameter(
            'covariance_threshold').value
        
        self.last_pose_time = None
        self.localization_lost = False
        
        # Parameters
        self.declare_parameter('pose_timeout', 10.0)
        
        self.pose_timeout = self.get_parameter('pose_timeout').value
        
        # Subscribe to SLAM Toolbox pose output
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/pose',  # or '/slam_toolbox/pose'
            self.pose_callback,
            10
        )
        
        # Publisher for localization status
        self.status_pub = self.create_publisher(
            Bool,
            '/localization_status',
            10
        )
        
        # Timer to check pose timeout
        # self.timer = self.create_timer(
        #     self.get_parameter('check_interval').value,
        #     self.check_localization
        # )
        
        self.get_logger().info('Localization Monitor Started')

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        self.get_logger().debug('Received pose update')
        self.last_pose_time = self.get_clock().now()
        
        # Extract covariance (x, y are indices 0, 7 in 6x6 matrix)
        cov_x = msg.pose.covariance[0]   # xx
        cov_y = msg.pose.covariance[7]   # yy
        cov_yaw = msg.pose.covariance[35] # yaw-yaw
        
        max_cov = max(abs(cov_x), abs(cov_y), abs(cov_yaw))
        
        self.get_logger().debug(
            f'Covariance - X: {cov_x:.4f}, Y: {cov_y:.4f}, Yaw: {cov_yaw:.4f}'
        )
        
        if max_cov > self.covariance_threshold:
            if not self.localization_lost:
                self.localization_lost = True
                self.get_logger().error(
                    f'⚠️  LOCALIZATION LOST! High covariance detected: {max_cov:.4f}'
                )
                self.notify_user()
        else:
            if self.localization_lost:
                self.localization_lost = False
                self.get_logger().info('✅ Localization recovered')
        
        # Publish status
        status_msg = Bool()
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def check_localization(self):
        """Check if pose updates have stopped (timeout)"""
        status_msg = Bool()
        
        if self.last_pose_time is None:
            self.get_logger().debug('Waiting for initial pose...')
            status_msg.data = True
            self.status_pub.publish(status_msg)
            return
        
        elapsed = (self.get_clock().now() - self.last_pose_time).nanoseconds / 1e9
        
        if elapsed > self.pose_timeout:
            # Just log a warning, don't mark as localization lost
            self.get_logger().warn(f'No pose update for {elapsed:.1f}s')
        
        # Publish status
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def notify_user(self):
        """Notify user to restart localization"""
        self.get_logger().error('=' * 50)
        self.get_logger().error('LOCALIZATION FAILED!')
        self.get_logger().error('Please restart the program or re-initialize pose')
        self.get_logger().error('Run: ros2 service call /slam_toolbox/clear_changes ...')
        self.get_logger().error('=' * 50)


def main(args=None):
    rclpy.init(args=args)
    node = LocalizationMonitor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()