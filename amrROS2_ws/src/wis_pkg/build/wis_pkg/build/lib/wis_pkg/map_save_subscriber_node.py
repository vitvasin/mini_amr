import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from slam_toolbox.srv import SaveMap, SerializePoseGraph  # Import service types # https://github.com/SteveMacenski/slam_toolbox/tree/ros2/srv


class MapSaveSubscriberNode(Node):

    def __init__(self):

        super().__init__('map_save_subscriber_node')  # The node is named "map_save_subscriber_node"

        # SaveMap service
        self.save_cli = self.create_client(SaveMap, '/miniRobot/slam_toolbox/save_map')
        
        while not self.save_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('SaveMap service not available, waiting again...')
        self.save_req = SaveMap.Request()

        # SerializePoseGraph service
        self.serialize_cli = self.create_client(SerializePoseGraph, '/miniRobot/slam_toolbox/serialize_map')

        while not self.serialize_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('SerializePoseGraph service not available, waiting again...')
        self.serialize_req = SerializePoseGraph.Request()
        
        # Subscribes to the topic "wis_map_save" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_save',
            self.listener_callback,  # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def send_save_request(self, new_map_path):
        self.get_logger().info('send_save_request')

        self.save_req.name.data = new_map_path
        self.future = self.save_cli.call_async(self.save_req)
        self.get_logger().info('send_save_request - 2')
        rclpy.spin_until_future_complete(self, self.future)
        self.get_logger().info('send_save_request - 3')
        return self.future.result()
    
    def send_serialize_request(self, new_map_path):
        self.get_logger().info('send_serialize_request')

        self.serialize_req.filename = new_map_path
        self.future = self.serialize_cli.call_async(self.serialize_req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    def listener_callback(self, msg):

        # Check if the message data starts with "Floor_"
        if msg.data.startswith('Floor_'):
            self.get_logger().info(f'Received map save request for floor: "{msg.data}"')
            self.save_new_map(msg.data)  # Call save_new_map if the condition is met
        else:
            self.get_logger().info(f'Ignoring message: "{msg.data}", does not start with "Floor_"')  # Do nothing if condition is not met

    def save_new_map(self, new_map_name):

        self.get_logger().info('save_new_map')

        # Construct the new map path
        new_map_path = f'/home/smr/maps/{new_map_name}'
        
        # Save map using SaveMap service
        save_response = self.send_save_request(new_map_path)

        if save_response is not None:
            self.get_logger().info('Map saved successfully.')
            self.get_logger().info(str(save_response))
        else:
            self.get_logger().error('Failed to call SaveMap service.')

        # Serialize pose graph using SerializePoseGraph service
        serialize_response = self.send_serialize_request(new_map_path)

        if serialize_response is not None:
            self.get_logger().info('Map serialized successfully.')
            self.get_logger().info(str(serialize_response))
        else:
            self.get_logger().error('Failed to call SerializePoseGraph service.')


# Initializes the node and keeps it running until interrupted
def main(args=None):

    rclpy.init(args=args)
    node = MapSaveSubscriberNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "map_save = wis_pkg.map_save_subscriber_node:main",
# ros2 run wis_pkg map_save