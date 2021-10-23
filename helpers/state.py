import json

class State:
    @staticmethod
    def fromRedis(r):
        rawState = r.get('pl:color')

        if rawState:
            state = json.loads(rawState)

            lastModified    = state['lastModified']
            lastHue         = state['lastHue']
        else:
            lastModified    = 0
            lastHue         = 0

        return State(lastModified, lastHue)

    def __init__(self, lastModified, lastHue):
        self.lastModified   = lastModified
        self.lastHue        = lastHue

    def save(self, r):
        state = {
            'lastModified'  : self.lastModified,
            'lastHue'       : self.lastHue
        }
        rawState = json.dumps(state)
        r.set('pl:color', rawState)
