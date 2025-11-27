#define USE_SMR_CONFIG

#include <Arduino.h>
#include <TeensyThreads.h>
#include <ModbusMaster.h>
// #include <jbdbms.h>
#include <Adafruit_MCP23X17.h>

#include <stdio.h>
#include <vector>
#include "math.h"

#include "config.h"
#include "kinematics.h"
#include "JY61P.h"
// #include "motor_driver.cpp"
#include "can_driver.h"
#include "bms.h"

#define DEBUG false
#define DEBUG_IMU false
#define DEBUG_MOTOR false
#define DEBUG_MOTION false
#define DEBUG_RANGE false

#define DEBUG_ODOM false
#define DEBUG_SEND false
#define DEBUG_RECEIVE false
#define DEBUG_OLED false
#define DEBUG_SAFTY true // false
#define DEBUG_BATT true  // false

#define HEAD 0xFF
#define HOST_ID 0x00
#define DEVICE_ID 0x01

#define FUNC_MOTION 0x01
#define FUNC_IMU 0x02
#define FUNC_ODOM 0x03
#define FUNC_RANGE 0x04
#define FUNC_IP 0x05
#define FUNC_STATUS 0x06
#define FUNC_BATT 0x07
#define FUNC_CHARGE 0x08
#define FUNC_MTR_DRIVE 0x09

/////////////////////////////////////////////////////////////////////////////////////
#define motor_axis0 0
#define motor_axis1 1
// #define MAX485_DE 4
// #define MAX485_RE 5

#define TEENSY_RS485_DIR_PIN 22

// #define MOTOR_DRIVER_SERIAL Serial1
#define SENSORS_SERIAL Serial1 // use for cliff & ultra sonic
#define BMS_SERIAL Serial2
// #define ULTARSONICS_SERIAL Serial2

#define REG_DUALAXIS_CMD_SPEED 0x0B1A
#define REG_AXIS1_COMMAND_SPEED 0x0A02
#define REG_AXIS1_FEEDBACK_SPEED 0x0A03
#define REG_AXIS2_COMMAND_SPEED 0x0C02
#define REG_AXIS2_FEEDBACK_SPEED 0x0C03

#define CliffDistanceLimit 200 // 20cm

//----------- Pkg data -----------------
#define _PKG_LEN    43 //  param_len + 3(for _header, _host_id, _pkg_size) + 1(for _chk_sum)    == 36

#define _HEADER 0
#define _HOST_ID 1
#define _PKG_SIZE 2

#define _IMU_ROLL_L 3 // IMU data(12)
#define _IMU_ROLL_H 4
#define _IMU_PITCH_L 5
#define _IMU_PITCH_H 6
#define _IMU_YAW_L 7
#define _IMU_YAW_H 8
#define _IMU_ACCX_L 9
#define _IMU_ACCX_H 10
#define _IMU_ACCY_L 11
#define _IMU_ACCY_H 12
#define _IMU_ACCZ_L 13
#define _IMU_ACCZ_H 14

#define _ODOM_VX_L 15 // ODOM data(6)
#define _ODOM_VX_H 16
#define _ODOM_VY_L 17
#define _ODOM_VY_H 18
#define _ODOM_WZ_L 19
#define _ODOM_WZ_H 20

#define _RANGER_RIGHT_L 21 // Ranger data(6)
#define _RANGER_RIGHT_H 22
#define _RANGER_CENTER_L 23
#define _RANGER_CENTER_H 24
#define _RANGER_LEFT_L 25
#define _RANGER_LEFT_H 26

#define _SAFETY_ 27 // Safty data(1)  xxxx xyzw     y: emer state, z: bumper_state, w: clift_state

#define _BMS_VOLTAGE_L 28 // BMS data(4)(28-31)  for mini emr   , BMS data(7)(28-34)  for thai_easy & WIS amr
#define _BMS_VOLTAGE_H 29
#define _BMS_CURRENT_L 30
#define _BMS_CURRENT_H 31
#define _BMS_PERCENT_L 32
#define _BMS_PERCENT_H 33
#define _BMS_STATUS_ 34
#define _IR_CHARGE_STATE_  35   
#define _MTR_DRIVE_STATE_ 36
#define _MTR_FAULT_STATE_ 37
#define _RESERVED2_        38
#define _RESERVED3_        39
#define _RESERVED4_        40
#define _RESERVED5_        41 

#define _CHK_SUM_       42


//--------------------------------------

ModbusMaster Led_Modele;
ModbusMaster Cliff_Sensor;
ModbusMaster Ultrasonics_L; // Left
ModbusMaster Ultrasonics_C; // Center
ModbusMaster Ultrasonics_R; // Right
ModbusMaster IR_Charge_State;

int LED = 13;        // LED status TeensyMicromod
int LED_RUN = 32;    // G9 - Teensy pin 32, MicroMod pad 65
int LED_STATUS = 26; // G8 - Teensy pin 26, MicroMod pad 67
int RS485_DE = 4;
int RS485_RE = 5;
String data;
/////////////////////////////////////////////////////////////////////////////////////

int16_t range_left;
int16_t range_center;
int16_t range_right;
uint16_t cliff;

uint8_t range_limit = 200;
uint8_t led_mode_prev;
uint8_t alarm_mode_prev;

uint8_t imu2send[12];
uint8_t odom2send[6];
uint8_t batt2send[4];
uint8_t range2send[6];
bool imu_ready;
bool odom_ready;
bool batt_ready;
bool range_ready;
static bool emer_flag = true;
// Latest BMS floats filled when valid packet received

