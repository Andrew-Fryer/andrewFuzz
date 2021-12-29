from src.ParsingProgress import ParsingProgress
from src.NonTerminal import NamedBranchingNonTerminal

class Sequence(NamedBranchingNonTerminal):
    # This is analogous to a struct in c
    def parse(self, stream):
        current_progress = [([], stream)]
        for child in self.children:
            next_progress = []
            for parsed_children, remaining_stream in current_progress:
                results = list(child.parse(remaining_stream))
                for result in results:
                    new_child, result_stream = result.get_tuple()
                    next_progress.append((parsed_children + [new_child], result_stream))
            
            current_progress = next_progress
        for children, remaining_stream in current_progress:
            yield ParsingProgress(Sequence(children=children), remaining_stream)
