from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    # 1. Define the first launch file (Dummy A)
    # Using 'dummy_package_A' and 'dummy_launch_A.py' as placeholders
    launch_a = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('dummy_package_A'),
                'launch',
                'dummy_launch_A.py'
            ])
        ])
    )

    # 2. Define the second launch file (Dummy B)
    # This one we want to launch "in sequence" - e.g., after 5 seconds
    launch_b = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('dummy_package_B'),
                'launch',
                'dummy_launch_B.py'
            ])
        ])
    )

    # Strategy 1: Time-based sequence
    # Launch B 5.0 seconds after Launch A starts
    delayed_launch_b = TimerAction(
        period=5.0,
        actions=[
            LogInfo(msg="Sequencing: Launching B after 5s delay..."),
            launch_b
        ]
    )

    # Strategy 2: Event-based sequence (Launch C after A exits)
    # Useful if A is an init script.
    # launch_c = ...
    # sequence_c_after_a = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=launch_a,
    #         on_exit=[
    #             LogInfo(msg="Sequencing: A exited, launching C..."),
    #             launch_c
    #         ]
    #     )
    # )

    return LaunchDescription([
        LogInfo(msg="Starting sequential launch..."),
        launch_a,
        delayed_launch_b
    ])
