import serial
import colorsys
import pygame
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

def hsv(h, s, v):
    return tuple(map(lambda x: int(x*255), colorsys.hsv_to_rgb(h, s, v)))

class Display(object):
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0')

        self.size = (80, 16)
        self.surface = pygame.Surface(self.size, depth=24)

    def stop(self):
        self.ser.close()

    def blank(self):
        self.surface.fill((0, 0, 0))

    def flip(self):
        self.ser.write(b'\x01')
        buf = self.surface.get_view().raw
        self.ser.write(b''.join(buf[i:i+3][::-1] for i in range(0, len(buf), 3)))

class App(object):
    framerate = 20

    def __init__(self, disp, init=True):
        if init:
            pygame.display.init()
            pygame.joystick.init()
            pygame.font.init()

        self.display = disp
        self.running = True

        self.clock = pygame.time.Clock()

    def draw(self, surface):
        pass

    def stop(self, display_stop=True):
        if display_stop:
            self.display.stop()
        self.running = False

    def getEvent(self, event):
        pass

    def loop(self):
        while self.running:
            for event in pygame.event.get():
                self.getEvent(event)
                if event.type == pygame.QUIT:
                    self.stop()
                    self.running = False

                if event.type == pygame.JOYDEVICEADDED:
                    js = pygame.joystick.Joystick(event.device_index)
                    js.init()

                if (event.type == pygame.JOYBUTTONDOWN) and (event.button == 9):
                        self.running = False

            self.display.blank()
            self.draw(self.display.surface)
            self.display.flip()

            self.clock.tick(self.framerate)
