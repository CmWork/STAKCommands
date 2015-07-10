from StcIntPythonPL import *
import utils.CommandUtils as CommandUtils
import json
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


def validate(TrafficFilter, TargetPort, CallbackInfo):
    return ''


def run(TrafficFilter, TargetPort, CallbackInfo):
    hnd_reg = CHandleRegistry.Instance()

    cb = json.loads(CallbackInfo)
    with AutoCommand("SubscribePropertyChangeCommand") as pushCmd:
        pushCmd.Set("PropertyClassId", "ResultViewData")
        pushCmd.SetCollection("PropertyIdList", ["ResultViewData.ResultData"])
        pushCmd.Set("PublishUrl", str(cb["url"]))
        pushCmd.Set("Context", str(cb["context"]))
        pushCmd.Execute()

    with AutoCommand("CreateDrvFromResultFilterCommand") as createDrvCmd:
        createDrvCmd.Set("CounterResultFilter", TrafficFilter)
        createDrvCmd.SetCollection("RxPortHandleList", [TargetPort])
        createDrvCmd.Execute()
    drvHnd = createDrvCmd.Get("DynamicResultView")
    drv = hnd_reg.Find(drvHnd)
    prq = drv.GetObject('PresentationResultQuery')
    columns = prq.GetCollection("SelectProperties")

    with AutoCommand('subscribeDynamicResultView') as subscribeCmd:
        subscribeCmd.Set('DynamicResultView', drvHnd)
        subscribeCmd.Execute()

    with AutoCommand("TimedRefreshResumeCommand") as refresh_cmd:
        refresh_cmd.Set("DynamicResultView", drvHnd)
        refresh_cmd.Execute()

    CommandUtils.set_attribute("HealthDetailDrv",
                               drvHnd, _get_this_cmd())

    CommandUtils.set_attribute("HealthDetailDrvChild",
                               prq.GetObjectHandle(), _get_this_cmd())

    CommandUtils.set_collection("HealthDetailColumns",
                                columns, _get_this_cmd())

    return True


def reset():
    return True
