import math

from helpers import microcontroller

class Animation:
    fps     = 30
    name    = 'base-animation'

    def generateLed(self, t, i, c, y):
        return [255, 255, 255]

class HeartBeat(Animation):
    name = 'heartbeat'

    def generateLed(self, t, i, c, y):
        intensity = (math.sin(t * 2) + 1) / 2
        lum_range = 255 - microcontroller.MIN_LUM

        return [255, 255, int(intensity * lum_range) + microcontroller.MIN_LUM]

class ColorRotation(Animation):
    name = 'color-rotation'

    def generateLed(self, t, i, c, y):
        return [int(t * 50 % 255), 255, 255]

class Rainbow(Animation):
    name = 'rainbow'

    def generateLed(self, t, i, c, y):
        return [int(((t * 50) + (i * 10)) % 255), 255, 255]

class Rainfall(Animation):
    name = 'rainfall'

    def generateLed(self, t, i, c, y):
        intensity = (math.sin(t * 3 - y) + 1) / 2
        lum_range = 255 - microcontroller.MIN_LUM

        return [160, 255, int(intensity * lum_range) + microcontroller.MIN_LUM]

# This is broken
class RainbowColumns(Animation):
    name = 'rainbow-columns'

    def generateLed(self, t, i, c, y):
        hueRange = max(microcontroller.LED_COLUMNS)

        return [int(y + t * 4 % (hueRange + 1) / hueRange * 255), 255, 255]

animations = {animation.name: animation for animation in Animation.__subclasses__()}
