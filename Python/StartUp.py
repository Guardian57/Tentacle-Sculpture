#!/home/rock/miniconda3/envs/tentacle/bin/python

#crontab: @reboot /home/rock/miniconda3/envs/tentacle/bin/python /home/rock/Desktop/Tentacle-Sculpture/Python/StartUp.py &

from periphery import GPIO
import time
import subprocess
 
Run_Button_Pin = 47  # GPIO pin 47 physical pin 31
Shutdown_Button_Pin = 103  # GPIO pin 103 physical pin 33
program = None
state = 0  # defaults to program being off
 
RUN_BUTTON_GPIO = GPIO(Run_Button_Pin, "in")
SHUT_BUTTON_GPIO = GPIO(Shutdown_Button_Pin, "in")
 
 
def startProgram():
    global program
    
    if isRunning():

        program.terminate()
        program.wait()
        program = None

    else:

        program = subprocess.Popen(['/home/rock/miniconda3/envs/tentacle/bin/python',
                                '/home/rock/Desktop/Tentacle-Sculpture/Python/pose_thread.py'])
 
def stopProgram():
    
    global program
    
    program.terminate()
    program.wait()
    program = None

def isRunning():
    
    global program  
    
    if program is not None and program.poll() is None:
        
        return True

    else: 

        return False
 
 
while True:
    try:
        runButtonValue = RUN_BUTTON_GPIO.read()
        # print("Run Button Value", runButtonValue)
        # print(runButtonValue)
        shutdownButtonValue = SHUT_BUTTON_GPIO.read()
        # print("Shut Button Value", shutdownButtonValue)
        # print(shutdownButtonValue)
 
        if (runButtonValue == True):
            print("Starting Program...")
            time.sleep(2)
            
            startProgram()
            # subprocess.Popen(['/home/rock/miniconda3/envs/tentacle/bin/python',
            #                  '/home/rock/Documents/Tentacle-Sculpture/Python/pose_thread.py'])
            # LED_GPIO.write(True)
            time.sleep(3)
        elif (shutdownButtonValue == True):
            
            print('ShuttingDown')
            
            if isRunning():
                stopProgram()

            time.sleep(2)
            subprocess.Popen(['shutdown', 'now'])

        else:

            pass  # for now, this could be used for error handling later
 
        time.sleep(0.1)
 
    except KeyboardInterrupt:
        # LED_GPIO.write(False)
        break
 
    except IOError:
        print("error")
 
 
# LED_GPIO.close()
 
