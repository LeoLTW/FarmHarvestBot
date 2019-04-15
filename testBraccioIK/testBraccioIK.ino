
#include <Braccio.h>
#include <Servo.h>
#include <InverseK.h>
#include <SoftwareSerial.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

SoftwareSerial BTSerial(14, 15); // RX | TX

void setup() {
  Serial.begin(9600);
  BTSerial.begin(9600);
  BTSerial.println("Ready");
  Braccio.begin();

  // Setup the lengths and rotation limits for each link
  Link base, upperarm, forearm, hand;
  
  base.init(0, b2a(0.0), b2a(180.0));
  upperarm.init(125, b2a(15.0), b2a(165.0));
  forearm.init(125, b2a(0.0), b2a(180.0));
  hand.init(195, b2a(0.0), b2a(180.0));

  // Attach the links to the inverse kinematic model
  InverseK.attach(base, upperarm, forearm, hand);
}

int dg1 = 97;
int dg2 = 99;
int dg3 = 98;
int dg4 = 103;
int dg5 = 88;
int dg6 = 73;
// 角度校正
int os1 = dg1-90;
int os2 = dg2-90;
int os3 = dg3-90;
int os4 = dg4-90;
int os5 = dg5-90;

void loop() {
  /*
   Step Delay: a milliseconds delay between the movement of each servo.  Allowed values from 10 to 30 msec.
   M1=base degrees. Allowed values from 0 to 180 degrees
   M2=shoulder degrees. Allowed values from 15 to 165 degrees
   M3=elbow degrees. Allowed values from 0 to 180 degrees
   M4=wrist vertical degrees. Allowed values from 0 to 180 degrees
   M5=wrist rotation degrees. Allowed values from 0 to 180 degrees
   M6=gripper degrees. Allowed values from 10 to 73 degrees. 10: the toungue is open, 73: the gripper is closed.
  */

  // the arm is aligned upwards  and the gripper is closed
                        //(step delay, M1, M2, M3, M4, M5, M6);
  // Braccio.ServoMovement(20,         dg1, dg2, dg3, dg4, dg5, dg6);

    
  float a0, a1, a2, a3;
  int x, y, z;
  int m1 = dg1, m2 = dg2, m3 = dg3, m4 = dg4, m5 = dg5, m6 = dg6;
  char cmd[1];

  while ( BTSerial.available() ) {
//    *data = BTSerial.read();
    //Serial.write(BTSerial.read());
    String data = BTSerial.readString();// read the incoming data as string
    Serial.println(data);
    sscanf(data.c_str(), "%1s:%d,%d,%d", &cmd, &x, &y, &z);
    Serial.print(cmd); Serial.print(',');
    Serial.print(x); Serial.print(',');
    Serial.print(y); Serial.print(',');
    Serial.println(z);
    if ( strcmp(cmd, "c")  == 0 ) {
      if(InverseK.solve(x, y, z, a0, a1, a2, a3)) {
        Serial.print(a2b(a0)); Serial.print(',');
        Serial.print(a2b(a1)); Serial.print(',');
        Serial.print(a2b(a2)); Serial.print(',');
        Serial.println(a2b(a3));
        m1 = a2b(a0)+os1, m2 = a2b(a1)+os2, m3 = a2b(a2)+os3, m4 = a2b(a3)+os4;
        m5 = dg5;
      } else {
        Serial.print(a2b(dg1)); Serial.print(',');
        Serial.print(a2b(dg2)); Serial.print(',');
        Serial.print(a2b(dg3)); Serial.print(',');
        Serial.println(a2b(dg4));
        m1 = dg1, m2 = dg2, m3 = dg3, m4 = dg4, m5 = dg5, m6 = dg6;
      }
    }
    else if ( strcmp(cmd, "s")  == 0 ) {
     if(InverseK.solve(x, y, z, a0, a1, a2, a3)) {
        Serial.print(a2b(a0)); Serial.print(',');
        Serial.print(a2b(a1)); Serial.print(',');
        Serial.print(a2b(a2)); Serial.print(',');
        Serial.println(a2b(a3));
        m1 = a2b(a0)+os1, m2 = a2b(a1)+os2, m3 = a2b(a2)+os3, m4 = a2b(a3)+os4;
        m5 = dg5, m6=73;
      }
    }
     else if ( strcmp(cmd, "o")  == 0 ) {
      if(InverseK.solve(x, y, z, a0, a1, a2, a3)) {
        Serial.print(a2b(a0)); Serial.print(',');
        Serial.print(a2b(a1)); Serial.print(',');
        Serial.print(a2b(a2)); Serial.print(',');
        Serial.println(a2b(a3));
        m1 = a2b(a0)+os1, m2 = a2b(a1)+os2, m3 = a2b(a2)+os3, m4 = a2b(a3)+os4;
        m5 = dg5, m6=0;
      }
    }
    else {
      m1 = x, m2 = y, m3 = z, m4 = dg4, m5 = dg5, m6 = dg6;
    }
    Braccio.ServoMovement(30,         m1, m2, m3, m4, m5, m6);
 }
}

// Quick conversion from the Braccio angle system to radians 
float b2a(float b){ 
  return b / 180.0 * PI - HALF_PI;
}

// Quick conversion from radians to the Braccio angle system
float a2b(float a) { 
  return (a + HALF_PI) * 180 / PI;
}
