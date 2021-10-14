import os
import web
import json
import time
import redis
import random
import socket
import logging

from helpers import colorTools

UDP_IP          = '192.168.1.56'
UDP_PORT        = 12345
COLOR_GAP       = 40
LED_COLUMNS     = [20, 21, 15, 16, 14, 14]
SECONDS_TO_IDLE = 60 * 29
REDIS_COLOR_KEY = 'pl:color'

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

def sendLedData(led_data):
    raw_led_data = bytes(led_data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(raw_led_data, (UDP_IP, UDP_PORT))
    return sock.recv(4)

class homepage:
    def GET(self):
        return render.homepage(cacheBust)

class randomColor:
    def POST(self):
        params = web.input()

        onlyOnIdle  = params.get('automated')
        now         = int(time.time())

        rawLastColor    = r.get(REDIS_COLOR_KEY)
        rawLastColor    = rawLastColor if rawLastColor else b'0,0'

        (lastColourTimestamp, lastColour) = [int(x) for x in rawLastColor.split(',')]

        if onlyOnIdle:
            secondUntilIdle = lastColourTimestamp + SECONDS_TO_IDLE - now

            if secondUntilIdle > 0:
                logging.info(f"Ignoring automated colour request, not idle for another {secondUntilIdle / 60} mins")
                return

        foundColor = False
        while (not foundColor):
            hue         = random.randint(0, 255)
            foundColor  = abs(hue - lastColour) > COLOR_GAP

        sat = 255
        lum = 255

        led_data = [hue, sat, lum] * 100

        response = sendLedData(led_data)

        r.set(REDIS_COLOR_KEY, f'{now},{hue}')

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
            led_data = colorTools.generateColoursFromColumns(colors, LED_COLUMNS)
        else:
            raise web.badrequest(f'Unknown multiplier "{multiplier}"')

        response = sendLedData(led_data)

        hue = led_data[0] if len(rawColors) == 1 else 0
        r.set(REDIS_COLOR_KEY, f'{int(time.time())},{hue}')

        return response

if __name__ == "__main__":
    app.run()
