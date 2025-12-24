#!/bin/bash

# Exports from .bashrc content
export ROS_WS="/home/smr/workspaces/mini_amr/amrROS2_ws"
export QT_QPA_PLATFORM=xcb
export AMR_UI="/home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR"
export ROS_DOMAIN_ID=31 
export CYCLONEDDS_URI=$HOME/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
export NAMESPACE=

# Source ROS 2 system installation
source /opt/ros/jazzy/setup.bash

# Source the workspaces
source $ROS_WS/install/setup.bash
source $ROS_WS/install/local_setup.bash
# Save SLAM Toolbox map (.posegraph + .data)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MAPS_DIR="$SCRIPT_DIR/../amrROS2_ws/maps"

# Function to get next available map number
get_next_map_number() {
    last_num=$(ls "$MAPS_DIR"/mapSLAM_[0-9]*.posegraph 2>/dev/null | \
        sed 's/.*mapSLAM_\([0-9]\+\)\.posegraph/\1/' | sort -n | tail -n 1)
    if [ -z "$last_num" ]; then
        echo "1"
    else
        echo "$((last_num + 1))"
    fi
}

map_num=$(get_next_map_number)
map_name="mapSLAM_$(printf "%03d" $map_num)"
map_path="$MAPS_DIR/$map_name"

echo "Saving SLAM Toolbox map as: $map_path.posegraph and .data"

# Call the SLAM Toolbox save_map service
# ros2 service call /slam_toolbox/save_map slam_toolbox_msgs/srv/SaveMap "{name: \"$map_path\"}" 
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: \"$map_path\"}"
if [ $? -eq 0 ]; then
    echo "Posegraph and data saved successfully!"
    latest_link="$MAPS_DIR/latest_map"
    ln -sf "$map_name.posegraph" "$latest_link.posegraph"
    ln -sf "$map_name.data" "$latest_link.data"
    echo "Updated symlinks:"
    echo " - $latest_link.posegraph"
    echo " - $latest_link.data"

    echo -e "\nAvailable saved maps:"
    ls -1 "$MAPS_DIR"/mapSLAM_*.posegraph | sed 's|.*/||' | sort
else
    echo "Error saving SLAM Toolbox map!"
fi
