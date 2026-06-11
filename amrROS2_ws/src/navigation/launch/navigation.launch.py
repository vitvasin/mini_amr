import os
import json
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression, EnvironmentVariable, TextSubstitution, IfElseSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition

from launch_ros.actions import Node, PushRosNamespace, SetRemap
from nav2_common.launch import RewrittenYaml, ReplaceString
from launch_ros.descriptions import ParameterFile

def generate_launch_description():
 
    robot_navigation_dir = get_package_share_directory("navigation")
    robot_bringup_dir = get_package_share_directory("bringup")
    nav2_bringup_dir = get_package_share_directory("nav2_bringup")
    slam_toolbox_dir = get_package_share_directory("slam_toolbox")

    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    use_rviz = LaunchConfiguration("rviz")
    use_sim_time = LaunchConfiguration('sim')
    use_slam_tb = LaunchConfiguration('slam_tb')
    use_mapping = LaunchConfiguration('use_mapping')
    nav_params_file = LaunchConfiguration('nav_params_file')    
    localize_params_file = LaunchConfiguration('localize_params_file')
    mapping_params_file = LaunchConfiguration('mapping_params_file')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    map = LaunchConfiguration("map")
    bringup = LaunchConfiguration("bringup")

    workspace_path = os.environ.get('ROS_WS', '/home/smr/workspaces/mini_amr/amrROS2_ws')
    config_path = os.path.join(workspace_path, "maps", "config.json")

    with open(config_path, "r") as f:
        config = json.load(f)

    default_map_path = os.path.join(workspace_path, "maps", config['map']['name'])

    namespace_replacement = IfElseSubstitution(
        use_namespace,
        if_value = ('/', namespace),
        else_value = '')
    
    slam_toolbox_params_file = IfElseSubstitution(
        use_mapping,
        if_value = mapping_params_file,
        else_value = localize_params_file)
    
    map2run = IfElseSubstitution(
        use_mapping,
        if_value = '',
        else_value = map)

    localize_params_file = ReplaceString(
        source_file=localize_params_file,
        replacements={'<robot_namespace>': namespace_replacement})
    
    mapping_params_file = ReplaceString(
        source_file=mapping_params_file,
        replacements={'<robot_namespace>': namespace_replacement})

    nav_params_file = ReplaceString(
        source_file=nav_params_file,
        replacements={'<robot_namespace>': namespace_replacement})   
    
    
    declare_namespace_cmd = DeclareLaunchArgument(
            'namespace',
            # default_value= [EnvironmentVariable('NAMESPACE')],
            default_value= '',
            description='prefix for node name'
        )
    
    declare_use_namespace_cmd = DeclareLaunchArgument(
            'use_namespace',
            default_value='false',
            description='Whether to apply a namespace to the navigation stack'
        )

    declare_map_cmd = DeclareLaunchArgument(
            name='map', 
            default_value= default_map_path,
            description='Navigation map path'
        )
    declare_keepout_mask_yaml_cmd = DeclareLaunchArgument(
            name='keepout_mask_yaml', 
            default_value= default_map_path,
            description='Keepout mask yaml file path'
        )
    declare_use_keepout_zones_cmd = DeclareLaunchArgument(
            name='use_keepout_zones', 
            default_value='true',
            description='Enable keepout zones'
        )
    declare_use_sim_time_cmd = DeclareLaunchArgument(
            name='sim', 
            default_value='false',
            description='Enable use_sime_time to true'
        )
    declare_use_rviz_cmd = DeclareLaunchArgument(
            name='rviz', 
            default_value='false',
            description='Run rviz'
        )
    declare_use_slam_tb_cmd = DeclareLaunchArgument(
            name='slam_tb', 
            default_value='true',
            description='Using slam toolbox localization'
        )
    declare_use_mapping_cmd = DeclareLaunchArgument(
            name='use_mapping', 
            default_value='false',
            description='Using slam toolbox mapping'
        )
    declare_bringup_cmd = DeclareLaunchArgument(
            name='bringup', 
            default_value='true',
            description='Bringup robot with this command'
        )
    
    declare_nav_params_file_cmd = DeclareLaunchArgument(
        'nav_params_file',
        default_value= PathJoinSubstitution([robot_navigation_dir, "config", "nav2_params.yaml"]),
        description='Full path to the ROS2 parameters file to use for all launched nodes')
    
    declare_localize_params_file_cmd = DeclareLaunchArgument(
        'localize_params_file',
        default_value= PathJoinSubstitution([robot_navigation_dir, "config", "slam_localization.yaml"]),
        description='Full path to the SLAM localization parameters file')
    
    declare_mapping_params_file_cmd = DeclareLaunchArgument(
        'mapping_params_file',
        default_value=PathJoinSubstitution([robot_navigation_dir, "config", "mapper_params_online_async.yaml"]),
        description='Full path to the SLAM mapping parameters file')
    
    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(robot_navigation_dir, 'rviz', 'nav2_default_view.rviz'),
        description='Full path to the RVIZ config file to use',
    )
    
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
                'params_file':  nav_params_file,
                'map_subscribe_transient_local': 'true',
                'keepout_mask_yaml': LaunchConfiguration('keepout_mask_yaml'),
                'use_keepout_zones': LaunchConfiguration('use_keepout_zones'),
            }.items()
        )
    
    amcl = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
                [robot_navigation_dir, 'launch', 'amcl_localization_launch.py'])),
            # condition=UnlessCondition(use_mapping),
            condition=IfCondition(
                PythonExpression(["'", use_mapping, "' == 'false' and'", use_slam_tb, "' == 'false'" ])),
            launch_arguments={
                'map' : map,
                'use_sim_time': use_sim_time,
                'params_file':  nav_params_file,
            }.items()
        )
    
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
                [robot_navigation_dir, 'launch', 'slam_toolbox_launch.py'])),
            condition=IfCondition(
                PythonExpression(["'", use_mapping, "' == 'true' and'", use_slam_tb, "' == 'true'" ])),
            launch_arguments={                
                'autostart':  'true',
                'use_sim_time': use_sim_time,
                'slam_params_file' : slam_toolbox_params_file,
                'use_lifecycle_manager': 'false',
                'namespace': namespace,
                'use_namespace': use_namespace,
                'map_file_name': map2run,
            }.items()
        )
    slam_toolbox_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
                [robot_navigation_dir, 'launch', 'slam_localization_launch.py'])),
            condition=IfCondition(
                PythonExpression(["'", use_mapping, "' == 'false' and'", use_slam_tb, "' == 'true'" ])),
            launch_arguments={                
                'autostart':  'true',
                'use_sim_time': use_sim_time,
                'slam_params_file' : slam_toolbox_params_file,
                'use_lifecycle_manager': 'false',
                'namespace': namespace,
                'use_namespace': use_namespace,
                'map_file_name': map2run,
            }.items()
        )
    
    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
                [robot_bringup_dir, 'launch', 'bringup.launch.py'])),
            condition=IfCondition(bringup) #default is false
        )

    localization_monitor_node = Node(
        package='localization_monitor',
        executable='localization_monitor',
        name='localization_monitor',
        output='screen',
        parameters=[{
            'covariance_threshold': 0.4,
            'check_interval': 1.0,
            'pose_timeout': 60.0
        }]
    )

    delayed_slam_toolbox = TimerAction(
        period=10.0,
        actions=[slam_toolbox]
    )

    delayed_slam_toolbox_localization = TimerAction(
        period=10.0,
        actions=[slam_toolbox_localization]
    )

    delayed_navigation = TimerAction(
        period=45.0,  # Increased from 25s: give slam_toolbox 35s after activation to match scans
        actions=[navigation]
    )

    launch_elements = GroupAction(
     actions=[
        PushRosNamespace(condition=IfCondition(use_namespace), namespace=namespace),
        SetRemap('/tf','tf'),
        SetRemap('/tf_static','tf_static'),
        bringup,
        amcl,
        delayed_slam_toolbox,
        delayed_slam_toolbox_localization,
        delayed_navigation,
        rviz_cmd,
        localization_monitor_node,
      ]
   )

    return LaunchDescription([
        # Declare the launch options
        declare_namespace_cmd,
        declare_use_namespace_cmd,
        declare_use_mapping_cmd,
        declare_nav_params_file_cmd,
        declare_localize_params_file_cmd,
        declare_mapping_params_file_cmd,
        declare_map_cmd,
        declare_bringup_cmd,
        declare_use_sim_time_cmd,
        declare_use_rviz_cmd,
        declare_use_slam_tb_cmd,
        declare_rviz_config_file_cmd,
        declare_keepout_mask_yaml_cmd,
        declare_use_keepout_zones_cmd,
        #Launch all navigation nodes
        launch_elements
    ])