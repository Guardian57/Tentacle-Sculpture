import mediapipe as mp
import cv2
from CountsPerSec import CountsPerSec
from VideoGet import VideoGet
from VideoShow import VideoShow
from MpProcess import MpProcess
import time
import signal


#turns off the camera properly when an interupt happens
def sig_handler(signum, frame):
    video_getter.stop()
    cv2.destroyAllWindows()
    exit(1)

#registers signal handlers to catch interupts
signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTSTP, sig_handler)

show_video = False
process_frames = True

#cap = cv2.VideoCapture(0)

start_rot = None #default start rotation
send_reset = False



video_getter = VideoGet(1).start()

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