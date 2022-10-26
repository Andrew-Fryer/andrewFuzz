from copy import copy

from src.lib.NonTerminal import NonBranchingNonTerminal
from src.core.ParsingProgress import ParsingProgress
from src.core.Ctx import Ctx
from src.core.FeatureVector import FeatureVector

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
    def get_all_potential_children_data_models(self):
        return self.potential_children
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
                    self.__class__(potential_children=self.potential_children, child=parsed_child),
                    remaining_stream,
                )
    def __init__(self, potential_children=None, child=None):
        super().__init__(child)
        if potential_children != None:
            self.set_potential_children(potential_children)
    def fuzz(self):
        # ancestor_types = []
        # node = self
        # try:
        #     while True:
        #         ancestor_types.append(node.__class__)
        #         node = node.parent
        # except AttributeError:
        #     pass

        for child in self.potential_children:
            # # prevent infinite recursion for recursive grammars
            # threshold = 3
            # # count num ancestors with same time
            # num_same_ancestors = 0
            # for a_t in ancestor_types:
            #     if a_t == self.__class__:
            #         num_same_ancestors += 1
            # if num_same_ancestors > threshold:
            #     continue
            for child_data_model in child.fuzz():
                c = copy(self)
                c.set_child(child_data_model)
                yield c

class ChoiceUnion(Union):
    # this is a union in which the option is determined at parse-time (forward constraint)
    pass
