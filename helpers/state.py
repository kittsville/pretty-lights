import json

class State:
    @staticmethod
    def fromRedis(r):
        rawState = r.get('pl:state')

        if rawState:
            state = json.loads(rawState)

            lastModified    = state['lastModified']
            lastHue         = state['lastHue']
            isAnimation     = state['isAnimation']
        else:
            lastModified    = 0
            lastHue         = 0
            isAnimation     = False

        return State(lastModified, lastHue, isAnimation)

    def __init__(self, lastModified, lastHue, isAnimation):
        self.lastModified   = lastModified
        self.lastHue        = lastHue
        self.isAnimation    = isAnimation

    def save(self, r):
        state = {
            'lastModified'  : self.lastModified,
            'lastHue'       : self.lastHue,
            'isAnimation'   : self.isAnimation
        }
        rawState = json.dumps(state)
        r.set('pl:state', rawState)
