import random
import time
import requests
import display
import pygame
import signal
import sys


class Snake(display.App):
    framerate = 3
    def __init__(self, d):
        display.App.__init__(self, d)

        self.w = 80
        self.h = 16

        self.newGame()
        self.eventBlock = False

    def newGame(self):
        self.snake = [(13, 8), (12, 8), (11, 8), (10, 8)]
        self.apples = [self.randomApple() for i in range(3)]
        self.x_dir = 1
        self.y_dir = 0
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
        head = (self.snake[0][0] + self.x_dir, self.snake[0][1] + self.y_dir)

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
            if (event.axis == 0 and event.value != 0 and self.x_dir == 0):
                self.x_dir = int(event.value)
                self.y_dir = 0
                self.eventBlock = True

            elif (event.axis == 1 and event.value != 0 and self.y_dir == 0):
                self.y_dir = int(event.value)
                self.x_dir = 0
                self.eventBlock = True

if __name__=="__main__":
    disp = display.Display()
    snake = Snake(disp)
    def term_handler(sig, frame):
        snake.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, term_handler)
    snake.loop()
