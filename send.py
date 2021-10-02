import socket
import time

UDP_IP = '192.168.1.56'
UDP_PORT = 12345

colours = []

def genColumn(hue, sat, lum, length):
    colours = []

    for _ in range(length):
        colours.extend((hue, sat, lum))

    return colours

columns = [20, 21, 15, 16, 14, 14]

colours.extend(genColumn(0, 99, 89, 20))
colours.extend(genColumn(33, 100, 100, 21))
colours.extend(genColumn(56, 100, 100, 15))
colours.extend(genColumn(138, 100, 50, 16))
colours.extend(genColumn(222, 100, 100, 14))
colours.extend(genColumn(292, 95, 53, 14))

MESSAGE = bytes(colours)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
print(sock.recv(4))
