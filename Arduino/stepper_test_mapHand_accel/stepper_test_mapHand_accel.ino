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
int driverDIR = 6;


const int stepperPins[][2] = {{7, 6},
                              {0, 0}
                             }; // (address, PUL, DIR)

int stepperInfo[][2] = {{700, 100},
                        {700, 100},
                        {700, 100}                     
                      }; //(maxSpeed, acceleration)


boolean setdir = LOW; // Set Direction
int ppr = 800; //pulse per revolution based on stepper driver
boolean isProcessing = false;

AccelStepper stepper[2]; 

byte dataArray[3];

// Interrupt Handler

void revmotor (){

  setdir = !setdir;
  Serial.println("Boop");
  
}


void setup() {
  Serial.begin(9600);
  
  
  for(int i = 0; i < 2; i++){
    Serial.println("d");
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    
    pinMode (stepperPins[i][0], OUTPUT);
    pinMode (stepperPins[i][1], OUTPUT);
    
  }
  
  pinMode (8, INPUT);
  pinMode (4, INPUT);
  pinMode (2, INPUT);
  
  
  
  Wire.begin(0x8);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendState); 

  stepper[0].setMaxSpeed(700);
  stepper[0].setAcceleration(100);
  
}

void receiveEvent(int howMany) {
    
    while (Wire.available()){
        for(int i = 0; i < howMany;i++){
            dataArray[i] = Wire.read();
            //Serial.println(dataArray[i]);
          }

          pulse(dataArray[0], dataArray[1], dataArray[2]);
        
      }
  }

void pulse(int stpr, int deg, int dir){
      
      float pulseDeg = 360.0f/ppr;
      int pulsesNeeded = deg/pulseDeg;
     
      stepper[0].setMaxSpeed(700);
      stepper[0].setAcceleration(100);
      
      stepper[0].moveTo(pulsesNeeded);
          
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

void setShaftPos(int stepr, int current) { //sets the current pos of the stepper. takes in the stepper array index and desired pos of the stepper
      stepper[stepr].setCurrentPosition(current);
      Serial.println("Stepper " + String(stepr) + " current Pos set to " + String(current));
  }

void loop() {
    
    
    if(stepper[0].distanceToGo() != 0) {
       stepper[0].run();
    }
    
    if(digitalRead(2)==LOW){
        //insert
        setShaftPos( 0, 10);
    }
    
    if(digitalRead(4)==HIGH){
       
        stepper[0].move(15);
        Serial.println("go");
        
     }

     if(digitalRead(8)==HIGH){
        
        stepper[0].move(-15);
     }
     //Serial.println(stepper[0].targetPosition());
     stepper[0].run();
    
}
