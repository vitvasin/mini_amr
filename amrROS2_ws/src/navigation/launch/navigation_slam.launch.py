import os
import json
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution, IfElseSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node, PushRosNamespace, SetRemap
from nav2_common.launch import RewrittenYaml, ReplaceString

def generate_launch_description():
    # Get package directories
    robot_navigation_dir = get_package_share_directory("navigation")
    robot_bringup_dir = get_package_share_directory("bringup")

    # Launch configurations
    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    use_rviz = LaunchConfiguration("rviz")
    use_sim_time = LaunchConfiguration('sim')
    nav_params_file = LaunchConfiguration('nav_params_file')
    mapping_params_file = LaunchConfiguration('mapping_params_file')
    rviz_config_file = LaunchConfiguration('rviz_config_file')

    # Default configurations
    namespace_replacement = IfElseSubstitution(
        use_namespace,
        if_value=('/', namespace),
        else_value=''
    )

    # Parameter file configurations
    nav_params_file = ReplaceString(
        source_file=nav_params_file,
        replacements={'<robot_namespace>': namespace_replacement})

    mapping_params_file = ReplaceString(
        source_file=mapping_params_file,
        replacements={'<robot_namespace>': namespace_replacement})

    # Launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='prefix for node name'
    )
    
    declare_use_namespace_cmd = DeclareLaunchArgument(
        'use_namespace',
        default_value='false',
        description='Whether to apply a namespace to the navigation stack'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='sim',
        default_value='false',
        description='Enable use_sime_time to true'
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='rviz',
        default_value='true',
        description='Run rviz'
    )

    declare_nav_params_file_cmd = DeclareLaunchArgument(
        'nav_params_file',
        default_value=PathJoinSubstitution([robot_navigation_dir, "config", "nav2_params.yaml"]),
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    declare_mapping_params_file_cmd = DeclareLaunchArgument(
        'mapping_params_file',
        default_value=PathJoinSubstitution([robot_navigation_dir, "config", "mapper_params_online_async.yaml"]),
        description='Full path to the SLAM mapping parameters file'
    )

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(robot_navigation_dir, 'rviz', 'nav2_default_view.rviz'),
        description='Full path to the RVIZ config file to use'
    )

    # Include required launch files
    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(robot_navigation_dir, "launch", 'rviz_launch.py')),
        condition=IfCondition(use_rviz),
        launch_arguments={
            'namespace': namespace,
            'use_namespace': use_namespace,
            'use_sim_time': use_sim_time,
            'rviz_config': rviz_config_file,
        }.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [robot_navigation_dir, 'launch', 'navigation_launch.py'])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav_params_file,
            'map_subscribe_transient_local': 'true'
        }.items()
    )

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [robot_navigation_dir, 'launch', 'slam_toolbox_launch.py'])),
        launch_arguments={
            'autostart': 'true',
            'use_sim_time': use_sim_time,
            'slam_params_file': mapping_params_file,
            'use_lifecycle_manager': 'false',
            'namespace': namespace,
            'use_namespace': use_namespace,
        }.items()
    )

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [robot_bringup_dir, 'launch', 'bringup.launch.py']))
    )

    # Group all actions
    launch_elements = GroupAction(
        actions=[
            PushRosNamespace(condition=IfCondition(use_namespace), namespace=namespace),
            SetRemap('/tf', 'tf'),
            SetRemap('/tf_static', 'tf_static'),
            bringup,
            slam_toolbox,
            navigation,
            rviz_cmd,
        ]
    )

    return LaunchDescription([
        # Declare the launch options
        declare_namespace_cmd,
        declare_use_namespace_cmd,
        declare_nav_params_file_cmd,
        declare_mapping_params_file_cmd,
        declare_use_sim_time_cmd,
        declare_use_rviz_cmd,
        declare_rviz_config_file_cmd,
        # Launch all navigation nodes
        launch_elements
    ])
