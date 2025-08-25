import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess  # Import subprocess for running shell commands

class MapScanSubscriberNode(Node):
    
    def __init__(self):
        super().__init__('map_scan_subscriber_node')  # The node is named "map_scan_subscriber_node"
        
        # Subscribes to the topic "wis_map_scan" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_scan',
            self.listener_callback,  # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

        self.launch_service_instance = None  # To store the launch service instance

    def listener_callback(self, msg): 
        self.get_logger().info(f'Received: "{msg.data}"')  # Log the received string

        if msg.data == "Start":

            # Start the process if not already running
            if self.launch_service_instance is None:
                self.start_process()
            else:
                self.get_logger().warning("A process is already running. Ignoring new start request.")

        elif msg.data == "Stop":

            # Stop the process if already running
            if self.launch_service_instance is None:
                self.get_logger().warning("A process is not already running. Ignoring new stop request.")
            else:
                self.stop_process()

        else:
            self.get_logger().warning("Invalid request.")

    def start_process(self):
        try:
            ''' #### PIN: Close for test
            # Execute the MQTT start command
            subprocess.run(
                ["mosquitto_pub", "-h", "localhost", "-p", "1883", "-t", "mode", "-m", "map"],
                check=True
            )
            '''

            self.get_logger().info("Process started with MQTT command: map")
            self.launch_service_instance = True  # Set the instance as running

        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to start process: {e}")
            
        except Exception as e:
            self.get_logger().error(f"An unexpected error occurred: {e}")

    def stop_process(self):
        try:
            ''' #### PIN: Close for test
            # Execute the MQTT stop command
            subprocess.run(
                ["mosquitto_pub", "-h", "localhost", "-p", "1883", "-t", "mode", "-m", "stop"],
                check=True
            )
            '''

            self.get_logger().info("Process stopped with MQTT command: stop")
            self.launch_service_instance = None  # Reset the instance

        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to stop process: {e}")

        except Exception as e:
            self.get_logger().error(f"An unexpected error occurred: {e}")
    
    def destroy_node(self):
        super().destroy_node()


# Initializes the node and keeps it running until interrupted
def main(args=None):
    rclpy.init(args=args)
    node = MapScanSubscriberNode()
    
    try:
        rclpy.spin(node)
        
    except KeyboardInterrupt:
        pass
        
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

# "map_scan = wis_pkg.map_scan_subscriber_node:main",
# ros2 run wis_pkg map_scan