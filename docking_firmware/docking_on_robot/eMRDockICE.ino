#include <Arduino.h>
#include <ModbusRTUSlave.h>

// === IR Serial ===
#define IR_HEADER       0xAA
#define RX1_PIN         20
#define TX1_PIN         21
#define CONST_HIGH_PIN  10
#define LED_BUILTIN     8
HardwareSerial IRSerial(1);

// === RS485 Modbus ===
#define RS485_DE_RE   5
#define RS485_RX      6
#define RS485_TX      7
#define SLAVE_ID      9
HardwareSerial RS485Serial(0);
ModbusRTUSlave modbus(RS485Serial, RS485_DE_RE, RS485_DE_RE);

// Holding registers
// [0] = Event/status ส่งให้ PC อ่าน
// [1] = Command ที่ PC เขียนเข้ามา
uint16_t holdingRegs[2] = {0};

volatile int RobotStage = 0;
volatile unsigned long lastIRReceiveTime = 0; // ตัวแปรสำหรับ Watchdog

int prevRobotStage = -1;

// ========== IR Protocol ==========
void sendIRCommand(uint8_t cmd) {
  IRSerial.write(IR_HEADER);
  IRSerial.write(cmd);
  IRSerial.write(IR_HEADER ^ cmd);
  Serial.print("📤 IR Sent: 0x"); Serial.println(cmd, HEX);
}

bool receiveIRCommand(uint8_t &cmd) {
  static int state=0; static uint8_t buf[3];
  while (IRSerial.available()) {
    uint8_t b=IRSerial.read(); buf[state++]=b;
    if (b == IR_HEADER){
      lastIRReceiveTime=millis(); // บันทึกเวลาเมื่อรับ IR สำเร็จ
    }
    if (state==1 && buf[0]!=IR_HEADER) state=0;
    else if (state==3) {
      if ((buf[0]^buf[1])==buf[2]) {
        cmd=buf[1]; state=0;
        Serial.print("📥 IR Received: 0x"); Serial.println(cmd, HEX);
        return true;
      }
      state=0;
    }
  }
  return false;
}

// ========== Superloop (millis-timed) Tasks ==========

