from src.__init__ import *

def debug():
    return True

class Query(Sequence):
    pass
query = Query()
class ResourceRecord(PureUnion):
    pass
resource_record = ResourceRecord()

dns = Sequence(children={
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
    # 'end': Button(),
})

class Domain(TerminatedSet):
    pass
domain = Domain()

query.set_children({
    'name': domain,
    'type': Uint16(),
    'class': Uint16(),
})

class Address(Sequence):
    pass
address = Address(children=[Byte(), Byte(), Byte(), Byte()])
resource_record.set_potential_children([
    Sequence(children={
        'name': domain,
        'type': Uint16(),
        'class': Uint16(),
        'ttl': Uint32(),
        'dataLength': Uint16(),
        'data': DynamicLengthSet(Byte(), lambda this: debug() and this.parent.children['dataLength'].get_value()),
    }),
    # todo
])

class Label(PureUnion):
    pass
label = Label()
def terminate_function(this):
    if not isinstance(this.child, Sequence):
        print('encountered null')
        return True
    if not 'letters' in this.child.children:
        print('encountered ref')
        return True
    print('encountered letters')
    return False
domain.set_details(label, terminate_function)
# domain.set_details(label, lambda this: not isinstance(this.child, Sequence) or not hasattr(this.child.children, 'letters'))

null = bitarray('0000 0000')
c = bitarray('0000 1100')
label.set_potential_children([
    Sequence({
        'length': Constraint(Uint8(), lambda this: debug() and this.data != c and this.data != null),
        'letters': DynamicLengthSet(Char(), lambda this: debug() and this.parent.children['length'].child.get_value()), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    Sequence(children={
        'marker': Literal(c + null), # 0xc0
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
