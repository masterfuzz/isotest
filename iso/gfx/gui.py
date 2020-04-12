import lxml.objectify
import pygame

class Widget:
    """ Base class for Widgets """
    def __init__(self, x=0, y=0, width=0, height=0, colorkey=(255,0,255), **kwargs):
        """ Parameters should be considered "constraints"
            potentially modified by a parent widget """
        self.x, self.y = int(x), int(y)
        self.width, self.height = width, height
        self.colorkey = colorkey
        # self.surf = pygame.Surface((int(width), int(height)))
        # self.surf.set_colorkey((255,0,255))

    def get_size(self, parent_width, parent_height, **kwargs):
        def _get_size(sz, pz):
            if type(sz) == str:
                if sz.endswith("%"):
                    return int(pz * (int(sz[:-1]) / 100))
                else:
                    sz = int(sz)
            if sz == 0:
                return pz
            return min(sz, pz)
        return _get_size(self.width, parent_width), _get_size(self.height, parent_height)

    def _get_surf(self, size):
        surf = pygame.Surface(size)
        surf.fill(self.colorkey)
        surf.set_colorkey(self.colorkey)
        return surf
        
    def renderer(self, **kwargs):
        surf = self._get_surf(self.get_size(**kwargs))
        return surf


class TextBox(Widget):
    """ For displaying a line of text """
    def __init__(self, text, fg_color=(0,0,0), 
                    wrap=False, resize=False,
                    bg_color=(255,255,255), font=None, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.resize = resize
        self.font = font if font else pygame.font.SysFont(None, 24)

    def renderer(self, **kwargs):
        font_surf = self.font.render(self.text, True, self.fg_color, self.bg_color)
        if self.resize:
            self.width = font_surf.get_width()
            self.height = font_surf.get_height()
            surf = font_surf
            if self.colorkey:
                surf.set_colorkey(self.colorkey)
        else:
            surf = super().renderer(**kwargs)
            # surf = pygame.Surface((self.width, self.height))
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
    def __init__(self, *children, **kwargs):
        super().__init__(**kwargs)
        self.children = children

    def _render_children(self, **kwargs):
        for child in self.children:
            yield child.renderer(**kwargs), (child.x, child.y)

    def renderer(self, **kwargs):
        child_surfs = list(self._render_children(**kwargs))
        width = max(loc[0]+s.get_width() for s, loc in child_surfs)
        height = max(loc[1]+s.get_height() for s, loc in child_surfs)
        surf = self._get_surf((width, height))
        for child_surf, loc in child_surfs:
            surf.blit(child_surf, loc)

        return surf

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
    def _render_children(self, **kwargs):
        my_width, my_height = self.get_size(**kwargs)
        for child in self.children:
            child_surf = child.renderer(**kwargs)
            yield child_surf, (int(my_width / 2 - child_surf.get_width() / 2), child.y)

class CenterVertical(Container):
    def _render_children(self, **kwargs):
        my_width, my_height = self.get_size(**kwargs)
        for child in self.children:
            child_surf = child.renderer(**kwargs)
            yield child_surf, (child.x, int(my_height / 2 - child_surf.get_height() / 2))

class Column(Container):
    def _render_children(self, **kwargs):
        y = self.y
        for child in self.children:
            child_surf = child.renderer(**kwargs)
            yield child_surf, (child.x, y)
            y += child_surf.get_height()


class AlignBottom(Container):
    def _render_children(self, **kwargs):
        for child in self.children:
            child_surf = child.renderer(**kwargs)
            y = kwargs['parent_height'] - child_surf.get_height()
            yield child_surf, (child.x, y)

schema = {
    "textbox": TextBox,
    "center": CenterHorizontal,
    "vcenter": CenterVertical,
    "bottom": AlignBottom,
    "column": Column
}


class Gui:
    def __init__(self, *widgets):
        self.root = Container(*widgets)
        self.ids = {}

    @classmethod
    def from_file(cls, path):
        etree = lxml.objectify.parse(path)
        root = etree.getroot()
        if root.tag != "gui":
            raise ValueError("Root node should be 'gui'")
        gui = cls()
        gui.root.children = list(gui._get_elements(root.iterchildren(), gui.root))
        return gui
    
    def _get_elements(self, elems, parent):
        for elem in elems:
            if elem.text:
                elem.attrib['text'] = elem.text
            widget = schema[elem.tag](**elem.attrib)

            if "id" in elem.attrib:
                self.ids[elem.attrib["id"]] = widget

            if isinstance(widget, Container):
                widget.children = list(self._get_elements(elem.iterchildren(), widget))
            yield widget

    def render(self, surf):
        surf.blit(self.root.renderer(parent_width=surf.get_width(), parent_height=surf.get_height()), (0,0))

    def get(self, name):
        return self.ids[name]

