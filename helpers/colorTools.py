import web
import random
import numpy as np

from helpers.microcontroller import LED_COLUMNS, NUM_LEDS

COLOR_GAP = 40

class Color:

    def __init__(self, hue, sat, lum):
        self.hue = hue
        self.sat = sat
        self.lum = lum

    def toList(self):
        return [self.hue, self.sat, self.lum]

    def toDict(self):
        return {
            'hue'   : self.hue,
            'sat'   : self.sat,
            'lum'   : self.lum
        }

    def clone(self):
        return Color(self.hue, self.sat, self.lum)

    def multiplyBy(self, num):
        return [self] + [self.clone() for _ in range(num - 1)]

    def __repr__(self):
        return f'Color(hue: {self.hue}, sat: {self.sat}, lum: {self.lum})'

    @staticmethod
    def fromDict(params):
        hue = getValue(params, 'hue')
        sat = getValue(params, 'sat')
        lum = getValue(params, 'lum')
        return Color(hue, sat, lum)

    @staticmethod
    def fromList(params):
        hue = params[0]
        sat = params[1]
        lum = params[2]
        return Color(hue, sat, lum)

    @staticmethod
    def fromHue(hue):
        sat = 255
        lum = 255

        return Color(hue, sat, lum)

    @staticmethod
    def none():
        return Color(0, 0, 0)


def getValue(params, name):
    if name not in params:
        raise web.badrequest(f'Missing param "{name}" from colour config')
    try:
        value = int(params[name])
    except ValueError:
        raise web.badrequest(f"{name} should be an integer, given {params[name]}")

    if value < 0 or value > 255:
        raise web.badrequest(f"{name} should be 0 <= x <= 255, given {value}")
    return value

def generateRandomDifferentHue(avoidHue):
    randomHue = random.randint(COLOR_GAP, 255)
    hue = (randomHue + avoidHue) % 255

    return hue

def generateRandomHue():
    return random.randint(0, 255)


def generateLedColumns(colors):
    if len(colors) > len(LED_COLUMNS):
        raise web.badrequest(f"Too many colours given, LED lights only have {len(LED_COLUMNS)} columns")
    else:
        columnsPerColor = int(len(LED_COLUMNS) / len(colors))
        remainder = len(LED_COLUMNS) % len(colors)
    ledColors = []

    for i, color in enumerate(colors):
        firstPos    = columnsPerColor * i
        secondPos   = firstPos + columnsPerColor

        numLedsInColumn = sum(LED_COLUMNS[firstPos + remainder:secondPos + remainder])
        if i == 0:
            numLedsInColumn += sum(LED_COLUMNS[i:i + remainder])
        columnColors = color.multiplyBy(numLedsInColumn)
        ledColors.extend(columnColors)

    return ledColors


def generateLedBlocks(colors, multiplier):
    if len(colors) * multiplier > NUM_LEDS:
        raise web.badrequest(f"Multiplier {multiplier} and given colors {len(colors)} greater than number of LEDs {NUM_LEDS}")
    ledColors = []
    while len(ledColors) < NUM_LEDS:
        for color in colors:
            ledColorBlock = color.multiplyBy(multiplier)
            ledColors.extend(ledColorBlock)

    ledColors = ledColors[0:NUM_LEDS]

    return ledColors

def generateGradient(firstNum, secondNum, numElements):
    return map(int, np.linspace(firstNum, secondNum, numElements))

def generateColorGradient(firstColor, secondColor, numElements):
    hueGradient = generateGradient(firstColor.hue, secondColor.hue, numElements)
    satGradient = generateGradient(firstColor.sat, secondColor.sat, numElements)
    lumGradient = generateGradient(firstColor.lum, secondColor.lum, numElements)

    colorGradient = list(map(Color.fromList, zip(hueGradient, satGradient, lumGradient)))

    return colorGradient

def generateGradientColumns(firstColor, secondColor):
    numElements = len(LED_COLUMNS)
    gradient    = generateColorGradient(firstColor, secondColor, numElements)

    colors = []

    for i, color in enumerate(gradient):
        column_colors = color.multiplyBy(LED_COLUMNS[i])

        colors.extend(column_colors)

    return colors
