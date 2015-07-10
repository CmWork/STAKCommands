from StcIntPythonPL import *
import os
import xml.etree.ElementTree as etree
from unit_test_utils import UnitTestUtils
from ..utils.txml_utils import MetaManager as meta_man, get_unique_property_id
from ..utils.methodologymanagerConst import MethodologyManagerConst as mgr_const


class TestSaveTestCase:
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
    def make_fake_test_pkg(mac, enable_vlan, vlan, ip, port_loc, meth_name):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject("Project")

        sequencer = CStcSystem.Instance().GetObject("Sequencer")
        meth_pkg = "spirent.methodology"
        meth_man_pkg = "spirent.methodology.manager"

        plLogger.LogInfo("Handle ports")
        port = None
        if port_loc is not "":
            port = ctor.Create("Port", project)
            port.Set("Location", port_loc)

        plLogger.LogInfo("Create network profile command")
        net_prof_cmd = ctor.CreateCommand(meth_pkg +
                                          ".Ipv4NetworkProfileGroupCommand")
        net_prof_cmd.Set("MacAddr", mac)
        net_prof_cmd.Set("EnableVlan", enable_vlan)
        net_prof_cmd.Set("VlanId", vlan)
        net_prof_cmd.Set("Ipv4Addr", ip)

        if port is not None:
            net_prof_cmd.SetCollection("PortList", [port.GetObjectHandle()])

        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", [net_prof_cmd.GetObjectHandle()])
        insert_cmd.Execute()

        exposedConfig = ctor.Create("ExposedConfig", project)

        plLogger.LogInfo("Create exposed properties")
        cmd_name = meth_pkg + ".Ipv4NetworkProfileGroupCommand"
        prop1 = ctor.Create("ExposedProperty", exposedConfig)
        TestSaveTestCase.bind(cmd_name, prop1, net_prof_cmd, "MacAddr")
        prop2 = ctor.Create("ExposedProperty", exposedConfig)
        TestSaveTestCase.bind(cmd_name, prop2, net_prof_cmd, "EnableVlan")
        prop3 = ctor.Create("ExposedProperty", exposedConfig)
        TestSaveTestCase.bind(cmd_name, prop3, net_prof_cmd, "VlanId")
        prop4 = ctor.Create("ExposedProperty", exposedConfig)
        TestSaveTestCase.bind(cmd_name, prop4, net_prof_cmd, "Ipv4Addr")

        prop1_name = get_unique_property_id(net_prof_cmd, "MacAddr")
        prop2_name = get_unique_property_id(net_prof_cmd, "EnableVlan")
        prop3_name = get_unique_property_id(net_prof_cmd, "VlanId")
        prop4_name = get_unique_property_id(net_prof_cmd, "Ipv4Addr")

        name_dict = {"MacAddr": prop1_name, "EnableVlan": prop2_name,
                     "VlanId": prop3_name, "Ipv4Addr": prop4_name}

        plLogger.LogInfo("Handle port locations")
        # Note that this works because the port's handle won't change between this point
        # and when the PublishMethodologyCommand generates the exposed property for the port
        # location.
        if port is not None:
            port_id = "port.location." + str(port.GetObjectHandle())
            name_dict[port_loc] = port_id

        plLogger.LogInfo("Export " + meth_name)

        # Export to a distributable zip file
        cmd = ctor.CreateCommand(meth_man_pkg + ".PublishMethodologyCommand")
        cmd.Set("MethodologyName", meth_name)
        cmd.Set("MinPortCount", "0")
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

        plLogger.LogInfo("end")

        return meth_name, name_dict

    @staticmethod
    def check_txml_values(txml, test_inst, mac, enable_vlan, vlan, ip, port_map, meth_name):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        stc_sys = CStcSystem.Instance()
        install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                   mgr_const.MM_TEST_METH_DIR)
        test_meth_dir = os.path.join(install_dir, meth_name)
        assert os.path.exists(test_meth_dir)
        test_case_dir = os.path.join(test_meth_dir, mgr_const.MM_TEST_CASE_SUBDIR)
        assert os.path.exists(test_case_dir)

        # Check the defaults in the TXML file
        txml_tree = etree.parse(os.path.join(test_case_dir, txml))
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
                cmd_prop_name = \
                    "spirent.methodology.ipv4networkprofilegroupcommand"
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
                        if "macaddr" in prop_id:
                            plLogger.LogInfo(" MAC addr...")
                            assert prop_val.lower() == mac.lower()
                            prop_count = prop_count + 1
                        elif "enablevlan" in prop_id:
                            plLogger.LogInfo(" Enable VLAN...")
                            assert prop_val.lower() == str(enable_vlan).lower()
                            prop_count = prop_count + 1
                        elif "vlanid" in prop_id:
                            plLogger.LogInfo(" vlanid...")
                            assert prop_val == str(vlan)
                            prop_count = prop_count + 1
                        elif "ipv4addr" in prop_id:
                            plLogger.LogInfo(" ipv4addr...")
                            assert prop_val == ip
                            prop_count = prop_count + 1
        assert found_name is True
        assert prop_count == 4
        if port_map is not None:
            assert port_count == len(port_map.keys())
        plLogger.LogInfo("end")

    def d_test_save_test_case(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        # TODO: Fix this once the test case work is finished
        if True:
            plLogger.LogWarn("Fix me after test cases have been repaired.")
            return
        ctor = CScriptableCreator()
        meth_name = "TestMeth_SaveTestCase"

        stc_sys = CStcSystem.Instance()
        meth_man_pkg = "spirent.methodology.manager"

        # Defaults
        mac_addr = "00:01:94:00:00:01"
        enable_vlan = False
        vlan_id = 100
        ipv4_addr = "192.85.1.3"

        plLogger.LogInfo("Create and export the test")
        test_name, name_dict = TestSaveTestCase.make_fake_test_pkg(mac_addr,
                                                                   enable_vlan,
                                                                   vlan_id,
                                                                   ipv4_addr,
                                                                   "",
                                                                   meth_name)
        plLogger.LogInfo("name_dict: " + str(name_dict))
        plLogger.LogInfo("test_name: " + test_name)

        new_mac = "00:01:95:CC:CC:05"
        new_enable_vlan = "true"
        new_vlan = "541"
        new_ip = "182.0.0.1"

        # Create JSON string with new defaults
        json_input = "{ \"ports\" : {}, \"params\" : {\"" + name_dict["MacAddr"] + "\" : \"" + \
                     new_mac + "\"," + \
                     " \"" + name_dict["EnableVlan"] + "\" : \"" + new_enable_vlan + "\"," + \
                     " \"" + name_dict["VlanId"] + "\" : \"" + new_vlan + "\"," + \
                     " \"" + name_dict["Ipv4Addr"] + "\" : \"" + new_ip + "\" } }"

        plLogger.LogInfo("Execute save test with json_input: \n" + json_input)

        # Change the defaults in "original" TXML by setting TestCaseName to ""
        cmd = ctor.CreateCommand(meth_man_pkg + ".SaveTestCaseCommand")
        cmd.Set("TestMethodologyName", test_name)
        cmd.Set("InputJson", json_input)
        cmd.Set("TestCaseName", "")
        cmd.Execute()
        cmd.MarkDelete()

        # Check the TXML file exists
        install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                   mgr_const.MM_TEST_METH_DIR)
        test_meth_dir = os.path.join(install_dir, meth_name)
        assert os.path.exists(test_meth_dir)
        test_case_dir = os.path.join(test_meth_dir, mgr_const.MM_TEST_CASE_SUBDIR)
        assert os.path.exists(test_case_dir)
        file_list = os.listdir(test_case_dir)
        assert len(file_list) == 1
        meta_file = file_list[0]
        assert meta_file == mgr_const.MM_META_FILE_NAME

        # Check TXML defaults
        plLogger.LogInfo("check original txml has new values")
        TestSaveTestCase.check_txml_values(meta_file,
                                           meta_man.TEST_INSTANCE_ORIGINAL,
                                           new_mac,
                                           new_enable_vlan,
                                           new_vlan,
                                           new_ip,
                                           None,
                                           meth_name)
        # Clean up anything that might be left
        meth_handle = UnitTestUtils.get_methodology_handle(meth_name)
        UnitTestUtils.cleanup_methodology(meth_handle)
        plLogger.LogInfo("end")

    def d_test_save_as_test_case_with_ports(self, stc):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogInfo("begin")
        # TODO: Fix this once the test case work is finished
        if True:
            plLogger.LogWarn("Fix me after test cases have been repaired.")
            return
        ctor = CScriptableCreator()
        meth_name = "TestMeth_SaveAsTestCase"

        stc_sys = CStcSystem.Instance()
        meth_man_pkg = "spirent.methodology.manager"

        # Defaults
        port_loc = "//10.14.16.20/2/1"
        mac_addr = "00:01:94:00:00:01"
        enable_vlan = False
        vlan_id = 100
        ipv4_addr = "192.85.1.3"

        plLogger.LogInfo("Create a test package")
        test_name, name_dict = TestSaveTestCase.make_fake_test_pkg(mac_addr,
                                                                   enable_vlan,
                                                                   vlan_id,
                                                                   ipv4_addr,
                                                                   port_loc,
                                                                   meth_name)
        # Build a port_map for validation (flip the name_dict)
        port_map = {}
        port_map[name_dict[port_loc]] = port_loc

        plLogger.LogInfo("Import the methodology " + test_name)
        # Import the test methodology (make available)
        cmd = ctor.CreateCommand(meth_man_pkg + ".ImportTestCommand")
        cmd.Set("fileName", test_name + ".stm")
        cmd.Execute()
        cmd.MarkDelete()

        plLogger.LogInfo("Verify that the TXML file exists after import")
        # Check the TXML file exists
        install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                   mgr_const.MM_TEST_METH_DIR)
        test_meth_dir = os.path.join(install_dir, meth_name)
        assert os.path.exists(test_meth_dir)
        test_case_dir = os.path.join(test_meth_dir, mgr_const.MM_TEST_CASE_SUBDIR)
        assert os.path.exists(test_case_dir)
        file_list = os.listdir(test_case_dir)
        assert len(file_list) == 1
        meta_file = file_list[0]
        assert meta_file == mgr_const.MM_META_FILE_NAME

        plLogger.LogInfo("Verify the TXML file contents haven't changed")
        # Check TXML defaults
        TestSaveTestCase.check_txml_values(meta_file,
                                           meta_man.TEST_INSTANCE_ORIGINAL,
                                           mac_addr,
                                           enable_vlan,
                                           vlan_id, ipv4_addr,
                                           port_map,
                                           meth_name)

        new_port_loc = "//10.14.16.27/2/1"
        new_mac = "00:01:95:CC:CC:0s"
        new_enable_vlan = "true"
        new_vlan = "541"
        new_ip = "182.0.0.1"

        # New port_map (for validation)
        new_port_map = {}
        new_port_map[name_dict[port_loc]] = new_port_loc

        # Create JSON string with new defaults
        json_input = "{\"ports\" : {\"" + name_dict[port_loc] + "\" : \"" + \
                     new_port_loc + "\"},\"params\" : {\"" + \
                     name_dict["MacAddr"] + "\" : \"" + new_mac + "\"," + \
                     " \"" + name_dict["EnableVlan"] + "\" : \"" + new_enable_vlan + "\"," + \
                     " \"" + name_dict["VlanId"] + "\" : \"" + new_vlan + "\"," + \
                     " \"" + name_dict["Ipv4Addr"] + "\" : \"" + new_ip + "\" }}"

        plLogger.LogInfo("Execute SaveTestCaseCommand with json_input: \n" + json_input)

        # Create a new "instance" of the testcase
        new_test_case = "MyNewTestCase"
        cmd = ctor.CreateCommand(meth_man_pkg + ".SaveTestCaseCommand")
        cmd.Set("TestMethodologyName", test_name)
        cmd.Set("InputJson", json_input)
        cmd.Set("TestCaseName", new_test_case)
        cmd.Execute()

        # Get the TXML file path
        new_txml_file_path = cmd.Get("TxmlFileName")
        new_txml_file = os.path.split(new_txml_file_path)[-1]
        cmd.MarkDelete()

        # Check the TXML file exists
        install_dir = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                   mgr_const.MM_TEST_METH_DIR)
        test_meth_dir = os.path.join(install_dir, meth_name)
        assert os.path.exists(test_meth_dir)
        test_case_dir = os.path.join(test_meth_dir, mgr_const.MM_TEST_CASE_SUBDIR)
        assert os.path.exists(test_case_dir)
        file_list = os.listdir(test_case_dir)
        assert len(file_list) > 1
        assert new_txml_file in file_list
        assert mgr_const.MM_META_FILE_NAME in file_list

        plLogger.LogInfo("Check the new saved file")
        TestSaveTestCase.check_txml_values(new_txml_file, new_test_case, new_mac,
                                           new_enable_vlan, new_vlan, new_ip,
                                           new_port_map, meth_name)
        plLogger.LogInfo("Verify the original hasn't changed")
        TestSaveTestCase.check_txml_values(mgr_const.MM_META_FILE_NAME,
                                           meta_man.TEST_INSTANCE_ORIGINAL, mac_addr,
                                           enable_vlan, vlan_id,
                                           ipv4_addr, port_map, meth_name)
        # Clean up anything that might be left from a previous run
        meth_handle = UnitTestUtils.get_methodology_handle(meth_name)
        UnitTestUtils.cleanup_methodology(meth_handle)
        plLogger.LogInfo("end")
