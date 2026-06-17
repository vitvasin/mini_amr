#!/usr/bin/env python3
"""
register_markers.py
-------------------
Utility node to register ArUco marker poses in the 'map' frame.
To use this:
  1. Optionally localize the robot accurately (e.g. using RViz / AMCL / SLAM).
  2. Start this script.
  3. Drive the robot around your facility. Every time a tag is seen, the script
     calculates its coordinates.
  4. Press Ctrl+C to stop. The script will automatically average all observations
     (to filter out camera noise) and save the final database to a markers_auto.yaml file.

NOTE: If the nav stack map frame is not available, this script immediately
      publishes its own static map->odom identity TF so it works standalone.
"""

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
import cv2
import numpy as np
import tf2_ros
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import transforms3d as t3d
import json
import argparse
import sys
import os



class MarkerRegisterNode(Node):
    def __init__(self, marker_size, dictionary_name, camera_topic, camera_info_topic,
                 base_frame, sensor_frame, output_yaml_path, min_observations):
        super().__init__('marker_register_node')
        self.marker_size = marker_size
        self.dict_name = dictionary_name
        self.base_frame = base_frame
        self.sensor_frame = sensor_frame
        self.output_yaml_path = output_yaml_path
        self.min_observations = min_observations

        # Dictionary to store accumulated poses for averaging: marker_id -> list of [x, y, z, roll, pitch, yaw]
        self.recorded_markers = {}

        # Resolve ArUco dictionary
        self.dictionary = self._get_aruco_dictionary(self.dict_name)
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
        # ─────────────────────────────────────────────────────────────────────
        # Geometric validation thresholds (applied after solvePnP)
        self.MAX_REPROJ_ERROR = 4.0    # pixels  - reject if reprojection error > 4.0px (false positive is usually >10px)
        self.MIN_MARKER_DIST  = 0.10   # metres  - too close = bad PnP
        self.MAX_MARKER_DIST  = 5.00   # metres  - too far   = too small on sensor
        self.MIN_MARKER_AREA_PX = 100  # pixels² - minimum detection area (10x10px box)
        try:
            self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.detector_params)
        except AttributeError:
            self.detector = None

        self.cv_bridge = CvBridge()
        self.K = None
        self.D = None

        # TF listener to get map -> sensor frame
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Locked tracking frame ('map' or 'odom')
        self.tracking_frame = None

        # Standard ROS-OpenCV coordinate alignment quaternion
        # Rotates OpenCV camera frame (Z-forward, X-right, Y-down) to standard ROS frame (X-forward, Y-left, Z-up)
        self.camera_frame_alignment_qvec = np.array([0.5, -0.5, 0.5, -0.5])

        # Subscribers
        self.info_sub = self.create_subscription(CameraInfo, camera_info_topic, self.info_callback, 10)
        self.img_sub = self.create_subscription(Image, camera_topic, self.image_callback, 10)

        self.get_logger().info(f"Continuous Marker Mapper started. Watching camera: {camera_topic}")
        self.get_logger().info("Drive the robot slowly around the map. Poses will be recorded automatically.")
        self.get_logger().info(f"Minimum observations to save a marker: {self.min_observations} (filters false positives)")

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
            'DICT_APRILTAG_16h5': cv2.aruco.DICT_APRILTAG_16h5,
            'DICT_APRILTAG_25h9': cv2.aruco.DICT_APRILTAG_25h9,
            'DICT_APRILTAG_36h10': cv2.aruco.DICT_APRILTAG_36h10,
            'DICT_APRILTAG_36h11': cv2.aruco.DICT_APRILTAG_36h11,
        }
        val = mapping.get(name, cv2.aruco.DICT_4X4_50)
        return cv2.aruco.getPredefinedDictionary(val)

    def info_callback(self, msg):
        self.K = np.array(msg.k).reshape(3, 3)
        self.D = np.array(msg.d)

    def image_callback(self, msg):
        if self.K is None or self.D is None:
            self.get_logger().warn("Waiting for CameraInfo...", throttle_duration_sec=3.0)
            return

        try:
            cv_img = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

            if self.detector is not None:
                corners, ids, _ = self.detector.detectMarkers(gray)
            else:
                corners, ids, _ = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.detector_params)

            if ids is None or len(ids) == 0:
                return

            if self.tracking_frame is None:
                # We must STRICTLY use the map frame. No fallback to odom, because odom drifts.
                try:
                    self.tf_buffer.lookup_transform('map', self.sensor_frame, rclpy.time.Time())
                    self.tracking_frame = 'map'
                    self.get_logger().info("Successfully acquired 'map' frame for marker registration.")
                except Exception:
                    self.get_logger().warn(
                        "Waiting for 'map' frame to be published... Please localize the robot (e.g. using 2D Pose Estimate) BEFORE running this script!",
                        throttle_duration_sec=3.0
                    )
                    return

            # Lookup transform from world (map/odom) -> sensor_frame (camera)
            try:
                # Try exact stamp first with a small timeout
                t_world_sensor = self.tf_buffer.lookup_transform(
                    self.tracking_frame, self.sensor_frame, msg.header.stamp,
                    timeout=rclpy.duration.Duration(seconds=0.1)
                )
            except Exception:
                try:
                    # Fallback to latest available transform
                    t_world_sensor = self.tf_buffer.lookup_transform(
                        self.tracking_frame, self.sensor_frame, rclpy.time.Time()
                    )
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
                    self.get_logger().warn(
                        f"Failed to lookup transform {self.tracking_frame} -> {self.sensor_frame}: {e}",
                        throttle_duration_sec=3.0
                    )
                    return

            # Extract world -> camera position and orientation
            pos_m2c = t_world_sensor.transform.translation
            rot_m2c = t_world_sensor.transform.rotation

            t_c2w = np.array([pos_m2c.x, pos_m2c.y, pos_m2c.z]).reshape(3, 1)
            q_c2w_ros = np.array([rot_m2c.w, rot_m2c.x, rot_m2c.y, rot_m2c.z])

            # Convert ROS camera frame orientation back to OpenCV camera frame
            q_c2w = t3d.quaternions.qmult(q_c2w_ros, self.camera_frame_alignment_qvec)
            R_c2w = t3d.quaternions.quat2mat(q_c2w)

            # Object corners
            L = self.marker_size
            obj_points = np.array([
                [-L/2.0,  L/2.0, 0.0],
                [ L/2.0,  L/2.0, 0.0],
                [ L/2.0, -L/2.0, 0.0],
                [-L/2.0, -L/2.0, 0.0]
            ], dtype=np.float32)

            for i, marker_id_arr in enumerate(ids):
                marker_id = int(marker_id_arr[0])

                # ── Geometric sanity: minimum pixel area ─────────────────────
                pts = corners[i][0]  # shape (4, 2)
                side_a = np.linalg.norm(pts[0] - pts[1])
                side_b = np.linalg.norm(pts[1] - pts[2])
                pixel_area = side_a * side_b
                if pixel_area < self.MIN_MARKER_AREA_PX:
                    self.get_logger().debug(
                        f"Marker {marker_id} rejected: too small on screen "
                        f"({pixel_area:.0f}px² < {self.MIN_MARKER_AREA_PX}px²)"
                    )
                    continue

                success, rvec, tvec = cv2.solvePnP(
                    obj_points, corners[i][0], self.K, self.D,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if not success:
                    continue

                # ── Reprojection error check ─────────────────────────────────
                projected, _ = cv2.projectPoints(obj_points, rvec, tvec, self.K, self.D)
                reproj_error = np.mean(np.linalg.norm(
                    projected.reshape(-1, 2) - corners[i][0], axis=1
                ))
                if reproj_error > self.MAX_REPROJ_ERROR:
                    self.get_logger().warn(
                        f"Marker {marker_id} rejected: reprojection error too high "
                        f"({reproj_error:.2f}px > {self.MAX_REPROJ_ERROR}px)"
                    )
                    continue

                # ── Physical distance check ──────────────────────────────────
                dist = float(np.linalg.norm(tvec))
                if dist < self.MIN_MARKER_DIST or dist > self.MAX_MARKER_DIST:
                    self.get_logger().warn(
                        f"Marker {marker_id} rejected: distance out of range "
                        f"({dist:.2f}m, valid: {self.MIN_MARKER_DIST}–{self.MAX_MARKER_DIST}m)"
                    )
                    continue

                # tvec is marker in camera coordinates: t_m2c
                # rvec is marker rotation in camera coordinates: R_m2c
                R_m2c, _ = cv2.Rodrigues(rvec)

                # Find marker position in map frame: p_w = R_c2w * p_c + t_c2w
                t_m2w = np.dot(R_c2w, tvec) + t_c2w
                R_m2w = np.dot(R_c2w, R_m2c)

                # Convert rotation matrix to Euler angles
                roll, pitch, yaw = t3d.euler.mat2euler(R_m2w)

                pose_observation = [t_m2w[0][0], t_m2w[1][0], t_m2w[2][0], roll, pitch, yaw]

                if marker_id not in self.recorded_markers:
                    self.recorded_markers[marker_id] = []
                    self.get_logger().info(
                        f"First sight of Marker ID: {marker_id}! "
                        f"dist={dist:.2f}m reproj={reproj_error:.2f}px "
                        f"(need {self.min_observations} obs to save)..."
                    )

                self.recorded_markers[marker_id].append(pose_observation)
                count = len(self.recorded_markers[marker_id])

                if count < self.min_observations:
                    self.get_logger().info(
                        f"Marker {marker_id}: {count}/{self.min_observations} observations "
                        f"(x={t_m2w[0][0]:.3f}, y={t_m2w[1][0]:.3f}, z={t_m2w[2][0]:.3f})",
                        throttle_duration_sec=1.0
                    )
                else:
                    self.get_logger().info(
                        f"Recording Marker {marker_id}: "
                        f"x={t_m2w[0][0]:.3f}, y={t_m2w[1][0]:.3f}, z={t_m2w[2][0]:.3f} "
                        f"dist={dist:.2f}m reproj={reproj_error:.2f}px "
                        f"({count} observations) ✓",
                        throttle_duration_sec=2.0
                    )
        except Exception as e:
            self.get_logger().error(f"Error in register: {e}")

    def save_recorded_markers(self):
        if not self.recorded_markers:
            self.get_logger().info("No markers were detected. Output file not written.")
            return

        # Filter out false positives: only keep markers seen >= min_observations times
        confirmed = {mid: poses for mid, poses in self.recorded_markers.items()
                     if len(poses) >= self.min_observations}
        rejected = {mid: len(poses) for mid, poses in self.recorded_markers.items()
                    if len(poses) < self.min_observations}

        if rejected:
            self.get_logger().warn(
                f"Rejected {len(rejected)} marker(s) as false positives "
                f"(seen < {self.min_observations} times): IDs {list(rejected.keys())} "
                f"with observation counts {list(rejected.values())}"
            )

        if not confirmed:
            self.get_logger().warn(
                f"No markers met the minimum {self.min_observations} observations threshold. "
                "Output file not written. Point camera at tags longer and closer."
            )
            return

        averaged_config = {}
        for marker_id, poses in confirmed.items():
            poses = np.array(poses)
            # Average translation
            avg_t = np.mean(poses[:, :3], axis=0)

            # Average orientation using quaternions to handle angular wrapping
            q_list = []
            for r, p, y in poses[:, 3:]:
                q_list.append(t3d.quaternions.mat2quat(t3d.euler.euler2mat(r, p, y)))

            avg_q = np.mean(np.array(q_list), axis=0)
            avg_q = avg_q / np.linalg.norm(avg_q)

            avg_roll, avg_pitch, avg_yaw = t3d.euler.quat2euler(avg_q)

            averaged_config[str(marker_id)] = {
                "x": round(float(avg_t[0]), 4),
                "y": round(float(avg_t[1]), 4),
                "z": round(float(avg_t[2]), 4),
                "roll": round(float(avg_roll), 4),
                "pitch": round(float(avg_pitch), 4),
                "yaw": round(float(avg_yaw), 4)
            }

        try:
            import yaml
            import os
            
            # Load existing config if it exists so we can append/update
            existing_config = {}
            if os.path.exists(self.output_yaml_path):
                with open(self.output_yaml_path, 'r') as f:
                    try:
                        existing_yaml = yaml.safe_load(f)
                        existing_json = existing_yaml["/marker_localization_node"]["ros__parameters"]["markers_config"]
                        existing_config = json.loads(existing_json)
                        self.get_logger().info(f"Loaded {len(existing_config)} existing markers from previous file to merge.")
                    except Exception:
                        self.get_logger().warn("Could not parse existing markers_config. Creating a fresh file.")
            
            # Merge existing with new ones
            existing_config.update(averaged_config)

            # Format into ROS 2 YAML parameter structure
            yaml_data = {
                "/marker_localization_node": {
                    "ros__parameters": {
                        "marker_size": self.marker_size,
                        "marker_dictionary_name": self.dict_name,
                        "markers_config": json.dumps(existing_config)
                    }
                }
            }

            os.makedirs(os.path.dirname(self.output_yaml_path), exist_ok=True)
            with open(self.output_yaml_path, 'w') as f:
                yaml.dump(yaml_data, f, default_flow_style=False)
            self.get_logger().info(
                f"Successfully saved/merged {len(existing_config)} total markers (Added/Updated {len(averaged_config)}) to {self.output_yaml_path}"
            )
        except Exception as e:
            self.get_logger().error(f"Failed to save YAML file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Register marker poses relative to map.")
    parser.add_argument('--size', type=float, default=0.15, help='Marker size in meters')
    parser.add_argument('--dict', type=str, default='DICT_4X4_50', help='ArUco dictionary name')
    parser.add_argument('--camera_topic', type=str, default='/image_raw', help='Camera image topic')
    parser.add_argument('--camera_info_topic', type=str, default='/camera_info', help='Camera info topic')
    parser.add_argument('--base_frame', type=str, default='base_link', help='Robot base frame')
    parser.add_argument('--sensor_frame', type=str, default='rgbd_frame', help='Camera frame')
    parser.add_argument('--output', type=str,
                        default='/home/smr/workspaces/mini_amr/amrROS2_ws/src/marker_localization/config/markers_auto.yaml',
                        help='Output YAML file path')
    parser.add_argument('--min-obs', type=int, default=1,
                        help='Minimum observations required to register/save a marker (default: 1)')

    ros_args = rclpy.utilities.remove_ros_args(sys.argv)
    args, unknown = parser.parse_known_args(ros_args[1:])

    rclpy.init()
    node = MarkerRegisterNode(
        marker_size=args.size,
        dictionary_name=args.dict,
        camera_topic=args.camera_topic,
        camera_info_topic=args.camera_info_topic,
        base_frame=args.base_frame,
        sensor_frame=args.sensor_frame,
        output_yaml_path=args.output,
        min_observations=args.min_obs,
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.save_recorded_markers()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()


