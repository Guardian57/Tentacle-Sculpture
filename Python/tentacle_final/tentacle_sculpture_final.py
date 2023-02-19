from smbus import SMBus
import time
import numpy as np


from VideoManager import VideoManager
from Motor import Motor
from AnimationMethods import AnimationMethods

class Tentacle:

        
    def __init__(self):
            
        self.addr = 0x8 # arduino bus address
        self.bus = 1 # indicates /dev/ic2-1
        
        self.show_video = True
        self.process_frames = True
        
        self.running = True
        
        
        
        if self.process_frames:
            self.video = VideoManager(self.show_video).start()
            #self.video_getter = VideoGet(0).start()
            #self.video_process = MpProcess(0, video_getter.frame).start()
            pass

        '''
        if self.show_video:
            self.video_shower = VideoShow(self.video_getter.frame).start()
           ''' 
        
        # calibrates the motors
        motors = []
        
        for i in range(4):
            motors.append(Motor(i, 180, 0))
        
        
        self.animation = AnimationMethods(self.addr, self.bus, motors)
        
        print("Starting manual calibration")
        
        for i in range(4):
            value = 0
            calibrated = False
            while calibrated == False:
                value = 0
                #value = int(input("Enter change to motor " + str(i) + ": "))
                if value == 0:
                    calibrated = True
                else:
                    command = str(i) + "_" + str(value)
                    
                    self.animation.write_data(command)
        self.animation.write_data("reset")
        
        print("calibration complete. starting program...")
        #TODO: home the motors to find their positions

        #self.animation.run_animation("test_animation")
        #exit()
        
        


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
        if self.video.get_stopped():
            self.running = False
            self.animation.write_data("reset")
            exit()


tentacle = Tentacle()
tentacle.main()