from src.NonTerminal import NonBranchingNonTerminal
from src.ParsingProgress import ParsingProgress

class Union(NonBranchingNonTerminal):
    # this is analogous to a union in c
    # this is an abstract class that does not know how to determine which option to parse
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
    def parse(self, stream):
        parses = []
        for child in self.potential_children:
            for parse in child.parse(stream):
                child_data_model, child_stream = parse.get_tuple()
                yield ParsingProgress(
                    PureUnion(potential_children=self.potential_children, child=child_data_model),
                    child_stream,
                )
    def __init__(self, potential_children, child=None):
        assert len(potential_children) > 0
        self.potential_children = potential_children
        self.child = child if child != None else potential_children[0]
    def fuzz(self):
        for child_data_model in self.child.fuzz():
            yield PureUnion(potential_children=self.potential_children, child=child_data_model)

class ChoiceUnion(Union):
    # this is a union in which the option is determined at parse-time (forward constraint)
    pass
