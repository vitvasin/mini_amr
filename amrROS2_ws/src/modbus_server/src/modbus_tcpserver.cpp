/*
 * =====================================================================================
 *
 *       Filename:  modbus_tcpserver.cpp
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  06/22/2023 01:17:43 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  YOUR NAME (), 
 *   Organization:  
 *
 * =====================================================================================
 */
#include <chrono>
#include "modbus_tcpserver.h"
#include <QDebug>
#include <QUrl>
#define ADDR_PAN 100
#define ADDR_TILT 101
#define ADDR_ZOOM 102
#define ADDR_ROTATE 103
#define ADDR_ROTATION_SPEED 104
#define ADDR_SET_PRESET 105
#define ADDR_GOTO_PRESET 106
#define ADDR_LOWER_LINE 110
#define ADDR_UPPER_LINE 111
#define ADDR_MOVE_NEXT 112

#define ADDR_INPUT_PAN 100
#define ADDR_INPUT_TILT 101
#define ADDR_INPUT_ZOOM 102
#define ADDR_INPUT_ROTATE 103
#define ADDR_INPUT_ROTATION_SPEED 104
#define ADDR_INPUT_SET_PRESET 105
#define ADDR_INPUT_GOTO_PRESET 106
#define ADDR_INPUT_LOWER_LINE 110
#define ADDR_INPUT_UPPER_LINE 111

//////////// ROBOT //////////////
#define ADDR_IS_START_AUTO 2
#define ADDR_AUTO_CMD_ROBOT 4
#define ADDR_AUTO_CMD_ARM 5
#define ADDR_CMD_DX 7
#define ADDR_CMD_DY 8
#define ADDR_REQUEST_NEXT_POS 9
#define ADDR_MODE 30
//////////// ROBOT TEMPERATURES /////////////
#define ADDR_TEMP_1 20
#define ADDR_TEMP_2 21
//#define PTZ_CAM
#define STAG_POSE_SIM

using namespace rclcpp;
using namespace std::placeholders;

Modbus_TCP_Server::Modbus_TCP_Server(QObject* parent) :
    QObject(parent), Node("HGCR_ModBusServer")
{
////////////////////////////////////////////////  Modbus  /////////////////////////////////////////////////

////////////////////////////////////////////////  Modbus  /////////////////////////////////////////////////
    m_HoldingRegisters.resize(NUMBER_OF_REGISTER);
    m_InputRegisters.resize(NUMBER_OF_REGISTER);

    // mpSetZAnglePublisher = this->create_publisher<std_msgs::msg::UInt16>("/ptz_camera/set_angle", 10);

    mpHoldingRegisterPublisher = this->create_publisher<hgcr_interfaces::msg::ModbusHoldingRegs>("mserver/holding_regs", 10);
    mpHoldingRegisterSubscriber = this->create_subscription<hgcr_interfaces::msg::ModbusHoldingRegs>("mmaster/holding_regs", 10, std::bind(&Modbus_TCP_Server::holding_regs_topic_callback, this, _1)); 
    // mpHGCRPoseSubscriber = this->create_subscription<stag_ros::msg::HGCRPose>("stag_ros/pose", 10, std::bind(&Modbus_TCP_Server::hgcr_pose_topic_callback, this, _1)); 
    service_ = this->create_service<SetHoldingRegister>("mservice/holding_regs", std::bind(&Modbus_TCP_Server::set_holding_regs_callback, this, std::placeholders::_1, std::placeholders::_2));

    init_modbus_server();
//////////////////////////////////////////////////////////////////////////////////////////////////////////

}

void Modbus_TCP_Server::set_holding_regs_callback(const std::shared_ptr<SetHoldingRegister::Request> request, std::shared_ptr<SetHoldingRegister::Response> response)
{
   
    response->result = "success";
    RCLCPP_INFO_STREAM(this->get_logger(), "Srv/Address: " << request->address  << "   " << "Srv/value: " << request->value );
//    mpModbusDevice->setData(QModbusDataUnit::InputRegisters, request->address, request->value);
    mpModbusDevice->setData(QModbusDataUnit::HoldingRegisters, request->address, request->value);

}

Modbus_TCP_Server::~Modbus_TCP_Server()
{
    if( mpModbusDevice )
    {
        mpModbusDevice->disconnectDevice();
        delete mpModbusDevice;
    }
    RCLCPP_INFO(this->get_logger(), "Exit the Modbus Server!");
}

