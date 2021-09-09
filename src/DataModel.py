class Parser:
    # -parser     -> it can parse a binary stream into a list of ParsingProgress objects (which contain new instances of this class)
    def parse(self, stream):
        pass

class AST:
    def __str__(self):
        pass

class Fuzzer:
    # -fuzzer     -> it can produce mutated versions of itself (new instances of this class)
    def fuzz(self):
        pass

class Serializer:
    # -serializer -> it can deparse its state by performing an inorder tree traversal
    def serialize(self):
        pass

class DataModel:
    # borrowing the name "DataModel" from Peach Fuzzer
    def __init__(self, parser, fuzzer, serializer):
        self._parser = parser
        self._fuzzer = fuzzer
        self._serializer = serializer
    def clone(self, parser=None, fuzzer=None, serializer=None):
        parser = parser or self._parser
        fuzzer = fuzzer or self._fuzzer
        serializer = serializer or self._serializer
        return self.__class__(parser, fuzzer, serializer)
    # An instance of this class is a:
    # -grammar    -> writing a grammar is done by calling the constructor
    # -AST        -> it stores 
    pass