#!/bin/bash

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Source Workspace
source /home/smr/workspaces/mini_amr/amrROS2_ws/install/setup.bash

# Export Environment Variables
export ROS_DOMAIN_ID=31
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/home/smr/cyclonedds.xml
export QT_QPA_PLATFORM=xcb

# Allow the script to talk to the local UI (for Zenity popups)
export DISPLAY=:0

# Navigate to the correct directory and run the python script
cd /home/smr/workspaces/mini_amr/amrROS2_ws/ros2_bag_recorder
python3 rolling_recorder.py
