import pygame
import time
import display
import random
import signal
import sys


class Block(object):
    def __init__(self, pattern):
        self.shape = pattern['shape']
        self.color = pattern['color']
        self.w = 16
        self.h = 80
        self.position = [0, 4]

    def moveDown(self):
        maxx = len(self.shape)
        if (self.position[0] + maxx < self.h):
            self.position[0] += 1

    def moveRight(self):
        if self.position[1] >= 1:
            self.position[1] -= 1

    def moveLeft(self):
        if self.position[1] + len(self.shape[0]) < self.w:
            self.position[1] += 1

    def rotateLeft(self):
        maxy = len(self.shape[0])
        maxx = len(self.shape)
        newmatrix = [[0 for i in range(maxx)] for i in range(maxy)]
        for x in range(maxx):
            for y in range(maxy):
                newmatrix[maxy-1-y][x] = self.shape[x][y]
            
        # Shift the piece away from the edge
        if (len(newmatrix[0]) + self.position[1]) > self.w:
            self.position[1] = self.w - len(newmatrix[0])

        self.shape = newmatrix

    def rotateRight(self):
        maxy = len(self.shape[0])
        maxx = len(self.shape)
        newmatrix = [[0 for i in range(maxx)] for i in range(maxy)]
        for x in range(maxx):
            for y in range(maxy):
                newmatrix[y][maxx-1-x] = self.shape[x][y]
        
        if (len(newmatrix[0]) + self.position[1]) > self.w:
            self.position[1] = self.w - len(newmatrix[0])

        self.shape = newmatrix


class Tetris(display.App):
    framerate = 10

    def __init__(self, *a, **kw):
        display.App.__init__(self, *a, **kw)

        self.shapes = [
            { # T
                'shape': ((0, 1),(1, 1),(0, 1)),
                'color': 1
            },
            { # Z
                'shape': ((0, 1), (1, 1), (1, 0)),
                'color': 2
            },
            { # S
                'shape': ((1, 0),(1, 1),(0, 1)),
                'color': 3
            },
            { # I
                'shape': ((1,),(1,),(1,),(1,)),
                'color': 4
            },
            { # O
                'shape': ((1, 1),(1, 1)),
                'color': 5
            },
            { # J
                'shape': ((1, 1), (1, 0), (1, 0)),
                'color': 6
            },
            { # L
                'shape': ((1, 1), (0, 1), (0, 1)),
                'color': 7
            }
	]

        self.colors = [
            (0, 0, 0),
            (255, 0, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 255, 255),
            (255, 255, 0),
            (0, 0, 255),
            (255, 128, 0)
        ]

        self.font = pygame.font.Font("fonts/DejaVuSansMono.ttf", 12)

        self.run = True
        self.speed = 0.01
        self.down = 0
        self.game_over = False

        self.w = 16
        self.h = 80

        self.last_dir = 0
        
        self.newField()
        self.getBlock()

    def newField(self):
        self.field = [[0 for i in range(self.w)] for i in range(self.h)]

    def getBlock(self):
        self.currentBlock = Block(random.choice(self.shapes))

    def disp(self):
        self.screen.display(self.image)
        self.screen.partial_update()

    def eraseBlock(self):
        ax, ay = self.currentBlock.position
        for x, row in enumerate(self.currentBlock.shape):
            for y, v in enumerate(row):
                if v:
                    self.field[ax + x][ay + y] = 0

    def drawBlock(self):
        ax, ay = self.currentBlock.position
        for x, row in enumerate(self.currentBlock.shape):
            for y, v in enumerate(row):
                if v:
                    self.field[ax + x][ay + y] = self.currentBlock.color

    def clip(self):
        ax, ay = self.currentBlock.position
        
        maxy = len(self.currentBlock.shape[0])
        maxx = len(self.currentBlock.shape)

        if (maxx + ax) >= len(self.field):
            return True

        extents = [-1 for i in range(maxy)]

        for i in reversed(range(maxx)):
            for j in range(maxy):
                if (self.currentBlock.shape[i][j] == 1) and (extents[j] == -1):
                    extents[j] = i

        for y, x in enumerate(extents):
            if self.field[ax + x + 1][ay + y] > 0:
                return True

        return False

    def checkField(self):
        newfield = []
        for x, row in enumerate(self.field):
            if sum(i>0 for i in row) != len(row):
                newfield.append(row)

        self.field = [[0 for i in range(self.w)] for i in range(self.h - len(newfield))]
        self.field.extend(newfield)

    def clipRight(self):
        ax, ay = self.currentBlock.position
        
        maxx = len(self.currentBlock.shape)
        maxy = len(self.currentBlock.shape[0])

        if ay > 0:
            for i, row in enumerate(self.currentBlock.shape):
                try:
                    maxr = row.index(1)
                    if row[maxr] and self.field[ax + i][ay + maxr - 1]:
                        return True
                except ValueError as e:
                    pass
        else:
            return True

    def clipLeft(self):
        ax, ay = self.currentBlock.position
        
        maxx = len(self.currentBlock.shape)
        maxy = len(self.currentBlock.shape[0])


        if (ay + maxy) < self.w:
            for i, row in enumerate(self.currentBlock.shape):
                try:
                    minr = len(row) - 1 - row[::-1].index(1)

                    if row[minr] and self.field[ax + i][ay + minr + 1]:
                        return True
                except ValueError as e:
                    pass
        else:
            return True

    def draw(self, surface):
        self.move()
        if not self.game_over:
            if (self.down > 1):
                self.down = 0
                clipped = self.clip()
                if not clipped:
                    self.eraseBlock()
                    self.currentBlock.moveDown()
                    self.drawBlock()
                else:
                    if self.currentBlock.position[0] < 4:
                        self.game_over = True
                        
                    self.checkField()
                    self.getBlock()
            else:
                self.down += 1

        for x, row in enumerate(self.field):
            for y, b in enumerate(row):
                if b:
                    surface.set_at((x, y), self.colors[b])

        if self.game_over:
            surface.blit(self.font.render("GAME OVER!", False, (255, 0, 0)), (10, 3))

    def move(self):
        if self.last_dir < 0:
            if not self.clipRight():
                self.eraseBlock()
                self.currentBlock.moveRight()
                self.drawBlock()

        if self.last_dir > 0:
            if not self.clipLeft():
                self.eraseBlock()
                self.currentBlock.moveLeft()
                self.drawBlock()

    def getEvent(self, event):
        d = None
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if event.value > 0:
                    clipped = self.clip()
                    while not clipped:
                        self.eraseBlock()
                        self.currentBlock.moveDown()
                        self.drawBlock()
                        clipped = self.clip()

            if event.axis == 1:
                self.last_dir = event.value
       
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                self.eraseBlock()
                self.currentBlock.rotateLeft()
                self.drawBlock()

            if event.button == 2:
                self.eraseBlock()
                self.currentBlock.rotateRight()
                self.drawBlock()

            if self.game_over and (event.button == 8):
                self.game_over = False
                self.newField()
                self.getBlock()
                self.down = 0
    
if __name__=="__main__":
    disp = display.Display()
    tetris = Tetris(disp)
    def term_handler(sig, frame):
        tetris.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, term_handler)
    tetris.loop()
