import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable
from launch.conditions import IfCondition
from launch_ros.actions import Node, PushRosNamespace, SetRemap, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    robot_description_dir = get_package_share_directory("description")
    robot_bringup_dir = get_package_share_directory("bringup")

    vlp16_params_path = os.path.join(
        get_package_share_directory('velodyne_pointcloud'), 'params', 'VLP16db.yaml')

    params_file = LaunchConfiguration("params_file")
    use_rviz = LaunchConfiguration("bringup_rviz")
    use_sim_time = LaunchConfiguration("sim")

    declare_model_cmd = DeclareLaunchArgument(
        name="model", 
        default_value=os.path.join(robot_description_dir, "urdf/robot", "robot2.urdf.xacro"),
        description="Absolute path to robot urdf file")

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='bringup_rviz', 
        default_value='false',
        description='Run rviz'
    )
    
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='sim', 
        default_value='false',
        description='Enable use_sime_time to true'
    )
    
    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(robot_bringup_dir, "config", "3Dbringup.yaml"),
        description='Full path to the parameters file')

    robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]),
                                       value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(robot_description_dir, "rviz", "bringup.rviz")],
        condition=IfCondition(use_rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # แก้ไขการย่อหน้าบริเวณนี้ให้ถูกต้อง
    velodyne_container = ComposableNodeContainer(
        name='velodyne_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            ComposableNode(
                package='velodyne_driver',
                plugin='velodyne_driver::VelodyneDriver',
                name='velodyne_driver_node',
                parameters=[{
                    'device_ip': '192.168.1.201',
                    'model': 'VLP16',
                    'port': 2368,
                    'frame_id': 'velodyne',
                    'rpm': 1200.0,
                }],
            ),
            ComposableNode(
                package='velodyne_pointcloud',
                plugin='velodyne_pointcloud::Transform',
                name='velodyne_transform_node',
                parameters=[{
                    'model': 'VLP16',
                    'calibration': vlp16_params_path,
                    'fixed_frame': 'velodyne',
                    'target_frame': 'velodyne',
                    'max_range': 130.0,
                    'min_range': 0.4,
                }],
            ),
            ComposableNode(
                package='velodyne_laserscan',
                plugin='velodyne_laserscan::VelodyneLaserScan',
                name='velodyne_laserscan_node',
                parameters=[{
                    'ring': 8,
                    'resolution': 0.007,
                }],
                remappings=[
                    ('scan', '/velodyne_scan') 
                ],
            ),
        ],
        output='screen',
    )

    velodyne_static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='velodyne_base_link_static_tf',
        arguments=['0.13', '0', '0.76', '0', '0', '0', 'base_link', 'velodyne']
    )

    scan = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("sllidar_ros2"),
            "launch",
            "sllidar_s2_launch.py"),
        launch_arguments={
            'serial_port': '/dev/rplidar',
        }.items(),
    ) 

    camera = Node(
        package='usb_cam', 
        executable='usb_cam_node_exe',
        output='screen',
        name="usb_camera",
        parameters=[params_file]
    )

    laser_filter = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        parameters=[params_file],
    )

    robot_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[params_file],
        remappings=[("odometry/filtered", "odom")]
    ) 

    hardware_node = Node(
        package="robot_hardware_interface",
        executable="robot_hardware",
        name="robot_hardware",
        output="screen",
        parameters=[{'serial_port': "/dev/teensy"}],
    )

    launch_elements = GroupAction(
        actions=[
            SetRemap('/tf','tf'),
            SetRemap('/tf_static','tf_static'),
            robot_state_publisher_node,
            joint_state_publisher_node,   
            scan,
            velodyne_container,
            velodyne_static_tf,
            laser_filter,
            rviz_node, 
            robot_localization,
            hardware_node
        ]
    )

    return LaunchDescription([
        declare_params_file_cmd,
        declare_model_cmd,
        declare_use_sim_time_cmd,
        declare_use_rviz_cmd,
        launch_elements
    ]) 