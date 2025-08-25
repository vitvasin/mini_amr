#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav2_msgs.msg import SpeedLimit

class SpeedLimitSubscriber(Node):

    def __init__(self):

        super().__init__('speed_limit_subscriber')

        self.subscription = self.create_subscription(
            SpeedLimit,         # Message type
            '/speed_limit',     # Topic name
            self.listener_callback,
            10                  # QoS history depth
        )
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):

        self.get_logger().info(
            f'Received SpeedLimit message:\n'
            f'  percentage: {msg.percentage}\n'
            f'  speed_limit: {msg.speed_limit}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = SpeedLimitSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
