from StcIntPythonPL import *
import spirent.methodology.utils.iteration_framework_utils as iter_utils
from spirent.methodology.results.ResultInterface import ResultInterface


def validate(ObjectList):
    # Check that the group contains at least one each of the SequencerWhileCommand,
    # IteratorCommand, and IteratorConfigCommand.
    # Sequence may also have a IteratorValidateCommand and nested IterationGroupCommands.

    # Let the command execution order handle IterationGroups rather than trying to
    # recursively check here.
    return ""


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def run(ObjectList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run IterationGroupCommand")

    this_cmd = get_this_cmd()

    # Build property chains
    iter_utils.build_iteration_group_property_chains(this_cmd)

    return True


def on_complete(failed_commands):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("on_complete")

    # call result end iterator
    ResultInterface.end_iterator()
    return True


def reset():
    return True
