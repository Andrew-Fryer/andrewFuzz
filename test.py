from bitarray import bitarray, util as bitarray_util
from main import *

stream = BinaryStream(bitarray('000000001000000000011111'))
my_data_model = Sequence(children=[
    Byte(),
    Flag(),
    Blob(num_bits=10),
    DynamicBlob(get_num_bits=lambda this: 5)
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
