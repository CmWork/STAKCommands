from StcIntPythonPL import *


def validate_command_on_disk(fileName):

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate_command_on_disk.validator")
    ctor = CScriptableCreator()

    validate_cmd = ctor.CreateCommand("spirent.methodology."
                                      "manager.ValidateTestCompatibleCommand")

    validate_cmd.Set("fileName", fileName)
    validate_cmd.Execute()
    res = validate_cmd.Get("PassFailState")

    if str(res) == "FAILED":
        plLogger.LogError("Test is not compatible with the current STC version.")
        return False

    plLogger.LogDebug("end.validate_command_on_disk.validator")
    return True