
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
        # Launch navigation with SLAM (formapping)
        ros2 launch navigation navigation_slam.launch.py \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
        ;;
    "amcl")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor.yaml" \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz" \
            use_keepout_zones:=true \
            keepout_mask_yaml:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor_keepout.yaml"
        ;;
    "amcl_nr")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor.yaml" \
            rviz:=false \
            use_keepout_zones:=true \
            keepout_mask_yaml:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor_keepout.yaml"
        ;;
    "amcl_nr_nk")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor.yaml" \
            rviz:=false \
            use_keepout_zones:=false \
            keepout_mask_yaml:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor_keepout.yaml"
        ;;
    "amcl_smr")
        # Launch navigation with AMCL #NECTEC_4th_Floor.yaml
        ros2 launch navigation navigation_amcl.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/smr_room.yaml" \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
        ;;
    "slam_localization")
        # Launch navigation with AMCL #SMR_room.yaml
        ros2 launch navigation navigation.launch.py \
            map:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor_SLAM" \
            rviz:=true \
            rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav_slam.rviz" \
            use_keepout_zones:=true \
            keepout_mask_yaml:="$SCRIPT_DIR/../amrROS2_ws/maps/NECTEC_4th_Floor_SLAM_keepout.yaml"
        ;;

    *)
        show_usage
        ;;
esac
