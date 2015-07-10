from StcIntPythonPL import *
import os.path
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const


def validate(TemplateName):
    if TemplateName == "":
        return "Require TemplateName"
    return ''


def run(TemplateName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.PublishTemplateCommand")
    plLogger.LogDebug("TemplateName name is " + TemplateName)
    ctor = CScriptableCreator()

    install_dir = os.path.join(CStcSystem.Instance().GetApplicationCommonDataPath(),
                               mgr_const.MM_TEST_METH_DIR)
    plLogger.LogDebug("Template directory: " + str(install_dir))
    if not os.path.exists(install_dir):
        plLogger.LogError("Could not find path to the template.")
        return False

    # Save configuration to XML
    save_cmd = ctor.CreateCommand("SaveAsXml")
    save_cmd.Set("FileName", os.path.join(install_dir, TemplateName))
    save_cmd.Execute()

    plLogger.LogDebug("end.run.PublishTemplateCommand")
    return True


def reset():
    return True
