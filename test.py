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

data_model, stream = list(results)[0].get_tuple()

assert len(stream) == 0
print('data model looks like:', data_model)

fuzz = data_model.fuzz()
print('here is the fuzz:')
for data_model in fuzz:
    print('\t' + str(data_model.serialize()))


# test alternation
stream = BinaryStream(bitarray('00001111'))
my_data_model = PureUnion(potential_children=[
    Byte(), # succeeds
    Flag(), # succeeds leaving 7 bits
    Blob(num_bits=9), # fails
    DynamicBlob(get_num_bits=lambda this: 8), # succeeds
])
results = list(my_data_model.parse(stream))

pass
