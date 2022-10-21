from copy import copy

from src.core.ParsingProgress import ParsingProgress
from src.core.DataModel import DataModel
from src.core.BinaryStream import bitarray
from src.core.FeatureVector import FeatureVector

class NonTerminal(DataModel):
    def set_parent(self, parent):
        # assert not self.parent
        self.parent = parent

class BranchingNonTerminal(NonTerminal):
    def __init__(self, children=None):
        self.children = None
        if children != None:
            self.link_children(children)
    def link_children(self, children):
        self.children = children
        '''
        Note that parents only make sense when a DataModel is a tree, which is garanteed when it is used as an AST, when it is the result of a parse, and when it is the result of a fuzz of a parse.
        A DataModel may only be a DAG (or even a graph with cycles).
        For now, we go on assigning parents in the DAG even though they aren't useful.
        Just be careful not to think the parent field in a DAG is the only parent.
        '''
        if isinstance(children, dict):
            children = children.values()
        for child in children:
            child.set_parent(self)
    def vectorize(self): # TODO: inline data that is always present into the feature vector
        v = FeatureVector({
            self.__class__.__name__: 1,
        })
        child_data_models = self.children if isinstance(self.children, list) else self.children.values()
        v.merge_children([c.vectorize() for c in child_data_models])
        return v

class NamedBranchingNonTerminal(BranchingNonTerminal):
    def __init__(self, children: dict={}):
        super().__init__(children)
    def set_children(self, children: dict):
        super().link_children(children)
    # `self.children` is a dict
    def __str__(self):
        result = "{\n"
        for child_name, child in self.children.items():
            result += "\t" + child_name + ": " + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for child_name, child in self.children.items():
            for mutated_child in child.fuzz():
                mutated_children = self.children.copy()
                mutated_children[child_name] = mutated_child
                c = copy(self)
                c.set_children(mutated_children)
                yield c
    def serialize(self):
        result = bitarray()
        for child in self.children.values(): # this works because python dicts preserve order
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class UnNamedBranchingNonTerminal(BranchingNonTerminal):
    # `self.children` is a list
    def __init__(self, children: list=[]):
        super().__init__(children)
    def set_children(self, children: list):
        super().link_children(children)
    def __str__(self):
        result = "{\n"
        for child in self.children:
            result += "\t" + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for i in range(len(self.children)):
            for mutated_child in self.children[i].fuzz():
                mutated_children = self.children[:]
                mutated_children[i] = mutated_child
                c = copy(self)
                c.set_children(mutated_children)
                yield c
    def serialize(self):
        result = bitarray()
        for child in self.children:
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class NonBranchingNonTerminal(NonTerminal):
    def __init__(self, child=None):
        self.child = None
        if child != None:
            self.link_child(child)
    def link_child(self, child):
        self.child = child
        '''
        Note that parents only make sense when a DataModel is a tree, which is garanteed when it is used as an AST, when it is the result of a parse, and when it is the result of a fuzz of a parse.
        A DataModel may only be a DAG (or even a graph with cycles).
        For now, we go on assigning parents in the DAG even though they aren't useful.
        Just be careful not to think the parent field in a DAG is the only parent.
        '''
        child.set_parent(self)
    def vectorize(self):
        v = FeatureVector({
            self.__class__.__name__: 1,
        })
        v.merge([self.child.vectorize()])
        return v

class Wrapper(NonBranchingNonTerminal):
    def __str__(self):
        return str(self.child)
    def set_child(self, child):
        super().link_child(child)
    def parse(self, stream, ctx_children=None):
        for parsing_progress in self.child.parse(stream, ctx_children):
            parsed_child, remaining_stream = parsing_progress.get_tuple()
            yield ParsingProgress(self.__class__(parsed_child), remaining_stream)
    def fuzz(self):
        for mutated_child in self.child.fuzz():
            yield self.__class__(mutated_child)
    def serialize(self):
        return self.child.serialize()
