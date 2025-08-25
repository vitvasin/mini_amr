#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import time




class MapNavSubscriberNode(Node):

    def __init__(self):

        super().__init__('map_nav_subscriber_node') # The node is named "map_nav_subscriber_node"
        
        # Subscribe to the "wis_map_nav" topic with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_nav',
            self.listener_callback, # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

        # self.launch_service_instance = None

    def listener_callback(self, msg):

        # self.get_logger().info(f'Received: "{msg.data}"') # Log the received string

        if msg.data == "Start":

            # Start the process if not already running
            # if self.launch_service_instance is None:
            if True:
                self.start_process()
            else:
                self.get_logger().warning("A process is already running. Ignoring new start request.")
        
        elif msg.data == "Stop":

            # if self.launch_service_instance is None:
            if False:
                self.get_logger().warning("No process running to stop.")
            else:
                self.stop_process()
        
        else:
            self.get_logger().warning(f"Invalid request: {msg.data}")

    def start_process(self):

        # 1. Start the navigation mode
        try:
            # Construct the MQTT message
            mqtt_message_nav = f"nav"

            publish.single(
            topic="mode",
            payload=mqtt_message_nav,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_nav}")
            # self.launch_service_instance = True # Set the instance as running

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

        # 2. Wait for the navigation mode start
        time.sleep(5)

    def stop_process(self):

        # 3. Stop navigation mode
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
        
        # 4. Wait for the navigation mode stop
        time.sleep(15)

    def destroy_node(self):
        super().destroy_node()


# Initializes the node and keeps it running until interrupted
def main(args=None):

    rclpy.init(args=args)
    node = MapNavSubscriberNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "map_nav = wis_pkg.map_nav_subscriber_node:main",
# ros2 run wis_pkg map_nav
