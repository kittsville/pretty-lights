import math

from helpers import microcontroller
from helpers.colorTools import Color

class Animation:
    fps     = 30
    name    = 'base-animation'

    def generateColor(self, t, i, c, y):
        value = 255 if t % 2 == 0 else 0
        return Color(value, value, value)

class HeartBeat(Animation):
    name = 'heartbeat'

    def generateColor(self, t, i, c, y):
        intensity = (math.sin(t * 2) + 1) / 2
        lum_range = 255 - microcontroller.MIN_LUM

        return Color(255, 255, int(intensity * lum_range) + microcontroller.MIN_LUM)

class ColorRotation(Animation):
    name = 'color-rotation'

    def generateColor(self, t, i, c, y):
        hue = int(t * 50 % 255)
        return Color.fromHue(hue)

class Rainbow(Animation):
    name = 'rainbow'

    def generateColor(self, t, i, c, y):
        hue = int(((t * 50) + (i * 10)) % 255)
        return Color.fromHue(hue)

class Rainfall(Animation):
    name = 'rainfall'

    def generateColor(self, t, i, c, y):
        intensity = (math.sin(t * 3 - y) + 1) / 2
        lum_range = 255 - microcontroller.MIN_LUM

        hue = 160
        sat = 255
        lum = int(intensity * lum_range) + microcontroller.MIN_LUM

        return Color(hue, sat, lum)

# This is broken
class RainbowColumns(Animation):
    name = 'rainbow-columns'

    def generateColor(self, t, i, c, y):
        hueRange    = max(microcontroller.LED_COLUMNS)
        hue         = int(y + t * 4 % (hueRange + 1) / hueRange * 255)

        return Color.fromHue(hue)

animations = {animation.name: animation for animation in Animation.__subclasses__()}
