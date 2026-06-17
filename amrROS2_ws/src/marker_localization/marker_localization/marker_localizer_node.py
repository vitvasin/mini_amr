#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseWithCovarianceStamped, Point, Quaternion
import cv2
import numpy as np
import json
import threading
import transforms3d as t3d

from marker_localization.coordinate_transforms import SensorOffsetCompensator

class MarkerLocalizer(Node):
    def __init__(self):
        super().__init__('marker_localization_node')

        # Declare parameters
        self.declare_parameter('pose_publish_topic', '/marker_localization/pose_response')
        self.declare_parameter('camera_topic', '/marker_localization/image_request')
        self.declare_parameter('camera_info_topic', '/camera_info')
        self.declare_parameter('marker_size', 0.15)  # size in meters
        self.declare_parameter('marker_dictionary_name', 'DICT_4X4_50')
        self.declare_parameter('compensate_sensor_offset', True)
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('sensor_frame', 'rgbd_frame')

        # Markers configuration as a JSON string
        # Maps marker ID (as string) to its 3D pose in the 'map' frame
        default_markers = {
            "1": {"x": 0.0, "y": 0.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            "2": {"x": 2.0, "y": 1.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 1.5708}
        }
        self.declare_parameter('markers_config', json.dumps(default_markers))

        # Retrieve parameters
        pose_publish_topic = self.get_parameter('pose_publish_topic').get_parameter_value().string_value
        camera_topic = self.get_parameter('camera_topic').get_parameter_value().string_value
        camera_info_topic = self.get_parameter('camera_info_topic').get_parameter_value().string_value
        self.marker_size = self.get_parameter('marker_size').get_parameter_value().double_value
        dict_name = self.get_parameter('marker_dictionary_name').get_parameter_value().string_value
        self.compensate_sensor_offset = self.get_parameter('compensate_sensor_offset').get_parameter_value().bool_value
        base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        sensor_frame = self.get_parameter('sensor_frame').get_parameter_value().string_value

        try:
            markers_json = self.get_parameter('markers_config').get_parameter_value().string_value
            self.markers = json.loads(markers_json)
            self.get_logger().info(f"Loaded {len(self.markers)} markers from configuration.")
        except Exception as e:
            self.get_logger().error(f"Failed to parse markers_config parameter: {e}. Using empty dictionary.")
            self.markers = {}

        # Resolve ArUco dictionary
        self.dictionary = self._get_aruco_dictionary(dict_name)
        self.detector_params = cv2.aruco.DetectorParameters()
        
        # ── Robust default parameters to ensure real-world detection ───────────
        self.detector_params.errorCorrectionRate = 0.1 # Reduced from 0.6 to prevent false positives
        self.detector_params.maxErroneousBitsInBorderRate = 0.1 # Reduced from 0.35
        self.detector_params.minMarkerPerimeterRate = 0.05
        self.detector_params.polygonalApproxAccuracyRate = 0.05

        # Keep subpixel refinement active, as it ensures geometric accuracy
        self.detector_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.detector_params.cornerRefinementWinSize = 5
        self.detector_params.cornerRefinementMaxIterations = 30
        self.detector_params.cornerRefinementMinAccuracy = 0.1
        # ── Post-PnP geometric validation thresholds ───────────────────────────
        self.MAX_REPROJ_ERROR = 4.0    # pixels  - reject if reprojection error > 4.0px
        self.MIN_MARKER_DIST  = 0.10   # metres  - too close = bad PnP geometry
        self.MAX_MARKER_DIST  = 5.00   # metres  - too far = marker too small to trust
        self.MIN_MARKER_AREA_PX = 100  # pixels² - minimum area (10x10px)
        
        # In newer OpenCV, we use ArucoDetector.
        try:
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.detector_params)
            self.get_logger().info("Using modern OpenCV ArucoDetector API.")
        except AttributeError:
            self.detector = None
            self.get_logger().info("Using legacy OpenCV detectMarkers API.")

        # Camera intrinsics storage (thread safe)
        self.camera_lock = threading.Lock()
        self.K = None
        self.D = None
        self.camera_width = 640
        self.camera_height = 360

        # Subscriptions and Publishers
        self.cv_bridge = CvBridge()
        self.pose_pub = self.create_publisher(PoseWithCovarianceStamped, pose_publish_topic, 10)
        
        self.img_sub = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )

        self.info_sub = self.create_subscription(
            CameraInfo,
            camera_info_topic,
            self.camera_info_callback,
            10
        )

        # Sensor offset compensator setup
        if self.compensate_sensor_offset:
            self.get_logger().info(f"Setting up sensor offset compensator for {base_frame} -> {sensor_frame}...")
            self.sensor_offset_compensator = SensorOffsetCompensator(
                base_frame_name=self.get_parameter('base_frame').value,
                sensor_frame_name=self.get_parameter('sensor_frame').value,
                align_camera_frame=False  # CRITICAL: qvec_final is already aligned to ROS!
            )
        else:
            self.sensor_offset_compensator = None

        # Standard ROS-OpenCV coordinate alignment quaternion
        # Rotates OpenCV camera frame (Z-forward, X-right, Y-down) to standard ROS frame (X-forward, Y-left, Z-up)
        self.camera_frame_alignment_qvec = np.array([0.5, -0.5, 0.5, -0.5])

        # Covariance representing high confidence in marker localization (low uncertainty)
        loc_var = 0.05
        or_var = 0.02
        self.covariance = [
            loc_var, 0.0,     0.0,     0.0,    0.0,    0.0,
            0.0,     loc_var, 0.0,     0.0,    0.0,    0.0,
            0.0,     0.0,     loc_var, 0.0,    0.0,    0.0,
            0.0,     0.0,     0.0,     or_var, 0.0,    0.0,
            0.0,     0.0,     0.0,     0.0,    or_var, 0.0,
            0.0,     0.0,     0.0,     0.0,    0.0,    or_var
        ]

        self.get_logger().info(f"Marker Localization Node initialized. Listening on [{camera_topic}]")

    def _get_aruco_dictionary(self, name):
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
            'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
            'DICT_7X7_100': cv2.aruco.DICT_7X7_100,
            'DICT_7X7_250': cv2.aruco.DICT_7X7_250,
            'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
            'DICT_APRILTAG_16h5': cv2.aruco.DICT_APRILTAG_16h5,
            'DICT_APRILTAG_25h9': cv2.aruco.DICT_APRILTAG_25h9,
            'DICT_APRILTAG_36h10': cv2.aruco.DICT_APRILTAG_36h10,
            'DICT_APRILTAG_36h11': cv2.aruco.DICT_APRILTAG_36h11,
        }
        val = mapping.get(name, cv2.aruco.DICT_4X4_50)
        return cv2.aruco.getPredefinedDictionary(val)

    def camera_info_callback(self, msg: CameraInfo):
        with self.camera_lock:
            self.K = np.array(msg.k).reshape(3, 3)
            self.D = np.array(msg.d)
            self.camera_width = msg.width
            self.camera_height = msg.height

    def _get_intrinsics(self, img_w, img_h):
        with self.camera_lock:
            if self.K is not None:
                return self.K.copy(), self.D.copy()
            
            # Fallback values
            fx = 500.0
            fy = 500.0
            cx = img_w / 2.0
            cy = img_h / 2.0
            K = np.array([[fx, 0.0, cx],
                          [0.0, fy, cy],
                          [0.0, 0.0, 1.0]], dtype=np.float32)
            D = np.zeros(5, dtype=np.float32)
            return K, D

    def image_callback(self, msg: Image):
        self.get_logger().info("Received image request for marker localization...")
        try:
            cv_img = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            img_h, img_w = gray.shape[:2]

            # Detect markers
            if self.detector is not None:
                corners, ids, _ = self.detector.detectMarkers(gray)
            else:
                corners, ids, _ = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.detector_params)

            if ids is None or len(ids) == 0:
                self.get_logger().warn("No ArUco markers detected in the image. Relocalization failed.")
                empty_pose = PoseWithCovarianceStamped()
                empty_pose.header.frame_id = 'map'
                empty_pose.header.stamp = msg.header.stamp
                self.pose_pub.publish(empty_pose)
                return

            self.get_logger().info(f"Detected marker IDs: {ids.flatten().tolist()}")

            # Get intrinsics
            K, D = self._get_intrinsics(img_w, img_h)

            # Marker 3D corners in its own local coordinate system
            L = self.marker_size
            obj_points = np.array([
                [-L/2.0,  L/2.0, 0.0],
                [ L/2.0,  L/2.0, 0.0],
                [ L/2.0, -L/2.0, 0.0],
                [-L/2.0, -L/2.0, 0.0]
            ], dtype=np.float32)

            best_estimate = None
            best_marker_id = None
            min_dist = float('inf')

            # Process each detected marker
            for i, marker_id_arr in enumerate(ids):
                marker_id = str(marker_id_arr[0])
                if marker_id not in self.markers:
                    self.get_logger().info(f"Marker ID {marker_id} detected but not registered in map database. Skipping.")
                    continue

                # ── Minimum pixel area check ──────────────────────────────────
                pts = corners[i][0]
                side_a = np.linalg.norm(pts[0] - pts[1])
                side_b = np.linalg.norm(pts[1] - pts[2])
                pixel_area = side_a * side_b
                if pixel_area < self.MIN_MARKER_AREA_PX:
                    self.get_logger().warn(
                        f"Marker {marker_id} rejected: too small ({pixel_area:.0f}px² < {self.MIN_MARKER_AREA_PX}px²). Move closer."
                    )
                    continue

                # Use IPPE_SQUARE solver to prevent 180-degree rotation ambiguity
                success, rvec, tvec = cv2.solvePnP(
                    obj_points, corners[i][0], K, D,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if not success:
                    continue

                # ── Reprojection error check ─────────────────────────────────
                projected, _ = cv2.projectPoints(obj_points, rvec, tvec, K, D)
                reproj_error = np.mean(np.linalg.norm(
                    projected.reshape(-1, 2) - corners[i][0], axis=1
                ))
                if reproj_error > self.MAX_REPROJ_ERROR:
                    self.get_logger().warn(
                        f"Marker {marker_id} rejected: reprojection error {reproj_error:.2f}px > {self.MAX_REPROJ_ERROR}px"
                    )
                    continue

                # Distance to tag
                dist = float(np.linalg.norm(tvec))
                if dist < self.MIN_MARKER_DIST or dist > self.MAX_MARKER_DIST:
                    self.get_logger().warn(
                        f"Marker {marker_id} rejected: distance {dist:.2f}m out of range "
                        f"({self.MIN_MARKER_DIST}–{self.MAX_MARKER_DIST}m)"
                    )
                    continue

                self.get_logger().info(
                    f"Marker {marker_id} validated: dist={dist:.2f}m reproj={reproj_error:.2f}px "
                    f"area={pixel_area:.0f}px²"
                )

                if dist < min_dist:
                    min_dist = dist
                    best_marker_id = marker_id
                    
                    R_m2c, _ = cv2.Rodrigues(rvec)
                    
                    # Calculate camera position in marker frame
                    # P_cam = R_m2c * P_m + tvec
                    # Origin of camera (P_cam = 0) in marker frame:
                    # 0 = R_m2c * P_m + tvec => P_m = -R_m2c.T * tvec
                    t_c2m = -np.dot(R_m2c.T, tvec)

                    m_data = self.markers[marker_id]
                    t_m2w = np.array([m_data['x'], m_data['y'], m_data['z']]).reshape(3, 1)
                    
                    roll = m_data.get('roll', 0.0)
                    pitch = m_data.get('pitch', 0.0)
                    yaw = m_data.get('yaw', 0.0)
                    R_m2w = t3d.euler.euler2mat(roll, pitch, yaw)

                    t_c2w = np.dot(R_m2w, t_c2m) + t_m2w
                    
                    # R_c2w = R_m2w * R_c2m = R_m2w * R_m2c.T
                    R_c2w = np.dot(R_m2w, R_m2c.T)

                    q_c2w = t3d.quaternions.mat2quat(R_c2w)

                    # Align OpenCV camera frame with standard ROS frame
                    q_c2w_ros = t3d.quaternions.qmult(q_c2w, t3d.quaternions.qinverse(self.camera_frame_alignment_qvec))
                    q_c2w_ros = q_c2w_ros / t3d.quaternions.qnorm(q_c2w_ros)

                    best_estimate = {
                        'tvec': t_c2w.flatten(),
                        'qvec': q_c2w_ros
                    }

            if best_estimate is None:
                self.get_logger().warn("None of the detected markers were registered in the database. Relocalization failed.")
                empty_pose = PoseWithCovarianceStamped()
                empty_pose.header.frame_id = 'map'
                empty_pose.header.stamp = msg.header.stamp
                self.pose_pub.publish(empty_pose)
                return

            # Pose compensation for sensor offset
            tvec_final = best_estimate['tvec']
            qvec_final = best_estimate['qvec']

            if self.compensate_sensor_offset and self.sensor_offset_compensator is not None:
                tvec_final, qvec_final = self.sensor_offset_compensator.remove_offset_from_array(tvec_final, qvec_final)
                self.get_logger().info("Compensated for camera physical offset relative to base_link.")

            # Flatten to 2D for AMCL (Z=0, Roll=0, Pitch=0)
            yaw_final = t3d.euler.quat2euler(qvec_final)[2]
            qvec_flat = t3d.quaternions.mat2quat(t3d.euler.euler2mat(0.0, 0.0, yaw_final))

            # Publish the pose message
            pose_msg = PoseWithCovarianceStamped()
            pose_msg.header.frame_id = f'map|{best_marker_id}'
            pose_msg.header.stamp = msg.header.stamp
            pose_msg.pose.pose.position = Point(x=float(tvec_final[0]), y=float(tvec_final[1]), z=0.0)
            pose_msg.pose.pose.orientation = Quaternion(w=float(qvec_flat[0]), x=float(qvec_flat[1]), y=float(qvec_flat[2]), z=float(qvec_flat[3]))
            pose_msg.pose.covariance = self.covariance

            self.pose_pub.publish(pose_msg)
            self.get_logger().info(f"Relocalization successful! Robot pose estimated via tag {best_marker_id}: "
                                   f"x={tvec_final[0]:.3f}, y={tvec_final[1]:.3f}, z={tvec_final[2]:.3f}")

        except Exception as e:
            self.get_logger().error(f"Error during marker localization: {e}")
            empty_pose = PoseWithCovarianceStamped()
            empty_pose.header.frame_id = 'map'
            empty_pose.header.stamp = msg.header.stamp
            self.pose_pub.publish(empty_pose)

def main(args=None):
    rclpy.init(args=args)
    node = MarkerLocalizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
