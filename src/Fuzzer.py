class Fuzzer:
    def __init__(self, session_objects, send_grammars, response_grammars, response_check_functions, interact_function, fuzzing_policy=None):
        # I'm not sure what the fuzzing policy shoud be and specify exactly...
        self.n = len(session_objects)
        assert(len(send_grammars) == self.n)
        assert(len(response_grammars) == self.n)
        assert(len(response_check_functions) == self.n)

        self.session_objects = session_objects
        self.send_grammars = send_grammars
        self.response_grammars = response_grammars
        self.response_check_functions = response_check_functions
        self.interact_function = interact_function
        self.fuzzing_policy = fuzzing_policy
    def _do_fuzzing(self, i):
        # this method is essentially a depth-first-search
        if i >= self.n:
            return
        for fuzzed_data_model in self.send_grammars[i].fuzz():
            fuzzed_data = fuzzed_data_model.serialize()
            fuzziness = fuzzed_data_model.fuzziness
            response_data = self.interact_function(fuzzed_data) # nonono, the SUT has state, so we need to reset it and hold it's hand through each stage...
            parsing_results = self.response_grammars[i].parse(response_data)
            # parsing_results = [x for x in parsing_results if len(x.stream) == 0] # I think this should actually be inforced by the grammars...
            for should_continue, next_session in self.response_check_functions[i](parsing_results, fuzziness):
                if should_continue:
                    self.session_objects[i + 1].reset(next_session)
                    self._do_fuzzing(i + 1)
    def do_fuzzing(self):
        self._do_fuzzing(0)
