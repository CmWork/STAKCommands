from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


def _get_this_cmd():
    '''
    Get this Command instance from the
    HandleRegistry for setting output properties,
    status, progress, etc.
    '''
    hndReg = CHandleRegistry.Instance()
    try:
        thisCommand = hndReg.Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand


def validate(HealthDetailDrv):
    hndReg = CHandleRegistry.Instance()
    drv = hndReg.Find(HealthDetailDrv)
    if drv is None:
        return "Invalid DRV handle"
    return ''


def run(HealthDetailDrv):
    with AutoCommand('unsubscribeDynamicResultView') as unsubscribeCmd:
        unsubscribeCmd.Set('DynamicResultView', HealthDetailDrv)
        unsubscribeCmd.Execute()
    hndReg = CHandleRegistry.Instance()
    drv = hndReg.Find(HealthDetailDrv)
    drv.MarkDelete()
    return True


def reset():
    return True