uint8_t batt_status = 0;
bool update_batt_ = false;
// --- BMS state machine ---
static uint8_t bms_buf[50];
static uint8_t bms_index = 0;
static unsigned long last_bms_request = 0;
const unsigned int bms_request_interval = 1000; // every 1s

// --- Non-blocking parser state ---
#define RX_BUFFER_MAX 128

static uint8_t rx_buffer[RX_BUFFER_MAX];
static uint8_t rx_index = 0;
static uint8_t rx_expected_length = 0;

Kinematics kinematics(
    Kinematics::SMR_BASE,
    MOTOR_MAX_RPM,
    MAX_RPM_RATIO,
    MOTOR_OPERATING_VOLTAGE,
    MOTOR_POWER_MAX_VOLTAGE,
    WHEEL_DIAMETER,
    LR_WHEELS_DISTANCE);

Kinematics::velocities cmd_vel;
Kinematics::velocities vel, vel_old;

Threads::Mutex xSendDataMutex;

static const int RX_BUF_SIZE = 100; // 1024;

unsigned long prev_cmd_time = 0;
unsigned long master_time = 0, imu_update_time = 0, control_update_time = 0, bms_update_time = 0, sensor_update_time;
unsigned long safety_time = 0, send_data_time = 0, receive_data_time = 0;
//const unsigned int imu_interval = 45, control_interval = 30, bms_interval = 200, sensor_interval = 50, safety_interval = 50, send_data_interval = 30, receive_data_interval;
const unsigned int imu_interval = 30, control_interval = 10, bms_interval = 1000, sensor_interval = 200, safety_interval = 50, send_data_interval = 10, receive_data_interval;

unsigned char pkg_data[_PKG_LEN];

Adafruit_MCP23X17 mcp;
bool mcp_input[8];
bool mcp_out_put[8];

bool cliff_state, bumper_state, emer_state, virtual_emer_state = false , stop, ack;
bool connection_failed;


//charge state
// uint8_t charge_state = 0; // 0: not charging, 1: charging, 2: charge done

void parse_data(uint8_t func, uint8_t *data, uint8_t data_len)
{
    uint8_t charge_state = 0; // 0: not charging, 1: charging, 2: charge done

    if (func == FUNC_MOTION)
    {
        int16_t packed_v_x = (data[1] << 8) | data[0];
        int16_t packed_v_y = (data[3] << 8) | data[2];
        int16_t packed_w_z = (data[5] << 8) | data[4];

        cmd_vel.linear_x = packed_v_x / 1000.0;
        cmd_vel.linear_y = packed_v_y / 1000.0;
        cmd_vel.angular_z = packed_w_z / 1000.0;

        prev_cmd_time = millis();

        //Serial5.printf("Vx: %f ---  Vy: %f  ---  Wz: %f\n", cmd_vel.linear_x, cmd_vel.linear_y, cmd_vel.angular_z);
    }
    if (func == FUNC_STATUS)
    {
        static uint32_t LedRosComm = millis();
        if ((millis() - LedRosComm) > 1000)
        {
            digitalWrite(LED_RUN, !digitalRead(LED_RUN)); // For ROS Communication
            // Serial5.printf("ROS comm start.\n");
            LedRosComm = millis();
        }
    }
    if (func == FUNC_CHARGE)
    {
        if (data_len >= 1)
        {
            uint8_t result;
            charge_state = data[0];
            // Serial5.print("Charge state: ");
            // Serial5.println(charge_state);
            
            if (charge_state == 20)
            {
                result = IR_Charge_State.writeSingleRegister(1, 20); // start charge
                if (result == IR_Charge_State.ku8MBSuccess)
                {
                   // Serial5.println("Sent: RobotReadyToCharge (20)");
                   //charge_state =11;
                }else {
                //Serial5.println("Error sending state to robot");
                }


            }else if (charge_state == 22)
            {
                result = IR_Charge_State.writeSingleRegister(1, 22); // stop charge
            
                if (result == IR_Charge_State.ku8MBSuccess)
                {
                  //  Serial5.println("Sent: StopCharging (22)");
                     //charge_state =12;
                }else {
                //Serial5.println("Error sending state to robot");
                }


            }else if (charge_state == 21)
            {
                result = IR_Charge_State.writeSingleRegister(1, 21); // Robot is fully charged
                if (result == IR_Charge_State.ku8MBSuccess)
                {
                   // Serial5.println("Sent: ChargingComplete (21)");
                   // charge_state =13;
                }else {
                //Serial5.println("Error sending state to robot");
                }
            }

            /// for debug /////////////////////////////////////////////////////////////// DB
            // result = IR_Charge_State.writeSingleRegister(1, 22);

            ////////////////////////////////////////////////////////////////////////////// DB
        
        }
    }
    if(func == FUNC_MTR_DRIVE)
    {
        if (data_len >= 1)
        {
            uint8_t mtr_drive_state = data[0];
            // Serial5.print("MTR Drive State: ");
            // Serial5.println(mtr_drive_state);
            if(mtr_drive_state == 1)
            {
                // mcp.digitalWrite(3, HIGH);
                virtual_emer_state = false;
                mcp.digitalWrite(6, HIGH);
                mcp.digitalWrite(5, HIGH);
                mcp.digitalWrite(4, HIGH);

                // mcp.digitalWrite(8, HIGH);
                // mcp.digitalWrite(9, HIGH);
                // delay(10);
            }
            else if(mtr_drive_state == 0)
            {
                // mcp.digitalWrite(3, LOW);
                mcp.digitalWrite(6, LOW);
                mcp.digitalWrite(5, LOW);
                mcp.digitalWrite(4, LOW);
                virtual_emer_state = true;
                emer_flag = true;

                

                // mcp.digitalWrite(8, LOW);
                // mcp.digitalWrite(9, LOW);
                // delay(10);
            }
        }
    }
}



