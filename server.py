import os
import web
import json
import time
import redis
import random
import socket
import logging

UDP_IP          = '192.168.1.56'
UDP_PORT        = 12345
LED_COLUMNS     = [20, 21, 15, 16, 14, 14]
SECONDS_TO_IDLE = 60 * 29
REDIS_COLOR_KEY = 'pl:color'

# State management
cacheBust   = int(time.time())
r           = redis.Redis()
r.ping()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

urls = (
    '/', 'homepage',
    '/lights', 'lights',
    '/random', 'randomColor'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

def getValue(params, name):
    if not name in params:
        raise web.badrequest(f'Missing param "{name}" from colour config')

    try:
        value = int(params[name])
    except ValueError:
        raise web.badrequest(f'{name} should be an integer, given {params[name]}')

    if value < 0 or value > 255:
        raise web.badrequest(f'{name} should be 0 <= x <= 255, given {value}')

    return value

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

        if onlyOnIdle:
            rawLastColorChange  = r.get(REDIS_COLOR_KEY)
            lastColorChange     = int(rawLastColorChange) if rawLastColorChange else 0

            secondUntilIdle = lastColorChange + SECONDS_TO_IDLE - now

            if secondUntilIdle > 0:
                logging.info(f"Ignoring automated colour request, not idle for another {secondUntilIdle / 60} mins")
                return

        hue = random.randint(0, 255)
        sat = 255
        lum = 255

        led_data = [hue, sat, lum] * 100

        response = sendLedData(led_data)

        r.set(REDIS_COLOR_KEY, now)

        return response

class lights:
    def POST(self):
        rawColors = json.loads(web.data())

        if len(rawColors) == 0:
            raise web.badrequest(f'No colors given')
        elif len(rawColors) > len(LED_COLUMNS):
            raise web.badrequest(f'Too many colours given, LED lights only have {len(LED_COLUMNS)} columns')
        else:
            num_color_columns   = int(len(LED_COLUMNS) / len(rawColors))
            remainder           = len(LED_COLUMNS) % len(rawColors)

        led_data = []

        for i, rawColor in enumerate(rawColors):
            hue = getValue(rawColor, 'hue')
            sat = getValue(rawColor, 'sat')
            lum = getValue(rawColor, 'lum')

            num_leds_in_color_column = sum(LED_COLUMNS[i + remainder:i + remainder + num_color_columns])

            if i == 0:
                num_leds_in_color_column += sum(LED_COLUMNS[i:i + remainder])

            column_led_data = [hue, sat, lum] * num_leds_in_color_column

            led_data.extend(column_led_data)

        response = sendLedData(led_data)

        r.set(REDIS_COLOR_KEY, int(time.time()))

        return response

if __name__ == "__main__":
    app.run()
