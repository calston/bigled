#include <OctoWS2811.h>
#include "font.h"

#define RED    0xAA0000
#define GREEN  0x001600
#define BLUE   0x000016
#define YELLOW 0x101400
#define PINK   0x120009
#define ORANGE 0x100400
#define WHITE  0x101010

const int ledsPerStrip = 160;

DMAMEM int displayMemory[ledsPerStrip*6];
int drawingMemory[ledsPerStrip*6];

const int config = WS2811_GRB | WS2811_800kHz;

OctoWS2811 leds(ledsPerStrip, displayMemory, drawingMemory, config);

int makeColor(unsigned int hue, unsigned int saturation, unsigned int lightness)
{
  unsigned int red, green, blue;
  unsigned int var1, var2;

  if (hue > 359) hue = hue % 360;
  if (saturation > 100) saturation = 100;
  if (lightness > 100) lightness = 100;

  // algorithm from: http://www.easyrgb.com/index.php?X=MATH&H=19#text19
  if (saturation == 0) {
    red = green = blue = lightness * 255 / 100;
  } else {
    if (lightness < 50) {
      var2 = lightness * (100 + saturation);
    } else {
      var2 = ((lightness + saturation) * 100) - (saturation * lightness);
    }
    var1 = lightness * 200 - var2;
    red = h2rgb(var1, var2, (hue < 240) ? hue + 120 : hue - 240) * 255 / 600000;
    green = h2rgb(var1, var2, hue) * 255 / 600000;
    blue = h2rgb(var1, var2, (hue >= 120) ? hue - 120 : hue + 240) * 255 / 600000;
  }
  return (red << 16) | (green << 8) | blue;
}

unsigned int h2rgb(unsigned int v1, unsigned int v2, unsigned int hue)
{
  if (hue < 60) return v1 * 60 + (v2 - v1) * hue;
  if (hue < 180) return v2 * 60;
  if (hue < 240) return v1 * 60 + (v2 - v1) * (240 - hue);
  return v1 * 60;
}

void setPixel(int x, int y, unsigned int colour) {
  if (x>79 || y > 15) return;
  if (y < 8) {
    leds.setPixel((y * 160) + x, colour);
  }
  else {
    leds.setPixel(((y - 8) * 160) + (159 - x), colour);
  }
}

void renderText(const char s[], int x, int y, unsigned int colour) {
  int ix, iy;
  for (unsigned int i = 0; i < strlen(s); i++){
    for (ix = 0; ix < 5; ix++) {
      for (iy = 0; iy < 7; iy++) {
        if (FONT5_7[(int)s[i]][ix] & (1<<(6-iy)))
          setPixel(x + (i*6) + ix, y+iy, colour);
      }
    }
  }
}

int mode = 0;
int px_buf = 0;
int px_count = 0;
int px_sub_count = 0;
int px_x = 0;
int px_y = 0;
unsigned long previousMillis = 0;

void readSerial() {
  unsigned long currentMillis = millis();
  if ((mode==1) && (currentMillis - previousMillis >= 2000)) {
    // Timeout 
    mode = 0;
    previousMillis = currentMillis;
  }
  while (Serial.available()) {
    char in_b = Serial.read();
    if (mode == 0) {
      // Set new mode
      mode = (int) in_b;
      previousMillis = currentMillis;
    }
    else if (mode==1) {
      // Full buffer stream 
      px_buf += (unsigned int) in_b << 8*(2-px_sub_count);
      px_sub_count++;
      if (px_sub_count > 2){
        setPixel(px_x, px_y, px_buf);
        px_buf = 0;
        px_x++;
        if (px_x > 79) {
          px_x = 0;
          px_y++;
        }        
        if (px_y > 15) {
          // End of stream
          mode=0;
          px_sub_count=0;
          px_x=0;
          px_y=0;
          leds.show();
        }
        px_sub_count=0;
      }
    }
  }
}

void setup() {
  Serial.begin(9600); 
  leds.begin();
  leds.show();
}

char test[] = "Whats up       ";
char sub[13] = "            ";
unsigned int counter = 0;

void loop() {
  /*renderText(sub, 1, 8, 0);
  for (int i = 0; i<13; i++) {
    if ((counter+i) < strlen(test)) {
      sub[i] = test[counter + i];
    }
    else {
      sub[i] = test[counter - strlen(test) + i ];
    }
  }
  renderText(sub, 1, 8, GREEN);
  leds.show();
  counter++;
  if (counter >= strlen(test)) {
    counter = 0;
  }
  delay(200);*/
  readSerial();
}
