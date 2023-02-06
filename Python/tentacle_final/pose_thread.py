import mediapipe as mp
import cv2
from VideoGet import VideoGet
from VideoShow import VideoShow
from MpProcess import MpProcess
import time


show_video = True
process_frames = True

#cap = cv2.VideoCapture(0)
value = input("Please enter starting rotation: ")

start_rot = int(value)

value = input("Type 'yes' to start tracking: ")
if value == 'yes':
    print("calibration complete. starting program...")

video_getter = VideoGet(0).start()
if process_frames:
    video_process = MpProcess(start_rot, video_getter.frame).start()
if show_video:
    video_shower = VideoShow(video_getter.frame).start()


# cps = CountsPerSec().start()


# print('setting current pos ' + str(MpProcess.currentPos))

def putIterationsPerSec(frame, iterations_per_sec):
    """
    Add iterations per second text to lower-left corner of a frame.
    """

    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
        (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
    
    print("{:.0f} iterations/sec".format(iterations_per_sec))
    
    return frame



while True:
    
    
    if video_getter.stopped:
        
        if show_video:
            video_shower.stop()
            
        video_getter.stop()
        if process_frames:
            video_process.stop()
        break
    
                                                            

    frame = video_getter.frame
    frame = cv2.resize(frame, (640, 480))
    #frame = putIterationsPerSec(frame, cps.countsPerSec())
    #cps.increment()
    
    if process_frames:
        video_process.frame = frame
    
    

    
    if show_video:
        if process_frames:
            video_shower.frame = video_process.image
        else:
            video_shower.frame = frame
    
        

#cap.release()
cv2.destroyAllWindows()