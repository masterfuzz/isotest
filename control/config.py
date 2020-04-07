import json

class Config:
    def __init__(self, path):
        with open(path) as fh:
            cfg = json.load(fh)
        self._json = cfg 

    def get(self, key, default=None):
        def _get(data, path):
            if path:
                nxt = path[0]
                if nxt in data:
                    return _get(data[nxt], path[1:])
                else: 
                    return default
            else:
                return data
        return _get(self._json, key.split('/'))
