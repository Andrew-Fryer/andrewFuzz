from itertools import chain, product

class Parse:
    # this class is essentially the Haskell List Monad
    def __init__(self, iterator):
        # iterator is of (DataModel, BinaryStream) tuples
        self.iterator = iterator
    def _map(self, parse_function):
        for data_model, stream in self.iterator:
            iter = parse_function(stream)
            yield (data_model, iter)
    def _flatten(self, double_wrapped, join):
        for data_model_1, iter in double_wrapped:
            for data_model_2, remaining_stream in iter:
                yield join(data_model_1, data_model_2), remaining_stream
    def flat_map(self, parse_function, join):
        # `join` is a function that takes 2 data models and 
        return Parse(self.flatten(self.map(parse_function), join))
    def flat_map_add(self, parse_function):
        return self.flat_map(parse_function, chain)
    def flat_map_mult(self, parse_function):
        return self.flat_map(parse_function, product)

class Fuzz:
    def __init__(self, iterator):
        # iterator is of (DataModel, Fuzziness) tuples
        self.iterator = iterator
    # def 
