#!/bin/bash
export NAMESPACE=
export ROS_DOMAIN_ID=41
export CYCLONEDDS_URI=$HOME/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST

# Source ROS 2 Jazzy and Workspace
source /opt/ros/jazzy/setup.bash
source /home/smr/workspaces/mini_amr/install/setup.bash

# Run Teleop App
SCRIPT_DIR=$(dirname "$0")
PYTHON_EXEC=${LAUNCHER_PYTHON:-python3}
"$PYTHON_EXEC" "$SCRIPT_DIR/teleop_app.py" || { echo "Teleop crashed with exit code $?"; read -p "Press Enter to exit..."; exit 1; }
