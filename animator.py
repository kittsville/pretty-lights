import sys
import time
import math
import socket
import logging
import multiprocessing as mp

from helpers import microcontroller, animations

def animationLoop(q):
    sleep = True

    # # Uncomment for testing animations
    # sleep = False
    # animationInstance = animations.Rampant()

    logger = logging.getLogger()

    while True:
        if not q.empty() or sleep: # TODO: Only check every 1/2 second
            animationInstance = q.get() # TODO: get() second time to freeze if given Sleep command
            logger.info(f'Recieved message "{animationInstance}"')

            if animationInstance is None:
                logger.info('Sleeping animation loop...')
                sleep = True
                continue
            else:
                if sleep:
                    logger.info('Waking animation loop...')
                    sleep = False
                logger.info(f'Updating animation to "{animationInstance.__class__.name}"')

        t       = time.time()
        colors  = []

        i = 0

        for c, columnLength in enumerate(microcontroller.LED_COLUMNS):
            for y in range(columnLength):
                relativeY = y if c % 2 == 0 else columnLength - y
                colors.append(animationInstance.generateColor(t, i, c, relativeY))

                i += 1

        try:
            microcontroller.fireAndForgetColors(colors)
        except socket.timeout:
            pass
        time.sleep(1 / animationInstance.fps) # TODO: Scale based on time left

def send(msg):
    address = ('localhost', 6000)

    with mp.connection.Client(address) as conn:
        conn.send(msg)


logging.basicConfig(format='[%(process)s] %(levelname)s: %(message)s', level=logging.INFO)

if __name__ == '__main__':
    address = ('localhost', 6000)
    q       = mp.Queue()
    p       = mp.Process(target=animationLoop, args=(q,))
    p.start()

    with mp.connection.Listener(address) as listener:
        logging.info("Listening for connections...")

        while True:
            with listener.accept() as conn:
                logging.info(f'Connection accepted from {listener.last_accepted}')
                msg = conn.recv()

                logging.info(f'Recieved message "{msg}", sending to animation loop')
                q.put(msg)
                conn.close()
                connectionAlive = False
