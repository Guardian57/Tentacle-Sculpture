/*
  
*/

#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 4 //number of motors being driven

#define CW_BUTT 4 //button for manually controlling motor CW
#define CCW_BUTT 5 //manually controlling motor CCW
#define MOTOR_TOGGLE 3 //button switching between motors

//defines hall effect pins 
#define hall0 A0
#define hall1 A3
#define hall2 A1
#define hall3 A2
byte halls[] = {1, 1, 1, 1}; // the state of the hall effect senseor. 0 = magnet detected

int offsets[] = {0, 0, 0, -10}; //offset angles to account for sensitive hall sensors

// Defin pins
// stepper motor pins
const int stepperPins[][2] = {{10, 11},                          
                              {12, 13},
                              {6, 7},
                              {8, 9}
                             }; // (address, PUL, DIR)

// information about each individual stepper motor
// useful in case varying speeds and acceleration are desired
int stepperInfo[][3] = {{700, 100, 0},
                        {700, 100, 0},
                        {700, 100, 0},
                        {700, 100, 0}                   
                      }; //(maxSpeed, acceleration, target pos (degrees))

// current motor posistion
long positions[M_NUM];


int ppr = 400; //pulse per revolution based on stepper driver
int gearBoxRatio = 15; //gearbox ratio, how many revolutions of stepper it takes to move gearbox shaft 360 deg
int mSteps = 1; //amout of steps to move based on ppr. default 1
float pulseDeg = 1.8;
byte homeStepIndex = 0;

boolean isProcessing = true; // whether or not the arduino is processing a command
boolean homing = false; // whether the ardunio is homing the sensors
// true by default to home on boot

//Stepper handlers
AccelStepper stepper[M_NUM]; 
MultiStepper steppers;

//temporary holding array for info set over i2c
byte dataArray[5]; //changed this to 5 to remove warnings

int cntrM = 0; //the current manually controlled motor
boolean isPress = false;
boolean manualCntr = true;


void setup() {
  Serial.begin(9600);

  pinMode(hall0, INPUT_PULLUP);
  pinMode(hall1, INPUT_PULLUP);
  pinMode(hall2, INPUT_PULLUP);
  pinMode(hall3, INPUT_PULLUP);
  
  for(int i = 0; i < M_NUM; i++){ //individual motor settings
    
    //define stepper
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    
    // configure stepper
    // acceleration must be set before speed
    stepper[i].setMaxSpeed(10000);
    stepper[i].setAcceleration(5000);
    stepper[i].setSpeed(2000);
    
    //add stepper to MultiStepper
    steppers.addStepper(stepper[i]);
    
  }

  //sets button pinMode
  
  pinMode (CW_BUTT, INPUT);
  pinMode (CCW_BUTT, INPUT);
  pinMode (MOTOR_TOGGLE, INPUT);
  
  
  
  Wire.begin(0x8);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendState); 

  // motor movement information
  ppr = ppr*gearBoxRatio;
  pulseDeg = 360.0f/ppr;
  mSteps = pulseDeg*1000;

  
}

void receiveEvent(int howMany) { // triggers when pi sends a command
    
    int degs[M_NUM]; 
    
    while (Wire.available()){
        isProcessing = true; //turns true to prevent commands while processing existing command
        
        for(int i = 0; i < howMany;i++){
            dataArray[i] = Wire.read(); // reads the information sent by pi
            //Serial.println(dataArray[i]);
          }
          //I THINK THIS IS BUSTED THIS WAS NOT TRIGGERING
          if(dataArray[0] == 0){ // sets motor locations to zero if data array starts with zero
            //is not moving the motors, instead is changing the label of their location
            //set starting position
            Serial.println("sending start position");
            for(int i = 0; i < M_NUM; i++){
              setShaftPos(i , dataArray[1]);
              }
            manualCntr = false;

            }

          if (dataArray[0] == 9) { // triggers to home motors
            Serial.println("Sending Home motors"); 
            for(int i = 0; i < M_NUM; i++){
              stepper[i].setSpeed(2000);
              //stepper[i].run();
              }
            homing = true;
          }  
            

          if(dataArray[0] == 7){ // in charge of moving the motors
              Serial.println("sending motor position");
              manualCntr = false; // TEMPORARY FIX FOR MANUALS NOT SWITCHING OFF
              for(int i = 1; i <= M_NUM; i++){
                  degs[i-1] = dataArray[i]; // reads the angles sent through pi
                  //Serial.println( i + ": " + String(dataArray[i]));
                  
                }
              
              pulse(0, degs); // command to set motor targets
            }

          
        
      }
  }

