#define USE_SMR_CONFIG

#include <Arduino.h>
#include <ModbusMaster.h>
#include <Adafruit_MCP23X17.h>

#include <stdio.h>
#include <vector>
#include "math.h"

#include "config.h"
#include "kinematics.h"
#include "JY61P.h"
#include "motor_driver.cpp"
#include "bms.h"
// #include "can_driver.h"
// --- Encoder reader for CANopen position value (0x6064) ---
class EncoderReader {
public:
    EncoderReader(uint32_t cpr, float wheel_diameter)
        : CPR(cpr),
          wheel_circumference(M_PI * wheel_diameter),
          prev_count(0),
          position_m(0.0f),
          initialized(false) {}

    float update(uint32_t raw_count) {
        if (!initialized) {
            prev_count = raw_count;
            initialized = true;
            return position_m;
        }

        int64_t delta = (int64_t)raw_count - (int64_t)prev_count;
        // handle 32-bit rollover
        if (delta > (int64_t)(UINT32_MAX / 2)) delta -= (int64_t)UINT32_MAX;
        else if (delta < -(int64_t)(UINT32_MAX / 2)) delta += (int64_t)UINT32_MAX;

        prev_count = raw_count;

        float delta_revs = (float)delta / (float)CPR;
        float delta_m = delta_revs * wheel_circumference;
        position_m += delta_m;
        return position_m; // cumulative displacement [m]
    }

    float getPosition() const { return position_m; }

private:
    const uint32_t CPR;
    const float wheel_circumference;
    uint32_t prev_count;
    float position_m;
    bool initialized;
};

// Encoder readers for left/right drives
EncoderReader left_encoder(16384, 0.165f);
EncoderReader right_encoder(16384, 0.165f);

static constexpr float WHEEL_CPR = 16384.0f;
// static constexpr float WHEEL_DIAMETER = 0.165f;   // meters
static constexpr float WHEELBASE = 0.333f;        // meters between wheels

// Track last positions for delta calculation
float last_left_pos_m  = 0.0f;
float last_right_pos_m = 0.0f;
// Robot pose (for debugging if you want)
float x=0.0f, y=0.0f, theta=0.0f;

// ---------------- Debug Flags ----------------
#define DEBUG false
#define DEBUG_IMU false
#define DEBUG_MOTOR false
#define DEBUG_MOTION false
#define DEBUG_RANGE false
#define DEBUG_ODOM false
#define DEBUG_SEND false
#define DEBUG_RECEIVE false
#define DEBUG_OLED false
#define DEBUG_SAFTY false
#define DEBUG_BATT false

// ---------------- Protocol -------------------
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

// ---------------- Pkg data frame -----------------
#define _PKG_LEN    43  // Total bytes: header + host + size + payload + checksum

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
#define _IMU_ACCX_H    10
#define _IMU_ACCY_L    11
#define _IMU_ACCY_H    12
#define _IMU_ACCZ_L    13
#define _IMU_ACCZ_H    14

// --- ODOM (6 bytes) ---
#define _ODOM_VX_L     15
#define _ODOM_VX_H     16
#define _ODOM_VY_L     17
#define _ODOM_VY_H     18
#define _ODOM_WZ_L     19
#define _ODOM_WZ_H     20

#define _ODOM_X_L     36
#define _ODOM_X_H     37
#define _ODOM_Y_L     38
#define _ODOM_Y_H     39
#define _ODOM_Z_L     40
#define _ODOM_Z_H     41

// --- RANGE (6 bytes) ---
#define _RANGER_RIGHT_L   21
#define _RANGER_RIGHT_H   22
#define _RANGER_CENTER_L  23
#define _RANGER_CENTER_H  24
#define _RANGER_LEFT_L    25
#define _RANGER_LEFT_H    26

// --- SAFETY (1 byte) ---
#define _SAFETY_       27   // bits: xxxx xyzw (emergency, bumper, cliff etc)

// --- BMS (7 bytes for your platform) ---
#define _BMS_VOLTAGE_L   28
#define _BMS_VOLTAGE_H   29
#define _BMS_CURRENT_L   30
#define _BMS_CURRENT_H   31
#define _BMS_PERCENT_L   32
#define _BMS_PERCENT_H   33
#define _BMS_STATUS_     34
#define _IR_CHARGE_STATE_ 35
#define _MTR_DRIVE_STATE_ 36
#define _MTR_FAULT_STATE_ 37
#define _RESERVED2_        38
#define _RESERVED3_        39
#define _RESERVED4_        40
#define _RESERVED5_        41 

