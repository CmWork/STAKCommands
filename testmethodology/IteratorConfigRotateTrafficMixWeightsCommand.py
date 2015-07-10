from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
from utils.iteration_framework_utils import update_results_with_current_value
import spirent.methodology.utils.data_model_utils as dm_utils
import IteratorConfigCommand as base


PKG = "spirent.methodology.traffic"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(ObjectList, CurrVal, Iteration, TagList, IgnoreEmptyTags):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("IteratorConfigRotateTrafficMixWeightsCommand.validate()")

    # Call base class for validation
    res = base.validate(ObjectList, TagList, IgnoreEmptyTags,
                        CurrVal, Iteration)
    if res is not "":
        return res

    return ''


def run(ObjectList, CurrVal, Iteration, TagList, IgnoreEmptyTags):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("IteratorConfigRotateTrafficMixWeightsCommand.run()")

    count = int(CurrVal)

    tml = dm_utils.process_inputs_for_objects(ObjectList, TagList, "StmTrafficMix")
    for tm in tml:
        e = etree.fromstring(tm.Get('MixInfo'))
        # Pull the information we need for this MIX group...
        load = float(e.get('Load'))
        load_unit = e.get('LoadUnit')
        original_weights = e.get('OriginalWeightList')
        if original_weights is None:
            e.set('OriginalWeightList', e.get('WeightList'))
        e.set('WeightList', e.get('OriginalWeightList'))
        tm.Set('MixInfo', etree.tostring(e))

        # The default rotation is to the right, so we need to negate the count to rotate left...
        rotate_weights(-count, tm)

        # Reallocate the load based upon the new weights...
        with AutoCommand('spirent.methodology.traffic.AllocateTrafficMixLoad1Command') as alloc:
            alloc.Set('StmTrafficMix', tm.GetObjectHandle())
            alloc.Set('TagName', '')
            alloc.Set('Load', load)
            alloc.Set('LoadUnit', load_unit)
            alloc.Execute()

    # The configurator must keep the results framework in sync with the iteration framework.
    # What we want to do is pass information to the results framework to let it know that
    # a new iteration is taking place and a meaningful value that it can display.
    this_cmd = get_this_cmd()
    update_results_with_current_value('Non-conformant Streams', count, Iteration, this_cmd)

    return True


def rotate_weights(count, tm):
    tmi = tm.Get('MixInfo')
    e = etree.fromstring(tmi)
    weight_list = e.get('WeightList')
    weights = weight_list.split(' ')

    # If count is the same or more than the length of weights, the result
    # is no change at all in the weights list ordering of weights.
    weights = weights[count:] + weights[:count]
    e.set('WeightList', ' '.join(weights).replace(',', ''))
    tm.Set('MixInfo', etree.tostring(e))


def reset():
    return True