// Blink task: toggle LED every 500ms
void Blink_loop() {
  static unsigned long last = 0;
  const unsigned long interval = 500;
  if (millis() - last >= interval) {
    last = millis();
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
}

// IR communication task: handle receive, ACKs and send commands
void IRCommu_loop() {
  static uint8_t lastSent = 0;
  static bool gotAck = false;
  static int retry = 0;
  static unsigned long lastTime = 0;

  uint8_t recv;
  // drain all available IR bytes and process commands
  while (receiveIRCommand(recv)) {
    if (recv == 0xF0 && lastSent != 0) {
      gotAck = true; retry = 0;
      Serial.println("✅ Got ACK from Dock");
    } else {
      // always reply ACK
      sendIRCommand(0xF0);
      if (recv == 0x01) { RobotStage = 0; }
      else if (recv == 0x02) RobotStage = 1;
      else if (recv == 0x03) RobotStage = 5;
      else if (recv == 0x05) RobotStage = 0;
    }
  }

  // prepare command to Dock
  uint8_t cmd = 0;
  if (RobotStage == 3) cmd = 0x11;       // ReadyToCharge
  else if (RobotStage == 7) cmd = 0x12;  // FullyCharged
  else if (RobotStage == 8) cmd = 0x13;  // StopCharging

  if (cmd && (cmd != lastSent || !gotAck || millis() - lastTime > 500)) {
    if (!gotAck && cmd == lastSent) {
      if (++retry >= 10) {
        RobotStage = 0; retry = 0; gotAck = false; lastSent = 0;
        Serial.println("⚠️ Max retry reached, reset stage");
        return;
      }
    }
    sendIRCommand(cmd);
    lastSent = cmd; lastTime = millis(); gotAck = false;
  }

  if (gotAck && lastSent != 0) {
    if (lastSent == 0x11) RobotStage = 4;
    else if (lastSent == 0x12) RobotStage = 0;
    else if (lastSent == 0x13) RobotStage = 2;
    gotAck = false; lastSent = 0;
  }
}

// Modbus handling task: update events, process incoming commands
void Modbus_loop() {
  static uint16_t prevReg0 = 0, prevReg1 = 0;

  // event to PC
  if (RobotStage == 0) { holdingRegs[0] = 0; }
  else if (RobotStage == 1) { holdingRegs[0] = 10; RobotStage = 2; }
  else if (RobotStage == 5) { holdingRegs[0] = 11; RobotStage = 6; }

  // log เมื่อ event เปลี่ยน
  if (holdingRegs[0] != prevReg0) {
    Serial.print("📤 Modbus Event updated -> holdingRegs[0] = ");
    Serial.println(holdingRegs[0]);
    prevReg0 = holdingRegs[0];
  }

  // command from PC
  uint16_t cmd = holdingRegs[1];
  if (cmd != 0 && cmd != prevReg1) {
    Serial.print("📥 Modbus Received from PC -> holdingRegs[1] = ");
    Serial.println(cmd);
    prevReg1 = cmd;
  }

  if (cmd == 20) {
    RobotStage = 3; holdingRegs[1] = 0; Serial.println("➡️ PC Command: ReadyToCharge executed");
  }
  else if (cmd == 21) {
    RobotStage = 7; holdingRegs[1] = 0; Serial.println("➡️ PC Command: FullyCharged executed");
  }
  else if (cmd == 22) {
    RobotStage = 8; holdingRegs[1] = 0; Serial.println("➡️ PC Command: StopCharging executed");
  }

  // keep Modbus stack running
  modbus.poll();
}

// Watchdog task: reset state if no IR seen in 2s
void Watchdog_loop() {
  static unsigned long last = 0;
  const unsigned long interval = 500;
  if (millis() - last >= interval) {
    last = millis();
    if (millis() - lastIRReceiveTime > 2000) {
      // If we were charging and IR stopped, likely the dock lost power.
      if (RobotStage == 4) {
        // Report dock power lost to PC via holdingRegs[0]
        holdingRegs[0] = 12; // DockPowerLost event
        // Clear incoming command and move to safe idle state
        holdingRegs[1] = 0;
        RobotStage = 0;
        Serial.println("⚠️ Watchdog: Dock power lost detected during charging -> reported to Modbus (holdingRegs[0]=12) and reset RobotStage");
      } else {
        RobotStage = 0;
        holdingRegs[0] = 0;
        holdingRegs[1] = 0;
        Serial.println("Watchdog Triggered: No IR seen in 2s --> Reset RobotStage and Modbus Reg");
      }
    }
  }
}

// Monitor task: periodic debug print
void Monitor_loop() {
  static unsigned long last = 0;
  const unsigned long interval = 500;
  if (millis() - last >= interval) {
    last = millis();
    Serial.print("🧭 RobotStage changed: ");
    Serial.println(RobotStage);
    prevRobotStage = RobotStage;
    Serial.print("485 command[0,1]: ");
    Serial.print(holdingRegs[0]); Serial.print(" , "); Serial.println(holdingRegs[1]);
  }
}

// ========== Setup ==========
void setup(){
  pinMode(CONST_HIGH_PIN,OUTPUT); digitalWrite(CONST_HIGH_PIN,HIGH);
  Serial.begin(9600);

  IRSerial.begin(9600,SERIAL_8N1,RX1_PIN,TX1_PIN);
  RS485Serial.begin(115200,SERIAL_8N1,RS485_RX,RS485_TX);
  modbus.begin(SLAVE_ID,115200,SERIAL_8N1);
  modbus.configureHoldingRegisters(holdingRegs,2);
  // Run in superloop (no RTOS): initialize peripherals and timers
  pinMode(LED_BUILTIN, OUTPUT);
  lastIRReceiveTime = millis();
  Serial.println("Setup complete - running in superloop mode");
}

void loop(){
  // cooperative multitasking by calling each loop function
  IRCommu_loop();
  Modbus_loop();
  Watchdog_loop();
  Monitor_loop();
  Blink_loop();
  // small sleep to yield CPU and keep timing stability
  delay(10);
}

/*
================= RobotStage Mapping =================

StageID   |ความหมาย (Description)
------------------------------------------------------------
0         |Initial — ยังไม่อยู่ในสถานะใด
1         |eMR หยุดถอยหลังหลัง Dock สั่ง StopBackward
2         |รอคำสั่งจาก PC (ผ่าน Modbus) หลังหยุดถอย
3         |eMR เตรียมส่ง ReadyToCharge ไป Dock
4         |eMR อยู่ระหว่างชาร์จ (Dock เปิดรีเลย์ให้แล้ว)
5         |eMR แจ้ง Event "กำลังชาร์จ" (11) ไปยัง PC แล้ว
6         |eMR รอ PC สั่ง FullyCharged
7         |eMR ส่ง IR "FullyCharged" ไป Dock
8         |eMR ส่ง IR "StopCharging" ไป Dock

------------------------------------------------------------
IR Command IDs ใช้สัมพันธ์กัน:
 0x01 = InitialStage        (Dock ➜ eMR)
 0x02 = StopBackward        (Dock ➜ eMR)
 0x03 = BattCharging        (Dock ➜ eMR)
 0x04 = FullyCharged        (Dock ➜ eMR)
 0x05 = StopCharging        (Dock ➜ eMR)

 0x11 = ReadyToCharge       (eMR ➜ Dock)
 0x12 = FullyCharged        (eMR ➜ Dock)
 0x13 = StopCharging        (eMR ➜ Dock)

 0xF0 = ACK                 (Bidirectional ACK)

------------------------------------------------------------
Modbus Holding Register Mapping:
 holdingRegs[0] = Event out (eMR ➜ PC/PLC/ROS)
   - 0  = Idle
   - 10 = RobotStopBackward
   - 11 = RobotBattCharging
  - 12 = DockPowerLost

 holdingRegs[1] = Command in (PC/PLC/ROS ➜ eMR)
   - 20 = RobotReadyToCharge
   - 21 = emrFullyCharged
   - 22 = emrStopCharging
============================================================
*/