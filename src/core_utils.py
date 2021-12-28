from src.BinaryStream import bitarray
from src.ParsingProgress import ParsingProgress

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
    def __init__(self, child, constraint_function):
        self.child = child
        self.constraint_fuction = constraint_function
    def parse(self, stream):
        for parsed_child, remaining_stream in self.child.parse(stream):
            if self.constraint_fuction(parsed_child):
                yield ParsingProgress(Constraint(parsed_child, self.constraint_fuction), stream)
    def __str__(self):
        return "<Constraint " + str(self.child) + " >"
    def fuzz(self):
        return self.child.fuzz() # TODO: subclass Constraint to allow us to fuzz diferent constraints
    def serialize(self):
        return self.child.serialize()

# class notEqualsConstraint(Constraint):
#     def __init__(self, child, )
#     def fuzz
