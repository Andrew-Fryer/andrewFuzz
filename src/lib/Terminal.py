from src.core.BinaryStream import bitarray, bitarray_util
from src.core.DataModel import DataModel
from src.core.ParsingProgress import ParsingProgress

class Terminal(DataModel):
    def set_parent(self, parent):
        # assert not self.parent
        self.parent = parent

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

class Char(Byte):
    def __str__(self):
        return self.data.tobytes()

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
    def __init__(self, data=None, num_bits=None, num_bytes=None):
        if data != None:
            self.num_bits = len(data)
            self.data = data if isinstance(data, bitarray) else bitarray(data)
        else:
            if num_bits != None:
                assert(num_bytes == None)
                self.num_bits = num_bits
            else:
                assert(num_bytes != None)
                self.num_bits = num_bytes * 8
            self.data = bitarray('0' * self.num_bits)
    def __str__(self):
        return self.data.to01()
    def get_value(self):
        return bitarray_util.ba2int(self.data)
    def fuzz(self):
        yield Blob(bitarray('0' * self.num_bits))
        yield Blob(bitarray('1' * self.num_bits))
        yield Blob(bitarray('0' * (self.num_bits - 1) + '1'))
        yield Blob(bitarray('1' * (self.num_bits - 1) + '0'))
        yield Blob(bitarray('')) # this breaks the structure
    def serialize(self):
        return self.data

class String(Blob):
    def __init__(self, string):
        data = ''.join([format(b, 'b').zfill(8) for b in [ord(l) for l in string] + [0]])
        super().__init__(data)
    # TODO: override get_value, __str__, and fuzz

class Number(Blob):
    def __init__(self, value, num_bytes):
        value_bytes = value.to_bytes(num_bytes, 'big')
        data = ''.join([format(b, 'b').zfill(8) for b in value_bytes])
        super().__init__(data)
    def get_value(self):
        return bitarray_util.ba2int(self.data, signed=False)
    def __str__(self):
        return str(bitarray_util.ba2int(self.data, signed=False))
    # TODO: override fuzz

class Uint8(Number):
    def __init__(self, value: int=0):
        super().__init__(value, 1)

class Uint16(Number):
    def __init__(self, value: int=0):
        super().__init__(value, 2)

class Uint32(Number):
    def __init__(self, value: int=0):
        super().__init__(value, 4)

class Uint64(Number):
    def __init__(self, value: int=0):
        super().__init__(value, 8)

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

class Button(Terminal):
    def parse(self, stream):
        if len(stream) == 0:
            yield ParsingProgress(self, stream)
    def __init__(self):
        pass
    def __str__(self):
        return '()'
    def fuzz(self):
        yield Byte(bitarray(''))
        yield Byte(bitarray('0'))
        yield Byte(bitarray('1'))
    def serialize(self):
        return bitarray()
