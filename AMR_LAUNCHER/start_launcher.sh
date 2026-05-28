#!/bin/bash

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Source Workspace
source /home/smr/workspaces/mini_amr/amrROS2_ws/install/setup.bash
source /home/smr/workspaces/mini_amr/traffic_editor/install/setup.bash

# Export Environment Variables
export ROS_DOMAIN_ID=41
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=/home/smr/cyclonedds.xml
export QT_QPA_PLATFORM=xcb

# Activate Virtual Environment
source /home/smr/workspaces/mini_amr/AMR_LAUNCHER/.venv/bin/activate

# Launch Application
cd /home/smr/workspaces/mini_amr/AMR_LAUNCHER/gui_launcher
python3 launcher.py
