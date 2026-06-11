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

# Ensure MongoDB and Backend Server are running
/home/smr/workspaces/mini_amr/Shortcut/ensure_services.sh

# Generate base date string (YYYY-MM-DD)
CURRENT_DATE=$(date +"%Y-%m-%d")

# Create logs directory for the current date if it doesn't exist
LOG_DIR="$ROS_WS/ROS_LOG/$CURRENT_DATE"
mkdir -p "$LOG_DIR"

# Find the next counter for today
COUNTER=1
while [ -f "$LOG_DIR/run_${COUNTER}_"*.log ]; do
    ((COUNTER++))
done

# Generate the full timestamped filename
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/run_${COUNTER}_${TIMESTAMP}.log"

# Run the launch file and record output
ros2 launch nectec_amr_launch slam_localization_sequential_launch.py 2>&1 | tee "$LOG_FILE"