void receive_data_task(void *parameter = nullptr)
{
    // Read all available bytes from UART
    while (Serial.available() > 0)
    {
        uint8_t byte_in = Serial.read();

        // Step 1: header check
        if (rx_index == 0)
        {
            if (byte_in == HEAD)
            {
                rx_buffer[rx_index++] = byte_in;
            }
            // else ignore garbage
        }
        else
        {
            rx_buffer[rx_index++] = byte_in;

            // Step 2: determine expected length
            if (rx_index == 3) // got HEAD + device_id + len
            {
                rx_expected_length = rx_buffer[2]; // len from packet
                if (rx_expected_length > RX_BUFFER_MAX)
                {
                    // reset if bogus length
                    rx_index = 0;
                }
            }

            // Step 3: check if full frame received
            if (rx_expected_length > 0 && rx_index == (rx_expected_length + 1)) // +1 for HEAD
            {
                // Got a full frame!
                uint8_t checksum = 0;
                for (uint8_t i = 0; i < rx_index - 1; i++) checksum += rx_buffer[i];
                checksum &= 0xFF;
                uint8_t rx_checksum = rx_buffer[rx_index - 1];

                if (checksum == rx_checksum)
                {
                    uint8_t device_id = rx_buffer[1];
                    if (device_id == DEVICE_ID)
                    {
                        uint8_t func = rx_buffer[3];
                        uint8_t data_len = rx_expected_length - 4; // exclude header, dev, len, func
                        uint8_t *data = &rx_buffer[4];

                        if (DEBUG_RECEIVE) Serial5.println("Frame OK");
                        parse_data(func, data, data_len);
                    }
                }
                else
                {
                    if (DEBUG_RECEIVE) Serial5.println("Checksum fail");
                }

                // Reset for next frame
                rx_index = 0;
                rx_expected_length = 0;
            }
        }
    }
}
void send_data_task()
{
    //memset(pkg_data, 0, sizeof(pkg_data));

    pkg_data[_HEADER] = HEAD;
    pkg_data[_HOST_ID] = HOST_ID;
    pkg_data[_PKG_SIZE] = sizeof(pkg_data) - 1; //41-1// 36 - 1 // not include chk_sum  err.

    uint8_t checksum = 0;
    for (size_t i = 0; i < pkg_data[2]; i++)
    {
        checksum += pkg_data[i];
    }
    pkg_data[_CHK_SUM_] = checksum &= 0xFF;

    Serial.write(pkg_data, sizeof(pkg_data));

    // for (size_t i = 0; i < sizeof(cmd); i++)
    // {
    //     Serial.write(cmd[i]);
    // }

    // for (size_t i = 0; i < sizeof(pkg_data); i++)
    // {
    //     Serial.printf("%d : ", i);
    //     Serial.println(pkg_data[i]);
    //     // Serial5.print(" ");
    // }
}

void imu_update_task()
{
    float imu_gyro_dps[3] = {0};
    float imu_accel_g[3] = {0};

    // uint64_t start_time = millis();

    imu_gyro_dps[0] = (JY61P.getGyroX() / 180) * 3.14;
    imu_gyro_dps[1] = (JY61P.getGyroY() / 180) * 3.14;
    imu_gyro_dps[2] = (JY61P.getGyroZ() / 180) * 3.14;

    imu_accel_g[0] = JY61P.getAccX();
    imu_accel_g[1] = JY61P.getAccY();
    imu_accel_g[2] = JY61P.getAccZ();

    // Serial5.print("roll : %f - pitch: %f - "); Serial.println(imu_gyro_dps[0]);
    // Serial5.print("pitch: "); Serial.println(imu_gyro_dps[1]);
    // Serial5.print("yaw  : "); Serial.println(imu_gyro_dps[2]);
    // Serial5.print("accx : "); Serial.println(imu_accel_g[0]);
    // Serial5.print("accy : "); Serial.println(imu_accel_g[1]);
    // Serial5.print("accz : "); Serial.println(imu_accel_g[2]);
    // Serial5.println("-------------------------------------------");

    int16_t roll = static_cast<int16_t>(imu_gyro_dps[0] * 1000);
    int16_t pitch = static_cast<int16_t>(imu_gyro_dps[1] * 1000);
    int16_t yaw = static_cast<int16_t>(imu_gyro_dps[2] * 1000);

    int16_t acc_x = static_cast<int16_t>(imu_accel_g[0] * 1000);
    int16_t acc_y = static_cast<int16_t>(imu_accel_g[1] * 1000);
    int16_t acc_z = static_cast<int16_t>(imu_accel_g[2] * 1000);

    pkg_data[_IMU_ROLL_L] = static_cast<uint8_t>(roll & 0xFF);
    pkg_data[_IMU_ROLL_H] = static_cast<uint8_t>((roll >> 8) & 0xFF);
    pkg_data[_IMU_PITCH_L] = static_cast<uint8_t>(pitch & 0xFF);
    pkg_data[_IMU_PITCH_H] = static_cast<uint8_t>((pitch >> 8) & 0xFF);
    pkg_data[_IMU_YAW_L] = static_cast<uint8_t>(yaw & 0xFF);
    pkg_data[_IMU_YAW_H] = static_cast<uint8_t>((yaw >> 8) & 0xFF);
    pkg_data[_IMU_ACCX_L] = static_cast<uint8_t>(acc_x & 0xFF);
    pkg_data[_IMU_ACCX_H] = static_cast<uint8_t>((acc_x >> 8) & 0xFF);
    pkg_data[_IMU_ACCY_L] = static_cast<uint8_t>(acc_y & 0xFF);
    pkg_data[_IMU_ACCY_H] = static_cast<uint8_t>((acc_y >> 8) & 0xFF);
    pkg_data[_IMU_ACCZ_L] = static_cast<uint8_t>(acc_z & 0xFF);
    pkg_data[_IMU_ACCZ_H] = static_cast<uint8_t>((acc_z >> 8) & 0xFF);
    //pkg_data[_IMU_READY_] = 1;

    // uint64_t end_time = millis();
    // uint32_t dt = end_time - start_time;
}