#define _CHK_SUM_        42   // Final byte
//--------------------------------------------------

uint8_t pkg_data[_PKG_LEN];   // Global buffer

// ---------------- Hardware -------------------
#define MAX485_DE 4
#define MAX485_RE 5
#define TEENSY_RS485_DIR_PIN 22

#define SENSORS_SERIAL Serial2
#define BMS_SERIAL Serial1
#define ULTARSONICS_SERIAL Serial2

// ---------------- Devices --------------------
ModbusMaster Sensor_module;
ModbusMaster Ultrasonics_1; 
ModbusMaster Ultrasonics_2; 
ModbusMaster Ultrasonics_3; 
ModbusMaster IR_Charge_state;

int RS485_DE = 4;
int RS485_RE = 5;

// ---------------- Sensors State --------------
int16_t range_left;
int16_t range_center;
int16_t range_right;
uint16_t cliff;

uint8_t imu2send[12];
uint8_t odom2send[6];
uint8_t batt2send[7];
uint8_t range2send[6];
bool imu_ready;
bool odom_ready;
bool batt_ready;
bool range_ready;
static bool emer_flag = true;

// ---------------- Control --------------------
Kinematics kinematics(
    Kinematics::SMR_BASE,
    MOTOR_MAX_RPM,
    MAX_RPM_RATIO,
    MOTOR_OPERATING_VOLTAGE,
    MOTOR_POWER_MAX_VOLTAGE,
    0.165f,
    0.333f);

Kinematics::velocities cmd_vel;

unsigned long prev_cmd_time = 0;

Adafruit_MCP23X17 mcp;

bool cliff_state, bumper_state, emer_state,virtual_emer_state = false, stop;
bool connection_failed;

static const int RX_BUF_SIZE = 128;  // safe static buffer size

// ---------------- Task Timing ----------------
const unsigned int recv_interval    = 1;   // check UART almost every cycle
const unsigned int control_interval = 10;  // 33 Hz motor update
const unsigned int send_interval    = 10;  // 50 Hz odometry feedback
const unsigned int imu_interval     = 10;  // 25 Hz IMU
const unsigned int bms_interval     = 1000;// 1 Hz BMS
const unsigned int sensor_interval  = 100; //50;  // 20 Hz rangers
const unsigned int safety_interval  = 20;  // 50 Hz for safety

unsigned long imu_time = 0;
unsigned long control_time = 0;
unsigned long bms_time = 0;
unsigned long sensor_time = 0;
unsigned long safety_time = 0;
unsigned long send_time = 0;
unsigned long recv_time = 0;

// --- Non-blocking parser state ---
#define RX_BUFFER_MAX 128

static uint8_t rx_buffer[RX_BUFFER_MAX];
static uint8_t rx_index = 0;
static uint8_t rx_expected_length = 0;

// --- BMS state machine ---
static uint8_t bms_buf[50];
static uint8_t bms_index = 0;
static unsigned long last_bms_request = 0;
const unsigned int bms_request_interval = 1000; // every 1s

// ---------------- LED status --------------------
int LED = 13;        // LED status TeensyMicromod
int LED_RUN = 32;    // G9 - Teensy pin 32, MicroMod pad 65
int LED_STATUS = 26; // G8 - Teensy pin 26, MicroMod pad 67
uint8_t led_mode_prev;
uint8_t alarm_mode_prev;
uint8_t alarm_mode = 0;
uint8_t led_mode = 0;
uint8_t range_limit = 100;  // 200 = 20cm



