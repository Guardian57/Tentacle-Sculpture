#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 4

// define pins

int reverseSwitch = 2;


const int stepperPins[][2] = {
  {6, 7},
  {8, 9},
  {10, 11},
  {12, 13}
}; // (address, PUL, DIR)

int stepperInfo[][3] = {{1500, 700, 0},
                        {1500, 700, 0},
                        {1500, 700, 0},
                        {1500, 700, 0}                   
                      }; //(maxSpeed, acceleration, target pos (degrees))
                      
long positions[] = {0, 0, 0, 0};


int ppr = 3000; //pulse per revolution based on stepper driver

//Stepper handlers
AccelStepper stepper[M_NUM]; 
MultiStepper steppers;

byte motorData = 0;


// variables for reading data from pi
String str = "";
int data[32];
int motorInfo[M_NUM];
volatile boolean receiveFlag = false;

boolean moving = false;


void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  Wire.begin(0x8);  

  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendData);

  Serial.begin(9600);

  for(int i = 0; i < M_NUM; i++){
    
    //define stepper
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    
    //configure stepper
    stepper[i].setMaxSpeed(stepperInfo[i][0]);
    stepper[i].setSpeed(stepperInfo[i][0]);
    stepper[i].setAcceleration(stepperInfo[i][1]);
    
    //add stepper to MultiStepper
    steppers.addStepper(stepper[i]);
    
  }

}

// the loop function runs over and over again forever
void loop() {

  // checks for message from pi
  if (receiveFlag == true) {
    parseCommand(); // parses new string for commands
    receiveFlag = false;
  }

  
  // runs the motors
  for(int i = 0; i < M_NUM; i++){
    
    stepper[i].run();
    updateMotorData();
  }
  
  
}



void receiveEvent(int howMany){ // took this off the interwebs. gets a string command from the pi
  for(int i = 0; i < 32; i++){
    data[i] = '\0';
    
    
  }
  
  Serial.print(String(howMany) + " received: ");
  
  for(int i = 0; i < howMany;i++){
    data[i] = Wire.read();
    Serial.print(String(data[i]) + "_");
    
  }
  Serial.println();
  
  bitWrite(motorData, 0, 1);
  receiveFlag = true;

}

void sendData()
{
  printMotorData();
  Wire.write(motorData);
}


void parseCommand(){ 

  if(data[5] == 1){
    
    Serial.println("Reset pog");
    for (int i = 0; i < M_NUM; i++) {
      //rotate calibrate celebrate
      positions[i] = 0;
      stepper[i].setCurrentPosition(0);
      
    }
  }
  else{
    
    for(int i = 0; i < M_NUM; i++){
      Serial.println(data[i+1]);
      int target = map(data[i+1], 0, 255, 0, 360); // plus is because arduino is bad and i am bad
      stepperInfo[i][2] = target;
      pulse(i, target);
    }
  }
  
  
}

void pulse(int stpr, int deg){
      String printer = "pulse " + String(stpr) + " " + String(deg);
      Serial.println(printer);
      Serial.println();
      //converts degrees into pulses factoring in micro steps
      float pulseDeg = 360.0f/ppr;
      positions[stpr] = deg;
      long pulsePositions[M_NUM];
      
      bitWrite(motorData, stpr, 1);
      //printMotorData();
      stepper[stpr].moveTo(positions[stpr]/pulseDeg);
      
      
      
}

void updateMotorData(){
  byte oldData = motorData;
  for(int i = 0; i < M_NUM; i++){
    if(stepper[i].isRunning()){
      bitWrite(motorData, i, 1);
    }
    else{
      bitWrite(motorData, i, 0);
    }
  }
  if(oldData != motorData){
  //printMotorData();
  }
}

void printMotorData(){
  for(int i = 7; i >= 0; i--){
    Serial.print(bitRead(motorData, i));
  }
  Serial.println();
  Serial.println();
}
