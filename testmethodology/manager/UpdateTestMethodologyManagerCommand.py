from StcIntPythonPL import *
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


def validate(UseTxml):
    return ""


def run(UseTxml):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.UpdateTestMethodologyManagerCommand")

    # FIXME:
    # For now, it is easier to delete all BLL objects and create new ones.  In
    # the future, make this command smarter so it does an updated instead of
    # what it is doing now.  This command should only really be called on init
    # or if the user installs new test methodologies without using the
    # ImportTestCommand.
    meth_man_utils.reset_meth_manager()
    meth_man_utils.build_test_methodology_manager(UseTxml)

    plLogger.LogDebug("end.run.UpdateTestMethodologyManagerCommand")
    return True


def reset():
    return True
