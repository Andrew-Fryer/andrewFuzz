from enum import Enum

class Fuzz:
    # this class is a named tuple which stores the progress of a fuzz
    def __init__(self, data_model, fuzziness):
        self.data_model = data_model
        self.fuzziness = fuzziness
    def get_tuple(self):
        return self.data_model, self.fuzziness

class Fuzziness(Enum):
    correct = 1
    semantic = 2
    syntactic = 3
    both = 4
    unknown = 5
