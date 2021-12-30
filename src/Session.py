class Session:
    # This class is essentially a proxy for a dict.
    # Use this to store session data.
    def __init__(self):
        self._data = {}
    def set(self, name, value):
        self._data[name] = value
    def enter(self, name, value):
        assert name not in self._data
        self.set(name, value)
    def overwrite(self, name, value):
        assert name in self._data
        self.set(name, value)
    def get(self, name):
        return self._data[name] # be careful not to mutate data contain in this return value!
