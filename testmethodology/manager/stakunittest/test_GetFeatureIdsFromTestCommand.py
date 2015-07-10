from StcIntPythonPL import *
from ..utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils
from ..utils.txml_utils import get_unique_property_id


class TestGetFeatureIds:
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
    def make_fake_test_pkg(copies_per_parent, port_loc,
                           meth_name, meth_key, meth_description, feature_id_list):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.make_fake_test_pkg")
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        meth_pkg = "spirent.methodology"
        meth_man_pkg = "spirent.methodology.manager"

        plLogger.LogDebug("Handle ports")
        port = None
        if port_loc is not "":
            port = ctor.Create("Port", project)
            port.Set("Location", port_loc)

        plLogger.LogInfo("Create load template command")
        load_temp_cmd = ctor.CreateCommand(meth_pkg +
                                           ".LoadTemplateCommand")
        load_temp_cmd.Set("CopiesPerParent", copies_per_parent)

        # FIXME (not that it matters here)
        # Need to set the port group tag.  However, the unit test
        # does not use ports at the moment.

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [load_temp_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        plLogger.LogInfo("Create exposed properties")
        cmd_name = meth_pkg + ".LoadTemplateCommand"
        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        TestGetFeatureIds.bind(cmd_name, prop1, load_temp_cmd, "CopiesPerParent")
        plLogger.LogDebug("Publish " + meth_name)

        # Publish the methodology
        cmd = ctor.CreateCommand(meth_man_pkg + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", meth_name)
        cmd.Set("MethodologyKey", meth_key)
        cmd.Set("MethodologyDescription", meth_description)
        cmd.Set("MinPortCount", "0")
        cmd.SetCollection("FeatureIdList", feature_id_list)
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

        plLogger.LogDebug("end.make_fake_test_pkg")

        return

    def test_get_feature_ids_from_test(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.test_get_feature_ids_from_test")
        ctor = CScriptableCreator()
        meth_name = "GetFID"
        meth_key = "METH_KEY"
        meth_description = "Test Get Feature Ids Description"
        test_case_name = "GetFID1"
        test_case_description = "Description of test case"
        feature_id_list = ["Feature1", "Feature2"]

        meth_man_pkg = "spirent.methodology.manager"

        # Defaults
        copies_per_parent = 10
        TestGetFeatureIds.make_fake_test_pkg(copies_per_parent,
                                             "",
                                             meth_name,
                                             meth_key,
                                             meth_description,
                                             feature_id_list)

        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        # Create a test case
        cmd = ctor.CreateCommand(meth_man_pkg + ".CreateTestCaseCommand")
        cmd.Set("TestCaseSrc", test_meth_obj.GetObjectHandle())
        cmd.Set("TestCaseName", test_case_name)
        cmd.Set("TestCaseDescription", test_case_description)
        cmd.Execute()
        test_case_handle = cmd.Get("StmTestCase")
        cmd.MarkDelete()

        hnd_reg = CHandleRegistry.Instance()
        test_case_obj = hnd_reg.Find(test_case_handle)
        assert test_case_obj is not None

        # Check the feature IDs
        cmd = ctor.CreateCommand(meth_man_pkg + ".GetFeatureIdsFromTestCommand")
        cmd.Set("StmTestCase", test_case_obj.GetObjectHandle())
        cmd.Execute()

        feature_id_list_2 = cmd.GetCollection("FeatureIdList")
        plLogger.LogDebug("Returned: " + str(feature_id_list_2))

        cmd.MarkDelete()

        # Clean up the test case and the methodology
        cmd = ctor.CreateCommand(meth_man_pkg + ".DeleteTestCaseCommand")
        cmd.Set("StmTestCase", test_case_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        cmd = ctor.CreateCommand(meth_man_pkg + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        # The lists must match in length and content, though order may be different
        assert len(feature_id_list) == \
            len(set(feature_id_list).intersection(set(feature_id_list_2)))

        plLogger.LogDebug("end.test_get_feature_ids_from_test")
