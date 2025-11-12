#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define SENSOR1_PIN     0
#define SENSOR2_PIN     1
#define RELAY_PIN       2
#define LED_PIN         4
#define CONST_HIGH_PIN  10
#define RX1_PIN         20
#define TX1_PIN         21
#define LED_BUILTIN     8

HardwareSerial IRSerial(1);
Adafruit_NeoPixel pixels(14, LED_PIN, NEO_GRB + NEO_KHZ800);

#define IR_HEADER 0xAA

volatile int DockStage = 0;
volatile int prevDockStage = -1;
volatile int ChargingStage = 0;
volatile int prevChargingStage = -1;

unsigned long lastBlinkTime = 0;
bool ledState = false;

// ======================= Binary IR Protocol =======================
void sendIRCommand(uint8_t cmd) {
  IRSerial.write(IR_HEADER);
  IRSerial.write(cmd);
  IRSerial.write(IR_HEADER ^ cmd);
}

bool receiveIRCommand(uint8_t &cmd) {
  static int state = 0;
  static uint8_t buf[3];
  while (IRSerial.available()) {
    uint8_t b = IRSerial.read();
    buf[state++] = b;
    if (state == 1 && buf[0] != IR_HEADER) state = 0;
    else if (state == 3) {
      uint8_t chk = buf[0] ^ buf[1];
      if (chk == buf[2]) {
        cmd = buf[1];
        state = 0;
        return true;
      } else state = 0;
    }
  }
  return false;
}

// ======================= Tasks =======================
void BlinkBuiltinLED(void *param) {
  pinMode(LED_BUILTIN, OUTPUT);
  while (1) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    vTaskDelay(500 / portTICK_PERIOD_MS);
  }
}