void pulse(int stpr, int deg[]){
      
      //converts degrees into pulses factoring in micro steps
      float pulseDeg = 360.0f/ppr;
      
      for(int i = 0; i < M_NUM; i++){
           positions[i] = deg[i]/pulseDeg; // calculates the new position based on degrees
           //Serial.println(String(i) + ": " + positions[i]);
        }
        
      
      moveStep(); // moves a step
        
    }

void sendState(){ 
  //sends a 1 or 0 depending on if the arduino is busy to prevent pi from overloading arduino
      byte num;
      if(isProcessing){
          num = 0x00; // arduino is busy
          //Serial.println("Busy");
        } else if (!isProcessing) {
          num = 0x01; // arduino is not busy
          Serial.println("Not busy");
          }
      
      Wire.write(num);
      
    }

void setShaftPos(int stepr, int current) { // sets the current pos of the stepper. takes in the stepper array index and desired pos of the stepper
      // calculations to turn degree angles into motor steps 
      float pulseDeg = 360.0f/ppr;
      int steps = current/pulseDeg;
      
      stepper[stepr].setCurrentPosition(steps); // sets the new current location of motors
      Serial.println("Stepper " + String(stepr) + " current Pos set to " + String(current));
  }

void moveStep(){ // moves the motors
  //Serial.println("Move step");
    for(int i = 0; i < M_NUM; i++) {
        stepper[i].moveTo(positions[i]);
        //Serial.println("Move motor " + String(i));
      }
  }

void homeMotors() {

    // uncommenting the print statements will slow down motors
    // should only be done to bug test hall effect sensors

    
    // reads hall effect sensors
    //Serial.println("homing");
    halls[0] = digitalRead(hall0);
    //Serial.print(halls[0]);
    halls[1] = digitalRead(hall1);
    //Serial.print(halls[1]);
    halls[2] = digitalRead(hall2);
    //Serial.print(halls[2]);
    halls[3] = digitalRead(hall3);
    //Serial.print(halls[3]);
    //Serial.println();

    // sets homing to false, then resets it to true if any motor still needs to move
    // so that homing loop will run again
    if(halls[homeStepIndex%4] != 0){
      stepper[homeStepIndex%4].runSpeed();
      } else {
        homeStepIndex += 1;
        }
    
//    for(int i = 0; i < 4; i++){
//      if(halls[i] != 0){
//        stepper[i].runSpeed(); // runs the motor by the set speed
//      }
//
//    }
//    
    //Serial.println(String(halls[0]) + ", " + String(halls[1]) + ", " + String(halls[2]) + ", " + String(halls[3]));
    if(halls[0] == 0 && halls[1] == 0 && halls[2] == 0 && halls[3] == 0) {
      homing = false; 
      Serial.println("hit");
    }
    
       
    if(!homing){ // sets the shaft locations once homed
      // 90 to ensure straight up and down with drilled holes
      setShaftPos(0, 90 + offsets[0]);
      setShaftPos(1, 90 + offsets[1]);
      setShaftPos(2, 90 + offsets[2]);
      setShaftPos(3, 90 + offsets[3]);
      isProcessing = false;
    }
}

void loop() {

    // if the device is homing, it does that
    // if homing has been finished, it'll do everything else
    if(homing == true){
      homeMotors();   
     }
    else{
    
      if(digitalRead(MOTOR_TOGGLE)==HIGH and isPress == false){ //switch motors for manual control
          cntrM = (cntrM + 1) % M_NUM;
          Serial.println("controlling Motor " + String(cntrM));
          isPress = true;
        } else if(digitalRead(3)==LOW and isPress == true) {
            isPress = false;
          }
      
      if(digitalRead(CW_BUTT)==HIGH){ //manual control Clockwise     
          stepper[cntrM].move(mSteps);
          
       }
  
       if(digitalRead(CCW_BUTT)==HIGH){ //manual control Counterclockwise
         
          stepper[cntrM].move(-mSteps);
       }
  
//       if(manualCntr){
//          stepper[cntrM].run();
//       }
//       
//       
//       else { 
          for(int i = 0; i < M_NUM; i++) { // runs the motors to the target sent by pi
            stepper[i].run();
            //Serial.println("running");
          }
          if(stepper[0].distanceToGo() == 0 && stepper[1].distanceToGo() == 0 && stepper[2].distanceToGo() == 0 && stepper[3].distanceToGo() == 0){
            isProcessing = false; //checks if motors have reached target and stops processing if yes
          }
//        }
       

    }
     
    
}
