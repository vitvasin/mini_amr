#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import sqlite3


class MapNamePublisherNode(Node):

    def __init__(self):

        super().__init__("map_name_publisher_node")  # The node is named "map_name_publisher_node"
        self.publisher_ = self.create_publisher(String, "wis_map_name", 10) # A publisher is created to publish messages to the topic "wis_map_name" with a queue size of 10

        self.current_map_name = ""
        self.previous_map_name = ""  # To track changes in the map name

        # Database connection
        self.declare_parameter('db_path', '/home/smr/workspaces/mini_amr/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db')  # Declare a parameter for the database path
        self.db_path = self.get_parameter('db_path').get_parameter_value().string_value

        try:
            self.conn = sqlite3.connect(self.db_path)  # Connect to the database
            self.cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        except sqlite3.Error as e:
            self.get_logger().error(f"Failed to connect to database: {e}")
            self.conn = None

        # Timer to trigger `publish_message`
        timer_period = 5.0  # seconds
        self.timer = self.create_timer(timer_period, self.publish_message)

    def publish_message(self):

        if not self.conn:
            self.get_logger().error("Database connection is not available.")
            return

        try:

            # 1.
            self.cursor.execute("SELECT map_name FROM types WHERE map_type = 'current_map';")
            result = self.cursor.fetchone()
            if result:
                # self.get_logger().info(f"current_map_name: {result[0]}")
                self.current_map_name = result[0]

            # 2. Publish the map name
            msg = String()
            msg.data = self.current_map_name
            self.publisher_.publish(msg)
            # self.get_logger().info(f'Publishing: "{msg.data}"')

            # Publish only if the map name has changed
            # if self.current_map_name != self.previous_map_name:
            #     msg = String()
            #     msg.data = self.current_map_name
            #     self.publisher_.publish(msg)
            #     self.get_logger().info(f'Published: "{msg.data}"')
            #     self.previous_map_name = self.current_map_name  # Update previous map name
        
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
    node = MapNamePublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# "map_name = wis_pkg.map_name_publisher_node:main"
# ros2 run wis_pkg map_name
# ros2 run wis_pkg map_name --ros-args --params-file wis_config.yaml