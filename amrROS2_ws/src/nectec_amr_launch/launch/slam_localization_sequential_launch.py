import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess, RegisterEventHandler, EmitEvent
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Define paths
    map_yaml = "/home/smr/workspaces/mini_amr/amrROS2_ws/maps/latest_map"
    keepout_mask_yaml = "/home/smr/workspaces/mini_amr/amrROS2_ws/maps/latest_map_keepout.yaml"
    amr_ui_path = "/home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR"
    
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
        period=5.0,
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
        period=10.0,
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
        navigation_launch,
        delayed_delivery_launch,
        delayed_ui_launch,
        shutdown_handler
    ])
