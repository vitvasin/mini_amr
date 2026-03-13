import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # --- 1. CONFIG: ตรวจสอบ Path ให้ถูกต้อง ---
    # map_yaml_file = '/home/smr/molamaps/mapout_processed.yaml'
    nav2_params_file = '/home/smr/workspaces/mini_amr/amrROS2_ws/src/navigation/config/molaconfignoF.yaml'
    # -----------------------------------------------

    # รายชื่อ Node ของระบบ Navigation ที่เราจะรัน
    # [จุดแก้ที่ 1] เพิ่ม 'waypoint_follower' เข้าไปในลิสต์
    nav_lifecycle_nodes = ['controller_server',
                           'planner_server',
                           'behavior_server',
                           'bt_navigator',
                           'velocity_smoother',
                           'collision_monitor',
                           'waypoint_follower'] 

    return LaunchDescription([
        # ---------------------------------------------------------
        # ส่วนที่ 1: Map Server
        # ---------------------------------------------------------
        # Node(
        #     package='nav2_map_server',
        #     executable='map_server',
        #     name='map_server',
        #     output='screen',
        #     parameters=[{'use_sim_time': False},
        #                 {'yaml_filename': map_yaml_file}]
        # ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{'use_sim_time': False},
                        {'autostart': True},
                        {'node_names': ['map_server']}]
        ),

        # ---------------------------------------------------------
        # ส่วนที่ 2: Navigation Stack
        # ---------------------------------------------------------
        
        # 1. Controller Server
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params_file],
            prefix=['taskset -c 6 nice -n -10'], 
            remappings=[('/cmd_vel', '/cmd_vel_nav')]
        ),

        # 2. Velocity Smoother
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_params_file],
    
            remappings=[('/cmd_vel', '/cmd_vel_nav')] 
        ),

 
        Node(
            package='nav2_collision_monitor',
            executable='collision_monitor',
            name='collision_monitor',
            output='screen',
            parameters=[nav2_params_file]
        ),

        # 4. Planner Server
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params_file]
        ),

        # 5. Behavior Server
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params_file]
        ),


        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params_file]
        ),
        
    
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_params_file]
        ),

    
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': False},
                        {'autostart': True},
                        {'node_names': nav_lifecycle_nodes}]
        ),
    ])