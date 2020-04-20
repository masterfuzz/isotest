from iso.engine import Engine
from iso.gfx.map import TileMap, TileSet
# from iso.gfx.gui import Gui, TextBox, CenterHorizontal
from iso.gfx.gui import Gui
from iso.gfx.sprite import Sprite
from iso.control.scene import Scenario
from iso.control.config import Config
from iso.control.keybind import Keybindings
from iso.control.keybind import KEYDOWN, KEYUP, MOUSEBUTTONDOWN
import iso.util.path
import demo.terrain
from logging import Logger
log = Logger(__name__)

cfg = Config("data/control/default_config.json")
eng = Engine(cfg)
keybindings = Keybindings(cfg.get("keybindings"))
eng.on(KEYDOWN)(keybindings.keydown)
eng.on(KEYUP)(keybindings.keyup)
eng.set_timer(cfg.get("game/key_repeat_period", 250))(keybindings.keyrepeat)

eng.gui = Gui.from_file("data/gui/main.xml")
status_box = eng.gui.get("status_box")
entity_box = eng.gui.get("entity_box")

tmap = demo.terrain.TerrainMap("data/maps/terrain_types.json")

scene = Scenario(cfg.get("game/opening_scene"))
eng.set_scene(scene)


@eng.set_timer(160)
def show_stats(e):
    status_box.text = f"FPS: {eng.get_fps()}"

class Cursor(Sprite):
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
        cursor.selected_ent = (cursor.selected_ent + 1) % len(eng.layers[1])
        ent = eng.layers[1][cursor.selected_ent]
        cursor.goto(ent.x, ent.y)

@keybindings.hook("CURSOR", "SELECT")
def select_entity():
    ent = eng.sprite_at((cursor.x, cursor.y))
    if ent:
        entity_box.text = "You selected something"
        highlight_path((ent.x, ent.y), 5)
    else:
        entity_box.text = "Nothing here"

def highlight_path(start, budget):
    eng.map.clear_tint()
    for point in iso.util.path.find_reachable(start, budget, tmap.get_dist_func("default", eng.map)):
        eng.map.tint[point] = (0,0,200)

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
