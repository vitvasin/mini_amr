import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

class CameraCheckNode(Node):
    def __init__(self):
        super().__init__('camera_check_node')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )
        self.get_logger().info("Subscribed to /image_raw. Waiting for a frame...")
        self.frame_captured = False

    def image_callback(self, msg):
        if self.frame_captured:
            return
        
        self.get_logger().info("Frame received! Processing...")
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            
            # Using standard DICT_4X4_50
            dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters()
            
            # Use modern API if available
            try:
                detector = cv2.aruco.ArucoDetector(dictionary, parameters)
                corners, ids, rejected = detector.detectMarkers(gray)
            except AttributeError:
                corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
            
            if ids is not None:
                detected_ids = [int(i[0]) for i in ids]
                self.get_logger().info(f"Detected Marker IDs: {detected_ids}")
                cv2.aruco.drawDetectedMarkers(cv_img, corners, ids)
            else:
                self.get_logger().info("No markers detected.")
                detected_ids = []

            # Save the captured image to workspace path
            out_path = "/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/camera_capture.jpg"
            cv2.imwrite(out_path, cv_img)
            self.get_logger().info(f"Saved annotated image to {out_path}")
            
            self.frame_captured = True
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            self.frame_captured = True

def main():
    rclpy.init()
    node = CameraCheckNode()
    
    start_time = time.time()
    while rclpy.ok() and not node.frame_captured:
        rclpy.spin_once(node, timeout_sec=0.1)
        if time.time() - start_time > 10.0:
            node.get_logger().warn("Timeout waiting for image frame (10 seconds).")
            break
            
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
