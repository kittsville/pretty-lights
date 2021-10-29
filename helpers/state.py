import json
import enum
import logging

from helpers.colorTools import Color

class Multiplier(str, enum.Enum):
    NONE                = 'NONE'
    SINGLE_COLOR        = 'SINGLE_COLOR'
    COLUMNS_GRADIENT    = 'COLUMNS_GRADIENT'
    GRADIENT            = 'GRADIENT'
    COLUMNS             = 'COLUMNS'
    REPEATING           = 'REPEATING'

class State:
    @staticmethod
    def fromRedis(r):
        rawState = r.get('pl:state')

        if rawState:
            state = json.loads(rawState)

            lastModified    = state['lastModified']
            colors          = list(map(Color.fromDict, state['colors']))
            multiplier      = state['multipler']
            animation       = state['animation']
        else:
            logging.info('State not found in Redis, initializing state')
            lastModified    = 0
            colors          = [Color.fromHue(255)]
            multiplier      = None
            animation       = None

        return State(lastModified, colors, multiplier, animation)

    def __init__(self, lastModified, colors, multipler, animation = None):
        self.lastModified   = lastModified
        self.colors         = colors
        self.multipler      = multipler
        self.animation      = animation

    def save(self, r):
        state = {
            'lastModified'  : self.lastModified,
            'colors'        : [color.toDict() for color in self.colors],
            'multipler'     : self.multipler,
            'animation'     : self.animation
        }
        rawState = json.dumps(state)
        r.set('pl:state', rawState)
