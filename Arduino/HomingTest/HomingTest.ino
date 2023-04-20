#include <AccelStepper.h>
#include <MultiStepper.h>


AccelStepper stepper(1, 8, 9); // direction Digital 9 (CCW), pulses Digital 8 (CLK)
AccelStepper stepper2(1, 10, 11); // direction Digital 11 (CCW), pulses Digital 10 (CLK)


//Pins
const byte Analog_X_pin = A0; //x-axis readings
const byte Analog_Y_pin = A1; //y-axis readings
const byte Analog_R_pin = A2; //r-axis readings
const byte LED_pin = 3; //PWM output for LED

#define sensorPin  6 // pin 4 
//#define relayPin 8 // pin
#define ledPin 13

//Variables
int Analog_X = 0; //x-axis value
int Analog_Y = 0; //y-axis value
int Analog_R = 0; //r-axis value

int Analog_X_AVG = 0; //x-axis value average
int Analog_Y_AVG = 0; //y-axis value average
int Analog_R_AVG = 0; //r-axis value average

int Analog_R_Value = 0; //this is used for the PWM value

bool sensedPrev = false;

void setup()
{

  //SERIAL
  Serial.begin(9600);
  //----------------------------------------------------------------------------    
  //PINS
  pinMode(Analog_X_pin, INPUT);
  pinMode(Analog_Y_pin, INPUT);  
  pinMode(Analog_R_pin, INPUT); 
  pinMode(LED_pin, OUTPUT);

  // Robojax.com 20181110 NJK-5002C hall sensor
  pinMode(sensorPin, INPUT_PULLUP);// define pin  as input for sensor
  // watch video explaining the INPUT_PULLUP
  //http://robojax.com/learn/arduino/?vid=robojax-push_botton_resistor
  
  //pinMode(relayPin, OUTPUT);// defind pin as output
  pinMode(ledPin, OUTPUT);

  //----------------------------------------------------------------------------  
  InitialValues(); //averaging the values of the 3 analog pins (values from potmeters)
  //----------------------------------------------------------------------------  
  //Stepper parameters
  //setting up some default values for maximum speed and maximum acceleration
  stepper.setMaxSpeed(5000); //SPEED = Steps / second  
  stepper.setAcceleration(1000); //ACCELERATION = Steps /(second)^2    
  stepper.setSpeed(500);
  delay(500);
  //----------------------------------------------------------------------------
  stepper2.setMaxSpeed(5000); //SPEED = Steps / second  
  stepper2.setAcceleration(1000); //ACCELERATION = Steps /(second)^2    
  stepper2.setSpeed(500);
  delay(500);  

  homeMotor();

}

void loop()
{
  /*
  ReadAnalog();  
  stepper.runSpeed(); //step the motor (this will step the motor by 1 step at each loop indefinitely)
  stepper2.runSpeed();  
  
  readHallSensor();
  */
 //delay(300);// delay for 0.3 seconds
  // Robojax.com 20181110 NJK-5002C hall sensor
  
}

void homeMotor(){
  for(int i = 0; i < 4; i++){
    int sensed;
    do{
      sensed = digitalRead(sensorPin);// read pin 2 and put the result in the "sensed" variable
      stepper.runSpeed();
      

    }while(sensed == true);

  }
}

void readHallSensor(){
  // Robojax.com 20181110 NJK-5002C hall sensor
  int sensed = digitalRead(sensorPin);// read pin 2 and put the result in the "sensed" variable
  if(sensed == LOW){
    if(sensedPrev == false){
      sensedPrev = true;
      Serial.println("Sensed");
      // digitalWrite(relayPin, LOW);// if sensed turn relay ON
      digitalWrite(ledPin, HIGH);// if sensed turn LED ON
      //delay(wait);// keep the relay ON for the "wait" amount of time
    }
    
  }else{
    if(sensedPrev == true){
      sensedPrev = false;
      //digitalWrite(relayPin, HIGH);// else turn the relay OFF
      digitalWrite(ledPin, LOW);// else turn the led OFF
      Serial.println("====");
    }
    
  }
}

void ReadAnalog()
{
  //Reading the 3 potentiometers in the joystick: x, y and r.
  Analog_X = analogRead(Analog_X_pin);  
  Analog_Y = analogRead(Analog_Y_pin);    
  Analog_R = analogRead(Analog_R_pin);    

  //if the value is 25 "value away" from the average (midpoint), we allow the update of the speed
  //This is a sort of a filter for the inaccuracy of the reading
  if(abs(Analog_X-Analog_X_AVG)>25) 
  {
  stepper.setSpeed(5*(Analog_X-Analog_X_AVG));    
  }
  else
  {
    stepper.setSpeed(0);
  }
  //----------------------------------------------------------------------------  
  if(abs(Analog_Y-Analog_Y_AVG)>25) 
  {
  stepper2.setSpeed(5*(Analog_Y-Analog_Y_AVG));  
  }
  else
  {
    stepper2.setSpeed(0);
  }
  //----------------------------------------------------------------------------  
  if(abs(Analog_R-Analog_R_AVG)>25) 
  {
    Analog_R_Value = map(Analog_R, 0, 1023, 0, 255); //10 bit ADC (0-1023) and 8 bit PWM (0-255)
    analogWrite(LED_pin, Analog_R_Value); //modify the PWM value     
  }
}

void InitialValues()
{
  //Set the values to zero before averaging
  float tempX = 0;
  float tempY = 0;
  float tempR = 0;
  //----------------------------------------------------------------------------  
  //read the analog 50x, then calculate an average. 
  //they will be the reference values
  for(int i = 0; i<50; i++)
  {
     tempX += analogRead(Analog_X_pin);  
     delay(10); //allowing a little time between two readings
     tempY += analogRead(Analog_Y_pin);        
     delay(10);
     tempR += analogRead(Analog_R_pin);
     delay(10);
  }
  //----------------------------------------------------------------------------  
  Analog_X_AVG = tempX/50; 
  Analog_Y_AVG = tempY/50; 
  Analog_R_AVG = tempR/50; 
  //----------------------------------------------------------------------------  
  Serial.print("AVG_X: ");
  Serial.println(Analog_X_AVG);
  Serial.print("AVG_Y: ");
  Serial.println(Analog_Y_AVG);
  Serial.print("AVG_R: ");
  Serial.println(Analog_R_AVG);
  Serial.println("Calibration finished");  
}

/*
#include <AccelStepper.h>

#define joyX A0
#define joyY A1

#define stepPUL 6
#define stepDIR 7

AccelStepper stepper; // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5
int speed = 500;

void setup() {
  // put your setup code here, to run once:
  stepper = AccelStepper(AccelStepper::DRIVER, stepPUL, stepDIR);
  Serial.begin(9600);
  stepper.setMaxSpeed(10000);
  stepper.setSpeed(5000);        
}

void loop() {
  // put your main code here, to run repeatedly:
  int xValue = analogRead(joyX) - 341;
  int yValue = analogRead(joyY) - 336;
  stepper.runSpeed();

  if(xValue > 4){
    speed = abs(speed);
    stepper.setSpeed(speed);
    Serial.println(speed);
  }

  else if(xValue < -4){
    speed = abs(speed)*-1;
    stepper.setSpeed(speed);
    Serial.println(speed);
  }
  else{
    stepper.setSpeed(0);

  }
  
  
}
*/