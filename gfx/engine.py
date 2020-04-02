from collections import defaultdict
import pygame
import random
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

        for layer in self.layers.values():
            for entity in layer:
                self.view.draw(entity)

        pygame.display.flip()

    def set_timer(self, etype, period):
        pygame.time.set_timer(etype, period)

    def quit(self): 
        pygame.quit()



class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 10))
        self.image.fill((0, 0, 255))


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

class Entity:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self._sprite = Ball()

    def get_image(self):
        return self._sprite.image



