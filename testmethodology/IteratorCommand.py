from StcIntPythonPL import *


# This is the iterator framework's iterator base class
def validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate IteratorCommand")

    return ''


def run(BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run IteratorCommand")

    return True


def reset():

    return True
