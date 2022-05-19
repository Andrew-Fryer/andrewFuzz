from src.core.ParsingProgress import ParsingProgress
from src.core.DataModel import DataModel
from src.core.BinaryStream import bitarray

class NonTerminal(DataModel):
    def __init__(self, children=None):
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
    def set_parent(self, parent):
        # assert not self.parent
        self.parent = parent\

class BranchingNonTerminal(NonTerminal):
    def __init__(self, children: dict={}):
        super().__init__(children)
    def set_children(self, children: dict):
        super().link_children(children)

class NamedBranchingNonTerminal(BranchingNonTerminal):
    # `self.children` is a dict
    def __str__(self):
        result = "{\n"
        for child_name, child in self.children.items():
            result += "\t" + child_name + ": " + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for child_name, child in self.children.items():
            mutated_children = self.children.copy()
            for mutated_child in child.fuzz():
                mutated_children[child_name] = mutated_child
                yield self.__class__(mutated_children) # eww, this will break if the sub-class takes different parameters...
    def serialize(self):
        result = bitarray()
        for child in self.children.values(): # this works because python dicts preserve order
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class UnNamedBranchingNonTerminal(BranchingNonTerminal):
    # `self.children` is a list
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
                yield self.__class__(mutated_children) # eww, this will break if the sub-class takes different parameters...
    def serialize(self):
        result = bitarray()
        for child in self.children:
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class NonBranchingNonTerminal(NonTerminal):
    def __init__(self, children: list=[]):
        super().__init__(children)
    def set_children(self, children: list):
        super().link_children(children)

class Wrapper(NonBranchingNonTerminal):
    def __init__(self, child):
        super().__init__()
        self.child = child
    def __str__(self):
        return str(self.child)
    def parse(self, stream):
        for parsing_progress in self.child.parse(stream):
            parsed_child, remaining_stream = parsing_progress.get_tuple()
            yield ParsingProgress(self.__class__(parsed_child), remaining_stream)
    def fuzz(self):
        for mutated_child in self.child.fuzz():
            yield self.__class__(mutated_child)
    def serialize(self):
        return self.child.serialize()
