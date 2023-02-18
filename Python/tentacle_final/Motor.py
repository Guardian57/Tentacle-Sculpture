class Motor:
    target = 0 # current target position for motor
    ready = True # whether or not motor is ready for a new command
    
    def __init__(self, label, maximum, position):
        self.label = label # numerical label of motor
        self.maximum = maximum # maximum angle motor can turn to
        self.position = position
        
        
    # returns the command for the arduino to read
    def send_command(self):
        pass
        
      
    # checks if arduino and pi are synced 
    def is_motor_ready(self, at_pos):
        if at_pos == "1":
            self.position = self.target
            self.ready = True
        else:
            self.ready = False
        return self.ready
    
    def set_position(self, pos):
        self.position = pos
    
    # returns whether or not motor is ready for a new command
    def is_ready(self):
        return self.ready
    
    # returns the position of the motor
    def get_position(self):
        return self.position
    
    # returns the target of the motor
    def get_target(self):
        return self.target
    
    # returns the label of the motor
    def get_label(self):
        return self.label
    
    
    

