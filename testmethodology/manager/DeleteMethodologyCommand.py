from StcIntPythonPL import *
from utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils


def validate(StmMethodology):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate.DeleteMethodologyCommand")

    meth_list = CCommandEx.ProcessInputHandleVec("StmMethodology",
                                                 [StmMethodology])
    if len(meth_list) != 1:
        plLogger.LogError("Invalid StmMethodology object")
        return "Invalid Test Methodology"

    meth = meth_list[0]
    if meth is None:
        plLogger.LogError("Was unable to find StmMethodology with " +
                          "handle " + StmMethodology +
                          " in the set of installed methodologies.")
        return "Unable to find StmMethodology from handle"
    plLogger.LogDebug("end.validate.DeleteMethodologyCommand")
    return ""


def run(StmMethodology):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("DeleteMethodologyCommand.run.begin")

    meth_list = CCommandEx.ProcessInputHandleVec("StmMethodology",
                                                 [StmMethodology])
    if len(meth_list) != 1:
        plLogger.LogError("Invalid StmMethodology object")
        return False

    test_meth = meth_list[0]
    if test_meth is None:
        plLogger.LogError("Was unable to find StmMethodology with " +
                          "handle " + StmMethodology +
                          " in the set of installed test cases.")
        return False

    # Do not allow the methodology to be deleted if one of its test
    # cases is currently active (and running)
    active_tc = meth_man_utils.get_active_test_case()
    if active_tc is not None:
        tc_list = test_meth.GetObjects("StmTestCase")
        for tc in tc_list:
            if tc.GetObjectHandle() == active_tc.GetObjectHandle():
                plLogger.LogDebug("Test Methodology " + test_meth.Get("Name") +
                                  " has a current active test case " +
                                  tc.Get("Name") + ".  Checking to see if it" +
                                  " can be deleted.")
                # Check the results to see if the test is still running
                if meth_man_utils.is_test_case_running(tc):
                    plLogger.LogError("Can not delete a methodology with " +
                                      "an actively running test case.")
                    return False
                # Remove the active test case
                meth_man_utils.remove_active_test_relation()
                break

    # Delete the methodology and all configured test cases from
    # the file system
    if meth_man_utils.methodology_rmdir(test_meth.Get("MethodologyKey")):
        plLogger.LogDebug("Successfully deleted " + test_meth.Get("Name") +
                          " from disk")
    else:
        plLogger.LogError("Failed to delete " + test_meth.Get("Name") +
                          " from disk")
        return False

    # Delete the methodology object
    test_meth.MarkDelete()

    plLogger.LogDebug("DeleteMethodologyCommand.run.end")
    return True


def reset():
    return True
