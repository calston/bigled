import random
import time
import display
import pygame
import signal
import sys
import operator


class Snake(display.App):
    framerate = 3
    def __init__(self, *a, **kw):
        display.App.__init__(self, *a, **kw)

        self.w = 80
        self.h = 16

        self.newGame()
        self.eventBlock = False

    def newGame(self):
        self.snake = [(13, 8), (12, 8), (11, 8), (10, 8)]
        self.apples = [self.randomApple() for i in range(3)]
        self.dir_vector = [1, 0]
        self.nutrition = len(self.snake)
        self.framerate = 4

    def randomApple(self):
        return (random.randrange(0, self.w), random.randrange(0, self.h))

    def newApple(self):
        self.apples.append(self.randomApple())

    def setSpeed(self):
        if self.nutrition > 10:
            self.framerate = 5
        if self.nutrition > 20:
            self.framerate = 6
        if self.nutrition > 40:
            self.framerate = 7
        if self.nutrition > 80:
            self.framerate = 9
        if self.nutrition > 160:
            self.framerate = 12

    def draw(self, surface):
        self.eventBlock = False

        head = tuple(map(operator.add, self.snake[0], self.dir_vector))

        if (head[0] >= self.w) or (head[0] < 0) or (head[1] >= self.h) or (head[1] < 0):
            self.newGame()
            return

        if head in self.snake:
            self.newGame()
            return

        if head in self.apples:
            self.apples.pop(self.apples.index(head))
            self.newApple()
            self.nutrition += 1
            self.setSpeed()
        else:
            self.snake.pop()

        self.snake.insert(0, head)

        # Draw apples
        for apple in self.apples:
            surface.set_at(apple, (255, 0, 0))

        # Draw snake
        for segment in self.snake:
            surface.set_at(segment, (0, 255, 0))

    def getEvent(self, event):
        if self.eventBlock:
            return 

        if event.type == pygame.JOYAXISMOTION:
            if (event.axis == 0 and event.value != 0 and self.dir_vector[0] == 0):
                self.dir_vector = [int(event.value), 0]
                self.eventBlock = True

            elif (event.axis == 1 and event.value != 0 and self.dir_vector[1] == 0):
                self.dir_vector = [0, int(event.value)]
                self.eventBlock = True

if __name__=="__main__":
    disp = display.Display()
    snake = Snake(disp)
    def term_handler(sig, frame):
        snake.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, term_handler)
    snake.loop()
