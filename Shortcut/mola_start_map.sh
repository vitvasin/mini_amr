export LIBGL_ALWAYS_SOFTWARE=1 
ros2 launch mola_lidar_odometry ros2-lidar-odometry.launch.py \
  lidar_topic_name:=/velodyne_points \
  generate_simplemap:=True \
use_mola_gui:=False \
use_rviz:=False
 