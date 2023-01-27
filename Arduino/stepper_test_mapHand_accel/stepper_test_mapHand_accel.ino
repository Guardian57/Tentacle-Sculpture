/*
  Stepper Motor Test
  stepper-test01.ino
  Uses MA860H or similar Stepper Driver Unit
  Has speed control & reverse switch
  
  DroneBot Workshop 2019
  https://dronebotworkshop.com
*/

#include <Wire.h>
#include <AccelStepper.h>

// Defin pins

int reverseSwitch = 2;  // Push button for reverse
int driverPUL = 7;    // PUL- pin
int driverDIR = 6;    // DIR- pin
int spd = A0;     // Potentiometer

// Variables

int pd = 2500;// Pulse Delay period
int minPd = 3000;
int maxPd = 500;
int speedRange = 500;
boolean setdir = LOW; // Set Direction
int ppr = 400; //pulse per revolution based on stepper driver
boolean isProcessing = false;


byte dataArray[3];

// Interrupt Handler

void revmotor (){

  setdir = !setdir;
  Serial.println("Boop");
}


void setup() {

  AccelStepper(AccelStepper::DRIVER, 7, 6); 
  
  pinMode (driverPUL, OUTPUT);
  pinMode (driverDIR, OUTPUT);
  pinMode (8, INPUT);
  pinMode (4, INPUT);
  
  //attachInterrupt(digitalPinToInterrupt(reverseSwitch), revmotor, FALLING);
  Serial.begin(9600);

  Wire.begin(0x8);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendState);

  speedRange = minPd - maxPd;
  
}

void receiveEvent(int howMany) {
    
    
    while (Wire.available()){
        for(int i = 0; i < howMany;i++){
            dataArray[i] = Wire.read();
            Serial.println(dataArray[i]);
          }

            
        
          
        
          pulse(dataArray[0], dataArray[1], dataArray[2]);
        
      }
  }

  void pulse(int stpr, int deg, int dir){
      
      digitalWrite(driverDIR,dir);
      float pulseDeg = 360.0f/ppr;
      int pulsesNeeded = deg/pulseDeg;
      //Serial.println(pulseDeg); 
      //Serial.println(pulsesNeeded);

      int middle = pulsesNeeded/2;
      int speeds[pulsesNeeded];
      int speedSteps = speedRange/middle;
      Serial.print(pulsesNeeded);
      for(int i = 0; i < pulsesNeeded; i++){
        if(i <= middle){
            speeds[i] = minPd - (i * speedSteps);
            //Serial.println(speeds[i]);
          }
        if(i > middle){
            speeds[i] = maxPd + ((i - middle) * speedSteps);
            //Serial.println(speeds[i]);
          }
          
      }

      
      for(int i = 0; i < pulsesNeeded; i++){ //pulses the motor for the desired steps
      
      digitalWrite(driverPUL,HIGH);
      delayMicroseconds(speeds[i]); //delay determines speed
      digitalWrite(driverPUL,LOW);
      delayMicroseconds(speeds[i]);
      }

      
    }

  void sendState(){
      byte num;
      if(isProcessing){
          num = 0x00;
        } else if (!isProcessing) {
          num = 0x01;
          }
      
      
      Wire.write(num);
    }

void loop() {

    if(digitalRead(4)==HIGH){
        digitalWrite(driverDIR,HIGH);
        digitalWrite(driverPUL,HIGH);
        delayMicroseconds(pd);
        digitalWrite(driverPUL,LOW);
        delayMicroseconds(pd);
     }

     if(digitalRead(8)==HIGH){
        digitalWrite(driverDIR,LOW);
        digitalWrite(driverPUL,HIGH);
        delayMicroseconds(pd);
        digitalWrite(driverPUL,LOW);
        delayMicroseconds(pd);
     }
    /*
    pd = map((analogRead(spd)),0,1023,2000,50);
    digitalWrite(driverDIR,setdir);
    digitalWrite(driverPUL,HIGH);
    delayMicroseconds(pd);
    digitalWrite(driverPUL,LOW);
    delayMicroseconds(pd);
    */
 
}
