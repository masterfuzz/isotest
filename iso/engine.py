from collections import defaultdict
from typing import Callable, Any
import pygame
import random
from math import floor, ceil
from logging import Logger
from iso.control.scene import Scenario
log = Logger(__name__)

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    FULLSCREEN
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 32

class Engine:
    def __init__(self, config):
        pygame.init()
        flags = int(config.get('graphics/full_screen', 0))
        self.screen = pygame.display.set_mode(config.get('graphics/display_mode', [SCREEN_WIDTH, SCREEN_HEIGHT]), flags=flags)
        self.frame_limit = config.get('graphics/frame_limit', 30)

        self.view = Viewport(self.screen)
        self.running = False
        self.clock = pygame.time.Clock()
        self.event_hooks = defaultdict(list)
        self.step_hooks = {}
        self.layers = defaultdict(list)
        self.map = None
        self.gui = None
        self.user_event = pygame.USEREVENT

    @property
    def screen_width(self):
        return self.screen.get_width()

    @property
    def screen_height(self):
        return self.screen.get_height()

    def get_fps(self):
        return self.clock.get_fps()

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
            sprite_count, tile_count = self.render()
            self.clock.tick(self.frame_limit)
            fps = self.clock.get_fps()
            
            pygame.display.set_caption(f"{sprite_count} sprites, {tile_count} tiles @{fps:.2f} FPS")

    def set_scene(self, scene: Scenario) -> None:
        """ Switch the scenario. Won't change gui if gui is None """
        self.map = scene.map
        # TODO clear entities?
        self.layers.update(scene.entities)
        if scene.gui:
            self.gui = scene.gui

    def handle_steps(self):
        for name, hook in self.step_hooks.items():
            # print(f"run step_hook: {name}")
            hook()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            for hook in self.event_hooks[event.type]:
                hook(event)

    def register_hook(self, etype: int, hook) -> None:
        self.event_hooks[etype].append(hook)

    def on(self, etype: int) -> Callable[[Callable], Callable]:
        def wrap(hook: Callable[[pygame.event.Event], Any]):
            self.register_hook(etype, hook)
            return hook
        return wrap

    def on_step(self, hook):
        self.register_step(str(hook), hook)
        return hook
    
    def register_step(self, name, hook):
        self.step_hooks[name] = hook

    def render(self):
        sprite_count = 0
        self.screen.fill(self.map.bg_color)
        tile_count = self.view.draw_map(self.map)

        for layer in self.layers.values():
            for sprite in layer:
                sprite_count += int(self.view.draw(sprite))

        # for widget in self.gui.widgets:
        #     self.screen.blit(widget.renderer(), (widget.x, widget.y))
        self.gui.render(self.screen)

        pygame.display.flip()
        return sprite_count, tile_count

    def set_timer(self, period: int, etype: int=None):
        def decorate(func):
            nonlocal etype 
            if etype is None:
                self.user_event += 1
                etype = self.user_event
            pygame.time.set_timer(etype, period)
            self.on(etype)(func)
            return func
        return decorate

    def stop(self):
        # trigger pygame quit event??
        self.running = False

    def quit(self): 
        pygame.quit()

    def sprite_at(self, pos, layers=None, ignore=(99,)):
        x, y = pos
        layers = layers if layers else self.layers.keys()
        for layer in layers:
            if layer in ignore: continue
            for sprite in self.layers[layer]:
                if sprite.x == x and sprite.y == y:
                    return sprite


class Viewport:
    def __init__(self, surface, pos=None):
        self.surf = surface
        self.pos = pos if pos else [0,0]
        self.scale = 2

    def draw(self, sprite):
        if self.in_view(sprite.get_rect()):
            self.surf.blit(self.transform_surf(sprite.get_image()), 
                self.transform_pos(sprite.x, sprite.y))
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
        if self.scale == 2:
            return pygame.transform.scale2x(surf)
        else:
            rect = surf.get_rect()
            return pygame.transform.scale(surf, (int(rect.width*self.scale), int(rect.height*self.scale)))


    def transform_pos(self, x, y):
        x = self.scale*GRID_SIZE * x - self.pos[0]
        y = self.scale*GRID_SIZE * y - self.pos[1]
        return x, y

    def shift(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def center_on(self, sprite):
        self.pos = 0, 0
        nx, ny = self.screen_to_grid(self.surf.get_width() / 2, self.surf.get_height() / 2)
        self.pos = self.transform_pos(sprite.x-nx+0.5, sprite.y-ny+0.5)

    def screen_to_grid(self, screen_x, screen_y):
        grid_x = (screen_x + self.pos[0]) / (self.scale*GRID_SIZE)
        grid_y = (screen_y + self.pos[1]) / (self.scale*GRID_SIZE)
        return grid_x, grid_y

    def view_grid_range(self):
        tl_x, tl_y = self.screen_to_grid(0,0)
        tr_x, tr_y = self.screen_to_grid(self.surf.get_width(), 0)
        bl_x, bl_y = self.screen_to_grid(0, self.surf.get_height())
        br_x, br_y = self.screen_to_grid(self.surf.get_width(), self.surf.get_height())
        return ((floor(min(tl_x, tr_x, bl_x, br_x)), ceil(max(tl_x, tr_x, bl_x, br_x))), 
                (floor(min(tl_y, tr_y, bl_y, br_y)), ceil(max(tl_y, tr_y, bl_y, br_y))))
