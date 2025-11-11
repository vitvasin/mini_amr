#!/usr/bin/env python3

"""Launch Nav2 with AMCL while recording a SLAM Toolbox pose graph.

This bringup keeps the Nav2 stack in the default AMCL localization mode and
spawns an additional slam_toolbox node so you can serialize a .posegraph/.data
after the run (e.g. with Shortcut/save_slamtb_map.sh).
"""

import os
from typing import List

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def _serialize_posegraph_on_shutdown(context) -> List:
    """Generate actions to serialize the pose graph when the launch shuts down."""
    target_path = LaunchConfiguration('posegraph_output').perform(context).strip()
    if not target_path:
        return [
            LogInfo(
                msg='[posegraph] posegraph_output is empty; skipping pose graph serialization.'
            )
        ]

    service_name = LaunchConfiguration('posegraph_service').perform(context).strip()
    request = f'{{filename: "{target_path}"}}'

    return [
        LogInfo(msg=f'[posegraph] Serializing SLAM Toolbox pose graph to {target_path}'),
        ExecuteProcess(
            cmd=[
                'ros2',
                'service',
                'call',
                service_name or '/slam_toolbox/serialize_map',
                'slam_toolbox/srv/SerializePoseGraph',
                request,
            ],
            name='serialize_posegraph',
            output='screen',
        ),
    ]


