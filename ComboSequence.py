

class ComboSequence:
    def __init__(self, subseqs):
        self.storyLine = subseqs
        self.index = 0
        self.freq = self.storyLine[0].freq


    def __next__(self):
        try:
            return next(self.storyLine[self.index])
        except StopIteration:
            if self.index + 1 == len(self.storyLine):
                raise StopIteration
            self.index += 1

            return next(self)