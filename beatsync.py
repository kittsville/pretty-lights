import json
import time
import sys

import animator

from helpers import colorTools, microcontroller, animations
from helpers.colorTools import Color
from multiprocessing.connection import Client

levelDirectory = sys.argv[1]
infoFilePath   = levelDirectory + 'info.dat'

with open(infoFilePath) as infoFile:
    info = json.load(infoFile)

standardLevels      = next((level for level in info['_difficultyBeatmapSets'] if level['_beatmapCharacteristicName'] == 'Standard'))
levelMetadata       = next((level for level in standardLevels['_difficultyBeatmaps'] if level['_difficulty'] == 'ExpertPlus'))
levelInfoFilePath   = f"{levelDirectory}/{levelMetadata['_beatmapFilename']}"

with open(levelInfoFilePath) as levelInfoFile:
    levelInfo = json.load(levelInfoFile)

# https://bsmg.wiki/mapping/map-format.html#events-2
lightingEvents  = sorted([event for event in levelInfo['_events'] if event['_type'] == 0], key = lambda event: event['_time'])


print("Get ready")
time.sleep(2)
print("Play!")

beatsPerSecond  = 60.0 / info['_beatsPerMinute']
startTime       = time.time()

for event in lightingEvents:
    timeSinceStart = time.time() - startTime
    timeUntilEvent = max(0, (event['_time'] * beatsPerSecond) - timeSinceStart)

    time.sleep(timeUntilEvent)

    if event['_value'] == 0:
        animator.send(None)
        ledColors = colorTools.generateLedColumns([Color(255, 255, 127)])
        microcontroller.sendColors(ledColors)
    elif event['_value'] == 2:
        animator.send(animations.FlashFadeDim(135))
    elif event['_value'] == 3:
        animator.send(animations.FlashFadeOff(135))
    elif event['_value'] == 5:
        animator.send(None)
        ledColors = colorTools.generateLedColumns([Color(255, 255, 127)])
        microcontroller.sendColors(ledColors)
    elif event['_value'] == 6:
        animator.send(animations.FlashFadeDim(255))
    elif event['_value'] == 7:
        animator.send(animations.FlashFadeOff(255))
    else:
        print(f"Unsupported event value {event['_value']}")

    print(event)


# Shut up and Dance contains _values:
# 0, 1, 3, 5, 7

# 0 	Turns the light group off.
# 1 	Changes the lights to blue, and turns the lights on.
# 2 	Changes the lights to blue, and flashes brightly before returning to normal.
# 3 	Changes the lights to blue, and flashes brightly before fading to black.
# 5 	Changes the lights to red, and turns the lights on.
# 6 	Changes the lights to red, and flashes brightly before returning to normal.
# 7 	Changes the lights to red, and flashes brightly before fading to black.
