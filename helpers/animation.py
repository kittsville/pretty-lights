import time
import math

import microcontroller

FPS = 30

def heartBeat(t, i):
    intensity = (math.sin(t * 2) + 1) / 2
    lum_range = 255 - microcontroller.MIN_LUM

    return [255, 255, int(intensity * lum_range) + microcontroller.MIN_LUM]

def colorRotation(t, i):
    return [int(t * 50 % 255), 255, 255]

def rainbow(t, i):
    return [int(((t * 50) + (i * 10)) % 255), 255, 255]

def rainfall(t, i, c, y):
    intensity = (math.sin(t * 3 - y) + 1) / 2
    lum_range = 255 - microcontroller.MIN_LUM

    return [160, 255, int(intensity * lum_range) + microcontroller.MIN_LUM]

def rainbowColumns(t, i, c, y):
    hueRange = max(microcontroller.LED_COLUMNS)

    return [int(y + t * 4 % (hueRange + 1) / hueRange * 255), 255, 255]

while True:
    t       = time.time()
    ledData = []

    i = 0

    for c, columnLength in enumerate(microcontroller.LED_COLUMNS):
        for y in range(columnLength):
            relativeY = y if c % 2 == 0 else columnLength - y
            ledData.extend(rainfall(t, i, c, relativeY))

            i += 1

    microcontroller.sendLedData(ledData)
    time.sleep(1 / FPS)
