import math
import random

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

class Ripples(Animation):
    name = 'ripples'

    def __init__(self):
        self.hue = random.randint(0, 255)

    def generateColor(self, t, i, c, y):
        intensity = (math.sin(t * 3 - y) + 1) / 2
        lum_range = 255 - microcontroller.MIN_LUM

        sat = 255
        lum = int(intensity * lum_range) + microcontroller.MIN_LUM

        return Color(self.hue, sat, lum)

animations = {animation.name: animation for animation in Animation.__subclasses__()}
