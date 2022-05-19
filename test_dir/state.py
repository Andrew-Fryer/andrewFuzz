from src.__init__ import *

session_state = Session()

session_objects = [Session() for _ in range(4)]
base_session_data = {
    "user_email": "user1@gmail.com",
    "password": "password123",
}
session_objects[0].reset(base_session_data)

def sign_in_grammar():
    return Sequence({
    'endpoint': Uint8(0),
    "email": String(session_state.get('user_email')),
    "password": String(session_state.get('password')),
})

sign_in_response_grammar = Sequence({
    "token": Blob(num_bits=256),
})

def sign_in_check(parsing_results, fuzziness):
    if len(parsing_results) != 1 or len(parsing_results[0].stream) != 0:
        if fuzziness == Fuzziness.correct:
            print('we should log this event for sure')
        return False, None
    path = "token"
    session_data = {path: parsing_results[0].data_model.get_value(path)}
    # TODO: implement feature vector creation and fancy logging of results...
    return True, session_data

get_handle_grammar = Sequence({
    'endpoint': Uint8(1),
    "token": Blob(session_state.get('token')),
    "file_path": String('/mnt/a/b/c/file')
})

get_handle_response_grammar = Sequence({
    "handle": Blob(num_bits=256),
})

def get_handle_check(parsing_results, fuzziness):
    if len(parsing_results) != 1 or len(parsing_results[0].stream) != 0:
        if fuzziness == Fuzziness.correct:
            print('we should log this event for sure')
        return False, None
    path = "handle"
    session_data = {path: parsing_results[0].data_model.get_value(path)}
    # TODO: implement feature vector creation and fancy logging of results...
    return True, session_data

get_data_grammar = Sequence({
    'endpoint': Uint8(2),
    'handle': Blob(session_state('handle')), # hopefully this gets mutated to point somewhere that doesn't make sense or at /etc/shadow :)
})

get_data_response_grammar = Sequence({
    'length': Byte(),
    'data': DynamicBlob(get_num_bits=lambda this: this.parent.children['length']),
})

def get_data_check(parsing_results, fuzziness):
    return True, base_session_data

sign_out_grammar = Sequence({
    'endpoint': Uint8(3),
    "email": String(session_state.get('user_email'))
})

sign_out_response_grammar = Sequence({
    "status": Byte(), # TODO: make a sub-class that gives meaning to values
})

def sign_out_check(parsing_results, fuzziness):
    return True, base_session_data

send_grammars = [
    sign_in_grammar,
    get_handle_grammar,
    get_data_grammar,
    sign_out_grammar,
]
response_grammars = [
    sign_in_response_grammar,
    get_handle_response_grammar,
    get_data_response_grammar,
    sign_out_response_grammar,
]
response_check_functions = [
    sign_in_check,
    get_handle_check,
    get_data_check,
    sign_out_check,
]

from bitarray.util import ba2int
from secrets import randbits
class SUT:
    def __init__(self):
        self.memory = { 'auth': base_session_data.copy(), 'tokens': [], 'handles': [], }
    def interact_function(self, input_data):
        try:
            endpoint = ba2int(input_data[:8])
            input_data = input_data[8:]
            if endpoint == 0: # sign in
                user_email = ''
                while True:
                    char_data = input_data[:8]
                    if char_data != bitarray('0' * 8):
                        char = char_data.tobytes().decode('ascii')
                        user_email += char
                    else:
                        break
                password = ''
                while True:
                    char_data = input_data[:8]
                    if char_data != bitarray('0' * 8):
                        char = char_data.tobytes().decode('ascii')
                        password += char
                    else:
                        break
                if user_email not in self.memory['auth'] or self.memory['auth'][user_email] != password:
                    return bitarray('')
                token = randbits(256)
                self.memory['tokens'].append(token)
                return bitarray(format(token, '0256b'))
            elif endpoint == 1: # get handle
                token = ba2int(input_data[:256])
                input_data = input_data[256:]
                if token not in self.memory['tokens']:
                    return bitarray('')
                file_path = ''
                while True:
                    char_data = input_data[:8]
                    if char_data != bitarray('0' * 8):
                        char = char_data.tobytes().decode('ascii')
                        file_path += char
                    else:
                        break
                handle = randbits(256)
                self.memory['handles'].append((handle, file_path))
                return bitarray(format(handle, '0256b'))
            elif endpoint == 2: # get data
                handle = ba2int(input_data[:256])
                input_data = input_data[256:]
                if handle not in [x for x, _ in self.memory['tokens']]:
                    return bitarray('')
                return bitarray(''.join([format(ord(x), '08b') for x in 'This is the data!']))
            elif endpoint == 3: # sign out
                return bitarray('0' * 8)
            else:
                return bitarray('') # error
        except:
            return bitarray('') # error
sut = SUT()

fuzzer = Fuzzer(session_objects, send_grammars, response_grammars, response_check_functions, sut.interact_function)