// ---------------- BMS Task -------------------
void poll_bms()
{
    // Step A: send request periodically
    if (millis() - last_bms_request >= bms_request_interval)
    {
        SendDataToBMS(VOLT_AMP_CMD);     
        last_bms_request = millis();
    }

    // Step B: accumulate incoming bytes
    while (BMS_SERIAL.available())
    {
        uint8_t c = BMS_SERIAL.read();
        if (bms_index < sizeof(bms_buf))
        {
            bms_buf[bms_index++] = c;
        }

        // Simple heuristic: check minimum length for packet
        if (bms_index >= 13) // enough for 0x90 packet
        {
            // calculate checksum
            uint8_t chk = calChecksum((char*)bms_buf, bms_index-1);
            if (chk == bms_buf[bms_index-1])
            {
                // ✅ Parse packet now
                parse_bms_packet(bms_buf, bms_index);
                bms_index = 0; // reset buffer
            }
            else if (bms_index >= 50) {
                // overflow / invalid packet -> reset
                bms_index = 0;
            }
        }
    }
}

void parse_bms_packet(uint8_t *Buf, uint8_t len)
{
    if (Buf[2] == 0x90) // voltage/current/SOC frame
    {
        unsigned int BattVolt = ((unsigned)Buf[4]<<8) | Buf[5];
        fBattVolt = BattVolt * 0.1f;

        int BattCurrent = ((int)Buf[8]<<8) | Buf[9];
        fBattCurrent = (BattCurrent - 30000) * 0.1f;

        unsigned int BattSOC = ((unsigned)Buf[10]<<8) | Buf[11];
        fBattSOC = BattSOC * 0.1f;

        // Determine status
        if (fBattSOC >= 100.0) batt_status = 4;  // full
        else if (fBattCurrent > 0) batt_status = 1; // charging
        else if (fBattCurrent < 0) batt_status = 2; // discharging
        else batt_status = 0; // unknown

        update_batt_ = true;
    }
    else if (Buf[2] == 0x93) // info frame
    {
        uint8_t ChargeStatus = Buf[4];
        uint8_t BmsLife = Buf[7];
        uint32_t BattCap = (Buf[8]<<24) | (Buf[9]<<16) | (Buf[10]<<8) | Buf[11];
        // store / log if you want
        update_batt_ = true;
    }
}

// void bms_task()
// {
//     int16_t voltage = 0, current = 0, percentage = 0;
//     uint8_t batt_status = 0;

//     if (RequestDataFromBMD(VOLT_AMP_CMD) == 1)
//     {
//         voltage = static_cast<int16_t>(fBattVolt * 100);
//         current = static_cast<int16_t>(fBattCurrent * 100);
//         percentage = static_cast<int16_t>(fBattSOC * 100);

//         if (fBattSOC >= 100)
//             batt_status = 4; // FULL
//         else if (fBattCurrent > 0)
//             batt_status = 1; // CHARGIGN
//         else if (fBattCurrent < 0)
//             batt_status = 2; // DISCHARGIGN
//         else
//             batt_status = 0; // UNKNOWN

//         pkg_data[_BMS_VOLTAGE_L] = static_cast<uint8_t>(voltage & 0xFF);
//         pkg_data[_BMS_VOLTAGE_H] = static_cast<uint8_t>((voltage >> 8) & 0xFF);
//         pkg_data[_BMS_CURRENT_L] = static_cast<uint8_t>(current & 0xFF);
//         pkg_data[_BMS_CURRENT_H] = static_cast<uint8_t>((current >> 8) & 0xFF);
//         pkg_data[_BMS_PERCENT_L] = static_cast<uint8_t>(percentage & 0xFF);
//         pkg_data[_BMS_PERCENT_H] = static_cast<uint8_t>((percentage >> 8) & 0xFF);
//         pkg_data[_BMS_STATUS_] = static_cast<uint8_t>(batt_status & 0xFF);
//         //pkg_data[_BMS_READY_] = 1;

//         // Serial5.printf("voltage    : %d\n", voltage);
//         // Serial5.printf("current    : %d\n", current);
//         // Serial5.printf("percentage : %d\n", percentage);
//     }
//     //threads.delay(5);
// }

