/*
  CANOpen source code (V1.0) for comunication with L12 dual BLDC driver eMR motor(TeensyMicromod).
  Created: 2024-03-01
  Modified: 2024-03-01
  By: Udom K.(NECTEC)
*/
//#include <ModbusMaster.h>
//#include <ModbusSlave.h>
// #include <JY901.h>
#include <Arduino.h>
#include <TimerOne.h>
//#include <ODriveArduino.h>
#include <stdio.h>
#include <FlexCAN_T4.h>           // https://github.com/tonton81/FlexCAN_T4
#include <TimerOne.h>

#define DLC                       8   


/* eMR COB-ID */
#define NMT_COBID                 0x000
#define EMERG_COBID               0x080
#define BOOTUP_COBID              0x700
#define TSDO_COBID                0x600   
#define RSDO_COBID                0x580            
#define TPDO1_COBID               0x200     
#define TPDO2_COBID               0x300 
#define TPDO3_COBID               0x400 
#define TPDO4_COBID               0x500 
#define RPDO1_COBID               0x180       
#define RPDO2_COBID               0x280     
#define RPDO3_COBID               0x380     
#define RPDO4_COBID               0x480     
#define SYNC_COBID                0x080
#define Motor_ID1                0x01
#define Motor_ID2                0x02
#define DKE_TPDO3          0x380
#define DKE_RPDO4          0x500


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



#define ReceiveTimeOut            100            // Maximum for waiting answer from eMR in milli second
#define Acceleration              5000            // rpm/s^2 
#define Deceleration              5000            // rpm/s^2 
#define MaxVelocity               160             // rpm/s      // maxspeed eMR motor hub
#define ProfileQuickDecel         10000           // rpm/s^2  




// CiA402 CANOpen eMR Object Dictionary 
#define Controlword_Obj           0x6040
#define Statusword_Obj            0x6041
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
#define ActualPosition_Obj        0x6064
//#define ActualVelocity_Obj        0x606B                      // Maxon
#define ActualVelocity_Obj        0x606C                        // eMR Motor hub 606C
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
  axis2 = 2
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
  // int32_t StatusWord;
  // int32_t ControlWord;
  uint16_t StatusWord;      // <-- FIXED (was int32_t)
  uint16_t ControlWord;     // <-- also 16-bit in CiA402

} eMR_t;


FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can1;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> can2;

CAN_message_t msg;
CAN_message_t revPACKET;
eMR_t eMR; 
eMR_t eMR_left;
eMR_t eMR_right;

uint16_t count = 0;

typedef struct velocity_s{
    int32_t velocity1;
    int32_t velocity2;
}velocity_t;

velocity_t v;
// int LED = 13;                 // LED status TeensyMicromod
// int LED_RUN = 32;             // G9 - Teensy pin 32, MicroMod pad 65
// int LED_STATUS = 26;          // G8 - Teensy pin 26, MicroMod pad 67
const int PWM0 = 3;
const int PWM1 = 2;
float motor_pwm1;
float motor_pwm2;


// bool CAN1_ReceiveFrame()
// {
//   unsigned long timer_out = millis();

//   for ( uint8_t i = 0; i <revPACKET.len ; i++ ) revPACKET.buf[i] = 0;

//   revPACKET.id = 0x000000;

//   while ((revPACKET.id == 0x000000) and (millis()-timer_out < ReceiveTimeOut))
//   {
//     if(can1.read(revPACKET))
//     { 

//       if (revPACKET.id == 0x000701) eMR.bootup_ID1 = 0x000701;
//       if (revPACKET.id == 0x000702) eMR.bootup_ID2 = 0x000702;
      
//     }
//   }

//   // Check CANOpen eMR Time out:
//   if (millis()-timer_out >= ReceiveTimeOut)
//   {
//     // Serial.println("CANOpen eMR respond time out.. ");
//     return false;
//   }

//   return true;
// }

bool CAN1_ReceiveFrame()
{
  unsigned long timer_out = millis();

  for ( uint8_t i = 0; i <msg.len ; i++ ) msg.buf[i] = 0;

  msg.id = 0x000000;

  while ((msg.id == 0x000000) and (millis()-timer_out < ReceiveTimeOut))
  {
    if(can1.read(msg))
    { 

      if (msg.id == 0x000701) eMR.bootup_ID1 = 0x000701;
      if (msg.id == 0x000702) eMR.bootup_ID2 = 0x000702;
      
    }
  }

  // Check CANOpen eMR Time out:
  if (millis()-timer_out >= ReceiveTimeOut)
  {
   // Serial5.println("CANOpen eMR respond time out.. ");
    return false;
  }

  return true;
}


