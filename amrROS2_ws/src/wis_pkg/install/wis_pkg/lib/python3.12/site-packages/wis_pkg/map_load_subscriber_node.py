#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import sqlite3
import time


class MapLoadSubscriberNode(Node): ## FOR NOP TEST
    
    def __init__(self):
        
        super().__init__('map_load_subscriber_node') # The node is named "map_load_subscriber_node"

        # Database connection
        # self.db_path = 'wis_data.db'  # Path to the SQLite database
        self.db_path = '/home/smr/workspaces/mini_amr/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db'  # Path to the SQLite database
        self.conn = sqlite3.connect(self.db_path)  # Connect to the database
        self.cursor = self.conn.cursor()  # Create a cursor to execute SQL queries
        
        # Subscribes to the topic "wis_map_load" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_load',
            self.listener_callback, # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg): 
        
        # self.get_logger().info(f'Received: "{msg.data}"') # The msg.data contains the received string
        
        # Check if the message data starts with "Floor_"
        if msg.data.startswith('Floor_'):
            self.request_new_map(msg.data)  # Call request_new_map if the condition is met
        # else:
            # self.get_logger().info(f'Ignoring message: "{msg.data}", does not start with "Floor_"')  # Do nothing if condition is not met

    def request_new_map(self, requested_map_name):

        try:
            # Update the value of map_name for map_type "requested_map"
            self.cursor.execute("""
            UPDATE types
            SET map_name = ?
            WHERE map_type = ?
            """, (requested_map_name, "current_map")) ## FOR NOP TEST

            time.sleep(10) ## FOR NOP TEST

            self.conn.commit()  # Commit the changes to the database
            # self.get_logger().info(f'Updated current_map to "{requested_map_name}" in the database.')

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
    node = MapLoadSubscriberNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "map_load = wis_pkg.map_load_subscriber_node:main",
# ros2 run wis_pkg map_load
