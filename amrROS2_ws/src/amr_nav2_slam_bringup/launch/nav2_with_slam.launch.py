#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition

def generate_launch_description():

    # ---- Launch Args ----
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true')

    map_file = DeclareLaunchArgument(
        'map', default_value='',
        description='Full path to existing map YAML (for Nav2 costmaps & visualization)')

    nav2_params = DeclareLaunchArgument(
        'nav2_params', 
        default_value=PathJoinSubstitution([
            get_package_share_directory('navigation'),
            'config', 'nav2_params.yaml'
        ]),
        description='Nav2 parameters file')

    slam_params = DeclareLaunchArgument(
        'slam_params',
        default_value=PathJoinSubstitution([
            get_package_share_directory('navigation'),
            'config', 'slam_localization.yaml'
        ]),
        description='Slam Toolbox parameters file')

    autostart = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically startup the nav2 lifecycle nodes')

    use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch RViz2 alongside the navigation stack')

    rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            get_package_share_directory('navigation'),
            'rviz', 'rviz_nav.rviz'
        ]),
        description='RViz configuration file for visualization')

    # ---- Include Nav2 Bringup (no AMCL, no internal SLAM) ----
    bringup_pkg_dir = get_package_share_directory('amr_nav2_slam_bringup')
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [bringup_pkg_dir, '/launch/bringup_no_route.launch.py']
        ),
        launch_arguments={
            # IMPORTANT: don't let nav2 spawn amcl or slam_toolbox for us
            'slam': 'False',
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': LaunchConfiguration('nav2_params'),
            'map': LaunchConfiguration('map'),
            'autostart': LaunchConfiguration('autostart'),
        }.items()
    )

    # ---- Slam Toolbox (online_async) ----
    # It will publish map->odom and build a new posegraph.
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            LaunchConfiguration('slam_params'),
            {
                # Inject the map yaml of the existing map so SLAM aligns from the start
                'map_file_name': LaunchConfiguration('map'),
                # If you know the start pose in the existing map, set it here or via /initialpose
                # 'map_start_at_dock': True,
                # 'map_start_pose': [0.0, 0.0, 0.0]
            }
        ],
        remappings=[
            # Adjust if your lidar topic is different
            ('/scan', '/scan'),
            ('/odom', '/odom')
        ]
    )

    rviz_node = Node(
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        package='rviz2',
        executable='rviz2',
        name='nav2_rviz',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # Optional: avoid FastDDS noisy logs, keep clean
    env_log = SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1')

    return LaunchDescription([
        use_sim_time, map_file, nav2_params, slam_params, autostart,
        use_rviz, rviz_config,
        env_log,
        nav2_launch,
        slam_toolbox_node,
        rviz_node,
    ])
