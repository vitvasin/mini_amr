#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import time




class MapShutdownSubscriberNode(Node):

    def __init__(self):

        super().__init__('map_shutdown_subscriber_node') # The node is named "map_shutdown_subscriber_node"
        
        # Subscribe to the "wis_map_shutdown" topic with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_shutdown',
            self.listener_callback, # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):

        # self.get_logger().info(f'Received: "{msg.data}"') # Log the received string

        if msg.data == "Shutdown":
            self.shutdown_process()
            
        
        elif msg.data == "Restart":
           self.restart_process()
        
        else:
            self.get_logger().warning(f"Invalid request: {msg.data}")

    def shutdown_process(self):

        # 1. Stop navigation or map mode
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

        except:
            self.get_logger().error(f"Failed to publish MQTT message")
        
        # 2. Wait for the navigation mode stop
        time.sleep(15)

        # 3. Start the shutdown mode
        try:
            # Construct the MQTT message
            mqtt_message_shutdown = f"shutdown"

            publish.single(
            topic="mode",
            payload=mqtt_message_shutdown,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_shutdown}")

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

    def restart_process(self):

        # 4. Stop navigation or map mode
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

        except:
            self.get_logger().error(f"Failed to publish MQTT message")
        
        # 5. Wait for the navigation mode stop
        time.sleep(15)

        # 6. Start the navigation mode
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

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

        # 7. Wait for the navigation mode start
        time.sleep(5)

    def destroy_node(self):
        super().destroy_node()


# Initializes the node and keeps it running until interrupted
def main(args=None):

    rclpy.init(args=args)
    node = MapShutdownSubscriberNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "map_shutdown = wis_pkg.map_shutdown_subscriber_node:main",
# ros2 run wis_pkg map_shutdown
