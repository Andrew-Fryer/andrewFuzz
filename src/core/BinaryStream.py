from bitarray import bitarray, util as bitarray_util # this gives us performant, bit-wise binary operations (Python's stock binary operations are all byte-wise)

class BinaryStream:
    # this class is wrapper for a bitarray
    # the idea is to avoid copying the actual data unless we really need to
    # note that this class is immutable to enable easy back-tracking
    def __init__(self, bits, pos=0):
        self.bits = bits if isinstance(bits, bitarray) else bitarray(bits)
        self.pos = pos
    def __str__(self):
        return str(self.bits[self.pos:])
    def clone(self):
        return BinaryStream(self.bits, self.pos)
    def eat(self, num_bits=8):
        # returns None if we don't have enough bits
        new_pos = self.pos + num_bits
        if new_pos > len(self.bits):
            return None, self
        result = self.bits[self.pos:new_pos]
        return result, BinaryStream(self.bits, new_pos)
    def __len__(self):
        return len(self.bits) - self.pos
