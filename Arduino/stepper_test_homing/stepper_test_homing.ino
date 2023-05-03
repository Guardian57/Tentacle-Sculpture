/*

*/

#include <Wire.h>
#include <AccelStepper.h>
#include <MultiStepper.h>

#define M_NUM 4 //number of motors being driven

#define CW_BUTT 4 //button for manually controlling motor CW
#define CCW_BUTT 5 //manually controlling motor CCW
#define MOTOR_TOGGLE 3 //button switching between motors


// Defin pins



const int stepperPins[][2] = {{10, 11},
  {12, 13},
  {6, 7},
  {8, 9}
}; // (address, PUL, DIR)

int stepperInfo[][3] = {{700, 100, 0},
  {700, 100, 0},
  {700, 100, 0},
  {700, 100, 0}
}; //(maxSpeed, acceleration, target pos (degrees))

long positions[M_NUM];

#define hall0 0
#define hall1 1
#define hall2 2
#define hall3 3
int halls[] = {1, 1, 1, 1};


int ppr = 400; //pulse per revolution based on stepper driver
int gearBoxRatio = 15; //gearbox ratio, how many revolutions of stepper it takes to move gearbox shaft 360 deg
int mSteps = 1; //amout of steps to move based on ppr. default 1
float pulseDeg = 1.8;
boolean isProcessing = false;
boolean homed = false;


//Stepper handlers
AccelStepper stepper[M_NUM];
MultiStepper steppers;

//temporary holding array for info set over i2c
// NOTE: WAS 3, changing to 5 removed warning, may break.
byte dataArray[5];

int cntrM = 0; //the current manually controlled motorco
boolean isPress = false;
boolean manualCntr = true;

void setup() {
  Serial.begin(9600);

  pinMode(hall0, INPUT_PULLUP);
  pinMode(hall1, INPUT_PULLUP);
  pinMode(hall2, INPUT_PULLUP);
  pinMode(hall3, INPUT_PULLUP);

  for (int i = 0; i < M_NUM; i++) {

    //define stepper
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    //configure stepper
    stepper[i].setMaxSpeed(4000);
    stepper[i].setSpeed(500);
    stepper[i].setAcceleration(2000);

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

  ppr = ppr * gearBoxRatio;
  pulseDeg = 360.0f / ppr;
  mSteps = pulseDeg * 1000;


  homeMotors();
}

void receiveEvent(int howMany) {
  
  int degs[M_NUM];
  
  
  if(!isProcessing){
    
    isProcessing = true;
    
  //while (Wire.available()) {
  
    
    
    for (int i = 0; i < howMany; i++) {
      dataArray[i] = Wire.read();
      Serial.print(String(dataArray[i]) + "_");

    }
    
    Serial.println(" ");
    
    if (dataArray[howMany - 1] == 2) { //somehow this must be triggering first
      
      //homeMotors(); 
      //isProcessing = false;
      //homed = true;
      //Serial.println("Homed");
    }

    
    

    if (dataArray[0] == 0) {
      //set starting position
      for (int i = 0; i < howMany; i++) {
        setShaftPos(i , dataArray[1]);
      }
      manualCntr = false;
    }


    //Serial.println("i don't get it...");
    if (dataArray[0] == 7) {

      for (int i = 1; i <= M_NUM; i++) {
        degs[i - 1] = dataArray[i];
        //Serial.println( i + ": " + String(dataArray[i]));

      }

      pulse(0, degs);
      isProcessing = false;
    }
    
  }
  
  
}

void pulse(int stpr, int deg[]) {

  //converts degrees into pulses factoring in micro steps
  float pulseDeg = 360.0f / ppr;

  for (int i = 0; i < M_NUM; i++) {
    positions[i] = deg[i] / pulseDeg;
    Serial.println(String(i) + ": " + positions[i]);
  }
  Serial.println();

  moveStep();

}

void sendState() {
  byte num;
  if (isProcessing) {
    num = 0x00;
  } else if (!isProcessing) {
    num = 0x01;
  }

  Wire.write(num);

}

void setShaftPos(int stepr, int current) { //sets the current pos of the stepper. takes in the stepper array index and desired pos of the stepper
  float pulseDeg = 360.0f / ppr;
  int steps = current / pulseDeg;

  stepper[stepr].setCurrentPosition(steps);
  Serial.println("Stepper " + String(stepr) + " current Pos set to " + String(current));
}

void moveStep() {


  for (int i = 0; i < M_NUM; i++) {
    stepper[i].moveTo(positions[i]);
  }

  Serial.println("Movement Complete");


}


void homeMotors() {
  Serial.println("home motors");
  //delay(1000);
  //Serial.println("outofloop");
  boolean homedHere = false;
  String oldNum = "";
  String num = "";
  
  while (homedHere == false) {
    
    //Serial.println("homing");
    halls[0] = digitalRead(hall0);
    Serial.print(halls[0]);
    halls[1] = digitalRead(hall1);
    Serial.print(halls[1]);
    halls[2] = digitalRead(hall2);
    Serial.print(halls[2]);
    halls[3] = digitalRead(hall3);
    Serial.print(halls[3]);
    Serial.println();
    boolean homed = true;
    for(int i = 0; i < 4; i++){
      if(halls[i] != 0){
        stepper[i].runSpeed();
        homed = false;
      }
    }
    
    homedHere = homed;
    
    
    
  }



}

void loop() {



  /*
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
    }*/
  //else {
  if (true) {
    for (int i = 0; i < M_NUM; i++) {
      stepper[i].run();

    }
    if (stepper[0].distanceToGo() == 0 && stepper[1].distanceToGo() == 0 && stepper[2].distanceToGo() == 0 && homed)
      isProcessing = false; // UNCOMMENT THIS LATER
      
  }




  //Serial.println(stepper[0].targetPosition());
  //stepper[0].run();

}
