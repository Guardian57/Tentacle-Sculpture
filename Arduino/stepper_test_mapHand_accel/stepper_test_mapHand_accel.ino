/*
  
*/

#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 2 //number of motors being driven

// Defin pins

int reverseSwitch = 2;  // Push button for reverse
int driverPUL = 7;    // PUL- pin
int driverDIR = 6;


const int stepperPins[][2] = {{7, 6},
                              {12, 11}
                             }; // (address, PUL, DIR)

int stepperInfo[][3] = {{700, 100, 0},
                        {700, 100, 0},
                        {700, 100, 0}                     
                      }; //(maxSpeed, acceleration, target pos (degrees))
long positions[M_NUM];


int ppr = 800; //pulse per revolution based on stepper driver
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
    stepper[i].setMaxSpeed(500);

    stepper[i].setAcceleration(100);
    
    //add stepper to MultiStepper
    steppers.addStepper(stepper[i]);
    
  }

  //sets button pinMode
  pinMode (8, INPUT);
  pinMode (4, INPUT);
  pinMode (2, INPUT);
  pinMode (3, INPUT);
  
  
  
  Wire.begin(0x8);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendState); 

  
  
}

void receiveEvent(int howMany) {
    
    int degs[M_NUM]; 
    
    while (Wire.available()){
        isProcessing = true;
        
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
    steppers.moveTo(positions);
    
    
    Serial.println("wahhhaat");
    
  }

void loop() {
    
    
    

    if(digitalRead(3)==HIGH and isPress == false){
        cntrM = (cntrM + 1) % M_NUM;
        Serial.println("controlling Motor " + String(cntrM));
        isPress = true;
      } else if(digitalRead(3)==LOW and isPress == true) {
          isPress = false;
        }
    
    if(digitalRead(2)==LOW){
        //insert
        setShaftPos( 0, 0);
    }
    
    if(digitalRead(4)==HIGH){
       
        stepper[cntrM].move(15);
        //Serial.println("go");
        
     }

     if(digitalRead(8)==HIGH){
        
        stepper[cntrM].move(-15);
     }

     if(manualCntr){
        stepper[cntrM].run();
      } else {
          steppers.runSpeedToPosition();
          isProcessing = false;
        }
     
     
     
     //Serial.println(stepper[0].targetPosition());
     //stepper[0].run();
    
}
