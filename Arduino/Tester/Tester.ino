#include <AccelStepper.h> //accelstepper library
//AccelStepper stepper(1, 8, 9); // direction Digital 9 (CCW), pulses Digital 8 (CLK)
//AccelStepper stepper2(1, 10, 11); // direction Digital 11 (CCW), pulses Digital 10 (CLK)
AccelStepper stepper(1, 7, 6); // direction Digital 9 (CCW), pulses Digital 8 (CLK)
AccelStepper stepper2(1, 8, 9); // direction Digital 11 (CCW), pulses Digital 10 (CLK)
AccelStepper stepper3(1, 10, 11); // direction Digital 9 (CCW), pulses Digital 8 (CLK)
AccelStepper stepper4(1, 12, 13); // direction Digital 11 (CCW), pulses Digital 10 (CLK)

int speedy = 0;

void setup() {
  // put your setup code here, to run once:
  stepper.setMaxSpeed(5000); //SPEED = Steps / second  
  stepper.setAcceleration(1000); //ACCELERATION = Steps /(second)^2    
  stepper.setSpeed(500);
  
  
}

void loop() {
  // put your main code here, to run repeatedly:
  speedy+=10;
  stepper.setSpeed(speedy);
  stepper.runSpeed();
  
  delay(500);
}
