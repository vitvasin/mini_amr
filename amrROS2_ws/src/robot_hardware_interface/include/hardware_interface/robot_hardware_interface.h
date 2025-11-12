#ifndef ROBOT_HARDWARE_INTERFACE_H
#define ROBOT_HARDWARE_INTERFACE_H

#include <iostream>
#include <libserial/SerialPort.h>
#include <libserial/SerialStream.h>
#include <vector>
#include <thread>
#include <iomanip>
#include <unistd.h>

//----------- Pkg data -----------------
#define _PKG_LEN       43 //  param_len + 3(for _header, _host_id, _pkg_size) + 1(for _chk_sum)    == 36

#define _HEADER         0
#define _HOST_ID        1
#define _PKG_SIZE       2

#define _IMU_ROLL_L     0               // IMU data(12)
#define _IMU_ROLL_H     1
#define _IMU_PITCH_L    2
#define _IMU_PITCH_H    3
#define _IMU_YAW_L      4
#define _IMU_YAW_H      5
#define _IMU_ACCX_L     6
#define _IMU_ACCX_H     7
#define _IMU_ACCY_L     8
#define _IMU_ACCY_H     9
#define _IMU_ACCZ_L     10
#define _IMU_ACCZ_H     11

#define _ODOM_VX_L      12 // ODOM data(6)
#define _ODOM_VX_H      13
#define _ODOM_VY_L      14
#define _ODOM_VY_H      15
#define _ODOM_WZ_L      16
#define _ODOM_WZ_H      17

#define _RANGER_RIGHT_L     18 // Ranger data(6)
#define _RANGER_RIGHT_H     19
#define _RANGER_CENTER_L    20
#define _RANGER_CENTER_H    21
#define _RANGER_LEFT_L      22
#define _RANGER_LEFT_H      23

#define _SAFETY_            24 // Safty data(1)  xxxx xyzw     y: emer state, z: bumper_state, w: clift_state

#define _BMS_VOLTAGE_L      25 // BMS data(4)(28-31)  for mini emr   , BMS data(7)(28-34)  for thai_easy & WIS amr
#define _BMS_VOLTAGE_H      26
#define _BMS_CURRENT_L      27
#define _BMS_CURRENT_H      28
#define _BMS_PERCENT_L      29
#define _BMS_PERCENT_H      30
#define _BMS_STATUS_        31
#define _IR_CHARGE_STATE_  32
#define _MTR_DRIVE_STATE_ 33
#define _MTR_FAULT_STATE_        34
#define _RESERVED2_        35
#define _RESERVED3_        36
#define _RESERVED4_        37
#define _RESERVED5_        38
#define _CHK_SUM_           39

// #define _IMU_READY_     32          // add new
// #define _ODOM_READY_    33          // add new
// #define _RANGER_READY_  34          // add new
// #define _SAFETY_READY_  35          // add new
// #define _BMS_READY_     36          // add new

// #define _CHK_SUM_       37          //32


// #define _IMU_ROLL_L     3               // IMU data(12)
// #define _IMU_ROLL_H     4
// #define _IMU_PITCH_L    5
// #define _IMU_PITCH_H    6
// #define _IMU_YAW_L      7
// #define _IMU_YAW_H      8
// #define _IMU_ACCX_L     9
// #define _IMU_ACCX_H     10
// #define _IMU_ACCY_L     11
// #define _IMU_ACCY_H     12
// #define _IMU_ACCZ_L     13
// #define _IMU_ACCZ_H     14

// #define _ODOM_VX_L      15 // ODOM data(6)
// #define _ODOM_VX_H      16
// #define _ODOM_VY_L      17
// #define _ODOM_VY_H      18
// #define _ODOM_WZ_L      19
// #define _ODOM_WZ_H      20

// #define _RANGER_RIGHT_L     21 // Ranger data(6)
// #define _RANGER_RIGHT_H     22
// #define _RANGER_CENTER_L    23
// #define _RANGER_CENTER_H    24
// #define _RANGER_LEFT_L      25
// #define _RANGER_LEFT_H      26

// #define _SAFETY_            27 // Safty data(1)  xxxx xyzw     y: emer state, z: bumper_state, w: clift_state

// #define _BMS_VOLTAGE_L      28 // BMS data(4)(28-31)  for mini emr   , BMS data(7)(28-34)  for thai_easy & WIS amr
// #define _BMS_VOLTAGE_H      29
// #define _BMS_CURRENT_L      30
// #define _BMS_CURRENT_H      31
// #define _BMS_PERCENT_L      32
// #define _BMS_PERCENT_H      33
// #define _BMS_STATUS_        34

// #define _CHK_SUM_           35

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
    uint16_t ir_charge_state_;
    uint8_t motor_drive_state_;
    uint8_t drive_fault_state_;

    bool update_imu_;
    bool update_odom_;
    bool update_range_;
    bool update_batt_;

    HardwareInterface(const std::string& port);

    ~HardwareInterface();

    void SetMotion(float v_x, float v_y, float v_z);
    void SetChargeState(uint16_t charge_state); 
    void SetMotorDriveState(bool state);
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
    const uint8_t FUNC_CHARGE     = 0x08;
    const uint8_t FUNC_MTR_DRIVE     = 0x09;

    std::string port_name;
    LibSerial::SerialPort serial_port;
    bool run_receive_thread;

    void ParseData(uint8_t FUNC_TYPE, const std::vector<uint8_t>& data); 
    void ParseData(const std::vector<uint8_t>& data); 
    void SendData(uint8_t FUNC_TYPE, const std::vector<uint8_t>& param);
    void ReceiveData();

};


#endif
