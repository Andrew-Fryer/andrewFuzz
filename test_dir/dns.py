from src.__init__ import *

char = Byte()
uint8 = None
uint16 = Sequence(children=[Byte(), Byte()])

# this is my make-shift way to implement hoisting
# TODO: why not define the children dicts first using hoisting and then create the objects?
#    -> will that work?
query = Sequence()
domain = Union()

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

query.set_children(children={
    'name': domain,
    'type': uint16,
    'class': uint16,
})

null = '0000 0000'
c = '0000 1100'
domain.set_children(
    Sequence(children={
        'length': Constraint(uint8, lambda this: this.value != c and this.value != null),
        'letters': LengthSet(char, lambda this: this.parent.children['length']), # TODO: replace `lambda ...` with `helper("../length")`
    }),
    Sequence(children={
        'marker': Literal(c + null), # 0xc0
        'ref': uint8,
    }),
    Literal(null),
)

pass
