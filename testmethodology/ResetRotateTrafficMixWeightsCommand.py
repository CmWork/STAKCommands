from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import spirent.methodology.utils.data_model_utils as dm_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(ObjectList, TrafficMixTagList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("ResetRotateTrafficMixWeightsCommand.validate()")
    return ''


def run(ObjectList, TrafficMixTagList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("ResetRotateTrafficMixWeightsCommand.run()")

    tml = dm_utils.process_inputs_for_objects(ObjectList, TrafficMixTagList, "StmTrafficMix")
    for tm in tml:
        e = etree.fromstring(tm.Get('MixInfo'))
        # Pull the information we need for this MIX group...
        load = float(e.get('Load'))
        load_unit = e.get('LoadUnit')

        # If the weights have not been rotated yet, then nothing to do...
        original_weights = e.get('OriginalWeightList')
        if original_weights is None:
            continue

        # Set back to the original weight list...
        e.set('WeightList', e.get('OriginalWeightList'))
        tm.Set('MixInfo', etree.tostring(e))

        # Reallocate the load based upon the new weights...
        with AutoCommand('spirent.methodology.traffic.AllocateTrafficMixLoad1Command') as alloc:
            alloc.Set('StmTrafficMix', tm.GetObjectHandle())
            alloc.Set('TagName', '')
            alloc.Set('Load', load)
            alloc.Set('LoadUnit', load_unit)
            alloc.Execute()

    return True


def reset():
    return True