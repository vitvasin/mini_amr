#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np

class MarkerDebugPublisher(Node):
    def __init__(self):
        super().__init__('marker_debug_publisher')
        
        self.declare_parameter('camera_topic', '/image_raw')
        self.declare_parameter('camera_info_topic', '/camera_info')
        self.declare_parameter('marker_size', 0.15)
        self.declare_parameter('marker_dictionary_name', 'DICT_4X4_50')
        
        camera_topic = self.get_parameter('camera_topic').value
        camera_info_topic = self.get_parameter('camera_info_topic').value
        self.marker_size = self.get_parameter('marker_size').value
        dict_name = self.get_parameter('marker_dictionary_name').value
        
        # ArUco dictionary setup
        mapping = {
            'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
            'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
            'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
            'DICT_4X4_1000': cv2.aruco.DICT_4X4_1000,
            'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
            'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
            'DICT_5X5_250': cv2.aruco.DICT_5X5_250,
            'DICT_5X5_1000': cv2.aruco.DICT_5X5_1000,
            'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
            'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
            'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
            'DICT_6X6_1000': cv2.aruco.DICT_6X6_1000,
        }
        val = mapping.get(dict_name, cv2.aruco.DICT_4X4_50)
        self.dictionary = cv2.aruco.getPredefinedDictionary(val)
        self.detector_params = cv2.aruco.DetectorParameters()
        
        try:
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.detector_params)
        except AttributeError:
            self.detector = None
            
        self.bridge = CvBridge()
        self.K = None
        self.D = None
        
        # Subscribers
        self.info_sub = self.create_subscription(CameraInfo, camera_info_topic, self.info_callback, 10)
        self.img_sub = self.create_subscription(Image, camera_topic, self.image_callback, 10)
        
        # Publisher for the annotated image stream
        self.img_pub = self.create_publisher(Image, '/marker_localization/annotated_image', 10)
        
        self.get_logger().info("Marker Debug Publisher Node started.")
        self.get_logger().info(f"Subscribing to: {camera_topic}")
        self.get_logger().info("Publishing annotated stream to: /marker_localization/annotated_image")

    def info_callback(self, msg):
        self.K = np.array(msg.k).reshape(3, 3)
        self.D = np.array(msg.d)

    def image_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            
            # Detect markers
            if self.detector is not None:
                corners, ids, _ = self.detector.detectMarkers(gray)
            else:
                corners, ids, _ = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.detector_params)
                
            if ids is not None and len(ids) > 0:
                # Draw marker borders
                cv2.aruco.drawDetectedMarkers(cv_img, corners, ids)
                
                # Draw 3D axis if camera calibration is available
                if self.K is not None and self.D is not None:
                    L = self.marker_size
                    obj_points = np.array([
                        [-L/2.0,  L/2.0, 0.0],
                        [ L/2.0,  L/2.0, 0.0],
                        [ L/2.0, -L/2.0, 0.0],
                        [-L/2.0, -L/2.0, 0.0]
                    ], dtype=np.float32)
                    
                    for i in range(len(ids)):
                        success, rvec, tvec = cv2.solvePnP(obj_points, corners[i][0], self.K, self.D)
                        if success:
                            # Draw 3D coordinate frame axes
                            try:
                                cv2.drawFrameAxes(cv_img, self.K, self.D, rvec, tvec, 0.1)
                            except AttributeError:
                                try:
                                    cv2.aruco.drawAxis(cv_img, self.K, self.D, rvec, tvec, 0.1)
                                except AttributeError:
                                    pass
            
            # Publish the annotated frame
            ann_msg = self.bridge.cv2_to_imgmsg(cv_img, "bgr8")
            ann_msg.header = msg.header
            self.img_pub.publish(ann_msg)
            
        except Exception as e:
            self.get_logger().error(f"Error in image callback: {e}")

def main():
    rclpy.init()
    node = MarkerDebugPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
