from copy import copy

from src.core.ParsingProgress import ParsingProgress
from src.core.DataModel import DataModel
from src.core.BinaryStream import bitarray
from src.core.FeatureVector import FeatureVector

class NonTerminal(DataModel):
    def set_parent(self, parent):
        # assert not self.parent
        self.parent = parent
    def get_children_data_models(self):
        raise NotImplementedError
    def get_all_potential_children_data_models(self):
        return self.get_children_data_models() # to be overridden by Union
    def features(self, seen):
        for el in seen:
            if self is el: # note that python sets use equality rather than identity
                # this should prevent infinite recursion for cyclic grammars
                return []
        seen.append(self)
        features = [self.__class__.__name__]
        child_data_models = self.get_all_potential_children_data_models()
        for c in child_data_models:
            for f in c.features(seen):
                if f not in features:
                    features.append(f)
        return features
    def do_vectorization(self, v, depth): # TODO: inline data that is always present into the feature vector
        v.tally(self.__class__.__name__, depth)
        for c in self.get_children_data_models():
            c.do_vectorization(v, depth + 1)

class BranchingNonTerminal(NonTerminal):
    def __init__(self, children=None):
        self.children = None
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
    def get_children_data_models(self):
        if isinstance(self.children, list):
            return self.children
        elif isinstance(self.children, dict):
            return self.children.values()
        else:
            assert(False)

class NamedBranchingNonTerminal(BranchingNonTerminal):
    def __init__(self, children: dict={}):
        super().__init__(children)
    def set_children(self, children: dict):
        super().link_children(children)
    # `self.children` is a dict
    def propagate(self, diffs):
        children = diffs.get('children', self.children)
        return self.__class__(children)
    def __str__(self):
        result = "{\n"
        for child_name, child in self.children.items():
            result += "\t" + child_name + ": " + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for child_name, child in self.children.items():
            for mutated_child in child.fuzz():
                mutated_children = self.children.copy()
                mutated_children[child_name] = mutated_child
                c = copy(self)
                c.set_children(mutated_children)
                yield c
    def breed(self, other):
        assert(isinstance(other, self.__class__))
        children_even = {}
        children_odd = {}
        i = 0
        for child_name in self.children.keys():
            c_even, c_odd = (self.children[child_name], other.children[child_name]) if i & 1 else (other.children[child_name], self.children[child_name])
            children_even[child_name] = c_even
            children_odd[child_name] = c_odd
            i += 1
        yield self.propagate({
            'children': children_even,
        })
        # we use other here just in case there is a different between self and other from a mutation I haven't dreamt up yet
        yield other.propagate({
            'children': children_odd,
        })
    def serialize(self):
        result = bitarray()
        for child in self.children.values(): # this works because python dicts preserve order
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class UnNamedBranchingNonTerminal(BranchingNonTerminal):
    # `self.children` is a list
    def __init__(self, children: list=[]):
        super().__init__(children)
    def set_children(self, children: list):
        super().link_children(children)
    def __str__(self):
        result = "{\n"
        for child in self.children:
            result += "\t" + str(child) + ",\n"
        result += "}"
        return result
    def fuzz(self):
        for i in range(len(self.children)):
            for mutated_child in self.children[i].fuzz():
                mutated_children = self.children[:]
                mutated_children[i] = mutated_child
                c = copy(self)
                c.set_children(mutated_children)
                yield c
    def breed(self, other):
        assert(isinstance(other, self.__class__))
        all_children = self.children + other.children
        children_odd = []
        children_even = []
        for c_ind in range(len(all_children)):
            c = all_children[c_ind]
            if c_ind & 1:
                children_odd.append(c)
            else:
                children_even.append(c)
        yield self.propagate({
            'children': children_even,
        })
        yield other.propagate({
            'children': children_odd,
        })
    def serialize(self):
        result = bitarray()
        for child in self.children:
            result += child.serialize() # TODO: I might be able to get better performance by wrapping bitarray and implementing + as just remembering the operands...
        return result

class NonBranchingNonTerminal(NonTerminal):
    def __init__(self, child=None):
        self.child = None
        if child != None:
            self.link_child(child)
    def link_child(self, child):
        self.child = child
        '''
        Note that parents only make sense when a DataModel is a tree, which is garanteed when it is used as an AST, when it is the result of a parse, and when it is the result of a fuzz of a parse.
        A DataModel may only be a DAG (or even a graph with cycles).
        For now, we go on assigning parents in the DAG even though they aren't useful.
        Just be careful not to think the parent field in a DAG is the only parent.
        '''
        child.set_parent(self)
    def get_children_data_models(self):
        return [self.child]
    def breed(self, other):
        assert(isinstance(other, self.__class__))
        yield self.propagate({})
        yield other.propagate({})

class Wrapper(NonBranchingNonTerminal):
    def __str__(self):
        return str(self.child)
    def set_child(self, child):
        super().link_child(child)
    def parse(self, stream, ctx_children=None):
        for parsing_progress in self.child.parse(stream, ctx_children):
            parsed_child, remaining_stream = parsing_progress.get_tuple()
            yield ParsingProgress(self.propagate({
                'child': parsed_child,
            }), remaining_stream)
    def fuzz(self):
        for mutated_child in self.child.fuzz():
            yield self.propagate({
                'child': mutated_child,
            })
    def serialize(self):
        return self.child.serialize()
