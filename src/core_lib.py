from bitarray import bitarray, util as bitarray_util # this gives us performant, bit-wise binary operations (Python's stock binary operations are all byte-wise)

from .ParsingProgress import ParsingProgress
from .DataModel import DataModel
from .BinaryStream import BinaryStream

class NonTerminal(DataModel):
    # def __init__(self, children=[], allow_recursion=False):
    #     self._allow_recursion = allow_recursion # used to allow recursion in a DataModel when used as a grammar, and not when used as an AST
    #     for child in children:
    #         child.set_parent(self)
    # def set_parent(self, parent):
    #     if self._allow_recursion:
    #         self.parent = (self.parent or []).append(parent)
    #     assert not self.parent
    #     self.parent = parent
    pass

class Terminal(DataModel):
    # def set_parent(self, parent):
    #     assert not self.parent
    #     self.parent = parent
    pass

class Byte(Terminal):
    def parse(self, stream):
        data, stream = stream.eat(8)
        if data != None:
            yield ParsingProgress(Byte(data), stream)
    def __init__(self, data=bitarray('00000000')):
        self.data = data
    def __str__(self):
        return self.data.to01()
    def fuzz(self):
        yield Byte(bitarray('00000000'))
        yield Byte(bitarray('11111111'))
        yield Byte(bitarray('10101010'))
    def serialize(self):
        return self.data

class Flag(Terminal):
    def parse(self, stream):
        data, stream = stream.eat(1)
        if data != None:
            yield ParsingProgress(Flag(data), stream)
    def __init__(self, data=bitarray('0')):
        self.data = data
    def __str__(self):
        return self.data.to01()
    def fuzz(self):
        yield Flag(bitarray('0'))
        yield Flag(bitarray('1'))
    def serialize(self):
        return self.data

class Blob(Terminal):
    # used when length is known at before parse-time
    def parse(self, stream):
        data, stream = stream.eat(self.num_bits)
        if data != None:
            yield ParsingProgress(Blob(data, num_bits=self.num_bits), stream)
    def __init__(self, data=None, num_bits=0):
        self.num_bits = num_bits
        self.data = data if data != None else bitarray('0' * self.num_bits)
    def __str__(self):
        return self.data.to01()
    def get_value(self):
        return bitarray_util.ba2int(self.data)
    def fuzz(self):
        yield Blob(bitarray('0' * self.num_bits))
        yield Blob(bitarray('1' * self.num_bits))
        yield Blob(bitarray('')) # this breaks the structure
    def serialize(self):
        return self.data

class DynamicBlob(Terminal):
    # used when length is only known at parse-time
    # Warning! param get_num_bits must be ideponent
    # TODO: add parent reference to all grammar constructors because they need to be linked in both directions
    def parse(self, stream):
        num_bits = self.get_num_bits(self)
        data, stream = stream.eat(num_bits)
        if data != None:
            yield ParsingProgress(DynamicBlob(data, get_num_bits=self.get_num_bits), stream)
    def __init__(self, data=bitarray(''), get_num_bits=lambda this: 0):
        self.get_num_bits = get_num_bits
        self.data = data
    def __str__(self):
        return self.data.to01()
    def get_value(self):
        return bitarray_util.ba2int(self.data)
    def fuzz(self):
        num_bits = len(self.data)
        yield Blob(bitarray('0' * num_bits))
        yield Blob(bitarray('1' * num_bits))
        yield Blob(bitarray('')) # this breaks the structure
    def serialize(self):
        return self.data

class Sequence(NonTerminal):
    # This is analogous to a struct in c
    def parse(self, stream):
        current_progress = [([], stream)]
        for child in self.children:
            next_progress = []
            for parsed_children, remaining_stream in current_progress:
                results = list(child.parse(remaining_stream))
                for result in results:
                    new_child, result_stream = result.get_tuple()
                    next_progress.append((parsed_children + [new_child], result_stream))
            
            current_progress = next_progress
        for children, remaining_stream in current_progress:
            yield ParsingProgress(Sequence(children=children), remaining_stream)
    def __init__(self, children=[]):
        self.children = children # todo: change children to be a dict so that we can name each field
    def __str__(self):
        result = "{\n"
        for child in self.children:
            result += "\t" + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for i in range(len(self.children)):
            mutated_children = self.children[:]
            for mutated_child in self.children[i].fuzz():
                mutated_children[i] = mutated_child
                yield Sequence(mutated_children)
    def serialize(self):
        result = bitarray()
        for child in self.children:
            result += child.serialize()
        return result

class Set(NonTerminal):
    # this is analogous to an array in c
    # this is an abstract class that does not know how the length of the set is determined
    pass

class LengthSet(Set):
    # this is a set in which the length is known before parse-time
    pass

class DynamicLengthSet(Set):
    # this is a set in which the length is known only at parse-time
    pass

class TerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some condition
    pass

class SymbolTerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some special symbol
    pass

class Union(NonTerminal):
    # this is analogous to a union in c
    # this is an abstract class that does not know how to determine which option to parse
    def __str__(self):
        # TODO: allow child to have multiple lines
        result = "(\n"
        for child in self.potential_children:
            result += "\t| " + str(child) + " ***" if child == self.child else "" + "\n"
        result += ")"
        return result
    def serialize(self):
        return self.child.serialize()

class PureUnion(Union):
    # this is a union in which all options are tried (even if a previous option's parse is successful)
    def parse(self, stream):
        parses = []
        for child in self.potential_children:
            for parse in child.parse(stream):
                child_data_model, child_stream = parse.get_tuple()
                yield ParsingProgress(
                    PureUnion(potential_children=self.potential_children, child=child_data_model),
                    child_stream,
                )
    def __init__(self, potential_children, child=None):
        assert len(potential_children) > 0
        self.potential_children = potential_children
        self.child = child if child != None else potential_children[0]
    def fuzz(self):
        for child_data_model in self.child.fuzz():
            yield PureUnion(potential_children=self.potential_children, child=child_data_model)

class ChoiceUnion(Union):
    # this is a union in which the option is determined at parse-time (forward constraint)
    pass
