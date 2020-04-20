import json
from math import inf

class TerrainMap:
    def __init__(self, path):
        with open(path) as fh:
            self.data = json.load(fh)

    def get_dist_func(self, vehicle, tmap):
        def _d(a, b):
            terrain = tmap.get_terrain(b)
            mult = self.get_mult(vehicle, terrain)
            ax, ay = a
            bx, by = b
            return mult * (abs(ax-bx) + abs(ay-by))
        return _d

    def get_mult(self, vehicle, terrain):
        # default = self.data['default'].copy()
        # default.update(self.data[vehicle])
        mult = self.data[vehicle].get(terrain, self.data['default'][terrain])
        return mult if mult else inf
