import math

# A feature vector
class FeatureVector:
    def __init__(self, d={}):
        self._d = d
    def merge(self, ds):
        for d in ds:
            for key in d:
                self._d[key] = self._d.get(key, 0) + d[key]
    def depress(self, factor=math.e):
        for key in self._d:
            self._d[key] /= factor
    def to_list(self):
        keys = self._d.keys()
        keys.sort()
        return [self._d[k] for k in keys]
