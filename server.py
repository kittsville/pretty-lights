import os
import web
import json
import time
import redis
import logging
import functools

import animator

from helpers import colorTools, microcontroller, animations, dimmer
from helpers.state import State, Multiplier

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
    '/random/(.+)', 'randomColor',
    '/state', 'ledState',
    '/lock', 'lock'
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

            if state.lockedBy:
                logging.info(f"Ignoring automated colour request, colours locked by {state.lockedBy}")
                return web.NotModified()

            if secondUntilIdle > 0:
                logging.info(f"Ignoring automated colour request, not idle for another {secondUntilIdle / 60} mins")
                return web.NotModified()

        hue     = colorTools.generateRandomDifferentHue(state.colors[0].hue) if len(state.colors) > 0 else colorTools.generateRandomHue()
        color   = colorTools.Color.fromHue(hue)

        if type == 'single':
            colors = [color] * 100

            newState = State(now, [color], Multiplier.SINGLE_COLOR)
        elif type == 'columns':
            secondHue   = colorTools.generateRandomDifferentHue(hue)
            secondColor = colorTools.Color.fromHue(secondHue)
            colors      = colorTools.generateGradientColumns(color, secondColor)

            newState = State(now, [color, secondColor], Multiplier.COLUMNS_GRADIENT)
        elif type == 'gradient':
            secondHue   = colorTools.generateRandomDifferentHue(hue)
            secondColor = colorTools.Color.fromHue(secondHue)
            steps       = microcontroller.NUM_LEDS
            colors      = colorTools.generateColorGradient(color, secondColor, steps)

            newState = State(now, [color, secondColor], Multiplier.GRADIENT)
        else:
            raise web.badrequest(f'Unknown type of random display, given "{type}"')

        animator.send('__sleep')

        response = microcontroller.sendColors(dimmer.dimColorsIfNight(colors))

        newState.save(r)

        return response

class lights:
    def POST(self):
        inputData = json.loads(web.data())

        multiplier  = inputData['multiplier']
        rawColors   = inputData['colors']

        if len(rawColors) == 0:
            raise web.badrequest('No colors given')

        colors  = list(map(colorTools.Color.fromDict, rawColors))
        now     = int(time.time())

        if multiplier == 'columns':
            ledColors   = colorTools.generateLedColumns(colors)
            newState    = State(now, colors, Multiplier.COLUMNS)
        elif isinstance(multiplier, int):
            ledColors   = colorTools.generateLedBlocks(colors, multiplier)
            newState    = State(now, colors, Multiplier.REPEATING)
        else:
            raise web.badrequest(f'Unknown multiplier "{multiplier}"')

        oldState = State.fromRedis(r)
        animator.send('__sleep')

        response = microcontroller.sendColors(dimmer.dimColorsIfNight(ledColors))

        newState.save(r)

        return response

class animation:
    def POST(self, name):
        if not name in animations.animations:
            animationNames = ", ".join(animations.animations.keys())
            raise web.badrequest(f'No animation found with name "{name}". Available: {animationNames}')

        animator.send(name)

        lastModified    = int(time.time())
        newState        = State(lastModified, [], Multiplier.NONE, name)
        newState.save(r)

class ledState:
    def GET(self):
        # Blah blah blah API boundaries
        return r.get(State.REDIS_KEY)

class lock:
    def POST(self):
        state           = State.fromRedis(r)
        state.lockedBy  = web.ctx['ip']

        state.save(r)

        return web.Created()

    def DELETE(self):
        state           = State.fromRedis(r)
        state.lockedBy  = None

        state.save(r)

        return web.NoContent()

if __name__ == "__main__":
    app.run()