// Latest BMS floats filled when valid packet received
uint8_t batt_status = 0;
bool update_batt_ = false;
//charge state
uint8_t charge_state = 0; // 0: not charging, 1: charging, 2: charge done
// ---------------- Parse Data ----------------
void parse_data(uint8_t func, uint8_t *data, uint8_t data_len)
{
    if (func == FUNC_MOTION)
    {
        int16_t packed_v_x = (data[1] << 8) | data[0];
        int16_t packed_v_y = (data[3] << 8) | data[2];
        int16_t packed_w_z = (data[5] << 8) | data[4];

        cmd_vel.linear_x = packed_v_x / 1000.0;
        cmd_vel.linear_y = packed_v_y / 1000.0;
        cmd_vel.angular_z = packed_w_z / 1000.0;

        prev_cmd_time = millis();

        if (DEBUG_MOTION)
        {
            Serial.printf("Vx: %f, Vy: %f, Wz: %f\n", cmd_vel.linear_x, cmd_vel.linear_y, cmd_vel.angular_z);
        }
    }
    if (func == FUNC_CHARGE)
    {
        if (data_len >= 1)
        {
            uint8_t result;
            charge_state = data[0];
             //Serial5.print("Charge state: ");
             //Serial5.println(charge_state);
            
            if (charge_state == 20)
            {
                result = IR_Charge_state.writeSingleRegister(1, 20); // Robot is ready to charge
                if (result == IR_Charge_state.ku8MBSuccess)
                {
                    //Serial5.println("Sent: RobotReadyToCharge (20)");
                }else {
                //Serial5.println("Error sending state to robot");
                }


            }else if (charge_state == 22)
            {
                result = IR_Charge_state.writeSingleRegister(1, 22); // Robot is charging
            
                if (result == IR_Charge_state.ku8MBSuccess)
                {
                    //Serial5.println("Sent: StopCharging (22)");
                }else {
                //Serial5.println("Error sending state to robot");
                }


            }
        }
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

    if(func == FUNC_MTR_DRIVE)
    {
        if (data_len >= 1)
        {
            uint8_t mtr_drive_state = data[0];
            // Serial5.print("MTR Drive State: ");
            // Serial5.println(mtr_drive_state);
            if(mtr_drive_state == 0)
            {
                // mcp.digitalWrite(3, HIGH);
                virtual_emer_state = true;
                mcp.digitalWrite(7, LOW);
                // mcp.digitalWrite(6, LOW);
                // mcp.digitalWrite(5, LOW);
                mcp.digitalWrite(4, LOW);


                // mcp.digitalWrite(8, HIGH);
                // mcp.digitalWrite(9, HIGH);
                // delay(10);
            }
            else if(mtr_drive_state == 1)
            {
                // mcp.digitalWrite(3, LOW);
                mcp.digitalWrite(7, HIGH);
                // mcp.digitalWrite(6, HIGH);
                // mcp.digitalWrite(5, HIGH);
                mcp.digitalWrite(4, HIGH);
                virtual_emer_state = false;
                //emer_flag = true;

                

                // mcp.digitalWrite(8, LOW);
                // mcp.digitalWrite(9, LOW);
                // delay(10);
            }
        }
    }
}

// ---------------- Receive Data Task ----------
void recive_data_task(void *parameter = nullptr)
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

// ---------------- Send Data ------------------
void send_data(uint8_t FUNC_TYPE, uint8_t *param, size_t param_len)
{
    const size_t MAX_PACKET_SIZE = 64;
    uint8_t cmd[MAX_PACKET_SIZE];

    size_t cmd_len = param_len + 5; 
    if (cmd_len > MAX_PACKET_SIZE) return; // prevent overflow

    cmd[0] = HEAD;
    cmd[1] = HOST_ID;
    cmd[2] = cmd_len - 1;
    cmd[3] = FUNC_TYPE;
    memcpy(&cmd[4], param, param_len);

    uint8_t checksum = 0;
    for (size_t i = 0; i < cmd_len - 1; i++) checksum += cmd[i];
    cmd[cmd_len - 1] = checksum & 0xFF;

    Serial.write(cmd, cmd_len);

    if (DEBUG_SEND)
    {
        Serial5.print("Sent [FUNC "); Serial5.print(FUNC_TYPE, HEX); Serial5.print("]: ");
        for (size_t i=0;i<cmd_len;i++) { Serial5.print(cmd[i]); Serial5.print(" "); }
        Serial5.println();
    }
}

// ---------------- IMU Task -------------------
void imu_update_task(void *arg = nullptr)
{
    float imu_gyro_dps[3] = {
        (JY61P.getGyroX() / 180) * 3.14,
        (JY61P.getGyroY() / 180) * 3.14,
        (JY61P.getGyroZ() / 180) * 3.14
    };
    float imu_accel_g[3] = { JY61P.getAccX(), JY61P.getAccY(), JY61P.getAccZ() };

    int16_t roll  = (int16_t)(imu_gyro_dps[0] * 1000);
    int16_t pitch = (int16_t)(imu_gyro_dps[1] * 1000);
    int16_t yaw   = (int16_t)(imu_gyro_dps[2] * 1000);
    int16_t acc_x = (int16_t)(imu_accel_g[0] * 1000);
    int16_t acc_y = (int16_t)(imu_accel_g[1] * 1000);
    int16_t acc_z = (int16_t)(imu_accel_g[2] * 1000);

    pkg_data[_IMU_ROLL_L]  = roll & 0xFF;
    pkg_data[_IMU_ROLL_H]  = (roll >> 8) & 0xFF;
    pkg_data[_IMU_PITCH_L] = pitch & 0xFF;
    pkg_data[_IMU_PITCH_H] = (pitch >> 8) & 0xFF;
    pkg_data[_IMU_YAW_L]   = yaw & 0xFF;
    pkg_data[_IMU_YAW_H]   = (yaw >> 8) & 0xFF;
    pkg_data[_IMU_ACCX_L]  = acc_x & 0xFF;
    pkg_data[_IMU_ACCX_H]  = (acc_x >> 8) & 0xFF;
    pkg_data[_IMU_ACCY_L]  = acc_y & 0xFF;
    pkg_data[_IMU_ACCY_H]  = (acc_y >> 8) & 0xFF;
    pkg_data[_IMU_ACCZ_L]  = acc_z & 0xFF;
    pkg_data[_IMU_ACCZ_H]  = (acc_z >> 8) & 0xFF;
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

        pkg_data[_BMS_VOLTAGE_L] = voltage & 0xFF;
        pkg_data[_BMS_VOLTAGE_H] = (voltage >> 8) & 0xFF;

        pkg_data[_BMS_CURRENT_L] = current & 0xFF;
        pkg_data[_BMS_CURRENT_H] = (current >> 8) & 0xFF;

        pkg_data[_BMS_PERCENT_L] = percentage & 0xFF;
        pkg_data[_BMS_PERCENT_H] = (percentage >> 8) & 0xFF;

        pkg_data[_BMS_STATUS_]   = batt_status & 0xFF;

        update_batt_ = false; // clear flag until next packet
    }
}

