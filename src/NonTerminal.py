from .DataModel import DataModel
from src.BinaryStream import bitarray

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

class BranchingNonterminal(NonTerminal):
    def __init__(self, children=None):
        self.children = children # todo: change children to be a dict so that we can name each field
    def set_children(self, children):
        self.children = children
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

class Wrapper(NonTerminal):
    pass