bool CAN1_SendFrame(uint32_t node_id, uint32_t data_size, uint8_t* data)
{
  msg.id = node_id;
  msg.len = data_size;

  memcpy(&msg.buf[0], &data[0], data_size);
  can1.write(msg);  
  //delay(1);
  return true;
  //return CAN1_ReceiveFrame();
}
//////////////////  NMT command ///////////////////////
uint8_t NMT_SetOperational()
{
  uint8_t data[2];
  uint32_t node_id;
  
  node_id = NMT_COBID;
  data[0] = NMT_Operation ;                                             
  data[1] = 0x00 ;                                   //  NMT Command all network                             
  
  return CAN1_SendFrame(node_id, 0x02, data);
}
uint8_t NMT_SetPreoperational()
{
  uint8_t data[2];
  uint32_t node_id;
  
  node_id = NMT_COBID;
  data[0] = NMT_PreOperation;                                             
  data[1] = 0x00 ;                                   //  NMT Command all network                             
  
  return CAN1_SendFrame(node_id, 0x02, data);
}
//////////////////  NMT bootup check command ///////////////////////
uint8_t NMT_Bootup()
{
  uint8_t data[2];

//   Serial.println("eMR CANopen check bootup message.. "); 
                                    
  for ( uint8_t i = 0; i <5 ; i++ ) {

        data[0] = NMT_Query;                                               //  NMT Command                 
        data[1] = axis1 ;    
        CAN1_SendFrame(NMT_COBID, 0x02, data);      
        data[0] = NMT_Query;                                               //  NMT Command                 
        data[1] = axis2 ;    
        CAN1_SendFrame(NMT_COBID, 0x02, data);        
        
        if ((eMR.bootup_ID1==0x701) || (eMR.bootup_ID1==0x702))
        {
            // Serial.println("eMR CANopen Initial OK... "); 
            // Serial.print(" Found! eMR ID1: 0x"); Serial.println(eMR.bootup_ID1, HEX );
            // Serial.print(" Found! eMR ID2: 0x"); Serial.println(eMR.bootup_ID2, HEX );
            return 1;
        }
  }

    // Serial.println("Can't find eMR L12 dual driver motor in CANopen bus. "); 
  return 0;  
}
//////////////  SYNCHRONIZATION OBJECT (SYNC) /////////
////////// The Synchronization object is used to simultaneously validate the time of PDO data //////////
uint8_t Sync_message()
{
  uint8_t data[1];          
  uint32_t node_id;
  
  node_id = SYNC_COBID;
  data[0] = 0x00;                                                                

  return CAN1_SendFrame(node_id, 0x01, data);
}
////////////// Producer Heartbeat messsage /////////
uint8_t Heartbeat_CheckMessage(eMR_t *eMR)
{
  CAN_message_t msg;

  if(can1.read(msg))
  {   
    Serial.print("  ID: 0x"); Serial.print(msg.id, HEX );
    Serial.print(" DATA: ");
    Serial.print(msg.buf[0],HEX); Serial.print(" ");
    Serial.print("  TS: "); Serial.println(msg.timestamp);
  }
  return msg.buf[0];
}

uint8_t CANOpen_ResetFaults(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = eMR->cobid;
  data[0] = SDO_Expedited_2;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(Controlword_Obj & 0xFF);                // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((Controlword_Obj>>8) & 0xFF);           // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  data[4] = 0x80;                                             // SDO <DATA_Byte0>     Byte4
  data[5] = 0x00;                                             // SDO <DATA_Byte1>     Byte5
  data[6] = 0x00;                                             // SDO <DATA_Byte2>     Byte6
  data[7] = 0x00;                                             // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);                          // Test DLC = 6?
}
uint8_t CANOpen_Shutdown(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = eMR->cobid;
  data[0] = SDO_Expedited_2;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(Controlword_Obj & 0xFF);                // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((Controlword_Obj>>8) & 0xFF);           // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  data[4] = 0x06;                                             // SDO <DATA_Byte0>     Byte4
  data[5] = 0x00;                                             // SDO <DATA_Byte1>     Byte5
  data[6] = 0x00;                                             // SDO <DATA_Byte2>     Byte6
  data[7] = 0x00;                                             // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);                               // Test DLC = 6?
}  

uint8_t CANOpen_SetOperationMode(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = eMR->cobid;
  data[0] = SDO_Expedited_1;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(OperationMode_Obj & 0xFF);              // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((OperationMode_Obj>>8) & 0xFF);         // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  data[4] = eMR->mode;                                      // SDO <DATA_Byte0>     Byte4
  data[5] = 0x00;                                             // SDO <DATA_Byte1>     Byte5
  data[6] = 0x00;                                             // SDO <DATA_Byte2>     Byte6
  data[7] = 0x00;                                             // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);                               // Test DLC = 6?
}

