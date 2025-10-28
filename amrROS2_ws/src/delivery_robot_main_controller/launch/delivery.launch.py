from launch import LaunchDescription
from launch_ros.actions import Node, PushRosNamespace,  SetRemap
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
import os
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    
    namespace = LaunchConfiguration("namespace")
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value= [EnvironmentVariable('NAMESPACE')],
        description='prefix for node name')
    
    main_controller = Node(
            package='delivery_robot_main_controller',
            executable='delivery_robot_main_controller',
            name='main_controller_node',
            parameters=[],  # ใส่ parameter file ได้ถ้ามี
            output='screen',
            emulate_tty=True,
    )
    
    robot_sound = Node(
            package='delivery_robot_main_controller',
            executable='robot_sound',
            name='robot_sound_node',
            output='screen',
            emulate_tty=True,
    )

    call_robot_button = Node(
            package='delivery_robot_main_controller',
            executable='call_robot_button',
            name='call_robot_button_node',
            output='screen',
            emulate_tty=True,
    )

    launch_elements = GroupAction(
    	actions=[
        PushRosNamespace(namespace),
        SetRemap('/tf','tf'),
        SetRemap('/tf_static','tf_static'),
        main_controller,
        robot_sound,
        call_robot_button,
        ]
    )

    autodock_launch = IncludeLaunchDescription(
         PythonLaunchDescriptionSource(
             os.path.join(
                 get_package_share_directory('action_autodock'),
                 'launch',
                 'auto_dock_launch.py'
             )
         ),
         launch_arguments={'namespace': namespace}.items()
    )

    return LaunchDescription([
        declare_namespace_cmd,
        launch_elements,
        autodock_launch
    ])
