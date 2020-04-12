import pygame

class Sprite:
    def __init__(self, tile_set, pos=None, pose=0):
        pos = pos if pos else [0,0]
        self.x, self.y = pos
        self.tile_set = tile_set
        self.pose = pose
        self.vflip = False
        self.hflip = False
        self.frame = 0
        self.animate = False

    def get_image(self):
        img = self.tile_set[self.pose]
        if type(img) == list:
            return pygame.transform.flip(img[int(self.frame) % len(img)], self.vflip, self.hflip)
        return pygame.transform.flip(img, self.vflip, self.hflip)

    def get_rect(self):
        rect = self.get_image().get_rect()
        return pygame.Rect(self.x, self.y, rect.width, rect.height)
