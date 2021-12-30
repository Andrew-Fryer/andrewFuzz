from enum import Enum

class Fuzziness(Enum):
    correct = 1
    semantic = 2
    syntactic = 3
    both = 4
    unknown = 5
