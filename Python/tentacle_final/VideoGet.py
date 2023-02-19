from threading import Thread
import cv2



class VideoGet():
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        #self.num = 0
        (self.grabbed, self.frame) = self.stream.read()
        #self.num += 1
        self.stopped = False

    def start(self):
        Thread(target=self.get,args = ()).start()
        return self

    def get(self):
        while not self.stopped:
            #if cv2.waitKey(1) == ord("q"):
            #    self.stopped = True
                
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                cv2.resize(self.frame, (640, 480))
                
    def stop(self):
        self.stopped = True

    
        