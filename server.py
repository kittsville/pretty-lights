import os
import web
import json
import time
import redis
import random
import logging

from helpers import colorTools
from helpers import microcontroller
from helpers.state import State

COLOR_GAP       = 40
SECONDS_TO_IDLE = 60 * 29

# State management
cacheBust   = int(time.time())
r           = redis.Redis(charset="utf-8", decode_responses=True)
r.ping()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

urls = (
    '/', 'homepage',
    '/lights', 'lights',
    '/random', 'randomColor'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

class homepage:
    def GET(self):
        return render.homepage(cacheBust)

class randomColor:
    def POST(self):
        params = web.input()

        onlyOnIdle  = params.get('automated')
        now         = int(time.time())

        state = State.fromRedis(r)

        if onlyOnIdle:
            secondUntilIdle = state.lastModified + SECONDS_TO_IDLE - now

            if secondUntilIdle > 0:
                logging.info(f"Ignoring automated colour request, not idle for another {secondUntilIdle / 60} mins")
                return

        randomHue = random.randint(COLOR_GAP, 255)
        hue = (randomHue + state.lastHue) % 255
        sat = 255
        lum = 255

        led_data = [hue, sat, lum] * 100

        response = microcontroller.sendLedData(led_data)

        newState = State(now, hue)
        newState.save(r)

        return response

class lights:
    def POST(self):
        inputData = json.loads(web.data())

        multiplier  = inputData['multiplier']
        rawColors   = inputData['colors']

        if len(rawColors) == 0:
            raise web.badrequest(f'No colors given')

        colors = list(map(colorTools.Color.fromDict, rawColors))

        if multiplier == 'columns':
            led_data = colorTools.generateLedColumns(colors)
        elif isinstance(multiplier, int):
            led_data = colorTools.generateLedBlocks(colors, multiplier)
        else:
            raise web.badrequest(f'Unknown multiplier "{multiplier}"')

        response = microcontroller.sendLedData(led_data)

        hue             = led_data[0] if len(rawColors) == 1 else 0
        lastModified    = int(time.time())
        newState        = State(lastModified, hue)
        newState.save(r)

        return response

if __name__ == "__main__":
    app.run()
