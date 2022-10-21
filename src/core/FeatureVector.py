import math

# A feature vector
class FeatureVector:
    def __init__(self, d={}):
        self.d = d
    def merge(self, others):
        for v in others:
            for key in v.d:
                self.d[key] = self.d.get(key, 0) + v.d[key]
    def depress(self, factor=math.e):
        for key in self.d:
            self.d[key] /= factor
    def merge_children(self, children, attenuation=math.e):
        self.merge(children)
        self.depress(attenuation)
    def to_list(self):
        keys = list(self.d.keys())
        keys.sort()
        return [self.d[k] for k in keys]

