import os
import web
import json
import time
import redis
import random
import logging

import animator

from helpers import colorTools, microcontroller, animations
from helpers.state import State

from multiprocessing.connection import Client

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
    '/animations/(.+)', 'animation',
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

        ledData = [hue, sat, lum] * 100

        if state.isAnimation:
            animator.send('__sleep')
        response = microcontroller.sendLedData(ledData)

        isAnimation = False
        newState    = State(now, hue, isAnimation)
        newState.save(r)

        return response

class lights:
    def POST(self):
        inputData = json.loads(web.data())

        multiplier  = inputData['multiplier']
        rawColors   = inputData['colors']

        if len(rawColors) == 0:
            raise web.badrequest('No colors given')

        colors = list(map(colorTools.Color.fromDict, rawColors))

        if multiplier == 'columns':
            ledData = colorTools.generateLedColumns(colors)
        elif isinstance(multiplier, int):
            ledData = colorTools.generateLedBlocks(colors, multiplier)
        else:
            raise web.badrequest(f'Unknown multiplier "{multiplier}"')

        oldState = State.fromRedis(r)
        if oldState.isAnimation:
            animator.send('__sleep')

        response = microcontroller.sendLedData(ledData)

        hue             = ledData[0] if len(rawColors) == 1 else 0
        lastModified    = int(time.time())
        isAnimation     = False
        newState        = State(lastModified, hue, isAnimation)
        newState.save(r)

        return response

class animation:
    def POST(self, name):
        if not name in animations.animations:
            animationNames = ", ".join(animations.animations.keys())
            raise web.badrequest(f'No animation found with name "{name}". Available: {animationNames}')

        animator.send(name)

        hue             = 0
        lastModified    = int(time.time())
        isAnimation     = True
        newState        = State(lastModified, hue, isAnimation)
        newState.save(r)

if __name__ == "__main__":
    app.run()
