from StcIntPythonPL import *
import time


def validate(EventName):
    if EventName == "":
        return "Event Name must not be blank"
    return ""


def run(EventName):
    plLogger = PLLogger.GetLogger('methodology')
    key = 'spirent.methodology.sampling'
    if not CObjectRefStore.Exists(key):
        err = "Sampling system not properly initialized"
        plLogger.LogError(err)
        raise RuntimeError(err)
    sampDict = CObjectRefStore.Get('spirent.methodology.sampling')
    if 'Event' not in sampDict:
        sampDict['Event'] = []
    # Everything in python is by reference, so we can modify this
    evList = sampDict['Event']
    idx = 0
    # Not very efficient, possibly need to make a map, but linear should be
    # fine for most cases
    for evTup in evList:
        if EventName == evTup[0]:
            idx += 1
    evList.append((EventName, idx, int(time.time())))
    return True


def reset():
    return True
