from copy import copy

from src.lib.NonTerminal import NonBranchingNonTerminal
from src.core.ParsingProgress import ParsingProgress
from src.core.Ctx import Ctx

class Union(NonBranchingNonTerminal):
    # this is analogous to a union in c
    # this is an abstract class that does not know how to determine which option to parse
    def set_child(self, child):
        super().link_child(child)
    def set_potential_children(self, potential_children):
        self.potential_children = potential_children
        assert len(potential_children) > 0
        self.potential_children = potential_children
        if self.child == None:
            self.child = potential_children[0]
    def __str__(self):
        # TODO: allow child to have multiple lines
        result = "(\n"
        for child in self.potential_children:
            result += "\t| " + str(child) + " ***" if child == self.child else "" + "\n"
        result += ")"
        return result
    def serialize(self):
        return self.child.serialize()

class PureUnion(Union):
    # this is a union in which all options are tried (even if a previous option's parse is successful)
    def parse(self, stream, ctx=None):
        cctx = Ctx(p=ctx)
        for potential_child in self.potential_children:
            for progress_obj in potential_child.parse(stream, cctx):
                parsed_child, remaining_stream = progress_obj.get_tuple()
                yield ParsingProgress(
                    PureUnion(potential_children=self.potential_children, child=parsed_child),
                    remaining_stream,
                )
    def __init__(self, potential_children=None, child=None):
        super().__init__(child)
        if potential_children != None:
            self.set_potential_children(potential_children)
    def fuzz(self):
        for child in [self.child]: #self.potential_children: # this causes infinite recursion for recursive grammars :|. Could I cap it somehow???
            for child_data_model in child.fuzz():
                c = copy(self)
                c.set_child(child_data_model)
                yield c

class ChoiceUnion(Union):
    # this is a union in which the option is determined at parse-time (forward constraint)
    pass