uint8_t CANOpen_ReadStatusObj(eMR_t *eMR)
{
    uint8_t data[8];
    uint32_t node_id;
    node_id = eMR->cobid;

    // Request Statusword (0x6041:00)
    data[0] = RSDO_Expedited_4;                       // SDO <CMD>
    data[1] = (uint8_t)(Statusword_Obj & 0xFF);       // Index low
    data[2] = (uint8_t)((Statusword_Obj >> 8) & 0xFF);// Index high
    data[3] = 0x00;                                   // Subindex
    data[4] = 0x00;
    data[5] = 0x00;
    data[6] = 0x00;
    data[7] = 0x00;

    CAN1_SendFrame(node_id, DLC, data);

    // Response: Statusword is 16-bit (little-endian), located in buf[4]..buf[5]
    eMR->StatusWord = (uint16_t)(revPACKET.buf[4]) |
                      ((uint16_t)revPACKET.buf[5] << 8);

    return 0;
}

uint8_t CANOpen_ReadActualVelocityObj(eMR_t *eMR)
{
    uint8_t data[8];
    uint32_t node_id = eMR->cobid;

    // Build SDO request for ActualVelocity (0x6069:00)
    data[0] = RSDO_Expedited_4;  // 0x40 = upload request
    data[1] = (uint8_t)(ActualVelocity_Obj & 0xFF);
    data[2] = (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF);
    data[3] = 0x00;  // subIndex
    data[4] = data[5] = data[6] = data[7] = 0x00;

    // Send request
    // Serial5.println("Request ActualVelocity Obj..");

    CAN1_SendFrame(node_id, DLC, data);
    

        // Serial.print("  ID: 0x"); Serial.print(msg.id, HEX );
        // Serial.print(" DATA: ");
        // for ( uint8_t i = 0; i <msg.len ; i++ ) {
        //     Serial.print(msg.buf[i],HEX); Serial.print(" ");
        // }
        // Serial.print("  TS: "); Serial.println(msg.timestamp);
    
    if (msg.buf[1] == (uint8_t)(ActualVelocity_Obj & 0xFF) &&
        msg.buf[2] == (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF)) 
            {
                // Ignore strict revPACKET.buf[0], just parse
                eMR->ActualVelocity =
                    (int32_t)((uint32_t)msg.buf[4] |
                            ((uint32_t)msg.buf[5] << 8) |
                            ((uint32_t)msg.buf[6] << 16) |
                            ((uint32_t)msg.buf[7] << 24));
                return 1;
            }
            else if (msg.buf[0] == SDO_Error_Msg) // 0x80
            {
                eMR->Err_Flag = true;
                eMR->ActualVelocity = 0;
                return 0;  // error response
            }
     
    return 0;  // not valid
}

uint8_t CANOpen_ReadActualPosObj(eMR_t *eMR)
{
    uint8_t data[8];
    uint32_t node_id = eMR->cobid;

    // Build SDO request for ActualVelocity (0x6069:00)
    data[0] = RSDO_Expedited_4;  // 0x40 = upload request
    data[1] = (uint8_t)(ActualPosition_Obj & 0xFF);
    data[2] = (uint8_t)((ActualPosition_Obj >> 8) & 0xFF);
    data[3] = 0x00;  // subIndex
    data[4] = data[5] = data[6] = data[7] = 0x00;

    // Send request
    // Serial5.println("Request ActualVelocity Obj..");

    CAN1_SendFrame(node_id, DLC, data);
    

        // Serial.print("  ID: 0x"); Serial.print(msg.id, HEX );
        // Serial.print(" DATA: ");
        // for ( uint8_t i = 0; i <msg.len ; i++ ) {
        //     Serial.print(msg.buf[i],HEX); Serial.print(" ");
        // }
        // Serial.print("  TS: "); Serial.println(msg.timestamp);
    
    if (msg.buf[1] == (uint8_t)(ActualPosition_Obj & 0xFF) &&
        msg.buf[2] == (uint8_t)((ActualPosition_Obj >> 8) & 0xFF)) 
            {
                // Ignore strict revPACKET.buf[0], just parse
                eMR->ActualPosition =
                    (int32_t)((uint32_t)msg.buf[4] |
                            ((uint32_t)msg.buf[5] << 8) |
                            ((uint32_t)msg.buf[6] << 16) |
                            ((uint32_t)msg.buf[7] << 24));
                return 1;
            }
            else if (msg.buf[0] == SDO_Error_Msg) // 0x80
            {
                eMR->Err_Flag = true;
                eMR->ActualVelocity = 0;
                return 0;  // error response
            }
     
    return 0;  // not valid
}
bool CAN1_ReceiveFrameEx(CAN_message_t &rxMsg)
{
    unsigned long timer_out = millis();
    rxMsg.id = 0x000000;   // reset

    while ((rxMsg.id == 0x000000) && (millis() - timer_out < ReceiveTimeOut))
    {
        if (can1.read(rxMsg))  // read fills rxMsg
        {
            if (rxMsg.id == 0x000701) eMR.bootup_ID1 = 0x000701;
            if (rxMsg.id == 0x000702) eMR.bootup_ID2 = 0x000702;
            return true; // got a frame
        }
    }

    return false; // timeout
}

