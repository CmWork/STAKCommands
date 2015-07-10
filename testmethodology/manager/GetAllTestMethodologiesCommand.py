from StcIntPythonPL import *
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


def validate():
    return ""


def run():
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.GetAllTestMethodologiesCommand")
    hnd_reg = CHandleRegistry.Instance()

    installed_meths = []
    install_dir = meth_man_utils.get_methodology_home_dir()

    meth_man = meth_man_utils.get_meth_manager()
    test_meth_list = meth_man.GetObjects("StmMethodology")
    for test_meth in test_meth_list:
        installed_meths.append(test_meth.GetObjectHandle())

    plLogger.LogDebug("installed_meths: " + str(installed_meths))

    this_cmd = hnd_reg.Find(__commandHandle__)
    this_cmd.SetCollection("StmMethodologyList", installed_meths)
    this_cmd.Set("TestMethodologyDir", str(install_dir))

    plLogger.LogDebug("end.run.GetAllTestMethodologiesCommand")
    return True


def reset():
    return True
