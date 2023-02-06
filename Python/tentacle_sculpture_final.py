from smbus import SMBus
import time
import numpy as np
import cv2
import mediapipe as mp

show_video = True
process_frames = True

#cap = cv2.VideoCapture(0)

# calibrates the motors
calibrate_motors()


start_rot = int(value)



video_getter = VideoGet(0).start()
if process_frames:
    video_process = MpProcess(start_rot, video_getter.frame).start()
if show_video:
    video_shower = VideoShow(video_getter.frame).start()
    

# sets all the motors to angle zero
def calibrate_motors():
    value = input("Please enter the starting rotation")
    start_rot = int(value)
    value = input("Type 'yes' to start tracking: ")
    if value == 'yes':
        print("calibration complete. starting program...")
    #TODO: home the motors to find their positions
