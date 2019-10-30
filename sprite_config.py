import pygame
class SpriteConfig:
    def __init__ (self, rect, num, name='idle', mwpt=40, border=3, lookBuffer=0.2, animSpeed=4, skipBuffer=0):
        self.name = name
        self.maxWidthPerTile = mwpt
        self.border = border
        self.lookBuffer = lookBuffer
        self.rect = rect
        self.num = num
        self.reference = {}
        self.loopIndex = 0
        self.animSpeed = animSpeed
        self.skipBuffer = skipBuffer

    def getAnimation (self, name):
        return self.config[self.reference[name]]
    def iterate(self):
        for i in self.config:
            yield i
        raise StopIteration