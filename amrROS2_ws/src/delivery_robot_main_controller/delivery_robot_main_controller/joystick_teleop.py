"""Simple joystick teleoperation node for the delivery robot.

This node listens to `sensor_msgs/msg/Joy` messages (e.g. from the `joy` node)
and publishes velocity commands on `/cmd_vel`.  It mirrors the behaviour of the
common `teleop_twist_joy` package but keeps the logic local to this workspace so
that it can be customised alongside the main controller.
"""

from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy


class JoystickTeleop(Node):
    """Convert joystick input to Twist velocity commands."""

    def __init__(self) -> None:
        super().__init__('joystick_teleop')

        # Axis mappings default to a typical Xbox / generic gamepad layout.
        self.declare_parameter('axis_linear', 1)
        self.declare_parameter('axis_angular', 0)

        # Velocity scaling factors (m/s and rad/s respectively).
        self.declare_parameter('scale_linear', 0.5)
        self.declare_parameter('scale_angular', 1.5)
        self.declare_parameter('scale_linear_turbo', 1.0)
        self.declare_parameter('scale_angular_turbo', 3.0)

        # Button indices for enabling / turbo modes (-1 disables the feature).
        self.declare_parameter('enable_button', -1)
        self.declare_parameter('enable_turbo_button', 4)

        # Stop publishing a non-zero Twist if no joystick activity is received.
        self.declare_parameter('command_timeout', 0.5)  # seconds
        self.declare_parameter('publish_rate', 20.0)  # Hz

        qos_profile = QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
        )
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            qos_profile,
        )
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        publish_period = 1.0 / self.get_parameter('publish_rate').get_parameter_value().double_value
        self.timer = self.create_timer(publish_period, self._publish_safe_stop)

        self._last_joy_time: Optional[float] = None
        self._last_twist = Twist()

        self.get_logger().info('Joystick teleop ready (waiting for /joy messages)')

    def joy_callback(self, msg: Joy) -> None:
        axis_linear = self.get_parameter('axis_linear').get_parameter_value().integer_value
        axis_angular = self.get_parameter('axis_angular').get_parameter_value().integer_value
        scale_linear = self.get_parameter('scale_linear').get_parameter_value().double_value
        scale_angular = self.get_parameter('scale_angular').get_parameter_value().double_value
        scale_linear_turbo = self.get_parameter('scale_linear_turbo').get_parameter_value().double_value
        scale_angular_turbo = self.get_parameter('scale_angular_turbo').get_parameter_value().double_value
        enable_button = self.get_parameter('enable_button').get_parameter_value().integer_value
        enable_turbo_button = self.get_parameter('enable_turbo_button').get_parameter_value().integer_value

        enabled = True
        if 0 <= enable_button < len(msg.buttons):
            enabled = msg.buttons[enable_button] == 1

        if not enabled:
            twist = Twist()
            self._publish(twist)
            return

        turbo = False
        if 0 <= enable_turbo_button < len(msg.buttons):
            turbo = msg.buttons[enable_turbo_button] == 1

        linear_scale = scale_linear_turbo if turbo else scale_linear
        angular_scale = scale_angular_turbo if turbo else scale_angular

        twist = Twist()
        if 0 <= axis_linear < len(msg.axes):
            twist.linear.x = msg.axes[axis_linear] * linear_scale
        if 0 <= axis_angular < len(msg.axes):
            twist.angular.z = msg.axes[axis_angular] * angular_scale

        self._publish(twist)

    def _publish(self, twist: Twist) -> None:
        self._last_twist = twist
        now = self.get_clock().now().nanoseconds / 1e9
        self._last_joy_time = now
        self.cmd_vel_pub.publish(twist)

    def _publish_safe_stop(self) -> None:
        if self._last_joy_time is None:
            return
        timeout = self.get_parameter('command_timeout').get_parameter_value().double_value
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self._last_joy_time > timeout and (
            self._last_twist.linear.x != 0.0 or self._last_twist.angular.z != 0.0
        ):
            self.get_logger().debug('Joystick timeout reached, publishing stop command')
            self._publish(Twist())


def main(args=None) -> None:
    rclpy.init(args=args)
    node = JoystickTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
