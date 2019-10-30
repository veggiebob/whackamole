import pygame
class AnimatedSprite:
    def __init__ (self, spritesheet, loadConfigs, default="idle"):
        self.images = {} # name, images list
        self.loadConfig = loadConfigs # SpriteConfig[]
        self.default = default
        self.Sdefault = None
        self.spritesheet = spritesheet

        self.frameTime = 5
        self.time = 0

        self.currentAnimation = default
        self.nextAnimation = [[default, 0]] # [next animation, index that it will happen]
        self.currentConfig = 0
        self.stack = []
    def getStackLength (self):
        return len(self.stack)
    def loadImages (self, surface=None):
        for config in self.loadConfig:
            name = config.name
            clip = config.rect
            mclip = pygame.Rect(clip.x, clip.y+clip.height*config.lookBuffer, clip.width, clip.height-clip.height*config.lookBuffer*2)
            num = config.num
            if surface is not None:
                pygame.draw.rect(surface, (0, 0, 0), clip, 1)
                pygame.draw.rect(surface, (255, 0, 0), mclip, 1)
            lastX = clip.x + 0
            self.images[name] = []
            for i in range(num):
                if num==1:
                    nextr = [clip.x, clip.x+clip.width]
                    print('only 1, so set the imaging clip')
                else:
                    nextr = self.getSpan(lastX, mclip.y, mclip.height, config.maxWidthPerTile)
                imgw = nextr[1]-nextr[0]
                img_clip = pygame.Rect(nextr[0]-config.border, clip.y, imgw+config.border*2, clip.height)
                img = pygame.Surface((25, 25))
                img.fill((255, 0, 0))
                try:
                    img = self.spritesheet.subsurface(img_clip)
                except:
                    pass

                if surface is not None:
                    #green box - the raw bounding box
                    pygame.draw.rect(surface, (0, 255, 0), (nextr[0], clip.y, imgw, clip.height), 1)
                    #blue box - where the image comes from
                    pygame.draw.rect(surface, (0, 0, 255), img_clip, 1)

                if nextr[1] >= clip.x + clip.width:
                    print('broke at %d'%i)
                    break
                lastX = nextr[1] + config.skipBuffer
                self.images[name].append(img)

        print("done loading!")
    def getSpan (self, startX, startY, yrange, maxWidth):
        maxX = startX
        minX = startX+maxWidth
        for y in range(startY, startY+yrange+1):
            hitImage = False
            for x in range(startX, startX+maxWidth):
                try:
                    col = self.spritesheet.get_at((x, y))
                except:
                    break
                brightness = (col[0]+col[1]+col[2])/3
                if brightness>0 and not hitImage:
                    hitImage = True
                    minX = min(minX, x)
                elif brightness<3 and hitImage:
                    if x-minX < maxWidth:
                        maxX = max(maxX, x)
                    break
        clear = True
        maxX+=1
        for y in range(startY, startY+yrange):
            try:
                col = self.spritesheet.get_at((maxX, y))
            except:
                break
            brightness =  (col[0]+col[1]+col[2])/3
            if brightness>3:
                clear = False
                break
        if not clear and maxX-minX<maxWidth:
            real = self.getSpan(maxX, startY, yrange, maxWidth-(maxX-minX))
            return [minX-1, real[1]]
        else:
            return [minX-1, min(maxX, startX+maxWidth)+1]
    def getCurrentConfig (self):
        index = -1
        for i in self.loadConfig:
            index += 1
            if i.name==self.currentAnimation:
                self.currentConfig = index
                break
    def setFrameTime (self):
        self.frameTime = self.loadConfig[self.currentConfig].animSpeed
    def advanceFrame (self):
        self.stack.pop(0)
        changed = False
        for i in self.nextAnimation:
            i[1] -= 1
            if i[1] <= 0:
                self.currentAnimation = i[0]
                self.getCurrentConfig()
                changed = True
        if changed:
            self.nextAnimation.pop(0)
        if len(self.stack)==0:
            if self.Sdefault is None:
                self.addAnimation('default')
            else:
                self.addAnimation(self.Sdefault)
                self.Sdefault = None
        self.setFrameTime()
        #hurry it up if there's a long queue
        self.frameTime -= max(len(self.nextAnimation), 0)
    def clearStack (self):
        self.stack = []
    def whenDone (self, d):
        self.Sdefault = d
    def addAnimation (self, name):
        if name=='default':
            name = self.default
        anim = self.images[name]
        self.nextAnimation.append([name, len(self.stack)-1])
        if self.currentAnimation == self.default:
            self.stack = []
        for i in anim:
            self.stack.append(i)
    def addAnimationById (self, id):
        if id>=len(self.images):
            self.addAnimation('default')
        else:
            self.addAnimation(list(self.images.keys())[id])
    def getImage(self, flip=False):
        if len(self.stack)==0:
            self.addAnimation('default')
        self.time+=1
        if self.time>=self.frameTime:
            self.time = 0
            self.advanceFrame()
        return pygame.transform.flip(self.stack[0], flip, False)