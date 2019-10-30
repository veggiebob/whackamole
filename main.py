### ARROW KEYS TO MOVE
### SPACE TO SHOOT



import math
import random

import pygame, sys
from pygame.locals import *
from animated_sprite import AnimatedSprite
from sprite_config import SpriteConfig
from text import Text
pygame.init()

KIRBY_SPRITE_SHEET = pygame.image.load("kirby_sprite_sheet_with_gun_fixed.png")
ZOMBIE_SPRITE_SHEET = pygame.image.load('zombie_spritesheet_2.png')
# KIRBY_SPRITE_SHEET.set_colorkey((255, 255, 255), pygame.RLEACCEL)
# KIRBY_SPRITE_SHEET = KIRBY_SPRITE_SHEET.convert_alpha()
CLOCK = pygame.time.Clock()
FPS = 30
TIME = 0
T = Text()

K_WIDTH = KIRBY_SPRITE_SHEET.get_width()
K_HEIGHT = KIRBY_SPRITE_SHEET.get_height()
Z_WIDTH = ZOMBIE_SPRITE_SHEET.get_width()
Z_HEIGHT = ZOMBIE_SPRITE_SHEET.get_height()

WIDTH = 400
HEIGHT = 400
UI_SIZE = 50
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN.fill((255, 255, 255))
SCREEN.blit(KIRBY_SPRITE_SHEET, (0, 0))

###image configurations
attack = SpriteConfig(
    pygame.Rect(6, 306, K_WIDTH-1, 25), # capture rect of all
    16, # number
    'attack', # name
    40, # max width per tile
    3, # border
    0.0, # look buffer
    2, # frames / animation_frame
    0, # skipping buffer - how many pixels to skip after green line
)
shoot = SpriteConfig(
    pygame.Rect(6, 333, K_WIDTH-1, 25), # capture rect of all
    16, # number
    'shoot', # name
    40, # max width per tile
    3, # border
    0.0, # look buffer
    2, # frames / animation_frame
    0, # skipping buffer - how many pixels to skip after green line
)
spin_attack = SpriteConfig(
    pygame.Rect(12, 594, K_WIDTH-1, 25), # capture rect of all
    8, # number
    'spin_attack', # name
    40, # max width per tile
    3, # border
    0.2, # look buffer
    3, # frames / animation_frame
    0, # skipping buffer - how many pixels to skip after green line
)
walk = SpriteConfig(
    pygame.Rect(6, 52, 243, 26), # capture rect of all
    10, # number
    'walk', # name
    25, # max width per tile
    2, # border
    0.2, # look buffer
    3, # frames / animation_frame
    1
)
ascend = SpriteConfig(
    pygame.Rect(6, 391, 243, 26), # capture rect of all
    6, # number
    'ascend', # name
    30, # max width per tile
    2, # border
    0.0, # look buffer
    2, # frames / animation_frame
    0
)
land = SpriteConfig(
    pygame.Rect(4, 130, 250, 23), # capture rect of all
    10, # number
    'land', # name
    40, # max width per tile
    2, # border
    0.3, # look buffer
    1, # frames / animation_frame
)
flip = SpriteConfig(
    pygame.Rect(16, 488, K_WIDTH-1, 40),
    12,
    'flip',
    30,
    2,
    0.0,
    4
)
spin = SpriteConfig(
    pygame.Rect(10, 750, K_WIDTH-1, 34), # capture rect of all
    11, # number
    'spin', # name
    40, # max width per tile
    2, # border
    0.1, # look buffer
    1, # frames / animation_frame
    4
)
idle = SpriteConfig(
    pygame.Rect(7, 244, K_WIDTH-1, 22),
    17,
    'idle',
    30,
    2,
    0.0,
    3,
    0
)
###

KEY_MAP = [None for i in range(1000)]
KEY_MAP[K_LEFT] = 'walk'
KEY_MAP[K_RIGHT] = 'walk'
KEY_MAP[K_UP] = 'walk'
KEY_MAP[K_DOWN] = 'walk'
KEY_MAP[K_SPACE] = 'shoot'
kirb_right = True
kirb_x = WIDTH/2
kirb_y = HEIGHT/2
bullet_speed = 10
half_speed = bullet_speed / math.sqrt(2)
walk_speed = 6
keyid = -1
DIFFICULTY = 0
SCORE = 0
LIVES = 3
GAMEOVER = False
keys = [False for i in range(1000)]