bool CAN1_SendFrameEx(uint32_t node_id, uint32_t data_size, uint8_t* data, CAN_message_t &rxMsg)
{
    CAN_message_t txMsg;
    txMsg.id = node_id;
    txMsg.len = data_size;
    memcpy(&txMsg.buf[0], &data[0], data_size);
    can1.write(txMsg);

    return CAN1_ReceiveFrameEx(rxMsg);
}

uint8_t CANOpen_ReadActualPosObj_Safe(eMR_t *eMR)
{
    uint8_t data[8] = {0}; // Initialize to zero
    CAN_message_t rxMsg;   // Use a LOCAL message struct, not the global 'msg'
    uint32_t node_id = eMR->cobid;
    uint32_t expected_response_id = RSDO_COBID + (node_id - TSDO_COBID); // e.g., 0x580 + node_id

    // Build SDO request for ActualPosition (0x6064:00)
    data[0] = RSDO_Expedited_4; // 0x40 = upload request
    data[1] = (uint8_t)(ActualPosition_Obj & 0xFF);
    data[2] = (uint8_t)((ActualPosition_Obj >> 8) & 0xFF);
    data[3] = 0x00; // subIndex

    // Send the request and wait for a response in our local rxMsg
    if (CAN1_SendFrameEx(node_id, DLC, data, rxMsg))
    {
        // --- ADDED VALIDATION ---
        // 1. Check if the response is from the correct CAN ID
        // 2. Check if it's a successful SDO Upload Response (cmd=0x43 for 4 bytes)
        // 3. Check if the object index matches our request
        if (rxMsg.id == expected_response_id &&
            rxMsg.buf[0] == 0x43 && 
            rxMsg.buf[1] == (uint8_t)(ActualPosition_Obj & 0xFF) &&
            rxMsg.buf[2] == (uint8_t)((ActualPosition_Obj >> 8) & 0xFF))
        {
            // The response is valid, parse the position data
            eMR->ActualPosition =
                (int32_t)(((uint32_t)rxMsg.buf[4])       |
                          ((uint32_t)rxMsg.buf[5] << 8)  |
                          ((uint32_t)rxMsg.buf[6] << 16) |
                          ((uint32_t)rxMsg.buf[7] << 24));
            return 1; // Success
        }
        // Check for an SDO Abort message from the correct node
        else if (rxMsg.id == expected_response_id && rxMsg.buf[0] == SDO_Error_Msg) // 0x80
        {
            eMR->Err_Flag = true;
            eMR->ActualPosition = 0; // CORRECTLY zero the position on error
            // Optionally, you could parse the abort code from rxMsg.buf[4-7]
            return 0; // Error response received
        }
    }
    
    // If CAN1_SendFrameEx returned false (timeout) or validation failed, return 0.
    // The old eMR->ActualPosition value remains, but the calling function knows it's stale.
    return 0; 
}

// uint8_t CANOpen_ReadActualPosObj_Safe(eMR_t *eMR)
// {
//     uint8_t data[8] = {0}; // Initialize to zero
//     CAN_message_t rxMsg;   // Use a LOCAL message struct, not the global 'msg'
//     uint32_t node_id = eMR->cobid;
//     uint32_t expected_response_id = RSDO_COBID + (node_id - TSDO_COBID); // e.g., 0x580 + node_id

//     // Build SDO request for ActualPosition (0x6064:00)
//     data[0] = RSDO_Expedited_4; // 0x40 = upload request
//     data[1] = (uint8_t)(ActualPosition_Obj & 0xFF);
//     data[2] = (uint8_t)((ActualPosition_Obj >> 8) & 0xFF);
//     data[3] = 0x00; // subIndex

//     // Send the request and wait for a response in our local rxMsg
//     if (CAN1_SendFrameEx(node_id, DLC, data, rxMsg))
//     {
//         // --- ADDED VALIDATION ---
//         // 1. Check if the response is from the correct CAN ID
//         // 2. Check if it's a successful SDO Upload Response (cmd=0x43 for 4 bytes)
//         // 3. Check if the object index matches our request
//         if (rxMsg.id == expected_response_id &&
//             rxMsg.buf[0] == 0x43 && 
//             rxMsg.buf[1] == (uint8_t)(ActualPosition_Obj & 0xFF) &&
//             rxMsg.buf[2] == (uint8_t)((ActualPosition_Obj >> 8) & 0xFF))
//         {
//             // The response is valid, parse the position data
//             eMR->ActualPosition =
//                 (int32_t)(((uint32_t)rxMsg.buf[4])       |
//                           ((uint32_t)rxMsg.buf[5] << 8)  |
//                           ((uint32_t)rxMsg.buf[6] << 16) |
//                           ((uint32_t)rxMsg.buf[7] << 24));
//             return 1; // Success
//         }
//         // Check for an SDO Abort message from the correct node
//         else if (rxMsg.id == expected_response_id && rxMsg.buf[0] == SDO_Error_Msg) // 0x80
//         {
//             eMR->Err_Flag = true;
//             eMR->ActualPosition = 0; // CORRECTLY zero the position on error
//             // Optionally, you could parse the abort code from rxMsg.buf[4-7]
//             return 0; // Error response received
//         }
//     }
    
