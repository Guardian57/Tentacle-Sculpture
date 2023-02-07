from smbus import SMBus
import time
import numpy as np

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
        self.process_frames = False
        
        self.running = True
        #cap = cv2.VideoCapture(0)


        #if process_frames:
        #    video_process = MpProcess(start_rot, video_getter.frame).start()

        '''
        if show_video:
            self.video_getter = VideoGet(0).start()
            self.video_shower = VideoShow(video_getter.frame).start()
            '''
        
        # calibrates the motors
        motors = []
        for i in range(4):
            value = input("Please enter the starting rotation for motor " + str(i) + ": ")
            start_rot = int(value)
            motors.append(Motor(i, 180, start_rot))
            
        self.animation = AnimationMethods(self.addr, self.bus, motors)
        
        print("calibration complete. starting program...")
        #TODO: home the motors to find their positions

        self.animation.run_animation("animation3")
            
        
        


    def main(self):
        while self.running:
            
            if self.show_video:
                #video_shower = VideoShow(video_getter.frame).show()
                pass
        
        pass



tentacle = Tentacle()
tentacle.main()