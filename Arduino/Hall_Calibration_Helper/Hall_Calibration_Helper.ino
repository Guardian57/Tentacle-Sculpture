/*description

moves all 4 motors to an exact target position from 0 positon for setting the hall effect magnets on the motor shafts. 

instructions
-----------------------
1. manually move motors into desired 0 positon

2. set the variable "targetPos" to the postion that you want the motors to end at 

3. upload script to arduino board and wait for motors to stop

4. for each motor, rotate the hall effect magnet past the sensor a couple of times and note when it becomes out of range on either end.
Use this to position the magnet at the rough center of the magnetic field (between the two falloff points) 

5. tighten the magnet on the shaft and move on to next motor until all magnets are secured to their shafts

*/
#include <AccelStepper.h>

#define M_NUM 4

const int stepperPins[][2] = {{10, 11},                          
                              {12, 13},
                              {6, 7},
                              {8, 9}
                              };

int ppr = 400; //pulse per revolution based on stepper driver
int gearBoxRatio = 15; //gearbox ratio, how many revolutions of stepper it takes to move gearbox shaft 360 deg

float pulseDeg = 1.8;

int targetPos = 90; //the target position of the shaft from current position

AccelStepper stepper[M_NUM];

void setShaftPos(int stepr, int current) { // sets the current pos of the stepper. takes in the stepper array index and desired pos of the stepper
      // calculations to turn degree angles into motor steps 
      float pulseDeg = 360.0f/ppr;
      int steps = current/pulseDeg;
      
      stepper[stepr].setCurrentPosition(steps); // sets the new current location of motors
      Serial.println("Stepper " + String(stepr) + " current Pos set to " + String(current));
  }

void setup() {
  // put your setup code here, to run once:
  
  ppr = ppr*gearBoxRatio;
  pulseDeg = 360.0f/ppr;

  
  for(int i = 0; i < M_NUM; i++){ //individual motor settings
    
    //define stepper
    stepper[i] = AccelStepper(AccelStepper::DRIVER, stepperPins[i][0], stepperPins[i][1]);
    
    // configure stepper
    // acceleration must be set before speed
    stepper[i].setMaxSpeed(5000);
    stepper[i].setAcceleration(5000);
    //stepper[i].setSpeed(2000);
    
    setShaftPos(i , 0);
    stepper[i].moveTo(targetPos/pulseDeg);
  }
}

void loop() {
  
  for(int i = 0; i < M_NUM; i++) { // runs the motors to the target sent by pi
            stepper[i].run();
            //Serial.println("running");
          }
}
