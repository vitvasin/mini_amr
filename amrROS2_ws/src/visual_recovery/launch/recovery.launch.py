from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name='cmd_vel_topic',
            default_value='/cmd_vel',
            description='Topic to publish velocity commands (bypassing nav2 if necessary)'
        ),
        DeclareLaunchArgument(
            name='camera_topic',
            default_value='/image_raw',
            description='Camera topic to capture a single frame from'
        ),
        DeclareLaunchArgument(
            name='request_image_topic',
            default_value='/visual_localization/image_request',
            description='Topic to forward the captured image to the AI pipeline'
        ),
        DeclareLaunchArgument(
            name='response_pose_topic',
            default_value='/visual_localization/pose_response',
            description='Topic to receive the 6DoF pose result from the AI pipeline'
        ),
        DeclareLaunchArgument(
            name='initialpose_topic',
            default_value='/initialpose',
            description='Topic to inject the estimated pose into AMCL/Slam-toolbox'
        ),
        DeclareLaunchArgument(
            name='timeout_seconds',
            default_value='15.0',
            description='Max seconds to wait for the AI pipeline to return a pose'
        ),

        Node(
            package='visual_recovery',
            executable='recovery_node',
            name='visual_recovery_node',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'cmd_vel_topic':        LaunchConfiguration('cmd_vel_topic'),
                'camera_topic':         LaunchConfiguration('camera_topic'),
                'request_image_topic':  LaunchConfiguration('request_image_topic'),
                'response_pose_topic':  LaunchConfiguration('response_pose_topic'),
                'initialpose_topic':    LaunchConfiguration('initialpose_topic'),
                'timeout_seconds':      LaunchConfiguration('timeout_seconds'),
            }]
        ),
    ])