volatile int32_t g_left_motor_position = 0;
volatile int32_t g_right_motor_position = 0;

void process_can_messages() {
  // Check if a new message is available from your CAN library

    if (msg.id == 0x380 + Motor_ID1) { // Assuming Motor_ID1 is the RIGHT motor
      g_right_motor_position =
          (int32_t)(((uint32_t)msg.buf[2])       |
                    ((uint32_t)msg.buf[3] << 8)  |
                    ((uint32_t)msg.buf[4] << 16) |
                    ((uint32_t)msg.buf[5] << 24));

    } else if (msg.id == 0x380 + Motor_ID2) { // Assuming Motor_ID2 is the LEFT motor
      g_left_motor_position =
          (int32_t)(((uint32_t)msg.buf[2])       |
                    ((uint32_t)msg.buf[3] << 8)  |
                    ((uint32_t)msg.buf[4] << 16) |
                    ((uint32_t)msg.buf[5] << 24));
    }else {
      // Unknown message ID, ignore or handle as needed
        Serial5.print("Unknown CAN ID: ");
        Serial5.println(msg.id, HEX);
    }
    // You can add more 'else if' blocks here to handle other messages
  
}
// ---------------- ODOM/Control ---------------
void update_odometry() {
    static unsigned long last_time = millis();
    unsigned long now = millis();
    //float left_pos_m, right_pos_m;
    uint8_t status;
    float dt = (now - last_time) / 1000.0f;
    if (dt <= 0) dt = 0.02f; // fallback
    last_time = now;
    
    // Read encoder positions
    // // Left motor
    // // eMR.cobid = TSDO_COBID + axis2;
    // eMR.cobid = DKE_TPDO3 + axis2; // use TPDO3 for less jitter
    // // CANOpen_ReadActualPosObj_Safe(&eMR);
    // CANOpen_ReadActualPosObj_PDO(&eMR); // use PDO read for less jitter
    // //Serial.print("Left pos: ");
    // //Serial.println((uint32_t)eMR.ActualPosition);
    // float left_pos_m = left_encoder.update((uint32_t)eMR.ActualPosition);
    // delay(1);
    // Right motor

    
    eMR_Read_data_base(); // read data for both motors
    //eMR_Read_data(&eMR_left,&eMR_right); // read data for both motors
    float left_pos_m = left_encoder.update((uint32_t)eMR_left.ActualPosition);
    float right_pos_m = right_encoder.update((uint32_t)eMR_right.ActualPosition);

    // Serial5.print("L: ");
    // Serial5.print(left_pos_m, 4);
    // Serial5.print(" R: ");
    // Serial5.print(right_pos_m, 4);
    
    // eMR.cobid = DKE_TPDO3 + axis1;
    // // CANOpen_ReadActualPosObj_Safe(&eMR);
    // CANOpen_ReadActualPosObj_PDO(&eMR); // use PDO read for less jitter
    // float right_pos_m = right_encoder.update((uint32_t)eMR.ActualPosition);
    // //delay(1);
    // eMR.cobid = DKE_TPDO3 + axis2; // use TPDO3 for less jitter
    // CANOpen_ReadActualPosObj_PDO(&eMR); // use PDO read for less jitter
    // float left_pos_m = left_encoder.update((uint32_t)eMR.ActualPosition);

    
    // Serial5.print("L: ");
    // Serial5.print(left_pos_m, 4);
    // Serial5.print(" R: ");
    // Serial5.println(right_pos_m, 4);
    
    // Calculate position deltas
    float d_left = left_pos_m - last_left_pos_m;
    float d_right = (right_pos_m - last_right_pos_m) * (-1); // right wheel is mounted in opposite direction
    last_left_pos_m = left_pos_m;
    last_right_pos_m = right_pos_m;
    
    // Calculate linear and angular velocities
    float v = (d_left + d_right) / (2.0f * dt);          // m/s forward
    float w = (d_right - d_left) / (WHEELBASE * dt);     // rad/s yaw
    
    // Update robot pose
    float d_center = (d_left + d_right) / 2.0f;
    float d_theta  = (d_right - d_left) / WHEELBASE;   // WHEELBASE = 0.333m in config
    x += d_center * cos(theta + d_theta/2.0f);
    y += d_center * sin(theta + d_theta/2.0f);
    theta += d_theta;
    // Serial.print("X: "); Serial.print(x, 4);
    // Serial.print(" Y: "); Serial.print(y, 4);
    // Serial.print(" Th: "); Serial.println(theta, 4);
    
    // Pack into pkg_data (mm/s, mrad/s with ×1000 scaling)
    auto clamp16 = [](float x) -> int16_t {
        if (x > 32.767f) return 32767;
        if (x < -32.768f) return -32768;
        return (int16_t)(x * 1000);
    };
    
    int16_t Vx = clamp16(v);
    int16_t Vy = 0;          // no lateral motion in diff drive
    int16_t Wz = clamp16(w);
    //Serial5.print(" Vx: "); Serial5.println(Vx/1000.0f);
    

    pkg_data[_ODOM_VX_L] = Vx & 0xFF;
    pkg_data[_ODOM_VX_H] = (Vx >> 8) & 0xFF;
    pkg_data[_ODOM_VY_L] = Vy & 0xFF;
    pkg_data[_ODOM_VY_H] = (Vy >> 8) & 0xFF;
    pkg_data[_ODOM_WZ_L] = Wz & 0xFF;
    pkg_data[_ODOM_WZ_H] = (Wz >> 8) & 0xFF;
    pkg_data[_ODOM_X_L] = ((int16_t)(x*1000)) & 0xFF;
    pkg_data[_ODOM_X_H] = (((int16_t)(x*1000)) >> 8) & 0xFF;
    pkg_data[_ODOM_Y_L] = ((int16_t)(y*1000)) & 0xFF;
    pkg_data[_ODOM_Y_H] = (((int16_t)(y*1000)) >> 8) & 0xFF;
    pkg_data[_ODOM_Z_L] = ((int16_t)(theta*1000)) & 0xFF;
    pkg_data[_ODOM_Z_H] = (((int16_t)(theta*1000)) >> 8) & 0xFF;
    
    odom_ready = true;
}

