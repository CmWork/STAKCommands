from StcIntPythonPL import *
from spirent.methodology.results.ResultInterface \
    import ResultInterface as ri
from spirent.methodology.results.ProviderConst \
    import ProviderConst as pc
from spirent.methodology.results.ResultEnum \
    import EnumVerdict


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


# This is the iterator framework's validate base class
def validate(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate IteratorValidateCommand")

    return ""


def run(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run IteratorValidateCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = get_this_cmd()

    # This is bad but there doesn't seem to be any other way of getting
    # the current iterator command handle
    while_cmd = this_cmd.GetParent()
    if while_cmd is not None and while_cmd.IsTypeOf("SequencerWhileCommand"):
        iter_cmd_hnd = while_cmd.Get("ExpressionCommand")
        iter_cmd = hnd_reg.Find(iter_cmd_hnd)
        if iter_cmd is not None and \
           iter_cmd.IsTypeOf("spirent.methodology.IteratorCommand"):
            info_dict = ri.get_last_iteration_info_status(iter_cmd_hnd)
            if info_dict is not None:
                if info_dict[pc.STATUS][pc.VERDICT] == \
                   EnumVerdict.failed:
                    this_cmd.Set("Verdict", False)
                else:
                    # This is for none or passed
                    this_cmd.Set("Verdict", True)
            else:
                plLogger.LogError("ERROR: Failed to determine the " +
                                  "verdict of this iteration")
                # Not too sure what to do here
                this_cmd.Set("Verdict", True)
    else:
        # Set the verdict to True (PASS)
        this_cmd.Set("Verdict", True)

    return True


def reset():

    return True
