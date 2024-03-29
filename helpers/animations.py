import math
import time
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

    def combineAnimations(self, t, i, c, y, animations):
        return max(map(lambda animation: animation.generateColor(t, i, c, y), animations), key=lambda color: color.lum)
    
class StepThrough(Animation):
    fps     = 2
    name    = 'step-through-colors'
    colors  = [Color(0, 0, 0), Color(255, 255, 255)]

    def __init__(self):
        self.colors = StepThrough.colors

    def generateColor(self, t, i, c, y):
        num_colors = len(self.colors)
        color_index = (int(t) + (i % num_colors)) % num_colors
        color = self.colors[color_index]
        return color
    
class Christmas1(StepThrough):
    fps     = 2
    name    = 'christmas-1'
    colors  = [Color(0, 0, 200), Color.fromHue(36)]

    def __init__(self):
        self.colors = Christmas1.colors

    
class Christmas2(StepThrough):
    fps     = 2
    name    = 'christmas-2'
    colors  = [Color.fromHue(1), Color.fromHue(89), Color.fromHue(36)]

    def __init__(self):
        self.colors = Christmas2.colors

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
    numLedColumns       = len(microcontroller.LED_COLUMNS)

    def __init__(self, speed, trailLength, hue):
        self.speed          = speed
        self.trailLength    = trailLength
        self.height         = max(microcontroller.LED_COLUMNS) + trailLength
        self.hue            = hue

    def generateColor(self, t, i, c, y):
        offset      = c * len(microcontroller.LED_COLUMNS)
        trailStart  = (t * self.speed + offset) % self.height

        column                  = Trails.numLedColumns - c
        normalisedColumn        = column / Trails.numLedColumns
        trailLengthMultiplier   = 1 + (.375 * normalisedColumn)
        relativeTrailLength     = self.trailLength * trailLengthMultiplier

        if y <= trailStart and y >= trailStart - Trails.trailStartLength:
            distFromTrailStart  = trailStart - y
            intensity           = distFromTrailStart / Trails.trailStartLength
            lum                 = int(255 * intensity)
            return Color(self.hue, 175, lum)
        elif y <= trailStart and y >= trailStart - relativeTrailLength:
            distFromTrailPeak   = trailStart - y - Trails.trailStartLength
            normalisedDFTP      = distFromTrailPeak / (relativeTrailLength - Trails.trailStartLength)
            intensity           = 1 - normalisedDFTP
            lum                 = int(255 * intensity)
            return Color(self.hue, 255, lum)
        else:
            return Color.none()

class Matrix(Animation):
    name        = 'matrix'
    greenHue    = 89

    trails = [
        Trails(8, 8, greenHue),
        Trails(6, 6, greenHue),
        Trails(4, 4, greenHue)
    ]

    def generateColor(self, t, i, c, y):
        return self.combineAnimations(t, i, c, y, Matrix.trails)

class Raining(Animation):
    name    = 'raining'
    rainHue = 135

    trails = [
        Trails(12, 5, rainHue),
        Trails(10, 5, rainHue),
        Trails(8, 4, rainHue)
    ]

    def generateColor(self, t, i, c, y):
        return self.combineAnimations(t, i, c, y, Raining.trails)

class FlashFadeOff(Animation):
    name    = 'flash-fade'

    duration    = 0.6

    def __init__(self, hue):
        self.hue = hue
        self.startTime = time.time()
        self.endTime = self.startTime + FlashFadeOff.duration

    def generateColor(self, t, i, c, y):
        normalisedLum   = max(0, self.endTime - t)
        lum             = int(normalisedLum * 255)

        return Color(self.hue, 255, lum)

class FlashFadeDim(Animation):
    name    = 'flash'

    duration    = 0.6

    def __init__(self, hue):
        self.hue = hue
        self.startTime = time.time()
        self.endTime = self.startTime + FlashFadeDim.duration

    def generateColor(self, t, i, c, y):
        normalisedLum   = max(0, self.endTime - t)
        lum             = int((normalisedLum * 127.5) + 127.5)

        return Color(self.hue, 255, lum)

def getRecursiveSubclasses(class_instance, first_call = True):
    names = {}

    if not first_call:
        names.update([(class_instance.name, class_instance)])

    for subclass in class_instance.__subclasses__():
        names.update(getRecursiveSubclasses(subclass, False))

    return names

animations = getRecursiveSubclasses(Animation)
