
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "sensor_msgs/msg/range.hpp"
#include "std_msgs/msg/int16.hpp"
#include "std_msgs/msg/bool.hpp"
#include "std_msgs/msg/string.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "action_msgs/msg/goal_status_array.hpp"
#include <sensor_msgs/msg/battery_state.hpp>

#include <chrono>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <math.h>
// #include <Eigen/Dense>
#include <eigen3/Eigen/Dense>

#include "hardware_interface/robot_hardware_interface.h"

using std::placeholders::_1;
using namespace std::literals::chrono_literals;
using namespace std;

class HardwareInterfaceNode : public rclcpp::Node
{
public:
  HardwareInterfaceNode() : Node("hardware_interface")
  {
    declare_parameter("serial_port", "/dev/teensy");
    serial_port_ = get_parameter("serial_port").as_string();
    hardware_interface = std::make_shared<HardwareInterface>(serial_port_);

    cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
        "cmd_vel", 1, std::bind(&HardwareInterfaceNode::twistCallback, this, _1));

    charge_state_sub_ = create_subscription<std_msgs::msg::Int16>(
        "set_charge_state", 1, std::bind(&HardwareInterfaceNode::ChargeStateCallback, this, _1));

    mtr_drive_state_sub_ = create_subscription<std_msgs::msg::Bool>(
        "set_mtr_state", 1, std::bind(&HardwareInterfaceNode::MotorDriveStateCallback, this, _1));


    imu_pub_    = create_publisher<sensor_msgs::msg::Imu>("imu/data_raw", 10);
    odom_pub_   = create_publisher<nav_msgs::msg::Odometry>("odom_raw", 10);
    batt_pub_   = create_publisher<sensor_msgs::msg::BatteryState>("battery", 10);
    charge_state_pub_ = create_publisher<std_msgs::msg::Int16>("ir_charge_state", 10);
      
    range_left_pub_   = create_publisher<sensor_msgs::msg::Range>("range/left", 10);
    range_center_pub_ = create_publisher<sensor_msgs::msg::Range>("range/center", 10);
    range_right_pub_  = create_publisher<sensor_msgs::msg::Range>("range/right", 10);

    fault_state_pub_  = create_publisher<std_msgs::msg::String>("drive_fault_state", 10);
    


    //timer_update_data_ = create_wall_timer(10ms , std::bind(&HardwareInterfaceNode::timerUpdateCallback, this));
    timer_update_data_ = create_wall_timer(15ms , std::bind(&HardwareInterfaceNode::timerUpdateCallback, this));
    //timer_less_update_data_ = create_wall_timer(500ms , std::bind(&HardwareInterfaceNode::timerLessUpdateCallback, this));

    msg_odom_.header.frame_id = "odom_frame";
    msg_odom_.child_frame_id  = "base_footprint";
    msg_odom_.twist.covariance[0] = 0.0001;
    msg_odom_.twist.covariance[7] = 0.0001;
    msg_odom_.twist.covariance[35] = 0.0001;

    msg_imu_.header.frame_id = "imu_frame";
    msg_imu_.angular_velocity_covariance[0] = 0.1199;
    msg_imu_.angular_velocity_covariance[4] = 0.5753;
    msg_imu_.angular_velocity_covariance[8] = 0.0267;
    
    msg_imu_.linear_acceleration_covariance[0] = 0.0088;
    msg_imu_.linear_acceleration_covariance[4] = 0.0550;
    msg_imu_.linear_acceleration_covariance[8] = 0.0267;

    ut_fov_       = 15.0;
    ut_min_range_ = 0.03;
    ut_max_range_ = 0.20;//0.30;//3.50;

    msg_range_left_.header.frame_id   = "left_ranger_link";
    msg_range_center_.header.frame_id = "center_ranger_link";
    msg_range_right_.header.frame_id  = "right_ranger_link";

    msg_range_left_.radiation_type   = 0;
    msg_range_center_.radiation_type = 0;
    msg_range_right_.radiation_type  = 0;

    msg_range_left_.field_of_view   = ut_fov_ * (3.14/180);
    msg_range_center_.field_of_view = ut_fov_ * (3.14/180);
    msg_range_right_.field_of_view  = ut_fov_ * (3.14/180);

