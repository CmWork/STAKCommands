from StcIntPythonPL import *
import os
import shutil
import stat
import sys
import json
sys.path.append(os.path.join(os.getcwd(), "STAKCommands"))
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from spirent.methodology.results.ResultEnum import EnumExecStatus
import txml_utils as txml_utils
import meta_utils as meta_utils


class MethodologyManagerUtils:
    @staticmethod
    # Produces a new testcase key for a given methodology
    def create_new_testcase(meth_key, test_case_name=""):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.create_new_testcase.begin")
        # Get the stm meth object from the key...
        meth_obj = MethodologyManagerUtils.get_stm_methodology_from_key(meth_key)
        if meth_obj is None:
            return "Methodology key appears to be invalid.", None, None
        # Generate a new test case key for the methodology...
        tc_key = MethodologyManagerUtils.get_new_testcase_key(meth_obj)
        if tc_key is None or tc_key == "":
            return "Unable to generate a new test case key.", None, None
        # Build out the new test case folder...
        target_dir = MethodologyManagerUtils.methodology_test_case_mkdir(meth_key, tc_key)
        if target_dir is None or target_dir == "":
            return "Unable to create test case folder.", tc_key, None
        source_dir = meth_obj.Get("Path")
        if source_dir is None or source_dir == "":
            return "Methodology path is invalid.", tc_key, None
        # Copy all the default methodology files to the test case folder...
        src_files = os.listdir(source_dir)
        for file_name in src_files:
            full_file_name = os.path.join(source_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, target_dir)
        # Create a new StmTestCase object and fill it out appropriately (as much as we can)...
        ctor = CScriptableCreator()
        test_case = ctor.Create("StmTestCase", meth_obj)
        test_case.Set("Name", test_case_name)
        test_case.Set("TestCaseKey", tc_key)
        test_case.Set("Path", target_dir)
        tc_obj_hnd = test_case.GetObjectHandle()
        plLogger.LogDebug("MethodologyManagerUtils.create_new_testcase.end")
        return "", tc_key, tc_obj_hnd

    @staticmethod
    def get_test_case_from_key(test_case_key):
        if not test_case_key:
            return None, 'test_case_key is empty'

        # Get methodology manager
        meth_man = MethodologyManagerUtils.get_meth_manager()
        if meth_man is None:
            return None, 'Could not get StmMethodologyManager'

        # Get list of methodologies
        test_meth_obj_list = meth_man.GetObjects("StmMethodology")
        if len(test_meth_obj_list) <= 0:
            return None, 'Did not find any installed methodologies'

        # Verify test case exists in one of the installed meths
        for test_meth_obj in test_meth_obj_list:
            test_case = MethodologyManagerUtils.get_stm_testcase_from_key(test_meth_obj,
                                                                          test_case_key)
            if test_case is not None:
                # Found the test case, return the handle
                return test_case.GetObjectHandle(), ''

        return None, 'Test case with key ' + test_case_key + ' not found'

    @staticmethod
    def is_valid_test_meth(test_meth_dir_name, use_txml=False):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.is_valid_test_meth.begin")
        verdict = False
        install_dir = MethodologyManagerUtils.get_methodology_home_dir()
        seq_file = os.path.join(install_dir,
                                test_meth_dir_name,
                                mgr_const.MM_SEQUENCER_FILE_NAME)
        if not use_txml:
            meta_file = os.path.join(install_dir,
                                     test_meth_dir_name,
                                     mgr_const.MM_META_JSON_FILE_NAME)
        else:
            meta_file = os.path.join(install_dir,
                                     test_meth_dir_name,
                                     mgr_const.MM_META_FILE_NAME)
        if os.path.exists(seq_file) and os.path.isfile(seq_file):
            test_meth_key = None
            if os.path.exists(meta_file) and os.path.isfile(meta_file):
                if not use_txml:
                    test_meth_key = \
                        meta_utils.extract_methodology_key_from_file(meta_file)
                else:
                    test_meth_key = \
                        txml_utils.extract_methodology_key_from_file(meta_file)
            if not test_meth_key:
                plLogger.LogWarn("Meta file {} is invalid, skipping"
                                 .format(meta_file))
            else:
                verdict = True
            plLogger.LogDebug("MethodologyManagerUtils.is_valid_test_meth.end")
        return verdict

    @staticmethod
    def get_meth_manager():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_meth_manager.begin")
        stc_sys = CStcSystem.Instance()
        meth_manager = stc_sys.GetObject("StmMethodologyManager")
        if meth_manager is None:
            plLogger.LogError("No StmMethodologyManager found.")
            raise Exception("No StmMethodologyManager found.")
        plLogger.LogDebug("MethodologyManagerUtils.get_meth_manager.end")
        return meth_manager

    @staticmethod
    def reset_meth_manager():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.reset_meth_manager.begin")
        meth_mgr = MethodologyManagerUtils.get_meth_manager()
        objects = meth_mgr.GetObjects('StmMethodology', RelationType('ParentChild'))
        for object in objects:
            object.MarkDelete()
        resultObj = meth_mgr.GetObject('StmTestResult')
        if resultObj is not None:
            resultObj.MarkDelete()
        plLogger.LogDebug("MethodologyManagerUtils.reset_meth_manager.end")

    @staticmethod
    def build_test_methodology(test_meth_path, use_txml=False):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.build_test_methodology.begin")
        if not test_meth_path:
            plLogger.LogError("Invalid methodology path")
            return
        plLogger.LogDebug("test_meth_path: " + str(test_meth_path))
        # First, handle the methodology itself
        meth_man = MethodologyManagerUtils.get_meth_manager()
        if meth_man is None:
            plLogger.LogError("Error finding the methodology manager object")
            return
        ctor = CScriptableCreator()
        test_meth = ctor.Create("StmMethodology", meth_man)
        if test_meth is None:
            plLogger.LogError("Error creating methodology in memory")
            return
        if not use_txml:
            meta_file_path = os.path.join(test_meth_path,
                                          mgr_const.MM_META_JSON_FILE_NAME)
        else:
            meta_file_path = os.path.join(test_meth_path,
                                          mgr_const.MM_META_FILE_NAME)
        plLogger.LogDebug("meta_file_path: {}".format(meta_file_path))
        if not use_txml:
            test_meth_key = meta_utils.extract_methodology_key_from_file(
                meta_file_path)
            test_meth_name = meta_utils.extract_methodology_name_from_file(
                meta_file_path)
            label_list = meta_utils.extract_test_labels_from_file(meta_file_path)
        else:
            test_meth_key = txml_utils.extract_methodology_key_from_file(
                meta_file_path)
            test_meth_name = txml_utils.extract_methodology_name_from_file(
                meta_file_path)
            label_list = txml_utils.extract_test_labels_from_file(meta_file_path)
        if not test_meth_key:
            plLogger.LogError("Could not get methodology key from meta " +
                              "data file")
            return
        test_meth.Set("Name", test_meth_name)
        test_meth.Set("MethodologyKey", test_meth_key)
        test_meth.Set("Path", test_meth_path)
        test_meth.SetCollection("LabelList", label_list)
        # Now handle any test cases.
        test_case_path = os.path.join(test_meth_path,
                                      mgr_const.MM_TEST_CASE_SUBDIR)
        plLogger.LogDebug("test_case_path: " + str(test_case_path))
        if os.path.exists(test_case_path):
            # If the path exists then there might be test cases
            for filename in os.listdir(test_case_path):
                plLogger.LogDebug("process filename: " + str(filename))
                if os.path.isfile(os.path.join(test_case_path, filename)):
                    # skip regular files. We want to process subdirectories.
                    continue
                MethodologyManagerUtils.build_test_case(test_meth,
                                                        os.path.join(test_case_path,
                                                                     filename),
                                                        use_txml)
        else:
            plLogger.LogDebug("No test cases found. Skipping test-case processing.")
        plLogger.LogDebug("MethodologyManagerUtils.build_test_methodology.end")

    @staticmethod
    def build_test_case(test_meth, test_case_path, use_txml=False):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.build_test_case.begin")
        ctor = CScriptableCreator()
        plLogger.LogDebug("add test case for " + str(test_meth) +
                          " with path " + str(test_case_path))
        if not use_txml:
            meta_file_path = \
                os.path.join(test_case_path, mgr_const.MM_META_JSON_FILE_NAME)
        else:
            meta_file_path = \
                os.path.join(test_case_path, mgr_const.MM_META_FILE_NAME)
        if not os.path.isfile(meta_file_path):
            plLogger.LogDebug("No meta file found for {}, skipping"
                              .format(test_case_path))
            return
        if not use_txml:
            test_case_name = meta_utils.extract_test_case_name_from_file(meta_file_path)
            test_case_key = meta_utils.extract_test_case_key_from_file(meta_file_path)
        else:
            test_case_name = txml_utils.extract_test_case_name_from_file(meta_file_path)
            test_case_key = txml_utils.extract_test_case_key_from_file(meta_file_path)
        if test_case_key is None:
            plLogger.LogError("Could not get test case key from meta data")
            return
        plLogger.LogDebug("test_case_name: " + str(test_case_name))
        plLogger.LogDebug("test_case_key: " + str(test_case_key))
        test_case = ctor.Create("StmTestCase", test_meth)
        test_case.Set("Name", test_case_name)
        test_case.Set("TestCaseKey", test_case_key)
        test_case.Set("Path", test_case_path)
        plLogger.LogDebug("MethodologyManagerUtils.build_test_case.end")

    @staticmethod
    def build_test_methodology_manager(use_txml=False):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.build_test_methodology_manager.begin")

        # Make sure the methodology home directory exists
        test_meth_home_dir = MethodologyManagerUtils.get_methodology_home_dir()
        if not os.path.exists(test_meth_home_dir):
            plLogger.LogDebug("No methodology directory. Skip methodology processing.")
            return True

        # If we get here, the directory exists...
        for dirname in os.listdir(test_meth_home_dir):
            if os.path.isfile(dirname):
                continue
            if MethodologyManagerUtils.is_valid_test_meth(dirname, use_txml):
                MethodologyManagerUtils.build_test_methodology(
                    os.path.join(test_meth_home_dir, dirname),
                    use_txml)
        plLogger.LogDebug("MethodologyManagerUtils.build_test_methodology_manager.end")

    @staticmethod
    def get_stm_methodology_from_key(meth_key):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_stm_methodology_from_key.begin")
        if not meth_key:
            return None
        test_meth = None
        stm_man = MethodologyManagerUtils.get_meth_manager()
        if stm_man is not None:
            stm_list = stm_man.GetObjects("StmMethodology")
            for stm in stm_list:
                plLogger.LogDebug("stm key: " + stm.Get("MethodologyKey"))
                if stm.Get("MethodologyKey").lower() == meth_key.lower():
                    test_meth = stm
                    break
        plLogger.LogDebug("MethodologyManagerUtils.get_stm_methodology_from_key.end")
        return test_meth

    @staticmethod
    def get_stm_testcase_from_key(test_meth, tc_key):
        testcase = None
        if test_meth:
            for tc in test_meth.GetObjects('StmTestCase'):
                if tc.Get('TestCaseKey').lower() == tc_key.lower():
                    testcase = tc
                    break
        return testcase

    @staticmethod
    def get_stm_test_result():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_stm_test_result.begin")
        result_parent = MethodologyManagerUtils.get_meth_manager()
        active_test = MethodologyManagerUtils.get_active_test_case()
        if active_test is not None:
            result_parent = active_test
        test_result = result_parent.GetObject('StmTestResult')
        if test_result is None:
            ctor = CScriptableCreator()
            test_result = ctor.Create("StmTestResult", result_parent)
        plLogger.LogDebug("MethodologyManagerUtils.get_stm_test_result.end")
        return test_result

    @staticmethod
    def get_active_test_case():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_active_test_case.begin")
        mgr = MethodologyManagerUtils.get_meth_manager()
        active_tc = mgr.GetObject('StmTestCase',
                                  RelationType('ActiveStmTestCase'))
        plLogger.LogDebug("MethodologyManagerUtils.get_active_test_case.end")
        return active_tc

    @staticmethod
    def set_active_test_case(test_case):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.set_active_test_case.begin")
        if test_case is None:
            plLogger.LogError("Unable to add null test case as active test case.")
            return
        MethodologyManagerUtils.remove_active_test_relation()
        mgr = MethodologyManagerUtils.get_meth_manager()
        mgr.AddObject(test_case, RelationType('ActiveStmTestCase'))
        plLogger.LogDebug('Active test case:' + test_case.Get('Name'))
        plLogger.LogDebug("MethodologyManagerUtils.set_active_test_case.end")

    @staticmethod
    def remove_active_test_relation():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.remove_active_test_relation.begin")
        mgr = MethodologyManagerUtils.get_meth_manager()
        active_test = MethodologyManagerUtils.get_active_test_case()
        if active_test is not None:
            mgr.RemoveObject(active_test, RelationType('ActiveStmTestCase'))
        plLogger.LogDebug("MethodologyManagerUtils.remove_active_test_relation.end")

    @staticmethod
    def is_test_case_running(tc):
        plLogger = PLLogger.GetLogger("methodology")
        active_test = MethodologyManagerUtils.get_active_test_case()
        if not active_test:
            return False
        if active_test.GetObjectHandle() != tc.GetObjectHandle():
            return False
        stm_result = tc.GetObject("StmTestResult")
        if stm_result:
            status_str = stm_result.Get("Status")
            plLogger.LogDebug("StmTestResult Status: " + status_str)
            status_dict = json.loads(status_str)
            if status_dict["execStatus"] == EnumExecStatus.running:
                return True
        return False

    @staticmethod
    def mkdir_helper(HomeDirPath, SubDirName):
        # Use the name that is passed in to create the appropriate
        # directory for the test case files. Returns the full path
        # of the directory.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.mkdir_helper.begin")
        if not HomeDirPath:
            plLogger.LogError("Invalid directory path")
            return ""
        if not SubDirName:
            plLogger.LogError("Invalid subdirectory name")
            return ""

        if not os.path.exists(HomeDirPath):
            os.mkdir(HomeDirPath)

        # Make sure it's there
        if not os.path.exists(HomeDirPath):
            plLogger.LogError("Failed to create the directory " +
                              HomeDirPath)
            return ""

        sub_dir = os.path.join(HomeDirPath, SubDirName)

        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        else:
            plLogger.LogDebug("Create directory " + sub_dir + " already " +
                              "exists.  Using existing directory.")

        # Make sure it's there
        if not os.path.exists(sub_dir):
            plLogger.LogError("Failed to create directory " +
                              sub_dir)
            return ""

        plLogger.LogDebug("MethodologyManagerUtils.mkdir_helper.end")
        return sub_dir

    @staticmethod
    def methodology_mkdir(meth_key):
        # Use the name that is passed in to create the appropriate
        # directory for the methodology files. Returns the full path
        # of the directory.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.methodology_mkdir.begin")
        if not meth_key:
            plLogger.LogError("Invalid methodology key: " + str(meth_key))
            return ""
        test_meth_home_dir = MethodologyManagerUtils.get_methodology_home_dir()
        test_meth_test_dir = MethodologyManagerUtils.mkdir_helper(test_meth_home_dir,
                                                                  meth_key)
        if not test_meth_test_dir:
            plLogger.LogError("Failed to create directory for " + meth_key)
            return ""
        plLogger.LogDebug("MethodologyManagerUtils.methodology_mkdir.end")
        return test_meth_test_dir

    @staticmethod
    def methodology_test_case_mkdir(meth_key, tc_key):
        # Use the name that is passed in to create the appropriate
        # directory for the test case files. Returns the full path
        # of the directory.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.methodology_test_case_mkdir.begin")
        if not tc_key:
            plLogger.LogError("Invalid test case key")
            return ""
        test_case_home_dir = MethodologyManagerUtils.get_test_case_home_dir(meth_key)
        test_case_dir = MethodologyManagerUtils.mkdir_helper(test_case_home_dir,
                                                             tc_key)
        if not test_case_dir:
            plLogger.LogError("Failed to create directory for " + tc_key)
            return ""
        plLogger.LogDebug("MethodologyManagerUtils.methodology_test_case_mkdir.end")
        return test_case_dir

    @staticmethod
    def topology_template_mkdir(TopologyTemplateName):
        # Use the name that is passed in to create the appropriate
        # directory for the topology template files. Returns the full path
        # of the directory.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.topology_template_mkdir.begin")
        if not TopologyTemplateName:
            plLogger.LogError("Invalid topology template name")
            return ""
        topology_template_home_dir = MethodologyManagerUtils.get_topology_template_home_dir()
        topology_template_dir = MethodologyManagerUtils.mkdir_helper(topology_template_home_dir,
                                                                     TopologyTemplateName)
        if not topology_template_dir:
            plLogger.LogError("Failed to create directory for " + TopologyTemplateName)
            return ""
        plLogger.LogDebug("MethodologyManagerUtils.topology_template_mkdir.end")
        return topology_template_dir

    @staticmethod
    def methodology_rmdir(meth_key):
        # Use the name that is passed in to delete the appropriate
        # directory for the methodology files. If the directory does
        # not exist we return true.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.methodology_rmdir.begin")
        if not meth_key:
            plLogger.LogError("Invalid methodology key: " + str(meth_key))
            return False
        test_meth_test_dir = MethodologyManagerUtils.get_methodology_dir(meth_key)
        plLogger.LogDebug("test_meth_test_dir: " + test_meth_test_dir)

        if os.path.exists(test_meth_test_dir):
            plLogger.LogDebug("os.path.exists: " + test_meth_test_dir)
            try:
                shutil.rmtree(test_meth_test_dir)
            except:
                e = sys.exc_info()[0]
                plLogger.LogError("Exception: " + str(e))

        # Verify that it's gone...
        if os.path.exists(test_meth_test_dir):
            plLogger.LogError("Failed to remove directory " +
                              test_meth_test_dir)
            return False

        plLogger.LogDebug("MethodologyManagerUtils.methodology_rmdir.end")
        return True

    @staticmethod
    def methodology_test_case_rmdir(meth_key, tc_key):
        # Use the name that is passed in to delete the appropriate
        # directory for the test case files. If the directory does
        # not exist, we return true.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.methodology_test_case_rmdir.begin")
        if not tc_key:
            plLogger.LogError("Invalid test case key: " + str(tc_key))
            return False
        test_case_dir = MethodologyManagerUtils.get_test_case_dir(
            meth_key, tc_key)

        if os.path.exists(test_case_dir):
            # Create a handler to take care of failures
            # http://stackoverflow.com/questions/21261132/\
            # python-shutil-rmtree-to-remove-readonly-files
            def del_rw(action, name, exc):
                # May not properly remove any nested sub-directories
                mode = os.stat(name)[stat.ST_MODE]
                os.chmod(name, mode | stat.S_IWRITE)
                os.remove(name)
            shutil.rmtree(test_case_dir, onerror=del_rw)

        # Verify that it's gone...
        if os.path.exists(test_case_dir):
            plLogger.LogError("Failed to remove directory " +
                              test_case_dir)
            return False

        plLogger.LogDebug("MethodologyManagerUtils.methodology_test_case_rmdir.end")
        return True

    @staticmethod
    def topology_template_rmdir(TopologyTemplateName):
        # Use the name that is passed in to delete the appropriate
        # directory for the topology template files. If the directory does
        # not exist, we return.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.topology_template_rmdir.begin")
        if not TopologyTemplateName:
            plLogger.LogError("Invalid topology template name")
            return False
        topology_template_dir = \
            MethodologyManagerUtils.get_topology_template_dir(TopologyTemplateName)

        if os.path.exists(topology_template_dir):
            shutil.rmtree(topology_template_dir)

        # Verify that it's gone...
        if os.path.exists(topology_template_dir):
            plLogger.LogError("Failed to remove directory " +
                              topology_template_dir)
            return False

        plLogger.LogDebug("MethodologyManagerUtils.topology_template_rmdir.end")
        return True

    @staticmethod
    def get_methodology_dir(meth_key):
        # Use the name that is passed in to find and return
        # the full path to the directory where the files are stored.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_methodology_dir.begin")
        if not meth_key:
            plLogger.LogError("Invalid methodology key: " + str(meth_key))
            return ""
        test_meth_home_dir = MethodologyManagerUtils.get_methodology_home_dir()
        plLogger.LogDebug("test_meth_home_dir: " + str(test_meth_home_dir))
        plLogger.LogDebug("meth_key: " + str(meth_key))
        meth_dir = os.path.join(test_meth_home_dir, meth_key)
        plLogger.LogDebug("MethodologyManagerUtils.get_methodology_dir.end")
        return meth_dir

    @staticmethod
    def get_test_case_dir(meth_key, tc_key):
        # Use the name that is passed in to find and return
        # the full path to the directory where the files are stored.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_test_case_dir.begin")
        if not tc_key:
            plLogger.LogError("Invalid test case key")
            return ""
        if not meth_key:
            plLogger.LogError("Invalid methodology key")
            return ""
        tc_home_dir = MethodologyManagerUtils.get_test_case_home_dir(meth_key)
        tc_dir = os.path.join(tc_home_dir, tc_key)
        plLogger.LogDebug("MethodologyManagerUtils.get_test_case_dir.end")
        return tc_dir

    @staticmethod
    def get_topology_template_dir(TopologyTemplateName):
        # Use the name that is passed in to find and return
        # the full path to the directory where the files are stored.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_topology_template_dir.begin")
        if not TopologyTemplateName:
            plLogger.LogError("Invalid topology template name")
            return ""
        topo_temp_home_dir = MethodologyManagerUtils.get_topology_template_home_dir()
        topo_temp_dir = os.path.join(topo_temp_home_dir, TopologyTemplateName)
        plLogger.LogDebug("MethodologyManagerUtils.get_topology_template_dir.end")
        return topo_temp_dir

    @staticmethod
    def get_common_data_path():
        cdp = CStcSystem.Instance().GetApplicationCommonDataPath()
        return os.path.normpath(cdp)

    @staticmethod
    def get_methodology_base_dir():
        # Returns the name of the methodology base directory
        common_data_path = MethodologyManagerUtils.get_common_data_path()
        base_path = os.path.join(common_data_path, mgr_const.MM_METHODOLOGY)
        if not os.path.exists(base_path):
            MethodologyManagerUtils.mkdir_helper(common_data_path,
                                                 mgr_const.MM_METHODOLOGY)
        return base_path

    @staticmethod
    def get_methodology_home_dir():
        # Get the name of the methodology packages directory
        common_data_path = MethodologyManagerUtils.get_common_data_path()
        home_path = os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR)

        if not os.path.exists(home_path):
            MethodologyManagerUtils.mkdir_helper(common_data_path,
                                                 mgr_const.MM_TEST_METH_DIR)
        return home_path

    @staticmethod
    def get_test_case_home_dir(meth_key):
        # Get the name of the test case home directory
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("MethodologyManagerUtils.get_test_case_home_dir.begin")
        if not meth_key:
            plLogger.LogError("Invalid methodology key: " + str(meth_key))
            return ""
        meth_path = MethodologyManagerUtils.get_methodology_dir(meth_key)
        plLogger.LogDebug("meth_path: " + str(meth_path))
        if not meth_path:
            plLogger.LogError("Could not find path to methodology " + meth_key)
            return ""
        path = os.path.join(meth_path,
                            mgr_const.MM_TEST_CASE_SUBDIR)
        plLogger.LogDebug("MethodologyManagerUtils.get_test_case_home_dir.end")
        return path

    @staticmethod
    def get_topology_template_home_dir():
        # Get the name of the topology template home directory
        common_data_path = MethodologyManagerUtils.get_common_data_path()
        return os.path.join(common_data_path, mgr_const.MM_TEMPLATE_DIR)

    @staticmethod
    def get_scripts_home_dir():
        # Get the name of the scripts home directory
        common_data_path = MethodologyManagerUtils.get_common_data_path()
        return os.path.join(common_data_path, mgr_const.MM_SCRIPTS_DIR)

    @staticmethod
    def find_script_across_common_paths(file_name):
        return MethodologyManagerUtils.find_file_across_common_paths(file_name, True, False)

    @staticmethod
    def find_template_across_common_paths(file_name):
        return MethodologyManagerUtils.find_file_across_common_paths(file_name, False, True)

    @staticmethod
    def find_file_across_common_paths(file_name,
                                      search_scripts=False,
                                      search_templates=False):
        plLogger = PLLogger.GetLogger("methodology")
        plLogger.LogDebug("MethodologyManagerUtils.find_file_across_common_paths")
        if not file_name or file_name == '':
            plLogger.LogError('Invalid file name "' + (file_name if not None else '') + '".')
            return ''
        project = CStcSystem.Instance().GetObject("Project")

        search_paths = []

        # If there is an active test case then we will use it...
        # If there isn't, search the directory the file is loaded
        # from.  If not running from a saved config...not sure
        # what to do....
        active_test = MethodologyManagerUtils.get_active_test_case()
        if active_test is not None:
            meth_obj = active_test.GetParent()
            search_paths.append(active_test.Get('Path'))
            search_paths.append(meth_obj.Get('Path'))
        else:
            config_file_name = project.Get("ConfigurationFileName")
            if config_file_name != "":
                config_file_path = os.path.dirname(config_file_name)
                if os.path.exists(config_file_path):
                    search_paths.append(config_file_path)

        if search_templates:
            search_paths.append(
                MethodologyManagerUtils.get_topology_template_home_dir())
        if search_scripts:
            search_paths.append(
                MethodologyManagerUtils.get_scripts_home_dir())

        common_data_path = MethodologyManagerUtils.get_common_data_path()
        search_paths.append(common_data_path)

        # For TCL scripts
        client_info = CStcSystem.Instance().GetObject("ClientInfo")
        if client_info:
            client_working_dir = client_info.Get("StartingWorkingDir")
            if client_working_dir:
                search_paths.append(client_working_dir)
        search_paths.append(os.getcwd())

        for path in search_paths:
            abs_file_name = os.path.join(path, file_name)
            plLogger.LogDebug("looking for file as " + str(abs_file_name))
            if os.path.isfile(abs_file_name):
                return os.path.normpath(abs_file_name)
        return ''

    @staticmethod
    # Produces a new testcase key for a given methodology
    def get_new_testcase_key(meth_obj):
        plLogger = PLLogger.GetLogger("methodology")
        plLogger.LogDebug("MethodologyManagerUtils.get_new_testcase_key")
        # Find the next available integer
        int_key = 1
        int_set = set()
        if meth_obj is None:
            plLogger.LogError("Invalid input StmMethodology object")
            return ""
        meth_key = meth_obj.Get("MethodologyKey")
        tc_list = meth_obj.GetObjects("StmTestCase")

        # No test cases
        if len(tc_list) == 0:
            return meth_key + "-1"

        for tc in tc_list:
            try:
                int_set.add(int(tc.Get("TestCaseKey").split("-")[-1]))
            except (ValueError, IndexError):
                # If the result of the split is not an int, we have
                # a non-standard test case key. Ignore it.
                pass

        # int_set may be empty if all the test cases in tc_list didn't have a valid test case key
        # This could happen if a test case is created and the key is not set
        if len(int_set) == 0:
            return meth_key + "-1"

        sorted(int_set)

        # No gaps
        if len(int_set) == max(int_set):
            return meth_key + "-" + str(len(int_set) + 1)

        # Walk the set and find a gap
        i = 1
        for key in int_set:
            if i != key:
                # Found a gap
                int_key = i
                break
            i = i + 1
        new_key = meth_key + "-" + str(int_key)
        plLogger.LogDebug("new key: " + str(new_key))
        return new_key
