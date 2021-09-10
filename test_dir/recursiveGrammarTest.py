from bitarray import bitarray, util as bitarray_util

from src.__init__ import *

stream = BinaryStream(bitarray('0000 0000  0'))
my_data_model = Shell()
my_data_model.value = Sequence(children=[
    Byte(),
    PureUnion(potential_children=[
        Flag(),
        my_data_model, # recursion inside the grammar!
    ])
])
results = my_data_model.parse(stream)

ast, stream = list(results)[0].get_tuple()

assert len(stream) == 0
print('ast looks like:', ast)

fuzz = ast.fuzz()
print('here is the fuzz:')
for ast in fuzz:
    print('\t' + str(ast.serialize()))

pass
