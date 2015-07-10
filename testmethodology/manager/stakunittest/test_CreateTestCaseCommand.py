from StcIntPythonPL import *
import os
from mock import MagicMock
import xml.etree.ElementTree as etree
from ..utils.txml_utils import MetaManager as meta_man, \
    get_unique_property_id
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
import spirent.methodology.manager.CreateTestCaseCommand as CreateCmd


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

    @staticmethod
    def check_txml_values(txml,
                          test_inst,
                          copy_count,
                          port_map,
                          meth_name,
                          meth_key,
                          meth_description):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")

        # Check the values in the TXML file
        txml_tree = etree.parse(txml)
        assert txml_tree is not None
        txml_root = txml_tree.getroot()
        assert txml_root is not None
        plLogger.LogInfo("txml: \n" + etree.tostring(txml_root))

        prop_count = 0
        found_name = False
        port_count = 0
        plLogger.LogInfo("txml_root = " + txml_root.tag)
        for child in txml_root:
            plLogger.LogInfo("object is " + str(child.tag))
            if child.tag == meta_man.TEST_INFO:
                # Process the test info section, specifically the instance name
                plLogger.LogInfo("Found " + str(child.tag))
                plLogger.LogInfo("Instance name: " + str(child.get(meta_man.TI_TEST_CASE_NAME)))
                found_name = True
                assert child.get(meta_man.TI_TEST_CASE_NAME) == test_inst
                assert child.get(meta_man.TI_DESCRIPTION) == meth_description
                assert child.get(meta_man.TI_KEY) == meth_key
            elif child.tag == meta_man.TEST_RESOURCES:
                plLogger.LogInfo("Found " + str(child.tag))
                # Skip this section if there is no port_map
                if port_map is not None:
                    plLogger.LogInfo("port_map: " + str(port_map))
                    PORT_STR = ".//" + meta_man.TR_RESOURCE_GROUPS + \
                               "/" + meta_man.TR_RESOURCE_GROUP + \
                               "/" + meta_man.TR_PORT_GROUPS + \
                               "/" + meta_man.TR_PORT_GROUP + \
                               "/" + meta_man.TR_PORTS + \
                               "/" + meta_man.TR_PORT
                    port_list = child.findall(PORT_STR)
                    for port in port_list:
                        # The port id is the name of the port tag
                        port_id = port.get(meta_man.TR_NAME)
                        plLogger.LogInfo("Found port " + port_id)
                        port_loc = None
                        for attribute in port:
                            if attribute.tag == meta_man.TR_ATTR:
                                plLogger.LogInfo("Found attribute")
                                if attribute.get(meta_man.TR_NAME) == meta_man.TR_LOCATION:
                                    port_loc = attribute.get(meta_man.TR_VALUE)
                                    plLogger.LogInfo("Location " + str(port_loc))
                        assert port_id in port_map.keys()
                        assert port_map[port_id] == port_loc
                        port_count = port_count + 1
                        plLogger.LogInfo("port_count = " + str(port_count))
            elif child.tag == meta_man.EDITABLE_PARAMS:
                plLogger.LogInfo("Found " + str(child.tag))
                PARAM_STR = ".//" + meta_man.EP_PARAM
                param_list = child.findall(PARAM_STR)
                cmd_prop_name = PKG_BASE + ".loadtemplatecommand"
                for param in param_list:
                    plLogger.LogInfo("attributes of parameter")
                    # Loop through the attributes
                    prop_id = ""
                    prop_val = ""
                    for attribute in param:
                        if attribute.get(meta_man.EP_NAME) == meta_man.EP_PROP_ID:
                            prop_id = attribute.get(meta_man.EP_VALUE)
                        elif attribute.get(meta_man.EP_NAME) == meta_man.EP_DEFAULT:
                            prop_val = attribute.get(meta_man.EP_VALUE)
                    plLogger.LogInfo(" prop_id: " + str(prop_id) + " prop_val: " + str(prop_val))
                    # Check to see if we find properties that we expect
                    if cmd_prop_name in prop_id:
                        plLogger.LogInfo(" Matched the command name...")
                        if "copiesperparent" in prop_id:
                            plLogger.LogInfo(" CopiesPerParent...")
                            # FIXME:
                            # Not handled correctly, currently.
                            # Default should come from the sequencer.xml
                            # or some other form of input to the PublishMethodologyCommand
                            # assert prop_val == copy_count
                            prop_count = prop_count + 1
                        elif "templatexmlfilename" in prop_id:
                            plLogger.LogInfo(" TemplateXmlFileName...")
                            # FIXME:
                            # Not handled correctly, currently.
                            # Default should come from the sequencer.xml
                            # or some other form of input to the PublishMethodologyCommand
                            # assert prop_val == 12345
                            prop_count = prop_count + 1
        assert found_name is True
        assert prop_count == 2
        if port_map is not None:
            assert port_count == len(port_map.keys())
        plLogger.LogInfo("end")

    def test_create_test_case(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        ctor = CScriptableCreator()
        hnd_reg = CHandleRegistry.Instance()
        meth_name = "TestMeth_CreateTestCase"
        meth_key = "UNITTEST_CREATEMETH"
        meth_description = "Test CreateTestCase Methodology Description"
        test_case_name = "CreateTestCase_Name"
        test_case_description = "Description of test case"

        # Defaults
        copy_count = 20

        TestCreateTestCase.make_fake_test_pkg(copy_count,
                                              "UnitTestFakeMeth",
                                              meth_name, meth_key,
                                              meth_description)
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert test_meth_obj is not None

        # Check TXML defaults
        install_dir = meth_man_utils.get_methodology_dir(meth_key)
        assert install_dir
        meta_file = os.path.join(install_dir, mgr_const.MM_META_FILE_NAME)
        TestCreateTestCase.check_txml_values(meta_file,
                                             meta_man.TEST_INSTANCE_ORIGINAL,
                                             copy_count,
                                             None,
                                             meth_name,
                                             meth_key,
                                             meth_description)

        # Change the defaults in "original" TXML by setting TestCaseName to test_case_name and
        # TestCaseDescription to test_case_description
        cmd = ctor.CreateCommand(PKG + ".CreateTestCaseCommand")
        cmd.Set("TestCaseSrc", test_meth_obj.GetObjectHandle())
        cmd.Set("TestCaseName", test_case_name)
        cmd.Set("TestCaseDescription", test_case_description)

        # Mock get_this_cmd to call run() directly
        CreateCmd.get_this_cmd = MagicMock(return_value=cmd)
        res = CreateCmd.run(test_meth_obj.GetObjectHandle(),
                            test_case_name,
                            test_case_description)
        assert res is True
        tc_obj_hnd = cmd.Get("StmTestCase")
        tc_obj = hnd_reg.Find(tc_obj_hnd)
        assert tc_obj is not None
        assert tc_obj.IsTypeOf("StmTestCase")

        # Check the TXML file exists
        install_dir = meth_man_utils.get_test_case_dir(meth_key, meth_key + "-1")
        assert install_dir
        meta_file_path = os.path.join(install_dir, mgr_const.MM_META_FILE_NAME)
        assert meta_file_path

        # Check TXML
        TestCreateTestCase.check_txml_values(meta_file_path,
                                             test_case_name,
                                             copy_count,
                                             None,
                                             meth_name,
                                             meth_key,
                                             test_case_description)

        cmd = ctor.CreateCommand(PKG + ".DeleteTestCaseCommand")
        cmd.Set("StmTestCase", tc_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("end")