z_walk = SpriteConfig(
    pygame.Rect(6, 90, K_WIDTH - 1, 68),  # capture rect of all
    12,  # number
    'walk',  # name
    40,  # max width per tile
    3,  # border
    0.0,  # look buffer
    8,  # frames / animation_frame
    0,  # skipping buffer - how many pixels to skip after green line
)
z_die = SpriteConfig(
    pygame.Rect(9, 395, 420, 70),
    8,
    'die',
    48,
    3,
    0.0,
    4,
    0
)
z_hit = SpriteConfig(
    pygame.Rect(9, 395, 420, 70),
    2,
    'hit',
    48,
    3,
    0.0,
    10,
    0
)
ex_zomb = AnimatedSprite(ZOMBIE_SPRITE_SHEET, [z_walk, z_hit, z_die], 'walk')
ex_zomb.loadImages()
kirb = AnimatedSprite(KIRBY_SPRITE_SHEET, [idle, walk, attack, flip, spin, land, ascend, spin_attack, shoot], "idle")
SCREEN.blit(KIRBY_SPRITE_SHEET, (0, 0))
kirb.loadImages(SCREEN)
enemies = []
bullets = []
def generateZombie ():
    x = 0
    y = random.randint(0, HEIGHT-UI_SIZE*2)+UI_SIZE
    dir = 1 + DIFFICULTY
    if bool(random.randint(0,1)):
        x = WIDTH + 50
        dir *= -1
    else:
        x = -50
    enemies.append(Enemy(x, y, dir))
def constrain (v, a, b):
    return min(max(v, a), b)
class Bullet:
    def __init__ (self, x, y, spdx, spdy):
        #spd = x speed of bullet
        self.spdx = spdx
        self.spdy = spdy
        self.x = x
        self.y = y
        self.dead = False
    def update (self):
        self.x += self.spdx
        self.y += self.spdy
        self.checkDead()
    def getPoint (self):
        return [int(self.x), int(self.y)]
    def draw (self, surface):
        pygame.draw.circle(surface, (255, 255, 200), self.getPoint(), 2, 0)
    def checkDead (self):
        if self.x > WIDTH or self.x < 0 or self.y < 0 or self.y > HEIGHT:
            self.dead = True

