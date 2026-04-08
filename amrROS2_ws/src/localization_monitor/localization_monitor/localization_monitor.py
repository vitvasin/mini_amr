#!/usr/bin/env python3
"""
Localization Monitor Node for AMR (Autonomous Mobile Robot)

Monitors SLAM Toolbox pose covariance to detect localization failures.
Publishes a boolean status to /localization_status indicating if localization is lost.

Covariance Threshold Notes:
- Covariance values are in squared meters (m²) for position and rad² for orientation
- Typical SLAM Toolbox values: 0.01 (very confident) to 10+ (uncertain)
- Threshold of 2.0 means ~1.4m position uncertainty or ~1.4 rad (~80°) orientation uncertainty
- Adjust based on your specific use case and SLAM configuration
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import Bool


class LocalizationMonitor(Node):
    def __init__(self):
        super().__init__('localization_monitor')
        
        # Individual thresholds for position (x, y) and orientation (yaw)
        # Default: 2.0 m² for position (~1.4m uncertainty), 0.5 rad² for yaw (~57° uncertainty)
        self.declare_parameter('covariance_position_threshold', 2.0)
        self.declare_parameter('covariance_yaw_threshold', 0.5)
        
        self.covariance_position_threshold = self.get_parameter(
            'covariance_position_threshold').value
        self.covariance_yaw_threshold = self.get_parameter(
            'covariance_yaw_threshold').value
        
        self.last_pose_time = None
        self.localization_lost = False
        
        # Parameters
        self.declare_parameter('pose_timeout', 10.0)
        self.pose_timeout = self.get_parameter('pose_timeout').value
        
        # Hysteresis counters to prevent rapid toggling (debouncing)
        # lost_counter_threshold: consecutive high covariance readings before declaring lost
        # recovered_counter_threshold: consecutive low covariance readings before declaring recovered
        self.declare_parameter('lost_counter_threshold', 3)
        self.declare_parameter('recovered_counter_threshold', 2)
        self.lost_counter_threshold = self.get_parameter('lost_counter_threshold').value
        self.recovered_counter_threshold = self.get_parameter('recovered_counter_threshold').value
        self.lost_counter = 0
        self.recovered_counter = 0
        
        # Subscribe to SLAM Toolbox pose output
        # Topic can be '/pose', '/odom', '/slam_toolbox/odom', or custom
        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/pose',
            self.pose_callback,
            10
        )
        
        # Publisher for localization status
        self.status_pub = self.create_publisher(
            Bool,
            '/localization_status',
            10
        )
        
        self.get_logger().info('Localization Monitor Started')
        self.get_logger().info(
            f'Thresholds - Position: {self.covariance_position_threshold} m², '
            f'Yaw: {self.covariance_yaw_threshold} rad²'
        )
        self.get_logger().info(
            f'Hysteresis - Lost: {self.lost_counter_threshold} samples, '
            f'Recovered: {self.recovered_counter_threshold} samples'
        )

    def pose_callback(self, msg: PoseWithCovarianceStamped):
        """
        Callback for pose updates from SLAM Toolbox.
        Evaluates covariance values to detect localization quality.
        """
        self.last_pose_time = self.get_clock().now()
        
        # Extract covariance values from 6x6 covariance matrix (flattened to 36 elements)
        # Indices: 0=xx, 7=yy, 14=zz, 21=roll, 28=pitch, 35=yaw
        cov_x = msg.pose.covariance[0]      # Position X covariance (m²)
        cov_y = msg.pose.covariance[7]      # Position Y covariance (m²)
        cov_yaw = msg.pose.covariance[35]   # Orientation Yaw covariance (rad²)
        
        # Calculate maximum position covariance
        max_position_cov = max(cov_x, cov_y)
        
        self.get_logger().debug(
            f'Covariance - X: {cov_x:.4f}, Y: {cov_y:.4f}, '
            f'Max Position: {max_position_cov:.4f}, Yaw: {cov_yaw:.4f}'
        )
        
        # Check if ANY of the covariances exceed their thresholds
        is_high_covariance = (
            max_position_cov > self.covariance_position_threshold or
            cov_yaw > self.covariance_yaw_threshold
        )
        
        # Hysteresis logic to prevent rapid toggling
        if is_high_covariance:
            # High covariance detected
            self.lost_counter += 1
            self.recovered_counter = 0  # Reset recovery counter
            
            if self.lost_counter >= self.lost_counter_threshold:
                if not self.localization_lost:
                    self.localization_lost = True
                    self.get_logger().error(
                        f'⚠️  LOCALIZATION LOST! '
                        f'Max Position Cov: {max_position_cov:.4f} m² (threshold: {self.covariance_position_threshold}), '
                        f'Yaw Cov: {cov_yaw:.4f} rad² (threshold: {self.covariance_yaw_threshold})'
                    )
                    self.notify_user()
        else:
            # Low covariance - good localization
            self.recovered_counter += 1
            self.lost_counter = 0  # Reset lost counter
            
            if self.recovered_counter >= self.recovered_counter_threshold:
                if self.localization_lost:
                    self.localization_lost = False
                    self.get_logger().info(
                        f'✅ Localization recovered! '
                        f'Max Position Cov: {max_position_cov:.4f} m², '
                        f'Yaw Cov: {cov_yaw:.4f} rad²'
                    )
        
        # Publish status
        status_msg = Bool()
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def check_localization(self):
        """
        Check if pose updates have stopped (timeout).
        Can be used with a timer for periodic checks.
        """
        status_msg = Bool()
        
        if self.last_pose_time is None:
            self.get_logger().debug('Waiting for initial pose...')
            status_msg.data = True  # Assume OK while waiting
            self.status_pub.publish(status_msg)
            return
        
        elapsed = (self.get_clock().now() - self.last_pose_time).nanoseconds / 1e9
        
        if elapsed > self.pose_timeout:
            # Log warning but don't mark as localization lost
            # (pose timeout alone doesn't mean localization failed)
            self.get_logger().warn(f'No pose update for {elapsed:.1f}s')
        
        # Publish status
        status_msg.data = not self.localization_lost
        self.status_pub.publish(status_msg)

    def notify_user(self):
        """
        Notify user to take action when localization is lost.
        """
        self.get_logger().error('=' * 60)
        self.get_logger().error('LOCALIZATION FAILED!')
        self.get_logger().error('The robot has lost its position estimate.')
        self.get_logger().error('Options to recover:')
        self.get_logger().error('  1. Move robot to a known location on the map')
        self.get_logger().error('  2. Use 2D Pose Estimate in RViz to re-localize')
        self.get_logger().error('  3. Restart the AMR navigation stack')
        self.get_logger().error('  4. Clear SLAM changes: ros2 service call /slam_toolbox/clear_changes slam_toolbox/srv/ClearChanges')
        self.get_logger().error('=' * 60)


def main(args=None):
    """Main entry point for the localization monitor node."""
    rclpy.init(args=args)
    node = LocalizationMonitor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()