import sys
import time
import math
import socket
import logging
import multiprocessing as mp

from helpers import microcontroller, animations

def animationLoop(q):
    sleep = True

    # Uncomment for testing animations
    sleep = False
    animationClass = animations.HeartBeat()

    while True:
        if not q.empty() or sleep: # TODO: Only check every 1/2 second
            msg = q.get() # TODO: get() second time to freeze if given Sleep command
            print(f'Recieved message "{msg}"')

            if msg == '__sleep':
                print('Sleeping animation loop...')
                sleep = True
                continue
            else:
                print('Waking animation loop...')
                sleep = False
                print(f'Updating animation to "{msg}"')
                animationClass = animations.animations[msg]()

        t       = time.time()
        colors  = []

        i = 0

        for c, columnLength in enumerate(microcontroller.LED_COLUMNS):
            for y in range(columnLength):
                relativeY = y if c % 2 == 0 else columnLength - y
                colors.append(animationClass.generateColor(t, i, c, relativeY))

                i += 1

        try:
            microcontroller.fireAndForgetColors(colors)
        except socket.timeout:
            pass
        time.sleep(1 / animationClass.fps) # TODO: Scale based on time left

def send(msg):
    address = ('localhost', 6000)

    with mp.connection.Client(address) as conn:
        conn.send(msg)
        conn.send('__goodbye')

if __name__ == '__main__':
    address = ('localhost', 6000)
    q       = mp.Queue()
    p       = mp.Process(target=animationLoop, args=(q,))
    p.start()

    with mp.connection.Listener(address) as listener:
        print("Listening for connections...")

        while True:
            with listener.accept() as conn:
                connectionAlive = True

                print('Connection accepted from', listener.last_accepted)
                while connectionAlive:
                    msg = conn.recv()

                    print(f'Recieved message "{msg}"')

                    if msg == '__goodbye':
                        print("Closing connection...")
                        conn.close()
                        connectionAlive = False
                    else:
                        print(f'Sending "{msg}" to animation loop')
                        q.put(msg)
