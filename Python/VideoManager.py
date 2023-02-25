from VideoGet import VideoGet
from VideoShow import VideoShow
from threading import Thread
from PoseReading import PoseReading

class VideoManager:
    def __init__(self, show):
        self.stopped = False
        self.show = show
        self.video_getter = VideoGet(0).start()
        self.reader = PoseReading()
        if self.show:
            #self.video_shower = VideoShow(self.video_getter.frame).start()
            pass
        pass

    def start(self):
        Thread(target=self.main, args=()).start()
        
        return self

    def main(self):
        while not self.video_shower.stopped:
            self.frame = self.video_getter.frame
            self.frame = self.reader.read_pose(self.frame)
            self.video_shower.frame = self.frame
            
            
            pass
        self.stopped = True
        #self.video_getter.stop()
        print("Stopping Program")
        

    def get_stopped(self):
        return self.stopped
        
