class Motor:
    position = 0 # current position of motor
    target = 0 # current target position for motor
    ready = True # whether or not motor is ready for a new command
    
    def __init__(self, label, maximum):
        self.label = label # numerical label of motor
        self.maximum = maximum # maximum angle motor can turn to
       
    # returns the command for the arduino to read
    def send_command():
        pass
        
    
    # sets the new target location
    def set_new_target(target): 
        self.target = target
    
    # adds the target to current target
    def add_to_target(target):
        target+=target
        
    # checks if arduino and pi are synced 
    def is_motor_ready(at_pos):
        if at_pos == "1":
            position = target
            ready = True
        else:
            ready = False
        return ready
    
    # returns whether or not motor is ready for a new command
    def is_ready():
        return ready
    
    # returns the position of the motor
    def get_position():
        return position
    
    # returns the target of the motor
    def get_target():
        return target
    
    # returns the label of the motor
    def get_label():
        return label
    
    
    
    
