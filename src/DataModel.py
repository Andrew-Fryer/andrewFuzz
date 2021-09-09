class Parser:
    def parse(self, stream):
        pass

class AST:
    def __str__(self):
        pass

class Fuzzer:
    def fuzz(self):
        pass

class Serializer:
    def serialize(self):
        pass

class DataModel(Parser, Fuzzer, Serializer): # wait a minute, why don't I use composition here?
    # borrowing the name "DataModel" from Peach Fuzzer
    # An instance of this class is a:
    # -grammar    -> writing a grammar is done by calling the constructor
    # -parser     -> it can parse a binary stream into a list of ParsingProgress objects (which contain new instances of this class)
    # -AST        -> it stores 
    # -fuzzer     -> it can produce mutated versions of itself (new instances of this class)
    # -serializer -> it can deparse its state by performing an inorder tree traversal
    pass
