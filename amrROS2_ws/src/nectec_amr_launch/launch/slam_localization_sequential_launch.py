import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, ExecuteProcess, RegisterEventHandler, EmitEvent
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    # Define paths
    map_yaml = "/home/smr/workspaces/mini_amr/amrROS2_ws/maps/latest_map"
    keepout_mask_yaml = "/home/smr/workspaces/mini_amr/amrROS2_ws/maps/latest_map_keepout.yaml"
    amr_ui_path = "/home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR"
    
    # 0. Localization Monitor
    localization_monitor_node = Node(
        package='localization_monitor',
        executable='localization_monitor',
        name='localization_monitor',
        output='screen',
        parameters=[{
            'pose_timeout': 60.0,
            'covariance_threshold': 0.5
        }]
    )
    
    # 1. Navigation Launch (SLAM Localization)
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('navigation'),
                'launch',
                'navigation.launch.py'
            ])
        ]),
        launch_arguments={
            'map': map_yaml,
            'rviz': 'false',
            'rviz_config_file': PathJoinSubstitution([
                FindPackageShare('navigation'),
                'rviz',
                'rviz_nav_slam.rviz'
            ]),
            'use_keepout_zones': 'true',
            'keepout_mask_yaml': keepout_mask_yaml
        }.items()
    )

    # Declare launch arguments for switching relocalization methods
    enable_ai = LaunchConfiguration('enable_ai')
    enable_marker = LaunchConfiguration('enable_marker')
    recovery_method = LaunchConfiguration('recovery_method')

    declare_enable_ai = DeclareLaunchArgument(
        name='enable_ai',
        default_value='false',
        description='Whether to launch the heavy 3D AI localization node'
    )
    declare_enable_marker = DeclareLaunchArgument(
        name='enable_marker',
        default_value='true',
        description='Whether to launch the ArUco fiducial marker localization node'
    )
    declare_recovery_method = DeclareLaunchArgument(
        name='recovery_method',
        default_value='marker',
        description='Relocalization recovery method to use: marker, ai, or hybrid'
    )

    # 0.5. Visual Relocalization / Recovery System
    relocalization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('visual_recovery'),
                'launch',
                'relocalization_system.launch.py'
            ])
        ]),
        launch_arguments={
            'enable_ai': enable_ai,
            'enable_marker': enable_marker,
            'recovery_method': recovery_method,
            'image_gallery_path': '/home/smr/workspaces/mini_amr/amrROS2_ws/src/visual_robot_localization/test/image_dataset/',
            'gallery_global_descriptor_path': '/home/smr/workspaces/mini_amr/amrROS2_ws/src/visual_robot_localization/test/image_dataset/outputs/netvlad+superpoint_aachen+superglue/global-feats-netvlad.h5',
            'gallery_local_descriptor_path': '/home/smr/workspaces/mini_amr/amrROS2_ws/src/visual_robot_localization/test/image_dataset/outputs/netvlad+superpoint_aachen+superglue/feats-superpoint-n4096-r1024.h5',
            'gallery_sfm_path': '/home/smr/workspaces/mini_amr/amrROS2_ws/src/visual_robot_localization/test/image_dataset/outputs/netvlad+superpoint_aachen+superglue/sfm_netvlad+superpoint_aachen+superglue'
        }.items()
    )

    # 2. Delivery Robot Controller (5s delay)
    delivery_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('delivery_robot_main_controller'),
                'launch',
                'delivery.launch.py'
            ])
        ]),
        launch_arguments={
            'localization_mode': 'slam_toolbox'
        }.items()
    )

    delayed_delivery_launch = TimerAction(
        period=5.0,  # Reverted back from 65.0s
        actions=[delivery_launch]
    )

    # 3. AMR UI (10s delay - 5s after delivery)
    # Command: cd $AMR_UI && source ../env/bin/activate && python main.py
    # Using explicit bash to support 'source' and &&
    ui_cmd = f"cd {amr_ui_path} && source ../env/bin/activate && python main.py"
    
    ui_action = ExecuteProcess(
        cmd=['/bin/bash', '-c', ui_cmd],
        output='screen'
    )

    delayed_ui_launch = TimerAction(
        period=13.0,  # Reverted back from 75.0s
        actions=[ui_action]
    )

    # 4. Shutdown Handler (Close everything when UI closes)
    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=ui_action,
            on_exit=[EmitEvent(event=Shutdown())]
        )
    )

    return LaunchDescription([
        declare_enable_ai,
        declare_enable_marker,
        declare_recovery_method,
        localization_monitor_node,
        navigation_launch,
        relocalization_launch,
        delayed_delivery_launch,
        delayed_ui_launch,
        shutdown_handler
    ])
