import time

freq = 24
class SingleFlash:
    def __init__(self, color, duration):
        self.color = color
        self.duration = duration
        self.freq = freq  # global refresh rate
        self.startTime = None
        self.keepGoing = True

    def __next__(self):

        if(self.startTime is None):
            self.startTime = time.time()

        if not self.keepGoing:
            raise StopIteration
        if time.time()-self.startTime > self.duration:
            self.keepGoing = False
            return "0 0 0"
        return self.color