// ---------------- BMS Task -------------------
void bms_task()
{   
    // Step A: poll non-blocking reader
    poll_bms();

    // Step B: if new packet parsed, update pkg_data
    if (update_batt_)
    {
        int16_t voltage    = (int16_t)(fBattVolt * 100);     // scale to centivolts
        int16_t current    = (int16_t)(fBattCurrent * 100);  // scale to centiamps
        int16_t percentage = (int16_t)(fBattSOC * 100);      // scale to centi%

        pkg_data[_BMS_VOLTAGE_L] = static_cast<uint8_t>(voltage & 0xFF);
        pkg_data[_BMS_VOLTAGE_H] = static_cast<uint8_t>((voltage >> 8) & 0xFF);
        pkg_data[_BMS_CURRENT_L] = static_cast<uint8_t>(current & 0xFF);
        pkg_data[_BMS_CURRENT_H] = static_cast<uint8_t>((current >> 8) & 0xFF);
        pkg_data[_BMS_PERCENT_L] = static_cast<uint8_t>(percentage & 0xFF);
        pkg_data[_BMS_PERCENT_H] = static_cast<uint8_t>((percentage >> 8) & 0xFF);
        pkg_data[_BMS_STATUS_] = static_cast<uint8_t>(batt_status & 0xFF);

        //update_batt_ = false; // clear flag until next packet
       // Serial.printf("BMS Update - Volt: %.1f V, Current: %.1f A, SOC: %.1f %%\n", fBattVolt, fBattCurrent, fBattSOC);
    }else
    {
        int16_t voltage    = (int16_t)(fBattVolt * 100);     // scale to centivolts
        int16_t current    = (int16_t)(fBattCurrent * 100);  // scale to centiamps
        int16_t percentage = (int16_t)(fBattSOC * 100);      // scale to centi%


        pkg_data[_BMS_VOLTAGE_L] = static_cast<uint8_t>(voltage & 0xFF);
        pkg_data[_BMS_VOLTAGE_H] = static_cast<uint8_t>((voltage >> 8) & 0xFF);
        pkg_data[_BMS_CURRENT_L] = static_cast<uint8_t>(current & 0xFF);
        pkg_data[_BMS_CURRENT_H] = static_cast<uint8_t>((current >> 8) & 0xFF);
        pkg_data[_BMS_PERCENT_L] = static_cast<uint8_t>(percentage & 0xFF);
        pkg_data[_BMS_PERCENT_H] = static_cast<uint8_t>((percentage >> 8) & 0xFF);
        pkg_data[_BMS_STATUS_] = static_cast<uint8_t>(batt_status & 0xFF);

        //Serial.printf("BMS No Update - Volt: %.1f V, Current: %.1f A, SOC: %.1f %%\n", fBattVolt, fBattCurrent, fBattSOC);
    }
}

void control_task()
{
    // static bool emer_flag = true;

    const float K = 0.5;

    uint64_t start_time = millis();
    uint8_t result;
    int16_t buff;
    float current_rpm_left = 0.0;
    float current_rpm_right = 0.0;
    static uint32_t LedControl = millis();

    if ((millis() - prev_cmd_time > 200) || stop || emer_state || virtual_emer_state)
    {
        cmd_vel.linear_x = 0.0;
        cmd_vel.linear_y = 0.0;
        cmd_vel.angular_z = 0.0;
        //digitalWrite(LED_STATUS, 0);
    }
    else
    {
        if ((millis() - LedControl) > 500)
        {
            digitalWrite(LED_STATUS, !digitalRead(LED_STATUS)); // For control task
            // Serial5.printf("ROS comm start.\n");
            LedControl = millis();
        }
    }

    //Serial5.printf("Time usege1 : %d\n", millis() - start_time);

    //-------- Calculate smooth velocity -------------

    // vel.linear_x = K * vel_old.linear_x + (1 - K) * cmd_vel.linear_x;
    // vel.linear_y = K * vel_old.linear_y + (1 - K) * cmd_vel.linear_y;

    // vel_old.linear_x = vel.linear_x;
    // vel_old.linear_y = vel.linear_y;
    //-----------------------------------------------

    Kinematics::rpm req_rpm = kinematics.getRPM(
        cmd_vel.linear_x,
        cmd_vel.linear_y,
        // vel.linear_x, 
        // vel.linear_y,
        cmd_vel.angular_z);

    
    if (emer_state || virtual_emer_state)
    {
        if(!emer_flag)
        {
            //eMR_SetTargetVelocity(0, DIR_NEG, 0, DIR_POS);
            // for (int i = 0; i < sizeof(pkg_data); i++)
            // {
            //     pkg_data[i] = 0;
            // }
        }
        emer_flag = true;
        // Serial.println("Emer ON");
        
    }
    else
    {

        if (emer_flag)
        {
            static unsigned long emer_recovery_start = 0;
            if (emer_recovery_start == 0) {
                emer_recovery_start = millis();
                // Serial.println("Emer OFF - Waiting for drive init...");
            }

            if (millis() - emer_recovery_start >= 7000) {
                // Serial.println("Drive Init Complete");
                eMR_CANOpen_Init();
                eMR_SetTargetVelocity(0, DIR_NEG, 0, DIR_POS);
                // Serial.println("eMR CANopen Init. eMR motor ");
                
                emer_flag = false;
                emer_recovery_start = 0; // Reset for next time
            }
            // Else: still waiting, do nothing (non-blocking)
        }
        else
        {
            float percentPWM1 = 0.0, percentPWM2 = 0.0;

            

            //------------- Calculate & Set Target RPM ----------
            //percentPWM1 = req_rpm.motor1 * 100 / MaxVelocity;
            //percentPWM2 = req_rpm.motor2 * 100 / MaxVelocity;
            percentPWM1 = req_rpm.motor1 * 100 / MOTOR_MAX_RPM;
            percentPWM2 = req_rpm.motor2 * 100 / MOTOR_MAX_RPM;

            //Serial5.printf("req_rpm.motor1: %f -- req_rpm.motor1: %f -- percentPWM1: %f -- percentPWM2: %f\n", req_rpm.motor1 , req_rpm.motor2, percentPWM1, percentPWM2);

            // eMR_SetTargetVelocity(percentPWM1, DIR_POS, percentPWM2, DIR_NEG);
            eMR_SetTargetVelocity(percentPWM2, DIR_NEG, percentPWM1, DIR_POS);
        }
    }


    //------------  Get Current RPM --------------------
    eMR_ReadActualVelocity2();
    // fault_monitor_task();

    current_rpm_right = v.velocity1/30;
    current_rpm_left = -1*v.velocity2 /30;

    Kinematics::velocities current_vel = kinematics.getVelocities(
        current_rpm_left,
        current_rpm_right,
        0,
        0);

    // Serial5.print("Actual RPM1 : ");
    // Serial5.print(current_rpm_right);
    // Serial5.print("   ");
    // Serial5.print("Actual RPM2 : ");
    // Serial5.print(current_rpm_left);

    // Serial5.print("   ");
    // Serial5.print("Vel_x: ");
    // Serial5.print(current_vel.linear_x);
    // Serial5.print("   ");
    // Serial5.print("ang_z: ");
    // Serial5.println(current_vel.angular_z);

    int16_t Vx = static_cast<int16_t>(current_vel.linear_x * 1000);
    int16_t Vy = static_cast<int16_t>(current_vel.linear_y * 1000);
    int16_t Wz = static_cast<int16_t>(current_vel.angular_z * 1000);

    pkg_data[_ODOM_VX_L] = static_cast<uint8_t>(Vx & 0xFF);
    pkg_data[_ODOM_VX_H] = static_cast<uint8_t>((Vx >> 8) & 0xFF);
    pkg_data[_ODOM_VY_L] = static_cast<uint8_t>(Vy & 0xFF);
    pkg_data[_ODOM_VY_H] = static_cast<uint8_t>((Vy >> 8) & 0xFF);
    pkg_data[_ODOM_WZ_L] = static_cast<uint8_t>(Wz & 0xFF);
    pkg_data[_ODOM_WZ_H] = static_cast<uint8_t>((Wz >> 8) & 0xFF);
    //pkg_data[_ODOM_READY_] = 1;
    
}

