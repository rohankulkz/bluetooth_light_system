

freq = 12
class FadeSequence:
    def __init__(self, start, end, length):
        self.start = start
        self.end = end
        self.length = length
        self.freq = freq  # global refresh rate

        self.maxSteps = max(1, int(self.length * self.freq)) if self.length > 0 else 1

        self.step = 0

        # Compute shifts per step
        self.rShift = (end[0] - start[0]) / self.maxSteps
        self.gShift = (end[1] - start[1]) / self.maxSteps
        self.bShift = (end[2] - start[2]) / self.maxSteps

        # Use float values for gradual fading
        self.r = float(start[0])
        self.g = float(start[1])
        self.b = float(start[2])

    def __next__(self):
        if self.step > self.maxSteps:
            raise StopIteration

        result = f"{int(self.r)} {int(self.g)} {int(self.b)}"
        # print(f"Step {self.step}: {result}")

        self.r += self.rShift
        self.g += self.gShift
        self.b += self.bShift

        self.step += 1
        return result
