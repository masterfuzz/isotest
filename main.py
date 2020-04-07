from gfx.engine import Engine, Entity
from gfx.map import TileMap, TileSet
from gfx.gui import Gui, Widget
from control.config import Config
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN
from logging import Logger
log = Logger(__name__)

cfg = Config("data/control/default_config.json")
eng = Engine(cfg)
# eng.map = TileMap("data/maps/zeroes.json").render()
eng.map = TileMap("data/maps/lorge.json")
eng.gui = Gui(None)

eng.gui.widgets.append(Widget())

class Cursor(Entity):
    def __init__(self, cursorfile):
        super().__init__(TileSet(cursorfile))

cursor = Cursor("data/tiles/cursor.json")
# cursor.x = int(eng.map.width / 2)
# cursor.y = int(eng.map.height / 2)

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
    if event.key == ord('w'):
        cursor.y -= 1
    if event.key == ord('s'):
        cursor.y += 1
    if event.key == ord('a'):
        cursor.x -= 1
    if event.key == ord('d'):
        cursor.x += 1
    if event.key == ord('-'):
        eng.view.scale -= 0.1
    if event.key == ord('='):
        eng.view.scale += 0.1
    if event.key == ord('n'):
        selected_ent = (selected_ent + 1) % len(eng.map.entities)
        goto_ent(selected_ent)
    # eng.view.shift(x*32, y*32)
    eng.view.center_on(cursor)
    # print(f"{cursor.x}, {cursor.y}")

eng.run()
eng.quit()
