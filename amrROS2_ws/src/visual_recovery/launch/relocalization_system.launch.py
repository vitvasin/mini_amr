"""
relocalization_system.launch.py
--------------------------------
Starts the full relocalization system with configurable switches:
  1. visual_localizer_node   — AI pipeline (disabled by default)
  2. marker_localizer_node   — Fiducial Marker pipeline (enabled by default)
  3. recovery_node           — Orchestrator (calls the selected method)

USAGE:
  ros2 launch visual_recovery relocalization_system.launch.py \
      enable_ai:=false \
      enable_marker:=true \
      recovery_method:=marker

TRIGGER (in a separate terminal, after launch):
  ros2 service call /visual_recovery_node/trigger_recovery std_srvs/srv/Trigger
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([

        # ─────────────────────────────────────────────────────────────────────
        # Relocalization Config Switches
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument(
            name='enable_ai',
            default_value='false',
            description='Whether to launch the heavy 3D AI localization node'
        ),
        DeclareLaunchArgument(
            name='enable_marker',
            default_value='true',
            description='Whether to launch the ArUco fiducial marker localization node'
        ),
        DeclareLaunchArgument(
            name='recovery_method',
            default_value='marker',
            description='Relocalization recovery method to use: marker, ai, or hybrid'
        ),

        # ─────────────────────────────────────────────────────────────────────
        # Fiducial Marker settings
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument(
            name='marker_size',
            default_value='0.15',
            description='Size of ArUco markers in meters'
        ),
        DeclareLaunchArgument(
            name='marker_dictionary_name',
            default_value='DICT_4X4_50',
            description='ArUco dictionary name to detect'
        ),
        DeclareLaunchArgument(
            name='markers_config',
            default_value='{"1": {"x": 0.0, "y": 0.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}, "2": {"x": 2.0, "y": 1.0, "z": 1.0, "roll": 0.0, "pitch": 0.0, "yaw": 1.5708}}',
            description='JSON string containing marker ID and 6DoF poses on the map'
        ),
        DeclareLaunchArgument(
            name='markers_yaml',
            default_value=os.path.join(get_package_share_directory('marker_localization'), 'config', 'markers_auto.yaml'),
            description='Path to the markers configuration YAML file'
        ),

        # ─────────────────────────────────────────────────────────────────────
        # Gallery / Map paths (for the AI localizer)
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
        DeclareLaunchArgument('compensate_sensor_offset', default_value='True'),
        DeclareLaunchArgument('base_frame',               default_value='base_link'),
        DeclareLaunchArgument('sensor_frame',             default_value='rgbd_frame'),

        # ─────────────────────────────────────────────────────────────────────
        # ROS topics
        # ─────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument('camera_topic',           default_value='/image_raw'),
        DeclareLaunchArgument('cmd_vel_topic',          default_value='/cmd_vel'),
        DeclareLaunchArgument('initialpose_topic',      default_value='/initialpose'),
        DeclareLaunchArgument('timeout_seconds',        default_value='60.0'),

        # ─────────────────────────────────────────────────────────────────────
        # Node 1: AI localization pipeline (Only launched if enable_ai is true)
        # ─────────────────────────────────────────────────────────────────────
        Node(
            package='visual_robot_localization',
            executable='visual_localizer_node',
            name='visual_localization_node',
            output='screen',
            emulate_tty=True,
            condition=IfCondition(LaunchConfiguration('enable_ai')),
            parameters=[{
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
        # Node 2: Fiducial Marker pipeline (Only launched if enable_marker is true)
        # ─────────────────────────────────────────────────────────────────────
        Node(
            package='marker_localization',
            executable='marker_localizer_node',
            name='marker_localization_node',
            output='screen',
            emulate_tty=True,
            condition=IfCondition(LaunchConfiguration('enable_marker')),
            parameters=[{
                'camera_topic':                   '/marker_localization/image_request',
                'pose_publish_topic':             '/marker_localization/pose_response',
                'camera_info_topic':              '/camera_info',
                'marker_size':                    LaunchConfiguration('marker_size'),
                'marker_dictionary_name':         LaunchConfiguration('marker_dictionary_name'),
                'compensate_sensor_offset':       LaunchConfiguration('compensate_sensor_offset'),
                'base_frame':                     LaunchConfiguration('base_frame'),
                'sensor_frame':                   LaunchConfiguration('sensor_frame'),
                'markers_config':                 ParameterValue(LaunchConfiguration('markers_config'), value_type=str),
            },
            LaunchConfiguration('markers_yaml')
            ]
        ),

        # ─────────────────────────────────────────────────────────────────────
        # Node 3: Recovery orchestrator bridge
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
                'initialpose_topic':    LaunchConfiguration('initialpose_topic'),
                'timeout_seconds':      LaunchConfiguration('timeout_seconds'),
                'recovery_method':      LaunchConfiguration('recovery_method'),
                'request_image_topic':  '/visual_localization/image_request',
                'response_pose_topic':  '/visual_localization/pose_response',
                'request_marker_image_topic': '/marker_localization/image_request',
                'response_marker_pose_topic': '/marker_localization/pose_response',
            }]
        ),
    ])
