from src.BinaryStream import bitarray

@DeprecationWarning
class Shell:
    # TODO: should this class create objects with a "set_value" method that actually turn an instance of this class into that class?
    def __init__(self):
        self.value = None # will be over-written by the caller
    def parse(self, stream):
        return self.value.parse(stream)
    def fuzz(self):
        return self.value.fuzz()
    def serialize(self):
        return self.value.serialize()

class Literal:
    def __init__(self, literal_value, num_bits=None):
        if isinstance(literal_value, str):
            self._value = bitarray(literal_value)
        elif isinstance(literal_value, bitarray):
            self._value = literal_value
        else:
            assert False

class Constraint:
    pass