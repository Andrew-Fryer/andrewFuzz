from src.NonTerminal import UnNamedBranchingNonTerminal
from src.ParsingProgress import ParsingProgress

class Set(UnNamedBranchingNonTerminal):
    # this is analogous to an array in c
    # this is an abstract class that does not know how the length of the set is determined
    def __init__(self, child_prototype, children=None):
        super().__init__(children)
        self.child_prototype = child_prototype
        self.children = None
    def __parse__():
        raise NotImplementedError

class LengthSet(Set):
    # this is a set in which the length is known before parse-time
    def __init__(self, child_prototype, length, children=None):
        pass

class DynamicLengthSet(Set):
    # this is a set in which the length is known only at parse-time
    def __init__(self, child_prototype, length_function, children=None):
        super().__init__(child_prototype, children)
        self.lenth_function = length_function
    def parse(self, stream): # Note that this is very similar to `Sequence.parse`
        length = self.lenth_function(self)
        current_progress = [([], stream)]
        for i in range(length):
            next_progress = []
            for parsed_children, remaining_stream in current_progress:
                results = list(self.child_prototype.parse(remaining_stream))
                for result in results:
                    new_child, result_stream = result.get_tuple()
                    next_progress.append((parsed_children + [new_child], result_stream))
                    # I would love to use Monads here to do the higher-level stuff nicely :)
            
            current_progress = next_progress
        for children, remaining_stream in current_progress:
            yield ParsingProgress(DynamicLengthSet(children=children), remaining_stream)


class TerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some condition
    pass

class SymbolTerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some special symbol
    pass
