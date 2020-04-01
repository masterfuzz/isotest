from engine import Engine, Entity
from pygame.locals import KEYDOWN



e = Engine()

for x in range(5):
    for y in range(5):
        e.layers[0].append(Entity((x, y)))

@e.on(KEYDOWN)
def move_view(event):
    x, y = 0, 0
    if event.key == ord('w'):
        y += 1
    if event.key == ord('s'):
        y -= 1
    if event.key == ord('a'):
        x += 1
    if event.key == ord('d'):
        x -= 1
    e.view.shift(x*10, y*10)
    pass

e.run()
e.quit()
