# light-weight context object
class Ctx:
    def __init__(self, p=None, c=None):
        self.parent = p
        self.children = c
        # self.child = c