void control_task(void *arg = nullptr) {
    // static bool emer_flag = false;
    static uint32_t LedControl = millis();
    
    // Handle command timeout
    if ((millis() - prev_cmd_time > 100) || stop || emer_state || virtual_emer_state) {
        cmd_vel.linear_x = 0.0;
        cmd_vel.linear_y = 0.0;
        cmd_vel.angular_z = 0.0;
    }else {
        //if (millis() - LedControl > 200) { digitalWrite(LED_STATUS, !digitalRead(LED_STATUS)); LedControl = millis(); }
    }
    
    // Calculate required RPM
    Kinematics::rpm req_rpm = kinematics.getRPM(cmd_vel.linear_x, cmd_vel.linear_y, cmd_vel.angular_z);
    
    // Handle emergency state
    // Handle emergency state
    static uint8_t recovery_state = 0;
    static unsigned long recovery_start_time = 0;

    if (emer_state || virtual_emer_state) {
        if (!emer_flag) {
            // Emergency state entered - could add motor shutdown code here if needed
        }
        emer_flag = true;
        recovery_state = 0;
    }
    else {
        if (emer_flag) {
            // Recovering from emergency state
            switch (recovery_state) {
                case 0: // Start wait timer
                    recovery_start_time = millis();
                    recovery_state = 1;
                   // Serial5.println("drive reset: state1");
                    break;
                case 1: // Wait for 7 seconds
                     if (millis() - recovery_start_time > 1000) {
                   // Serial5.println("drive reset: state2");
                        recovery_state = 2;
                    }
                    break;
                case 2: // Init motors
                    // can1.begin();
                    // can1.setBaudRate(500000);
                    // can1.setMBFilter(ACCEPT_ALL);
                    // can1.distribute();
                    CANOpen_eMR_Init();
                    //Serial5.print("drive reset complete");
                    // delay(500);
                   // eMRCanSpeedCntrl(0.0, DIR_NEG, axis2);
                   // eMRCanSpeedCntrl(0.0, DIR_POS, axis1);
                    emer_flag = false;
                    recovery_state = 0;
                    break;
            }
        }
        else {
            // Normal operation: send target velocity
            eMRCanSpeedCntrl(req_rpm.motor1, DIR_NEG, axis2); //left motor
            //delay(1);
            eMRCanSpeedCntrl(req_rpm.motor2, DIR_POS, axis1); //right motor
            //delay(1);
        }
    }
    //Sync_message(&eMR); // Send SYNC after setting velocity
    // Update odometry
    //process_can_messages();
    Sync_message();  // se  nd SYNC message
    update_odometry();
}

