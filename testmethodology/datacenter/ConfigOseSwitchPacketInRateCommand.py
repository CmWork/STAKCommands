from StcIntPythonPL import *

logger = PLLogger.GetLogger('methodology')


def validate(ObjectList, TagList, IgnoreEmptyTags, CurrVal, Iteration):
    logger.LogInfo(" Validate ConfigOseSwitchPacketInRateCommand")
    if not ObjectList:
        return 'Invalid OSE Object list cannot be empty'
    oseObjList = CCommandEx.ProcessInputHandleVec('OseSwitchConfig', ObjectList)
    if not oseObjList:
        return 'Invliad ObjectList'
    return ""


def reset():
    return True


def run(ObjectList, TagList, IgnoreEmptyTags, CurrVal, Iteration):
    logger.LogInfo(" Run ConfigOseSwitchPktInRateCommand")
    oseObjList = CCommandEx.ProcessInputHandleVec('OseSwitchConfig', ObjectList)

    logger.LogInfo('Iter: ' + str(Iteration) + 'Current rate: ' + str(CurrVal))
    # Concerned with the 1st object only
    oseTrafficObj = oseObjList[0].GetObject('OseTrafficConfig')
    oseTrafficObj.Set('TrafficFramesPerSecond', CurrVal)

    return True
