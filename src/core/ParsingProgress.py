class ParsingProgress:
    # this class is a named tuple which stores the progress of a parse
    def __init__(self, data_model, stream):
        self.data_model = data_model
        self.stream = stream
    def get_tuple(self):
        return self.data_model, self.stream
