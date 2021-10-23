import socket

LED_COLUMNS = [20, 21, 15, 16, 14, 14]
NUM_LEDS    = sum(LED_COLUMNS)
UDP_IP      = '192.168.1.56'
UDP_PORT    = 12345
sock        = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendLedData(led_data):
    raw_led_data = bytes(led_data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(raw_led_data, (UDP_IP, UDP_PORT))
    return sock.recv(4)
