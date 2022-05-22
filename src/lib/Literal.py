from src.core.BinaryStream import bitarray
from src.lib.Terminal import Terminal, Byte
from src.core.ParsingProgress import ParsingProgress

class Literal(Terminal):
    def __init__(self, literal_value, value=None, num_bits=None):
        if isinstance(literal_value, str):
            self.literal_value = bitarray(literal_value)
        elif isinstance(literal_value, bitarray):
            self.literal_value = literal_value
        else:
            assert False
        if isinstance(literal_value, str):
            self.value = bitarray(literal_value)
        elif isinstance(literal_value, bitarray):
            self.value = literal_value
        else:
            self.value = None
        self.literal_length = len(self.literal_value)
    def parse(self, stream, ctx=None):
        data, remaining_stream = stream.eat(self.literal_length)
        if data == self.literal_value:
            yield ParsingProgress(self, remaining_stream)
        # else:
        #     print('literal matching failed!', self._value)
    def fuzz(self):
        yield self
        yield Byte(bitarray('0' * self.literal_length))
        yield Byte(bitarray('1' * self.literal_length))
        # todo add fuzz
    def serialize(self):
        return self.value
