#include <Arduino.h>
#include <TimerOne.h>
//#include <ODriveArduino.h>
#include <stdio.h>
#include <FlexCAN_T4.h>           // https://github.com/tonton81/FlexCAN_T4
#include <TimerOne.h>
#include "can_driver.h"

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can1;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> can2;

CAN_message_t msg;
CAN_message_t revPACKET;
eMR_t eMR;
velocity_t v;

int32_t velocity1 = 0;
int32_t velocity2 = 0;
int32_t velocity = 0;


bool CAN1_ReceiveFrame()
{
  can1.read(revPACKET);
  return true;
}

bool CAN1_SendFrame(uint32_t node_id, uint32_t data_size, uint8_t* data)
{
  msg.id = node_id;
  msg.len = data_size;

  memcpy(&msg.buf[0], &data[0], data_size);
  can1.write(msg);  

  return CAN1_ReceiveFrame();
}

//////////////  SYNCHRONIZATION OBJECT (SYNC) /////////
////////// The Synchronization object is used to simultaneously validate the time of PDO data //////////
uint8_t eMR_Sync_message()
{
  uint8_t data[1];          
  uint32_t node_id;
  
  node_id = SYNC_COBID;
  data[0] = 0x00;                                                                

  return CAN1_SendFrame(node_id, 0x01, data);
}
//////////////////  NMT command ///////////////////////
uint8_t eMR_NMT_SetOperational()
{
  uint8_t data[2];
  uint32_t node_id;
  
  node_id = NMT_COBID;                               // NMT Command
  data[0] = NMT_Operation ;                                             
  data[1] = 0x01;                                   //                             
  
  return CAN1_SendFrame(node_id, 0x02, data);
}
uint8_t eMR_NMT_SetPreoperational()
{
  uint8_t data[2];
  uint32_t node_id;
  
  node_id = NMT_COBID;                               // NMT Command
  data[0] = NMT_PreOperation;                                             
  data[1] = 0x01 ;                                   //                             
  
  return CAN1_SendFrame(node_id, 0x02, data);
}

uint8_t eMR_NMT_SetStop()
{
  uint8_t data[2];
  uint32_t node_id;
  
  node_id = NMT_COBID;                               // NMT Command
  data[0] = NMT_Stop;                                             
  data[1] = 0x00 ;                                   //  Boardcast all network                             
  
  return CAN1_SendFrame(node_id, 0x02, data);
}

uint8_t eMR_SetHeartbeatTime()
{
  uint8_t data[8];
  uint32_t node_id;

  node_id = SDO_COBID + dual_axis;
  data[0] = SDO_Expedited_2;                                  // SDO <CMD>            Byte0
  data[1] = (uint8_t)(HeartbeatTime_Obj & 0xFF);              // SDO <Lowbyte_Index>  Byte1
  data[2] = (uint8_t)((HeartbeatTime_Obj>>8) & 0xFF);         // SDO <Highbyte_Index> Byte2
  data[3] = 0x00;                                             // SDO <SubIndex>       Byte3
  //data[4] = 0x88;                                             // SDO <DATA_Byte0>     Byte4
  //data[5] = 0x13;                                             // SDO <DATA_Byte1>     Byte5
  data[4] = 0x00;                                             // SDO <DATA_Byte0>     Byte4
  data[5] = 0x00;                                             // SDO <DATA_Byte1>     Byte5
  data[6] = 0x00;                                             // SDO <DATA_Byte2>     Byte6
  data[7] = 0x00;                                             // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);                               // Test DLC = 6?
}

void eMR_CANOpen_Begin()
{
    can1.begin();
    can1.setBaudRate(500000); // Set CAN1 bitrate 500 Kbps
    can1.setMBFilter(ACCEPT_ALL);
    can1.distribute();
    can1.mailboxStatus();
}

uint8_t  eMR_CANOpen_Init()
{
  eMR_SetHeartbeatTime();
  delay(500);
  eMR_NMT_SetOperational();
  delay(500);
  return 0;
}

