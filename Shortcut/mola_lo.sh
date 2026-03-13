export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch mola_lidar_odometry ros2-lidar-odometry.launch.py \
  start_active:=True \
  start_mapping_enabled:=False \
  lidar_topic_name:=/velodyne_points \
  use_mola_gui:=False \
  use_rviz:=False