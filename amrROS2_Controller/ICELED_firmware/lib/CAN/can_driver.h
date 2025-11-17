#ifndef CAN_DRIVER_H
#define CAN_DRIVER_H

#include <Arduino.h>

#define DLC                       8   


/* eMR COB-ID */
#define NMT_COBID                 0x000
#define SYNC_COBID                0x080
//#define EMERG_COBID               0x080
#define BOOTUP_COBID              0x700
#define TSDO_COBID                0x600 
#define SDO_COBID                0x600  
#define RSDO_COBID                0x580            
#define TPDO1_COBID               0x200     
#define TPDO2_COBID               0x300 
#define TPDO3_COBID               0x400 
#define TPDO4_COBID               0x500 
#define RPDO1_COBID               0x180       
#define RPDO2_COBID               0x280     
#define RPDO3_COBID               0x380     
#define RPDO4_COBID               0x480     

#define SDO_Expedited_1           0x2F
#define SDO_Expedited_2           0x2B
#define SDO_Expedited_3           0x27
#define SDO_Expedited_4           0x23
#define RSDO_Expedited_4          0x40
#define SDO_Error_Msg             0x80

/* eMR Network Management Command */
#define NMT_Operation             0x01            // Switch to the "Operational" state
#define NMT_Stop                  0x02            // Switch to the "Stop" state
#define NMT_Query                 0x03            // Query NMT state command
#define NMT_PreOperation          0x80            // Switch to the "Pre-Operational" state
#define NMT_Reset_Node            0x81            // Reset Node
#define NMT_Reset_communiction    0x82            // Reset Communication



#define ReceiveTimeOut            1000            // Maximum for waiting answer from eMR in milli second
#define Acceleration              1000//5000            // rpm/s^2 
#define Deceleration              1000//5000            // rpm/s^2 
#define MaxVelocity               3000             // for WIS : 160             // rpm/s      // maxspeed eMR motor hub
#define ProfileQuickDecel         10000           // rpm/s^2  

// CiA402 CANOpen eMR Object Dictionary 
#define Controlword_Obj           0x6040
#define Statusword_Obj            0x6041
#define HeartbeatTime_Obj         0x1017
#define OperationMode_Obj         0x6060
#define MotionProfileType_Obj     0x6086
#define TargetPosition_Obj        0x607A
#define DemandPosition_Obj        0x6062
#define TargetVelocity_Obj        0x60FF
#define DemandVelocity_Obj        0x606B
#define ProfileVelocity_Obj       0x6081
#define MaxProfileVelocity_Obj    0x607F
#define MaxMotorSpeed_Obj         0x6080
#define MaxGearInputSpeed_Obj     0x3003
#define MaxAcceleration_Obj       0x60C5
#define ProfileAcceleration_Obj   0x6083
#define ProfileDeceleration_Obj   0x6084
#define ActualPosition_Obj        0x6062
//#define ActualVelocity_Obj        0x606B                      // Maxon
#define ActualVelocity_Obj        0x6069                        // eMR Motor hub
#define PositionWindow_Obj        0x6067
#define SoftwarePositionLimit_Obj 0x607D
#define HomingMethod_Obj          0x6098
#define HomingSpeed_Obj           0x6099
#define HomingAcceleration_Obj    0x609A
#define HomeOffsetMove_Obj        0x30B1
#define HomePosition              0x30B0
#define HomingCurrentThreshold    0x30B2

/* eMR Statusword */
#define eMR_BIT15               0x8000          // bit code: position referenced to home position
#define eMR_BIT14               0x4000          // bit code: refresh cycle of power stage
#define eMR_BIT13               0x2000          // bit code: OpMode specific, some error
#define eMR_BIT12               0x1000          // bit code: OpMode specific
#define eMR_BIT11               0x0800          // bit code: NOT USED
#define eMR_BIT10               0x0400          // bit code: Target reached
#define eMR_BIT09               0x0200          // bit code: Remote (?)
#define eMR_BIT08               0x0100          // bit code: offset current measured (?)
#define eMR_BIT07               0x0080          // bit code: WARNING
#define eMR_BIT06               0x0040          // bit code: switch on disable
#define eMR_BIT05               0x0020          // bit code: quick stop
#define eMR_BIT04               0x0010          // bit code: voltage enabled
#define eMR_BIT03               0x0008          // bit code: FAULT
#define eMR_BIT02               0x0004          // bit code: operation enable
#define eMR_BIT01               0x0002          // bit code: switched on
#define eMR_BIT00               0x0001          // bit code: ready to switch on


#define PPM_MODE                  0x01             // Profile Position Mode
#define PVM_MODE                  0x03             // Profile Velocity Mode
#define PVT_MODE                  0x07             // Interpolated Position Mode
#define PM_MODE                   0xFF             // Position Mode (Electronic Gear)
#define VM_MODE                   0xFE             // Velocity Mode (Electronic Gear)
#define CM_MODE                   0xFD             // Current Mode
#define HM_MODE                   0x06             // Homing Mode

#define DIR_POS                   0
#define DIR_NEG                   1
#define STEP                      10

typedef enum axis_s{
    axis1 = 1,
    axis2 = 2,
    dual_axis = 1
}eMR_axis;
  
  
typedef struct eMR_s {
    uint32_t cobid;
    uint32_t bootup_ID1;
    uint32_t bootup_ID2;
    uint16_t cmd;
    uint8_t mode;
    bool Err_Flag;
    int32_t ProfileAcceleration;
    int32_t ProfileDeceleration;
    int32_t MaxProfileVelocity;
    int32_t TargetVelocity;
    int32_t TargetPosition;
    int32_t TargetTorque;
    int32_t ActualVelocity;
    int32_t ActualPosition;
    int32_t ActualTorque;
    int32_t StatusWord;
    int32_t ControlWord; 
  
}eMR_t;

typedef struct velocity_s{
    int32_t velocity1;
    int32_t velocity2;
}velocity_t;

extern eMR_t eMR;
extern velocity_t v;

bool CAN1_ReceiveFrame();
bool CAN1_SendFrame(uint32_t node_id, uint32_t data_size, uint8_t* data);
uint8_t eMR_Sync_message();
uint8_t eMR_NMT_SetOperational();
uint8_t eMR_NMT_SetPreoperational();
uint8_t eMR_NMT_SetStop();
uint8_t eMR_SetHeartbeatTime();
void eMR_CANOpen_Begin();
uint8_t eMR_CANOpen_Init();
uint8_t eMR_SetTargetVelocity(float percentPwm1,bool direction1, float percentPwm2, bool direction2);
uint8_t eMR_ReadActualVelocity();
void eMR_ReadActualVelocity2();

void print_statusword_debug();
bool eMR_ReadStatusWord(uint8_t node, uint16_t *out_status, uint32_t timeout_ms = 200);
bool eMR_ReadErrorRegister(uint8_t node, uint8_t *out_error, uint32_t timeout_ms = 200);

// void canSniff(const CAN_message_t &msg) ;

#endif