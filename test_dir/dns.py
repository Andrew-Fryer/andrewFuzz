from src.__init__ import *

query = Sequence()
resource_record = Union()

dns = Sequence(children={
    'transactionId': Uint16(),
    'flags': Blob(num_bytes=2),
    'numQuestion': Uint16(),
    'numAnswer': Uint16(),
    'numAuthority': Uint16(),
    'numAdditional': Uint16(),
    'question': DynamicLengthSet(query, lambda this: this.parent.children['numQuestion']),
    'answer': DynamicLengthSet(resource_record, lambda this: this.parent.children['numAnswer']),
    'authority': DynamicLengthSet(resource_record, lambda this: this.parent.children['numAuthority']),
    'additional': DynamicLengthSet(resource_record, lambda this: this.parent.children['numAdditional']),
})

domain = TerminatedSet()

query.set_children({
    'name': domain,
    'type': Uint16(),
    'class': Uint16(),
})

address = Sequence(children=[Byte(), Byte(), Byte(), Byte()])
resource_record.set_children([
    Sequence(children={
        'name': domain,
        'type': Uint16(),
        'class': Uint16(),
        'ttl': Uint32(),
        'dataLength': Uint16(),
        'address': address,
    }),
    # todo
])

label = Union()
domain.set_details(label, lambda this: this.children['inline'] == None)

null = '0000 0000'
c = '0000 1100'
label.set_children({
    'inline': Sequence({
        'length': Constraint(Uint8(), lambda this: this.value != c and this.value != null),
        'letters': LengthSet(Char(), lambda this: this.parent.children['length']), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    'pointer': Sequence(children={
        'marker': Literal(c + null), # 0xc0
        'ref': Uint8(),
    }),
    'null': Literal(null),
})

pass

my_data_model = dns
print(my_data_model.serialize())

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
