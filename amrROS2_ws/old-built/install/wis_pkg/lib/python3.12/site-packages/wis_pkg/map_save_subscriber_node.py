#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import sqlite3




class MapSaveSubscriberNode(Node):

    def __init__(self):

        super().__init__('map_save_subscriber_node')  # The node is named "map_save_subscriber_node"
        
        # Database connection
        self.db_path = '/home/smr/workspaces/mini_amr/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db'  # Path to the SQLite database
        self.conn = sqlite3.connect(self.db_path)  # Connect to the database
        self.cursor = self.conn.cursor()  # Create a cursor to execute SQL queries
        
        # Subscribes to the topic "wis_map_save" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_save',
            self.listener_callback,  # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):

        # 1. Check if the message data starts with "Floor_"
        if msg.data.startswith('Floor_'):
            # self.get_logger().info(f'Received map save request for floor: "{msg.data}"')
            self.save_new_map(msg.data)  # Call save_new_map if the condition is met
        
        else:
            self.get_logger().info(f'Ignoring message: "{msg.data}", does not start with "Floor_"')  # Do nothing if condition is not met

    def save_new_map(self, new_map_name):

        # 2. Save map using save mode
        try:
            # Construct the MQTT message
            mqtt_message_save = f"save"

            publish.single(
            topic="mode",
            payload=mqtt_message_save,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_save}")

        except:
            self.get_logger().error(f"Failed to publish MQTT message")

        # 3. Change name of the new map files (.data and .posegraph) fromt "new_map" to the received name
        try:
            # Construct the MQTT message in the format 'wis:old_name:new_name'
            mqtt_message_wis = f"wis:new_map:{new_map_name}"

            publish.single(
            topic="mode",
            payload=mqtt_message_wis,
            hostname="localhost",
            port=1883
            )

            # self.get_logger().info(f"Published MQTT message: {mqtt_message_wis}")

        except:
            self.get_logger().error(f"Failed to publish MQTT message")
 
        # 4. Save an example point in database
        try:
            # Insert new value into database
            self.cursor.execute("""
            INSERT INTO maps (map_name, point_name, point_metadata)
            VALUES (?, ?, ?)
            """, (new_map_name, "change_map_initial", ""))

            self.conn.commit()

        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")
        
    def destroy_node(self):

        # Close the database connection before destroying the node
        if self.conn:
            self.conn.close()
            # self.get_logger().info("Database connection closed.")
        
        super().destroy_node()
        
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