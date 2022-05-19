from src.core.BinaryStream import bitarray
from src.lib.Terminal import Terminal
from src.core.ParsingProgress import ParsingProgress

class Literal(Terminal):
    def __init__(self, literal_value, num_bits=None):
        if isinstance(literal_value, str):
            self._value = bitarray(literal_value)
        elif isinstance(literal_value, bitarray):
            self._value = literal_value
        else:
            assert False
        self._length = len(self._value)
    def parse(self, stream, ctx=None):
        data, remaining_stream = stream.eat(self._length)
        if data == self._value:
            yield ParsingProgress(self, remaining_stream)
        else:
            print('literal matching failed!')
