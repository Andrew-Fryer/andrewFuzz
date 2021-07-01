from bitarray import bitarray, util as bitarray_util # this gives us performant, bit-wise binary operations (Python's stock binary operations are all byte-wise)

# TODO: use inheritence to yet rid of the icky duplcate methods

class BinaryStream:
    # this class is wrapper for a bitarray
    # the idea is to avoid copying the actual data unless we really need to
    def __init__(self, bits, pos=0):
        self.bits = bits
        self.pos = pos
    def clone(self):
        return BinaryStream(self.bits, self.pos)
    def eat(self, num_bits=8):
        new_pos = self.pos + num_bits
        assert new_pos / 8 <= len(self.bits)
        result = self.bits[self.pos:self.pos + num_bits]
        self.pos += num_bits
        return result
    def __len__(self):
        return len(self.bits) - self.pos

class ParsingProgress:
    # this class is a named tuple which stores the progress of a parse
    def __init__(self, ast, stream):
        self.ast = ast
        self.stream = stream
    def get_tuple(self):
        return self.ast, self.stream

class DataModel:
    # borrowing the name "DataModel" from Peach Fuzzer
    # An instance of this class is a:
    # -grammar    -> writing a grammar is done by calling the constructor
    # -parser     -> it can parse a binary stream into a list of ParsingProgress objects (which contain new instances of this class)
    # -AST        -> it stores 
    # -fuzzer     -> it can produce mutated versions of itself (new instances of this class)
    # -serializer -> it can deparse its state by performing an inorder tree traversal
    def parse(self, stream):
        pass
    def fuzz(self):
        pass
    def serialize(self):
        pass

class NonTerminal(DataModel):
    def __init__(self, children=[], allow_recursion=False):
        self._allow_recursion = allow_recursion # used to allow recursion in a DataModel when used as a grammar, and not when used as an AST
        for child in children:
            child.set_parent(self)
    def set_parent(self, parent):
        if self._allow_recursion:
            self.parent = (self.parent or []).append(parent)
        assert not self.parent
        self.parent = parent

class Terminal(DataModel):
    def set_parent(self, parent):
        assert not self.parent
        self.parent = parent

class Byte(Terminal):
    def parse(self, stream):
        data = stream.eat(8)
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
        data = stream.eat(1)
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
        data = stream.eat(self.num_bits)
        yield ParsingProgress(Blob(data, num_bits=self.num_bits), stream)
    def __init__(self, data=bitarray(''), num_bits=0):
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
        data = stream.eat(num_bits)
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
        children = []
        for child in self.children:
            results = list(child.parse(stream))
            assert len(results) <= 1
            if len(results) == 0:
                return []
            child_ast, stream = results[0].get_tuple()
            children.append(child_ast)
        yield ParsingProgress(Sequence(children=children), stream)
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

class LenSet(Set):
    # this is a set in which the length is known before parse-time
    pass

class DynamicLenSet(Set):
    # this is a set in which the length is determined by an expression whose value is known only at parse-time
    pass

class TerminatedSet(Set):
    # this is a set in which the end of the set is indicated by a special terminator symbol
    pass

class Union(NonTerminal):
    # this is analogous to an array in c
    # this is an abstract class that does not know how to determine which option to parse
    pass

class PureUnion(Union):
    # this is a union in which all options are tried (even if a previous option's parse is successful)
    pass

class ChoiceUnion(Union):
    # this is a union in which the option is determined by an expression whose value is determined at parse-time
    pass
