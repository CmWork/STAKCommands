from StcIntPythonPL import *
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(MethodologyKey, TestCaseKey):
    if not MethodologyKey:
        return "Methodology key can not be blank"
    return ""


def run(MethodologyKey, TestCaseKey):
    plLogger = PLLogger.GetLogger('methodology')
    test_meth = meth_man_utils.get_stm_methodology_from_key(MethodologyKey)
    if not test_meth:
        plLogger.LogError("No methodology with key " + MethodologyKey +
                          " exists")
        return False
    this_cmd = get_this_cmd()
    this_cmd.Set('StmMethodology', test_meth.GetObjectHandle())
    if not TestCaseKey:
        return True
    testcase = meth_man_utils.get_stm_testcase_from_key(test_meth,
                                                        TestCaseKey)
    if testcase:
        this_cmd.Set('StmTestCase', testcase.GetObjectHandle())
    else:
        plLogger.LogError("No test case with key " + TestCaseKey +
                          " exists for " + MethodologyKey)
        return False
    return True


def reset():
    return True
