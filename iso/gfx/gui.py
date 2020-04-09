import pygame

class Widget:
    def __init__(self, pos=(0,0), size=(64,64)):
        self.x, self.y = pos
        self.surf = pygame.Surface(size)
        self.surf.set_colorkey((255,0,255))
        
    def renderer(self):
        self.surf.fill((255,0,255))
        return self.surf

class TextBox(Widget):
    def __init__(self, text, pos=(0,0), size=(64,64), fg_color=(0,0,0), 
                    wrap=False, resize=False,
                    bg_color=(255,255,255), font=None):

        super().__init__(pos, size)
        self._text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.resize = resize
        self.font = font if font else pygame.font.SysFont(None, 24)

    def renderer(self):
        font_surf = self.font.render(self.text, True, self.fg_color, self.bg_color)
        if self.resize:
            surf = font_surf
        else:
            surf = super().renderer()
            surf.fill(self.bg_color)
            surf.blit(font_surf, (0,0))
        return surf

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

class Container(Widget):
    def __init__(self, *children, pos=(0,0), size=(64,64)):
        super().__init__(pos=pos, size=size)
        self.children = children

class Flow(Container):
    def renderer(self):
        # TODO "flow" and margins...
        surf = super().renderer()
        x, y = 0, 0
        for child in self.children:
            child_surf = child.renderer()
            surf.blit(child_surf, (x, y))
            x += child_surf.get_width()
        return surf

class CenterHorizontal(Container):
    def renderer(self):
        surf = super().renderer()
        child_surfs = [child.renderer() for child in self.children]
        total_width = sum([c.get_width() for c in child_surfs])
        x = int(surf.get_width() / 2 - total_width / 2)
        y = 0
        for child in child_surfs:
            surf.blit(child, (x, y))
            x += child.get_width()
        return surf

class Gui:
    def __init__(self, *widgets):
        self.widgets = widgets

    @classmethod
    def from_file(cls, path):
        raise NotImplementedError()
