from bitarray import bitarray, util as bitarray_util

from src.__init__ import *

stream = BinaryStream('0000 0000  0000 0000  1')
my_data_model = Sequence()
my_data_model.set_children({
    'b': Byte(),
    'u': PureUnion(potential_children=[
        Flag(),
        my_data_model, # recursion inside the grammar!
    ]),
})
results = my_data_model.parse(stream)
results_list = list(results)

ast, stream = results_list[1].get_tuple() # the 1 is a hack...

assert len(stream) == 0
print('ast looks like:', ast)

fuzz = ast.fuzz()
print('here is the fuzz:')
for ast in fuzz:
    print('\t' + str(ast.serialize()))

pass
