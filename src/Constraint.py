from src.lib.NonTerminal import Wrapper
from src.core.ParsingProgress import ParsingProgress

class Constraint(Wrapper):
    def propagate(self, diffs):
        child = diffs.get('child', self.child)
        return self.__class__(child, self.constraint_function)
    def __init__(self, child, constraint_function):
        super().__init__(child)
        self.constraint_function = constraint_function
    def parse(self, stream, ctx=None):
        for progress_obj in self.child.parse(stream):
            parsed_child, remaining_stream = progress_obj.get_tuple()
            if self.constraint_function(parsed_child): # pass in ctx too?
                yield ParsingProgress(self.propagate({
                    'child': parsed_child,
                }), remaining_stream)
            # else:
            #     print('failed constraint', parsed_child)
    def __str__(self):
        return "<Constraint " + str(self.child) + " >"
    def fuzz(self):
        return self.child.fuzz() # TODO: subclass Constraint to allow us to fuzz different constraints

# class notEqualsConstraint(Constraint):
#     def __init__(self, child, )
#     def fuzz
