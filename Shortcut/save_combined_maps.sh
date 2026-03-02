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

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the maps directory
MAPS_DIR="$SCRIPT_DIR/../amrROS2_ws/maps"

# Temp files for status codes
NAV2_STATUS_FILE=$(mktemp)
SLAM_STATUS_FILE=$(mktemp)

# Start the process with a progress bar
(
    echo "10"
    echo "# Sourcing ROS 2 environment..."
    sleep 1

    # ==========================================
    # PART 1: Save Nav2 Map (map_XXX)
    # ==========================================
    
    echo "30"
    echo "# Preparing to save Nav2 map..."

    # Function to get the next available map number for Nav2 maps
    get_next_nav2_map_number() {
        # List all files matching the pattern map_*.pgm, extract numbers and find max
        last_num=$(ls "$MAPS_DIR"/map_[0-9]*.pgm 2>/dev/null | sed 's/.*map_\([0-9]\+\).pgm/\1/' | sort -n | tail -n 1)
        
        # If no existing maps found, start with 1, otherwise increment the last number
        if [ -z "$last_num" ]; then
            echo "1"
        else
            echo "$((last_num + 1))"
        fi
    }

    map_num=$(get_next_nav2_map_number)
    map_name="map_$(printf "%03d" $map_num)"
    map_path="$MAPS_DIR/$map_name"

    echo "40"
    echo "# Saving Nav2 map to $map_name..."
    ros2 run nav2_map_server map_saver_cli -f "$map_path"
    echo $? > "$NAV2_STATUS_FILE"
    
    # Check status inside the subshell to update symlinks
    if [ $(cat "$NAV2_STATUS_FILE") -eq 0 ]; then
        # Create/Update symlink to latest map
        latest_link="$MAPS_DIR/latest_map"
        ln -sf "$map_name.pgm" "$latest_link.pgm"
        ln -sf "$map_name.yaml" "$latest_link.yaml"
    fi


    # ==========================================
    # PART 2: Save SLAM Toolbox Map (mapSLAM_XXX)
    # ==========================================

    echo "60"
    echo "# Preparing to save SLAM Toolbox map..."

    # Function to get next available map number for SLAM maps
    get_next_slam_map_number() {
        last_num=$(ls "$MAPS_DIR"/mapSLAM_[0-9]*.posegraph 2>/dev/null | \
            sed 's/.*mapSLAM_\([0-9]\+\)\.posegraph/\1/' | sort -n | tail -n 1)
        if [ -z "$last_num" ]; then
            echo "1"
        else
            echo "$((last_num + 1))"
        fi
    }

    slam_map_num=$(get_next_slam_map_number)
    slam_map_name="mapSLAM_$(printf "%03d" $slam_map_num)"
    slam_map_path="$MAPS_DIR/$slam_map_name"

    echo "70"
    echo "# Saving SLAM Toolbox map to $slam_map_name..."

    # Call the SLAM Toolbox save_map service
    ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: \"$slam_map_path\"}"
    echo $? > "$SLAM_STATUS_FILE"

    # Check status inside subshell for symlinks
    if [ $(cat "$SLAM_STATUS_FILE") -eq 0 ]; then
        latest_link="$MAPS_DIR/latest_map"
        ln -sf "$slam_map_name.posegraph" "$latest_link.posegraph"
        ln -sf "$slam_map_name.data" "$latest_link.data"
    fi

    echo "90"
    echo "# Finalizing..."
    sleep 1
    echo "100"

) | zenity --progress \
  --title="Map Saver" \
  --text="Starting map save process..." \
  --percentage=0 \
  --auto-close \
  --no-cancel \
  --width=400

# ==========================================
# PART 3: Summary and Popup
# ==========================================

NAV2_SAVE_STATUS=$(cat "$NAV2_STATUS_FILE")
SLAM_SAVE_STATUS=$(cat "$SLAM_STATUS_FILE")

# Cleanup temp files
rm -f "$NAV2_STATUS_FILE" "$SLAM_STATUS_FILE"

echo -e "\nAvailable maps:"
ls -1 "$MAPS_DIR"/map_*.pgm 2>/dev/null | sed 's|.*/||' | sort
ls -1 "$MAPS_DIR"/mapSLAM_*.posegraph 2>/dev/null | sed 's|.*/||' | sort

if [ "$NAV2_SAVE_STATUS" -eq 0 ] && [ "$SLAM_SAVE_STATUS" -eq 0 ]; then
    MSG="Save Complete: Both maps saved successfully."
    zenity --info --text="$MSG" --title="Map Saver" --timeout=5 2>/dev/null
elif [ "$NAV2_SAVE_STATUS" -eq 0 ]; then
    MSG="Partial Save: Nav2 map saved, but SLAM map failed."
    zenity --warning --text="$MSG" --title="Map Saver" 2>/dev/null
elif [ "$SLAM_SAVE_STATUS" -eq 0 ]; then
    MSG="Partial Save: SLAM map saved, but Nav2 map failed."
    zenity --warning --text="$MSG" --title="Map Saver" 2>/dev/null
else
    MSG="Error: Failed to save both maps."
    zenity --error --text="$MSG" --title="Map Saver" 2>/dev/null
fi
