from src.__init__ import *

session_state = Session()

sign_in_grammar = Sequence({
    "email": String(session_state.get('user_email')),
    "password": String(session_state.get('password')),
})

sign_in_response_grammar = Sequence({
    "token": Blob(num_bits=256),
})

get_handle_grammar = Sequence({
    "token": Blob(session_state.get('token')),
    "file_path": String('/mnt/a/b/c/file')
})

get_handle_response_grammar = Sequence({
    "handle": Blob(num_bits=256),
})

get_data_grammar = Sequence({
    'handle': Blob(session_state('handle')), # hopefully this gets mutated to point somewhere that doesn't make sense or at /etc/shadow :)
})

get_data_response_grammar = Sequence({
    'length': Byte(),
    'data': DynamicBlob(get_num_bits=lambda this: this.parent.children['length']),
})

sign_in_grammar = Sequence({
    "email": String(session_state.get('user_email'))
})

sign_in_response_grammar = Sequence({
    "status": Byte(), # TODO: make a sub-class that gives meaning to values
})
