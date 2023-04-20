from smbus import SMBus
from configparser import ConfigParser
import time



class AnimationMethods:
    
    moving = False
    
    def __init__ (self, address, bus):
        self.address = address
        self.bus = SMBus(1)
        
        
        self.motor_count = 4 # number of motors
        self.maximum_angle = 180 # maximum angle motors can turn
        self.targets = [0,0,0,0]
        
        self.step = 0 # which step of the animation we are on
        self.uptime = time.perf_counter() # the time the program started running
        self.delay = 0 # the delay between commands
        self.current_time = 0
        
        self.write_data(self.targets) # writing motor data
        
        self.stall() # a stall to make sure all calibrations are done
        time.sleep(.1)
        #self.write_data([0, 0, 0, 0, 1]); # a reset command to set the new zeroes for the motor
        print("Animations Ready")


    def stall(self): # a stall to wait for the command to finish before starting a new one
        waiting = True
        while(waiting):
            
            try: # waits for the motor status to be empty of bits, meaning the command is finished executing
                status = self.bus.read_byte(self.address)
                #print(status)
                if(status == 0):
                    waiting = False
                time.sleep(.1) # a small delay to improve stability
            except:
                pass
        pass
        time.sleep(.1) # a small delay to improve stability
        

    def run_animation(self, animation):
        self.moving = True # whether the animation is running
        self.step = 0 # which step in the list of commands program is at
        
        config = ConfigParser()  
        config.read("animation_configs.ini") # reads the config file

        config_read = config["DEFAULT"]
        command = config_read[animation] # reads the animation listed in parameters

        command_lines = command.split("\n") # splits the commands into multiple steps
        if command_lines[0] == "":
            command_lines = command_lines[1:]
        print(command_lines)
        print("Starting Animation: " + animation)
        print()
        
        while self.step < len(command_lines): # while there are still commands that need to be executed
            # if the current time is greater than the current time and the delay. default is zero to start command immediately
            # print("step: " + str(self.step))
            if time.perf_counter() > self.delay:
                
                
                command = command_lines[self.step] 

                step_delay = 0 # delay of command is zero by default
                if "|" in command: # checks if a delay was logged in the command
                    delay_index = command.find("|")
                    step_delay = command[delay_index+1:] # separates the delay from the rest of the command
                    step_delay = step_delay.replace(" ", "") # removes any whitespaces
                    step_delay = int(step_delay) # typecasts to int
                    command = command[:delay_index]
                
                #print(command)
                command_steps = command.split() # splits command by whitespaces
                #print(command_steps)
                for i in range(len(command_steps)): # iterates through single angle commands
                    single_command = command_steps[i].split("_") # makes a single command in two parts
                    motor_num = int(single_command[0])
                    new_target = int(single_command[1])
                    
                    if new_target > 180:
                        new_target -= 180
                    
                    
                    value_scaled = float(new_target) / float(180)
                    new_target = int(value_scaled * 255)
                    
                    self.targets[motor_num] = new_target
                    
                print(self.targets)
                self.write_data(self.targets)
                self.stall() # makes sure tentacle isn't moving before executing command
                self.delay = step_delay + time.perf_counter()
                self.step+=1 # moves on to next step
                
                
        self.moving = False # the animation is complete
        print()
        
    # I didn't make this don't touch it, it's fine. used in old version of program
    def string_to_bytes(self, val):
        ret_val = []
        for c in val:
            ret_val.append(ord(c))
        return ret_val


    def write_data(self, value): # writes the command to the arduino
        #byte_value = self.string_to_bytes(value) # used in old version
        self.bus.write_i2c_block_data(self.address,0x00,value) #first byte is 0=command byte.. just is.
        print("to Arduino: " + str(value))
        return -1

    
    def get_moving(self):
        return self.moving
    