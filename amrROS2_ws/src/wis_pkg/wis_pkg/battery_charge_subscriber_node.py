#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import time


class BatteryChargeSubscriberNode(Node):

    def __init__(self):

        super().__init__('battery_charge_subscriber_node') # The node is named "battery_charge_subscriber_node"

        # Subscribes to the topic "wis_battery_charge" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_battery_charge',
            self.listener_callback, # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):

        # self.get_logger().info(f'Received: "{msg.data}"') # Log the received string

        if msg.data == "Charge":
            self.start_charging()
            # self.get_logger().info(f"Start charging!")

        else:
            self.get_logger().warning(f"Invalid request: {msg.data}")

    def start_charging(self):

        # 1. Start charging
        try:
            # Construct the MQTT message
            mqtt_message_charge = f"charge"

            publish.single(
            topic="mode",
            payload=mqtt_message_charge,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_charge}")

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

    def destroy_node(self):
        super().destroy_node()


# Initializes the node and keeps it running until interrupted
def main(args=None):

    rclpy.init(args=args)
    node = BatteryChargeSubscriberNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "battery_charge = wis_pkg.battery_charge_subscriber_node:main",
# ros2 run wis_pkg battery_charge