def generate_launch_description():
    bringup_dir = get_package_share_directory('amr_nav2_slam_bringup')
    robot_bringup_dir = get_package_share_directory('bringup')
    navigation_dir = get_package_share_directory('navigation')
    description_dir = get_package_share_directory('description')

    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    nav2_params = LaunchConfiguration('nav2_params')
    slam_params = LaunchConfiguration('slam_params')
    slam_map_frame = LaunchConfiguration('slam_map_frame')
    slam_scan_topic = LaunchConfiguration('slam_scan_topic')
    autostart = LaunchConfiguration('autostart')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')
    slam_use_rviz = LaunchConfiguration('slam_use_rviz')
    slam_rviz_config = LaunchConfiguration('slam_rviz_config')
    auto_serialize = LaunchConfiguration('auto_serialize_on_shutdown')
    run_bringup = LaunchConfiguration('run_bringup')
    bringup_params = LaunchConfiguration('bringup_params')
    bringup_model = LaunchConfiguration('bringup_model')
    bringup_use_rviz = LaunchConfiguration('bringup_use_rviz')
    initial_pose_x = LaunchConfiguration('initial_pose_x')
    initial_pose_y = LaunchConfiguration('initial_pose_y')
    initial_pose_yaw = LaunchConfiguration('initial_pose_yaw')

    stdout_linebuf_envvar = SetEnvironmentVariable(
        'RCUTILS_LOGGING_BUFFERED_STREAM', '1'
    )

    declare_namespace = DeclareLaunchArgument(
        'namespace', default_value='', description='Optional top-level namespace'
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true',
    )

    declare_map_file = DeclareLaunchArgument(
        'map',
        default_value='',
        description='Full path to the map YAML used by AMCL',
    )

    declare_nav2_params = DeclareLaunchArgument(
        'nav2_params',
        default_value=PathJoinSubstitution(
            [navigation_dir, 'config', 'nav2_params.yaml']
        ),
        description='Nav2 parameters file (should enable AMCL)',
    )

    declare_slam_params = DeclareLaunchArgument(
        'slam_params',
        default_value=PathJoinSubstitution(
            [navigation_dir, 'config', 'mapper_params_online_async.yaml']
        ),
        description='slam_toolbox parameters file used for pose graph recording',
    )

    declare_slam_map_frame = DeclareLaunchArgument(
        'slam_map_frame',
        default_value='slam_map',
        description='Frame ID published by slam_toolbox pose graph (kept separate from Nav2 map)',
    )

    declare_slam_scan_topic = DeclareLaunchArgument(
        'slam_scan_topic',
        default_value='scan',
        description='Laser scan topic streamed into slam_toolbox',
    )

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically bring the Nav2 lifecycle nodes online',
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true', description='Launch RViz for visualization'
    )

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution(
            [navigation_dir, 'rviz', 'rviz_nav.rviz']
        ),
        description='RViz2 configuration file',
    )

    declare_slam_use_rviz = DeclareLaunchArgument(
        'slam_use_rviz',
        default_value='true',
        description='Launch a dedicated RViz window focused on SLAM map growth',
    )

    declare_slam_rviz_config = DeclareLaunchArgument(
        'slam_rviz_config',
        default_value=PathJoinSubstitution(
            [navigation_dir, 'rviz', 'slam.rviz']
        ),
        description='RViz2 configuration file for SLAM visualization',
    )

    declare_auto_serialize = DeclareLaunchArgument(
        'auto_serialize_on_shutdown',
        default_value='false',
        description='Automatically call serialize_map when the launch terminates',
    )

    declare_run_bringup = DeclareLaunchArgument(
        'run_bringup',
        default_value='true',
        description='Launch the bringup stack alongside navigation',
    )

    declare_bringup_params = DeclareLaunchArgument(
        'bringup_params',
        default_value=PathJoinSubstitution(
            [robot_bringup_dir, 'config', 'bringup.yaml']
        ),
        description='Parameters file for the bringup package',
    )

    declare_bringup_model = DeclareLaunchArgument(
        'bringup_model',
        default_value=PathJoinSubstitution(
            [description_dir, 'urdf/robot', 'robot.urdf.xacro']
        ),
        description='Robot model used by bringup',
    )

    declare_bringup_use_rviz = DeclareLaunchArgument(
        'bringup_use_rviz',
        default_value='false',
        description='Enable RViz instance from bringup (Nav2 RViz launches separately)',
    )

    declare_initial_pose_x = DeclareLaunchArgument(
        'initial_pose_x',
        default_value='1.428',
        description='Initial pose X (match AMCL initial pose)',
    )

    declare_initial_pose_y = DeclareLaunchArgument(
        'initial_pose_y',
        default_value='-4.288',
        description='Initial pose Y (match AMCL initial pose)',
    )

    declare_initial_pose_yaw = DeclareLaunchArgument(
        'initial_pose_yaw',
        default_value='0.0',
        description='Initial pose yaw in radians (match AMCL initial pose)',
    )

    declare_posegraph_output = DeclareLaunchArgument(
        'posegraph_output',
        default_value='',
        description='Target path (without extension) for serialized pose graph (.posegraph/.data)',
    )

    declare_posegraph_service = DeclareLaunchArgument(
        'posegraph_service',
        default_value='/slam_toolbox/serialize_map',
        description='Service name for slam_toolbox SerializePoseGraph',
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'bringup_no_route.launch.py')
        ),
        launch_arguments={
            'namespace': namespace,
            'slam': 'False',
            'map': map_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'params_file': nav2_params,
            'use_localization': 'True',
        }.items(),
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='posegraph_recorder',
        namespace=namespace,
        output='screen',
        parameters=[
            slam_params,
            {
                'use_sim_time': use_sim_time,
                'map_frame': slam_map_frame,
                'map_start_pose': [initial_pose_x, initial_pose_y, initial_pose_yaw],
                'scan_topic': slam_scan_topic,
            },
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('/scan', slam_scan_topic),
            ('map', 'slam_map'),
            ('/map', '/slam_map'),
            ('map_metadata', 'slam_map_metadata'),
            ('/map_metadata', '/slam_map_metadata'),
            ('map_updates', 'slam_map_updates'),
            ('/map_updates', '/slam_map_updates'),
        ],
    )

    rviz_node = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='nav2_rviz',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    slam_rviz_node = Node(
        condition=IfCondition(slam_use_rviz),
        package='rviz2',
        executable='rviz2',
        name='slam_rviz',
        output='screen',
        arguments=['-d', slam_rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_bringup_dir, 'launch', 'bringup.launch.py')
        ),
        condition=IfCondition(run_bringup),
        launch_arguments={
            'params_file': bringup_params,
            'bringup_rviz': bringup_use_rviz,
            'model': bringup_model,
            'sim': use_sim_time,
        }.items(),
    )

    serialize_posegraph_handler = RegisterEventHandler(
        OnShutdown(on_shutdown=[OpaqueFunction(function=_serialize_posegraph_on_shutdown)]),
        condition=IfCondition(auto_serialize),
    )

    ld = LaunchDescription()

    ld.add_action(stdout_linebuf_envvar)
    ld.add_action(declare_namespace)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_map_file)
    ld.add_action(declare_nav2_params)
    ld.add_action(declare_slam_params)
    ld.add_action(declare_slam_map_frame)
    ld.add_action(declare_slam_scan_topic)
    ld.add_action(declare_autostart)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_rviz_config)
    ld.add_action(declare_slam_use_rviz)
    ld.add_action(declare_slam_rviz_config)
    ld.add_action(declare_auto_serialize)
    ld.add_action(declare_run_bringup)
    ld.add_action(declare_bringup_params)
    ld.add_action(declare_bringup_model)
    ld.add_action(declare_bringup_use_rviz)
    ld.add_action(declare_initial_pose_x)
    ld.add_action(declare_initial_pose_y)
    ld.add_action(declare_initial_pose_yaw)
    ld.add_action(declare_posegraph_output)
    ld.add_action(declare_posegraph_service)
    ld.add_action(nav2_launch)
    ld.add_action(bringup_launch)
    ld.add_action(slam_toolbox_node)
    ld.add_action(rviz_node)
    ld.add_action(slam_rviz_node)
    ld.add_action(serialize_posegraph_handler)

    return ld
