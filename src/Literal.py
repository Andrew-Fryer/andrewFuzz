from src.BinaryStream import bitarray

class Literal:
    def __init__(self, literal_value, num_bits=None):
        if isinstance(literal_value, str):
            self._value = bitarray(literal_value)
        elif isinstance(literal_value, bitarray):
            self._value = literal_value
        else:
            assert False