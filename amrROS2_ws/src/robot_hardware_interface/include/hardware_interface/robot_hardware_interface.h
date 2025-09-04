#ifndef ROBOT_HARDWARE_INTERFACE_H
#define ROBOT_HARDWARE_INTERFACE_H

#include <iostream>
#include <libserial/SerialPort.h>
#include <libserial/SerialStream.h>
#include <vector>
#include <thread>
#include <iomanip>
#include <unistd.h>

// -------- Shared Protocol Definition --------
#define _PKG_LEN    36  // Total size of data frame (bytes)

// Field indexes in the pkg_data
#define _HEADER   0
#define _HOST_ID  1
#define _PKG_SIZE 2

// --- IMU (12 bytes) ---
#define _IMU_ROLL_L    3
#define _IMU_ROLL_H    4
#define _IMU_PITCH_L   5
#define _IMU_PITCH_H   6
#define _IMU_YAW_L     7
#define _IMU_YAW_H     8
#define _IMU_ACCX_L    9
#define _IMU_ACCX_H   10
#define _IMU_ACCY_L   11
#define _IMU_ACCY_H   12
#define _IMU_ACCZ_L   13
#define _IMU_ACCZ_H   14

// --- ODOM (6 bytes) ---
#define _ODOM_VX_L     15
#define _ODOM_VX_H     16
#define _ODOM_VY_L     17
#define _ODOM_VY_H     18
#define _ODOM_WZ_L     19
#define _ODOM_WZ_H     20

// --- Range (6 bytes) ---
#define _RANGER_RIGHT_L   21
#define _RANGER_RIGHT_H   22
#define _RANGER_CENTER_L  23
#define _RANGER_CENTER_H  24
#define _RANGER_LEFT_L    25
#define _RANGER_LEFT_H    26

// --- Safety ---
#define _SAFETY_   27

// --- BMS (7 bytes) ---
#define _BMS_VOLTAGE_L   28
#define _BMS_VOLTAGE_H   29
#define _BMS_CURRENT_L   30
#define _BMS_CURRENT_H   31
#define _BMS_PERCENT_L   32
#define _BMS_PERCENT_H   33
#define _BMS_STATUS_     34

// --- Checksum ---
#define _CHK_SUM_   35

class HardwareInterface 
{
public:
    const uint8_t DEBUG         = false;
    const uint8_t DEBUG_IMU     = false;
    const uint8_t DEBUG_SEND    = false;
    const uint8_t DEBUG_RECEIVE = false;
    const uint8_t DEBUG_ODOM    = false;
    const uint8_t DEBUG_RANGE   = false;
    const uint8_t DEBUG_BATT    = false;

    const uint8_t SERIALPORT_TIMEOUT_MS = 50;

    struct three_dimension
    {
        float x = 0.0;
        float y = 0.0;
        float z = 0.0;
    };

    three_dimension angular_velocity;
    three_dimension linear_acceleration;
    three_dimension odom_velocity;

    float range_left;
    float range_center;
    float range_right;

    float voltage_;
    float current_;
    float percentage_;
    uint8_t status_;

    bool update_imu_;
    bool update_odom_;
    bool update_range_;
    bool update_batt_;
    bool emer_state_;
    bool bumper_state_;
    bool cliff_state_;


    HardwareInterface(const std::string& port);

    ~HardwareInterface();

    void SetMotion(float v_x, float v_y, float v_z);
    void UpdateIP(char* addressBuffer);
    void UpdateStatus(int status);

private:
    const uint8_t HEAD          = 0xFF;
    const uint8_t HOST_ID       = 0x00;
    const uint8_t DEVICE_ID     = 0x01;

    const uint8_t FUNC_MOTION   = 0x01;
    const uint8_t FUNC_IMU      = 0x02;
    const uint8_t FUNC_ODOM     = 0x03;
    const uint8_t FUNC_RANGE    = 0x04;
    const uint8_t FUNC_IP       = 0x05;
    const uint8_t FUNC_STATUS   = 0x06;
    const uint8_t FUNC_BATT     = 0x07;

    std::string port_name;
    std::thread receive_thread_;
    LibSerial::SerialPort serial_port;
    
    bool run_receive_thread;

    void ParseData(uint8_t FUNC_TYPE, const std::vector<uint8_t>& data); 
    void ParsePacket(const uint8_t* buf, size_t len);
    void SendData(uint8_t FUNC_TYPE, const std::vector<uint8_t>& param);
    void ReceiveData();

};


#endif
