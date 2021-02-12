import time
import display
import pygame
import signal
import sys
import yaml

from clock import Clock
from tetris import Tetris
from snake import Snake

class Blank(display.App):

    def draw(self, surface):
        pass


class Menu(display.App):
    framerate = 3
    def __init__(self, d):
        display.App.__init__(self, d)

        self.menu_items = [
            ('Clock', Clock(d)),
            ('Tetris', Tetris(d)),
            ('Snake', Snake(d)),
            ('Off', Blank(d))
        ]

        self.selected = 0

        self.font = pygame.font.Font("fonts/DejaVuSansMono.ttf", 8)

    def draw(self, surface):
        itime = self.font.render(time.strftime('%H:%M:%S'), False, (0, 128, 0))

        for i, item in enumerate(self.menu_items[self.selected:self.selected+2]):
            if i == 0:
                name = f"> {item[0]}"
            else:
                name = f"  {item[0]}"
            surface.blit(self.font.render(name, False, (0, 128, 0)), (1, 8*i))

    def switchTo(self):
        cls = self.menu_items[self.selected][1]
        cls.running = True
        cls.loop()

    def getEvent(self, event):
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                if (event.value > 0) and (self.selected < (len(self.menu_items)-1)):
                    self.selected += 1
                if (event.value < 0) and (self.selected > 0):
                    self.selected -= 1

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                self.switchTo()


if __name__=="__main__":
    disp = display.Display()
    menu = Menu(disp)
    def term_handler(sig, frame):
        menu.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, term_handler)
    menu.loop()
