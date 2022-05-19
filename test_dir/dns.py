from src.__init__ import *

query = Sequence()
resource_record = Union()

dns = Sequence(children={
    'transactionId': Uint16,
    'flags': Blob(num_bytes=2),
    'numQuestion': Uint16,
    'numAnswer': Uint16,
    'numAuthority': Uint16,
    'numAdditional': Uint16,
    'question': Set(query, lambda this: this.parent.children['numQuestion']),
    'answer': 'asdf',
    'authority': 'asdf',
    'additional': 'asdf',
})

domain = TerminatedSet()

query.set_children({
    'name': domain,
    'type': Uint16,
    'class': Uint16,
})

address = Sequence(children=[Byte(), Byte(), Byte(), Byte()])
resource_record.set_children([
    Sequence(children={
        'name': domain,
        'type': Uint16,
        'class': Uint16,
        'ttl': Uint32,
        'dataLength': Uint16,
        'address': address,
    }),
])

label = Union()
domain.set_details(label, lambda this: this.children['inline'] == None)

null = '0000 0000'
c = '0000 1100'
label.set_children({
    'inline': Sequence({
        'length': Constraint(Uint8, lambda this: this.value != c and this.value != null),
        'letters': LengthSet(Char, lambda this: this.parent.children['length']), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    'pointer': Sequence(children={
        'marker': Literal(c + null), # 0xc0
        'ref': Uint8,
    }),
    'null': Literal(null),
})

pass
