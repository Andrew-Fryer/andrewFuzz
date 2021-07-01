from bitarray import bitarray, util as bitarray_util
from main import *

stream = BinaryStream(bitarray('000000001'))
my_data_model = Sequence(children=[
    Byte(),
    Flag(),
])
results = my_data_model.parse(stream)

ast, stream = list(results)[0].get_tuple()

assert len(stream) == 0
print('ast looks like:', ast)

fuzz = ast.fuzz()
print('here is the fuzz:')
for ast in fuzz:
    print('\t' + str(ast.serialize()))