static uint8_t sensor_state = 0;
void sensor_module_task()
{



    int32_t buff;
    uint8_t alarm_mode;
    uint8_t led_mode;

    const uint8_t ultarsonic_max_range = 20;  // cm unit
        // Serial.printf("Sensor State: %d\n", sensor_state);
        // Serial.printf("Range Left: %d -- Range Center: %d -- Range Right: %d -- Cliff distance : %d\n", range_left, range_center, range_right, cliff);
        // Serial.printf("IR Charge State : %d\n", buff);
        // Serial.println("-------------------------------------------");
     switch(sensor_state) {
        case 0:  // Read Left
            if (Ultrasonics_L.readHoldingRegisters(0, 2) == Ultrasonics_L.ku8MBSuccess) {
                buff = Ultrasonics_L.getResponseBuffer(0);
                if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
                range_left = buff * 10;
                pkg_data[_RANGER_LEFT_L] = static_cast<uint8_t>(range_left & 0xFF);
                pkg_data[_RANGER_LEFT_H] = static_cast<uint8_t>((range_left >> 8) & 0xFF);
            } else {
                range_left = 99;
            }
            sensor_state = 1;
            break;
        case 1:  // Read Right
            if (Ultrasonics_R.readHoldingRegisters(0, 2) == Ultrasonics_R.ku8MBSuccess) {
                buff = Ultrasonics_R.getResponseBuffer(0);
                if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
                range_right = buff * 10;
                pkg_data[_RANGER_RIGHT_L] = static_cast<uint8_t>(range_right & 0xFF);
                pkg_data[_RANGER_RIGHT_H] = static_cast<uint8_t>((range_right >> 8) & 0xFF);
            }else {
                range_right = 99;
            }
            sensor_state = 2;
            break;
        case 2:  // Read Center
            if (Ultrasonics_C.readHoldingRegisters(0, 2) == Ultrasonics_C.ku8MBSuccess) {
                buff = Ultrasonics_C.getResponseBuffer(0);
                if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
                range_center = buff * 10;
                pkg_data[_RANGER_CENTER_L] = static_cast<uint8_t>(range_center & 0xFF);
                pkg_data[_RANGER_CENTER_H] = static_cast<uint8_t>((range_center >> 8) & 0xFF);
            }else {
                range_center = 99;
            }
            sensor_state = 3;
            break;
        case 3:  // Read Cliff
            if (Cliff_Sensor.readHoldingRegisters(0, 2) == Cliff_Sensor.ku8MBSuccess) {
                buff = Cliff_Sensor.getResponseBuffer(1);
                cliff = buff;
            }else {
                cliff = 9999;
            }
            sensor_state = 4;
            break;
        case 4:  // Read IR Charge
            if(IR_Charge_State.readHoldingRegisters(0, 1) == IR_Charge_State.ku8MBSuccess) {
                buff = IR_Charge_State.getResponseBuffer(0);
                pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
            }else 
            {
                buff = 99;
                pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
            }
            sensor_state = 0;
            break;


    }
//     static uint32_t fault_monitor = millis();

//     // uint64_t start_time = millis();

//     if (Ultrasonics_L.readHoldingRegisters(0, 2) == Ultrasonics_L.ku8MBSuccess)
//     {
//         buff = Ultrasonics_L.getResponseBuffer(0);// * 0.01; // coe = 0.01  => cm ==> m, addr = 0
//         if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
//         range_left = buff*10;// *0.01* 1000;

//         pkg_data[_RANGER_LEFT_L] = static_cast<uint8_t>(range_left & 0xFF);
//         pkg_data[_RANGER_LEFT_H] = static_cast<uint8_t>((range_left >> 8) & 0xFF);
        
//         // Serial5.printf("Range Letf : %d\n", buff);
//     }
//     else
//     {
//         if (DEBUG)
//             Serial5.println("Read range left error");
//     }
//     // cooperative sleep to allow other Threads to run
//     //threads.delay(5);

//     if (Ultrasonics_R.readHoldingRegisters(0, 2) == Ultrasonics_R.ku8MBSuccess)
//     {
//         buff = Ultrasonics_R.getResponseBuffer(0);// * 0.01; // coe = 0.01 => cm ==> m, addr = 0
//         if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
//         range_right = buff*10;// *0.01* 1000;

//         pkg_data[_RANGER_RIGHT_L] = static_cast<uint8_t>(range_right & 0xFF);
//         pkg_data[_RANGER_RIGHT_H] = static_cast<uint8_t>((range_right >> 8) & 0xFF);

//         // Serial5.printf("Range Right : %d\n", buff);
//     }
//     else
//     {
//         if (DEBUG)
//             Serial5.println("Read range right error");
//     }
//     // cooperative sleep to allow other Threads to run
//     // threads.delay(5);

//     if (Ultrasonics_C.readHoldingRegisters(0, 2) == Ultrasonics_C.ku8MBSuccess)
//     {
//         buff = Ultrasonics_C.getResponseBuffer(0);//*0.01; // coe = 0.01  => cm ==> m, addr = 0
//         if(buff > ultarsonic_max_range) buff = ultarsonic_max_range;
//         range_center = buff*10;// *0.01* 1000;
//         pkg_data[_RANGER_CENTER_L] = static_cast<uint8_t>(range_center & 0xFF);
//         pkg_data[_RANGER_CENTER_H] = static_cast<uint8_t>((range_center >> 8) & 0xFF);

//         // Serial5.printf("Range Center : %d\n", buff);
//     }
//     else
//     {
//         if (DEBUG)
//             Serial5.println("Read range center error");
//     }
//     // cooperative sleep to allow other Threads to run
//     // threads.delay(5);

//     if (Cliff_Sensor.readHoldingRegisters(0, 2) == Cliff_Sensor.ku8MBSuccess)
//     {
//         buff = Cliff_Sensor.getResponseBuffer(1);//* 0.001; // coe = 0.001, addr = 1
//         cliff = buff;// * 1000;

//         // Serial5.printf("Cliff distance : %d\n", buff);
//     }
//     else
//     {
//         if (DEBUG)
//             Serial5.println("Read range center error");
//     }
//     // cooperative sleep to allow other Threads to run
//     threads.delay(5);
//    // Serial5.printf("Range Letf: %d -- Range Center: %d -- Range Right: %d -- Cliff distance : %d\n", range_left, range_center, range_right, cliff);
//     //pkg_data[_RANGER_READY_] = 1;
//     uint8_t result;
//     if(IR_Charge_State.readHoldingRegisters(0, 1) == IR_Charge_State.ku8MBSuccess)
//     {
//         buff = IR_Charge_State.getResponseBuffer(0); // addr = 0
//         pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
//         // Serial5.printf("IR Charge State : %d\n", buff);
//     }
//     else
//     {
//         buff = 99;
//         pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
//         //Serial5.println("Read IR Charge State error");
//     }
   
}

