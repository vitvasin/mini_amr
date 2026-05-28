import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from cv_bridge import CvBridge
from rclpy.duration import Duration

from std_msgs.msg import ColorRGBA, Header
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose, Point, Quaternion, PoseArray, Vector3, PoseWithCovarianceStamped
from visualization_msgs.msg import Marker

import cv2
import threading
import numpy as np
from matplotlib import cm
import time

import sys
import os
sys.path.append("/home/smr/Projects/lino2_ws/src/visual_robot_localization/third_party/hloc/Hierarchical-Localization")

from visual_robot_localization.visual_6dof_localize import VisualPoseEstimator
from visual_robot_localization.coordinate_transforms import SensorOffsetCompensator


class VisualLocalizer(Node):
    def __init__(self):
        super().__init__('visual_localization_node')

        self.declare_parameter("pose_publish_topic", "/visual_localization/pose_response")
        pose_publish_topic = self.get_parameter('pose_publish_topic').get_parameter_value().string_value

        # On-demand: subscribe to image_request from recovery_node (not always-on camera)
        self.declare_parameter("camera_topic", "/visual_localization/image_request")
        camera_topic_name = self.get_parameter('camera_topic').get_parameter_value().string_value

        self.declare_parameter("global_extractor_name", "netvlad")
        global_extractor_name = self.get_parameter('global_extractor_name').get_parameter_value().string_value

        self.declare_parameter("local_extractor_name", "superpoint_aachen")
        local_extractor_name = self.get_parameter('local_extractor_name').get_parameter_value().string_value

        self.declare_parameter("local_matcher_name", "superglue")
        local_matcher_name = self.get_parameter('local_matcher_name').get_parameter_value().string_value

        self.declare_parameter("gallery_global_descriptor_path", "/image-gallery/example_dir/outputs/netvlad+superpoint_aachen+superglue/global-feats-netvlad.h5")
        gallery_global_descriptor_path = self.get_parameter('gallery_global_descriptor_path').get_parameter_value().string_value

        self.declare_parameter("gallery_local_descriptor_path", "/image-gallery/example_dir/outputs/netvlad+superpoint_aachen+superglue/feats-superpoint-n4096-r1024.h5")
        gallery_local_descriptor_path = self.get_parameter('gallery_local_descriptor_path').get_parameter_value().string_value

        self.declare_parameter("image_gallery_path", "/image-gallery/example_dir/")
        image_gallery_path = self.get_parameter('image_gallery_path').get_parameter_value().string_value

        self.declare_parameter("gallery_sfm_path", "/image-gallery/example_dir/outputs/sfm_netvlad+superpoint_aachen+superglue/")
        gallery_sfm_path = self.get_parameter('gallery_sfm_path').get_parameter_value().string_value

        self.declare_parameter("top_k_matches", 4)
        self.top_k = self.get_parameter('top_k_matches').get_parameter_value().integer_value

        # Set compensate_sensor_offset=False for a simple forward-facing USB webcam.
        # Set to True if the camera is rigidly offset from base_link and TF is published.
        self.declare_parameter("compensate_sensor_offset", False)
        self.compensate_sensor_offset = self.get_parameter('compensate_sensor_offset').get_parameter_value().bool_value

        self.declare_parameter("base_frame", "base_link")
        base_frame = self.get_parameter('base_frame').get_parameter_value().string_value

        self.declare_parameter("sensor_frame", "camera_link")
        sensor_frame = self.get_parameter('sensor_frame').get_parameter_value().string_value

        # align_camera_frame was a CARLA-simulator-specific correction. Disabled by default.
        self.declare_parameter("align_camera_frame", False)
        align_camera_frame = self.get_parameter('align_camera_frame').get_parameter_value().bool_value

        self.declare_parameter("ransac_thresh", 12)
        ransac_thresh = self.get_parameter('ransac_thresh').get_parameter_value().integer_value

        self.declare_parameter("visualize_estimates", False)
        self.visualize_estimates = self.get_parameter('visualize_estimates').get_parameter_value().bool_value

        # Publisher: output 6DoF pose result
        self.vloc_publisher = self.create_publisher(PoseWithCovarianceStamped, pose_publish_topic, 10)

        # Optional visualization publishers
        if self.visualize_estimates:
            self.place_recognition_publisher = self.create_publisher(Marker, '/place_recognition_visualization', 10)
            self.pnp_estimate_publisher = self.create_publisher(PoseArray, '/visual_pose_estimate_visualization', 10)
            self.colormap = cm.get_cmap('Accent')

        # Subscriber: one-shot image from recovery_node
        self.subscription = self.create_subscription(
            Image,
            camera_topic_name,
            self.image_request_callback,
            10)

        self.lock = threading.Lock()
        self.is_processing = False
        self.cv_bridge = CvBridge()

        # Load models and gallery at startup (heavy, done only once)
        self.pose_estimator = VisualPoseEstimator(
            global_extractor_name,
            local_extractor_name,
            local_matcher_name,
            image_gallery_path,
            gallery_global_descriptor_path,
            gallery_local_descriptor_path,
            gallery_sfm_path,
            ransac_thresh
        )

        if self.compensate_sensor_offset:
            self.get_logger().info('Constructing sensor offset compensator...')
            self.sensor_offset_compensator = SensorOffsetCompensator(base_frame, sensor_frame, align_camera_frame)
            if not hasattr(self.sensor_offset_compensator.tvec, '__len__'):
                self.get_logger().error("Sensor offset compensator construction failed!")

        # Covariance matrix: position & orientation uncertainty from visual localization
        loc_var = 0.1
        loc_cov = 0.0
        or_var = 0.1
        or_cov = 0.0
        self.vloc_estimate_covariance = np.array([
            loc_var, loc_cov, loc_cov, 0.0, 0.0, 0.0,
            loc_cov, loc_var, loc_cov, 0.0, 0.0, 0.0,
            loc_cov, loc_cov, loc_var, 0.0, 0.0, 0.0,
            0.0,     0.0,     0.0,     or_var, or_cov, or_cov,
            0.0,     0.0,     0.0,     or_cov, or_var, or_cov,
            0.0,     0.0,     0.0,     or_cov, or_cov, or_var,
        ])

        self.get_logger().info(
            f'Visual Localizer ready. Listening on [{camera_topic_name}] for on-demand pose requests.'
        )

    def image_request_callback(self, image_msg: Image):
        """
        On-demand callback: triggered by recovery_node.py sending a single captured frame.
        Runs full AI inference pipeline and publishes the resulting 6DoF pose.
        Guards against concurrent calls so only one inference runs at a time.
        """
        with self.lock:
            if self.is_processing:
                self.get_logger().warn('Already processing a localization request. Ignoring concurrent image.')
                return
            self.is_processing = True

        self.get_logger().info('Received image request. Starting 6DoF pose estimation...')
        computation_start_time = time.time_ns()

        try:
            # Convert ROS Image → OpenCV (BGR→RGB for hloc)
            cv2_img = self.cv_bridge.imgmsg_to_cv2(image_msg, "bgr8")
            cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

            ret = self.pose_estimator.estimate_pose(cv2_img, self.top_k)

            if self.compensate_sensor_offset:
                for pose in ret['place_recognition']:
                    pose['tvec'], pose['qvec'] = self.sensor_offset_compensator.remove_offset_from_array(
                        pose['tvec'], pose['qvec'])
                for pose in ret['pnp_estimates']:
                    if pose['success']:
                        pose['tvec'], pose['qvec'] = self.sensor_offset_compensator.remove_offset_from_array(
                            pose['tvec'], pose['qvec'])

            best_estimate, best_cluster_idx = self.choose_best_estimate(ret)

            true_delay = Duration(nanoseconds=time.time_ns() - computation_start_time)
            elapsed_s = true_delay.nanoseconds / 1e9
            self.get_logger().info(f'Inference completed in {elapsed_s:.2f}s.')

            pose_msg = self._construct_visual_pose_msg(best_estimate)
            self.vloc_publisher.publish(pose_msg)

            if best_estimate is not None:
                p = best_estimate['tvec']
                self.get_logger().info(f'Pose estimated: x={p[0]:.3f}, y={p[1]:.3f}, z={p[2]:.3f}')
            else:
                self.get_logger().warn('No valid pose found. Publishing empty pose (recovery_node will reject it).')

            if self.visualize_estimates:
                self._estimate_visualizer(ret, image_msg.header.stamp, best_cluster_idx)

        except Exception as e:
            self.get_logger().error(f'Exception during pose estimation: {e}')
        finally:
            with self.lock:
                self.is_processing = False

    def _construct_visual_pose_msg(self, best_estimate):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        if best_estimate is not None:
            msg.pose.pose.position = np2point_msg(best_estimate['tvec'])
            msg.pose.pose.orientation = np2quat_msg(best_estimate['qvec'])
            msg.pose.covariance = self.vloc_estimate_covariance.tolist()

        return msg

    def choose_best_estimate(self, visual_pose_estimates):
        """Pick the PnP estimate with the most RANSAC inliers."""
        best_inliers = 0
        best_estimate = None
        best_idx = None
        for i, estimate in enumerate(visual_pose_estimates['pnp_estimates']):
            if estimate['success'] and estimate['num_inliers'] > best_inliers:
                best_inliers = estimate['num_inliers']
                best_estimate = estimate
                best_idx = i
        return best_estimate, best_idx

    def _estimate_visualizer(self, ret, timestamp, best_pose_idx):
        header = Header(frame_id='map', stamp=timestamp)
        marker = Marker(
            header=header,
            scale=Vector3(x=1.0, y=1.0, z=1.0),
            type=8, action=0,
            color=ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0)
        )
        poses = PoseArray(header=header, poses=[])

        for i, estimate in enumerate(ret['pnp_estimates']):
            color = self.colormap(0 if i == best_pose_idx else i + 1)
            color = ColorRGBA(r=color[0], g=color[1], b=color[2], a=color[3])

            for idx in estimate['place_recognition_idx']:
                marker.colors.append(color)
                marker.points.append(np2point_msg(ret['place_recognition'][idx]['tvec']))

            if estimate['success']:
                poses.poses.append(
                    Pose(position=np2point_msg(estimate['tvec']),
                         orientation=np2quat_msg(estimate['qvec']))
                )

        self.place_recognition_publisher.publish(marker)
        self.pnp_estimate_publisher.publish(poses)


def np2point_msg(np_point):
    return Point(x=float(np_point[0]), y=float(np_point[1]), z=float(np_point[2]))


def np2quat_msg(np_quat):
    return Quaternion(w=float(np_quat[0]), x=float(np_quat[1]),
                      y=float(np_quat[2]), z=float(np_quat[3]))


def main(args=None):
    rclpy.init(args=args)
    localizer = VisualLocalizer()
    try:
        executor = SingleThreadedExecutor()
        executor.add_node(localizer)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        localizer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
