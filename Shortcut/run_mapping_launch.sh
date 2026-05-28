#!/bin/bash

# Exports from .bashrc content
export ROS_WS="/home/smr/workspaces/mini_amr/amrROS2_ws"
export QT_QPA_PLATFORM=xcb
export AMR_UI="/home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR"
export ROS_DOMAIN_ID=41
export CYCLONEDDS_URI=$HOME/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export NAMESPACE=

# Source ROS 2 system installation
source /opt/ros/jazzy/setup.bash

# Source the workspaces
source $ROS_WS/install/setup.bash
source $ROS_WS/install/local_setup.bash
if [ -f ~/workspaces/mini_amr/traffic_editor/install/setup.bash ]; then
    source ~/workspaces/mini_amr/traffic_editor/install/setup.bash
fi

# Run the launch file
ros2 launch nectec_amr_launch mapping_sequential_launch.py
