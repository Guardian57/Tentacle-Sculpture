from smbus import SMBus
import time
import numpy as np


from VideoManager import VideoManager
from AnimationMethods import AnimationMethods
from PoseReader import PoseReader

class Tentacle:

        
    def __init__(self):
        
        self.addr = 0x8 # arduino bus address
        self.bus = 1 # indicates /dev/ic2-1
        
        # whether or not to include video processing and display
        self.show_video = True
        self.process_frames = True
        
        self.running = True
        
        self.targets = [0, 0, 0, 0]
        
        self.idle_cooldown = 10
        self.idle_timer = 0
        self.idle = False
        
        # calibrates the motors
        self.calibrate_motors()
        
        
        #TODO: home the motors to find their positions automatically

        
        # starts the video manager for tracking user location
        if self.process_frames:
            self.video = VideoManager(self.show_video).start()
            self.reader = PoseReader()
            pass
        
        
        #self.animation.run_animation("motor_test")
        
        #self.animation.run_animation("test_animation")
        #exit()

      
    def calibrate_motors(self):
        
        self.animation = AnimationMethods(self.addr, self.bus)
        
        print("Starting manual calibration")
        
        for i in range(4):
            calibrated = False
            while calibrated == False:
                value = 0
                value = int(input("Enter change to motor " + str(i) + ": "))
                if value == 0:
                    calibrated = True
                elif value < 0:
                    value = 0
                    self.targets[i] = value
                    self.animation.write_data(self.targets)
                else:
                    # change this to new format for commands
                    self.targets[i] = value
                    self.animation.write_data(self.targets)
        # change this to new format for reset command if applicable
        
        self.animation.write_data([0, 0, 0, 0,  1])
        #self.animation.stall()
        print("calibration complete. starting program...")
        print()

        #self.test_animation("test_animation")
        #self.animation.run_animation("return_to_zero")
        


    def main(self):
        while self.running:

            self.process_video()
            #break
        pass

    def test_animation(self, animation_name):
        if self.animation.get_moving() == False:
            self.animation.run_animation(animation_name)
            pass
    
    
    def process_video(self):
        
        if self.video.idle: # if the program is idled
            
            if self.idle == False: # if it just switched to idle
                self.idle_timer == time.perf_counter() + self.idle_cooldown # starts a timer for when to play the animation
                self.idle = True # idle is now true
                
            elif self.idle and time.perf_counter() >= self.idle_timer: # if the code is set to idle and needs to play animation
                self.animation.run_animation("idle_twitch") # plays the idle twitch animation
                self.idle_timer == time.perf_counter()+self.idle_cooldown # creates a delay between animations
        else:
            if self.idle == True: # if idle just became false in video
                self.idle = False # sets idle to false
                print()
                print("Tracking Person!")
            
            if self.video.model_present and self.idle == False: # if not idling and a model is present
                new_targets = self.reader.read_pose(self.video.get_landmarks()) # tracks pose using landmarks from video
                #print(str(new_targets) + "|||" + str(self.targets))
                if not new_targets == self.targets: # if the targets are different from the current position
                    self.targets = new_targets[:] # sets the new targets
                    #print(self.targets)
                    while True:
                        try:
                            self.animation.write_data(targets); # writes the targets to arduino
                            break
                        except:
                            print("tracker writer error")
                            break                    
            
        if self.video.get_stopped(): # stops the code and resets tentacle
            self.running = False
            self.animation.run_animation("return_to_zero")
            exit()
      
    
tentacle = Tentacle()
tentacle.main()