import os
import web
import json
import time
import redis
import logging
import functools

import animator

from helpers import colorTools, microcontroller, animations
from helpers.state import State

from multiprocessing.connection import Client

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
    '/random/(.+)', 'randomColor'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

class homepage:
    def GET(self):
        return render.homepage(cacheBust)

class randomColor:
    def POST(self, type):
        params      = web.input()
        onlyOnIdle  = params.get('automated')
        now         = int(time.time())

        state = State.fromRedis(r)

        if onlyOnIdle:
            secondUntilIdle = state.lastModified + SECONDS_TO_IDLE - now

            if secondUntilIdle > 0:
                logging.info(f"Ignoring automated colour request, not idle for another {secondUntilIdle / 60} mins")
                return

        hue     = colorTools.generateRandomHue(state.lastHue)
        color   = colorTools.Color.fromHue(hue)

        if type == 'single':
            colors = [color] * 100
        elif type == 'columns':
            secondHue   = colorTools.generateRandomHue(hue)
            secondColor = colorTools.Color.fromHue(secondHue)
            colors      = colorTools.generateGradientColumns(color, secondColor)
        elif type == 'gradient':
            secondHue   = colorTools.generateRandomHue(hue)
            secondColor = colorTools.Color.fromHue(secondHue)
            steps       = microcontroller.NUM_LEDS
            colors      = colorTools.generateColorGradient(color, secondColor, steps)
        else:
            raise web.badrequest(f'Unknown type of random display, given "{type}"')

        if state.isAnimation:
            animator.send('__sleep')

        response = microcontroller.sendColors(colors)

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
            ledColors = colorTools.generateLedColumns(colors)
        elif isinstance(multiplier, int):
            ledColors = colorTools.generateLedBlocks(colors, multiplier)
        else:
            raise web.badrequest(f'Unknown multiplier "{multiplier}"')

        oldState = State.fromRedis(r)
        if oldState.isAnimation:
            animator.send('__sleep')

        response = microcontroller.sendColors(ledColors)

        hue             = ledColors[0].hue if len(rawColors) == 1 else 0
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
