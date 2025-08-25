#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import paho.mqtt.publish as publish
import sqlite3

import json



class PointSaveSubscriberNode(Node):

    def __init__(self):

        super().__init__('point_save_subscriber_node')  # The node is named "point_save_subscriber_node"
        
        # Database connection
        self.db_path = '/home/smr/workspaces/mini_amr/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db'  # Path to the SQLite database
        self.conn = sqlite3.connect(self.db_path)  # Connect to the database
        self.cursor = self.conn.cursor()  # Create a cursor to execute SQL queries
        
        # Subscribes to the topic "wis_point_save" with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_point_save',
            self.listener_callback,  # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):

        # 1. Check if the message data contain "point_name" and "point_metada"
        try:
            msg_json = json.loads(msg.data)
            point_name = msg_json["point_name"] # String
            point_metadata = msg_json["point_metadata"] # String

            self.save_new_point(point_name, point_metadata)  # Call save_new_map if the condition is met
        
        except:
            self.get_logger().info(f'Ignoring message: "{msg.data}", does not contain "point_name" and "point_metada"')  # Do nothing if condition is not met

    def save_new_point(self, point_name, point_metadata):
        self.get_logger().info(f"point_name: {point_name}")
        self.get_logger().info(f"point_metadata: {point_metadata}")

        # 2. Query to get current_map_name data from table types
        if not self.conn:
            self.get_logger().error("Database connection is not available.")
            return

        try:
            self.cursor.execute("SELECT map_name FROM types WHERE map_type = 'current_map';")
            result = self.cursor.fetchone()

            if result:
                self.get_logger().info(f"current_map_name: {result[0]}")
                current_map_name = result[0]

                 # 3. Save new point in database
                try:
                    # 3.1 Check if the point already exists for the given map
                    self.cursor.execute("""
                    SELECT 1 FROM maps
                    WHERE map_name = ? AND point_name = ?
                    """, (current_map_name, point_name))

                    result = self.cursor.fetchone()

                    if result:
                        # 3.2 Update existing point_metadata
                        self.cursor.execute("""
                        UPDATE maps
                        SET point_metadata = ?
                        WHERE map_name = ? AND point_name = ?
                        """, (point_metadata, current_map_name, point_name))

                    else:
                        # 3.3 Insert new value into database
                        self.cursor.execute("""
                        INSERT INTO maps (map_name, point_name, point_metadata)
                        VALUES (?, ?, ?)
                        """, (current_map_name, point_name, point_metadata))

                    self.conn.commit()

                except sqlite3.Error as e:
                    self.get_logger().error(f"Database error: {e}")
                   
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
    node = PointSaveSubscriberNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()



if __name__ == '__main__':
    main()


# "point_save = wis_pkg.point_save_subscriber_node:main",
# ros2 run wis_pkg point_save