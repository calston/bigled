import time
import requests
import display
import pygame
import signal
import sys
import yaml

class Clock(display.App):
    framerate = 3

    def __init__(self, *a, **kw):
        display.App.__init__(self, *a, **kw)

        self.weather_icons = {
            'Fog': pygame.image.load('images/fog.png'),
            'Thunderstorm': pygame.image.load('images/lightning.png'),
            'Clouds': pygame.image.load('images/cloudy.png'),
            'Few Clouds': pygame.image.load('images/partly.png'),
            'Mist': pygame.image.load('images/partly.png'),
            'Haze': pygame.image.load('images/partly.png'),
            'Rain': pygame.image.load('images/rain.png'),
            'Snow': pygame.image.load('images/snow.png'),
            'Clear': pygame.image.load('images/sunny.png'),
        }

        for n, img in self.weather_icons.items():
            img.fill((255, 255, 255, 64), special_flags=pygame.BLEND_RGBA_MULT)

        self.weather_age = 0
        self.weather = {}

        self.font = pygame.font.Font("fonts/5x7.pcf", 7)


        self.config = yaml.load(open('config.yml').read(), Loader=yaml.BaseLoader)

    def getWeather(self):
        if (time.time() - self.weather_age) > 120:
            try:
                uri = "http://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s" % (
                    self.config['weather']['location'],
                    self.config['weather']['token']
                )
                r = requests.get(uri)
                self.weather = r.json()
            except Exception as e:
                print(f"Error {e} retrieving weather")
            self.weather_age = time.time()
        return self.weather

    def draw(self, surface):
        itime = self.font.render(time.strftime('%H:%M:%S'), False, (0, 128, 0))

        weather = self.getWeather()
        temp_c = weather['main']['temp'] - 273.15

        hue = 1 - ((15 + temp_c) / 55.0)
        if hue > 1:
            hue = 1.0
        temp_color = display.hsv(hue, 1, 0.5)

        itemp = self.font.render(f"{int(temp_c)}°", False, temp_color)

        conditions = weather['weather'][0]['main']
        desc = weather['weather'][0]['description']
        if desc in ["few clouds", "scattered clouds"]:
            conditions = 'Few Clouds'
        if conditions == 'Drizzle':
            conditions = 'Rain'
        icon = self.weather_icons[conditions]

        surface.blit(icon, (1, 2))
        surface.blit(itime, (40, 5))
        surface.blit(itemp, (18, 5))


if __name__=="__main__":
    disp = display.Display()
    clock = Clock(disp)
    def term_handler(sig, frame):
        clock.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, term_handler)
    clock.loop()
