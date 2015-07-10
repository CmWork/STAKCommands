from StcIntPythonPL import *
import os
import json
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from unit_test_utils import UnitTestUtils


PKG = "spirent.methodology"
PKG_MGR = PKG + ".manager"


def test_get_methodology_manager(stc):
    test_meth_manager = meth_man_utils.get_meth_manager()
    assert test_meth_manager.IsTypeOf("StmMethodologyManager") is True


def test_import_save_delete_bll_object_update(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_import_save_delete_bll_object_update.begin")
    meth_name = "TestMethManUtils"
    meth_key = "UNITTEST_METHMANUTILS"
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    # Clean up empty folder (if existing)
    meth_man_utils.methodology_rmdir(meth_key)

    stak_cmd_name = PKG + ".LoadTemplateCommand"
    stak_cmd = ctor.CreateCommand(stak_cmd_name)

    insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
    insert_cmd.SetCollection("CommandList", [stak_cmd.GetObjectHandle()])
    insert_cmd.Execute()

    exposedConfig = ctor.Create("ExposedConfig", project)

    prop1 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop1, stak_cmd, stak_cmd_name, "CopiesPerParent")

    # Export to a distributable zip file
    cmd = ctor.CreateCommand(PKG_MGR + ".PublishMethodologyCommand")
    cmd.Set("MethodologyName", meth_name)
    cmd.Set("MethodologyKey", meth_key)
    cmd.Set("MinPortCount", "0")
    cmd.Execute()
    cmd.MarkDelete()

    # Reset Config
    cmd = ctor.CreateCommand("ResetConfigCommand")
    cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Update the Methodology Manager
    cmd = ctor.CreateCommand(PKG_MGR + ".UpdateTestMethodologyManagerCommand")
    cmd.Execute()
    cmd.MarkDelete()

    meth_mgr = CStcSystem.Instance().GetObject("StmMethodologyManager")
    assert meth_mgr is not None
    meth_obj = None
    meth_obj_list = meth_mgr.GetObjects("StmMethodology")
    for obj in meth_obj_list:
        if obj.Get("MethodologyKey") == meth_key:
            meth_obj = obj
            break
    assert meth_obj is not None
    assert 0 == len(meth_obj.GetObjects("StmTestCase"))

    # Add a test case
    new_test_case = "MyNewTestCase"
    cmd = ctor.CreateCommand(PKG_MGR + ".CreateTestCaseCommand")
    cmd.Set("TestCaseSrc", meth_obj.GetObjectHandle())
    cmd.Set("TestCaseName", new_test_case)
    cmd.Execute()
    cmd.MarkDelete()

    # Check object update
    test_case_list = meth_obj.GetObjects("StmTestCase")
    assert len(test_case_list) == 1
    found_tc1 = False
    tc_key = None
    for test_case in test_case_list:
        tc_name = test_case.Get("Name")
        if tc_name == new_test_case:
            found_tc1 = True
            tc_key = test_case.Get("TestCaseKey")
    assert found_tc1
    assert tc_key == meth_key + "-1"

    # Check the path
    tc1_path = meth_man_utils.get_test_case_dir(meth_key, tc_key)
    assert os.path.exists(tc1_path)

    # Add a test case
    new_test_case2 = "MyNewTestCase2"
    cmd = ctor.CreateCommand(PKG_MGR + ".CreateTestCaseCommand")
    cmd.Set("TestCaseSrc", meth_obj.GetObjectHandle())
    cmd.Set("TestCaseName", new_test_case2)
    cmd.Execute()
    cmd.MarkDelete()

    # Check object update
    test_case_list = meth_obj.GetObjects("StmTestCase")
    assert len(test_case_list) == 2
    found_tc2 = False
    tc_key = None
    for test_case in test_case_list:
        tc_name = test_case.Get("Name")
        if tc_name == new_test_case2:
            found_tc2 = True
            tc_key = test_case.Get("TestCaseKey")
    assert found_tc2
    assert tc_key == meth_key + "-2"

    # Check the path
    tc1_path = meth_man_utils.get_test_case_dir(meth_key, tc_key)
    assert os.path.exists(tc1_path)

    # Clean up
    cmd = ctor.CreateCommand(PKG_MGR + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth_obj.GetObjectHandle())
    cmd.Execute()

    found_meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
    assert found_meth is None

    # Test empty meth key
    assert meth_man_utils.get_stm_methodology_from_key("") is None


