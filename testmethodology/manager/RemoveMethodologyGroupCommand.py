from StcIntPythonPL import *
from utils.sequencer_utils import MethodologyGroupCommandUtils as tlgc_utils


def validate():
    return ''


def run():
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.RemoveMethodologyGroupCommand")
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # Removes the MethodologyGroupCommand and makes everything else writable.
    # Assumes that the MethodologyGroupCommand is at the outermost command
    # level in the sequencer (not nested in anything)
    tlgc_utils.remove_top_level_group_command()
    tlgc_utils.set_sequenceable_properties(
        sequencer.GetCollection("CommandList"), True)

    plLogger.LogDebug("end.run.RemoveMethodologyGroupCommand")
    return True


def reset():
    return True
