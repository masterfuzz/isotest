from iso.control.config import Config
from iso.gfx.sprite import Sprite
from iso.gfx.map import TileSet, TileMap
import json
from collections import defaultdict

class Scenario(Config):
    def __init__(self, path):
        super().__init__(path)
        self.map = TileMap(self.get("map"))
        self.entities = defaultdict(list)
        self.gui = self.get("gui")

        self._load_entities(self.get("entities", []))

    def _load_entities(self, entity_list):
        for spec in entity_list:
            with open(spec['id']) as fh:
                templ = json.load(fh)
            # for now entity = sprite
            e = Sprite(pos=spec['pos'], tile_set=TileSet(templ['tile_set']))
            layer = spec.get('layer', 1)
            self.entities[layer].append(e)
