"""
relocalization_system.launch.py
--------------------------------
Starts the full visual relocalization system in one command:
  1. visual_localizer_node  — AI pipeline (loads models, waits for image requests)
  2. visual_recovery_node   — Orchestrator (halts robot, captures image, injects pose)

USAGE:
  ros2 launch visual_recovery relocalization_system.launch.py \
      gallery_global_descriptor_path:=/path/to/global-feats-netvlad.h5 \
      gallery_local_descriptor_path:=/path/to/feats-superpoint.h5 \
      image_gallery_path:=/path/to/gallery/ \
      gallery_sfm_path:=/path/to/sfm_output/

TRIGGER (in a separate terminal, after launch):
  ros2 service call /visual_recovery_node/trigger_recovery std_srvs/srv/Trigger
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # ─────────────────────────────────────────────────────────────────────
        # Gallery / Map paths (YOU MUST SET THESE after running do_SfM.sh)
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument(
            name='gallery_global_descriptor_path',
            default_value='/image-gallery/outputs/netvlad+superpoint_aachen+superglue/global-feats-netvlad.h5',
            description='Path to the global (NetVLAD) feature database (.h5)'
        ),
        DeclareLaunchArgument(
            name='gallery_local_descriptor_path',
            default_value='/image-gallery/outputs/netvlad+superpoint_aachen+superglue/feats-superpoint-n4096-r1024.h5',
            description='Path to the local (SuperPoint) feature database (.h5)'
        ),
        DeclareLaunchArgument(
            name='image_gallery_path',
            default_value='/image-gallery/',
            description='Root directory containing gallery images'
        ),
        DeclareLaunchArgument(
            name='gallery_sfm_path',
            default_value='/image-gallery/outputs/netvlad+superpoint_aachen+superglue/sfm_netvlad+superpoint_aachen+superglue',
            description='Path to the COLMAP SfM output directory'
        ),

        # ─────────────────────────────────────────────────────────────────────
        # AI / Model settings
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument('global_extractor_name',  default_value='netvlad'),
        DeclareLaunchArgument('local_extractor_name',   default_value='superpoint_aachen'),
        DeclareLaunchArgument('local_matcher_name',     default_value='superglue'),
        DeclareLaunchArgument('top_k_matches',          default_value='4'),
        DeclareLaunchArgument('ransac_thresh',          default_value='12'),

        # ─────────────────────────────────────────────────────────────────────
        # Sensor offset (set True + base_frame/sensor_frame if camera is offset)
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument('compensate_sensor_offset', default_value='False'),
        DeclareLaunchArgument('base_frame',               default_value='base_link'),
        DeclareLaunchArgument('sensor_frame',             default_value='camera'),

        # ─────────────────────────────────────────────────────────────────────
        # ROS topics
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument('camera_topic',           default_value='/image_raw'),
        DeclareLaunchArgument('cmd_vel_topic',          default_value='/cmd_vel'),
        DeclareLaunchArgument('initialpose_topic',      default_value='/initialpose'),
        DeclareLaunchArgument('timeout_seconds',        default_value='60.0'),

        # ─────────────────────────────────────────────────────────────────────
        # Node 1: AI localization pipeline
        # ─────────────────────────────────────────────────────────────────────
        Node(
            package='visual_robot_localization',
            executable='visual_localizer_node',
            name='visual_localization_node',
            output='screen',
            emulate_tty=True,
            parameters=[{
                # On-demand mode: listen to image_request from recovery_node
                'camera_topic':                   '/visual_localization/image_request',
                'pose_publish_topic':             '/visual_localization/pose_response',
                'global_extractor_name':          LaunchConfiguration('global_extractor_name'),
                'local_extractor_name':           LaunchConfiguration('local_extractor_name'),
                'local_matcher_name':             LaunchConfiguration('local_matcher_name'),
                'gallery_global_descriptor_path': LaunchConfiguration('gallery_global_descriptor_path'),
                'gallery_local_descriptor_path':  LaunchConfiguration('gallery_local_descriptor_path'),
                'image_gallery_path':             LaunchConfiguration('image_gallery_path'),
                'gallery_sfm_path':               LaunchConfiguration('gallery_sfm_path'),
                'top_k_matches':                  LaunchConfiguration('top_k_matches'),
                'ransac_thresh':                  LaunchConfiguration('ransac_thresh'),
                'compensate_sensor_offset':       LaunchConfiguration('compensate_sensor_offset'),
                'base_frame':                     LaunchConfiguration('base_frame'),
                'sensor_frame':                   LaunchConfiguration('sensor_frame'),
                'align_camera_frame':             False,
                'visualize_estimates':            False,
            }]
        ),

        # ─────────────────────────────────────────────────────────────────────
        # Node 2: Recovery orchestrator bridge
        # ─────────────────────────────────────────────────────────────────────
        Node(
            package='visual_recovery',
            executable='recovery_node',
            name='visual_recovery_node',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'camera_topic':         LaunchConfiguration('camera_topic'),
                'cmd_vel_topic':        LaunchConfiguration('cmd_vel_topic'),
                'request_image_topic':  '/visual_localization/image_request',
                'response_pose_topic':  '/visual_localization/pose_response',
                'initialpose_topic':    LaunchConfiguration('initialpose_topic'),
                'timeout_seconds':      LaunchConfiguration('timeout_seconds'),
            }]
        ),
    ])
