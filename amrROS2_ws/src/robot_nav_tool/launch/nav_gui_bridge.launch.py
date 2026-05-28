import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.substitutions import TextSubstitution
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    robot_ns_launch_arg = DeclareLaunchArgument("robot_ns", default_value=TextSubstitution(text="lapras"))

    launch_include_with_namespaces_webbridge = GroupAction(actions=[PushRosNamespace(
        LaunchConfiguration('robot_ns')),IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('rosbridge_server'),'launch','rosbridge_websocket_launch.xml')))])
    
    return LaunchDescription([
    	
    	robot_ns_launch_arg,
    	Node(
            package='robot_data_tool',
            executable='map_pose_provider',
            output='screen',
            namespace='',
            remappings = [('/tf','tf'),('/tf_static','tf_static')],
        ),
        
        Node(
            package='robot_nav_tool',
            executable='nav_gui_bridge',
            namespace = '',
            output='screen',
        ),
        
        Node(
        	package='robot_data_tool',
                    executable='robot_detail',
                    namespace = "",
                    ),

        Node(
        	package='rosbridge_server',
            executable='rosbridge_websocket',
            namespace = "",
            ),
      
        #launch_include_with_namespaces_webbridge,
 
       
    ])