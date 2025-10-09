#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to display usage
show_usage() {
    echo "Usage: $0 [slam|amcl]"
    echo "  slam    Launch navigation with SLAM for mapping"
    echo "  amcl    Launch navigation with AMCL for localization using existing map"
    exit 1
}

# Check if argument is provided
if [ $# -ne 1 ]; then
    show_usage
fi

# Launch based on argument
case "$1" in
    "slam")
        # Launch navigation with SLAM
        ros2 launch navigation navigation_slam.launch.py \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
        ;;
    "amcl")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor.yaml" \
           #map:="$SCRIPT_DIR/../amrROS2_ws/maps/map_001.yaml" \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
        ;;
    "amcl_smr")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/smr_room.yaml" \
           #map:="$SCRIPT_DIR/../amrROS2_ws/maps/map_001.yaml" \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
        ;;

    *)
        show_usage
        ;;
esac
