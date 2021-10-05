import os
import web
import json
import socket
import logging

UDP_IP      = '192.168.1.56'
UDP_PORT    = 12345
LED_COLUMNS = [20, 21, 15, 16, 14, 14]

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

urls = (
    '/', 'homepage',
    '/lights', 'lights'
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

class homepage:
    def GET(self):
        return render.homepage()

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

        raw_led_data = bytes(led_data)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(raw_led_data, (UDP_IP, UDP_PORT))
        return sock.recv(4)

if __name__ == "__main__":
    app.run()
