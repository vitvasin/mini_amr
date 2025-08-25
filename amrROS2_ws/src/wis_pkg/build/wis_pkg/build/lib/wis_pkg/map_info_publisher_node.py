#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
import json

import sqlite3

class MapInfoPublisherNode(Node):
    
    def __init__(self):
        
        super().__init__("map_info_publisher_node") # the node is named "map_info_publisher_node"
        self.publisher_ = self.create_publisher(String, "wis_map_info", 10) # A publisher is created to publish messages to the topic "wis_map_info" with a queue size of 10
        
        # Database connection
        # self.db_path = 'wis_data.db'  # Path to the SQLite database
        self.db_path = '/home/smr/workspaces/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db'  # Path to the SQLite database
        self.conn = sqlite3.connect(self.db_path)  # Connect to the database
        self.cursor = self.conn.cursor()  # Create a cursor to execute SQL queries
        
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.publish_json) # The timer triggers the publish_json function every second 

        
    def publish_json(self):
        
        try:
            
            # Query to get all data from table maps
            self.cursor.execute("SELECT * FROM maps;")
            all_data = self.cursor.fetchall()

            json_data = {"maps":{}}

            for row in all_data:
                
                if row[1] not in json_data["maps"]:
                    json_data["maps"][row[1]] = {"points":{}}
                
                json_data["maps"][row[1]]["points"][row[2]] = row[3]

            # Convert the JSON data to a string
            msg = String()
            msg.data = json.dumps(json_data)
            
            # Publish the data
            self.publisher_.publish(msg)
            # self.get_logger().info(f'Publishing JSON: {msg.data}')
        
        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")
            
        
    def destroy_node(self):
        # Close the database connection when the node is destroyed
        self.conn.close()
        super().destroy_node()		
        
# Initializes the node and keeps it running until interrupted
def main(args=None):
    
    rclpy.init(args=args)
    node = MapInfoPublisherNode()
    
    try:
        rclpy.spin(node)
        
    except KeyboardInterrupt:
        pass
        
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()		


# "map_info = wis_pkg.map_info_publisher_node:main",
# ros2 run wis_pkg map_info