import socket

LED_COLUMNS = [20, 21, 15, 16, 14, 14]
NUM_LEDS    = sum(LED_COLUMNS)
UDP_IP      = '192.168.1.56'
UDP_PORT    = 12345
MIN_LUM     = 36

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)

def fireAndForgetLedData(ledData):
    expectedBytes = NUM_LEDS * 3
    if len(ledData) != expectedBytes:
        raise ValueError(f'Expected {expectedBytes} bytes, got {len(ledData)}')

    rawLedData = bytes(ledData)

    sock.sendto(rawLedData, (UDP_IP, UDP_PORT))

def sendLedData(ledData):
    fireAndForgetLedData(ledData)

    return sock.recv(4)
