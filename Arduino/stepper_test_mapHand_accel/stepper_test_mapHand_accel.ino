/*
  
*/

#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 4 //number of motors being driven

#define CW_BUTT 4 //button for manually controlling motor CW
#define CCW_BUTT 8 //manually controlling motor CCW
#define MOTOR_TOGGLE 3 //button switching between motors


// Defin pins



const int stepperPins[][2] = {{10, 11},                          
                              {12, 13},
                              {6, 7},
                              {11, 12}
                             }; // (address, PUL, DIR)

int stepperInfo[][3] = {{700, 100, 0},
                        {700, 100, 0},
                        {700, 100, 0},
                        {700, 100, 0}                   
                      }; //(maxSpeed, acceleration, target pos (degrees))

long positions[M_NUM];


int ppr = 400; //pulse per revolution based on stepper driver
int mSteps = 1; //amout of steps to move based on ppr. default 1
float pulseDeg = 1.8;
boolean isProcessing = false;

//Stepper handlers
AccelStepper stepper[M_NUM]; 
MultiStepper steppers;

//temporary holding array for info set over i2c
byte dataArray[3];

int cntrM = 0; //the current manually controlled motor
boolean isPress = false;
boolean manualCntr = true;

void setup() {
  Serial.begin(9600);
  
  
  for(int i = 0; i < M_NUM; i++){
    
    //define stepper
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    //configure stepper
    stepper[i].setMaxSpeed(1000);

    stepper[i].setAcceleration(700);
    
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

  pulseDeg = 360.0f/ppr;
  mSteps = pulseDeg*10;
}

void receiveEvent(int howMany) {
    
    int degs[M_NUM]; 
    
    while (Wire.available()){
        //isProcessing = true;
        
        for(int i = 0; i < howMany;i++){
            dataArray[i] = Wire.read();
            //Serial.println(dataArray[i]);
          }

          if(dataArray[0] == 0){
            
            //set starting position
            for(int i = 0; i < M_NUM; i++){
              setShaftPos(i , dataArray[1]);
            }
            manualCntr = false;

            }
            
          //Serial.println("i don't get it...");
          if(dataArray[0] == 7){
              
              for(int i = 1; i <= M_NUM; i++){
                  degs[i-1] = dataArray[i];
                  //Serial.println( i + ": " + String(dataArray[i]));
                  
                }
              
              pulse(0, degs);
            }

          
        
      }
  }

void pulse(int stpr, int deg[]){
      
      //converts degrees into pulses factoring in micro steps
      float pulseDeg = 360.0f/ppr;
      
      for(int i = 0; i < 2; i++){
           positions[i] = deg[i]/pulseDeg;
           Serial.println(String(i) + ": " + positions[i]);
        }
        Serial.println("why");
      
     
      
      
      moveStep(); 
        
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
      float pulseDeg = 360.0f/ppr;
      int steps = current/pulseDeg;
      
      stepper[stepr].setCurrentPosition(steps);
      Serial.println("Stepper " + String(stepr) + " current Pos set to " + String(current));
  }

void moveStep(){
    

    for(int i = 0; i < M_NUM; i++) {
        stepper[i].moveTo(positions[i]);
      }
    
    Serial.println("wahhhaat");
    
    
  }

void loop() {
    
    
    

    if(digitalRead(MOTOR_TOGGLE)==HIGH and isPress == false){ //switch motors for manual control
        cntrM = (cntrM + 1) % M_NUM;
        Serial.println("controlling Motor " + String(cntrM));
        isPress = true;
      } else if(digitalRead(3)==LOW and isPress == true) {
          isPress = false;
        }
    
    
    
    if(digitalRead(CW_BUTT)==HIGH){ //manual control CW
        
        stepper[cntrM].move(mSteps);
        //Serial.println("go");
        
     }

     if(digitalRead(CCW_BUTT)==HIGH){ //manual control CCW
        
        stepper[cntrM].move(-mSteps);
     }

     if(manualCntr){
        stepper[cntrM].run();
     }
     else { 
        for(int i = 0; i < M_NUM; i++) {
        stepper[i].run();

        }
      }
     
     
     
     
     //Serial.println(stepper[0].targetPosition());
     //stepper[0].run();
    
}
