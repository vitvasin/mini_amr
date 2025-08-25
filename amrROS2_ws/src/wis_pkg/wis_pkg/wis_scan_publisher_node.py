import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class ScanForwarder(Node):
    def __init__(self):
        super().__init__('scan_forwarder')

        # Subscriber to /scan
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Publisher to /scan_forwarded
        self.publisher_ = self.create_publisher(
            LaserScan,
            '/scan_forwarded',
            10
        )

        self.get_logger().info('ScanForwarder node has been started.')

    def scan_callback(self, msg):
        # Log (optional)
        self.get_logger().info('Received /scan message, republishing...')

        # Forward the message
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ScanForwarder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped by user.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
