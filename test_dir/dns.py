from src.__init__ import *

char = Byte()
uint8 = Byte() # TODO: I think it would better for Uint8 to be a subclass of Byte...
uint16 = Sequence(children=[Byte(), Byte()])

class U16(DataModel):
    pass
class U32(DataModel):
    pass

query = Sequence()
resource_record = Union()

dns = Sequence(children={
    'transactionId': uint16,
    'flags': Blob(num_bytes=2),
    'numQuestion': uint16,
    'numAnswer': uint16,
    'numAuthority': uint16,
    'numAdditional': uint16,
    'question': Set(query, lambda this: this.parent.children['numQuestion']),
    'answer': 'asdf',
    'authority': 'asdf',
    'additional': 'asdf',
})

domain = TerminatedSet()

query.set_children({
    'name': domain,
    'type': uint16,
    'class': uint16,
})

address = Sequence(children=[Byte(), Byte(), Byte(), Byte()])
resource_record.set_children([
    Sequence(children={
        'name': domain,
        'type': U16,
        'class': U16,
        'ttl': U32,
        'dataLength': U16,
        'address': address,
    }),
])

label = Union()
domain.set_details(label, lambda this: this.children['inline'] == None)

null = '0000 0000'
c = '0000 1100'
label.set_children({
    'inline': Sequence({
        'length': Constraint(uint8, lambda this: this.value != c and this.value != null),
        'letters': LengthSet(char, lambda this: this.parent.children['length']), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    'pointer': Sequence(children={
        'marker': Literal(c + null), # 0xc0
        'ref': uint8,
    }),
    'null': Literal(null),
})

pass