void ChargerChecking(void *param) {
  while (true) {
    bool s1 = digitalRead(SENSOR1_PIN);
    bool s2 = digitalRead(SENSOR2_PIN);
    
    if ((s1==1) && (s2==1))
    { if (ChargingStage <= 1) 
      { DockStage = 2;
        ChargingStage = 3;
      }
    }
    else if ((s1==0) && (s2==0))  // no pressed charging plate 
    { DockStage = 0;
      ChargingStage = 0;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    } 
    else if ((s1==0) && (s2==1))
    { digitalWrite(RELAY_PIN, LOW);
      DockStage = 1;
      ChargingStage = 1;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    }
    else if ((s2==0) && (s1==1))
    { digitalWrite(RELAY_PIN, LOW);
      DockStage = 1;
      ChargingStage = 1;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    }
    /*
    if ((s1==0) && (s2==0))
    { if (ChargingStage <= 1) 
      { DockStage = 2;
        ChargingStage = 3;
      }
    }
    else if ((s1==1) && (s2==1))  // no pressed charging plate 
    { DockStage = 0;
      ChargingStage = 0;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    } 
    else if ((s1==1) && (s2==0))
    { digitalWrite(RELAY_PIN, LOW);
      DockStage = 1;
      ChargingStage = 1;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    }
    else if ((s2==1) && (s1==0))
    { digitalWrite(RELAY_PIN, LOW);
      DockStage = 1;
      ChargingStage = 1;
      digitalWrite(RELAY_PIN, LOW);  // Power Contact OFF
    }
     */
    vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}


void DockIRCommu(void *param) {
  uint8_t lastSent = 0;
  bool gotAck = false;
  unsigned long lastTime = 0;
  int retryCount = 0;
/*
0x11 --> ReadyToCharge
0x12 --> FullyCharged
0x13 --> StopCharging
*/
  while (1) {
    // รับจาก eMR
    uint8_t recv;
    if (receiveIRCommand(recv)) {
      if (recv == 0xF0) { 
        gotAck = true; 
        retryCount = 0; 
        Serial.println("✅ Got ACK"); 
      }
      else {
        sendIRCommand(0xF0);  // ตอบกลับ ACK

        if (recv == 0x11 && (ChargingStage == 2 || ChargingStage == 3)) { 
          digitalWrite(RELAY_PIN, HIGH); 
          ChargingStage = 4; 
          Serial.println("📥 eMR ReadyToCharge"); 
        }   
        else if (recv == 0x12 && ChargingStage == 4) { 
          digitalWrite(RELAY_PIN, LOW); 
          ChargingStage = 5; 
          Serial.println("📥 eMR FullyCharged, stop relay"); 
        }
        else if (recv == 0x13) { 
          digitalWrite(RELAY_PIN, LOW); 
          ChargingStage = 0; 
          DockStage = 0; 
          Serial.println("📥 eMR StopCharging"); 
        }
        else if (recv == 0x11 && ChargingStage == 5)
        {
          digitalWrite(RELAY_PIN, HIGH);
          ChargingStage = 4;
        }
      }
    }
/*
0x01 --> InitialStage
0x02 --> StopBackward
0x03 --> BattCharging
0x04 --> FullyCharged
*/
    // จัดส่ง cmd ไปยัง eMR
    uint8_t cmdToSend = 0;
    if (DockStage == 0) cmdToSend = 0x01;
    else if (DockStage == 2 && ChargingStage == 3) cmdToSend = 0x02;
    else if (ChargingStage == 4) cmdToSend = 0x03;
    else if (ChargingStage == 5) cmdToSend = 0x04;

    if (cmdToSend && (cmdToSend != lastSent || !gotAck || millis() - lastTime > 500)) {
      if (!gotAck && cmdToSend == lastSent) {
        if (++retryCount >= 10) { 
          retryCount=0; gotAck=false; lastSent=0; 
          Serial.println("⚠️ Max retry reached, skip cmd"); 
        }
      } else {
        sendIRCommand(cmdToSend);
        Serial.print("📤 Sent to eMR: 0x"); Serial.println(cmdToSend, HEX);
        lastSent = cmdToSend;
        lastTime = millis();
        gotAck = false;
      }
    }

    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}


void LEDDisplay(void *param) {
  while (true) {
    uint32_t color = 0;
    unsigned long now = millis();

    if (ChargingStage == 0 || ChargingStage == 6) 
    { //  Green colour   initial stage
      color = pixels.Color(0, 255, 0); 
    } 
    else if (ChargingStage == 3) 
    {  // Red Colour  Two plates are pressing and waiting for charging command. 
      color = pixels.Color(255, 0, 0);  
    } 
    else if (ChargingStage == 1 || ChargingStage == 4 || ChargingStage == 5) 
    {
      if (now - lastBlinkTime > 800) {
        ledState = !ledState;
        lastBlinkTime = now;
      }
      color = ledState ?
        (ChargingStage == 1 ? pixels.Color(0, 0, 255) :
         ChargingStage == 4 ? pixels.Color(255, 0, 0) :
         pixels.Color(0, 255, 0)) :
        pixels.Color(0, 0, 0);
    }

    for (int i = 0; i < 14; i++) pixels.setPixelColor(i, color);
    pixels.show();
    vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}


/*
================= ChargingStage Mapping =================

StageID   | ความหมาย (Description)                        
------------------------------------------------------------
0         | Initial / Idle                                
          | = ไม่ได้อยู่บนแท่นชาร์จ / หรือออกจากแท่นแล้ว  
          | LED แสดง: เขียวค้าง (Green Solid)             

1         | One plate sensor ถูกกด (เข้า Dock ยังไม่สมบูรณ์)
          | = ยังไม่พร้อมชาร์จ                            
          | LED แสดง: น้ำเงินกระพริบ (Blue Blinking)       

3         | ทั้งสอง sensor ถูกกดพร้อมกัน                  
          | = eMR เข้า Dock ตรงตำแหน่งแล้ว รอเริ่มชาร์จ   
          | LED แสดง: แดงค้าง (Red Solid)                  

4         | กำลังชาร์จอยู่ (Relay ON)                      
          | = ได้รับคำสั่ง ReadyToCharge และ Dock เปิดรีเลย์
          | LED แสดง: แดงกระพริบ (Red Blinking)            

5         | ชาร์จเต็มแล้ว                                   
          | = eMR แจ้ง FullyCharged และ Dock ปิดรีเลย์       
          | LED แสดง: เขียวกระพริบ (Green Blinking)        

6         | Idle (State reset หลังการชาร์จเต็ม)             
          | = กลับไปสภาวะพัก                               
          | LED แสดง: เขียวค้าง (Green Solid)              

------------------------------------------------------------
สรุปสี LED Strip:
- Stage 0,6  → Green Solid (เขียวค้าง)
- Stage 1    → Blue Blinking (น้ำเงินกระพริบ)
- Stage 3    → Red Solid (แดงค้าง)
- Stage 4    → Red Blinking (แดงกระพริบ)
- Stage 5    → Green Blinking (เขียวกระพริบ)
============================================================
*/

void MonitorState(void *param) {
  while (1) {
    if (DockStage != prevDockStage) {
      Serial.println("DockStage: " + String(DockStage));
      prevDockStage = DockStage;
    }
    if (ChargingStage != prevChargingStage) {
      Serial.println("ChargingStage: " + String(ChargingStage));
      prevChargingStage = ChargingStage;
    }
    vTaskDelay(500 / portTICK_PERIOD_MS);
  }
}

// ======================= Main =======================
void setup() {
  pinMode(SENSOR1_PIN, INPUT);
  pinMode(SENSOR2_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(CONST_HIGH_PIN, OUTPUT);
  digitalWrite(CONST_HIGH_PIN, HIGH);
  digitalWrite(RELAY_PIN, LOW);

  Serial.begin(9600);
  IRSerial.begin(9600, SERIAL_8N1, RX1_PIN, TX1_PIN);

  pixels.begin();
  pixels.setBrightness(50);

  xTaskCreate(ChargerChecking, "Checker", 2048, NULL, 2, NULL);
  xTaskCreate(DockIRCommu,    "Commu",   4096, NULL, 3, NULL);
  xTaskCreate(LEDDisplay,     "LED",     2048, NULL, 1, NULL);
  xTaskCreate(MonitorState,   "Monitor", 2048, NULL, 1, NULL);
  xTaskCreate(BlinkBuiltinLED,"Blink",   1024, NULL, 1, NULL);
}

void loop() { 
  vTaskDelay(portMAX_DELAY); 
}