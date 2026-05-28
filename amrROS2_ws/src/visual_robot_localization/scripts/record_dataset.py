#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
import cv2
from cv_bridge import CvBridge
import os
import json
import time

class DatasetRecorder(Node):
    def __init__(self):
        super().__init__('dataset_recorder')
        self.declare_parameter('output_dir', './image_dataset')
        self.declare_parameter('record_interval_sec', 1.0)
        
        self.output_dir = self.get_parameter('output_dir').value
        self.record_interval = self.get_parameter('record_interval_sec').value
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.bridge = CvBridge()
        self.latest_odom = None
        self.image_counter = 0
        self.last_record_time = time.time()
        
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(Image, '/image_raw', self.image_callback, 10)
        
        self.get_logger().info(f"Dataset Recorder started. Saving to {self.output_dir}")

    def odom_callback(self, msg):
        self.latest_odom = msg

    def image_callback(self, msg):
        current_time = time.time()
        if current_time - self.last_record_time < self.record_interval:
            return
            
        if self.latest_odom is None:
            self.get_logger().warn("Waiting for /odom messages...")
            return
            
        self.last_record_time = current_time
        self.image_counter += 1
        
        # Save Image
        img_name = f"{self.image_counter:05d}.png"
        img_path = os.path.join(self.output_dir, img_name)
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imwrite(img_path, cv_image)
        
        # Save Odometry JSON
        odom_name = f"{self.image_counter:05d}_odometry_camera.json"
        odom_path = os.path.join(self.output_dir, odom_name)
        
        odom_data = {
            "pose": {
                "pose": {
                    "position": {
                        "x": self.latest_odom.pose.pose.position.x,
                        "y": self.latest_odom.pose.pose.position.y,
                        "z": self.latest_odom.pose.pose.position.z
                    },
                    "orientation": {
                        "x": self.latest_odom.pose.pose.orientation.x,
                        "y": self.latest_odom.pose.pose.orientation.y,
                        "z": self.latest_odom.pose.pose.orientation.z,
                        "w": self.latest_odom.pose.pose.orientation.w
                    }
                }
            }
        }
        
        with open(odom_path, 'w') as f:
            json.dump(odom_data, f, indent=4)
            
        self.get_logger().info(f"Saved {img_name} and {odom_name}")

def main(args=None):
    rclpy.init(args=args)
    node = DatasetRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
