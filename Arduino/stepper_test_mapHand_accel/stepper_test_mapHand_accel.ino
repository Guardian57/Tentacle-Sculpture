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
byte prevHalls[4] = {1, 1, 1, 1};

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

int cntrM = 0; //motor that is being manually controlled
boolean isPress = false;

byte homingState = 0; //the current homing state of the motor. 0 - searching for hall enter, 1 - searching for hall exit
int enterPos = NULL;
int exitPos = NULL;
byte triggerNum = 0; // number of times the hall effect has entered or exited the sensor

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
    stepper[i].setMaxSpeed(5000);
    stepper[i].setAcceleration(5000);
    //stepper[i].setSpeed(2000);
    
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

void setAllSpeed(int speedMax, int Accel) { //sets all motor speed and acceleration
    for (int i = 0; i < M_NUM; i++) {
        stepper[i].setMaxSpeed(speedMax);
        stepper[i].setAcceleration(Accel);
      }
  }

void receiveEvent(int howMany) { // triggers when pi sends a command
    
    int degs[M_NUM]; 
    
    while (Wire.available()){
        isProcessing = true; //turns true to prevent commands while processing existing command
        
        for(int i = 0; i < howMany;i++){
            dataArray[i] = Wire.read(); // reads the information sent by pi
            //Serial.println(dataArray[i]);
          }
          
          if(dataArray[0] == 0){ // sets motor locations to zero if data array starts with zero
            //is not moving the motors, instead is changing the label of their location
            //set starting position
            Serial.println("sending start position");
            for(int i = 0; i < M_NUM; i++){
              setShaftPos(i , dataArray[1]);
              }
            

            }

          if (dataArray[0] == 9) { // triggers to home motors
            Serial.println("Sending Home motors"); 
            for(int i = 0; i < M_NUM; i++){
              
              setShaftPos(i, 0); // sets motor position to 0 so it will spin 360 from current location
              
              }
              
              
              homeStepIndex = 0; //sets the index of the stepper being homed
              
              homingState = 0; //sets the initial state of the stepper motor for the switch statment below
              
              prevHalls[homeStepIndex] = halls[homeStepIndex]; //sets the current and previous positions to the same so nothing is triggered imediatly 
              
              setAllSpeed(2000, 10000); //slows the motor for homing to prevent seizing 
              pulse(homeStepIndex,405); //spin the first motor 360 degrees to find the hall sensor
            
            
            
              homing = true;
          }  
            

          if(dataArray[0] == 7){ // in charge of moving the motors
              
              
              for(int i = 1; i <= M_NUM; i++){
                  //degs[i-1] = dataArray[i]; // reads the angles sent through pi
                  //Serial.println( i + ": " + String(dataArray[i]));
                  pulse(i-1, dataArray[i]); // command to set motor targets
                }
              
            }

          if(dataArray[0] == 8){ // in charge of moving the motors for animation

              setAllSpeed(dataArray[5] * 100,dataArray[6] * 100); // sets the speed and accel for each new position
              
              for(int i = 1; i <= M_NUM; i++){
                  //degs[i-1] = dataArray[i]; // reads the angles sent through pi
                  //Serial.println( i + ": " + String(dataArray[i]));
                  pulse(i-1, dataArray[i]); // command to set motor targets
                }
              
            }  

            if(dataArray[0] == 10){ // in charge of changing speed of motors
              Serial.println("changed Speed");
              setAllSpeed(dataArray[1] * 100, dataArray[2] * 100); // sets the speed and accel for each new position
              
              
              
            }  

      }
  }

void pulse(int stpr, int deg){
      
      //converts degrees into pulses factoring in micro steps
      float pulseDeg = 360.0f/ppr;
      
     
           positions[stpr] = deg/pulseDeg; // calculates the new position based on degrees
           //Serial.println(String(i) + ": " + positions[i]);
       
        
      
      moveStep(stpr); // moves a step
        
    }

