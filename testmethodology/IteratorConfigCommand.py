from StcIntPythonPL import *


# This is the iterator framework's config base class
def validate(ObjectList, TagList, IgnoreEmptyTags, CurrVal, Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate IteratorConfigCommand")

    return ""


def run(ObjectList, TagList, IgnoreEmptyTags, CurrVal, Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run IteratorConfigCommand")

    return True


def reset():

    return True