def test_find_file_across_common_paths(stc):
    common_data_path = meth_man_utils.get_common_data_path()

    cleanup_info = UnitTestUtils.create_meth_tree_test_files()
    try:
        p1 = meth_man_utils.find_file_across_common_paths('file1')
        assert p1 == os.path.normpath(os.path.join(common_data_path, 'file1'))

        p2 = meth_man_utils.find_file_across_common_paths('file2')
        assert p2 == os.path.normpath(os.getcwd() + '/file2')

        p3 = meth_man_utils.find_file_across_common_paths('file3')
        assert p3 == ''
        p3 = meth_man_utils.find_file_across_common_paths('file3', True)
        assert p3 == ''
        p3 = meth_man_utils.find_file_across_common_paths('file3', True, True)
        assert p3 == ''

        p4 = meth_man_utils.find_file_across_common_paths('file4')
        assert p4 == ''
        p4 = meth_man_utils.find_file_across_common_paths('file4', False, True)
        assert p4 == ''
        p4 = meth_man_utils.find_template_across_common_paths('file4')
        assert p4 == ''
        p4 = meth_man_utils.find_file_across_common_paths('file4', True, False)
        expected = os.path.normpath(os.path.join(
            common_data_path, mgr_const.MM_SCRIPTS_DIR, 'file4'))
        assert p4 == expected
        p4 = meth_man_utils.find_script_across_common_paths('file4')
        assert p4 == expected

        p5 = meth_man_utils.find_file_across_common_paths('file5')
        assert p5 == ''
        p5 = meth_man_utils.find_file_across_common_paths('file5', False, True)
        expected = os.path.normpath(
            os.path.join(common_data_path, mgr_const.MM_TEMPLATE_DIR, 'file5'))
        assert p5 == expected
        p5 = meth_man_utils.find_template_across_common_paths('file5')
        assert p5 == expected
        p5 = meth_man_utils.find_file_across_common_paths('file5', True, False)
        assert p5 == ''
        p5 = meth_man_utils.find_script_across_common_paths('file5')
        assert p5 == ''
    finally:
        UnitTestUtils.cleanup_meth_tree_test_files(cleanup_info)
    return


