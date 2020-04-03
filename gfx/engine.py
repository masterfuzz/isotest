from collections import defaultdict
import pygame
import random
from logging import Logger
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
            self.render()
            self.clock.tick(30)

    def handle_steps(self):
        for name, hook in self.step_hooks.items():
            print(f"run step_hook: {name}")
            hook()

    def handle_events(self):
        for event in pygame.event.get():
            print(f"event: {event}")
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
        self.screen.fill(self.map.bg_color)
        self.view.draw_map(self.map)
        for entity in self.map.entities:
            self.view.draw(entity)

        for layer in self.layers.values():
            for entity in layer:
                self.view.draw(entity)

        pygame.display.flip()

    def set_timer(self, etype, period):
        pygame.time.set_timer(etype, period)

    def quit(self): 
        pygame.quit()


class Viewport:
    def __init__(self, surface, pos=None):
        self.surf = surface
        self.pos = pos if pos else [0,0]

    def draw(self, entity):
        self.surf.blit(self.transform_surf(entity.get_image()), 
            self.transform_pos(entity.x, entity.y))

    def draw_map(self, map):
        self.draw(map)

    def transform_surf(self, surf):
        return pygame.transform.scale2x(surf)

    def transform_pos(self, x, y):
        # var xScreen = xWorld * 1   + yWorld * -1  + 160;
        # var yScreen = xWorld * 0.5 + yWorld * 0.5 + 0;  
        x = 2*GRID_SIZE * x - self.pos[0]
        y = 2*GRID_SIZE * y - self.pos[1]
        return x, y

    def shift(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def screen_to_grid(self, screen_x, screen_y):
        grid_x = (screen_x + self.pos[0]) / (2*GRID_SIZE)
        grid_y = (screen_y + self.pos[0]) / (2*GRID_SIZE)
        return grid_x, grid_y

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




