from StcIntPythonPL import *
import os
import sys
from mock import MagicMock
from ..utils.txml_utils import get_unique_property_id
from ..utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from ..utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils
from unit_test_utils import UnitTestUtils
sys.path.append(os.path.join(os.getcwd(), "STAKCommands", "spirent", "methodology"))


PKG_BASE = "spirent.methodology"
PKG = PKG_BASE + ".manager"


# FIXME:
# This file SHOULD be broken up into multiple files, one
# for each command that is being tested.  As it is, some
# of these unit tests might be better suited as simple
# regression scripts.
class TestMethodologyManagerCommands:
    def d_test_publish_methodology(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("test_publish_methodology.begin")
        test_name = "UnitTestMethPublishTest"
        meth_key = "UNITTEST_PUB"
        test_label_list = ["UnitTest", "Arp", "Ipv4"]
        min_num_ports = "2"
        max_num_ports = "4"
        port_speed_list = ["40", "100"]
        PORT1_LOCATION = "//10.14.16.20/2/1"
        PORT2_LOCATION = "//10.14.16.20/2/2"

        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")
        sequencer = CStcSystem.Instance().GetObject("Sequencer")

        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        if test_meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
            cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Clean up empty folders (if existing)
        meth_man_utils.methodology_rmdir(meth_key)

        # Create Untagged ports
        port1 = ctor.Create("Port", project)
        port1.Set("Location", PORT1_LOCATION)
        port2 = ctor.Create("Port", project)
        port2.Set("Location", PORT2_LOCATION)

        cmd_name = "ArpNdStartCommand"
        arp_cmd = ctor.CreateCommand(cmd_name)
        stak_cmd_name = "Ipv4NetworkProfileGroupCommand"
        stak_cmd = ctor.CreateCommand(PKG_BASE + ".Ipv4NetworkProfileGroup")

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [arp_cmd.GetObjectHandle(),
                                                 stak_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop1, arp_cmd, cmd_name, "ArpNdOption")

        prop2 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop2, arp_cmd, cmd_name, "ForceArp")

        prop3 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop3, arp_cmd, cmd_name, "WaitForArpToFinish")

        prop4 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop4, stak_cmd, PKG_BASE + "." +
                           stak_cmd_name, "DeviceCount")

        obj = prop1.GetObject("Scriptable", RelationType("ScriptableExposedProperty"))
        assert obj.GetObjectHandle() == arp_cmd.GetObjectHandle()

        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", test_name)
        cmd.Set("MethodologyKey", meth_key)
        cmd.SetCollection("MethodologyLabelList", test_label_list)
        cmd.Set("MinPortCount", min_num_ports)
        cmd.Set("MaxPortCount", max_num_ports)
        cmd.SetCollection("PortSpeedList", port_speed_list)
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Set("EditableParams", get_tagged_xml())
        cmd.Execute()
        cmd.MarkDelete()

        sequencer = CStcSystem.Instance().GetObject("Sequencer")

        # Check the sequencer
        assert sequencer.Get("ErrorHandler") == "STOP_ON_ERROR"

        # Check the command sequencer
        cmd_list = sequencer.GetObjects("Command")
        assert len(cmd_list) == 3

        sp_list = sequencer.GetObjects("SequenceableCommandProperties")
        assert len(sp_list) > 0

        for cmd in cmd_list:
            if cmd.IsTypeOf(PKG + ".MethodologyGroupCommand"):
                found_tlgc = True
            else:
                sp = cmd.GetObject("SequenceableCommandProperties",
                                   RelationType("SequenceableProperties"))
                assert sp is not None
                assert sp.Get("AllowDelete") is False
                assert sp.Get("AllowMove") is False
                assert sp.Get("AllowUngroup") is False
                assert sp.Get("AllowDisable") is False
                assert sp.Get("ShowEditor") is False
        assert found_tlgc is True

        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert test_meth_obj

        # Delete installed test methodology
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("test_publish_methodology.end")

    def d_test_publish_methodology_no_exposed_property(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_publish_methodology_no_exposed_property")
        test_name = "UnitTestMethPublishTestNoExposed"
        meth_key = "UNITTEST_PUB_NO_EXP"

        ctor = CScriptableCreator()

        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        if test_meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
            cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Clean up empty folders (if existing)
        meth_man_utils.methodology_rmdir(meth_key)

        cmd_name = "ArpNdStartCommand"
        stak_cmd_name = PKG_BASE + ".Ipv4NetworkProfileGroupCommand"
        arp_cmd = ctor.CreateCommand(cmd_name)
        stak_cmd = ctor.CreateCommand(stak_cmd_name)

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [arp_cmd.GetObjectHandle(),
                                                 stak_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        # Publish the methodology
        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", test_name)
        cmd.Set("MethodologyKey", meth_key)
        cmd.Set("MinPortCount", "0")
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Execute()
        errorMsg = cmd.Get("ErrorMsg")
        cmd.MarkDelete()

        assert (errorMsg == "")

        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert test_meth_obj

        # Delete installed test methodology
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("end.test_publish_methodology_no_exposed_property")

    def test_publish_template(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_publish_template")
        template_name = "MyTemplate.xml"

        project = CStcSystem.Instance().GetObject("project")
        ctor = CScriptableCreator()
        port1 = ctor.Create("port", project)

        ifStack = ["EthIIIf", "Ipv4If"]
        ifCount = ["1", "1"]
        cmd = ctor.CreateCommand("DeviceCreateCommand")
        cmd.Set("Port", port1.GetObjectHandle())
        cmd.Set("DeviceType", "EmulatedDevice")
        cmd.SetCollection("IfStack", ifStack)
        cmd.SetCollection("IfCount", ifCount)
        cmd.Execute()
        cmd.MarkDelete()

        dev = port1.GetObject("EmulatedDevice", RelationType("AffiliationPort", 1))
        assert dev is not None
        bgp = ctor.Create("BgpRouterConfig", dev)
        assert bgp is not None

        cmd = ctor.CreateCommand(PKG + ".PublishTemplateCommand")
        cmd.Set("TemplateName", template_name)
        cmd.Execute()
        cmd.MarkDelete()

        common_data_path = CStcSystem.Instance().GetApplicationCommonDataPath()
        install_dir = os.path.join(common_data_path, mgr_const.MM_TEST_METH_DIR)
        out_filename = os.path.join(install_dir, template_name)
        assert os.path.exists(out_filename)

        cmd = ctor.CreateCommand(PKG + ".DeleteTemplateCommand")
        cmd.Set("TemplateName", template_name)
        cmd.Execute()
        cmd.MarkDelete()
        assert not os.path.exists(out_filename)
        plLogger.LogInfo("end.test_publish_template")

    # FIXME:
    # LoadTestMethodologyCommand will be removed and this
    # unit test will need to be fixed.
    def disabled_test_RemoveMethodologyGroupCommand(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_RemoveMethodologyGroupCommand")
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")
        sequencer = CStcSystem.Instance().GetObject("Sequencer")

        cmd_name = "ArpNdStartCommand"
        stak_cmd_name = "spirent.methodology.Ipv4NetworkProfileGroupCommand"
        arp_cmd = ctor.CreateCommand(cmd_name)
        stak_cmd = ctor.CreateCommand(stak_cmd_name)
        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [arp_cmd.GetObjectHandle(),
                                                 stak_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop1, arp_cmd, cmd_name, "ArpNdOption")

        prop4 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop4, stak_cmd, stak_cmd_name, "DeviceCount")

        test_name = "TestMethRemoveGroup"
        meth_key = "UNITTEST_RM_GRP"
        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        if test_meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand("spirent.methodology.manager."
                                     "DeleteMethodologyCommand")
            cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Publish methodology
        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", test_name)
        cmd.Set("MethodologyKey", meth_key)
        cmd.Set("MinPortCount", "0")
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Execute()
        cmd.MarkDelete()

        # Reset Config
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        cmd_list = sequencer.GetObjects("Command")
        assert len(cmd_list) == 0

        meth_handle = UnitTestUtils.get_methodology_handle(meth_key)
        assert meth_handle

        # Load the test methodology created earlier
        cmd = ctor.CreateCommand(PKG + ".LoadTestMethodologyCommand")
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        cmd.Set("StmMethodology", meth.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        cmd_list = sequencer.GetObjects("Command")
        assert len(cmd_list) == 3

        # Strip the MethodologyGroupCommand and make the test methodology editable again
        cmd = ctor.CreateCommand(PKG + ".RemoveMethodologyGroupCommand")
        cmd.Execute()
        cmd.MarkDelete()

        # Check the sequence
        for cmd in sequencer.GetObjects("Command"):
            assert cmd.IsTypeOf(PKG + ".MethodologyGroupCommand") is False
            scp = cmd.GetObject("SequenceableCommandProperties",
                                RelationType("SequenceableProperties"))
            assert scp is not None
            assert scp.Get("AllowDelete") is True
            assert scp.Get("AllowMove") is True
            assert scp.Get("AllowUngroup") is True
            assert scp.Get("AllowDisable") is True
            assert scp.Get("ShowEditor") is True

        # Clean up
        meth_man_utils.remove_active_test_relation()
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
        plLogger.LogInfo("end.test_RemoveMethodologyGroupCommand")

    # FIXME:
    # LoadTestMethodologyCommand will be removed and this
    # unit test will need to be fixed.
    def disabled_test_load_with_json(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_load_with_json")
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")
        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        hnd_reg = CHandleRegistry.Instance()

        cmd_name = "Ipv4NetworkProfileGroupCommand"
        create_cmd = ctor.CreateCommand(PKG_BASE + "." + cmd_name)

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [create_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop1, create_cmd, PKG_BASE +
                           "." + cmd_name, "DeviceCount")
        prop2 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop2, create_cmd, PKG_BASE +
                           "." + cmd_name, "RouterId")
        prop3 = ctor.Create("ExposedProperty", exposedConfig)
        UnitTestUtils.bind(prop3, create_cmd, PKG_BASE +
                           "." + cmd_name, "Ipv4Addr")

        test_name = "TestLoadWithJson"
        meth_key = "UNITTEST_LOADJSON"
        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        if test_meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
            cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Publish as a methodology
        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", test_name)
        cmd.Set("MinPortCount", "0")
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Execute()
        cmd.MarkDelete()

        # Reset Config
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        cmd_list = sequencer.GetObjects("Command")
        assert len(cmd_list) == 0

        meth_handle = UnitTestUtils.get_methodology_handle(meth_key)
        assert meth_handle

        # TODO: Create a test case instead of running the methodology
        # itself.

        # Set up JSON input
        json_input = "{ \"ports\": {}, \"params\" : {\"" + prop1.Get("EPNameId") + "\" : 101, " + \
                     "\"" + prop2.Get("EPNameId") + "\" : \"188.0.0.5\", " + \
                     "\"" + prop3.Get("EPNameId") + "\" : \"172.0.17.5\" } }"
        active_test = meth_man_utils.get_active_test_case()
        assert active_test is None
        # Load the test methodology created earlier
        # Set the JSON input
        cmd = ctor.CreateCommand(PKG + ".LoadTestMethodologyCommand")
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert meth is not None
        cmd.Set("StmMethodology", meth.GetObjectHandle())
        cmd.Set("InputJson", json_input)
        cmd.Execute()

        # Check the command sequence
        cmd_hnd_list = sequencer.GetCollection("CommandList")
        assert len(cmd_hnd_list) == 1

        tlgc = hnd_reg.Find(cmd_hnd_list[0])
        assert tlgc is not None
        assert tlgc.IsTypeOf(PKG + ".MethodologyGroupCommand") is True

        cmd_hnd_list = tlgc.GetCollection("CommandList")
        assert len(cmd_hnd_list) == 1

        create_cmd = hnd_reg.Find(cmd_hnd_list[0])
        assert create_cmd.IsTypeOf(PKG_BASE + "." + cmd_name) is True

        # Check defaults
        assert create_cmd.Get("DeviceCount") == 1
        assert create_cmd.Get("RouterId") == "192.0.0.1"
        assert create_cmd.Get("Ipv4Addr") == "192.85.1.3"

        # Execute a MethodologyGroupCommand
        tlgc2 = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
        tlgc2.Set("InputJson", tlgc.Get("InputJson"))
        tlgc2.Execute()
        tlgc2.MarkDelete()

        # Check the new defaults
        assert create_cmd.Get("DeviceCount") == 101
        assert create_cmd.Get("RouterId") == "188.0.0.5"
        assert create_cmd.Get("Ipv4Addr") == "172.0.17.5"

        # Clean up
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
        plLogger.LogInfo("end.test_load_with_json")

    def test_GetAllTestMethodologiesCommand(self, stc):
        ctor = CScriptableCreator()
        hnd_reg = CHandleRegistry.Instance()
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_GetAllTestMethodologiesCommand")

        test_pkg1 = "UNITTEST_GETALL1"
        test_pkg2 = "UNITTEST_GETALL2"
        test_pkg3 = "UNITTEST_GETALL3"
        UnitTestUtils.create_fake_installed_test_meth(test_pkg1, [])
        UnitTestUtils.create_fake_installed_test_meth(test_pkg2, [])
        UnitTestUtils.create_fake_installed_test_meth(test_pkg3, [])

        UnitTestUtils.add_fake_test_case(test_pkg1, [], "UNITTEST_GETALL1-1")
        UnitTestUtils.add_fake_test_case(test_pkg1, [], "UNITTEST_GETALL1-2")
        UnitTestUtils.add_fake_test_case(test_pkg1, [], "UNITTEST_GETALL1-3")

        UnitTestUtils.add_fake_test_case(test_pkg3, [], "UNITTEST_GETALL3-1")

        # Manually update TestMethodologyManager
        cmd = ctor.CreateCommand(PKG + ".UpdateTestMethodologyManagerCommand")
        cmd.Execute()
        cmd.MarkDelete()

        # Get all installed test methodologies
        list_cmd = ctor.CreateCommand(PKG + ".GetAllTestMethodologiesCommand")
        list_cmd.Execute()
        test_meth_handle_list = list_cmd.GetCollection("StmMethodologyList")
        list_cmd.MarkDelete()

        meth_key_list = []
        meth_obj1 = None
        meth_obj2 = None
        meth_obj3 = None
        for meth_handle in test_meth_handle_list:
            meth_obj = hnd_reg.Find(meth_handle)
            assert meth_obj is not None
            meth_key = meth_obj.Get("MethodologyKey")
            if meth_key == test_pkg1:
                meth_obj1 = meth_obj
            elif meth_key == test_pkg2:
                meth_obj2 = meth_obj
            elif meth_key == test_pkg3:
                meth_obj3 = meth_obj
        assert meth_obj1 is not None
        assert meth_obj2 is not None
        assert meth_obj3 is not None

        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth_obj1.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth_obj2.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth_obj3.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        # Manually update TestMethodologyManager
        cmd = ctor.CreateCommand(PKG + ".UpdateTestMethodologyManagerCommand")
        cmd.Execute()
        cmd.MarkDelete()

        # Get all installed test methodologies
        list_cmd = ctor.CreateCommand(PKG + ".GetAllTestMethodologiesCommand")
        list_cmd.Execute()
        test_meth_handle_list = list_cmd.GetCollection("StmMethodologyList")
        list_cmd.MarkDelete()

        meth_key_list = []
        for meth_handle in test_meth_handle_list:
            meth_obj = hnd_reg.Find(meth_handle)
            meth_key_list.append(meth_obj.Get("MethodologyKey"))
        assert test_pkg1 not in meth_key_list
        assert test_pkg2 not in meth_key_list
        assert test_pkg3 not in meth_key_list
        list_cmd.MarkDelete()
        plLogger.LogInfo("end.test_GetAllTestMethodologiesCommand")

    # FIXME:
    # LoadTestMethodologyCommand will be removed and this
    # unit test will need to be fixed.
    def disabled_test_export_import_load_loose_ports(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin.test_export_import_load_loose_ports")
        ctor = CScriptableCreator()
        stc_sys = CStcSystem.Instance()
        project = stc_sys.GetObject("Project")

        port = ctor.Create("Port", project)
        etcu = ctor.Create("EthernetCopper", port)
        port.AddObject(etcu, RelationType("ActivePhy"))
        port.Set("Location", "//10.14.18.4/1/1")
        port_id = get_unique_property_id(port, "Location")

        stak_cmd_name = "spirent.methodology.Ipv4NetworkProfileGroupCommand"
        stak_cmd = ctor.CreateCommand(stak_cmd_name)
        stak_cmd.SetCollection("PortList", [port.GetObjectHandle()])

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [stak_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        # Expose properties
        exposed_config = ctor.Create("ExposedConfig", project)

        # MacAddr
        mac_prop = ctor.Create("ExposedProperty", exposed_config)
        mac_prop_id = UnitTestUtils.bind(mac_prop, stak_cmd, stak_cmd_name, "MacAddr")

        # EnableVlan
        enable_prop = ctor.Create("ExposedProperty", exposed_config)
        enable_prop_id = UnitTestUtils.bind(enable_prop, stak_cmd, stak_cmd_name, "EnableVlan")

        # VlanId
        vlan_prop = ctor.Create("ExposedProperty", exposed_config)
        vlan_prop_id = UnitTestUtils.bind(vlan_prop, stak_cmd, stak_cmd_name, "VlanId")

        test_name = "TestLoosePorts"
        # Delete the methodology we are about to create just in case
        # there was an error on a previous run.
        test_meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

        if test_meth_obj:
            # Delete installed test methodology
            cmd = ctor.CreateCommand("spirent.methodology.manager."
                                     "DeleteMethodologyCommand")
            cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
            cmd.Execute()
            cmd.MarkDelete()

        # Publish methodology
        cmd = ctor.CreateCommand(PKG + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", test_name)
        cmd.SetCollection("FeatureIdList", ["Feature1"])
        cmd.Execute()
        cmd.MarkDelete()

        # Reset Config
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

        # Load the test methodology created earlier
        # Use mock to prevent the AttachPortsCommand in the LoadTestMethodologyCommand
        # from being executed.
        LoadTestMethodologyCommand.attach_ports = MagicMock()

        # JSON Input
        json_input = "{\"ports\" : {\"" + port_id + "\" : \"//10.14.16.27/2/2\"}, " + \
                     "\"params\" : {\"" + mac_prop_id + "\" : \"55:55:55:55:55:55\", " + \
                     "\"" + enable_prop_id + "\" : \"TRUE\", \"" + vlan_prop_id + "\" : 555} }"

        plLogger.LogInfo("json_input: " + json_input)

        # Call run directly
        # Note that 0 is an invalid STC handle.  Asking the HandleRegistry for
        # it will result in None.
        # Last arg "1" is to turn on TIE check. "0" will turn off the check
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        assert meth is not None
        LoadTestMethodologyCommand.run(meth.GetObjectHandle(), 0, json_input, 1)

        # Check the loaded objects
        project = CStcSystem.Instance().GetObject("Project")
        port_list = project.GetObjects("Port")
        assert len(port_list) == 1

        # Check the port location has been reconfigured properly
        assert port_list[0].Get("Location") == "//10.14.16.27/2/2"

        # Note that one of the exposed properties is the port location
        # that is tacked on automatically
        exp_conf = project.GetObject("ExposedConfig")
        exp_prop_list = exp_conf.GetObjects("ExposedProperty")
        assert len(exp_prop_list) == 4

        found_location_prop = False
        for exp_prop in exp_prop_list:
            if exp_prop.Get("EPNameId") == port_id:
                found_location_prop = True
        assert found_location_prop is True

        # Clean up
        meth_man_utils.remove_active_test_relation()
        meth = meth_man_utils.get_stm_methodology_from_key(meth_key)
        cmd = ctor.CreateCommand(PKG + ".DeleteMethodologyCommand")
        cmd.Set("StmMethodology", meth.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
        plLogger.LogInfo("end.test_export_import_load_loose_ports")


def get_tagged_xml():
    tagged_xml = "<paramGroups>\
    <paramGroup name=\"LoadTemplateGroupCommand.1234\">\
    <params>\
    <param tag=\"Bgp\" id=\"1234\">\
    <attribute name=\"BgpRouterConfig.AsNum\" value=\"564\"/>\
    <attribute name=\"BgpRouterConfig.PeerAs\" value=\"111\"/>\
    </param>\
    <param tag=\"OuterVlan\" id=\"5678\">\
    <attribute name=\"VlanIfnIf.VlanId\" value=\"100\"/>\
    </param>\
    </params>\
    </paramGroup>\
    <paramGroup name=\"LoadTemplateGroupCommand.5678\">\
    <params>\
    <param tag=\"Bgp\" id=\"9012\">\
    <attribute name=\"BgpRouterConfig.AsNum\" value=\"444\"/>\
    <attribute name=\"BgpRouterConfig.PeerAs\" value=\"333\"/>\
    </param>\
    <param tag=\"InnerVlan\" id=\"3456\">\
    <attribute name=\"VlanIfnIf.VlanId\" value=\"101\"/>\
    </param>\
    </params>\
    </paramGroup>\
    </paramGroups>"
    return tagged_xml
