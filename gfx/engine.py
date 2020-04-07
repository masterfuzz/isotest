from collections import defaultdict
import pygame
import random
from math import floor, ceil
from logging import Logger
from .gui import Widget
log = Logger(__name__)

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500
GRID_SIZE = 32

class Engine:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode([width, height])
        self.view = Viewport(self.screen)
        self.running = False
        self.clock = pygame.time.Clock()
        self.event_hooks = defaultdict(list)
        self.step_hooks = {}
        self.layers = defaultdict(list)
        self.map = None
        self.gui = None

    def run(self):
        if self.running:
            print('already running??')
            return
        else:
            self.running = True

        while self.running:
            self.handle_events()
            self.handle_steps()
            self.map.advance()
            entity_count, tile_count = self.render()
            self.clock.tick(200)
            fps = self.clock.get_fps()
            
            pygame.display.set_caption(f"drew {entity_count} entities, {tile_count} tiles @{fps:.2f} FPS")

    def handle_steps(self):
        for name, hook in self.step_hooks.items():
            # print(f"run step_hook: {name}")
            hook()

    def handle_events(self):
        for event in pygame.event.get():
            # print(f"event: {event}")
            for hook in self.event_hooks[event.type]:
                hook(event)
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == ord('q'):
                    self.running = False
            elif event.type == pygame.QUIT:
                self.running = False

    def register_hook(self, etype, hook):
        self.event_hooks[etype].append(hook)

    def on(self, etype):
        def wrap(hook):
            self.register_hook(etype, hook)
            return hook
        return wrap

    def on_step(self, hook):
        self.register_step(str(hook), hook)
        return hook
    
    def register_step(self, name, hook):
        self.step_hooks[name] = hook

    def render(self):
        entity_count = 0
        self.screen.fill(self.map.bg_color)
        tile_count = self.view.draw_map(self.map)

        for entity in self.map.entities:
            entity_count += int(self.view.draw(entity))

        for layer in self.layers.values():
            for entity in layer:
                entity_count += int(self.view.draw(entity))

        for widget in self.gui.widgets:
            self.screen.blit(widget.renderer(), (widget.x, widget.y))

        pygame.display.flip()
        return entity_count, tile_count

    def set_timer(self, etype, period):
        pygame.time.set_timer(etype, period)

    def quit(self): 
        pygame.quit()


class Viewport:
    def __init__(self, surface, pos=None):
        self.surf = surface
        self.pos = pos if pos else [0,0]

    def draw(self, entity):
        if self.in_view(entity.get_rect()):
            self.surf.blit(self.transform_surf(entity.get_image()), 
                self.transform_pos(entity.x, entity.y))
            return True
        else:
            return False

    def in_view(self, rect):
        # return self.transform_rect(rect).colliderect(self.surf.get_rect())
        x,y = self.transform_pos(rect.x, rect.y)
        return self.surf.get_rect().collidepoint(x,y)


    def draw_map(self, map):
        tile_count = 0
        # get grid points of viewport
        range_x, range_y = self.view_grid_range()
        for i in range(*range_x):
            for j in range(*range_y):
                tile = map[i, j]
                if tile is None: continue
                self.surf.blit(self.transform_surf(tile), 
                    self.transform_pos(i, j))
                tile_count += 1
        return tile_count

    def transform_surf(self, surf):
        return pygame.transform.scale2x(surf)

    def transform_pos(self, x, y):
        x = 2*GRID_SIZE * x - self.pos[0]
        y = 2*GRID_SIZE * y - self.pos[1]
        return x, y

    def transform_rect(self, rect):
        x, y = self.transform_pos(rect.x, rect.y)
        img_w, img_h = rect.bottomright
        bx, by = self.transform_pos(img_w / 32 + rect.x, img_h / 32 + rect.y)
        w = bx - x
        h = by - y
        return pygame.Rect(x,y,w,h)

    def shift(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def center_on(self, entity):
        self.pos = 0, 0
        nx, ny = self.screen_to_grid(self.surf.get_width() / 2, self.surf.get_height() / 2)
        self.pos = self.transform_pos(entity.x-nx+0.5, entity.y-ny+0.5)

    def screen_to_grid(self, screen_x, screen_y):
        grid_x = (screen_x + self.pos[0]) / (2*GRID_SIZE)
        grid_y = (screen_y + self.pos[1]) / (2*GRID_SIZE)
        return grid_x, grid_y

    def view_grid_range(self):
        tl_x, tl_y = self.screen_to_grid(0,0)
        tr_x, tr_y = self.screen_to_grid(self.surf.get_width(), 0)
        bl_x, bl_y = self.screen_to_grid(0, self.surf.get_height())
        br_x, br_y = self.screen_to_grid(self.surf.get_width(), self.surf.get_height())
        return ((floor(min(tl_x, tr_x, bl_x, br_x)), ceil(max(tl_x, tr_x, bl_x, br_x))), 
                (floor(min(tl_y, tr_y, bl_y, br_y)), ceil(max(tl_y, tr_y, bl_y, br_y))))

class Entity:
    def __init__(self, tile_set, pos=None, pose=0):
        pos = pos if pos else [0,0]
        self.x, self.y = pos
        self.tile_set = tile_set
        self.pose = pose
        self.vflip = False
        self.hflip = False
        self.frame = 0
        self.animate = False

    def get_image(self):
        img = self.tile_set[self.pose]
        if type(img) == list:
            return pygame.transform.flip(img[int(self.frame) % len(img)], self.vflip, self.hflip)
        return pygame.transform.flip(img, self.vflip, self.hflip)

    def get_rect(self):
        rect = self.get_image().get_rect()
        return pygame.Rect(self.x, self.y, rect.width, rect.height)




