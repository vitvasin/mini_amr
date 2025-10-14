/*
 * =====================================================================================
 *
 *       Filename:  modbus_tcpserver.h
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  06/22/2023 01:11:17 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  YOUR NAME (), 
 *   Organization:  
 *
 * =====================================================================================
 */

#ifndef MODBUS_TCPSERVER_H
#define MODBUS_TCPSERVER_H
#pragma once

#include <QObject>
#include <QModbusTcpServer>
#include <QVector>
#include <QString>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include "hgcr_interfaces/msg/modbus_holding_regs.hpp"
// #include "hgcr_interfaces/action/goto_preset.hpp"
// #include "hgcr_interfaces/action/ptz_relative_move.hpp"
// #include "hgcr_interfaces/action/rotate_to_pose.hpp"
// #include "hgcr_interfaces/srv/rotate.hpp"
// #include "hgcr_interfaces/srv/set_preset.hpp"
// #include "hgcr_interfaces/srv/set_rotate_speed.hpp"
#include "hgcr_interfaces/srv/set_holding_regs.hpp"


//#include "stag_ros/msg/hgcr_pose.hpp"

#include "std_msgs/msg/u_int16.hpp"

#define NUMBER_OF_REGISTER 256 

class Modbus_TCP_Server: public QObject, public rclcpp::Node
{
    Q_OBJECT
public:
    explicit Modbus_TCP_Server(QObject * parrent = nullptr);
    ~Modbus_TCP_Server();
    void init_modbus_server();
    void set_holding_regs_callback(const std::shared_ptr<hgcr_interfaces::srv::SetHoldingRegs::Request> request, std::shared_ptr<hgcr_interfaces::srv::SetHoldingRegs::Response> response); 
    
    // using PTZRelativeMove = hgcr_interfaces::action::PTZRelativeMove;
    // using GoalHandlePTZRelativeMove = rclcpp_action::ClientGoalHandle<PTZRelativeMove>;

    // using RotateToPose = hgcr_interfaces::action::RotateToPose;
    // using GoalHandleRotateToPose = rclcpp_action::ClientGoalHandle<RotateToPose>;

    // using GotoPreset = hgcr_interfaces::action::GotoPreset;
    // using GoalHandleGotoPreset = rclcpp_action::ClientGoalHandle<GotoPreset>;

    // using Rotate = hgcr_interfaces::srv::Rotate;
    // using SetRotateSpeed = hgcr_interfaces::srv::SetRotateSpeed;
    // using SetPreset = hgcr_interfaces::srv::SetPreset;

    // using SetStagParams = rcl_interfaces::srv::SetParameters;
    using SetHoldingRegister = hgcr_interfaces::srv::SetHoldingRegs;
signals:

public slots:
    void handleDeviceError(QModbusDevice::Error newError);
    void regsWritten(QModbusDataUnit::RegisterType table, int address, int size);
    void onStateChanged(int state);

private:
    int miDebugNoCleanStep{0};

    QModbusTcpServer *mpModbusDevice{nullptr};
    bool bModbusCommOK{true};
    void holding_regs_topic_callback(const hgcr_interfaces::msg::ModbusHoldingRegs::SharedPtr msg) const;
    // void hgcr_pose_topic_callback(const stag_ros::msg::HGCRPose::SharedPtr msg) const;

    // rclcpp::Publisher<std_msgs::msg::UInt16>::SharedPtr mpSetZAnglePublisher;

    rclcpp::Publisher<hgcr_interfaces::msg::ModbusHoldingRegs>::SharedPtr mpHoldingRegisterPublisher;
    rclcpp::Subscription<hgcr_interfaces::msg::ModbusHoldingRegs>::SharedPtr mpHoldingRegisterSubscriber;
    
    rclcpp::Service<SetHoldingRegister>::SharedPtr service_;
    hgcr_interfaces::msg::ModbusHoldingRegs mPublisherMessages;

    // rclcpp_action::Client<PTZRelativeMove>::SharedPtr mpPTZ_relative_client;
    // void send_ptz_goal(qint16 pan, qint16 tilt, qint16 zoom);
    // void goal_ptz_response_callback(GoalHandlePTZRelativeMove::SharedPtr future);
    // void feedback_ptz_callback(GoalHandlePTZRelativeMove::SharedPtr, const std::shared_ptr<const PTZRelativeMove::Feedback> feedback);
    // void result_ptz_callback(const GoalHandlePTZRelativeMove::WrappedResult & result);

    // rclcpp_action::Client<RotateToPose>::SharedPtr mpRotateToPose_client;
    // void send_rotate_pose(quint16 pose);
    // void goal_rotate_to_pose_response_callback(GoalHandleRotateToPose::SharedPtr future);
    // void feedback_rotate_to_pose_callback(GoalHandleRotateToPose::SharedPtr, const std::shared_ptr<const RotateToPose::Feedback> feedback);
    // void result_rotate_to_pose_callback(const GoalHandleRotateToPose::WrappedResult & result);

    // rclcpp_action::Client<GotoPreset>::SharedPtr mpGotoPreset_client;
    // void goto_preset(int preset_id);
    // void goal_goto_preset_response_callback(GoalHandleGotoPreset::SharedPtr future);
    // void feedback_goto_preset_callback(GoalHandleGotoPreset::SharedPtr, const std::shared_ptr<const GotoPreset::Feedback> feedback);
    // void result_goto_preset_callback(const GoalHandleGotoPreset::WrappedResult & result);

    // rclcpp::Client<Rotate>::SharedPtr mpRotate_client;
    // rclcpp::Client<SetRotateSpeed>::SharedPtr mpSetRotateSpeed_client;
    // rclcpp::Client<SetPreset>::SharedPtr mpSetPreset_client;
    // rclcpp::Client<SetStagParams>::SharedPtr mpSetStagParams_client;

    // rclcpp::Subscription<stag_ros::msg::HGCRPose>::SharedPtr mpHGCRPoseSubscriber;

    // bool mbAUTO{false};
    // int miCMD_ROBOT{0};
    // int miCMD_ARM{0};
    // int miAUTO_CLEAN_STATE{-1};
    
    // int miCamera_Rotation_Pose{3250};
    // int miRotation_Step{0};
public:
    QVector<qint32> m_HoldingRegisters;
    QVector<qint32> m_InputRegisters;
};

#endif
