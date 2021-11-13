import logging

from datetime import datetime

DIMMING_FACTOR  = 2
START_HOUR      = 23
END_HOUR        = 6

def dimColorsIfNight(colors):
    now = datetime.now()

    if now.hour >= START_HOUR or now.hour <= END_HOUR:
        logging.info(f"Dimming colors because it is past bedtime")
        colors = list(map(dimColor, colors))

    return colors

def dimColor(color):
    color.lum = int(color.lum / DIMMING_FACTOR)

    return color
