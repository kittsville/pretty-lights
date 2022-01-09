import socket

LED_COLUMNS = [20, 21, 14, 16, 14, 14]
NUM_LEDS    = sum(LED_COLUMNS)
UDP_IP      = '192.168.1.56'
UDP_PORT    = 12345
MIN_LUM     = 36

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)

def fireAndForgetColors(colors):
    if len(colors) != NUM_LEDS:
        raise ValueError(f'Given {len(colors)} colors, LED strip has {NUM_LEDS} LEDs')

    ledData = []

    for color in colors:
        ledData.extend(color.toList())

    rawLedData = bytes(ledData)

    sock.sendto(rawLedData, (UDP_IP, UDP_PORT))

def sendColors(colors):
    fireAndForgetColors(colors)

    return sock.recv(4)