//     // If CAN1_SendFrameEx returned false (timeout) or validation failed, return 0.
//     // The old eMR->ActualPosition value remains, but the calling function knows it's stale.
//     return 0; 
// }

//////////////////  Read eMR data ///////////////////////
void eMR_Read_data(eMR_t *eMR_L, eMR_t *eMR_R)   //////////////// (Program type 1)
{
  // volatile int32_t status_word1 = 0;
  int32_t position_L = 0;
  int32_t position_R = 0;
  bool get_L=false;
  bool get_R=false;
  static unsigned long count = 0;
  // bool both_get=true;

    // for ( uint8_t i = 0; i < 8; i++ ) {
    //   Serial5.print(msg.buf[i],HEX); Serial5.print(" ");
    // }
    // Serial5.print(" ");
    while(1)
    {
      Serial5.print("In loop"); Serial5.println(count++);
      
      if (msg.id==0x380 + Motor_ID1 && !get_L) {
        // status_word1  = msg.buf[0] | (msg.buf[1] << 8);
        position_L = (uint32_t)msg.buf[2] | (uint32_t)(msg.buf[3] << 8) | (uint32_t)(msg.buf[4] << 16) | (uint32_t)(msg.buf[5] << 24);
        Serial5.println("position_L: " + String(position_L));
        
        eMR_L->ActualPosition = (int32_t)position_L;
        
        get_L = true;

      }
      if (msg.id==0x380 + Motor_ID2 && !get_R) {
        // status_word1  = msg.buf[0] | (msg.buf[1] << 8);
        position_R = (uint32_t)msg.buf[2] | (uint32_t)(msg.buf[3] << 8) | (uint32_t)(msg.buf[4] << 16) | (uint32_t)(msg.buf[5] << 24);
        Serial5.println("position_R: " + String(position_R));

        eMR_R->ActualPosition = (int32_t)position_R;

        get_R = true;

      }
      if (get_L ==true && get_R ==true){
        get_L = false;
        get_R = false;
        
        Serial5.println("Both motor positions updated.");
        break;
      }
    }

  

}

void eMR_Read_data_base()   //////////////// (Program type 1)
{
 // volatile int32_t status_word1 = 0;
  // volatile int32_t position1 = 0;
  // volatile int32_t position2 = 0;
  CAN_message_t RXmsg;
  unsigned long start = millis();

  while ((millis() - start) < 3) 
  {
    if (can1.read(RXmsg)) 
    {
      if (RXmsg.id==0x380 + Motor_ID1)
      {
      //status_word1  = msg.buf[0] | (msg.buf[1] << 8);
      int32_t position1 = RXmsg.buf[2] | (RXmsg.buf[3] << 8) | (RXmsg.buf[4] << 16) | (RXmsg.buf[5] << 24);
      eMR_right.ActualPosition = position1;

      }

      if (RXmsg.id==0x380 + Motor_ID2)
      {
      //status_word1  = msg.buf[0] | (msg.buf[1] << 8);
      int32_t position2 = RXmsg.buf[2] | (RXmsg.buf[3] << 8) | (RXmsg.buf[4] << 16) | (RXmsg.buf[5] << 24);
      eMR_left.ActualPosition = position2;
      }
    }
  }
}
// uint8_t CANOpen_ReadActualPosObj_PDO(eMR_t *eMR)
// {
//     CAN_message_t rxMsg;
//     uint32_t expectedId = TPDO3_COBID + (eMR->cobid - TSDO_COBID);  
//     // For Actual Position in PDO3 (0x380 + NodeID)

//     unsigned long start = millis();
//     while (millis() - start < ReceiveTimeOut) // wait until timeout
//     {
//         if (can1.read(rxMsg))  // got a frame
//         {
//             // Only process if this is the PDO3 from our motor
//             if (rxMsg.id == expectedId)
//             {
//                 eMR->StatusWord = rxMsg.buf[0] | (rxMsg.buf[1] << 8);
//                 eMR->ActualPosition =
//                     (int32_t)( ((uint32_t)rxMsg.buf[2]) |
//                                ((uint32_t)rxMsg.buf[3] << 8) |
//                                ((uint32_t)rxMsg.buf[4] << 16) |
//                                ((uint32_t)rxMsg.buf[5] << 24));
//                 return 1;  // success
//             }
//         }
//     }

