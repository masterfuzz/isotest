from gfx.engine import Engine, Entity
from gfx.map import TileMap, TileSet
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN
from logging import Logger
log = Logger(__name__)


eng = Engine()
eng.map = TileMap("data/maps/zeroes.json").render()

class Cursor(Entity):
    def __init__(self, cursorfile):
        super().__init__(TileSet(cursorfile))

cursor = Cursor("data/tiles/cursor.json")
cursor.x = int(eng.map.width / 2)
cursor.y = int(eng.map.height / 2)
eng.view.center_on(cursor)

eng.layers[99].append(cursor)

@eng.on(KEYDOWN)
def move_view(event):
    if event.key == ord('w'):
        cursor.y -= 1
    if event.key == ord('s'):
        cursor.y += 1
    if event.key == ord('a'):
        cursor.x -= 1
    if event.key == ord('d'):
        cursor.x += 1
    # eng.view.shift(x*32, y*32)
    eng.view.center_on(cursor)

eng.run()
eng.quit()
