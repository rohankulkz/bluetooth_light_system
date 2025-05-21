import asyncio
import time

import LightRunner


class StrobeSequence:
    def __init__(self, seq, speed, length=-1):
        self.sequence = seq
        self.speed = speed  # flashes per second
        self.length = length  # total seconds (-1 for infinite)
        self.step = 0
        self.start_time = None
        self.freq = LightRunner.freq
        self.last_step_time = None
        self.max_steps = None if length == -1 else int(speed * length)

    def __next__(self):

        if self.start_time is None:
            self.start_time = time.time()
            self.last_step_time = self.start_time

        current_time = time.time()
        elapsed = current_time - self.last_step_time

        # Only move to the next step if enough time has passed
        if elapsed < 1 / self.speed:
            # Don't advance — try again later
            return None

        self.last_step_time = current_time

        if self.max_steps is not None and self.step >= self.max_steps:
            raise StopIteration

        result = self.sequence[self.step % len(self.sequence)]
        self.step += 1
        return result
