from StcIntPythonPL import *
from utils.iteration_framework_utils import parse_iterate_mode_input
from utils.iteration_framework_utils import update_results_with_current_value
import spirent.methodology.utils.data_model_utils as dm_utils
import xml.etree.ElementTree as etree


PKG = "spirent.methodology.traffic"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(ObjectList, TagList, IgnoreEmptyTags,
             CurrVal, Iteration, LoadUnit):
    return ''


def run(ObjectList, TagList, IgnoreEmptyTags,
        CurrVal, Iteration, LoadUnit):
    ctor = CScriptableCreator()
    plLogger = PLLogger.GetLogger('methodology')

    # There are two ways to configure load:
    # 1. Streamblock (directly configure)
    # 2. TrafficMix (use the allocate command)

    # Find the Streamblock objects
    sb_list = dm_utils.process_inputs_for_objects(ObjectList, TagList, "StreamBlock")
    # Find the StmTrafficMix objects
    tm_list = dm_utils.process_inputs_for_objects(ObjectList, TagList, "StmTrafficMix")
    # Process the load from CurrVal
    val = parse_iterate_mode_input(CurrVal)
    if val["type"] != "fixed":
        plLogger.LogError("ERROR: Only the fixed load size is " +
                          "currently supported")
        return False
    if LoadUnit == "FRAMES_PER_SECOND" or LoadUnit == "INTER_BURST_GAP":
        try:
            int(val["start"])
        except ValueError:
            plLogger.LogError("ERROR: " + LoadUnit +
                              " requires an integer value")
            return False
    load = val["start"]

    # Configure the TrafficProfile's Load and reallocate to the generated
    # streamblocks (if there are any)
    plLogger.LogInfo("calling AllocateTrafficMixLoad1Command")
    for tm in tm_list:
        # Call AllocateTrafficMixLoad
        set_load_cmd = ctor.CreateCommand(PKG + ".AllocateTrafficMixLoad1Command")
        set_load_cmd.Set("StmTrafficMix", tm.GetObjectHandle())
        set_load_cmd.Set("Load", load)
        set_load_cmd.Set("LoadUnit", LoadUnit)
        set_load_cmd.Execute()
        set_load_cmd.MarkDelete()
        # Keep track of the load that was used for this mix...
        tmi = tm.Get('MixInfo')
        e = etree.fromstring(tmi)
        e.set('Load', load)
        e.set('LoadUnit', LoadUnit)
        tm.Set('MixInfo', etree.tostring(e))

    # Configure the StreamBlocks
    for sb in sb_list:
        sb.Set("Load", val["start"])
        sb.Set("LoadUnit", LoadUnit)

    # Update the results
    this_cmd = get_this_cmd()
    update_results_with_current_value('Load', CurrVal, Iteration, this_cmd)
    return True


def reset():
    return True
