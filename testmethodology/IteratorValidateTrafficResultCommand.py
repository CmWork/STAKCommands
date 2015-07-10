from StcIntPythonPL import *


# This is the iterator framework's validate base class
def validate(Iteration, EnableFrameLossVerification, AcceptableFrameLossPercent,
             EnableDeadStreamVerification, EnableOosVerification,
             AcceptableOosThreshold, EnableLatencyVerification, AcceptableLatencyThreshold):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate IteratorValidateTrafficResultCommand")

    return ""


def run(Iteration, EnableFrameLossVerification, AcceptableFrameLossPercent,
        EnableDeadStreamVerification, EnableOosVerification,
        AcceptableOosThreshold, EnableLatencyVerification, AcceptableLatencyThreshold):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run IteratorValidateTrafficResultCommand")

    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)

    # Call the VerifyTrafficResultCommand
    cmd = ctor.CreateCommand("spirent.methodology.VerifyTrafficResultCommand")
    cmd.Set("enableFrameLossVerification", EnableFrameLossVerification)
    cmd.Set("enableDeadStreamVerification", EnableDeadStreamVerification)
    cmd.Set("enableOosVerification", EnableOosVerification)
    cmd.Set("enableLatencyVerification", EnableLatencyVerification)
    cmd.Set("acceptableOosThreshold", AcceptableOosThreshold)
    cmd.Set("acceptableLatencyThreshold", AcceptableLatencyThreshold)
    cmd.Set("acceptableFrameLossPercent", AcceptableFrameLossPercent)

    cmd.Execute()

    this_cmd.Set("Verdict", cmd.Get("Verdict"))
    return True


def reset():

    return True
