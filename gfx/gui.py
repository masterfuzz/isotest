from pygame import font, Surface
# from .engine import SCREEN_HEIGHT, SCREEN_WIDTH

class Widget:
    def __init__(self, width=32, height=32):
        self.x = 20
        self.y = 20
        self.text = "Uninitialized Widget"
        self.color = (0,0,0)
        self.surf = Surface((width, height))

        self.font = font.SysFont(None, 24)
        
    def renderer(self):
        self.surf.fill((255,255,255))
        font_surf = self.font.render(self.text, True, self.color)
        self.surf.blit(font_surf, (0,0))
        return self.surf


class Gui:
    def __init__(self, gui_file):
        self.widgets = []
        pass
