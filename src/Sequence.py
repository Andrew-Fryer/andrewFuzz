from src.ParsingProgress import ParsingProgress
from src.NonTerminal import NamedBranchingNonTerminal

class Sequence(NamedBranchingNonTerminal):
    # This is analogous to a struct in c
    def parse(self, stream):
        current_progress = [({}, stream)]
        for child_name, child in self.children.items():
            next_progress = []
            for parsed_children, remaining_stream in current_progress:
                results = list(child.parse(remaining_stream))
                for result in results:
                    new_child, result_stream = result.get_tuple()
                    parsed_children_copy = parsed_children.copy()
                    parsed_children_copy[child_name] = new_child
                    next_progress.append((parsed_children_copy, result_stream))
            
            current_progress = next_progress
        for children, remaining_stream in current_progress:
            yield ParsingProgress(Sequence(children=children), remaining_stream)
