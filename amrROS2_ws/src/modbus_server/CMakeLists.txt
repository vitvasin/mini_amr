cmake_minimum_required(VERSION 3.8)
project(modbus_server)

set(CMAKE_CXX_STANDARD 14)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic -Wunused-variable -fPIC)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rcpputils REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rmw_implementation REQUIRED)
find_package(Qt5SerialBus REQUIRED)
find_package(ros2qt REQUIRED)
find_package(hgcr_interfaces REQUIRED)
#find_package(stag_ros REQUIRED)

if(rclcpp_VERSION_MAJOR GREATER_EQUAL 2)
    message("Foxy or newer rclcpp detected")
    add_compile_definitions(POST_FOXY)
    ament_export_definitions(POST_FOXY)
endif(rclcpp_VERSION_MAJOR GREATER_EQUAL 2)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

include_directories(
    ${rclcpp_INCLUDE_DIRS}
    ${rclcpp_action_INCLUDE_DIRS}
    ${std_msgs_INCLUDE_DIRS}
    ${Qt5SerialBus_INCLUDE_DIRS}
    ${ros2qt_INCLUDE_DIRS}
    ${hgcr_interfaces_INCLUDE_DIRS}
    #${stag_ros_INCLUDE_DIRS}
    )

file(GLOB SOURCE_FILES
    "src/*.cpp"
    )

file(GLOB HEADER_FILES
    "include/modbus_server/*.h"
    )

add_executable(${PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})

ament_target_dependencies(${PROJECT_NAME}
    rclcpp
    rclcpp_action
    std_msgs
    rmw_implementation
    rcpputils
    ros2qt
    hgcr_interfaces
    # stag_ros 
    )

target_include_directories(${PROJECT_NAME}
    PUBLIC    
        include/modbus_server
    )
target_link_libraries(${PROJECT_NAME}
    Qt5::SerialBus 
    )

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
    TARGETS ${PROJECT_NAME} 
    RUNTIME DESTINATION lib/${PROJECT_NAME}
)

ament_package()
