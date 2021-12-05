import math
import random

from helpers import microcontroller
from helpers.colorTools import Color

class Animation:
    fps     = 30
    name    = 'base-animation'

    def generateColor(self, t, i, c, y):
        """
        Render a single pixel as part of a larger animation

        :param t: Time in seconds, including nanoseconds
        :param i: Index of pixel
        :param c: Index of pixel's column
        :param y: Pixel's height within column
        :return: Pixel's Color
        """
        value = 255 if t % 2 == 0 else 0
        return Color(value, value, value)

class Breathing(Animation):
    name        = 'breathing'
    lumRange    = 255 - microcontroller.MIN_LUM

    def generateColor(self, t, i, c, y):
        intensity   = (math.sin(t * 2) + 1) / 2
        lum         = int(intensity * Breathing.lumRange) + microcontroller.MIN_LUM

        return Color(255, 255, lum)

class Rampant(Animation):
    name        = 'rampant'
    lumRange    = 255 - microcontroller.MIN_LUM

    @staticmethod
    def trapezoidalWave(xin, width=1., slope=1.):
        x = xin % (4 * width)
        if (x <= width):
            # Ascending line
            return x * slope;
        elif (x <= 2 * width):
            # Top horizontal line
            return width * slope
        elif (x <= 3 * width):
            # Descending line
            return 3 * width * slope - x * slope
        elif (x <= 4 * width):
            # Bottom horizontal line
            return 0.

    def generateColor(self, t, i, c, y):
        lum = int(Rampant.trapezoidalWave(t) * Rampant.lumRange) + microcontroller.MIN_LUM

        return Color(255, 255, lum)

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


class Trails:
    trailStartLength    = 0.75
    greenHue            = 89

    # Slowest 3
    # Fastest 15

    def __init__(self, speed, trailLength):
        self.speed          = speed
        self.trailLength    = trailLength
        self.height         = max(microcontroller.LED_COLUMNS) + trailLength

    def generateColor(self, t, i, c, y):
        offset      = c * len(microcontroller.LED_COLUMNS)
        trailStart  = (t * self.speed + offset) % self.height

        if y <= trailStart and y >= trailStart - Trails.trailStartLength:
            distFromTrailStart  = trailStart - y
            intensity           = distFromTrailStart / Trails.trailStartLength
            lum                 = int(255 * intensity)
            return Color(Trails.greenHue, 175, lum)
        elif y <= trailStart and y >= trailStart - self.trailLength:
            distFromTrailPeak   = trailStart - y - Trails.trailStartLength
            normalisedDFTP      = distFromTrailPeak / (self.trailLength - Trails.trailStartLength)
            intensity           = 1 - normalisedDFTP
            lum                 = int(255 * intensity)
            return Color(Trails.greenHue, 255, lum)
        else:
            return Color.none()



class Matrix(Animation):
    name = 'matrix'

    trails = [
        Trails(8, 8),
        Trails(6, 6),
        Trails(4, 4)
    ]

    def generateColor(self, t, i, c, y):
        return max(map(lambda trailGenerator: trailGenerator.generateColor(t, i, c, y), Matrix.trails), key=lambda x: x.lum)

animations = {animation.name: animation for animation in Animation.__subclasses__()}