static uint8_t sensor_state = 0;
// ---------------- Sensor Task -------------------
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
            if (Ultrasonics_1.readHoldingRegisters(0, 2) == Ultrasonics_1.ku8MBSuccess) {
                buff = Ultrasonics_1.getResponseBuffer(0);
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
            if (Ultrasonics_2.readHoldingRegisters(0, 2) == Ultrasonics_2.ku8MBSuccess) {
                buff = Ultrasonics_2.getResponseBuffer(0);
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
            if (Ultrasonics_3.readHoldingRegisters(0, 2) == Ultrasonics_3.ku8MBSuccess) {
                buff = Ultrasonics_3.getResponseBuffer(0);
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
            if (Sensor_module.readHoldingRegisters(0, 2) == Sensor_module.ku8MBSuccess) {
                buff = Sensor_module.getResponseBuffer(1);
                cliff = buff;
            }else {
                cliff = 9999;
            }
            sensor_state = 4;
            break;
        case 4:  // Read IR Charge
            if(IR_Charge_state.readHoldingRegisters(0, 1) == IR_Charge_state.ku8MBSuccess) {
                buff = IR_Charge_state.getResponseBuffer(0);
                pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
            }else 
            {
                buff = 99;
                pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
            }
            sensor_state = 3; // skip ultrasonic reading for next cycle
            break;


    }
    // int32_t buff;
    // if (Ultrasonics_1.readHoldingRegisters(0x0101, 1) == Ultrasonics_1.ku8MBSuccess)
    //     {range_left = Ultrasonics_1.getResponseBuffer(0);

    //         if (range_left < 0 ) range_left = 0;
    //         if (range_left > 3000 ) range_left = 3000;
            
        
    //     }
    // else {range_left = 9999;}
    // delay(5);
    // if (Ultrasonics_2.readHoldingRegisters(0x0101, 1) == Ultrasonics_2.ku8MBSuccess)
    //    { 
    //     range_center = Ultrasonics_2.getResponseBuffer(0);
    //         if (range_center < 0 ) range_center = 0;
    //         if (range_center > 3000 ) range_center = 3000;
    
    // }
    // // else {range_center = 9999;}
    // // delay(5);
    // if (Ultrasonics_3.readHoldingRegisters(0x0101, 1) == Ultrasonics_3.ku8MBSuccess)
    // {
    //     range_right = Ultrasonics_3.getResponseBuffer(0);
    //         if (range_right < 0 ) range_right = 0;
    //         if (range_right > 3000 ) range_right = 3000;
    // }
    //     else range_right = 9999;
    // // delay(5);
    // if (Sensor_module.readHoldingRegisters(0x00, 1) == Sensor_module.ku8MBSuccess)
    //     cliff = Sensor_module.getResponseBuffer(0);
    // delay(5);
    // //Serial5.printf("Range L: %d  C: %d  R: %d  Cliff: %d\n", range_left, range_center, range_right, cliff);

    // uint8_t result;
    // if(IR_Charge_state.readHoldingRegisters(0x00, 1) == IR_Charge_state.ku8MBSuccess)
    // {
    //     buff = IR_Charge_state.getResponseBuffer(0); // addr = 0
        
    //  //   Serial5.printf("IR Charge State : %d\n", buff);
    //     pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
        
    // }
    // else
    // {
    //     buff = 99;
    //     pkg_data[_IR_CHARGE_STATE_] = static_cast<uint8_t>(buff & 0xFF);
    //     //Serial5.println("READ IR ERROR");
    //     //Serial5.println("Read IR Charge State error");
    // }
    // // range_center =1000;

    // pkg_data[_RANGER_LEFT_L]   = range_left & 0xFF;
    // pkg_data[_RANGER_LEFT_H]   = (range_left >> 8) & 0xFF;
    // pkg_data[_RANGER_CENTER_L] = range_center & 0xFF;
    // pkg_data[_RANGER_CENTER_H] = (range_center >> 8) & 0xFF;
    // pkg_data[_RANGER_RIGHT_L]  = range_right & 0xFF;
    // pkg_data[_RANGER_RIGHT_H]  = (range_right >> 8) & 0xFF;
    // pkg_data[_RANGER_LEFT_L]   = 300 & 0xFF;
    // pkg_data[_RANGER_LEFT_H]   = (300 >> 8) & 0xFF;
    // pkg_data[_RANGER_CENTER_L] = 300 & 0xFF;
    // pkg_data[_RANGER_CENTER_H] = (300 >> 8) & 0xFF;
    // pkg_data[_RANGER_RIGHT_L]  = 300 & 0xFF;
    // pkg_data[_RANGER_RIGHT_H]  = (300 >> 8) & 0xFF;
    

    /////// ALARM & LED MODE ///////
    range_ready = true;

    bool A = (range_left < range_limit);
    bool B = (range_center < range_limit);
    bool C = (range_right < range_limit);

    if (stop || emer_state || connection_failed)
        A = B = C = true;

    alarm_mode = (static_cast<uint8_t>(A) << 2) |
                (static_cast<uint8_t>(B) << 1) |
                (static_cast<uint8_t>(C));
    
    Sensor_module.writeSingleRegister(1, alarm_mode);

    if (cmd_vel.linear_x == 0 && cmd_vel.angular_z == 0)
        {
            led_mode = 0;
        }
    else if (cmd_vel.linear_x != 0 && cmd_vel.angular_z == 0)
        {
            led_mode = 1;
        }
    else if (((cmd_vel.angular_z < -0.05) && (cmd_vel.linear_x >= 0)) || ((cmd_vel.angular_z > 0.05) && (cmd_vel.linear_x < 0)))
        {
            led_mode = 2;
        }
    else if (((cmd_vel.angular_z > 0.05) && (cmd_vel.linear_x >= 0)) || ((cmd_vel.angular_z < -0.05) && (cmd_vel.linear_x < 0)))
        {
            led_mode = 3;
        }

    if (led_mode != led_mode_prev)
    {
        if (DEBUG)
            Serial.println(led_mode);
        // Serial.println(led_mode);
        Sensor_module.writeSingleRegister(2, led_mode);
        // delay(10);
    }

    led_mode_prev = led_mode;
    alarm_mode_prev = alarm_mode;
    A = B = C = false;   

}

// ---------------- Safety ---------------------
void safty_task()
{
    emer_state = !mcp.digitalRead(8);
    //Serial.println(emer_state);
    bumper_state = !mcp.digitalRead(9) || !mcp.digitalRead(10);
    cliff_state = (cliff > 200 && cliff < 5000);
    stop = (bumper_state || cliff_state);
    uint8_t safety = 0;
    safety |= (emer_state   ? 0x04 : 0);
    safety |= (bumper_state ? 0x02 : 0);
    safety |= (cliff_state  ? 0x01 : 0);
    pkg_data[_SAFETY_] = safety;
}

// ---------------- Send Task ------------------
void send_data_task()
{
    pkg_data[_HEADER]   = HEAD;
    pkg_data[_HOST_ID]  = HOST_ID;
    pkg_data[_PKG_SIZE] = _PKG_LEN - 1; // exclude checksum

    // Compute checksum
    uint8_t checksum = 0;
    for (uint8_t i = 0; i < _PKG_LEN - 1; i++) {
        checksum += pkg_data[i];
    }
    pkg_data[_CHK_SUM_] = checksum & 0xFF;

    // Send entire frame
    Serial.write(pkg_data, _PKG_LEN);

    if (DEBUG_SEND) {
        Serial5.println("Sent pkg_data:");
        for (int i=0; i<_PKG_LEN; i++) {
            Serial5.print(pkg_data[i]);
            Serial5.print(" ");
        }
        Serial5.println();
    }
}


// ---------------- Setup ----------------------
void setup()
{
    pinMode(LED, OUTPUT);
    pinMode(LED_STATUS, OUTPUT);
    pinMode(LED_RUN, OUTPUT);
    pinMode(MAX485_RE, OUTPUT);
    pinMode(MAX485_DE, OUTPUT);

    mcp.begin_I2C(0x21);
    for (uint8_t i = 0; i < 16; i++)
        mcp.pinMode(i, (i > 7) ? INPUT_PULLUP : OUTPUT);
    mcp.digitalWrite(7, HIGH);
    // mcp.digitalWrite(6, LOW);
    // mcp.digitalWrite(5, LOW);
    mcp.digitalWrite(4, HIGH);

    Serial.begin(460800);
    Serial5.begin(115200);
    //Serial5.println('start serial 5');

    can1.begin();
    can1.setBaudRate(500000);
    can1.setMBFilter(ACCEPT_ALL);
    can1.distribute();
    CANOpen_eMR_Init();


    SENSORS_SERIAL.begin(115200);
    Ultrasonics_1.begin(1, ULTARSONICS_SERIAL);
    Ultrasonics_2.begin(2, ULTARSONICS_SERIAL);
    Ultrasonics_3.begin(3, ULTARSONICS_SERIAL);
    Sensor_module.begin(5, SENSORS_SERIAL);
    IR_Charge_state.begin(9, SENSORS_SERIAL);

    BMS_SERIAL.begin(9600);

    JY61P.startIIC();
    JY61P.caliIMU();
    // sendTimer.begin(sendTimerISR, 20000);  // 20ms interval
}

// Simple loop frequency counter
uint32_t loop_count = 0;
uint32_t last_report_time = 0;
const uint32_t REPORT_INTERVAL = 1000;  // Report every 1 second
void monitor_loop_frequency() {
    loop_count++;
    
    if (millis() - last_report_time >= REPORT_INTERVAL) {
        Serial5.printf("Loop Frequency: %u Hz\n", loop_count);
        loop_count = 0;
        last_report_time = millis();
    }
}
// ---------------- Superloop ------------------
void loop()
{
    unsigned long now = millis();
    static uint32_t LedActivity = millis();
    //monitor_loop_frequency();

    recive_data_task(); 

    
    if (now - control_time > control_interval) { control_task(); control_time = now; }
    if (now - imu_time > imu_interval) { imu_update_task(); imu_time = now; }
    if (now - bms_time > bms_interval) { bms_task(); bms_time = now; }
    if (now - sensor_time > sensor_interval) { sensor_module_task(); sensor_time = now; }
    if (now - safety_time > safety_interval) { safty_task(); safety_time = now; }
    if (now - send_time > send_interval) { send_data_task(); send_time = now; }
    if (now - LedActivity > 200 ){digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN)); LedActivity = now; }
    
}