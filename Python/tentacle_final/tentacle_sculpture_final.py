from smbus import SMBus
import time
import numpy as np
#import cv2

#from VideoGet import VideoGet
#from VideoShow import VideoShow
from Motor import Motor
from AnimationMethods import AnimationMethods
#from MpProcess import MpProcess

class Tentacle:

        
    def __init__(self):
            
        self.addr = 0x8 # arduino bus address
        self.bus = 1 # indicates /dev/ic2-1
        
        self.show_video = True
        self.process_frames = True
        
        self.running = True
        
        '''
        self.cap = cv2.VideoCapture(0)


        if process_frames:
            self.video_process = MpProcess(0, video_getter.frame).start()

        
        if show_video:
            self.video_getter = VideoGet(0).start()
            self.video_shower = VideoShow(video_getter.frame).start()
            
        '''
        # calibrates the motors
        motors = []
        
        for i in range(4):
            value = ""
            start_rot = 0
            while(value == ""):
                value = input("Please enter the starting rotation for motor " + str(i) + ": ")
            start_rot = int(value)
            motors.append(Motor(i, 180, start_rot))
        
        
        self.animation = AnimationMethods(self.addr, self.bus, motors)
        
        print("Starting manual calibration")
        
        for i in range(4):
            value = 0
            calibrated = False
            while calibrated == False:
                value = int(input("Enter change to motor " + str(i) + ": "))
                if value == 0:
                    calibrated = True
                else:
                    command = str(i) + "_" + str(value)
                    
                    self.animation.write_data(command)
        self.animation.write_data("reset")
        
        print("calibration complete. starting program...")
        #TODO: home the motors to find their positions

        self.animation.run_animation("animation3")
        #exit()
        
        


    def main(self):
        while self.running:
            if self.animation.get_moving() == False:
                self.animation.run_animation("animation3")
                pass
            '''
            if self.process_frames == True:
                pass
            if self.show_video == True:
                pass
            '''
        
        pass



tentacle = Tentacle()
tentacle.main()