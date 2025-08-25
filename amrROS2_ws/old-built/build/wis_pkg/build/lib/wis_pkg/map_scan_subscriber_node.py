#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import time




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

        # self.launch_service_instance = None  # To store the launch service instance

    def listener_callback(self, msg): 

        # self.get_logger().info(f'Received: "{msg.data}"')  # Log the received string

        if msg.data == "Start":

            # Start the process if not already running
            # if self.launch_service_instance is None:
            if True:
                self.start_process()
            else:
                self.get_logger().warning("A process is already running. Ignoring new start request.")

        elif msg.data == "Stop":

            # Stop the process if already running
            # if self.launch_service_instance is None:
            if False:
                self.get_logger().warning("A process is not already running. Ignoring new stop request.")
            else:
                self.stop_process()

        else:
            self.get_logger().warning("Invalid request.")

    def start_process(self):

        # 1. Start the map mode
        try:
            # Construct the MQTT message
            mqtt_message_map = f"map"

            publish.single(
            topic="mode",
            payload=mqtt_message_map,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_map}")
            # self.launch_service_instance = True # Set the instance as running

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

        # 2. Wait for the map mode start
        time.sleep(5)

    def stop_process(self):

        # 3. Stop map mode
        try:
            # Construct the MQTT message
            mqtt_message_stop = f"stop"

            publish.single(
            topic="mode",
            payload=mqtt_message_stop,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_stop}")
            # self.launch_service_instance = None  # Reset the instance

        except:
            self.get_logger().error(f"Failed to publish MQTT message")
        
        # 4. Wait for the map mode stop
        time.sleep(15)

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