from smbus import SMBus
from configparser import ConfigParser
import time
from Motor import Motor



class AnimationMethods:
    def __init__(self, address):
        self.bus = SMBus(1)
        
        #address of arduino controlling motors
        self.address = address

    def run_animation(animation):
        motors = [] # aray of motors
        motor_count = 4 # number of motors
        maximum_angle = 180 # maximum angle motors can turn
        
        
        step = 0 # which step of the animation we are on
        uptime = time.perf_counter() # the time the program started running
        delay = 0
        current_time = 0
        
        
        
        
        # resets the arduino data being saved
        write_data("reset")

        config = ConfigParser()
        config.read("animation_configs.ini")

        config_read = config["DEFAULT"]
        command = config_read[animation]
        print(command)

        commands = command.split(" ")
        print(commands)
        
        while step < len(commands):
            if time.perf_counter() > uptime + 1 and time.perf_counter() > current_time + delay:
                current_time = time.perf_counter()
                waiting = True
                
                while(waiting): 
                    try:
                        status = bus.read_byte(address)
                        binary_status = str(bin(status))[2:]
                        binary_status = binary_status[::-1]
                        print(binary_status)
                        
                        waiting = False
                        for i in range(len(motors)):
                            if motors[i].is_motor_ready(binary_status(i)) == False:
                                waiting = True
                        
                        if waiting == False:
                            break
                
                        
       
                    except:
                        pass
                    
                    break
                command_pieces = commands[step].split("_")
                print(command_pieces)
                motor_num = command_pieces[0]
                new_target = command_pieces[1]
                write_data(motor_num+"_"+new_target)
                delay = int(command_pieces[2])
                step+=1
                


    def write_data(value):
        byte_value = string_to_bytes(value)    
        bus.write_i2c_block_data(address,0x00,byte_value) #first byte is 0=command byte.. just is.
        #print(byteValue)
        return -1

    # I didn't make this don't touch it, it's fine
    def string_to_bytes(val):
            ret_val = []
            for c in val:
                    ret_val.append(ord(c))
            return ret_val
    


