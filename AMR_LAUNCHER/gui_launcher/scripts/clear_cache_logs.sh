#!/bin/bash
echo "Clearing system cache and ROS logs older than 7 days..."

# Clear ROS logs older than 7 days
find /home/smr/workspaces/mini_amr/amrROS2_ws/ROS_LOG -mindepth 1 -mtime +7 -delete 2>/dev/null
find /home/smr/workspaces/mini_amr/amrROS2_ws/ROS_LOG -mindepth 1 -type d -empty -delete 2>/dev/null

# Clean ~/.ros/log older than 7 days
find /home/smr/.ros/log -mindepth 1 -mtime +7 -delete 2>/dev/null
find /home/smr/.ros/log -mindepth 1 -type d -empty -delete 2>/dev/null

# Clear user cache entirely or selectively
rm -rf ~/.cache/* 2>/dev/null

echo "Cache and logs cleared."