void safety_task()
{
    // while (true)
    // {
    emer_state = !mcp.digitalRead(8);
    bumper_state = !mcp.digitalRead(9) || !mcp.digitalRead(10);

    if (cliff > 100.0)  
        //cliff_state = true; // 50 mm. for flat surface
        cliff_state =false; //hardcode to test without cliff sensor
    else
        cliff_state = false;

    if (bumper_state || cliff_state)
        stop = true;
    else
        stop = false;


    //pkg_data[_SAFETY_READY_] = 1;
 //Serial5.printf("bumper_state: %d  --- emer_state: %d --- cliff: %d\n", bumper_state, emer_state, cliff);

}

void fault_monitor_task()
{
    uint16_t status_word = 0;
    uint8_t error_reg = 0;
    
    if (eMR_ReadStatusWord(dual_axis, &status_word, 10)) {

         // If fault detected, read error register
        if (status_word & 0x08) {
            if (eMR_ReadErrorRegister(dual_axis, &error_reg, 10)) {
                // print_error_register_debug(error_reg);
                if (error_reg & 0x01) {
                    pkg_data[_MTR_FAULT_STATE_] = 1; // Generic Error
                } else if (error_reg & 0x02) {
                    pkg_data[_MTR_FAULT_STATE_] = 2; // Current Error
                } else if (error_reg & 0x04) {
                    pkg_data[_MTR_FAULT_STATE_] = 3; // Voltage Error
                } else if (error_reg & 0x08) {
                    pkg_data[_MTR_FAULT_STATE_] = 4; // Temperature Error
                } else if (error_reg & 0x10) {
                    pkg_data[_MTR_FAULT_STATE_] = 5; // Device Hardware Error
                } else if (error_reg & 0x20) {
                    pkg_data[_MTR_FAULT_STATE_] = 6; // Device Software Error
                } else if (error_reg & 0x40) {
                    pkg_data[_MTR_FAULT_STATE_] = 7; // Additional Modules Error
                } else if (error_reg & 0x80) {
                    pkg_data[_MTR_FAULT_STATE_] = 8; // Monitoring Error
                } 
            } else {
                // Serial.println("Failed to read error register");
                pkg_data[_MTR_FAULT_STATE_] = 9; // Indicate read failure Unknow error
            }
        }
        else {
            pkg_data[_MTR_FAULT_STATE_] = 0; // No fault
            
        }


    } else {
        // Serial.println("Failed to read status");
        pkg_data[_MTR_FAULT_STATE_] = 99; // Indicate read failure
        
    }
}

