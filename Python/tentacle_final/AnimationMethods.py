from smbus import SMBus
from configparser import ConfigParser
import time
from Motor import Motor


class AnimationMethods:
    
    moving = False
    
    def __init__ (self, address, bus, motors):
        self.address = address
        self.bus = SMBus(1)
        
        self.motors = motors # aray of motors
        self.motor_count = 4 # number of motors
        self.maximum_angle = 180 # maximum angle motors can turn
        
        
        self.step = 0 # which step of the animation we are on
        self.uptime = time.perf_counter() # the time the program started running
        self.delay = 0 # the delay between commands
        self.current_time = 0
        
        for i in range(len(motors)): # resetting all motors to 0
            
            self.write_data(str(i)+"_"+str(motors[i].get_position()*-1)) # writing motor data
            motors[i].set_position(0) # 
            time.sleep(.1) # small delay to improve stability
            
        
        self.stall() # a stall to make sure all calibrations are done
        self.write_data("reset"); # a reset command to set the new zeroes for the motor
        print("Animations Ready")


    def stall(self): # a stall to wait for the command to finish before starting a new one
        waiting = True
        while(waiting):
            try: # waits for the motor status to be empty of bits, meaning the command is finished executing
                status = self.bus.read_byte(self.address)
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
        
        self.uptime = time.perf_counter() # time the command started being executed

        config = ConfigParser()  
        config.read("animation_configs.ini") # reads the config file

        config_read = config["DEFAULT"]
        command = config_read[animation] # reads the animation listed in parameters

        commands = command.split(" ") # splits the commands into multiple steps
        print(commands)
        print("Starting Animation: " + command)
        print()
        
        
        delay_between_movements = True # assumes there is a delay between commands until proven to not need a delay
        while self.step < len(commands): # while there are still commands that need to be executed
            # if the current time is greater than the current time and the delay. default is zero to start command immediately
            if time.perf_counter() > self.uptime + .1 and time.perf_counter() > self.current_time + self.delay:
                
                while True: # crash protection
                    try:
                        self.current_time = time.perf_counter() # sets the current time
                        
                        
                        command_pieces = commands[self.step].split("_") # splits the current command into its smaller parts
                        if delay_between_movements: # triggers to wait until command can be executed
                            self.stall()
                        print(command_pieces)
                        motor_num = command_pieces[0]
                        new_target = command_pieces[1]
                        
                        
                        self.write_data(motor_num+"_"+new_target) # writes the command
                      
                        check_delay = command_pieces[2] # checks if there is a delay
                        if check_delay == "*": # asterisk means next command should trigger immediately
                            self.delay = 0 # delay is set to zero
                            print("No delay")
                            delay_between_movements = False # skips the stall command
                        else:
                            delay_between_movements = True
                            print("delay: " + check_delay) 
                            self.delay = int(check_delay) # sets the new delay
                            
                        self.step+=1 # moves on to next step
                        break
                    
                        
                    except:
                        pass
                    
                    
                
        self.moving = False # the animation is complete
        print()
        

    # I didn't make this don't touch it, it's fine
    def string_to_bytes(self, val):
        ret_val = []
        for c in val:
            ret_val.append(ord(c))
        return ret_val


    def write_data(self, value): # writes the command to the arduino
        byte_value = self.string_to_bytes(value)
        
        self.bus.write_i2c_block_data(self.address,0x00,byte_value) #first byte is 0=command byte.. just is.
        #print("Byte value!")
        print("to Arduino: " + value)
        #print(byte_value)
        print()
        return -1

    
    def get_moving(self):
        return self.moving
    