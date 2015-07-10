from StcIntPythonPL import *
import os
from mock import MagicMock
from ..utils.txml_utils import get_unique_property_id
from ..utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from ..utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.manager.CreateMethodologyTestCaseCommand as CreateCmd


PKG_BASE = "spirent.methodology"
PKG = PKG_BASE + ".manager"


class TestCreateTestCase:
    @staticmethod
    def bind(cmd_name, expose_prop, scriptable, property_name):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        prop_meta = CMeta.GetPropertyMeta(cmd_name, property_name)

        expose_prop.AddObject(scriptable, RelationType("ScriptableExposedProperty"))
        expose_prop.Set("EPClassId", cmd_name)

        prop_name = cmd_name + "." + property_name
        expose_prop.Set("EPPropertyId", prop_name)
        expose_prop.Set("EPNameId", get_unique_property_id(scriptable, property_name))
        expose_prop.Set("EPLabel", prop_meta["desc"])
        expose_prop.Set("EPDefaultValue", str(prop_meta["defaultValue"]))
        plLogger.LogInfo("end")
        return

    @staticmethod
    def make_fake_test_pkg(copy_count, port_group_tag,
                           meth_name, meth_key, meth_description):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("make_fake_test_pkg.begin")
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        plLogger.LogInfo("Create LoadTemplateCommand")
        temp_cmd = ctor.CreateCommand(PKG_BASE +
                                      ".LoadTemplateCommand")
        temp_cmd.Set("CopiesPerParent", copy_count)
        temp_cmd.SetCollection("TargetTagList", [port_group_tag])

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [temp_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        plLogger.LogInfo("Create exposed properties")
        cmd_name = PKG_BASE + ".LoadTemplateCommand"
        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        TestCreateTestCase.bind(cmd_name, prop1, temp_cmd, "CopiesPerParent")
        prop2 = ctor.Create("ExposedProperty", exposedConfig)
        TestCreateTestCase.bind(cmd_name, prop2, temp_cmd, "TemplateXmlFileName")

        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)
        if meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
            cmd.Set("StmMethodology", meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Clean up empty folders (if existing)
        meth_man_utils.methodology_rmdir(meth_key)

        # Publish the methodology
        plLogger.LogInfo("Publish " + meth_name)
        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", meth_name)
        cmd.Set("MethodologyKey", meth_key)
        cmd.Set("MethodologyDescription", meth_description)
        cmd.Set("MinPortCount", "0")
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("Cleanup")
        # Reset Config
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        cmd_list = sequencer.GetObjects("Command")
        assert len(cmd_list) == 0

        plLogger.LogInfo("make_fake_test_pkg.end")

        return

    def test_validate(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("test_validate.begin")
        ctor = CScriptableCreator()
        cmd = ctor.CreateCommand(PKG + ".CreateMethodologyTestCaseCommand")
        CreateCmd.get_this_cmd = MagicMock(return_value=cmd)
        res = CreateCmd.validate('{"methodology_key" : "a", "display_name" : "b"}')
        assert res == ""
        res = CreateCmd.validate('{"methodology_key" : "vvvv"}')
        assert res != ""
        return

    def test_create_test_case(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("test_create_test_case.begin")
        ctor = CScriptableCreator()
        meth_name = "TestMeth_CreateTestCase"
        meth_key = "UNITTEST_CREATEMETH"
        meth_description = "Test CreateTestCase Methodology Description"
        test_case_name = "CreateTestCase_Name"

        # Defaults
        copy_count = 20

        TestCreateTestCase.make_fake_test_pkg(copy_count,
                                              "UnitTestFakeMeth",
                                              meth_name, meth_key,
                                              meth_description)
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert test_meth_obj is not None

        # Change the defaults in "original" meta by setting TestCaseName to test_case_name and
        # TestCaseDescription to test_case_description
        cmd = ctor.CreateCommand(PKG + ".CreateMethodologyTestCaseCommand")

        # Mock get_this_cmd to call run() directly
        CreateCmd.get_this_cmd = MagicMock(return_value=cmd)
        res = CreateCmd.run('{"methodology_key" : "' + meth_key + '",' +
                            '"display_name" : "' + test_case_name + '"}')
        assert res is True
        tc_key = cmd.Get("TestCaseKey")
        assert tc_key is not None
        assert tc_key == meth_key + "-1"
        tc_obj = meth_man_utils.get_stm_testcase_from_key(test_meth_obj, tc_key)
        assert tc_obj is not None
        assert tc_obj.IsTypeOf("StmTestCase")

        # Check the meta file exists
        install_dir = meth_man_utils.get_test_case_dir(meth_key, tc_key)
        assert install_dir
        meta_json_file_path = os.path.join(install_dir, mgr_const.MM_META_JSON_FILE_NAME)
        assert meta_json_file_path
        assert os.path.isfile(meta_json_file_path)

        j = ""
        plLogger.LogDebug('meta.json is at ' + meta_json_file_path)
        with open(meta_json_file_path, "r") as f:
            j = f.read()
            plLogger.LogDebug('meta.json content includes: "' + j + '"')
        err_str, meta = json_utils.load_json(j)
        assert err_str == ""
        assert meta is not None
        assert 'test_case_key' in meta
        assert meta['test_case_key'] == tc_key
        assert 'display_name' in meta
        assert meta['display_name'] == test_case_name

        cmd = ctor.CreateCommand(PKG + ".DeleteTestCaseCommand")
        cmd.Set("StmTestCase", tc_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("end")