def test_find_file_across_common_paths_no_active_meth(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_find_file_across_common_paths_no_active_meth")

    meth_key = "UT_FIND_FILES_TEST_ACTIVE"

    # Clean up empty folders (if existing)
    meth_man_utils.methodology_rmdir(meth_key)

    # Can't use unit_test_utils here to create fake methodologies
    # due to the custom requirements of this particular methodology.
    install_dir = meth_man_utils.get_methodology_home_dir()
    test_meth_dir = os.path.join(install_dir, meth_key)
    assert not os.path.exists(test_meth_dir)
    os.makedirs(test_meth_dir)

    # Add a fake sequence file
    seq_file = os.path.join(test_meth_dir, mgr_const.MM_SEQUENCER_FILE_NAME)
    f = open(seq_file, "w")
    f.write("<?xml version=\"1.0\" encoding=\"windows-1252\"?>")
    f.close()

    # Add a fake TXML file
    meta_file = os.path.join(test_meth_dir, mgr_const.MM_META_FILE_NAME)
    f = open(meta_file, "w")
    data = UnitTestUtils.gen_test_info_header("unit test meth disp name",
                                              meth_key,
                                              "unit test meth test case",
                                              "")
    data = data + UnitTestUtils.UTU_FOOTER
    f.write(data)
    f.close()

    # Add a fake data file
    data_file_name = "fake_data_file.txt"
    data_file_path = os.path.join(test_meth_dir, data_file_name)
    f = open(data_file_path, "w")
    f.write("Unit Test Data File (end)")
    f.close()

    # Initialize the methodology manager by calling update
    cmd = ctor.CreateCommand(PKG_MGR +
                             ".UpdateTestMethodologyManagerCommand")
    cmd.Execute()
    cmd.MarkDelete()

    meth_manager = meth_man_utils.get_meth_manager()

    test_meth_obj_list = meth_manager.GetObjects("StmMethodology")
    assert len(test_meth_obj_list) > 0

    test_meth = None
    for test_meth_obj in test_meth_obj_list:
        act_meth_key = test_meth_obj.Get("MethodologyKey")
        plLogger.LogInfo("meth_name: " + test_meth_obj.Get("Name"))
        plLogger.LogInfo("meth_key: " + test_meth_obj.Get("MethodologyKey"))
        if act_meth_key == meth_key:
            test_meth = test_meth_obj
            break

    assert test_meth is not None

    meth_key = test_meth.Get("MethodologyKey")
    plLogger.LogInfo("meth_name: " + test_meth_obj.Get("Name"))
    plLogger.LogInfo("meth_key: " + test_meth_obj.Get("MethodologyKey"))

    # Check the path
    install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                               mgr_const.MM_TEST_METH_DIR)
    exp_path = os.path.join(install_dir, meth_key)
    assert test_meth.Get("Path") == os.path.normpath(exp_path)

    # Test the find_file_across_common_paths function
    # (no active, not loaded from file)
    active_tc = meth_manager.GetObject("StmTestCase",
                                       RelationType("ActiveStmTestCase"))
    assert active_tc is None

    ret_val = meth_man_utils.find_file_across_common_paths(data_file_name)
    assert ret_val == ""

    # Test the find_file_across_common_paths function
    # (no active, loaded from file)
    project.Set("ConfigurationFileName", seq_file)
    ret_val = meth_man_utils.find_file_across_common_paths(data_file_name)
    assert ret_val == os.path.normpath(data_file_path)

    # Clean up
    cmd = ctor.CreateCommand(PKG_MGR + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", test_meth.GetObjectHandle())
    cmd.Execute()


def test_UpdateMethodologyManagerCommand(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_UpdateMethodologyManagerCommand")

    test_pkg1 = "test_meth_1"
    test_pkg2 = "test_meth_2"
    test_pkg3 = "test_meth_3"
    label_list1 = ["benchmarking", "BGP", "CSMP"]
    label_list2 = ["OTV", "DHCPv6"]
    label_list3 = []

    # Clean up empty folders (if existing)
    meth_man_utils.methodology_rmdir(test_pkg1)
    meth_man_utils.methodology_rmdir(test_pkg2)
    meth_man_utils.methodology_rmdir(test_pkg3)

    UnitTestUtils.create_fake_installed_test_meth(test_pkg1, label_list1)
    UnitTestUtils.create_fake_installed_test_meth(test_pkg2, label_list2)
    UnitTestUtils.create_fake_installed_test_meth(test_pkg3, label_list3)

    # TODO: Uncomment the test case stuff once it's fixed.
    # UnitTestUtils.add_fake_test_case(test_pkg1, "test_case_1")
    # UnitTestUtils.add_fake_test_case(test_pkg1, "test_case_2")
    # UnitTestUtils.add_fake_test_case(test_pkg1, "test_case_3")

    # UnitTestUtils.add_fake_test_case(test_pkg3, "test_case_1")

    # Initialize the methodology manager by calling update
    cmd = ctor.CreateCommand(PKG_MGR + ".UpdateTestMethodologyManagerCommand")
    cmd.Execute()
    cmd.MarkDelete()

    meth_manager = meth_man_utils.get_meth_manager()

    test_meth_obj_list = meth_manager.GetObjects("StmMethodology")
    assert len(test_meth_obj_list) > 0

    meth1 = None
    meth2 = None
    meth3 = None
    for test_meth_obj in test_meth_obj_list:
        meth_key = test_meth_obj.Get("MethodologyKey")
        plLogger.LogInfo("meth_name: " + test_meth_obj.Get("Name"))
        plLogger.LogInfo("meth_key: " + test_meth_obj.Get("MethodologyKey"))
        # test_case_list = []
        label_list = []
        if meth_key == test_pkg1:
            meth1 = test_meth_obj
            # test_case_list = ["test_case_1", "test_case_2",
            #                   "test_case_3", "original"]
            label_list = label_list1
        elif meth_key == test_pkg2:
            meth2 = test_meth_obj
            # test_case_list = ["original"]
            label_list = label_list2
        elif meth_key == test_pkg3:
            meth3 = test_meth_obj
            # test_case_list = ["original", "test_case_1"]
            label_list = label_list3
        else:
            # No need to check this...anything here could be
            # from another unit test or other installed methodologies.
            continue

        # Check the path
        install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                   mgr_const.MM_TEST_METH_DIR)
        exp_path = os.path.join(install_dir, meth_key)
        assert test_meth_obj.Get("Path") == os.path.normpath(exp_path)

        # Check the test cases
        # if len(test_case_list) > 0:
        #     test_case_obj_list = test_meth_obj.GetObjects("StmTestCase")
        #     for test_case_obj in test_case_obj_list:
        #         test_case_name = test_case_obj.Get("TestCaseName")
        #         assert test_case_name in test_case_list
        #         test_case_list.remove(test_case_name)
        #     assert len(test_case_list) == 0

        # Check the labels
        exp_label_list = test_meth_obj.GetCollection("LabelList")
        plLogger.LogInfo("exp_label_list: " + str(exp_label_list))
        plLogger.LogInfo("act_label_list: " + str(label_list))
        assert len(label_list) == len(exp_label_list)
        if len(exp_label_list) > 0:
            for label in label_list:
                plLogger.LogInfo("  -> looking for label: " + str(label))
                assert label in exp_label_list

    assert meth1 is not None
    assert meth2 is not None
    assert meth3 is not None

    # Clean up
    cmd = ctor.CreateCommand(PKG_MGR + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth1.GetObjectHandle())
    cmd.Execute()
    cmd = ctor.CreateCommand(PKG_MGR + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth2.GetObjectHandle())
    cmd.Execute()
    cmd = ctor.CreateCommand(PKG_MGR + ".DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth3.GetObjectHandle())
    cmd.Execute()


def test_active_test_and_result(stc):
    test_pkg1 = "UnitTest_active_pkg_1"
    test_case_1 = "testcase1"

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    mgr = stc_sys.GetObject('StmMethodologyManager')
    assert mgr is not None
    mgr_copy_hnd = meth_man_utils.get_meth_manager().GetObjectHandle()
    assert mgr.GetObjectHandle() == mgr_copy_hnd

    test_meth1 = ctor.Create("StmMethodology", mgr)
    test_meth1.Set('Name', test_pkg1)
    test1 = ctor.Create("StmTestCase", test_meth1)
    test1.Set('Name', test_case_1)
    # test active test
    assert meth_man_utils.get_active_test_case() is None
    meth_man_utils.set_active_test_case(test1)
    assert meth_man_utils.get_active_test_case() is not None
    meth_man_utils.remove_active_test_relation()
    assert meth_man_utils.get_active_test_case() is None
    # test get result
    meth_man_utils.remove_active_test_relation()
    # no active test so create under mgr.
    resultObj1 = meth_man_utils.get_stm_test_result()
    assert resultObj1 is not None
    assert resultObj1.GetParent().GetObjectHandle() == mgr.GetObjectHandle()
    # add active test case
    meth_man_utils.set_active_test_case(test1)
    resultObj2 = meth_man_utils.get_stm_test_result()
    assert resultObj2 is not None
    assert resultObj2.GetObjectHandle() != resultObj1.GetObjectHandle()
    assert resultObj2.GetParent().GetObjectHandle() == test1.GetObjectHandle()
    # remove active test, should return resultObj1
    meth_man_utils.remove_active_test_relation()
    resultObj3 = meth_man_utils.get_stm_test_result()
    assert resultObj3 is not None
    assert resultObj3.GetObjectHandle() == resultObj1.GetObjectHandle()
    # reset manager
    assert test_meth1.IsDeleted() is False
    assert test1.IsDeleted() is False
    assert resultObj1.IsDeleted() is False
    assert resultObj2.IsDeleted() is False
    assert resultObj3.IsDeleted() is False
    meth_man_utils.reset_meth_manager()
    assert test_meth1.IsDeleted() is True
    assert test1.IsDeleted() is True
    assert resultObj1.IsDeleted() is True
    assert resultObj2.IsDeleted() is True
    assert resultObj3.IsDeleted() is True


def test_is_test_case_running(stc):
    ctor = CScriptableCreator()
    mgr = meth_man_utils.get_meth_manager()
    meth = ctor.Create("StmMethodology", mgr)
    tc1 = ctor.Create("StmTestCase", meth)
    tc2 = ctor.Create("StmTestcase", meth)

    # Check both test cases
    res = meth_man_utils.is_test_case_running(tc1)
    assert not res
    res = meth_man_utils.is_test_case_running(tc2)
    assert not res

    # Set one active but not running
    meth_man_utils.set_active_test_case(tc1)
    res = meth_man_utils.is_test_case_running(tc1)
    assert not res
    res = meth_man_utils.is_test_case_running(tc2)
    assert not res

    # Create the results object and set its status
    res_obj = ctor.Create("StmTestResult", tc1)
    status_dict = {"execStatus": "running",
                   "verdict": "created",
                   "verdictExplanation": "Not Defined"}
    res_obj.Set("Status", json.dumps(status_dict))

    res = meth_man_utils.is_test_case_running(tc1)
    assert res
    res = meth_man_utils.is_test_case_running(tc2)
    assert not res

    # Reset status to not running
    status_dict = {"execStatus": "completed",
                   "verdict": "created",
                   "verdictExplanation": "Not Defined"}
    res_obj.Set("Status", json.dumps(status_dict))

    res = meth_man_utils.is_test_case_running(tc1)
    assert not res
    res = meth_man_utils.is_test_case_running(tc2)
    assert not res

    # Remove active testcase
    meth_man_utils.remove_active_test_relation()


def test_get_new_testcase_key(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    mgr = stc_sys.GetObject('StmMethodologyManager')
    assert mgr is not None

    # Test first TestCase
    meth1 = ctor.Create("StmMethodology", mgr)
    meth1.Set("MethodologyKey", "YADAYADA")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth1)
    assert new_tc_key == "YADAYADA-1"

    # Test with gaps
    meth1_tc1 = ctor.Create("StmTestCase", meth1)
    meth1_tc1.Set("TestCaseKey", "YADAYADA-20")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth1)
    assert new_tc_key == "YADAYADA-1"

    meth1_tc2 = ctor.Create("StmTestCase", meth1)
    meth1_tc2.Set("TestCaseKey", "YADAYADA-1")
    meth1_tc3 = ctor.Create("StmTestCase", meth1)
    meth1_tc3.Set("TestCaseKey", "YADAYADA-2")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth1)
    assert new_tc_key == "YADAYADA-3"

    # Validate retrieval of testcase
    tc = meth_man_utils.get_stm_testcase_from_key(meth1, 'YADAYADA-1')
    assert meth1_tc2.GetObjectHandle() == tc.GetObjectHandle()

    tc = meth_man_utils.get_stm_testcase_from_key(meth1, 'YADAYADA-3')
    assert tc is None

    # Test without gaps
    meth1_tc1.Set("TestCaseKey", "YADAYADA-3")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth1)
    assert new_tc_key == "YADAYADA-4"
    meth1_tc4 = ctor.Create("StmTestCase", meth1)
    meth1_tc4.Set("TestCaseKey", "YADAYADA-4")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth1)
    assert new_tc_key == "YADAYADA-5"

    # Test a different meth object (first TestCase)
    meth2 = ctor.Create("StmMethodology", mgr)
    meth2.Set("MethodologyKey", "YADA_SEC")
    new_tc_key = meth_man_utils.get_new_testcase_key(meth2)
    assert new_tc_key == "YADA_SEC-1"
    return


def test_create_new_testcase(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_create_new_testcase")

    # Test empty meth key
    err_msg, tc_key, tc_obj_hnd = meth_man_utils.create_new_testcase("", "")
    assert err_msg == "Methodology key appears to be invalid."
    assert tc_key is None
    assert tc_obj_hnd is None

    # Create a fresh copy of the UnitTestMeth methodology...
    meth_man_utils.methodology_rmdir("UnitTestMeth")
    meth_path = meth_man_utils.methodology_mkdir("UnitTestMeth")
    UnitTestUtils.create_fake_installed_test_meth("UnitTestMeth", [])
    meth_man_utils.build_test_methodology(meth_path, True)

    err_msg, tc_key, tc_obj_hnd = meth_man_utils.create_new_testcase("UnitTestMeth", "tcx")
    assert err_msg == ""
    assert tc_key is not None
    assert tc_obj_hnd is not None

    # Clean up...
    meth_man_utils.methodology_rmdir("UnitTestMeth")
    return
