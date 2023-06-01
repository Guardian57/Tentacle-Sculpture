import time

class Timer:
    
    def __init__(self, interval):
        self.interval = interval
        self.start_time = None
        self.pause_time = None
        
    def start(self):
        
        if self.pause_time is not None: #resume a paused timer
            self.start_time += time.monotonic() - self.paused_time
            self.paused_time = None
        else: #start a new timer
            self.start_time = time.monotonic()
            
    def is_done(self):
        if self.start_time is None:
            return False
        elapsed_time = time.monotonic() - self.start_time
        return elapsed_time >= self.interval
    
    def pause(self):
        self.pause_time = time.monotonic()
        
    def cancel(self):
        self.start_time = None
        self.pause_time = None

    def update_interval(self, new_interval):
        self.interval = new_interval