void sendState(){ 
  //sends a 1 or 0 depending on if the arduino is busy to prevent pi from overloading arduino
      byte num;
      if(isProcessing){
          num = 0x00; // arduino is busy
          //Serial.println("Busy");
        } else if (!isProcessing) {
          num = 0x01; // arduino is not busy
          //Serial.println("Not busy");
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

void moveStep(int stpr){ // moves the motors
  //Serial.println("Move step");
    
        stepper[stpr].moveTo(positions[stpr]);
        //Serial.println("Move motor " + String(i));
      
  }



void homeMotors() {

    // uncommenting the print statements will slow down motors
    // should only be done to bug test hall effect sensors

    // reads hall effect sensors
    
    halls[0] = digitalRead(hall0);
    halls[1] = digitalRead(hall1);
    halls[2] = digitalRead(hall2);
    halls[3] = digitalRead(hall3);
    
    
    switch (homingState){
      case 0: //sees if the hall-effect is already in the homing zone 
      
        if(halls[homeStepIndex] != 0) {          
          homingState = 1;
          Serial.println("Outside Homing Range");
        } else {
          homingState = 3;
          Serial.println("Inside Homing Range");
        }
      
      break;
      
      case 1: // looks for entry into the homing zone 
      
        if(halls[homeStepIndex] != prevHalls[homeStepIndex]) {          
          enterPos = stepper[homeStepIndex].currentPosition(); //sets the entry position
          Serial.println("set enter point");
          homingState = 2; // changes to next state on next loop iteration 
        }
      
      break;
      
      case 2: // looks for exit of the homing zone
      
        if(halls[homeStepIndex] != prevHalls[homeStepIndex]) {
          exitPos = stepper[homeStepIndex].currentPosition(); //sets the exit position
          Serial.println("set exit point");
          stepper[homeStepIndex].stop(); // stops the motor as quickly as possible (with acceleration)
          int center = exitPos - (abs(exitPos - enterPos)/2); //finds the half of the difference of the entry and exit positions and subtracts it from the exit position to find the center of the magnetic field
          stepper[homeStepIndex].moveTo(center); // moves to the center position
          homingState = 10; //changes to next state on next loop iteration
        }
 
      break;

      case 3: //looks for the end position first (since already within homing zone)
      
      if(halls[homeStepIndex] > prevHalls[homeStepIndex]){
        exitPos = stepper[homeStepIndex].currentPosition(); //sets the exit position
        Serial.println("found end pos");
        stepper[homeStepIndex].stop(); // stops the motor as quickly as possible (with acceleration)
        pulse(homeStepIndex,-405); //starts rotating motor CCW to prepare to find enter position
        homingState = 4; //changes to next state on next loop iteration
        }
        
      break;

      case 4:
      
        if(halls[homeStepIndex] > prevHalls[homeStepIndex]){    
        enterPos = stepper[homeStepIndex].currentPosition();//sets the enter position
        Serial.println("found enter Pos");
        stepper[homeStepIndex].stop(); // stops the motor as quickly as possible (with acceleration)
        int center = exitPos - (abs(exitPos - enterPos)/2); //finds the half of the difference of the entry and exit positions and subtracts it from the exit position to find the center of the magnetic field
        stepper[homeStepIndex].moveTo(center); // moves to the center position
        homingState = 10; //changes to next state on next loop iteration
        }
       
      break;

      case 10: // waits for stepper to arrive at center before setting 0 position
        
        if( stepper[homeStepIndex].distanceToGo() == 0){
            setShaftPos(homeStepIndex, 90); //sets home position to desired value
            Serial.println("stepper home");
            homingState = 11; //changes to next state on next loop iteration
        }
        
      break;
      
      case 11: // moves on to next motor and if all are homed, ends homing
        
        if(homeStepIndex < 3){ 
          homeStepIndex += 1; // changes index to next motor
          Serial.println("next Motor");
          homingState = 0; // goes back to original homing state
          pulse(homeStepIndex,405); //turns the motor CW to prepare for homing
        } else {    
          setAllSpeed(7000, 7000); //sets motor speed and accel 
          Serial.println("all motors homed. proceed to checkout");
          homing = false; //ends homing 
          isProcessing = false;
          Serial.println("hit");    
        }
        
      break;
      
      default:

      break;
      
      }
      
      prevHalls[homeStepIndex] = halls[homeStepIndex]; // updates previous homing position for comparison on next loop iteration

    }
    

void loop() {

    // if the device is homing, it does that
    // if homing has been finished, it'll do everything else
    if(homing == true){
      homeMotors();   
     }
    
    
      if(digitalRead(MOTOR_TOGGLE)==HIGH and isPress == false){ //switch motors for manual control
          cntrM = (cntrM + 1) % M_NUM;
          Serial.println("controlling Motor " + String(cntrM));
          delay(100); //prevent debouncing
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
            if(homing == false){
              isProcessing = false; //checks if motors have reached target and stops processing if yes
            }
          }
//        }
       

    
     
    
}
