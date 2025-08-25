#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import subprocess
import time

import sqlite3

class MapNavSubscriberNode(Node):
    def __init__(self):

        super().__init__('map_nav_subscriber_node') # The node is named "map_nav_subscriber_node"

        # Database connection
        # self.declare_parameter('db_path', 'wis_data.db')  # Declare a parameter for the database path
        self.declare_parameter('db_path', '/home/smr/workspaces/amrROS2_ws/src/wis_pkg/wis_pkg/wis_data.db')  # Declare a parameter for the database path
        self.db_path = self.get_parameter('db_path').get_parameter_value().string_value

        try:
            self.conn = sqlite3.connect(self.db_path)  # Connect to the database
            self.cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        except sqlite3.Error as e:
            self.get_logger().error(f"Failed to connect to database: {e}")
            self.conn = None
        
        # Subscribe to the "wis_map_nav" topic with a queue size of 10
        self.subscription = self.create_subscription(
            String,
            'wis_map_nav',
            self.listener_callback, # When a message is received, the listener_callback function is triggered
            10
        )
        self.subscription  # Prevent unused variable warning

        self.launch_service_instance = None

    def listener_callback(self, msg):

        self.get_logger().info(f'Received: "{msg.data}"') # Log the received string

        if msg.data == "Start":

            current_map_name = self.get_current_map_name()
            requested_map_name = self.get_requested_map_name()

            if (current_map_name is None) or (requested_map_name is None):
                self.get_logger().warning("Failed to get map_name value.")

            elif current_map_name == requested_map_name:\
                self.get_logger().info("The requested map has already used.")

            else:
                # Start the process if not already running
                if self.launch_service_instance is None:
                    self.start_process(requested_map_name)
                else:
                    self.get_logger().warning("A process is already running. Ignoring new start request.")
        
        elif msg.data == "Stop":
            if self.launch_service_instance is None:
                self.get_logger().warning("No process running to stop.")
            else:
                self.stop_process()
        
        else:
            self.get_logger().warning(f"Invalid request: {msg.data}")

    def start_process(self, requested_map_name):

        try:
            ''' #### PIN: Close for test
            # Execute the MQTT start command
            subprocess.run(
                ["mosquitto_pub", "-h", "localhost", "-p", "1883", "-t", "mode", "-m", "nav"],
                check=True
            )
            '''
            
            self.get_logger().info("Process started with MQTT command: nav")
            self.launch_service_instance = True # Set the instance as running
            
            # Wait until the nav mode is ready
            time.sleep(10) 

            # Update current map name
            self.update_current_map_name(requested_map_name)

        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to start process: {e}")
        
        except Exception as e:
            self.get_logger().error(f"Unexpected error: {e}")

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
    
    def get_current_map_name(self):

        if not self.conn:
            self.get_logger().error("Database connection is not available.")
            return None
        
        try:
            self.cursor.execute("SELECT map_name FROM types WHERE map_type = 'current_map';")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")
            return None


    def get_requested_map_name(self):

        if not self.conn:
            self.get_logger().error("Database connection is not available.")
            return None

        try:
            self.cursor.execute("SELECT map_name FROM types WHERE map_type = 'requested_map';")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")
            return None

    def update_current_map_name(self, requested_map_name):
        
        try:
            # Update the value of map_name for map_type "current_map"
            self.cursor.execute("""
            UPDATE types
            SET map_name = ?
            WHERE map_type = ?
            """, (requested_map_name, "current_map"))
            self.conn.commit()  # Commit the changes to the database
            self.get_logger().info(f'Updated current_map to "{requested_map_name}" in the database.')

        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")

    def destroy_node(self):

        # Close the database connection before destroying the node
        if self.conn:
            self.conn.close()
            self.get_logger().info("Database connection closed.")
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
