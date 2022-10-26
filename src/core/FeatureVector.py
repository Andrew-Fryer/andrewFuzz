import math

# A feature vector
class FeatureVector:
    def __init__(self, features):
        self.features = features
        self.d = {}
        for key in features:
            self.d[key] = 0 #self.d.get(key, 0)
    def tally(self, feature, depth, attenuation=math.e):
        self.d[feature] += attenuation ** -depth
    # def merge(self, others):
    #     for v in others:
    #         for key in v.d:
    #             self.d[key] = self.d.get(key, 0) + v.d[key]
    # def depress(self, factor=math.e):
    #     for key in self.d:
    #         self.d[key] /= factor
    # def merge_children(self, children, attenuation=math.e):
    #     self.merge(children)
    #     self.depress(attenuation)
    def to_list(self):
        return [self.d[k] for k in self.features]
    def dist(self, other):
        features = self.features
        assert(other.features == features)
        return sum([(self.d[k] - other.d[k]) ** 2 for k in features]) ** 0.5
