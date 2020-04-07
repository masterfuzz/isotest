from pygame import font
# from .engine import SCREEN_HEIGHT, SCREEN_WIDTH

class Widget:
    def __init__(self):
        self.x = 20
        self.y = 20
        self.text = "I want to say something before this whole thing gets out of control."
        self.color = (0,0,0)

        self.font = font.SysFont(None, 24)
        
    def renderer(self):
        return self.font.render(self.text, True, self.color)


class Gui:
    def __init__(self, gui_file):
        self.widgets = []
        pass
