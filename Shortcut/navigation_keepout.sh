ros2 launch navigation navigation.launch_keepout.py \
map:="/home/smr/workspaces/mini_amr/amrROS2_ws/maps/NECTEC_4th_Floor_SLAM4" \
rviz:=true \
rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz" \
use_keepout_zones:=true \
keepout_mask_yaml:="/home/smr/workspaces/mini_amr/amrROS2_ws/maps/latest_map_keepout.yaml"