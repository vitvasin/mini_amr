#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import sqlite3
import time

import paho.mqtt.publish as publish



class MapLoadSubscriberNode(Node): ## FOR NOP TEST
    
    def __init__(self):
        
        super().__init__('map_load_subscriber_node') # The node is named "map_load_subscriber_node"

        # Database connection
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
        
        # 1. Check if the message data starts with "Floor_"
        if msg.data.startswith('Floor_'):
            self.request_new_map(msg.data)  # Call request_new_map if the condition is met
        # else:
            # self.get_logger().info(f'Ignoring message: "{msg.data}", does not start with "Floor_"')  # Do nothing if condition is not met

    def request_new_map(self, requested_map_name):

        # 2. Updated "requested_map" to requested_map_name in the database
        try:
            # Update the value of map_name for map_type "requested_map"
            self.cursor.execute("""
            UPDATE types
            SET map_name = ?
            WHERE map_type = ?
            """, (requested_map_name, "requested_map"))

            self.conn.commit()  # Commit the changes to the database

        except sqlite3.Error as e:
            self.get_logger().error(f"Database error: {e}")

        # 3. Retrieve the map_name for map_type = "current_map" from the database
        try:
            # Execute a SELECT query to get the map_name where map_type is "current_map"
            self.cursor.execute("""
            SELECT map_name FROM types WHERE map_type = ?
            """, ("current_map",))

            result = self.cursor.fetchone()  # Fetch one result

        except:
            self.get_logger().error(f"Database error: {e}")

        if result:
            current_map_name = result[0]
            print(f"Current map name: {current_map_name}")

            if requested_map_name != current_map_name:

                # 4. Stop navigation mode
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
                    self.get_logger().error(f"Failed to publish MQTT message: {e}")
                
                # 5. Wait for the navigation mode stop
                time.sleep(15)
                
                # 6. Change name of the current map files (.data and .posegraph) fromt "map" to its actual name 
                try:
                    # Construct the MQTT message in the format 'wis:old_name:new_name'
                    mqtt_message_wis = f"wis:map:{current_map_name}"

                    publish.single(
                    topic="mode",
                    payload=mqtt_message_wis,
                    hostname="localhost",
                    port=1883
                    )

                    # self.get_logger().info(f"Published MQTT message: {mqtt_message_wis}")

                except:
                    self.get_logger().error(f"Failed to publish MQTT message: {e}")

                # 7. Change name of the requested map files (.data and .posegraph) to "map" 
                try:
                    # Construct the MQTT message in the format 'wis:old_name:new_name'
                    mqtt_message_wis = f"wis:{requested_map_name}:map"

                    publish.single(
                    topic="mode",
                    payload=mqtt_message_wis,
                    hostname="localhost",
                    port=1883
                    )

                    # self.get_logger().info(f"Published MQTT message: {mqtt_message_wis}")

                except:
                    self.get_logger().error(f"Failed to publish MQTT message: {e}")

                # 8. Start the navigation mode with new map
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
                    self.get_logger().error(f"Failed to publish MQTT message: {e}")

                # 9. Wait for the navigation mode start
                time.sleep(5)

                # 10. Updated "current_map" to requested_map_name in the database
                try:
                    # Update the value of map_name for map_type "current_map"
                    self.cursor.execute("""
                    UPDATE types
                    SET map_name = ?
                    WHERE map_type = ?
                    """, (requested_map_name, "current_map"))

                    self.conn.commit()  # Commit the changes to the database

                except sqlite3.Error as e:
                    self.get_logger().error(f"Database error: {e}")

        else:
            self.get_logger().error("Database error: No entry found for map_type = 'current_map'")
    


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