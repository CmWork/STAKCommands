from StcIntPythonPL import *
import utils.CommandUtils as CommandUtils
from spirent.core.utils.scriptable import AutoCommand
import utils.json_util as json_util


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


def validate(TrafficFilters, Ports, Drvs, DrvPorts, CallbackInfo):
    return ''


def run(TrafficFilters, Ports, Drvs, DrvPorts, CallbackInfo):
    cb = json_util.loads(CallbackInfo)
    clear_sequencer()
    cmd = create_command_hnd(TrafficFilters, Ports, Drvs, DrvPorts)
    with AutoCommand("SequencerInsertCommand") as seq_insert_cmd:
        seq_insert_cmd.SetCollection("CommandList", [cmd])
        seq_insert_cmd.Execute()
    with AutoCommand("SubscribePropertyChangeCommand") as sub_cmd:
        sub_cmd.Set("PropertyClassId", "sequencer")
        sub_cmd.SetCollection("PropertyIdList", [
            "sequencer.state",
            "sequencer.teststate"
            ])
        sub_cmd.Set("PublishUrl", cb["url"])
        sub_cmd.Set("Context", cb["context"])
        sub_cmd.Execute()
    CommandUtils.set_attribute("StartedCommand", cmd, _get_this_cmd())
    return True


def create_command_hnd(traffic_filters, ports, drvs, drv_ports):
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(
        "spirent.methodology.trafficcenter.CollectResultCommand"
        )
    cmd.SetCollection('TrafficFilters', traffic_filters)
    cmd.SetCollection('Ports', ports)
    cmd.SetCollection('Drvs', drvs)
    cmd.SetCollection('DrvPorts', drv_ports)
    return cmd.GetObjectHandle()


def clear_sequencer():
    with AutoCommand("SequencerClearCommand") as cmd:
        cmd.Set("DoDestroy", True)
        cmd.Execute()


def reset():
    return True