//     return 0; // timeout, no valid PDO received for this motor
// }
uint8_t CANOpen_ReadActualPosObj_PDO(eMR_t *eMR)
{
    uint32_t node_id = eMR->cobid;

    //Sync_message(eMR); // Send SYNC before reading PDO
    
    //Serial.println("node_id: " + String(node_id));
    //Serial.println("msg id: " + String(msg.id, HEX) + " msg len: " + String(msg.len));

    // position = msg.buf[2] | (msg.buf[3] << 8) | (msg.buf[4] << 16) | (msg.buf[5] << 24);
    if (node_id != msg.id) // Example for Motor_ID1=1 or Motor_ID2=2
    {
        //Serial.println("Unexpected PDO ID: " + String(msg.id, HEX));
        return 0; // Not the expected PDO message
    }
    else
    {
    eMR->ActualPosition =
        (int32_t)(((uint32_t)msg.buf[2])       |
                  ((uint32_t)msg.buf[3] << 8)  |
                  ((uint32_t)msg.buf[4] << 16) |
                  ((uint32_t)msg.buf[5] << 24));


    return 1; // Success

    }


}


// uint8_t CANOpen_ReadActualVelocityObj(eMR_t *eMR)
// {
//     uint8_t data[8];
//     uint32_t node_id = eMR->cobid;

//     // Build SDO request for ActualVelocity (0x6069:00)
//     data[0] = RSDO_Expedited_4;  // 0x40 = upload request
//     data[1] = (uint8_t)(ActualVelocity_Obj & 0xFF);
//     data[2] = (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF);
//     data[3] = 0x00;  // subIndex
//     data[4] = data[5] = data[6] = data[7] = 0x00;

//     // Send request
//     CAN1_SendFrame(node_id, DLC, data);

//     if (revPACKET.buf[1] == (uint8_t)(ActualVelocity_Obj & 0xFF) &&
//         revPACKET.buf[2] == (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF)) 
//             {
//                 // Ignore strict revPACKET.buf[0], just parse
//                 eMR->ActualVelocity =
//                     (int32_t)((uint32_t)revPACKET.buf[4] |
//                             ((uint32_t)revPACKET.buf[5] << 8) |
//                             ((uint32_t)revPACKET.buf[6] << 16) |
//                             ((uint32_t)revPACKET.buf[7] << 24));
//                 return 1;
//             }
//             else if (revPACKET.buf[0] == SDO_Error_Msg) // 0x80
//             {
//                 eMR->Err_Flag = true;
//                 eMR->ActualVelocity = 0;
//                 return 0;  // error response
//             }
        
//     return 0;  // not valid
// }




uint8_t CANOpen_ReadActualVelocityObjEx(eMR_t *eMR)
{
    uint8_t data[8] = {0};
    CAN_message_t rxMsg;
    uint32_t node_id = eMR->cobid;

    // Build upload request (0x6069:00)
    data[0] = RSDO_Expedited_4;  // 0x40 = upload request
    data[1] = (uint8_t)(ActualVelocity_Obj & 0xFF);
    data[2] = (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF);
    data[3] = 0x00; // subindex

    if (CAN1_SendFrameEx(node_id, DLC, data, rxMsg))
    {
        if (rxMsg.buf[1] == (uint8_t)(ActualVelocity_Obj & 0xFF) &&
            rxMsg.buf[2] == (uint8_t)((ActualVelocity_Obj >> 8) & 0xFF))
        {
            // Parse the 32-bit signed velocity
            eMR->ActualVelocity =
                (int32_t)((uint32_t)rxMsg.buf[4] |
                         ((uint32_t)rxMsg.buf[5] << 8) |
                         ((uint32_t)rxMsg.buf[6] << 16) |
                         ((uint32_t)rxMsg.buf[7] << 24));
            return 1; // success
        }
        else if (rxMsg.buf[0] == SDO_Error_Msg) // 0x80
        {
            eMR->Err_Flag = true;
            eMR->ActualVelocity = 0;
            return 0;  
        }
    }

    return 0; // timeout or invalid
}


int32_t velocity1 = 0;
int32_t velocity2 = 0;
int32_t velocity = 0;

uint8_t eMR_Sync_message()
{
  uint8_t data[1];          
  uint32_t node_id;
  
  node_id = SYNC_COBID;
  data[0] = 0x00;                                                                

  return CAN1_SendFrame(node_id, 0x01, data);
}

void eMR_ReadActualVelocity2()
{
  int32_t  velocity=0;
  eMR_Sync_message();

  v.velocity1 = 0.1*(((velocity | revPACKET.buf[3])<<24) + ((velocity | revPACKET.buf[2])<<16)
              + ((velocity | revPACKET.buf[1])<<8) + (velocity | revPACKET.buf[0]));

  v.velocity2 = 0.1*(((velocity | revPACKET.buf[7])<<24) + ((velocity | revPACKET.buf[6])<<16)
             + ((velocity | revPACKET.buf[5])<<8) + (velocity | revPACKET.buf[4]));

}