void setup()
{
    pinMode(LED, OUTPUT);
    pinMode(LED_STATUS, OUTPUT);
    pinMode(LED_RUN, OUTPUT);
    digitalWrite(LED_BUILTIN, 0);
    digitalWrite(LED_RUN, 0);    // For ROS Communication
    digitalWrite(LED_STATUS, 0); // For control task
    // pinMode(MAX485_RE, OUTPUT);
    // pinMode(MAX485_DE, OUTPUT);

    //-------------- I2C I/O  Init---------------------
    mcp.begin_I2C(0x21);
    for (uint8_t i = 0; i < 16; i++)
    {
        if (i > 7)
            mcp.pinMode(i, INPUT_PULLUP);
        else
        {
            mcp.pinMode(i, OUTPUT);
        }
    }
    mcp.digitalWrite(7, HIGH);
    mcp.digitalWrite(6, HIGH);
    mcp.digitalWrite(5, HIGH);
    delay(3000);
    //-------------
    Serial.begin(460800);
    

    Serial5.begin(115200);

    //-----------  CAN Init ----------------------
    v.velocity1 = 0;
    v.velocity2 = 0;

    eMR_CANOpen_Begin();
    eMR_CANOpen_Init();
    eMR_SetTargetVelocity(0, DIR_NEG, 0, DIR_POS);
    //------------ BMS Init ---------------------
    BMS_SERIAL.begin(9600);
    BMS_SERIAL.setTimeout(50);
    delay(1000);
    //------------ Clifff sensor & Ultrasonics   Init -----------------------
    SENSORS_SERIAL.begin(115200);
    SENSORS_SERIAL.setTimeout(10);
    Cliff_Sensor.begin(1, SENSORS_SERIAL);
    Ultrasonics_L.begin(2, SENSORS_SERIAL);
    Ultrasonics_R.begin(3, SENSORS_SERIAL);
    Led_Modele.begin(5, SENSORS_SERIAL);
    Ultrasonics_C.begin(7, SENSORS_SERIAL);
    IR_Charge_State.begin(9, SENSORS_SERIAL);
    //------------ IMU Init --------------------------------
    JY61P.startIIC();
    JY61P.caliIMU();

   
    vel_old.linear_x = 0;
    vel_old.linear_y = 0;

    for (int i = 0; i < sizeof(pkg_data); i++)
    {
        pkg_data[i] = 0;
    }

    master_time = imu_update_time = control_update_time = send_data_time = safety_time = bms_update_time = sensor_update_time = millis();
    setup_loop_frequency();
}
// Simple loop frequency counter
uint32_t loop_count = 0;
uint32_t last_report_time = 0;
const uint32_t REPORT_INTERVAL = 1000;  // Report every 1 second

void setup_loop_frequency() {
    last_report_time = millis();
}

void monitor_loop_frequency() {
    loop_count++;
    
    if (millis() - last_report_time >= REPORT_INTERVAL) {
        Serial.printf("Loop Frequency: %u Hz\n", loop_count);
        loop_count = 0;
        last_report_time = millis();
    }
}
void loop()
{
    //char incomingChar = 0;
    static uint32_t LedActivity = millis();
    static uint32_t fault_monitor = millis();
    //static uint16_t count = 0;
    //static uint32_t prev_time = 0;
    //monitor_loop_frequency();

    receive_data_task();
    poll_can_bus();

    // pkg_data[_ODOM_VX_L] = 0;
    // pkg_data[_ODOM_VX_H] = 0;
    // pkg_data[_ODOM_VY_L] = 0;
    // pkg_data[_ODOM_VY_H] = 0;
    // pkg_data[_ODOM_WZ_L] = 0;
    // pkg_data[_ODOM_WZ_H] = 0;

    if ((millis() - control_update_time) > control_interval)
    {
        //uint32_t current_time = millis();
        control_task();
        //Serial5.printf("control: %d\n", millis()- control_update_time);
        control_update_time = millis();
        //Serial5.printf("control: %d\n", millis()- current_time);
        
    }

    if ((millis() - safety_time) > safety_interval)
    {
        //uint32_t current_time = millis();
        safety_task();
        safety_time = millis();
        //Serial5.printf("safety: %d\n", millis() - current_time);
    }

    if ((millis() - sensor_update_time) > sensor_interval)
    {
        //uint32_t current_time = millis();
        sensor_module_task();
        sensor_update_time = millis();
        //Serial5.printf("sensor: %d\n", millis()- current_time);
    }  

    if ((millis() - imu_update_time) > imu_interval)
    {
        //uint32_t current_time = millis();
        imu_update_task();
        imu_update_time = millis();        
        //Serial5.printf("imu: %d\n", millis()- current_time);
    }

    if ((millis() - bms_update_time) > bms_interval)
    {
        //uint32_t current_time = millis();
        bms_task();
        bms_update_time = millis();
        //Serial5.printf("bms: %d\n", millis()- current_time);
        
    }    

    if ((millis() - send_data_time) > send_data_interval)
    {
        //uint32_t current_time = millis();
        send_data_task();
        send_data_time = millis();
        //Serial5.printf("send_data: %d\n", millis()- current_time);
    }

    if (millis() - LedActivity > 200)
    {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        LedActivity = millis();
    }
    //Serial5.println("DEBUG MODE");

    // if(millis() - fault_monitor > 30000)
    // {
    //     fault_monitor_task();
    //     fault_monitor = millis();
    // }


}
