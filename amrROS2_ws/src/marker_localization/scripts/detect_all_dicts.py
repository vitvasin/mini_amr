#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import sys

class DetectAllDictsNode(Node):
    def __init__(self):
        super().__init__('detect_all_dicts_node')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )
        self.get_logger().info("DetectAllDictsNode started. Subscribed to /image_raw.")
        self.get_logger().info("Please point the camera at your physical tags...")
        self.done = False

    def image_callback(self, msg):
        if self.done:
            return
        
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            
            # List of all standard dictionaries
            dicts_to_try = {
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
                'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
                'DICT_7X7_100': cv2.aruco.DICT_7X7_100,
                'DICT_7X7_250': cv2.aruco.DICT_7X7_250,
                'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
                'DICT_ARUCO_ORIGINAL': cv2.aruco.DICT_ARUCO_ORIGINAL,
            }
            
            # Add AprilTag dictionaries if they exist
            for name in ['DICT_APRILTAG_16h5', 'DICT_APRILTAG_25h9', 'DICT_APRILTAG_36h10', 'DICT_APRILTAG_36h11']:
                if hasattr(cv2.aruco, name):
                    dicts_to_try[name] = getattr(cv2.aruco, name)

            any_detected = False
            for d_name, d_val in dicts_to_try.items():
                dictionary = cv2.aruco.getPredefinedDictionary(d_val)
                parameters = cv2.aruco.DetectorParameters()
                
                # STRICT NOISE FILTERING to prevent false positives from background textures
                parameters.errorCorrectionRate = 0.1  # Allow a tiny bit of error correction for screen glare
                parameters.minMarkerPerimeterRate = 0.05  # Reject tiny background spots
                parameters.polygonalApproxAccuracyRate = 0.05  # Allow normal camera perspective distortion
                parameters.maxErroneousBitsInBorderRate = 0.35  # Default OpenCV (allows some glare on the border)
                
                try:
                    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
                    corners, ids, rejected = detector.detectMarkers(gray)
                except AttributeError:
                    corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
                
                if ids is not None and len(ids) > 0:
                    detected_ids = [int(i[0]) for i in ids]
                    # We print all detections
                    self.get_logger().info(f"  * Try dictionary {d_name: <20} -> Detected IDs: {detected_ids}")
                    
                    # Check if it detects exactly 1, 2, or 3
                    if any(x in [1, 2, 3] for x in detected_ids):
                        self.get_logger().info(f"SUCCESS: Dictionary '{d_name}' successfully identified your physical tags as IDs {detected_ids}!")
                        any_detected = True
                    
            if any_detected:
                self.done = True
                self.get_logger().info("All dictionary test finished. You can now use the correct dictionary name.")
                sys.exit(0)
                
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            self.done = True

def main():
    rclpy.init()
    node = DetectAllDictsNode()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
