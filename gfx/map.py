import pygame
import json
from .engine import GRID_SIZE

class TileMap:
    def __init__(self, map_file):
        self.tile_images = None
        self.tile_set = []
        self.grid = None
        self.image = None
        self.x = None
        self.y = None
        self.bg_color = (0,0,0)
        self._load_map(map_file)

    def _load_tile_set(self, path):
        self.tile_images = pygame.image.load(path).convert()
        # for now assume its a grid of 32x32 tiles
        width, height = self.tile_images.get_size()
        for x in range(int(width / GRID_SIZE)):
            for y in range(int(height / GRID_SIZE)):
                self.tile_set.append(self.tile_images.subsurface(
                    pygame.Rect(
                        x*GRID_SIZE, y*GRID_SIZE,
                        GRID_SIZE, GRID_SIZE)))


    def _load_map(self, path):
        with open(path) as fh:
            map_data = json.load(fh)
        self.x, self.y = map_data.get('offset', (0, 0))
        self.bg_color = map_data.get('bg_color', (0,0,0))
        self.grid = map_data['grid']
        self._load_tile_set(map_data['tile_set'])
        

    def render(self):
        surf = pygame.Surface((len(self.grid) * GRID_SIZE, len(self.grid[0])* GRID_SIZE))
        
        for i, row in enumerate(self.grid):
            for j, tile_id in enumerate(row):
                tile = self.tile_set[tile_id]
                surf.blit(tile, (i*GRID_SIZE, j*GRID_SIZE))
            # isometric
            # for j, tile_id in reversed(list(enumerate(row))):
            #     tile = self.tile_set[tile_id]
            #     surf.blit(tile, (
            #         (j * GRID_SIZE/2) + (i * GRID_SIZE/2),
            #         (i * GRID_SIZE/2) - (j * GRID_SIZE/2)
            #     ))

        self.image = surf


    def get_image(self):
        return self.image
