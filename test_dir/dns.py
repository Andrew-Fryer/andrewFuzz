from src.__init__ import *

char = Byte()
uint8 = None
uint16 = Sequence(children=[Byte(), Byte()])

# this is my make-shift way to implement hoisting
query = Shell()
domain = Shell()

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

query.value = Sequence(children={
    'name': domain,
    'type': uint16,
    'class': uint16,
})

null = '0000 0000'
c = '0000 1100'
domain = Union(
    Sequence(children={
        'length': Constraint(uint8, lambda this: this.value != c and this.value != null),
        'letters': LengthSet(char, lambda this: this.parent.children['length']),
    }),
    Sequence(children={
        'marker': Literal(c + null), # 0xc0
        'ref': uint8,
    }),
    Literal(null),
)

pass
