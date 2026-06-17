#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
import os
import yaml

class CameraCalibratorNode(Node):
    def __init__(self):
        super().__init__('camera_calibrator_node')

        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('square_size', 0.06)  # distance in meters
        self.declare_parameter('target_frames', 25)
        self.declare_parameter('output_file', '/home/smr/workspaces/mini_amr/amrROS2_ws/src/bringup/config/camera_info_720p.yaml')

        self.image_topic = self.get_parameter('image_topic').value
        self.square_size = self.get_parameter('square_size').value
        self.target_frames = self.get_parameter('target_frames').value
        self.output_file = self.get_parameter('output_file').value

        self.bridge = CvBridge()
        self.cv_image = None
        self.imgpoints = []
        self.objpoints = []

        # Setup standard OpenCV SimpleBlobDetector parameters for circle detection
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 50.0
        params.maxArea = 100000.0
        self.detector = cv2.SimpleBlobDetector_create(params)

        # Generate 3D object points for a 4x11 asymmetric circle grid (44 circles total)
        self.objp = []
        # OpenCV sees 11 vertical columns, with 4 circles in each column
        for i in range(11):  
            for j in range(4):  
                # Swap X and Y from the standard formula so the 3D geometry matches your landscape board
                x = i * self.square_size
                y = (2 * j + (i % 2)) * self.square_size
                self.objp.append([x, y, 0.0])
        self.objp = np.array(self.objp, dtype=np.float32)

        self.last_capture_time = 0.0
        self.last_center = None
        self.frame_count = 0

        self.subscription = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.get_logger().info(f"Asymmetric Circle Grid Calibration Node started.")
        self.get_logger().info(f"Subscribed to topic: {self.image_topic}")
        self.get_logger().info(f"Target size: 11x8 grid (44 circles). Square spacing: {self.square_size} meters.")
        self.get_logger().info(f"Targeting {self.target_frames} stable frames. Please point the camera at the grid and move it around...")

    def image_callback(self, msg):
        try:
            self.frame_count += 1
            cv_img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            img_h, img_w = gray.shape[:2]

            # Update the expected grid size to 4x11
            found = False
            centers = None
            grid_size = (4, 11)

            # Try 1: Original Image
            ret, centers = cv2.findCirclesGrid(
                gray, grid_size,
                flags=cv2.CALIB_CB_ASYMMETRIC_GRID | cv2.CALIB_CB_CLUSTERING,
                blobDetector=detector_if_needed(self.detector)
            )
            if ret:
                found = True
            else:
                # Try 2: Rotate 90 degrees CW
                gray_rot_cw = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
                ret_cw, centers_cw = cv2.findCirclesGrid(
                    gray_rot_cw, grid_size,
                    flags=cv2.CALIB_CB_ASYMMETRIC_GRID | cv2.CALIB_CB_CLUSTERING,
                    blobDetector=detector_if_needed(self.detector)
                )
                if ret_cw:
                    found = True
                    # Convert coordinates back: x_orig = y_rot, y_orig = img_h - 1 - x_rot
                    centers = np.zeros_like(centers_cw)
                    for idx, pt in enumerate(centers_cw):
                        x_rot, y_rot = pt[0]
                        centers[idx][0] = [y_rot, img_h - 1 - x_rot]
                else:
                    # Try 3: Rotate 90 degrees CCW
                    gray_rot_ccw = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    ret_ccw, centers_ccw = cv2.findCirclesGrid(
                        gray_rot_ccw, grid_size,
                        flags=cv2.CALIB_CB_ASYMMETRIC_GRID | cv2.CALIB_CB_CLUSTERING,
                        blobDetector=detector_if_needed(self.detector)
                    )
                    if ret_ccw:
                        found = True
                        # Convert coordinates back: x_orig = img_w - 1 - y_rot, y_orig = x_rot
                        centers = np.zeros_like(centers_ccw)
                        for idx, pt in enumerate(centers_ccw):
                            x_rot, y_rot = pt[0]
                            centers[idx][0] = [img_w - 1 - y_rot, x_rot]

            # Log periodic status and save debug image
            if self.frame_count % 30 == 0:
                self.get_logger().info(f"Received {self.frame_count} frames. Grid detected: {found}")
                debug_img = cv_img.copy()
                if found and centers is not None:
                    cv2.drawChessboardCorners(debug_img, grid_size, centers, found)
                debug_path = '/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/scripts/debug_calib.jpg'
                cv2.imwrite(debug_path, debug_img)

            if found and centers is not None:
                current_time = time.time()
                # Ensure we wait at least 1.5 seconds between captures to get different angles
                if current_time - self.last_capture_time > 1.5:
                    current_center = np.mean(centers, axis=0)[0]
                    # Check if board has moved slightly from the last frame to ensure sample variety
                    if self.last_center is None or np.linalg.norm(current_center - self.last_center) > 15.0:
                        self.imgpoints.append(centers)
                        self.objpoints.append(self.objp)
                        self.last_capture_time = current_time
                        self.last_center = current_center
                        
                        self.get_logger().info(f"✓ Captured frame {len(self.imgpoints)}/{self.target_frames}!")
                        
                        # Once we collect enough frames, run the calibration
                        if len(self.imgpoints) >= self.target_frames:
                            self.run_calibration(img_w, img_h)
            
            # Print periodic status log every 5 seconds if we haven't seen the target yet
            if not found and int(time.time()) % 5 == 0:
                self.get_logger().info("Searching for 11x8 asymmetric circles grid... (Keep the board visible and flat)", once=True)

        except Exception as e:
            self.get_logger().error(f"Error in image callback: {e}")

    def run_calibration(self, width, height):
        self.get_logger().info("Starting camera calibration computation...")
        
        # Run camera calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints, self.imgpoints, (width, height), None, None
        )

        if ret:
            self.get_logger().info("Camera calibration successful!")
            self.get_logger().info(f"RMS projection error: {ret:.4f} pixels")
            
            # Format matrices for ROS 2 CameraInfo yaml
            camera_matrix = mtx.flatten().tolist()
            distortion_coefs = dist.flatten().tolist()
            projection_matrix = [
                float(mtx[0, 0]), float(mtx[0, 1]), float(mtx[0, 2]), 0.0,
                float(mtx[1, 0]), float(mtx[1, 1]), float(mtx[1, 2]), 0.0,
                float(mtx[2, 0]), float(mtx[2, 1]), float(mtx[2, 2]), 0.0
            ]
            rectification_matrix = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]

            yaml_data = {
                'image_width': width,
                'image_height': height,
                'camera_name': 'test_camera',
                'camera_matrix': {
                    'rows': 3,
                    'cols': 3,
                    'data': camera_matrix
                },
                'distortion_model': 'plumb_bob',
                'distortion_coefficients': {
                    'rows': 1,
                    'cols': 5,
                    'data': distortion_coefs[:5]
                },
                'rectification_matrix': {
                    'rows': 3,
                    'cols': 3,
                    'data': rectification_matrix
                },
                'projection_matrix': {
                    'rows': 3,
                    'cols': 4,
                    'data': projection_matrix
                }
            }

            # Write yaml file
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, 'w') as f:
                f.write("# Camera calibration parameters (dynamically calibrated via asymmetric circle grid)\n")
                yaml.dump(yaml_data, f, default_flow_style=None)
                
            self.get_logger().info(f"Successfully saved camera calibration file to: {self.output_file}")
            self.get_logger().info("Please run: colcon build --packages-select bringup")
        else:
            self.get_logger().error("Camera calibration failed!")

        # Shutdown node
        rclpy.shutdown()

def detector_if_needed(det):
    # Some opencv versions do not allow custom detector in findCirclesGrid, we return it anyway
    return det

def main(args=None):
    rclpy.init(args=args)
    node = CameraCalibratorNode()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
