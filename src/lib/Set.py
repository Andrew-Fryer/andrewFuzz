from src.lib.NonTerminal import UnNamedBranchingNonTerminal
from src.core.ParsingProgress import ParsingProgress
from src.core.Ctx import Ctx

class Set(UnNamedBranchingNonTerminal):
    # this is analogous to an array in c
    # this is an abstract class that does not know how the length of the set is determined
    def __init__(self, child_prototype, children=None):
        super().__init__(children)
        self.child_prototype = child_prototype
        # self.children = None # why did I do this???
    def __parse__():
        raise NotImplementedError

class LengthSet(Set):
    # this is a set in which the length is known before parse-time
    def __init__(self, child_prototype, length, children=None):
        pass
        # todo

class DynamicLengthSet(Set):
    # this is a set in which the length is known only at parse-time
    def __init__(self, child_prototype, length_function, children=None):
        super().__init__(child_prototype, children)
        self.length_function = length_function
    def parse(self, stream, ctx=None): # Note that this is very similar to `Sequence.parse`
        length = self.length_function(Ctx(p=ctx))
        current_progress = [([], stream)]
        for i in range(length):
            next_progress = []
            for parsed_children, remaining_stream in current_progress:
                results = list(self.child_prototype.parse(remaining_stream, Ctx(c=parsed_children, p=ctx)))
                for result in results:
                    new_child, result_stream = result.get_tuple()
                    next_progress.append((parsed_children + [new_child], result_stream))
                    # I would love to use Monads here to do the higher-level stuff nicely :)
            
            current_progress = next_progress
        for children, remaining_stream in current_progress:
            yield ParsingProgress(DynamicLengthSet(self.child_prototype, self.length_function, children=children), remaining_stream)


class TerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some condition
    def __init__(self, child_prototype=None, terminate_function=None, children=None):
        if child_prototype != None:
            super().__init__(child_prototype, children)
        else:
            assert(children == None)
        self.terminate_function = terminate_function
    def set_details(self, child_prototype, terminate_function, children=None):
        super().__init__(child_prototype, children)
        self.terminate_function = terminate_function
    def parse(self, stream, ctx=None):
        # TODO: construct a DAG on nodes for efficiency

        remaining_stream = stream
        children = []
        cctx = Ctx(c=children, p=ctx)
        terminated = False
        while not terminated:
            results = list(self.child_prototype.parse(remaining_stream, cctx))
            # assert len(results) == 1 # todo
            if len(results) == 0:
                return
            child, remaining_stream = results[0].get_tuple()
            children.append(child)
            terminated = self.terminate_function(child)
        yield TerminatedSet(self.child_prototype, self.terminate_function, children)

class SymbolTerminatedSet(Set):
    # this is a set in which the end of the set is indicated by some special symbol
    pass
