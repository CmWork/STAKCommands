from StcIntPythonPL import *
import os
import sys
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mmutils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def log_error(msg):
    get_this_cmd().Set("ErrorMsg", msg)
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogError(msg)


def validate(ScriptFilename, MethodName, TagName, Params):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("RunPyScriptCommand.validate()")

    if ScriptFilename == "":
        return "ScriptFilename property must be defined."

    if script_filename_path(ScriptFilename) == "":
        return "Failed to find file '" + assumed_filename(ScriptFilename) + ".py'"

    if MethodName == "":
        return "MethodName property must be defined."

    return ""


def run(ScriptFilename, MethodName, TagName, Params):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("RunPyScriptCommand.run()")

    file_path = script_filename_path(ScriptFilename)
    if file_path == "":
        plLogger.LogError("ERROR: Failed to find file '" +
                          assumed_filename(ScriptFilename) + ".py'")
        return None

    sys.path.append(file_path)
    # Import the module...
    exec 'import ' + assumed_filename(ScriptFilename)
    # Now reload it in case the author updated the script, we want the
    # latest changes...
    exec 'reload(' + assumed_filename(ScriptFilename) + ')'
    # To avoid PEP error, we need to import here, lest it seem like it
    # was never used...
    exec 'from spirent.methodology.utils.tag_utils ' + \
        'import get_tagged_objects_from_string_names as tagged'
    # Pass control to the method specified...
    exec 'err = ' + assumed_filename(ScriptFilename) + "." + MethodName + \
        '(TagName, tagged([TagName]), Params)'
    # Erase our knowledge of the module...
    exec 'del ' + assumed_filename(ScriptFilename)
    # Be robust, don't assume the author is returning the correct type
    # of return value...
    if err is None:
        err = ""
    err = str(err)

    # If the script returned a string (or anything that resulted in a
    # non empty string), treat it as an error string. If the author messed
    # up, they will see it as an error.
    if err != "":
        log_error(err)
    # Return true if no error, false if an error was recorded...
    return err == ""


def assumed_filename(ScriptFilename):
    return os.path.splitext(ScriptFilename)[0]


def script_filename_path(ScriptFilename):
    file_path = assumed_filename(ScriptFilename) + ".py"
    abs_file_name = mmutils.find_script_across_common_paths(file_path)
    if abs_file_name != '':
        return os.path.split(abs_file_name)[0]
    return ""


def reset():
    return True
