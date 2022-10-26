from src.core.FeatureVector import FeatureVector


class Breedable:
    def propagate(self, diffs: dict):
        # used by parsing and fuzzing processes instead of __init__
        # To be useful, the diffs dictionary is used to specify how the generated object should differ from self
        # Basically, if your subclass overrides __init__, you also have to override this.
        raise NotImplementedError

class Parser:
    def parse(self, stream, ctx=None):
        # Note that the returned DataModel object must be the root of a TREE while self is allowed to be a graph (allows for recursive grammars)
        raise NotImplementedError

class AST:
    def __str__(self):
        raise NotImplementedError

class Fuzzer:
    def fuzz(self):
        raise NotImplementedError

class Vectorizer:
    def features(self):
        raise NotImplementedError
    def do_vectorization(self, v, depth):
        raise NotImplementedError
    def vectorize(self):
        v = FeatureVector(self.features([]))
        self.do_vectorization(v, 0)
        return v

class Serializer:
    def serialize(self):
        raise NotImplementedError

class DataModel(Breedable, Parser, Fuzzer, Vectorizer, Serializer): # wait a minute, why don't I use composition here?
    # borrowing the name "DataModel" from Peach Fuzzer
    # An instance of this class is a:
    # -grammar    -> writing a grammar is done by calling the constructor
    # -parser     -> it can parse a binary stream into a list of ParsingProgress objects (which contain new instances of this class)
    # -AST        -> it stores 
    # -fuzzer     -> it can produce mutated versions of itself (new instances of this class)
    # -serializer -> it can deparse its state by performing an inorder tree traversal
    pass
