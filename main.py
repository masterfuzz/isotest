from gfx.engine import Engine, Entity
from gfx.map import TileMap, TileSet
from gfx.gui import Gui, Widget
from control.config import Config
from control.keybind import Keybindings
from pygame.locals import KEYDOWN, KEYUP, MOUSEBUTTONDOWN
# import pygame
from logging import Logger
log = Logger(__name__)

cfg = Config("data/control/default_config.json")
eng = Engine(cfg)
keybindings = Keybindings(cfg.get("keybindings"))
eng.on(KEYDOWN)(keybindings.keydown)
eng.on(KEYUP)(keybindings.keyup)
eng.set_timer(cfg.get("game/key_repeat_period", 250))(keybindings.keyrepeat)

eng.map = TileMap("data/maps/lorge.json")
eng.gui = Gui(None)

eng.gui.widgets.append(Widget())

class Cursor(Entity):
    def __init__(self, cursorfile):
        super().__init__(TileSet(cursorfile))
        self.on_shift = lambda s:None
        self.selected_ent = -1
    
    def shift(self, x=0, y=0):
        self.x += x
        self.y += y
        self.on_shift(self)
    
    def goto(self, x, y):
        self.x, self.y = x, y
        self.on_shift(self)

cursor = Cursor("data/tiles/cursor.json")
cursor.on_shift = lambda self: eng.view.center_on(self)
cursor.on_shift(cursor)

eng.layers[99].append(cursor)

@keybindings.hook("CURSOR")
def move_cursor(action):
    if action == "UP":
        cursor.shift(y=-1)
    elif action == "DOWN":
        cursor.shift(y=1)
    elif action == "LEFT":
        cursor.shift(-1)
    elif action == "RIGHT":
        cursor.shift(1)
    elif action == "NEXT":
        cursor.selected_ent = (cursor.selected_ent + 1) % len(eng.map.entities)
        ent = eng.map.entities[cursor.selected_ent]
        cursor.goto(ent.x, ent.y)

@keybindings.hook("VIEW")
def zoom_view(action):
    if action == "ZOOM_OUT":
        eng.view.scale -= 0.1
    elif action == "ZOOM_IN":
        eng.view.scale += 0.1
    eng.view.center_on(cursor)

keybindings.hook("GAME", "QUIT")(eng.stop)

eng.run()
eng.quit()
