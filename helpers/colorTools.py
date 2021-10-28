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
        return [
         self.hue, self.sat, self.lum]

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

def generateRandomHue(avoidHue):
    randomHue = random.randint(COLOR_GAP, 255)
    hue = (randomHue + avoidHue) % 255

    return hue


def generateLedColumns(colors):
    if len(colors) > len(LED_COLUMNS):
        raise web.badrequest(f"Too many colours given, LED lights only have {len(LED_COLUMNS)} columns")
    else:
        num_color_columns = int(len(LED_COLUMNS) / len(colors))
        remainder = len(LED_COLUMNS) % len(colors)
    ledData = []
    for i, color in enumerate(colors):
        num_leds_in_color_column = sum(LED_COLUMNS[i + remainder:i + remainder + num_color_columns])
        if i == 0:
            num_leds_in_color_column += sum(LED_COLUMNS[i:i + remainder])
        column_ledData = color.toList() * num_leds_in_color_column
        ledData.extend(column_ledData)

    return ledData


def generateLedBlocks(colors, multiplier):
    if len(colors) * multiplier > NUM_LEDS:
        raise web.badrequest(f"Multiplier {multiplier} and given colors {len(colors)} greater than number of LEDs {NUM_LEDS}")
    ledData = []
    while len(ledData) < NUM_LEDS * 3:
        for color in colors:
            color_block_ledData = color.toList() * multiplier
            ledData.extend(color_block_ledData)

    ledData[0:(NUM_LEDS - 1) * 3]
    return ledData

def generateGradient(firstNum, secondNum, numElements):
    return map(int, np.linspace(firstNum, secondNum, numElements))

def generateColorGradient(firstColor, secondColor, numElements):
    hueGradient = generateGradient(firstColor.hue, secondColor.hue, numElements)
    satGradient = generateGradient(firstColor.sat, secondColor.sat, numElements)
    lumGradient = generateGradient(firstColor.lum, secondColor.lum, numElements)

    colorGradient = map(Color.fromList, zip(hueGradient, satGradient, lumGradient))

    return colorGradient

def generateGradientColumns(firstColor, secondColor):
    numElements = len(LED_COLUMNS)
    gradient    = generateColorGradient(firstColor, secondColor, numElements)

    led_data = []

    for i, color in enumerate(gradient):
        column_ledData = color.toList() * LED_COLUMNS[i]

        led_data.extend(column_ledData)

    return led_data
