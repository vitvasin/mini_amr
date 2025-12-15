from launch_ros.actions import Node
from launch import LaunchDescription

from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # Get the package's share directory
    package_share_directory = get_package_share_directory('wis_pkg')
    
    # Path to the config.yaml file in the config directory
    # config_file_path = os.path.join(
    #     os.path.dirname(__file__),
    #     'wis_config.yaml'
    # )
    # config_file_path = os.path.join(package_share_directory, 'config', 'wis_config.yaml')
    
    # Ensure the config file exists
    # if not os.path.exists(config_file_path):
    #     raise FileNotFoundError(f"Config file not found: {config_file_path}")

    # Define the nodes
    node1 = Node(
        package = "wis_pkg",
        executable = "map_name",
        # parameters = [config_file_path]
    )

    node2 = Node(
        package = "wis_pkg",
        executable = "map_info"
        )
		
    node3 = Node(
        package = "wis_pkg",
        executable = "map_load"
    )
		
    node4 = Node(
        package = "wis_pkg",
        executable = "map_save"
    )

    node5 = Node(
        package = "wis_pkg",
        executable = "map_scan"
    )

    node6 = Node(
        package = "wis_pkg",
        executable = "map_nav"
    )

    node7 = Node(
        package = "wis_pkg",
        executable = "point_save"
    )

    node8 = Node(
        package = "wis_pkg",
        executable = "map_shutdown"
    )

    node9 = Node(
        package = "wis_pkg",
        executable = "battery_charge"
    )

    # Create a LaunchDescription and add nodes
    ld = LaunchDescription()
    ld.add_action(node1)
    ld.add_action(node2)
    ld.add_action(node3)
    ld.add_action(node4)
    ld.add_action(node5)
    ld.add_action(node6)
    ld.add_action(node7)
    ld.add_action(node8)
    ld.add_action(node9)

    return ld
    
    
# wis_pkg/
# ├── config/
# │   └── wis_config.yaml
# ├── launch/
# │   └── launch.py

# import os
# from glob import glob
# (os.path.join('share', package_name), glob("launch/*.launch.py")),
# ros2 launch wis_pkg wis.launch.py