class Enemy (pygame.sprite.Sprite):
    def __init__ (self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        # (x, y) represents bottom center
        self.x = x
        self.y = y
        self.time = 0
        self.speed = speed
        self.interval = z_walk.animSpeed / abs(self.speed)
        self.dead = False
        self.deadShot = False
        self.size = 25
        self.animSprite = AnimatedSprite(ZOMBIE_SPRITE_SHEET, [z_walk, z_hit, z_die], 'walk')
        self.animSprite.loadImages()
        self.rect = pygame.rect.Rect((self.x-self.size/2, self.y-self.size, self.size, self.size))
        self.image = pygame.Surface((self.size, self.size))
        self.hp = 100
    def updateHit (self):
        iw = self.image.get_width()
        ih = self.image.get_height()
        self.rect = pygame.rect.Rect((
            self.x-iw/2,
            self.y-ih,
            iw,
            ih
        ))
    def update (self):
        self.updateHit()
        self.image = self.animSprite.getImage(True if self.speed < 0 else False)
        if not self.dead and self.time%self.interval == 0:
            self.x += self.speed*self.interval
        self.time += 1 * abs(self.speed)
    def hItYoUrSeLf (self):
        if not self.dead:
            self.animSprite.clearStack()
            self.animSprite.addAnimation('hit')
            self.hp -= 25
            if self.hp <= 0:
                self.die()
    def die (self):
        self.animSprite.addAnimation('die')
        self.dead = True
    def draw (self, surf):
        surf.blit(self.image, (self.x-self.image.get_width()/2, self.y-self.image.get_height()))
    def collidePoint (self, x, y):
        return self.rect.collidepoint(x, y)

while True:
    mouse = 0,0
    kp = False
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        elif event.type==MOUSEBUTTONDOWN:
            mouse = event.pos
            #generateZombie()
            if GAMEOVER:
                pygame.quit()
                sys.exit()
            print(mouse)
        elif event.type==KEYDOWN:
            kp = True
            keyid = event.key
            keys[keyid] = True
            print("pressed %d"%keyid)
        elif event.type==KEYUP:
            keyid = -1
            keys[event.key] = False
    if not GAMEOVER:
        bullx = 0
        bully = 0
        if keys[K_RIGHT]:
            if kp:
                kirb.clearStack()
            kirb_right = True
            kirb_x += walk_speed
            bullx = 1
            kirb.whenDone('walk')
        if keys[K_LEFT]:
            if kp:
                kirb.clearStack()
            kirb_right = False
            kirb_x -= walk_speed
            bullx = -1
            kirb.whenDone('walk')
        if keys[K_UP]:
            kirb_y -= walk_speed
            bully = -1
            if kp:
                kirb.clearStack()
            kirb.whenDone('walk')
        if keys[K_DOWN]:
            kirb_y += walk_speed
            bully = 1
            if kp:
                kirb.clearStack()
            kirb.whenDone('walk')

        kirbImage = kirb.getImage(not kirb_right)
        kw = kirbImage.get_width()
        kh = kirbImage.get_height()

        kirb_x = constrain(kirb_x, 0, WIDTH-kw)
        kirb_y = constrain(kirb_y, UI_SIZE, HEIGHT-UI_SIZE-kh)

        if kp:
            if keyid>=48 and keyid<=58:
                action = keyid-48
                kirb.addAnimationById(action)
            else:
                action = KEY_MAP[keyid]
                if action is not None:
                    kirb.addAnimation(action)
                    if action == 'shoot':
                        bs = bullet_speed if bully==0 or bullx==0 else half_speed
                        if bully==0 and bullx==0:
                            bullx = 1 if kirb_right else -1
                        bullets.append(Bullet(kirb_x+kw/2, kirb_y+kh/2, bs*bullx, bs*bully))

        zomb_test = ex_zomb.getImage()
        zw = zomb_test.get_width()
        zh = zomb_test.get_height()

        SCREEN.fill((70, 100, 70))
        SCREEN.blit(kirbImage, (kirb_x, kirb_y))

        for e in enemies:
            e.update()
            e.draw(SCREEN)
            if not e.dead and (e.x < -50 or e.x > WIDTH + 50):
                e.dead = True
                e.animSprite.clearStack()
                LIVES -= 1
                if LIVES<0:
                    GAMEOVER = True
            if e.dead and e.animSprite.getStackLength()<2:
                enemies.remove(e)
        if len(enemies)==0:
            generateZombie()

        for b in bullets:
            b.update()
            b.draw(SCREEN)
            for e in enemies:
                if e.collidePoint(b.x, b.y):
                    e.hItYoUrSeLf()
                    if e.dead and not e.deadShot:
                        SCORE += 1
                        e.deadShot = True
                        generateZombie()
                        if bool(random.randint(0,1)):
                            generateZombie()
                    b.dead = True
                    break
            if b.dead:
                bullets.remove(b)

        SCREEN.fill((0, 0, 0), (0, 0, WIDTH, UI_SIZE))
        SCREEN.fill((0, 0, 0), (0, HEIGHT-UI_SIZE, WIDTH, UI_SIZE))
        SCREEN.blit(T.draw("Score: %d"%SCORE, 40, (255, 255, 255)), (0, 0))
        SCREEN.blit(T.draw("Lives: %d"%LIVES, 40, (255, 255, 255)), (0, HEIGHT-UI_SIZE))

        CLOCK.tick(FPS)
        TIME += 1
    else:
        SCREEN.blit(T.draw("GAMEOVER", 90, (255, 0, 0)), (0, 0))
    pygame.display.update()
