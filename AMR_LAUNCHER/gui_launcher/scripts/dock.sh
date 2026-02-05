#!/bin/bash

# Function to kill all background jobs on exit
cleanup() {
    echo "Terminating launch nodes..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT SIGINT SIGTERM

export NAMESPACE=
export ROS_DOMAIN_ID=31 
export CYCLONEDDS_URI=$HOME/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
# Source ROS 2 Jazzy and Workspace
source /opt/ros/jazzy/setup.bash
source /home/smr/workspaces/mini_amr/install/setup.bash

echo "Starting Bringup..."
ros2 launch bringup bringup.launch.py &
sleep 2 # Wait for bringup to stabilize

echo "Starting Auto Dock..."
ros2 launch action_autodock auto_dock_launch.py &
sleep 2


echo "Starting Battery Monitor..."
ros2 topic echo /battery &

echo "Sending Dock Goal..."
# Run the action goal. logic: script waits here for the action to complete.
ros2 action send_goal --feedback autodock custom_interface/action/Autodock "{is_dock: True}"

sleep 10

echo "Docking sequence finished."
# Script will exit now, triggering cleanup trap which kills the launch nodes and the battery echo.


