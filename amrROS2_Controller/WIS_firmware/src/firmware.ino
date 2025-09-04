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

// ---------------- Pkg data frame -----------------
#define _PKG_LEN    36  // Total bytes: header + host + size + payload + checksum

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

#define _CHK_SUM_        35   // Final byte
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

// ---------------- Control --------------------
Kinematics kinematics(
    Kinematics::SMR_BASE,
    MOTOR_MAX_RPM,
    MAX_RPM_RATIO,
    MOTOR_OPERATING_VOLTAGE,
    MOTOR_POWER_MAX_VOLTAGE,
    0.1651,
    0.333);

Kinematics::velocities cmd_vel;

unsigned long prev_cmd_time = 0;

Adafruit_MCP23X17 mcp;

bool cliff_state, bumper_state, emer_state, stop;
bool connection_failed;

static const int RX_BUF_SIZE = 128;  // safe static buffer size

// ---------------- Task Timing ----------------
const unsigned int recv_interval    = 1;   // check UART almost every cycle
const unsigned int control_interval = 10;  // 100 Hz motor update
const unsigned int send_interval    = 20;  // 50 Hz odometry feedback
const unsigned int imu_interval     = 40;  // 25 Hz IMU
const unsigned int bms_interval     = 1000;// 1 Hz BMS
const unsigned int sensor_interval  = 50;  // 20 Hz rangers
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

// ---------------- ODOM/Control ---------------
void control_task(void *arg = nullptr)
{
    static bool emer_flag = false;

    if ((millis() - prev_cmd_time > 100) || stop || emer_state)
    {
        cmd_vel.linear_x = 0.0;
        cmd_vel.linear_y = 0.0;
        cmd_vel.angular_z = 0.0;
    }

    Kinematics::rpm req_rpm = kinematics.getRPM(cmd_vel.linear_x, cmd_vel.linear_y, cmd_vel.angular_z);

    if (emer_state) { emer_flag = true; return; }
    else if (emer_flag) {
        // delay(1000); CANOpen_eMR_Init(); delay(3000);
        emer_flag = false;
    }

    eMRCanSpeedCntrl(req_rpm.motor1, DIR_NEG, axis2);
    eMRCanSpeedCntrl(req_rpm.motor2, DIR_POS, axis1);

    // Right motor
    eMR.cobid = TSDO_COBID + axis1;
    CANOpen_ReadActualVelocityObj(&eMR);
    float current_rpm_right = eMR.ActualVelocity * (3.75 / 16384) * 1.578 * (-1);

    // Left motor
    eMR.cobid = TSDO_COBID + axis2;
    CANOpen_ReadActualVelocityObj(&eMR);
    float current_rpm_left = eMR.ActualVelocity * (3.75 / 16384) * 1.578;

    Kinematics::velocities current_vel = kinematics.getVelocities(current_rpm_left, current_rpm_right, 0, 0);

    int16_t Vx = (int16_t)(current_vel.linear_x * 1000);
    int16_t Vy = (int16_t)(current_vel.linear_y * 1000);
    int16_t Wz = (int16_t)(current_vel.angular_z * 1000);

    pkg_data[_ODOM_VX_L] = Vx & 0xFF;
    pkg_data[_ODOM_VX_H] = (Vx >> 8) & 0xFF;
    pkg_data[_ODOM_VY_L] = Vy & 0xFF;
    pkg_data[_ODOM_VY_H] = (Vy >> 8) & 0xFF;
    pkg_data[_ODOM_WZ_L] = Wz & 0xFF;
    pkg_data[_ODOM_WZ_H] = (Wz >> 8) & 0xFF;
    odom_ready = true;
}

// ---------------- Sensors --------------------

void sensor_module_task()
{
    
    if (Ultrasonics_1.readHoldingRegisters(0x0101, 1) == Ultrasonics_1.ku8MBSuccess)
        range_left = Ultrasonics_1.getResponseBuffer(0);
    if (Ultrasonics_2.readHoldingRegisters(0x0101, 1) == Ultrasonics_2.ku8MBSuccess)
        range_center = Ultrasonics_2.getResponseBuffer(0);
    if (Ultrasonics_3.readHoldingRegisters(0x0101, 1) == Ultrasonics_3.ku8MBSuccess)
        range_right = Ultrasonics_3.getResponseBuffer(0);
    if (Sensor_module.readHoldingRegisters(0x00, 1) == Sensor_module.ku8MBSuccess)
        cliff = Sensor_module.getResponseBuffer(0);


    pkg_data[_RANGER_LEFT_L]   = range_left & 0xFF;
    pkg_data[_RANGER_LEFT_H]   = (range_left >> 8) & 0xFF;
    pkg_data[_RANGER_CENTER_L] = range_center & 0xFF;
    pkg_data[_RANGER_CENTER_H] = (range_center >> 8) & 0xFF;
    pkg_data[_RANGER_RIGHT_L]  = range_right & 0xFF;
    pkg_data[_RANGER_RIGHT_H]  = (range_right >> 8) & 0xFF;
    
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
        delay(10);
    }

    led_mode_prev = led_mode;
    alarm_mode_prev = alarm_mode;
    A = B = C = false;   

}

// ---------------- Safety ---------------------
void safty_task()
{
    emer_state = !mcp.digitalRead(8);
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

    Serial.begin(460800);
    Serial5.begin(115200);

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

    BMS_SERIAL.begin(9600);

    JY61P.startIIC();
    JY61P.caliIMU();
    // sendTimer.begin(sendTimerISR, 20000);  // 20ms interval
}

// ---------------- Superloop ------------------
void loop()
{
    unsigned long now = millis();
    
    recive_data_task(); 

    if (now - control_time > control_interval) { control_task(); control_time = now; }
    if (now - imu_time > imu_interval) { imu_update_task(); imu_time = now; }
    if (now - bms_time > bms_interval) { bms_task(); bms_time = now; }
    if (now - sensor_time > sensor_interval) { sensor_module_task(); sensor_time = now; }
    if (now - safety_time > safety_interval) { safty_task(); safety_time = now; }
    if (now - send_time > send_interval) { send_data_task(); send_time = now; }
    
}