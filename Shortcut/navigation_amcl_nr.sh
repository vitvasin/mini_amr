#ros2 launch navigation navigation.launch.py map:="$ROS_WS/maps/smr_room" rviz:=true rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz"
#ros2 launch navigation navigation.launch.py use_slam_tb:=false use_mapping:=false rviz:=true rviz_config_file:="$ROS_WS/install/navigation/share/navigation/rviz/rviz_nav.rviz" map:="/home/emr/workspaces/mini_amr/maps/NECTEC_4th_Floor.yaml"
#ros2 launch navigation amcl_localization_launch.py map:=/home/emr/workspaces/mini_amr/maps/NECTEC_4th_Floor.yaml
./navigation_new.sh amcl_nr
