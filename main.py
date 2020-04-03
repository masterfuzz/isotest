from gfx.engine import Engine, Entity
from gfx.map import TileMap, TileSet
from pygame.locals import KEYDOWN
from logging import Logger
log = Logger(__name__)


e = Engine()
m = TileMap("data/maps/zeroes.json")
m.render()
e.map = m

@e.on(KEYDOWN)
def move_view(event):
    x, y = 0, 0
    if event.key == ord('w'):
        y -= 1
    if event.key == ord('s'):
        y += 1
    if event.key == ord('a'):
        x -= 1
    if event.key == ord('d'):
        x += 1
    e.view.shift(x*32, y*32)
    pass

e.run()
e.quit()
