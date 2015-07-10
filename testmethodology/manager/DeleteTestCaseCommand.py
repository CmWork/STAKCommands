from StcIntPythonPL import *
from utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils


def validate(StmTestCase):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("DeleteTestCaseCommand.validate.begin")

    tc_list = CCommandEx.ProcessInputHandleVec("StmTestCase",
                                               [StmTestCase])
    if len(tc_list) != 1:
        plLogger.LogError("Invalid StmTestCase object")
        return "Invalid Test Case"

    test_case = tc_list[0]
    if test_case is None:
        plLogger.LogError("Was unable to find StmTestCase with " +
                          "handle " + StmTestCase +
                          " in the list of installed test cases.")
        return "Unable to find StmTestCase from handle."

    plLogger.LogDebug("DeleteTestCaseCommand.validate.end")
    return ""


def run(StmTestCase):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("DeleteTestCaseCommand.run.begin")

    tc_list = CCommandEx.ProcessInputHandleVec("StmTestCase",
                                               [StmTestCase])
    if len(tc_list) != 1:
        plLogger.LogError("Invalid StmTestCase object")
        return "Invalid Test Case"

    test_case = tc_list[0]
    if test_case is None:
        plLogger.LogError("Was unable to find StmTestCase with " +
                          "handle " + StmTestCase +
                          " in the list of installed test cases.")
        return False

    # Delete the BLL object but not allow to delete the active test case
    if meth_man_utils.is_test_case_running(test_case):
        plLogger.LogError("Can not delete an actively running test case.")
        return False

    del_test_case_name = test_case.Get('Name')
    plLogger.LogDebug("del_test_case_name: " + del_test_case_name)
    tc_key = test_case.Get("TestCaseKey")

    # Delete the test case from file system
    test_meth = test_case.GetParent()
    if test_meth is None:
        plLogger.LogError("Invalid StmMethodology")
        return False
    test_meth_name = test_meth.Get('Name')
    plLogger.LogDebug("StmMethodology name: " + test_meth_name)
    meth_key = test_meth.Get("MethodologyKey")

    return_value = meth_man_utils.methodology_test_case_rmdir(meth_key,
                                                              tc_key)
    if not return_value:
        plLogger.LogError("Failed to remove test case " + del_test_case_name)
        return False

    test_case.MarkDelete()
    plLogger.LogDebug("DeleteTestCaseCommand.run.end")
    return True


def reset():
    return True
