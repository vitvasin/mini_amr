#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the maps directory
MAPS_DIR="$SCRIPT_DIR/../amrROS2_ws/maps"

# Function to get the next available map number
get_next_map_number() {
    # List all files matching the pattern map_*.pgm, extract numbers and find max
    last_num=$(ls "$MAPS_DIR"/map_[0-9]*.pgm 2>/dev/null | sed 's/.*map_\([0-9]\+\).pgm/\1/' | sort -n | tail -n 1)
    
    # If no existing maps found, start with 1, otherwise increment the last number
    if [ -z "$last_num" ]; then
        echo "1"
    else
        echo "$((last_num + 1))"
    fi
}

# Get the next map number
map_num=$(get_next_map_number)

# Create the map name with sequence number
map_name="map_$(printf "%03d" $map_num)"
map_path="$MAPS_DIR/$map_name"

echo "Saving map as: $map_path"
ros2 run nav2_map_server map_saver_cli -f "$map_path"

# If map was successfully saved, create a symlink to the latest map
if [ $? -eq 0 ]; then
    echo "Map saved successfully!"
    
    # Create/Update symlink to latest map
    latest_link="$MAPS_DIR/latest_map"
    ln -sf "$map_name.pgm" "$latest_link.pgm"
    ln -sf "$map_name.yaml" "$latest_link.yaml"
    
    echo "Latest map symlinks updated:"
    echo " - $latest_link.pgm"
    echo " - $latest_link.yaml"
    
    # Optional: Show the list of all maps
    echo -e "\nAvailable maps:"
    ls -1 "$MAPS_DIR"/map_*.pgm | sed 's|.*/||' | sort
else
    echo "Error saving map!"
fi