from smbus import SMBus
import time
import numpy as np


from VideoManager import VideoManager
from Motor import Motor
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
        #exit()

      
    def calibrate_motors(self):
        self.motors = []
        
        for i in range(4):
            self.motors.append(Motor(i, 180, 0))
        
        
        self.animation = AnimationMethods(self.addr, self.bus, self.motors)
        
        print("Starting manual calibration")
        
        for i in range(4):
            calibrated = False
            while calibrated == False:
                value = 0
                value = int(input("Enter change to motor " + str(i) + ": "))
                if value == 0:
                    calibrated = True
                else:
                    # change this to new format for commands
                    command = str(i) + "_" + str(value)
                    self.animation.write_data(command)
        # change this to new format for reset command if applicable
        self.animation.write_data("reset")
        print("calibration complete. starting program...")
        print()

    


    def main(self):
        while self.running:
            
            '''
            TO TEST ANIMATION
            uncomment self.test_animation() and replace parameter in parenthesis with name of animation in quotation marks
            comment out self.process_video()
            this will loop the animation
            
            UNCOMMENT break() TO STOP ANIMATION FROM LOOPING
            '''
            #self.test_animation("test_animation")
            
            self.process_video()
            #break()
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
                self.animation.run_animation("idle_twitch")
                self.idle_timer == time.perf_counter()+self.idle_cooldown
        else:
            if self.idle:
                self.idle = False
                print()
                print("Tracking Person!")
            
            if self.video.model_present:
                self.reader.read_pose(self.video.get_landmarks())
            
            
        if self.video.get_stopped():
            self.running = False
            #self.animation.write_data("reset")
            exit()
      
    
tentacle = Tentacle()
tentacle.main()