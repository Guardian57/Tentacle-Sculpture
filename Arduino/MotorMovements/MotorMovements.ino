#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 2

// define pins

int reverseSwitch = 2;


const int stepperPins[][2] = {
  {7, 6},
  {12, 11}
}; // (address, PUL, DIR)

int stepperInfo[][3] = {{700, 100, 0},
                        {700, 100, 0}                   
                      }; //(maxSpeed, acceleration, target pos (degrees))
                      
long positions[] = {0, 0, 0, 0};


int ppr = 3000; //pulse per revolution based on stepper driver

//Stepper handlers
AccelStepper stepper[M_NUM]; 
MultiStepper steppers;

// variables for tracking incoming and outgoing data

byte motorData = 0;



String str = "";
char chars[32];
volatile boolean receiveFlag = false;
String runCommands = "";


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
    stepper[i].setMaxSpeed(500);
    
    stepper[i].setAcceleration(100);
    
    //add stepper to MultiStepper
    steppers.addStepper(stepper[i]);
    
  }

}

// the loop function runs over and over again forever
void loop() {
  
  if (receiveFlag == true) {
    parseString(str); // parses new string for commands
    receiveFlag = false;
  }

  
  stepper[0].run();
  
  
  //printMotorData();
  
}



void receiveEvent(int howMany){ // took this off the interwebs. gets a string command from the pi
  for(int i = 0; i < 32; i++){
    chars[i] = '\0';
  
  }
  for (int i = 0; i < howMany; i++) {
    
    chars[i] = Wire.read();
    chars[i + 1] = '\0'; //add null after ea. char
  } 

  for (int i = 0; i < howMany; ++i)
    chars[i] = chars[i + 1];

  str = chars; // probs don't need this but it's here in case we do
  
  Serial.println(str);
  
  receiveFlag = true;
  printMotorData();

}

void sendData()
{
  //Serial.println(motorData);
  Wire.write(motorData);
}


void parseString(String cmd){ 
  
  if(cmd.indexOf("_") >= 0){
    
    int motorNum = cmd.substring(0, 1).toInt();
    int targetNum = cmd.substring(2, cmd.length()).toInt();
    Serial.println(String(motorNum) + "_" + String(targetNum));
    stepperInfo[motorNum][2] = targetNum;
    pulse(motorNum, targetNum);
    
  }

  if(cmd.indexOf("reset")>= 0){
    Serial.println("Reset pog");
    for (int i = 0; i < M_NUM; i++) {
      //rotate calibrate celebrate
  
    }
  }
  //Serial.println(runCommands);

}

void pulse(int stpr, int deg){
  
      Serial.println("pulse " + String(stpr) + " " + String(deg));
      //converts degrees into pulses factoring in micro steps
      float pulseDeg = 360.0f/ppr;
      positions[stpr] = deg/pulseDeg;
      stepper[stpr].moveTo(deg/pulseDeg);
      //steppers.moveTo(positions);
      
      
      /*
      for(int i = 0; i < 2; i++){
           positions[i] = deg[i]/pulseDeg;
           Serial.println(String(i) + ": " + positions[i]);
        }
        Serial.println("i want to throw myself into the sea");
      */
     
      
}

void printMotorData(){
  for(int i = 7; i >= 0; i--){
    Serial.print(bitRead(motorData, i));
  }
  Serial.println();
  Serial.println(motorData);
  Serial.println();
}
