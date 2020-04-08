from iso.gfx.engine import Engine, Entity
from iso.gfx.map import TileMap, TileSet
from iso.gfx.gui import Gui, TextBox, CenterHorizontal
from iso.control.config import Config
from iso.control.keybind import Keybindings
from iso.control.keybind import KEYDOWN, KEYUP, MOUSEBUTTONDOWN
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
status_box = TextBox("Hello World", size=(80, 25))
entity_box = TextBox("No selection")
eng.gui = Gui(
    entity_box, 
    CenterHorizontal(
        status_box,
        pos=(0,eng.screen_height-64),
        size=(eng.screen_width, 64)
    )
)


@eng.set_timer(160)
def show_stats(e):
    status_box.text = f"FPS: {eng.get_fps()}"

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

@keybindings.hook("CURSOR", "SELECT")
def select_entity():
    ent = eng.entity_at((cursor.x, cursor.y))
    if ent:
        entity_box.text = "You selected something"
    else:
        entity_box.text = "Nothing here"

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
