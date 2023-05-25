from smbus import SMBus
from configparser import ConfigParser
import time
import os
import json

class AnimationMethods:
    
    moving = False
    
    def __init__ (self, address, bus):
        self.address = address
        self.bus = SMBus(7)
        time.sleep(0.1)
        
        
        self.motor_count = 4 # number of motors
        self.maximum_angle = 180 # maximum angle motors can turn
        self.targets = [90,90,90,90,70,70]
        
        self.step = 0 # which step of the animation we are on
        self.uptime = time.perf_counter() # the time the program started running
        self.delay = 0 # the delay between commands
        self.current_time = 0
        print(os.getcwd())
        with open("/home/rock/Desktop/Tentacle-Sculpture/Python/animations.json", "r") as read_file:
            self.data = json.load(read_file)

        
        #self.write_data(self.targets) # writing motor data
        
#         self.stall() # a stall to make sure all calibrations are done
        time.sleep(.1)
        #self.write_data([0, 0, 0, 0, 1]); # a reset command to set the new zeroes for the motor
        print("Animations Ready")


    def stall(self): # a stall to wait for the command to finish before starting a new one
        waiting = True
        while(waiting):
            
            # try: # waits for the motor status to be empty of bits, meaning the command is finished executing
            status = self.bus.read_byte(self.address)
            #print(status)
            if(status == 1):
                waiting = False
            time.sleep(.1) # a small delay to improve stability
            # except:
            #     pass
        pass
        time.sleep(.1) # a small delay to improve stability
        

    def run_animation(self, animation):
        self.moving = True # whether the animation is running
        self.step = 0 # which step in the list of commands program is at
        
        # config = ConfigParser()  
        # config.read(f"{os.path.dirname(__file__)}/animation_configs.ini") # reads the config file

        # config_read = config["DEFAULT"]
        # print(os.path.realpath(os.path.dirname(__file__)))
        # print(os.path.isfile("animation_configs.ini"))
        # command = config_read[animation] # reads the animation listed in parameters

        
        # command_lines = command.split("\n") # splits the commands into multiple steps
        # if command_lines[0] == "":
        #     command_lines = command_lines[1:]
        # print(command_lines)
        if self.data.get(animation) == None:
            print('No animation by that name')
        else:

            print("Starting Animation: " + animation)
            # print()
            print(self.data[animation]["frames"])
            while self.step < len(self.data[animation]["frames"]): # while there are still commands that need to be executed
                step_delay = self.data[animation]["frames"][self.step][4]
                # if the current time is greater than the current time and the delay. default is zero to start command immediately
                # print("step: " + str(self.step))
                if time.perf_counter() > self.delay:
                    
                    
                    # command = command_lines[self.step] 

                    # step_delay = 0 # delay of command is zero by default
                    # if "|" in command: # checks if a delay was logged in the command
                    #     delay_index = command.find("|")
                    #     step_delay = command[delay_index+1:] # separates the delay from the rest of the command
                    #     step_delay = step_delay.replace(" ", "") # removes any whitespaces
                    #     step_delay = int(step_delay) # typecasts to int
                    #     command = command[:delay_index]
                    
                    # #print(command)
                    # command_steps = command.split() # splits command by whitespaces
                    # #print(command_steps)
                    
                    
                    for i in range(4): # iterates through single angle commands
                        
                        
                        new_target = int(self.data[animation]["frames"][self.step][i])
                        
                    
                        if new_target > 180:
                            new_target -= 180
                        
                    
                        new_target = 180 - new_target #adjusts to flip motor orientation 
                        
                        self.targets[i] = new_target

                    self.targets[4] = self.data[animation]["frames"][self.step][5]
                    self.targets[5] = self.data[animation]["frames"][self.step][6]

                    print(self.targets)
                    self.write_data(self.targets)
                    self.stall() # makes sure tentacle isn't moving before executing command
                    self.delay = step_delay + time.perf_counter()
                    self.step+=1 # moves on to next step
                
        self.bus.write_i2c_block_data(self.address,0x0A,[70, 70])        
        self.moving = False # the animation is complete
        print()
        
   


    def write_data(self, value): # writes the command to the arduino
        #byte_value = self.string_to_bytes(value) # used in old version
        self.bus.write_i2c_block_data(self.address,0x08,value) #first byte is 0=command byte.. just is.
        print("to Arduino: " + str(value))
        return -1

    
    def get_moving(self):
        return self.moving
    