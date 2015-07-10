from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
sys.path.append(os.path.join(os.getcwd(), "STAKCommands"))
import spirent.methodology.manager.ConfigMethodologyTestCommand as ConfigCmd
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology.manager"


def remove_testscript(script_full_path):
    success = False
    try:
        os.remove(script_full_path)
        script_comp_full_path = script_full_path + "c"
        if os.path.exists(script_comp_full_path):
            os.remove(script_comp_full_path)
        success = True
    finally:
        pass
    return success


def write_testscript(script_filename, errorProcFunction=False):
    success = False
    try:
        plLogger = PLLogger.GetLogger('methodology')
        meth_home = meth_man_utils.get_methodology_base_dir()
        plLogger.LogInfo("meth_home: " + str(meth_home))
        script_dir = os.path.join(meth_home, "Scripts")
        plLogger.LogInfo("script_dir: " + str(script_dir))
        script_full_path = os.path.join(script_dir, script_filename)
        plLogger.LogInfo("script_full_path: " + str(script_full_path))
        with open(script_full_path, "w") as f:
            if errorProcFunction:
                f.write(get_error_calc_addr_script_contents())
            else:
                f.write(get_calc_addr_script_contents())
        success = True
    finally:
        pass
    if success:
        return script_full_path
    # We failed, remove what files we wrote and return None...
    remove_testscript(script_full_path)
    return None


def get_calc_addr_script_contents():
    return '''
def calc_addr(input_dict):
    output_dict = {"addr_next": "idk", "bgp_enable_count": str(len(input_dict["bgp_enables"]))}
    assert "addr_start" in input_dict
    assert "addr_step" in input_dict
    assert "bgp_enables" in input_dict
    assert input_dict["addr_start"] == "198.18.1.2"
    assert input_dict["addr_step"] == "0.0.1.0"
    assert len(input_dict["bgp_enables"]) == 3
    return output_dict, ""
'''


def get_error_calc_addr_script_contents():
    return '''
def calc_addr(input_dict):
    return None, "Error running calc_addr"
'''


