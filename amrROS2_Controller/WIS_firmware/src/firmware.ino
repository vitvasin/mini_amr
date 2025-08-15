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
#define _PKG_LEN 36 //  param_len + 3(for _header, _host_id, _pkg_size) + 1(for _chk_sum)    == 36

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

#define _CHK_SUM_ 35

//--------------------------------------

ModbusMaster Led_Modele;
ModbusMaster Cliff_Sensor;
ModbusMaster Ultrasonics_L; // Left
ModbusMaster Ultrasonics_C; // Center
ModbusMaster Ultrasonics_R; // Right

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
const unsigned int imu_interval = 45, control_interval = 20, bms_interval = 200, sensor_interval = 50, safety_interval = 50, send_data_interval = 10, receive_data_interval;

unsigned char pkg_data[_PKG_LEN];

Adafruit_MCP23X17 mcp;
bool mcp_input[8];
bool mcp_out_put[8];

bool cliff_state, bumper_state, emer_state, stop, ack;
bool connection_failed;

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

        //Serial5.printf("Vx: %f ---  Vy: %f  ---  Wz: %f\n", cmd_vel.linear_x, cmd_vel.linear_y, cmd_vel.angular_z);
    }
    else if (func == FUNC_STATUS)
    {
        static uint32_t LedRosComm = millis();
        if ((millis() - LedRosComm) > 1000)
        {
            digitalWrite(LED_RUN, !digitalRead(LED_RUN)); // For ROS Communication
            // Serial5.printf("ROS comm start.\n");
            LedRosComm = millis();
        }
    }
    else
    {
        if (DEBUG_RECEIVE)
        {
            Serial5.println("Out of provided function");
        }
    }
}

// void recive_data_task(void *parameter)
void receive_data_task()
{

    uint8_t header;
    uint8_t device_id;
    uint8_t len;
    uint8_t func;
    uint8_t data_len;
    uint8_t data_to_mem = 0;
    uint8_t value;
    uint8_t rx_check_num;
    uint8_t check_sum;

    uint8_t *data = (uint8_t *)malloc(RX_BUF_SIZE);
    uint8_t *buffer = (uint8_t *)malloc(RX_BUF_SIZE + 1);

    while (Serial.available() > 0)
    {

        header = Serial.read();

        if (header == HEAD)
        {
            if (DEBUG_RECEIVE)
            {
                Serial5.println("--------------New Data--------------");
                Serial5.println("Correct header");
            }
            device_id = Serial.read();

            if (device_id == DEVICE_ID)
            {

                len = Serial.read();
                func = Serial.read();

                check_sum = header + device_id + len + func;
                data_len = len - 4;
                data_to_mem = data_len;
                memset(data, 0, RX_BUF_SIZE);

                while (data_to_mem > 0)
                {
                    uint8_t index = data_len - data_to_mem;
                    data[index] = Serial.read();
                    check_sum += data[index];

                    data_to_mem--;
                }

                rx_check_num = Serial.read();

                if ((check_sum & 0xFF) == rx_check_num)
                {
                    if (DEBUG_RECEIVE)
                    {
                        Serial5.println("Data Recived");
                    }
                    threads.delay(1);
                    parse_data(func, data, data_len);
                }
                else
                {
                    if (DEBUG_RECEIVE)
                    {
                        Serial5.println("Check sum error");
                    }
                }

                if (DEBUG_RECEIVE)
                {
                    Serial5.print("Device_id:  ");
                    Serial5.println(device_id);
                    Serial5.print("Data_range:  ");
                    Serial5.println(len);
                    Serial5.print("Function:  ");
                    Serial5.println(func);
                    for (uint8_t i = 0; i < data_len; i++)
                    {
                        Serial5.print("Data ");
                        Serial5.print(i);
                        Serial5.print(": ");
                        Serial5.println(data[i]);
                    }
                    Serial5.print("Rx_check:  ");
                    Serial5.println(rx_check_num);
                    Serial5.print("Check sum:  ");
                    Serial5.println(check_sum & 0xFF);
                }
            }
        }
    }
    // threads.delay(25);
    //}
    free(data);
    free(buffer);
}

void send_data_task()
{
    //memset(pkg_data, 0, sizeof(pkg_data));

    pkg_data[_HEADER] = HEAD;
    pkg_data[_HOST_ID] = HOST_ID;
    pkg_data[_PKG_SIZE] = sizeof(pkg_data) - 1; // 36 - 1 // not include chk_sum  err.

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

    // uint64_t end_time = millis();
    // uint32_t dt = end_time - start_time;
}

