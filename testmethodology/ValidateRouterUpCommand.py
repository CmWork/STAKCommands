from StcIntPythonPL import *


# This is the iterator framework's validate base class
def validate(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate ValidateRouterUpCommand")

    return ""


def run(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run ValidateRouterUpCommand")

    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)

    # Call the VerifyTrafficResultCommand
    cmd = ctor.CreateCommand("VerifyRouterUpCommand")

    cmd.Execute()

    if cmd.Get("PassFailState") == "FAILED":
        this_cmd.Set("Verdict", False)
    else:
        this_cmd.Set("Verdict", True)
    return True


def reset():

    return True
