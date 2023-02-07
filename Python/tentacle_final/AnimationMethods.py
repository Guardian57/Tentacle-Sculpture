from smbus import SMBus
from configparser import ConfigParser
import time
from Motor import Motor

class AnimationMethods:
    def __init__ (self, address, bus, motors):
        self.address = address
        self.bus = SMBus(1)
        
        self.motors = motors # aray of motors
        self.motor_count = 4 # number of motors
        self.maximum_angle = 180 # maximum angle motors can turn
        
        
        self.step = 0 # which step of the animation we are on
        self.uptime = time.perf_counter() # the time the program started running
        self.delay = 0
        self.current_time = 0
        
        
        print("Animations Ready")

    def run_animation(self, animation):
        
        #write_data("reset", self.address)
        self.uptime = time.perf_counter()

        config = ConfigParser()
        config.read("animation_configs.ini")

        config_read = config["DEFAULT"]
        command = config_read[animation]
        print(command)

        commands = command.split(" ")
        print(commands)
        print("Starting Animation...")
        
        
        while self.step < len(commands):
            if time.perf_counter() > self.uptime + 1 and time.perf_counter() > self.current_time + self.delay:
                self.current_time = time.perf_counter()
                waiting = True
                
                while(waiting): 
                    try:
                        status = self.bus.read_byte(self.address)
                        binary_status = str(bin(status))[2:]
                        binary_status = binary_status[::-1]
                        print(binary_status)
                        
                        waiting = False
                        for i in range(len(self.motors)):
                            if self.motors[i].is_motor_ready(binary_status(i)) == False:
                                waiting = True
                        
                        if waiting == False:
                            break
                
                        
       
                    except:
                        pass
                    
                    break
                command_pieces = commands[self.step].split("_")
                print(command_pieces)
                motor_num = command_pieces[0]
                new_target = command_pieces[1]
                write_data(motor_num+"_"+new_target, self.address, self.bus)
                self.delay = int(command_pieces[2])
                self.step+=1
                


# I didn't make this don't touch it, it's fine
def string_to_bytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
    return ret_val


def write_data(value, address, bus):
    byte_value = string_to_bytes(value)    
    bus.write_i2c_block_data(address,0x00,byte_value) #first byte is 0=command byte.. just is.
    print("Byte value!")
    print(byte_value)
    return -1