void Modbus_TCP_Server::init_modbus_server()
{
    mpModbusDevice = new QModbusTcpServer(this);
    if( !mpModbusDevice )
        RCLCPP_ERROR(this->get_logger(), "Cannot create Modbus Server");
    else
    {
        QModbusDataUnitMap reg;
        reg.insert(QModbusDataUnit::InputRegisters, {QModbusDataUnit::InputRegisters, 0, NUMBER_OF_REGISTER} );
        reg.insert(QModbusDataUnit::HoldingRegisters, {QModbusDataUnit::HoldingRegisters, 0, NUMBER_OF_REGISTER} );
        mpModbusDevice->setMap(reg);

        connect(mpModbusDevice, &QModbusServer::dataWritten,
                this, &Modbus_TCP_Server::regsWritten);
        connect(mpModbusDevice, &QModbusServer::stateChanged,
                this, &Modbus_TCP_Server::onStateChanged);
        connect(mpModbusDevice, &QModbusServer::errorOccurred,
                this, &Modbus_TCP_Server::handleDeviceError);
    
        //const QUrl url = QUrl::fromUserInput("192.168.1.254:1502");
        const QUrl url = QUrl::fromUserInput("localhost:1520");
        mpModbusDevice->setConnectionParameter(QModbusDevice::NetworkPortParameter, url.port());
        mpModbusDevice->setConnectionParameter(QModbusDevice::NetworkAddressParameter, url.host());
        //mpModbusDevice->setServerAddress(10);
	mpModbusDevice->setServerAddress(10);

        if( !mpModbusDevice->connectDevice() )
        {
            RCLCPP_ERROR(this->get_logger(), "Cannot Start Modbus Server!");
            RCLCPP_ERROR(this->get_logger(), mpModbusDevice->errorString().toStdString().c_str());
        }
        else
        {
            RCLCPP_INFO(this->get_logger(), "Server Address : %d", mpModbusDevice->serverAddress());
            
        
            RCLCPP_INFO(this->get_logger(), "Modbus Server is Ready!");
        }
    }
}


void Modbus_TCP_Server::handleDeviceError(QModbusDevice::Error newError)
{
    if( newError == QModbusDevice::NoError || !mpModbusDevice )
        return;
    RCLCPP_ERROR(this->get_logger(), mpModbusDevice->errorString().toStdString().c_str()); 
}

void Modbus_TCP_Server::regsWritten(QModbusDataUnit::RegisterType table, int address, int size)
{
    if( table == QModbusDataUnit::InputRegisters )
    {
        for( int idx = 0; idx < size; idx ++ )
        {
            quint16 value;
            mpModbusDevice->data(QModbusDataUnit::InputRegisters, quint16(address + idx), &value);
            m_InputRegisters[address+idx] = static_cast<qint32>(value);
            qint16 abs_address = address + idx;
            if( abs_address != 15 && abs_address != ADDR_CMD_DY && abs_address != ADDR_CMD_DX ) 
                RCLCPP_INFO(this->get_logger(), "Update Input : %d \t %d", address + idx, value);
        }
        
    }
    else if( table == QModbusDataUnit::HoldingRegisters )
    {
        if( int(mPublisherMessages.data.size()) != size )
            mPublisherMessages.data.resize(size);
        for( int idx = 0; idx < size; idx++ )
        { 
            quint16 value;
            mpModbusDevice->data(QModbusDataUnit::HoldingRegisters, quint16(address + idx), &value);
            m_HoldingRegisters[address + idx] = static_cast<qint32>(value); 

            mPublisherMessages.data[idx] = value;
            RCLCPP_INFO(this->get_logger(), "Update Holding : %d \t %d", address + idx, value);
        }
        mPublisherMessages.address = address;
        mPublisherMessages.size = size;
       
        if( address < 100 )
        {
            // if( address == ADDR_MODE )
            // {
            //     auto parameter = rcl_interfaces::msg::Parameter();
            //     auto request = std::make_shared<SetStagParams::Request>();
            //     parameter.name = "mode";
            //     parameter.value.type = 2;
            //     parameter.value.integer_value = m_HoldingRegisters[ADDR_MODE];
            //     request->parameters.push_back(parameter);
            //     mpSetStagParams_client->async_send_request(request);
            // }
            mpHoldingRegisterPublisher->publish(mPublisherMessages);
        }
    } 
}

void Modbus_TCP_Server::onStateChanged(int state)
{
    if( state == QModbusDevice::ConnectedState )
        RCLCPP_INFO(this->get_logger(), "Modbus Server Connected!");
    else if( state == QModbusDevice::UnconnectedState )
        RCLCPP_INFO(this->get_logger(), "Modbus Server Disconnected!");
}
/////////////// From Modbus RTU Connected to the Robot
void Modbus_TCP_Server::holding_regs_topic_callback(const hgcr_interfaces::msg::ModbusHoldingRegs::SharedPtr msg) const
{
    for( quint16 idx = 0; idx < msg->size; idx++ )
        //mpModbusDevice->setData(QModbusDataUnit::HoldingRegisters, msg->address+idx, msg->data[idx]);
        mpModbusDevice->setData(QModbusDataUnit::InputRegisters, msg->address+idx, msg->data[idx]);

}