def test_map_var_to_key(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_map_var_to_key")
    d = [{"script_input_key": "v1", "src_prop_id": "pid.1"},
         {"script_input_key": "v2", "src_prop_id": "pid.2"},
         {"script_input_key": "v3", "constant": "konst"},
         {"script_input_key": "v4", "dict": {"k": "v"}}
         ]
    m = ConfigCmd.map_var_to_key(d)
    assert m == {"v1": "pid.1", "v2": "pid.2", "v3": "konst", "v4": {"k": "v"}}
    return


def test_substitute_prop_ids(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_map_var_to_key")
    kvs = {"p.1": "_p1_", "p.2": "_p2_"}
    d = {"v1": "p.1",
         "v2": "p.2",
         "v3": "konst",
         "v4": {"v11": "p.1",
                "v12": [{"v21a": "p.2", "v21b": "kanst"}]
                }
         }
    s = ConfigCmd.substitute_prop_ids(d, kvs)
    assert s is None
    assert d == {"v1": "_p1_",
                 "v2": "_p2_",
                 "v3": "konst",
                 "v4": {"v11": "_p1_",
                        "v12": [{"v21a": "_p2_", "v21b": "kanst"}]
                        }
                 }
    return


def test_run_the_proc_func(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_run_the_proc_func")
    meta_json = get_sample_2544_json()
    err_str, meta = json_utils.load_json(meta_json)
    input = {"addr_start": "198.18.1.2", "addr_step": "0.0.1.0", "bgp_enables": ["1", "2", "3"]}
    pf0 = meta["processing_functions"][0]

    # Run with missing script file
    output_dict, err_str = ConfigCmd.run_the_proc_func(pf0, input)
    assert err_str == "Failed to find script: ConfigMethodologyTestCommandTestScript.py"

    # Create the script file with proc function that returns error
    script_filename = meta["processing_functions"][0]["script_filename"]
    script_full_path = write_testscript(script_filename, True)
    assert script_full_path is not None
    output_dict, err_str = ConfigCmd.run_the_proc_func(pf0, input)
    assert err_str == "External script: ConfigMethodologyTestCommandTestScript running calc_addr " + \
                      "failed with: Error running calc_addr  Input was: {'bgp_enables': " + \
                      "['1', '2', '3'], 'addr_start': '198.18.1.2', 'addr_step': '0.0.1.0'}"
    assert remove_testscript(script_full_path)

    # Create the script file with valid proc function
    script_full_path = write_testscript(script_filename)
    assert script_full_path is not None
    output_dict, err_str = ConfigCmd.run_the_proc_func(pf0, input)
    assert not err_str
    assert "addr_next" in output_dict
    assert output_dict["addr_next"] == "idk"
    assert remove_testscript(script_full_path)
    return


def test_process_functions(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_process_functions")
    meta_json = get_sample_2544_json()
    err_str, meta = json_utils.load_json(meta_json)
    assert not err_str
    kv_dict = {"CommandAddressStartValue": "198.18.1.2",
               "CommandAddressStepValue": "0.0.1.0",
               "LeftBgpEnables": ["1", "22", "333"]
               }

    # Run with missing script file
    err_str = ConfigCmd.process_functions(meta, kv_dict)
    assert err_str == "Failed to find script: ConfigMethodologyTestCommandTestScript.py"

    # Create the script file and run
    script_filename = meta["processing_functions"][0]["script_filename"]
    script_full_path = write_testscript(script_filename)
    assert script_full_path is not None
    err_str = ConfigCmd.process_functions(meta, kv_dict)
    assert not err_str
    assert remove_testscript(script_full_path)
    assert "cmd1.addr.1" in kv_dict
    assert kv_dict["cmd1.addr.1"] == "idk"
    assert "CommandAddressStartValue" in kv_dict
    assert kv_dict["CommandAddressStartValue"] == "198.18.1.2"
    assert "CommandAddressStepValue" in kv_dict
    assert kv_dict["CommandAddressStepValue"] == "0.0.1.0"
    return


def test_validate(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_validate")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    cmd = ctor.Create(PKG + ".ConfigMethodologyTestCommand", sequencer)
    ConfigCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Didn't specify anything
    res = ConfigCmd.validate(0, False)
    assert res == 'Could not find StmTestCase'

    # Create a fake StmTestCase
    meth_man = stc_sys.GetObject("StmMethodologyManager")
    if meth_man is None:
        meth_man = ctor.Create("StmMethodologyManager", stc_sys)
    assert meth_man
    test_meth = ctor.Create("StmMethodology", meth_man)
    test_case = ctor.Create("StmTestCase", test_meth)
    test_case.Set("TestCaseKey", "MyFakeTestCase")

    # Valid test case handle
    res = ConfigCmd.validate(test_case.GetObjectHandle(), False)
    assert res == ''


def test_get_meta_json_file_dict(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_get_meta_json_file_dict")
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    common_data_path = stc_sys.GetApplicationCommonDataPath()

    meth_name = "test_ConfigMethodologyTestCommand_test_get_meta_json_file_dict"
    test_name = "test_get_meta_json_file_dict"

    # Clean up the fake installed methodology (if it exists)
    if os.path.exists(os.path.join(common_data_path,
                                   mgr_const.MM_TEST_METH_DIR,
                                   meth_name)):
        meth_man_utils.methodology_rmdir(meth_name)

    # Create a fake installed methodology
    home_dir = meth_man_utils.get_methodology_home_dir()
    assert home_dir is not None
    meth_dir = meth_man_utils.methodology_mkdir(meth_name)
    assert meth_dir is not None
    test_dir = meth_man_utils.methodology_test_case_mkdir(meth_name, test_name)
    assert test_dir is not None

    cmd = ctor.Create(PKG + ".ConfigMethodologyTestCommand", sequencer)
    ConfigCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Call the function with a invalid file path
    meta_json_dict, err_str = ConfigCmd.get_meta_json_file_dict("fake path")
    assert meta_json_dict is None
    assert "does not exist" in err_str

    # Create an empty json file
    meta_json_file = os.path.join(test_dir, mgr_const.MM_META_JSON_FILE_NAME)
    f = open(meta_json_file, "w")
    f.close()

    # Call the function - should error and return None
    meta_json_dict, err_str = ConfigCmd.get_meta_json_file_dict(meta_json_file)
    assert meta_json_dict is None
    assert err_str == "Error reading methodology json file"

    # Write some invalid json to the file
    f = open(meta_json_file, "w")
    f.write("invalid_json")
    f.close()

    # Call the function - should error and return None
    meta_json_dict, err_str = ConfigCmd.get_meta_json_file_dict(meta_json_file)
    assert meta_json_dict is None
    assert err_str == "Methodology JSON is invalid or does not conform to the schema: " + \
                      "JSON string: invalid_json is not valid JSON."

    # Create a valid JSON file
    json_content = get_sample_2544_json()
    f = open(meta_json_file, "w")
    f.write(json_content)
    f.close()

    # Call the function to load the meta json file
    meta_json_dict, err_str = ConfigCmd.get_meta_json_file_dict(meta_json_file)
    # Verify the primary keys exist
    assert meta_json_dict is not None
    assert err_str == ""
    assert "methodology_key" in meta_json_dict.keys()
    assert "display_name" in meta_json_dict.keys()
    assert "version" in meta_json_dict.keys()
    assert "feature_ids" in meta_json_dict.keys()
    assert "port_groups" in meta_json_dict.keys()
    assert "property_groups" in meta_json_dict.keys()

    # Clean up the fake installed methodology
    if os.path.exists(os.path.join(common_data_path,
                                   mgr_const.MM_TEST_METH_DIR,
                                   meth_name)):
        meth_man_utils.methodology_rmdir(meth_name)


def test_parse_meta_json_keys_values(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_parse_meta_json_keys_values")

    # Valid methodology json
    input_json = get_sample_2544_json()

    attr1 = "CommandAddressStartValue"
    attr2 = "CommandAddressStepValue"
    attr3 = "TrafficDuration"
    attr4 = "ObjectIteratorCommand.ValueList"
    attr5 = "testGuiOnly"

    val1 = "198.18.1.2"
    val2 = "0.0.1.0"
    val3 = "60"
    val4 = ["64", "128", "256", "512", "1024", "1280", "1518"]
    val5 = "10"

    # Load the json
    err_str, json_dict = json_utils.load_json(input_json)
    assert err_str == ""
    assert json_dict is not None

    # Call the parse function
    key_val_dict, gui_key_val_dict = ConfigCmd.parse_meta_json_keys_values(json_dict)
    assert key_val_dict is not None
    assert gui_key_val_dict == {'testGuiOnly': '10'}
    plLogger.LogInfo("key_val_dict: " + str(key_val_dict))
    assert len(key_val_dict.keys()) == 7

    # Check the keys
    for kv_pair in zip([attr1, attr2, attr3, attr4, attr5], [val1, val2, val3, val4, val5]):
        assert kv_pair[0] in key_val_dict.keys()
        assert key_val_dict[kv_pair[0]] == kv_pair[1]


def test_parse_meta_json_keys_values_invalid_json(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_parse_meta_json_keys_values_invalid_json")

    # No property_groups
    input_json = '''{
        "methodology_key": "RFC2544THROUGHPUT",
        "display_name": "RFC 2544 Throughput Test",
        "version": "1-0-0",
        "feature_ids": [],
        "port_groups": []
    }'''

    # Load the json
    err_str, json_dict = json_utils.load_json(input_json)
    assert err_str == ""
    assert json_dict is not None

    # Call the parse function
    key_val_dict, gui_key_val_dict = ConfigCmd.parse_meta_json_keys_values(json_dict)
    assert key_val_dict == {}
    assert gui_key_val_dict == {}

    # No test_properties
    input_json = '''{
        "methodology_key": "RFC2544THROUGHPUT",
        "display_name": "RFC 2544 Throughput Test",
        "version": "1-0-0",
        "feature_ids": [],
        "port_groups": [],
        "property_groups": []
    }'''

    # Load the json
    err_str, json_dict = json_utils.load_json(input_json)
    assert err_str == ""
    assert json_dict is not None

    # Call the parse function
    key_val_dict, gui_key_val_dict = ConfigCmd.parse_meta_json_keys_values(json_dict)
    assert key_val_dict == {}
    assert gui_key_val_dict == {}

    # Missing property_value and empty test_properties
    input_json = '''{
        "methodology_key": "RFC2544THROUGHPUT",
        "display_name": "RFC 2544 Throughput Test",
        "version": "1-0-0",
        "feature_ids": [],
        "port_groups": [],
        "property_groups": [
            {
                "prop_id": "leftEndpointConfig",
                "display_name": "Left Endpoint Addressing",
                "test_properties": [
                    {
                        "prop_id": "CommandAddressStartValue"
                    },
                    {
                        "prop_id": "CommandAddressStepValue",
                        "property_value": "0.0.1.0"
                    }
                ]
            },
            {
                "prop_id": "test",
                "display_name": "Test",
                "test_properties": []
            }
        ]
    }'''

    attr1 = "CommandAddressStepValue"
    val1 = "0.0.1.0"

    # Load the json
    err_str, json_dict = json_utils.load_json(input_json)
    assert err_str == ""
    assert json_dict is not None

    # Call the parse function
    key_val_dict, gui_key_val_dict = ConfigCmd.parse_meta_json_keys_values(json_dict)
    assert key_val_dict is not None
    assert gui_key_val_dict == {}
    plLogger.LogInfo("key_val_dict: " + str(key_val_dict))
    assert len(key_val_dict.keys()) == 1

    # Check the keys
    for kv_pair in zip([attr1], [str(val1)]):
        assert kv_pair[0] in key_val_dict.keys()
        assert key_val_dict[kv_pair[0]] == kv_pair[1]


def test_generate_tagged_ports(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict_string = '''{
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "bring_online": true,
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right",
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ]
    }'''
    err_str, input_dict = json_utils.load_json(input_dict_string)
    assert err_str == ""

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)

    assert 2 == len(port_hnd_list)
    assert False is offline
    assert err_str == ""
    hnd_reg = CHandleRegistry.Instance()
    port_list = [hnd_reg.Find(hnd) for hnd in port_hnd_list]
    tag0 = port_list[0].GetObject('Tag', RelationType('UserTag'))
    tag1 = port_list[1].GetObject('Tag', RelationType('UserTag'))
    assert left_tag.GetObjectHandle() == tag0.GetObjectHandle()
    assert port_list[0].Get('Name').startswith('Left 1')
    assert port_list[0].Get('Location') == '//10.10.10.1/1/1'
    assert right_tag.GetObjectHandle() == tag1.GetObjectHandle()
    assert port_list[1].Get('Name').startswith('Right 1')
    assert port_list[1].Get('Location') == '//10.10.10.2/1/1'

    # Test the bring_online parameter
    input_dict_string = '''{
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "bring_online": false,
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right",
                "bring_online": true,
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ]
    }'''
    err_str, input_dict = json_utils.load_json(input_dict_string)
    assert err_str == ""

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)

    assert 2 == len(port_hnd_list)
    assert True is offline
    assert err_str == ""


def test_generate_tagged_ports_no_exposed(stc):
    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right",
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "No exposed config object found"


def test_generate_tagged_ports_no_port_groups(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Input missing required port_groups section"


def test_generate_tagged_ports_no_prop_id(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "name": "Left",
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "name": "Right",
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Port group missing required prop_id"


def test_generate_tagged_ports_empty_port_list(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left"
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right"
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Port group {} has empty port list"


def test_generate_tagged_ports_no_locations(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right",
                "ports": [
                    {
                        "doh": "10.10.10.2/1/1"
                    }
                ]
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Port group Right is missing location attribute"


def test_generate_tagged_ports_no_ep(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroupX",
                "name": "Right",
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Exposed property missing: RightPortGroupX"


def test_generate_tagged_ports_no_tag(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    # ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    # The sample didn't have everything, so this unit test will take the
    # minimum needed
    input_dict = {
        "port_groups": [
            {
                "prop_id": "LeftPortGroup",
                "name": "Left",
                "ports": [
                    {
                        "location": "10.10.10.1/1/1"
                    }
                ]
            },
            {
                "prop_id": "RightPortGroup",
                "name": "Right",
                "ports": [
                    {
                        "location": "10.10.10.2/1/1"
                    }
                ]
            }
        ],
    }

    port_hnd_list, offline, err_str = ConfigCmd.generate_tagged_ports(input_dict)
    assert port_hnd_list == []
    assert err_str == "Tag key missing: RightPortGroup"


def test_run(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin test_run")

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    common_data_path = stc_sys.GetApplicationCommonDataPath()

    # Create exposed properties for the ports
    project = stc_sys.GetObject('Project')
    left_tag = tag_utils.get_tag_object('Left_Port_Group')
    right_tag = tag_utils.get_tag_object('Right_Port_Group')
    ep_cfg = ctor.Create('ExposedConfig', project)
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'LeftPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(left_tag, RelationType('ScriptableExposedProperty'))
    ep = ctor.Create('ExposedProperty', ep_cfg)
    ep.Set('EPNameId', 'RightPortGroup')
    ep.Set('EPClassId', 'tag')
    ep.Set('EPPropertyId', 'scriptable.name')
    ep.AddObject(right_tag, RelationType('ScriptableExposedProperty'))

    meth_name = "test_ConfigMethodologyTestCommand_test_run"
    test_name = "test_run"

    # Clean up the fake installed methodology (if it exists)
    if os.path.exists(os.path.join(common_data_path,
                                   mgr_const.MM_TEST_METH_DIR,
                                   meth_name)):
        meth_man_utils.methodology_rmdir(meth_name)

    # Create a fake installed methodology
    home_dir = meth_man_utils.get_methodology_home_dir()
    assert home_dir is not None
    meth_dir = meth_man_utils.methodology_mkdir(meth_name)
    assert meth_dir is not None
    test_dir = meth_man_utils.methodology_test_case_mkdir(meth_name, test_name)
    assert test_dir is not None

    cmd = ctor.Create(PKG + ".ConfigMethodologyTestCommand", sequencer)
    ConfigCmd.get_this_cmd = MagicMock(return_value=cmd)
    ConfigCmd.load_config = MagicMock()
    # TODO: set it up so we don't have to mock this function
    ConfigCmd.set_active_test_case = MagicMock()

    # Create a valid JSON file
    json_content = get_sample_2544_json()
    meta_json_file = os.path.join(test_dir, mgr_const.MM_META_JSON_FILE_NAME)
    f = open(meta_json_file, "w")
    f.write(json_content)
    f.close()

    meth_man = stc_sys.GetObject("StmMethodologyManager")
    if meth_man is None:
        meth_man = ctor.Create("StmMethodologyManager", stc_sys)
    assert meth_man
    test_meth = ctor.Create("StmMethodology", meth_man)
    test_meth.Set("MethodologyKey", meth_name)
    test_case = ctor.Create("StmTestCase", test_meth)
    assert test_case is not None
    assert test_case.IsTypeOf("StmTestCase")
    test_case.Set("Path", test_dir)
    test_case.Set("TestCaseKey", test_name)

    # Add MethodologyGroupCommand to the sequencer
    meth_group_cmd = ctor.Create(PKG + ".MethodologyGroupCommand", sequencer)
    sequencer.SetCollection("CommandList", [meth_group_cmd.GetObjectHandle()])
    key_value_json = meth_group_cmd.Get("KeyValueJson")
    assert key_value_json == ""

    # Call the run function with invalid StmTestCase handle
    res = ConfigCmd.run(test_meth.GetObjectHandle(), False)
    assert not res
    assert 'Was unable to find StmTestCase with handle' in cmd.Get("Status")
    cmd.Set("Status", '')

    # Call the run function with missing proc function script file
    res = ConfigCmd.run(test_case.GetObjectHandle(), False)
    assert not res
    assert cmd.Get("Status") == 'Failed to find script: ConfigMethodologyTestCommandTestScript.py'
    cmd.Set("Status", '')

    # Create the proc function script file
    err_str, meta = json_utils.load_json(json_content)
    assert err_str == ""
    script_filename = meta["processing_functions"][0]["script_filename"]
    script_full_path = write_testscript(script_filename)
    assert script_full_path is not None

    # Call the run function with valid StmTestCaseHandle
    res = ConfigCmd.run(test_case.GetObjectHandle(), False)
    assert res
    assert cmd.Get("Status") == ''

    # The KeyValueJson should be populated after running the command
    key_value_json = meth_group_cmd.Get("KeyValueJson")
    assert key_value_json != ""
    err_str, key_value_dict = json_utils.load_json(key_value_json)
    assert err_str == ""
    assert key_value_dict is not None

    assert len(key_value_dict.items()) == 8
    assert key_value_dict["CommandAddressStartValue"] == "198.18.1.2"
    assert key_value_dict["CommandAddressStepValue"] == "0.0.1.0"
    assert key_value_dict["TrafficDuration"] == "60"
    vlist = key_value_dict["ObjectIteratorCommand.ValueList"]
    assert type(vlist) is list
    sitems = set(vlist) & set(["64", "128", "256", "512", "1024", "1280", "1518"])
    assert len(sitems) == 7
    assert key_value_dict["cmd1.bgp.count"] == "3"

    # Clear out KeyValueJson in the meth group command
    meth_group_cmd.Set("KeyValueJson", "")
    key_value_json = meth_group_cmd.Get("KeyValueJson")
    assert key_value_json == ""

    assert remove_testscript(script_full_path)

    # Clean up the fake installed methodology
    if os.path.exists(os.path.join(common_data_path,
                                   mgr_const.MM_TEST_METH_DIR,
                                   meth_name)):
        meth_man_utils.methodology_rmdir(meth_name)


def get_sample_2544_json():
    return '''{
        "methodology_key": "RFC2544THROUGHPUT",
        "display_name": "RFC 2544 Throughput Test",
        "version": "1-0-0",
        "feature_ids": ["test"],
        "port_groups": [
            {
                "prop_id":"LeftPortGroup",
                "name":"Left",
                "bring_online":false,
                "ports":[
                    {
                        "location":"Offline/1/1"
                    }
                ]
            },
            {
                "prop_id":"RightPortGroup",
                "name":"Right",
                "bring_online":false,
                "ports":[
                    {
                        "location":"Offline/1/1"
                    }
                ]
            }
        ],
        "property_groups": [
            {
                "prop_id": "leftEndpointConfig",
                "display_name": "Left Endpoint Addressing",
                "test_properties": [
                    {
                        "prop_id": "CommandAddressStartValue",
                        "property_value": "198.18.1.2"
                    },
                    {
                        "prop_id": "CommandAddressStepValue",
                        "property_value": "0.0.1.0"
                    },
                    {
                        "prop_id": "LeftBgpEnables",
                        "property_value": ["True", "False", "False"]
                    },
                    {
                        "prop_id": "LeftIsisEnables",
                        "property_value": ["True", "True", "True"]
                    }
                ]
            },
            {
                "prop_id": "trafficConfig",
                "display_name": "Traffic Configuration",
                "test_properties": [
                    {
                        "prop_id": "TrafficDuration",
                        "property_value": "60"
                    },
                    {
                        "prop_id": "ObjectIteratorCommand.ValueList",
                        "property_value": ["64","128","256","512","1024","1280","1518"]
                    },
                    {
                        "prop_id": "testGuiOnly",
                        "property_value": "10",
                        "gui_only": true
                    }
                ]
            }
        ],
        "processing_functions": [
            {
                "script_filename" : "ConfigMethodologyTestCommandTestScript.py",
                "entry_function" : "calc_addr",
                "output" : [
                    {
                        "script_output_key" : "addr_next",
                        "ep_key" : "cmd1.addr.1"
                    },
                    {
                        "script_output_key": "bgp_enable_count",
                        "ep_key": "cmd1.bgp.count"
                    }
                ],
                "input" : [
                    {
                        "script_input_key": "addr_start",
                        "src_prop_id": "CommandAddressStartValue"
                    },
                    {
                        "script_input_key": "addr_step",
                        "src_prop_id": "CommandAddressStepValue"
                    },
                    {
                        "script_input_key": "bgp_enables",
                        "src_prop_id": "LeftBgpEnables"
                    }
                ]
            }
        ]
    }'''


def get_sample_2544_json_basic():
    return '''{
        "methodology_key": "RFC2544THROUGHPUT_SAMPLE_BASIC",
        "display_name": "RFC 2544 Throughput Test",
        "version": "1-0-0",
        "feature_ids": ["test"],
        "port_groups": [
            {
                "prop_id":"LeftPortGroup",
                "name":"Left",
                "bring_online":false,
                "ports":[
                    {
                        "location":"Offline/1/1"
                    }
                ]
            }
        ],
        "property_groups": [
            {
                "prop_id": "EndpointConfig",
                "display_name": "Endpoint Addressing",
                "test_properties": [
                    {
                        "prop_id": "AddressStartValue",
                        "property_value": "1.1.1.1"
                    }
                ]
            }
        ]
    }'''
