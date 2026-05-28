#!/bin/bash
export NAMESPACE=
export ROS_DOMAIN_ID=41
export CYCLONEDDS_URI=$HOME/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
# Source ROS 2 Jazzy and Workspace
source /opt/ros/jazzy/setup.bash
source /home/smr/workspaces/mini_amr/install/setup.bash

# Use exec to ensure the launch process replaces the shell (PID preservation)
exec ros2 launch bringup bringup.launch.py