uint8_t CANOpen_SwitchON(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = eMR->cobid;
  data[0] = SDO_Expedited_2;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(Controlword_Obj & 0xFF);                // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((Controlword_Obj>>8) & 0xFF);           // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  data[4] = 0x0F;                                             // SDO <DATA_Byte0>     Byte4
  data[5] = 0x00;                                             // SDO <DATA_Byte1>     Byte5
  data[6] = 0x00;                                             // SDO <DATA_Byte2>     Byte6
  data[7] = 0x00;                                             // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);                               // Test DLC = 6?
}
uint8_t CANOpen_SetProfileAcceleration(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t ProfileAccel;

  node_id = eMR->cobid;
  ProfileAccel = eMR->ProfileAcceleration;
  data[0] = SDO_Expedited_4;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(ProfileAcceleration_Obj & 0xFF);             // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((ProfileAcceleration_Obj>>8) & 0xFF);        // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3

  data[4] = (uint8_t)(ProfileAccel & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[5] = (uint8_t)((ProfileAccel>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[6] = (uint8_t)((ProfileAccel>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[7] = (uint8_t)((ProfileAccel>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data); 
}
uint8_t CANOpen_SetProfileDeceleration(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t ProfileDecel;

  node_id = eMR->cobid;
  ProfileDecel = eMR->ProfileAcceleration;
  data[0] = SDO_Expedited_4;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(ProfileDeceleration_Obj & 0xFF);             // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((ProfileDeceleration_Obj>>8) & 0xFF);        // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3

  data[4] = (uint8_t)(ProfileDecel & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[5] = (uint8_t)((ProfileDecel>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[6] = (uint8_t)((ProfileDecel>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[7] = (uint8_t)((ProfileDecel>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data); 
}
uint8_t CANOpen_SetTargetVelocity(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t velocity;

  node_id = eMR->cobid;
  velocity = eMR->TargetVelocity;
  data[0] = SDO_Expedited_4;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(TargetVelocity_Obj & 0xFF);             // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((TargetVelocity_Obj>>8) & 0xFF);        // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3

  data[4] = (uint8_t)(velocity & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[5] = (uint8_t)((velocity>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[6] = (uint8_t)((velocity>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[7] = (uint8_t)((velocity>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7

  // 5 rpm 

  //data[4] = 0x6A;                       
  //data[5] = 0xAA;                  
  //data[6] = 0x00;                 
  //data[7] = 0x00;                 

  return CAN1_SendFrame(node_id,DLC, data); 
}
uint8_t CANOpen_StopMotor(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = eMR->cobid;
  data[0] = SDO_Expedited_4;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(TargetVelocity_Obj & 0xFF);             // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((TargetVelocity_Obj>>8) & 0xFF);        // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  data[4] = 0x00;                       
  data[5] = 0x00;                  
  data[6] = 0x00;                 
  data[7] = 0x00;                 

  return CAN1_SendFrame(node_id,DLC, data); 
}
uint8_t CANOpen_SetTargetPosition(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t position;

  node_id = eMR->cobid;
  position = eMR->TargetPosition;
  data[0] = SDO_Expedited_4;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(TargetPosition_Obj & 0xFF);             // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((TargetPosition_Obj>>8) & 0xFF);        // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3

  data[4] = (uint8_t)(position & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[5] = (uint8_t)((position>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[6] = (uint8_t)((position>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[7] = (uint8_t)((position>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data); 
}

uint8_t CANOpen_SetPolarity(eMR_t *eMR, uint8_t value)
{
    uint8_t data[8];
    uint32_t node_id = eMR->cobid;

    data[0] = SDO_Expedited_1;                 // 1‑byte expedited write
    data[1] = (uint8_t)(0x607E & 0xFF);
    data[2] = (uint8_t)((0x607E >> 8) & 0xFF);
    data[3] = 0x00;                            // Sub‑index 0
    data[4] = value;                           // 0x00 = normal, 0x40 = flip velocity, etc.
    data[5] = 0x00;
    data[6] = 0x00;
    data[7] = 0x00;

    return CAN1_SendFrame(node_id, DLC, data);
}

void CANOpen_eMR_Init(void)
{

  NMT_SetOperational();
  delay(100);
  eMR.cobid = TSDO_COBID + axis1;

  CANOpen_ResetFaults(&eMR);
                                                 
  eMR.mode = PVM_MODE;                                      //  Target velocity mode     
  CANOpen_SetOperationMode(&eMR);                           
  //CANOpen_SetProfileAcceleration(&eMR);  
  //CANOpen_SetProfileDeceleration(&eMR); 
  //CANOpen_Shutdown(&eMR);

  // ✅ Ensure consistent polarity (say, invert for right wheel)
  // CANOpen_SetPolarity(&eMR, 0x40);

  delay(100);
  CANOpen_SwitchON(&eMR);    
  delay(100);

  eMR.cobid = TSDO_COBID + axis2;
  CANOpen_ResetFaults(&eMR);

  eMR.mode = PVM_MODE; 
  CANOpen_SetOperationMode(&eMR);                   
  //CANOpen_SetProfileAcceleration(&eMR);  
  //CANOpen_SetProfileDeceleration(&eMR); 
  //CANOpen_Shutdown(&eMR);

  // ✅ Ensure consistent polarity (say, invert for right wheel)
  // CANOpen_SetPolarity(&eMR, 0x00);
  delay(100);
  CANOpen_SwitchON(&eMR);
  delay(100);
  
}

void CANOpen_eMR_QuickStop(void)
{
    eMR.cobid = TSDO_COBID + axis1;
    //CANOpen_Shutdown(&eMR);
    CANOpen_StopMotor(&eMR);
    eMR.cobid = TSDO_COBID + axis2;
    //CANOpen_Shutdown(&eMR);
    CANOpen_StopMotor(&eMR);
}



uint8_t CANOpen_SetTargetVelocityPDO(eMR_t *eMR)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t velocity;

  node_id = eMR->cobid;                                       // 0x501, 0x502
  velocity = eMR->TargetVelocity;
  // 1F 20 64 AA 00 00
  data[0] = 0x1F;                                             // PDO <Lowbyte_Index>  Byte0
  data[1] = 0x20;                                             // PDO <Highbyte_Index> Byte1

  data[2] = (uint8_t)(velocity & 0xFF);                       // PDO <DATA_Byte0>     Byte4
  data[3] = (uint8_t)((velocity>>8) & 0xFF);                  // PDO <DATA_Byte1>     Byte5
  data[4] = (uint8_t)((velocity>>16) & 0xFF);                 // PDO <DATA_Byte2>     Byte6
  data[5] = (uint8_t)((velocity>>24) & 0xFF);                 // PDO <DATA_Byte3>     Byte7

  // 5 rpm 

  //data[2] = 0x64;                       
  //data[3] = 0xAA;                  
  // data[6] = 0x00;                 
  // data[7] = 0x00;                 

  return CAN1_SendFrame(node_id,6, data); 
}

uint8_t eMRCanSpeedCntrl(float percentPwm, bool direction, uint8_t motorNo)
{

    eMR.MaxProfileVelocity = MaxVelocity;                    // Max RPM

    if (motorNo==1)
    {
      //eMR.cobid = TSDO_COBID + axis1;
      eMR.cobid = DKE_RPDO4 + axis1;  //0x501
      if (direction)                             // Positive direction
      {
          // eMR.TargetVelocity = (int32_t)(eMR.MaxProfileVelocity*percentPwm*16384/600);
          eMR.TargetVelocity = (int32_t)(eMR.MaxProfileVelocity*percentPwm*16384/947);
        //   Serial.print("Target Speed motor1: "); Serial.println(eMR.TargetVelocity, DEC );
      }
      else                                       // Negative direction
      {
          // eMR.TargetVelocity = (int32_t)(-eMR.MaxProfileVelocity*percentPwm*16384/600);    
          eMR.TargetVelocity = (int32_t)(-eMR.MaxProfileVelocity*percentPwm*16384/947);
        //   Serial.print("Target Speed motor1: "); Serial.println(eMR.TargetVelocity, DEC );
      }      
      CANOpen_SetTargetVelocityPDO(&eMR);
      //Sync_message(&eMR); // Send SYNC after setting velocity
    }
    else if (motorNo==2){
      //eMR.cobid = TSDO_COBID + axis2;
      eMR.cobid = DKE_RPDO4 + axis2;  //0x501
      if (direction)
      {
          // eMR.TargetVelocity = (int32_t)(eMR.MaxProfileVelocity*percentPwm*16384/600);
          eMR.TargetVelocity = (int32_t)(eMR.MaxProfileVelocity*percentPwm*16384/947);
        //   Serial.print("Target Speed motor2: "); Serial.println(eMR.TargetVelocity, DEC );
      }
      else
      {
          // eMR.TargetVelocity = (int32_t)(-eMR.MaxProfileVelocity*percentPwm*16384/600);  
          eMR.TargetVelocity = (int32_t)(-eMR.MaxProfileVelocity*percentPwm*16384/947);
        //   Serial.print("Target Speed motor2: "); Serial.println(eMR.TargetVelocity, DEC );   
      }
      //CANOpen_SetTargetVelocity(&eMR);
      // CAN_Open_setTargetVelocityPDO(&eMR);
      CANOpen_SetTargetVelocityPDO(&eMR);
       
    }
    else
    {
      return -1;
    }
  return 0;   
}

void Update_eMRMotorSpeed(void)
{
  eMR.cobid = TSDO_COBID + axis1;
  CANOpen_SwitchON(&eMR); 
  eMR.cobid = TSDO_COBID + axis2;
  CANOpen_SwitchON(&eMR); 
}