void bms_task()
{
    int16_t voltage = 0, current = 0, percentage = 0;
    uint8_t batt_status = 0;

    if (RequestDataFromBMD(VOLT_AMP_CMD) == 1)
    {
        voltage = static_cast<int16_t>(fBattVolt * 100);
        current = static_cast<int16_t>(fBattCurrent * 100);
        percentage = static_cast<int16_t>(fBattSOC * 100);

        if (fBattSOC >= 100)
            batt_status = 4; // FULL
        else if (fBattCurrent > 0)
            batt_status = 1; // CHARGIGN
        else if (fBattCurrent < 0)
            batt_status = 2; // DISCHARGIGN
        else
            batt_status = 0; // UNKNOWN

        pkg_data[_BMS_VOLTAGE_L] = static_cast<uint8_t>(voltage & 0xFF);
        pkg_data[_BMS_VOLTAGE_H] = static_cast<uint8_t>((voltage >> 8) & 0xFF);
        pkg_data[_BMS_CURRENT_L] = static_cast<uint8_t>(current & 0xFF);
        pkg_data[_BMS_CURRENT_H] = static_cast<uint8_t>((current >> 8) & 0xFF);
        pkg_data[_BMS_PERCENT_L] = static_cast<uint8_t>(percentage & 0xFF);
        pkg_data[_BMS_PERCENT_H] = static_cast<uint8_t>((percentage >> 8) & 0xFF);
        pkg_data[_BMS_STATUS_] = static_cast<uint8_t>(batt_status & 0xFF);

        // Serial5.printf("voltage    : %d\n", voltage);
        // Serial5.printf("current    : %d\n", current);
        // Serial5.printf("percentage : %d\n", percentage);
    }
}