    msg_range_left_.min_range   = ut_min_range_;
    msg_range_center_.min_range = ut_min_range_;
    msg_range_right_.min_range  = ut_min_range_;

    msg_range_left_.max_range   = ut_max_range_;
    msg_range_center_.max_range = ut_max_range_;
    msg_range_right_.max_range  = ut_max_range_;

  }

private:

  std::string serial_port_;
  std::shared_ptr<HardwareInterface> hardware_interface;
  
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr mtr_drive_state_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr batt_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr range_left_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr range_center_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr range_right_pub_;
  rclcpp::Publisher<std_msgs::msg::Int16>::SharedPtr charge_state_pub_;
  rclcpp::Subscription<std_msgs::msg::Int16>::SharedPtr charge_state_sub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr fault_state_pub_;

  rclcpp::TimerBase::SharedPtr timer_update_data_;
  rclcpp::TimerBase::SharedPtr timer_less_update_data_;
  nav_msgs::msg::Odometry msg_odom_;
  sensor_msgs::msg::Imu msg_imu_;
  sensor_msgs::msg::BatteryState msg_batt_;
  sensor_msgs::msg::Range msg_range_left_, msg_range_center_, msg_range_right_;
  std_msgs::msg::Int16 msg_charge_state_;

  float ut_fov_;
  float ut_min_range_;
  float ut_max_range_;

  double pos_x_;
  double pos_y_;
  double heading_;

  double yaw_;

  uint64_t prev_update_;
  uint64_t imu_prev_update_;

    // Fault state string mapping (pre-computed, avoid repeated lookups)
  static constexpr const char* FAULT_STRINGS[] = {
    "No Fault",                            // 0
    "Over Current Fault",                  // 1
    "Over Voltage Fault",                  // 2
    "Motor Drive Disconnection Fault",     // 3
    "Over Temperature Fault",              // 4
    "Device Hardware Error",               // 5
    "Device Software Error",               // 6
    "Additional Modules Error",            // 7
    "Monitoring Error",                    // 8
    "Drive fault with Unknown reason",     // 9
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
    "Drive connection lost"                // 99
  };

  void odom_euler_to_quat(float roll, float pitch, float yaw, float *q)
  {
    float cy = cos(yaw * 0.5);
    float sy = sin(yaw * 0.5);
    float cp = cos(pitch * 0.5); //1
    float sp = sin(pitch * 0.5); //0
    float cr = cos(roll * 0.5);  //1
    float sr = sin(roll * 0.5);  //0

    q[0] = cy * cp * cr + sy * sp * sr;
    q[1] = cy * cp * sr - sy * sp * cr; //x    cy * 1 * 0 - sy * 0 * 
    q[2] = sy * cp * sr + cy * sp * cr; //y
    q[3] = sy * cp * cr - cy * sp * sr; //z
  }

  void twistCallback(const geometry_msgs::msg::Twist & msg)
  {
    //std::cout << "Received linear.x:"<< msg.linear.x << std::endl;
    hardware_interface->SetMotion(msg.linear.x, 0.0, msg.angular.z);
  }

  void ChargeStateCallback(const std_msgs::msg::Int16 & msg)
  {
    //std::cout << "Received linear.x:"<< msg.linear.x << std::endl;
    hardware_interface->SetChargeState(static_cast<uint16_t>(msg.data));
  }

   void MotorDriveStateCallback(const std_msgs::msg::Bool & msg)
  {
    //std::cout << "Received linear.x:"<< msg.linear.x << std::endl;
    hardware_interface->SetMotorDriveState(msg.data);
  }

  void timerLessUpdateCallback() //500ms
  {
    std_msgs::msg::String msg_fault_;
    //check fault state
    uint8_t fault_state = hardware_interface->drive_fault_state_;
    
    // Direct array lookup instead of if-else chain
    if (fault_state < 10) {
      msg_fault_.data = FAULT_STRINGS[fault_state];
    } else if (fault_state == 99) {
      msg_fault_.data = FAULT_STRINGS[99];
    } else {
      msg_fault_.data = "Unknown Fault";
    }

    fault_state_pub_->publish(msg_fault_);
  }
  void timerUpdateCallback()
    {
    static int tCount = 0;
    constexpr double NANOSECONDS_TO_SECONDS = 1e-9;

    auto current_time = get_clock()->now();
    uint64_t current_nanos = current_time.nanoseconds();

    // ===================== Odometry Update =====================
    if (hardware_interface->update_odom_) {
      uint64_t dt = current_nanos - prev_update_;
      double dt_seconds = static_cast<double>(dt) * NANOSECONDS_TO_SECONDS;

      double delta_heading = hardware_interface->odom_velocity.z * dt_seconds;
      // double cos_h = std::cos(heading_);
      // double sin_h = std::sin(heading_);

      double vx = hardware_interface->odom_velocity.x;
      double vy = hardware_interface->odom_velocity.y;

      // double delta_x = (vx * cos_h - vy * sin_h) * dt_seconds;
      // double delta_y = (vx * sin_h + vy * cos_h) * dt_seconds;

      Eigen::Vector2d velocity(vx, vy);
      Eigen::Rotation2Dd rot(heading_);
      Eigen::Vector2d delta = rot * velocity * dt;
      pos_x_ += delta.x();
      pos_y_ += delta.y();

      // pos_x_ += delta_x;
      // pos_y_ += delta_y;

      heading_ += delta_heading;

      float q[4];
      odom_euler_to_quat(0.0f, 0.0f, static_cast<float>(heading_), q);

      msg_odom_.header.stamp = current_time;
      msg_odom_.pose.pose.position.x = pos_x_;
      msg_odom_.pose.pose.position.y = pos_y_;
      msg_odom_.pose.pose.position.z = 0.0;

      msg_odom_.pose.pose.orientation.x = q[1];
      msg_odom_.pose.pose.orientation.y = q[2];
      msg_odom_.pose.pose.orientation.z = q[3];
      msg_odom_.pose.pose.orientation.w = q[0];

      msg_odom_.twist.twist.linear.x = vx;
      msg_odom_.twist.twist.linear.y = vy;
      msg_odom_.twist.twist.angular.z = hardware_interface->odom_velocity.z;

      odom_pub_->publish(msg_odom_);

      prev_update_ = current_nanos;
      hardware_interface->update_odom_ = false;
      }

    // ===================== IMU Update =====================
    if (hardware_interface->update_imu_) {
      uint64_t dt = current_nanos - imu_prev_update_;
      double dt_seconds = static_cast<double>(dt) * NANOSECONDS_TO_SECONDS;

      double imu_delta_z = hardware_interface->angular_velocity.z * dt_seconds;
      yaw_ += imu_delta_z;

      float imu_q[4];
      odom_euler_to_quat(0.0f, 0.0f, static_cast<float>(yaw_), imu_q);

      msg_imu_.header.stamp = current_time;

      msg_imu_.orientation.x = imu_q[1];
      msg_imu_.orientation.y = imu_q[2];
      msg_imu_.orientation.z = imu_q[3];
      msg_imu_.orientation.w = imu_q[0];

      msg_imu_.angular_velocity.x = hardware_interface->angular_velocity.y;
      msg_imu_.angular_velocity.y = -hardware_interface->angular_velocity.x;
      msg_imu_.angular_velocity.z = hardware_interface->angular_velocity.z;

      msg_imu_.linear_acceleration.x = hardware_interface->linear_acceleration.y;
      msg_imu_.linear_acceleration.y = -hardware_interface->linear_acceleration.x;
      msg_imu_.linear_acceleration.z = hardware_interface->linear_acceleration.z;

      imu_pub_->publish(msg_imu_);
      imu_prev_update_ = current_nanos;
      hardware_interface->update_imu_ = false;
      }

    // ===================== Range Update =====================
      if (hardware_interface->update_range_) {
      constexpr float MAX_RANGE = 3.5f;

      msg_range_left_.header.stamp = current_time;
      msg_range_center_.header.stamp = current_time;
      msg_range_right_.header.stamp = current_time;

      msg_range_left_.range = std::min(hardware_interface->range_left, MAX_RANGE);
      msg_range_center_.range = std::min(hardware_interface->range_center, MAX_RANGE);
      msg_range_right_.range = std::min(hardware_interface->range_right, MAX_RANGE);

      range_left_pub_->publish(msg_range_left_);
      range_center_pub_->publish(msg_range_center_);
      range_right_pub_->publish(msg_range_right_);

      hardware_interface->update_range_ = false;
      }

    // ===================== Battery Update =====================
      if (hardware_interface->update_batt_) {
      msg_batt_.voltage = hardware_interface->voltage_;
      msg_batt_.current = hardware_interface->current_;
      msg_batt_.percentage = hardware_interface->percentage_;
      msg_batt_.power_supply_status = hardware_interface->status_;

      batt_pub_->publish(msg_batt_);

      // msg_charge_state_.data = static_cast<int16_t>(hardware_interface->ir_charge_state_);
      // charge_state_pub_->publish(msg_charge_state_);

      hardware_interface->update_batt_ = false;
      }

      if (hardware_interface->update_ir_) {

        msg_charge_state_.data = static_cast<int16_t>(hardware_interface->ir_charge_state_);
        charge_state_pub_->publish(msg_charge_state_);

        hardware_interface->update_ir_ = false;
      }

    // ===================== Periodic Update (Every 10 ticks) =====================
      if (++tCount > 10) {
      hardware_interface->UpdateStatus(1);
      tCount = 0;
      }
    }
  // void timerUpdateCallback()
  // {
  //   static int tCount=0;
  //   auto current_time = get_clock()->now();
  //   // if (hardware_interface->update_odom_)
  //   // {
  //     msg_odom_.header.stamp = current_time;

  //     uint64_t dt = current_time.nanoseconds() - prev_update_;
  //     //std::cout << "odom publish time : "<< dt << std::endl;

  //     double dt_seconds = static_cast<double>(dt) / 1000000000.0f;

  //     double delta_heading = static_cast<double>(hardware_interface->odom_velocity.z) * dt_seconds; // radians
  //     double cos_h = cos(heading_);
  //     double sin_h = sin(heading_);
  //     double delta_x = (static_cast<double>(hardware_interface->odom_velocity.x) * cos_h - static_cast<double>(hardware_interface->odom_velocity.y) * sin_h) * dt_seconds; // m
  //     double delta_y = (static_cast<double>(hardware_interface->odom_velocity.x) * sin_h + static_cast<double>(hardware_interface->odom_velocity.y) * cos_h) * dt_seconds; // m

  //     pos_x_ += delta_x;
  //     pos_y_ += delta_y;
  //     heading_ += delta_heading;

  //     float q[4];
  //     odom_euler_to_quat(0.0, 0.0, static_cast<float>(heading_), q);

  //     msg_odom_.pose.pose.position.x = pos_x_;
  //     msg_odom_.pose.pose.position.y = pos_y_;
  //     msg_odom_.pose.pose.position.z = 0.0;

  //     msg_odom_.pose.pose.orientation.x = (double)q[1];
  //     msg_odom_.pose.pose.orientation.y = (double)q[2];
  //     msg_odom_.pose.pose.orientation.z = (double)q[3];
  //     msg_odom_.pose.pose.orientation.w = (double)q[0];

  //     msg_odom_.twist.twist.linear.x = hardware_interface->odom_velocity.x;
  //     msg_odom_.twist.twist.linear.y = hardware_interface->odom_velocity.y;
  //     msg_odom_.twist.twist.angular.z = hardware_interface->odom_velocity.z;

  //     //hardware_interface->update_odom_ = false;
  //     odom_pub_->publish(msg_odom_);
    
  //     prev_update_ = current_time.nanoseconds();
      

  //   // }
  //   // else if (hardware_interface->update_imu_)
  //   //{
  //     msg_imu_.header.stamp = current_time;

  //     dt = current_time.nanoseconds() - imu_prev_update_;
  //     dt_seconds = static_cast<double>(dt) / 1000000000.0;

  //     double imu_delta_z = static_cast<double>(hardware_interface->angular_velocity.z) * dt_seconds;
  //     yaw_ += imu_delta_z;

  //     float imu_q[4];
  //     odom_euler_to_quat(0.0, 0.0, static_cast<float>(yaw_), imu_q);

  //     msg_imu_.orientation.x = (double)imu_q[1];
  //     msg_imu_.orientation.y = (double)imu_q[2];
  //     msg_imu_.orientation.z = (double)imu_q[3];
  //     msg_imu_.orientation.w = (double)imu_q[0];

  //     msg_imu_.angular_velocity.x = hardware_interface->angular_velocity.y;
  //     msg_imu_.angular_velocity.y = hardware_interface->angular_velocity.x * (-1);
  //     msg_imu_.angular_velocity.z = hardware_interface->angular_velocity.z;

  //     msg_imu_.linear_acceleration.x = hardware_interface->linear_acceleration.y;
  //     msg_imu_.linear_acceleration.y = hardware_interface->linear_acceleration.x * (-1);
  //     msg_imu_.linear_acceleration.z = hardware_interface->linear_acceleration.z;

  //     //hardware_interface->update_imu_ = false;
  //     imu_pub_->publish(msg_imu_);

  //     imu_prev_update_ = current_time.nanoseconds();
  //   // }
  //   // else if (hardware_interface->update_range_)
  //   // //if (hardware_interface->update_range_)
  //   // {
  //     msg_range_left_.header.stamp   = current_time;
  //     msg_range_center_.header.stamp = current_time;
  //     msg_range_right_.header.stamp  = current_time;

  //     // msg_range_left_.range = 0.3;//hardware_interface->range_left;
  //     // msg_range_center_.range = 0.3;//hardware_interface->range_center;
  //     // msg_range_right_.range = 0.3;//hardware_interface->range_right;

  //     msg_range_left_.range = hardware_interface->range_left; //Convert to cm
  //     msg_range_center_.range = hardware_interface->range_center; //Convert to cm
  //     msg_range_right_.range = hardware_interface->range_right; //Convert to cm

  //     // Limit ultrasonic readings to not exceed 3.5 m
  //     //const float ULTRASONIC_MAX_CM = 3.5f;
  //     //msg_range_left_.range   = std::min(msg_range_left_.range,   ULTRASONIC_MAX_CM);
  //     //msg_range_center_.range = std::min(msg_range_center_.range, ULTRASONIC_MAX_CM);
  //     //msg_range_right_.range  = std::min(msg_range_right_.range,  ULTRASONIC_MAX_CM); 
      
  //     //std::cout << "range_left:"<< msg_range_left_.range << "    range_center:"<< msg_range_center_.range << "    range_right:"<< msg_range_right_.range << std::endl;

  //     //hardware_interface->update_range_ = false;

  //     range_left_pub_->publish(msg_range_left_);
  //     range_center_pub_->publish(msg_range_center_);
  //     range_right_pub_ ->publish(msg_range_right_);
  //   // }
  //   // else if (hardware_interface->update_batt_)
  //   // //if (hardware_interface->update_batt_)
  //   // {
  //     msg_batt_.voltage = hardware_interface->voltage_;
  //     msg_batt_.current = hardware_interface->current_;
  //     msg_batt_.percentage = hardware_interface->percentage_;
  //     msg_batt_.power_supply_status = hardware_interface->status_;

  //     // //print batt debug
  //     // std::cout << "Battery -";
  //     // std::cout << " " << hardware_interface->voltage_;
  //     // std::cout << " " << hardware_interface->current_;
  //     // std::cout << " " << hardware_interface->percentage_ << std::endl;
      
  //     hardware_interface->update_batt_ = false;
  //     batt_pub_->publish(msg_batt_);
      

  //     msg_charge_state_.data = static_cast<int16_t>(hardware_interface->ir_charge_state_);
  //     charge_state_pub_->publish(msg_charge_state_);

  //     if(tCount > 10){
  //       hardware_interface->UpdateStatus(1);
  //       // batt_pub_->publish(msg_batt_);
  //       tCount=0;
  //     }
  //     else
  //       tCount++;
  // }
};


int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<HardwareInterfaceNode>());
  rclcpp::shutdown();
  return 0;
}
