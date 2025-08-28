#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Launch navigation with SLAM
ros2 launch navigation navigation_slam.launch.py \
    rviz:=true \
    rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
