import pygame
import json
from .engine import GRID_SIZE
from .engine import Entity
from logging import Logger
log = Logger(__name__)

class TileSet:
    def __init__(self, path):
        self._image = None
        self._tiles = []
        self._named = {}

        with open(path) as fh:
            conf = json.load(fh)

        self._image = pygame.image.load(conf['image']).convert()
        sz = conf.get('size', (GRID_SIZE,GRID_SIZE))
        if type(sz) == int:
            self.sz_x = sz
            self.sz_y = sz
        else:
            self.sz_x, self.sz_y = sz

        key = conf.get("key")
        if key:
            self._image.set_colorkey(key)

        self._load_grid()

        for name, ids in conf.get('names', {}).items():
            self._named[name] = [self._tiles[i] for i in ids]

    def _load_grid(self):
        # for now assume its a grid
        width, height = self._image.get_size()
        for y in range(int(height / self.sz_y)):
            for x in range(int(width / self.sz_x)):
                self._tiles.append(self._image.subsurface(
                    pygame.Rect(
                        x*self.sz_x, y*self.sz_y,
                        self.sz_x, self.sz_y)))

    def __getitem__(self, index):
        if type(index) == int:
            return self._tiles[index]
        else:

            path = index.split('/')
            if len(path) == 2:
                return self._named[path[0]][int(path[1])]
            else:
                return self._named[index]


class TileMap:
    def __init__(self, map_file):
        self.tile_set = []
        self.grid = None
        self.image = None
        self.x = None
        self.y = None
        self.bg_color = (0,0,0)
        self.frame = 0
        self.entities = []
        self._load_map(map_file)

    @property
    def width(self):
        return len(self.grid)
    
    @property
    def height(self):
        return len(self.grid[0])

    def _load_map(self, path):
        with open(path) as fh:
            map_data = json.load(fh)
        self.x, self.y = map_data.get('offset', (0, 0))
        self.bg_color = map_data.get('bg_color', (0,0,0))
        self.grid = map_data['grid']
        self.tile_set = TileSet(map_data['tile_set'])
        self._load_entities(map_data.get('entities', []))

    def _load_entities(self, entity_list):
        for spec in entity_list:
            with open(spec['id']) as fh:
                templ = json.load(fh)
            e = Entity(pos=spec.get('pos', [0,0]), tile_set=TileSet(templ['tile_set']))
            self.entities.append(e)

    def advance(self, rate=10):
        self.frame += 1/rate
        self.render()

    def render(self):
        surf = pygame.Surface((len(self.grid) * GRID_SIZE, len(self.grid[0])* GRID_SIZE))
        
        for j, row in enumerate(self.grid):
            for i, tile_id in enumerate(row):
                tile = self.tile_set[tile_id]
                if type(tile) == list:
                    tile = tile[int(self.frame) % len(tile)]
                surf.blit(tile, (i*GRID_SIZE, j*GRID_SIZE))

        self.image = surf
        return self


    def get_image(self):
        return self.image

