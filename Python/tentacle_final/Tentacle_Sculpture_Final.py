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
        self.animation.stall()
        print("calibration complete. starting program...")
        print()

        self.test_animation("test_animation")
        self.animation.run_animation("return_to_zero")
        


    def main(self):
        while self.running:
            
            '''
            TO TEST ANIMATION
            uncomment self.test_animation() and replace parameter in parenthesis with name of animation in quotation marks
            comment out self.process_video()
            this will loop the animation
            
            UNCOMMENT break TO STOP ANIMATION FROM LOOPING
            '''
            self.test_animation("test_animation")
            
            #self.process_video()
            #break
        pass

    def test_animation(self, animation_name):
        if self.animation.get_moving() == False:
            self.animation.run_animation(animation_name)
            pass
    
    
    def process_video(self):
        if self.video.idle:
            if self.idle == False:
                self.idle_timer == time.perf_counter() + self.idle_cooldown
                self.idle = True
            elif time.perf_counter() >= self.idle_timer:
                self.animation.run_animation("return_to_zero")
                #self.animation.run_animation("idle_twitch")
                self.idle_timer == time.perf_counter()+self.idle_cooldown
        else:
            if self.idle:
                self.idle = False
                print()
                print("Tracking Person!")
            
            if self.video.model_present:
                new_targets = self.reader.read_pose(self.video.get_landmarks())
                #print(str(new_targets) + "|||" + str(self.targets))
                if not new_targets == self.targets:
                    self.targets = new_targets[:]
                    print(self.targets)
                    while True:
                        try:
                            self.animation.write_data(targets);
                            break
                        except:
                            pass                    
            
        if self.video.get_stopped():
            self.running = False
            self.animation.run_animation("return_to_zero")
            exit()
      
    
tentacle = Tentacle()
tentacle.main()