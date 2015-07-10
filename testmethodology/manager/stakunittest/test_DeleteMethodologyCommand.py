from StcIntPythonPL import *
import os
import sys
import json
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from unit_test_utils import UnitTestUtils
sys.path.append(os.path.join(os.getcwd(), "STAKCommands", "spirent", "methodology"))
import manager.DeleteMethodologyCommand as DelCmd


PKG_BASE = "spirent.methodology"
PKG = PKG_BASE + ".manager"


def test_delete_validation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    meth_man = meth_man_utils.get_meth_manager()
    meth = ctor.Create("StmMethodology", meth_man)
    tc1 = ctor.Create("StmTestCase", meth)
    tc2 = ctor.Create("StmTestCase", meth)
    assert tc1
    assert tc2

    # Note that StmMethodologyManager lives under system.
    # ProcessInputHandleVec will return nothing here:
    res = DelCmd.validate(project.GetObjectHandle())
    assert res == "Invalid Test Methodology"

    # ProcessInputHandleVec returns two test cases here:
    res = DelCmd.validate(tc1.GetObjectHandle())
    assert res == "Invalid Test Methodology"

    # Valid case (both checked here to prevent pep8 errors)
    res = DelCmd.validate(meth.GetObjectHandle())
    assert res == ""


def test_reset():
    res = DelCmd.reset()
    assert res is True


def test_delete(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_delete.begin")

    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    meth_key = "UNITTEST_DEL"
    UnitTestUtils.create_fake_installed_test_meth(meth_key, [])

    UnitTestUtils.add_fake_test_case(meth_key, [], meth_key + "-1")
    UnitTestUtils.add_fake_test_case(meth_key, [], meth_key + "-2")

    # Update the BLL objects
    meth_man_utils.build_test_methodology_manager(use_txml=True)
    meth_man = meth_man_utils.get_meth_manager()

    meth_handle = UnitTestUtils.get_methodology_handle(meth_key)
    assert meth_handle
    meth_obj = hnd_reg.Find(meth_handle)
    assert meth_obj is not None
    meth_path = meth_obj.Get("Path")

    tc_obj_list = meth_obj.GetObjects("StmTestCase")
    assert len(tc_obj_list) == 2
    tc_obj1 = None
    tc_obj2 = None
    for tc_obj in tc_obj_list:
        if tc_obj.Get("TestCaseKey") == meth_key + "-1":
            tc_obj1 = tc_obj
        elif tc_obj.Get("TestCaseKey") == meth_key + "-2":
            tc_obj2 = tc_obj
    assert tc_obj1
    tc_obj1_path = tc_obj1.Get("Path")
    assert tc_obj2
    tc_obj2_path = tc_obj2.Get("Path")

    # Delete the installed methodology
    cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth_obj.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the bll object is removed
    found_hnd = False
    for meth in meth_man.GetObjects("StmMethodology"):
        if meth.GetObjectHandle() == meth_handle:
            found_hnd = True
            break
    assert not found_hnd

    # Check the path
    assert not os.path.exists(tc_obj1_path)
    assert not os.path.exists(tc_obj2_path)
    assert not os.path.exists(meth_path)

    stc_sys = CStcSystem.Instance()
    common_data_path = stc_sys.GetApplicationCommonDataPath()
    install_dir = os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR)
    test_meth_dir = os.path.join(install_dir, meth_key)

    assert os.path.exists(test_meth_dir) is False
    plLogger.LogInfo("test_delete.end")


def test_delete_with_active_testcase(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_delete_active_test.begin")

    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    meth_key = "UNITTEST_DEL"
    UnitTestUtils.create_fake_installed_test_meth(meth_key, [])
    UnitTestUtils.add_fake_test_case(meth_key, [], meth_key + "-1")

    # Update the BLL objects
    meth_man_utils.build_test_methodology_manager(use_txml=True)
    meth_man = meth_man_utils.get_meth_manager()

    meth_handle = UnitTestUtils.get_methodology_handle(meth_key)
    assert meth_handle
    meth_obj = hnd_reg.Find(meth_handle)
    assert meth_obj is not None
    meth_path = meth_obj.Get("Path")
    assert os.path.exists(meth_path)

    tc_obj = meth_obj.GetObject("StmTestCase")
    assert tc_obj
    tc_path = tc_obj.Get("Path")
    assert os.path.exists(tc_path)

    # Set up the test case to look as if it were active
    # Set the active test case
    meth_man_utils.set_active_test_case(tc_obj)

    # Create the results object and set its status
    res_obj = ctor.Create("StmTestResult", tc_obj)
    status_dict = {"execStatus": "running",
                   "verdict": "created",
                   "verdictExplanation": "Not Defined"}
    res_obj.Set("Status", json.dumps(status_dict))

    # Try to delete the methodology
    cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth_obj.GetObjectHandle())
    cmd.Execute()
    assert cmd.Get("PassFailState") == "FAILED"
    cmd.MarkDelete()

    # Check the bll objects
    found_hnd = False
    for meth in meth_man.GetObjects("StmMethodology"):
        if meth.GetObjectHandle() == meth_handle:
            found_hnd = True
            break
    assert found_hnd

    # Check the active test case
    assert meth_man_utils.get_active_test_case().GetObjectHandle() == \
        tc_obj.GetObjectHandle()

    # Check the path
    assert os.path.exists(tc_path)
    assert os.path.exists(meth_path)

    # Set the testcase to completed
    status_dict = {"execStatus": "completed",
                   "verdict": "created",
                   "verdictExplanation": "Not Defined"}
    res_obj.Set("Status", json.dumps(status_dict))

    # Try to delete the methodology
    cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth_obj.GetObjectHandle())
    cmd.Execute()
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check the bll objects
    found_hnd = False
    for meth in meth_man.GetObjects("StmMethodology"):
        if meth.GetObjectHandle() == meth_handle:
            found_hnd = True
            break
    assert not found_hnd

    # Check the active test case
    assert meth_man_utils.get_active_test_case() is None

    # Check the path
    assert not os.path.exists(meth_path)
    assert not os.path.exists(tc_path)

    stc_sys = CStcSystem.Instance()
    common_data_path = stc_sys.GetApplicationCommonDataPath()
    install_dir = os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR)
    test_meth_dir = os.path.join(install_dir, meth_key)

    assert os.path.exists(test_meth_dir) is False
    plLogger.LogInfo("test_delete_active_test.end")
