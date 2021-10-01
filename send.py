import socket
import time

UDP_IP = '192.168.1.56'
UDP_PORT = 12345

colours = []

def genColumn(on, length):
    colours = []

    for _ in range(length):
        hue = 40 # Yellow
        sat = 255
        lum = 255 if on else 0
        colours.extend((hue, sat, lum))

    return colours

columns = [20, 21, 15, 16, 14, 14]

for i, column in enumerate(columns):
    colours += genColumn(True, column)

MESSAGE = b''.join([x.to_bytes(2, byteorder='big') for x in colours])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
print(sock.recv(4))
