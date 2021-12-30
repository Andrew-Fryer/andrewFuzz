class Fuzzer:
    def __init__(self, session_objects, default_session_values, send_grammars, response_grammars, session_set_up_functions, interact_function, fuzzing_policy=None):
        # I'm not sure what the fuzzing policy shoud be and specify exactly...
        self.n = len(session_objects)
        assert(len(default_session_values) == self.n)
        assert(len(send_grammars) == self.n)
        assert(len(response_grammars) == self.n)
        assert(len(session_set_up_functions) == self.n)

        self.session_objects = session_objects
        self.default_session_values = default_session_values
        self.send_grammars = send_grammars
        self.response_grammars = response_grammars
        self.session_set_up_functions = session_set_up_functions
        self.interact_function = interact_function
        self.fuzzing_policy = fuzzing_policy
    def _do_fuzzing(self, i):
        # this method is essentially a depth-first-search
        if i >= self.n:
            return
        for fuzzed_data_model in self.send_grammars[i].fuzz():
            fuzzed_data = fuzzed_data_model.serialize()
            expected_response_type = fuzzed_data_model.fuzziness
            response_data = self.interact_function(fuzzed_data)
            parsing_results = self.response_grammars[i].parse(response_data)
            # parsing_results = [x for x in parsing_results if len(x.stream) == 0] # I think this should actually be inforced by the grammars...
            response_seems_coherent = len(parsing_results) == 1 # TODO: call a lambda to check
            if response_seems_coherent:
                response, _ = parsing_results[0].get_tuple()
                next_session = self.session_set_up_functions[i](response)
                self.session_objects[i].reset(next_session)
            else:
                # TODO: think of the best way to alert the tester of unexpected results
                self.session_objects[i].reset(self.default_session_values[i])
            self._do_fuzzing(i + 1)
    def do_fuzzing(self):
        self.session_objects[0].reset(self.default_session_values[0])
        self._do_fuzzing(0)
