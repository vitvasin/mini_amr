cmake_minimum_required(VERSION 3.8)
project(amr_nav2_slam_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()