void control_task()
{
    static bool emer_flag = true;

    const float K = 0.5;

    uint64_t start_time = millis();
    uint8_t result;
    int16_t buff;
    float current_rpm_left = 0.0;
    float current_rpm_right = 0.0;
    static uint32_t LedControl = millis();

    if ((millis() - prev_cmd_time > 200) || stop || emer_state)
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

    
    if (emer_state)
    {
        emer_flag = true;
        // Serial.println("Emer ON");
    }
    else
    {

        if (emer_flag)
        {
            // Serial.println("Emer OFF");
            eMR_CANOpen_Init();
            // Serial.println("eMR CANopen Init. eMR motor ");
            delay(3000);
            emer_flag = false;
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

   // Serial5.printf("Time usege2 : %d\n", millis() - start_time);

    //------------  Get Current RPM --------------------
    eMR_ReadActualVelocity2();

   // Serial5.printf("Time usege3 : %d\n", millis() - start_time);
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
    
}

void sensor_module_task()
{
    float buff;
    uint8_t alarm_mode;
    uint8_t led_mode;

    // uint64_t start_time = millis();

    if (Ultrasonics_L.readHoldingRegisters(0, 2) == Ultrasonics_L.ku8MBSuccess)
    {
        buff = Ultrasonics_L.getResponseBuffer(0);//* 0.01; // coe = 0.01, addr = 0
        range_left = buff;

        pkg_data[_RANGER_LEFT_L] = static_cast<uint8_t>(range_left & 0xFF);
        pkg_data[_RANGER_LEFT_H] = static_cast<uint8_t>((range_left >> 8) & 0xFF);

        //Serial5.printf("Range Letf : %f\n", buff);
    }
    else
    {
        if (DEBUG)
            Serial5.println("Read range left error");
    }
    delay(10);

    if (Ultrasonics_R.readHoldingRegisters(0, 2) == Ultrasonics_R.ku8MBSuccess)
    {
        buff = Ultrasonics_R.getResponseBuffer(0);//* 0.01; // coe = 0.01, addr = 0
        range_right = buff;

        pkg_data[_RANGER_RIGHT_L] = static_cast<uint8_t>(range_right & 0xFF);
        pkg_data[_RANGER_RIGHT_H] = static_cast<uint8_t>((range_right >> 8) & 0xFF);

        // Serial5.printf("Range Right : %f\n", buff);
    }
    else
    {
        if (DEBUG)
            Serial5.println("Read range right error");
    }
    delay(10);

    if (Ultrasonics_C.readHoldingRegisters(0, 2) == Ultrasonics_C.ku8MBSuccess)
    {
        buff = Ultrasonics_C.getResponseBuffer(0);//*0.01; // coe = 0.01, addr = 0
        range_center = buff;
        pkg_data[_RANGER_CENTER_L] = static_cast<uint8_t>(range_center & 0xFF);
        pkg_data[_RANGER_CENTER_H] = static_cast<uint8_t>((range_center >> 8) & 0xFF);

        // Serial5.printf("Range Center : %f\n", buff);
    }
    else
    {
        if (DEBUG)
            Serial5.println("Read range center error");
    }
    delay(10);

    if (Cliff_Sensor.readHoldingRegisters(0, 2) == Cliff_Sensor.ku8MBSuccess)
    {
        buff = Cliff_Sensor.getResponseBuffer(1);//* 0.001; // coe = 0.001, addr = 1
        cliff = buff;

        //Serial5.printf("Cliff distance : %f\n", buff);
    }
    else
    {
        if (DEBUG)
            Serial5.println("Read range center error");
    }
    delay(10);

   
}

void safety_task()
{
    // while (true)
    // {
    emer_state = !mcp.digitalRead(8);
    bumper_state = !mcp.digitalRead(9) || !mcp.digitalRead(10);

    if (cliff > 50.0)  
        cliff_state = true; // 50 mm. for flat surface
    else
        cliff_state = false;

    if (bumper_state || cliff_state)
        stop = true;
    else
        stop = false;

 //Serial5.printf("bumper_state: %d  --- emer_state: %d --- cliff: %d\n", bumper_state, emer_state, cliff);

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
    delay(3000);
    //-------------
    Serial.begin(115200);

    Serial5.begin(115200);

    //-----------  CAN Init ----------------------
    v.velocity1 = 0;
    v.velocity2 = 0;

    eMR_CANOpen_Begin();
    eMR_CANOpen_Init();

    //------------ BMS Init ---------------------
    BMS_SERIAL.begin(9600);
    BMS_SERIAL.setTimeout(30);

    //------------ Clifff sensor & Ultrasonics   Init -----------------------
    SENSORS_SERIAL.begin(115200);
    SENSORS_SERIAL.setTimeout(10);
    Cliff_Sensor.begin(1, SENSORS_SERIAL);
    Ultrasonics_L.begin(3, SENSORS_SERIAL);
    Ultrasonics_R.begin(2, SENSORS_SERIAL);
    Led_Modele.begin(5, SENSORS_SERIAL);
    Ultrasonics_C.begin(7, SENSORS_SERIAL);
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
}

void loop()
{
    //char incomingChar = 0;
    static uint32_t LedActivity = millis();
    //static uint16_t count = 0;
    //static uint32_t prev_time = 0;

    receive_data_task();

    if ((millis() - safety_time) > safety_interval)
    {
        safety_task();
        safety_time = millis();
        
        // uint32_t current_time = millis();
        // Serial5.printf("Time usege for safety_task(): %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if ((millis() - sensor_update_time) > sensor_interval)
    {
        //sensor_module_task();
        sensor_update_time = millis();
        // uint32_t current_time = millis();
        // Serial5.printf("Time usege for sensor_module_task(): %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if ((millis() - control_update_time) > control_interval)
    {
        //uint32_t prev_time = millis();

        control_task();
        control_update_time = millis();

        //Serial5.printf("Time usege for control_task();: %d\n", millis()- prev_time);
        // uint32_t current_time = millis();
        //Serial5.printf("Time usege for control_task();: %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if ((millis() - imu_update_time) > imu_interval)
    {
        imu_update_task();
        imu_update_time = millis();
        
        // uint32_t current_time = millis();
        // Serial5.printf("Time usege for imu_update_task(): %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if ((millis() - bms_update_time) > bms_interval)
    {
        bms_task();
        bms_update_time = millis();

        // uint32_t current_time = millis();
        // Serial5.printf("Time usege for bms_task(): %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if ((millis() - send_data_time) > send_data_interval)
    {
        send_data_task();
        send_data_time = millis();

        // uint32_t current_time = millis();
        // Serial5.printf("Time usege for send_data_task(): %d\n", current_time - prev_time);
        // prev_time = current_time;
    }

    if (millis() - LedActivity > 200)
    {
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
        LedActivity = millis();
    }


}
