#!/bin/bash
# ------------------------------------------------------------
# Script: run_delivery
# Description: Run delivery_robot_main_controller launch file
# Author: SMR Robotics
# ------------------------------------------------------------

# ตั้งค่าพาธ workspace (ปรับตามจริง)
WORKSPACE=~/workspaces/mini_amr/amrROS2_ws/

# ตรวจสอบว่า workspace มีอยู่จริงไหม
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Workspace not found at: $WORKSPACE"
    exit 1
fi

# เข้า workspace
cd $WORKSPACE || exit 1

# ตรวจสอบว่า ROS2 ถูก source หรือยัง
if [ -z "$ROS_DISTRO" ]; then
    echo "⚙️  Sourcing ROS2 environment..."
    source /opt/ros/jazzy/setup.bash
fi

# ตรวจสอบว่า workspace build แล้วหรือยัง
if [ -f "$WORKSPACE/install/setup.bash" ]; then
    source $WORKSPACE/install/setup.bash
else
    echo "⚠️  install/setup.bash not found. Please build your workspace first."
    exit 1
fi

# รัน launch file
echo "Launching delivery_robot_main_controller..."
ros2 launch delivery_robot_main_controller delivery.launch.py