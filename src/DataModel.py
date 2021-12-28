class Parser:
    def parse(self, stream):
        # Note that the returned DataModel object must be the root of a TREE while self is allowed to be a graph (allows for recursive grammars)
        raise NotImplementedError

class AST:
    def __str__(self):
        raise NotImplementedError

class Fuzzer:
    def fuzz(self):
        raise NotImplementedError

class Serializer:
    def serialize(self):
        raise NotImplementedError

class DataModel(Parser, Fuzzer, Serializer): # wait a minute, why don't I use composition here?
    # borrowing the name "DataModel" from Peach Fuzzer
    # An instance of this class is a:
    # -grammar    -> writing a grammar is done by calling the constructor
    # -parser     -> it can parse a binary stream into a list of ParsingProgress objects (which contain new instances of this class)
    # -AST        -> it stores 
    # -fuzzer     -> it can produce mutated versions of itself (new instances of this class)
    # -serializer -> it can deparse its state by performing an inorder tree traversal
    pass
