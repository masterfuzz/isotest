import lxml.objectify
import pygame
from typing import Tuple, Union, List, Generator

Point = Tuple[int, int]
Surface = Union[pygame.Surface, "MultiSurface"]
SurfacePair = Tuple[Surface, Point]

class MultiSurface:
    def __init__(self, *pairs: SurfacePair):
        self.pairs = list(pairs)

    def shift(self, by_x, by_y):
        """ shift all pairs in place """
        self.pairs = list(
            (surf, (x+by_x, y+by_y)) for surf, (x, y) in self.pairs
        )

    def __iter__(self):
        yield from self.pairs

    def append(self, surf: Surface, loc: Point =(0,0)) -> None:
        if isinstance(surf, (pygame.Surface, MultiSurface)):
            self.pairs.append((surf, loc))
        else:
            raise TypeError("Must be pygame Surface or MultiSurface")

    def get_width(self) -> int:
        offset = min(loc[0] for _, loc in self.pairs)
        return max(loc[0]+surf.get_width()-offset for surf, loc in self.pairs)

    def get_height(self) -> int:
        offset = min(loc[1] for _, loc in self.pairs)
        return max(loc[1]+surf.get_height()-offset for surf, loc in self.pairs)

    def blit_to(self, dest: Surface, offset: Point =(0,0)) -> None:
        off_x, off_y = offset
        for surf, (x, y) in self.pairs:
            if isinstance(surf, MultiSurface):
                surf.blit_to(dest, (x+off_x, y+off_y))
            else:
                dest.blit(surf, (x+off_x, y+off_y))

    def blit(self, src: Surface, pos: Point =(0,0)) -> None:
        self.pairs.append((src, pos))


class Widget:
    """ Base class for Widgets """
    def __init__(self, x=0, y=0, width=0, height=0, colorkey=(255,0,255), **kwargs):
        """ Parameters should be considered "constraints"
            potentially modified by a parent widget """
        self.x, self.y = int(x), int(y)
        self.width, self.height = width, height
        self.colorkey = colorkey

    @property
    def pos(self) -> Point:
        return self.x, self.y

    def get_size(self, parent_width: int, parent_height: int, **kwargs) -> Point:
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

    def _get_surf(self, size: Point):
        surf = pygame.Surface(size)
        surf.fill(self.colorkey)
        surf.set_colorkey(self.colorkey)
        return surf
        
    def render(self, **kwargs):
        surf = self._get_surf(self.get_size(**kwargs))
        return MultiSurface((surf, (self.x, self.y)))


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

    def render(self, **kwargs):
        font_surf = self.font.render(self.text, True, self.fg_color, self.bg_color)
        if self.resize:
            self.width = font_surf.get_width()
            self.height = font_surf.get_height()
            surf = font_surf
            if self.colorkey:
                surf.set_colorkey(self.colorkey)
        else:
            surf = super().render(**kwargs)
            # surf = pygame.Surface((self.width, self.height))
            surf.blit(font_surf, (0,0))
        return MultiSurface((surf, self.pos))

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

    def render(self, **kwargs):
        return MultiSurface(*[(child.render(**kwargs), (child.x+self.x, child.y+self.y)) for child in self.children])

    # def renderer(self, **kwargs):
    #     child_surfs = list(self._render_children(**kwargs))
    #     width = max(loc[0]+s.get_width() for s, loc in child_surfs)
    #     height = max(loc[1]+s.get_height() for s, loc in child_surfs)
    #     surf = self._get_surf((width, height))
    #     for child_surf, loc in child_surfs:
    #         surf.blit(child_surf, loc)

    #     return surf

class CenterHorizontal(Container):
    def render(self, **kwargs):
        my_width, my_height = self.get_size(**kwargs)
        multi = super().render(**kwargs)
        return MultiSurface(*(
            (surf, (int(self.x + my_width / 2 - surf.get_width() /2), y))
            for surf, (x, y) in multi
        ))

class CenterVertical(Container):
    def render(self, **kwargs):
        multi = MultiSurface()
        my_width, my_height = self.get_size(**kwargs)
        for child in self.children:
            child_surf = child.render(**kwargs)
            multi.append(child_surf, (child.x, int(my_height / 2 - child_surf.get_height() / 2)))
        return multi

class Column(Container):
    def render(self, **kwargs):
        y = self.y
        multi = MultiSurface()
        for child in self.children:
            child_surf = child.render(**kwargs)
            multi.append(child_surf, (child.x, y))
            y += child_surf.get_height()
        return multi

class AlignBottom(Container):
    def render(self, **kwargs):
        parent_height = kwargs['parent_height']
        multi = MultiSurface()
        for child in self.children:
            child_surf = child.render(**kwargs)
            y = kwargs['parent_height'] - child_surf.get_height()
            multi.append(child_surf, (child.x, y))
        return multi

schema = {
    "textbox": TextBox,
    "center": CenterHorizontal,
    "vcenter": CenterVertical,
    "bottom": AlignBottom,
    "column": Column
}


class Gui:
    def __init__(self, *widgets: Widget):
        self.root = Container(*widgets)
        self.ids = {}

    @classmethod
    def from_file(cls, path: str):
        etree = lxml.objectify.parse(path)
        root = etree.getroot()
        if root.tag != "gui":
            raise ValueError("Root node should be 'gui'")
        gui = cls()
        gui.root.children = list(gui._get_elements(root.iterchildren(), gui.root))
        return gui
    
    def _get_elements(self, elems, parent: Widget) -> Generator[Widget, None, None]:
        for elem in elems:
            if elem.text:
                elem.attrib['text'] = elem.text
            widget = schema[elem.tag](**elem.attrib)

            if "id" in elem.attrib:
                self.ids[elem.attrib["id"]] = widget

            if isinstance(widget, Container):
                widget.children = list(self._get_elements(elem.iterchildren(), widget))
            yield widget

    def render(self, surf: pygame.Surface) -> None:
        self.root.render(parent_width=surf.get_width(), parent_height=surf.get_height()).blit_to(surf)

    def get(self, name: str) -> Widget:
        return self.ids[name]