uint8_t eMR_SetTargetVelocity(float percentPwm1,bool direction1, float percentPwm2, bool direction2)
{
  uint8_t data[8];
  uint32_t node_id;
  int32_t TargetVelocity1;
  int32_t TargetVelocity2;

  percentPwm1 = (percentPwm1 > 100) ? 100 : (percentPwm1 < -100) ? 0 : percentPwm1;
  percentPwm2 = (percentPwm2 > 100) ? 100 : (percentPwm2 < -100) ? 0 : percentPwm2;


      if (direction1)                             // Positive direction
      {
          TargetVelocity1 = (int32_t)(MaxVelocity*percentPwm1/100);
          //Serial.print("Target Speed motor1: "); 
          //Serial.println(TargetVelocity1 , DEC );
      }
      else                                       // Negative direction
      {
          TargetVelocity1 = (int32_t)(-MaxVelocity*percentPwm1/100);    
          //Serial.print("Target Speed motor1: "); 
          //Serial.println(TargetVelocity1 , DEC );
      }  
      
      if (direction2)                             // Positive direction
      {
          TargetVelocity2 = (int32_t)(MaxVelocity*percentPwm2/100);
          //Serial.print("Target Speed motor2: "); 
          //Serial.println(TargetVelocity2, DEC );
      }
      else                                       // Negative direction
      {
          TargetVelocity2 = (int32_t)(-MaxVelocity*percentPwm2/100);    
          //Serial.print("Target Speed motor2: "); 
          //Serial.println(TargetVelocity2, DEC );
      } 


  node_id = TPDO1_COBID + dual_axis;      
 
  data[0] = (uint8_t)(TargetVelocity1 & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[1] = (uint8_t)((TargetVelocity1>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[2] = (uint8_t)((TargetVelocity1>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[3] = (uint8_t)((TargetVelocity1>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7
  data[4] = (uint8_t)(TargetVelocity2 & 0xFF);                       // SDO <DATA_Byte0>     Byte4
  data[5] = (uint8_t)((TargetVelocity2>>8) & 0xFF);                  // SDO <DATA_Byte1>     Byte5
  data[6] = (uint8_t)((TargetVelocity2>>16) & 0xFF);                 // SDO <DATA_Byte2>     Byte6
  data[7] = (uint8_t)((TargetVelocity2>>24) & 0xFF);                 // SDO <DATA_Byte3>     Byte7

  return CAN1_SendFrame(node_id,DLC, data);  
}

uint8_t eMR_ReadActualVelocity()
{
  int32_t  velocity=0;
  eMR_Sync_message();

  velocity1 = 0.1*(((velocity | revPACKET.buf[3])<<24) + ((velocity | revPACKET.buf[2])<<16)
              + ((velocity | revPACKET.buf[1])<<8) + (velocity | revPACKET.buf[0]));

  velocity2 = 0.1*(((velocity | revPACKET.buf[7])<<24) + ((velocity | revPACKET.buf[6])<<16)
             + ((velocity | revPACKET.buf[5])<<8) + (velocity | revPACKET.buf[4]));

/*
  Serial.println(revPACKET.buf[0],HEX);
  Serial.println(revPACKET.buf[1],HEX);
  Serial.println(revPACKET.buf[2],HEX);
  Serial.println(revPACKET.buf[3],HEX);

  Serial.println(revPACKET.buf[4],HEX);
  Serial.println(revPACKET.buf[5],HEX);
  Serial.println(revPACKET.buf[6],HEX);
  Serial.println(revPACKET.buf[7],HEX);
*/
      
  return 0;
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

void canSniff(const CAN_message_t &msg) {


  Serial.println("Interrupted");
  Serial.print("MB "); Serial.print(msg.mb);
  Serial.print("  OVERRUN: "); Serial.print(msg.flags.overrun);
  Serial.print("  LEN: "); Serial.print(msg.len);
  Serial.print(" EXT: "); Serial.print(msg.flags.extended);
  Serial.print(" TS: "); Serial.print(msg.timestamp);
  Serial.print(" ID: "); Serial.print(msg.id, HEX);
  Serial.print(" Buffer: ");

  for ( uint8_t i = 0; i < msg.len; i++ ) {
    Serial.print(msg.buf[i], HEX); Serial.print(" ");
  } Serial.println();

}