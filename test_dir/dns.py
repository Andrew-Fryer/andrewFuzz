import sys
import os
import bitarray as ba
# sys.path.append('..')
sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/../'))

from src.__init__ import *
# from src.__init__ import *
# from ..src.__init import *

def debug():
    return True
class DebugSequence(Sequence):
    pass
    # def parse(self, stream, ctx=None):
    #     print('Parsing', self.__class__, stream)
    #     results = list(super().parse(stream, ctx))
    #     if len(results) == 0:
    #         print('failed to parse', self.__class__, results[0].stream)
    #     if len(results) > 1:
    #         print('multiple parses for', self.__class__)
    #     for r in results:
    #         print('parsed', self.__class__, r.data_model, r.stream)
    #         yield r
class Query(DebugSequence):
    pass
query = Query()
# class ResourceRecord(PureUnion):
class ResourceRecord(DebugSequence):
    pass
resource_record = ResourceRecord()

class DNS(DebugSequence):
    pass
dns = DNS(children={
    'transactionId': Uint16(),
    'flags': Blob(num_bytes=2),
    'numQuestion': Uint16(),
    'numAnswer': Uint16(),
    'numAuthority': Uint16(),
    'numAdditional': Uint16(),
    'question': DynamicLengthSet(query, lambda this: this.parent.children['numQuestion'].get_value()),
    'answer': DynamicLengthSet(resource_record, lambda this: debug() and this.parent.children['numAnswer'].get_value()),
    'authority': DynamicLengthSet(resource_record, lambda this: debug() and this.parent.children['numAuthority'].get_value()),
    'additional': DynamicLengthSet(resource_record, lambda this: debug() and this.parent.children['numAdditional'].get_value()),
    'end': Button(),
})

class Domain(TerminatedSet):
    pass
domain = Domain()

query.set_children({
    'name': domain,
    'type': Uint16(),
    'class': Uint16(),
})

class Address(DebugSequence):
    pass
address = Address(children=[Byte(), Byte(), Byte(), Byte()])
# resource_record.set_potential_children([
#     DebugSequence(children={
#         'name': domain,
#         'type': Uint16(),
#         'class': Uint16(),
#         'ttl': Uint32(),
#         'dataLength': Uint16(),
#         'data': DynamicLengthSet(Byte(), lambda this: debug() and this.parent.children['dataLength'].get_value()),
#     }),
#     # todo
# ])
resource_record.set_children({
    'name': domain,
    'type': Uint16(),
    'class': Uint16(),
    'ttl': Uint32(),
    'dataLength': Uint16(),
    'data': DynamicLengthSet(Byte(), lambda this: debug() and this.parent.children['dataLength'].get_value()),
})

class Label(PureUnion):
    pass
label = Label()
def terminate_function(this):
    if not isinstance(this.child, Sequence):
        # print('encountered null')
        return True
    if not 'letters' in this.child.children:
        # print('encountered ref')
        return True
    # print('encountered letters')
    return False
domain.set_details(label, terminate_function)
# domain.set_details(label, lambda this: not isinstance(this.child, Sequence) or not hasattr(this.child.children, 'letters'))

null = bitarray('0000 0000')
c = 0xc0 #bitarray('1100 0000')
label.set_potential_children([
    Sequence({
        'length': Constraint(Uint8(), lambda this: debug() and ba.util.ba2int(this.data) < c and this.data != null), # actually < 0x40
        'letters': DynamicLengthSet(Char(), lambda this: debug() and this.parent.children['length'].child.get_value()), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    Sequence(children={
        'marker': Constraint(Uint8(), lambda this: debug() and ba.util.ba2int(this.data) >= c and this.data != null),
        'ref': Uint8(),
    }),
    Literal(null),
])

pass

# my_data_model = dns

# stream = ???
# results = my_data_model.parse(stream)

# data_model, stream = list(results)[0].get_tuple()

# assert len(stream) == 0
# print('data model looks like:', data_model)

# fuzz = data_model.fuzz()
# print('here is the fuzz:')
# for data_model in fuzz:
#     print('\t' + str(data_model.serialize()))

pass
