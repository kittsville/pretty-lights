import os
import web
import socket
import logging

UDP_IP = '192.168.1.56'
UDP_PORT = 12345

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

urls = (
    '/', 'homepage',
    '/lights', 'lights'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

def getValue(params, name):
    if not hasattr(params, name):
        raise web.badrequest(f'Missing URL param "{name}"')

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
        params = web.input()

        hue = getValue(params, 'hue')
        sat = getValue(params, 'sat')
        lum = getValue(params, 'lum')

        colours = [hue, sat, lum] * 100
        MESSAGE = bytes(colours)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        return sock.recv(4)

if __name__ == "__main__":
    app.run()
