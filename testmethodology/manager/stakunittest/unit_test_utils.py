from StcIntPythonPL import *
import os
from ..utils.txml_utils import get_unique_property_id
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from ..utils.txml_utils import MetaManager as meta_man


class UnitTestUtils:
    UTU_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><test>"
    UTU_FOOTER = "</testInfo></test>"

    @staticmethod
    def gen_test_info_header(disp_name, meth_key, tc_name, tc_key):
        return UnitTestUtils.UTU_HEADER + \
            "<" + meta_man.TEST_INFO + " " + \
            meta_man.TI_DISPLAY_NAME + "=\"" + disp_name + "\" " + \
            meta_man.TI_DESCRIPTION + "=\"test description\" " + \
            meta_man.TI_KEY + "=\"" + meth_key + "\" " + \
            meta_man.TI_TEST_CASE_NAME + "=\"" + tc_name + "\" " + \
            meta_man.TI_VERSION + "=\"1.0\" " + \
            meta_man.TI_TEST_CASE_KEY + "=\"" + tc_key + "\">"

    @staticmethod
    def delete_test(file_name):
        # os.remove will fail if the file doesn't exist... So...
        try:
            os.remove(file_name)
        except OSError:
            pass

    @staticmethod
    def bind(expose_prop, scriptable, cmd_name, property_name):

        prop_meta = CMeta.GetPropertyMeta(cmd_name, property_name)

        expose_prop.AddObject(scriptable, RelationType("ScriptableExposedProperty"))
        expose_prop.Set("EPClassId", cmd_name)

        prop_name = cmd_name + "." + property_name
        expose_prop.Set("EPPropertyId", prop_name)
        # expose_prop.Set("EPNameId", prop_meta["name"])
        unique_id = get_unique_property_id(scriptable, property_name)
        expose_prop.Set("EPNameId", unique_id)
        expose_prop.Set("EPLabel", prop_meta["desc"])
        expose_prop.Set("EPDefaultValue", str(prop_meta["defaultValue"]))
        return unique_id

    @staticmethod
    def create_meth_tree_test_files():
        plLogger = PLLogger.GetLogger("create_meth_tree_test_files")
        stc_sys = CStcSystem.Instance()
        common_data_path = stc_sys.GetApplicationCommonDataPath()
        cleanup_info = {}
        for path, id in zip([common_data_path,
                             os.getcwd(),
                             os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR),
                             os.path.join(common_data_path, mgr_const.MM_SCRIPTS_DIR),
                             os.path.join(common_data_path, mgr_const.MM_TEMPLATE_DIR)],
                            ['1', '2', '3', '4', '5']):
            fileid = 'file' + id
            filename = os.path.join(path, fileid)
            cleanup_info[fileid] = filename
            pathid = 'path' + id
            if not os.path.exists(path):
                cleanup_info[pathid] = path
                os.makedirs(path)
                plLogger.LogInfo('creating path: ' + path)
            with open(filename, 'w') as f:
                f.write(' ')
                plLogger.LogInfo('creating file: ' + filename)
        return cleanup_info

    @staticmethod
    def cleanup_meth_tree_test_files(cleanup_info):
        plLogger = PLLogger.GetLogger("cleanup_meth_tree_test_files")
        for file in ['file1', 'file2', 'file3', 'file4', 'file5']:
            if file in cleanup_info:
                os.remove(cleanup_info[file])
                plLogger.LogInfo('removing file: ' + cleanup_info[file])
        for path in ['path3', 'path4', 'path5']:
            if path in cleanup_info and os.path.exists(path):
                plLogger.LogInfo('removing path: ' + path)
                os.rmdir(path)
        return

    @staticmethod
    def create_fake_installed_test_meth(meth_key, label_list,
                                        caseName='original', tc_key=""):
        install_dir = meth_man_utils.get_methodology_home_dir()
        test_meth_dir = os.path.join(install_dir, meth_key)
        plLogger = PLLogger.GetLogger("create_fake_installed_test_meth")
        plLogger.LogInfo("test_meth_dir: " + str(test_meth_dir))
        if not os.path.exists(test_meth_dir):
            os.makedirs(test_meth_dir)

        # Add a fake sequence file
        seq_file = os.path.join(test_meth_dir, mgr_const.MM_SEQUENCER_FILE_NAME)
        f = open(seq_file, "w")
        f.write("<?xml version=\"1.0\" encoding=\"windows-1252\"?>")
        f.close()
        plLogger.LogInfo("added sequence file")

        # Add a TXML file
        meta_file = os.path.join(test_meth_dir, mgr_const.MM_META_FILE_NAME)
        f = open(meta_file, "w")
        data = UnitTestUtils.gen_test_info_header("unit test meth disp name",
                                                  meth_key,
                                                  "unit test meth test case",
                                                  tc_key)
        # Add labels
        if len(label_list) > 0:
            data = data + "<labels>"
            for label in label_list:
                data = data + "<label>" + str(label) + "</label>"
            data = data + "</labels>"
        data = data + UnitTestUtils.UTU_FOOTER
        f.write(data)
        f.close()
        plLogger.LogInfo("added a TXML file")

    @staticmethod
    def add_fake_test_case(meth_key, label_list, tc_key):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("dir/case name: " + meth_key + "/" + tc_key)

        install_dir = meth_man_utils.get_methodology_home_dir()
        test_meth_dir = os.path.join(install_dir, meth_key)
        if not os.path.exists(test_meth_dir):
            return
        test_case_dir = os.path.join(test_meth_dir,
                                     mgr_const.MM_TEST_CASE_SUBDIR,
                                     tc_key)
        plLogger.LogInfo("test_case_dir: " + test_case_dir)

        if not os.path.exists(test_case_dir):
            os.makedirs(test_case_dir)

        # Add a TXML file
        meta_file = os.path.join(test_case_dir, mgr_const.MM_META_FILE_NAME)
        f = open(meta_file, "w")
        data = UnitTestUtils.gen_test_info_header("unit test meth disp name",
                                                  meth_key,
                                                  "unit test meth test case",
                                                  tc_key)
        # Add labels
        if len(label_list) > 0:
            data = data + "<labels>"
            for label in label_list:
                data = data + "<label>" + str(label) + "</label>"
            data = data + "</labels>"
        data = data + UnitTestUtils.UTU_FOOTER
        f.write(data)
        f.close()

    @staticmethod
    def delete_fake_installed_test_meth(dir_name):
        stc_sys = CStcSystem.Instance()
        common_data_path = stc_sys.GetApplicationCommonDataPath()
        install_dir = os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR)
        test_meth_dir = os.path.join(install_dir, dir_name)
        if not os.path.exists(test_meth_dir):
            return

        # Delete metadata file
        test_case_dir = test_meth_dir

        if os.path.exists(test_case_dir):
            for root, dirs, filenames in os.walk(test_case_dir):
                for f in filenames:
                    os.remove(os.path.join(test_case_dir, f))
            os.rmdir(test_case_dir)

        # Remove the test methodology directory
        os.rmdir(test_meth_dir)

    @staticmethod
    def get_methodology_handle(meth_key):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("meth_key: " + meth_key)
        meth_manager = meth_man_utils.get_meth_manager()
        meth_list = meth_manager.GetObjects("StmMethodology")
        meth_hnd = None
        for meth in meth_list:
            if meth is None:
                continue
            plLogger.LogInfo("test_meth key: " + meth.Get("MethodologyKey"))
            if meth.Get("MethodologyKey") == meth_key:
                meth_hnd = meth.GetObjectHandle()
                break
        plLogger.LogInfo("meth_name has handle : " + str(meth_hnd))
        return meth_hnd

    @staticmethod
    def cleanup_methodology(meth_handle):
        ctor = CScriptableCreator()
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")

        # Manually update TestMethodologyManager
        pkg = "spirent.methodology.manager."
        cmd = ctor.CreateCommand(pkg + "UpdateTestMethodologyManagerCommand")
        cmd.Execute()
        cmd.MarkDelete()

        cmd = ctor.CreateCommand(pkg + "DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth_handle)
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("end")
