from StcIntPythonPL import *
import os.path
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const


def validate(TemplateName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate.DeleteTemplateCommand")

    if TemplateName == "":
        return "Require TemplateName"

    plLogger.LogDebug("end.validate.DeleteTemplateCommand")
    return ''


def run(TemplateName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.DeleteTemplateCommand")
    plLogger.LogDebug("TemplateName name is " + TemplateName)

    install_dir = os.path.join(CStcSystem.Instance().GetApplicationCommonDataPath(),
                               mgr_const.MM_TEST_METH_DIR)
    full_path = os.path.join(install_dir, TemplateName)
    plLogger.LogDebug("Template file to be deleted: " + str(full_path))
    if not os.path.exists(full_path):
        plLogger.LogError("Could not find the to be deleted template: " + str(full_path))
        return False

    # Delete the xml file
    os.remove(full_path)
    plLogger.LogDebug("end.run.DeleteTemplateCommand")
    return True


def reset():
    return True
