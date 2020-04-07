from gfx.engine import Engine, Entity
from gfx.map import TileMap, TileSet
from gfx.gui import Gui, Widget
from control.config import Config
from control.keybind import Keybindings
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN
from logging import Logger
log = Logger(__name__)

cfg = Config("data/control/default_config.json")
eng = Engine(cfg)
keybindings = Keybindings(cfg.get("keybindings"))

eng.map = TileMap("data/maps/lorge.json")
eng.gui = Gui(None)

eng.gui.widgets.append(Widget())

class Cursor(Entity):
    def __init__(self, cursorfile):
        super().__init__(TileSet(cursorfile))

cursor = Cursor("data/tiles/cursor.json")

eng.layers[99].append(cursor)

selected_ent = 0
def goto_ent(ent_id):
    ent = eng.map.entities[ent_id]
    cursor.x = ent.x
    cursor.y = ent.y
goto_ent(0)
eng.view.center_on(cursor)

@eng.on(KEYDOWN)
def move_view(event):
    global selected_ent
    section, action = keybindings.filter()(event)
    if section == "CURSOR":
        if action == "UP":
            cursor.y -= 1
        if action == "DOWN":
            cursor.y += 1
        if action == "LEFT":
            cursor.x -= 1
        if action == "RIGHT":
            cursor.x += 1
        elif action == "NEXT":
            selected_ent = (selected_ent + 1) % len(eng.map.entities)
            goto_ent(selected_ent)
        eng.view.center_on(cursor)
    elif section == "VIEW":
        if action == "ZOOM_OUT":
            eng.view.scale -= 0.1
        elif action == "ZOOM_IN":
            eng.view.scale += 0.1
        eng.view.center_on(cursor)

eng.run()
eng.quit()
