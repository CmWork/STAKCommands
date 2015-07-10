from StcIntPythonPL import *
import os
import sys
import xml.etree.ElementTree as etree
from ..utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from ..utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from unit_test_utils import UnitTestUtils
sys.path.append(os.path.join(os.getcwd(), "STAKCommands",
                             "spirent", "methodology"))
import manager.RunStmTestCaseCommand as RunCmd


def disabled_test_load_with_json(stc):
    plLogger = PLLogger.GetLogger("test_load_with_json")
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    hnd_reg = CHandleRegistry.Instance()

    cmd_name = "Ipv4NetworkProfileGroupCommand"
    pkg_name = "spirent.methodology."
    create_cmd = ctor.CreateCommand(pkg_name + cmd_name)

    insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
    insert_cmd.SetCollection("CommandList", [create_cmd.GetObjectHandle()])
    insert_cmd.Execute()

    exposedConfig = ctor.Create("ExposedConfig", project)

    prop1 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop1, create_cmd, pkg_name + cmd_name, "DeviceCount")
    prop2 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop2, create_cmd, pkg_name + cmd_name, "RouterId")
    prop3 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop3, create_cmd, pkg_name + cmd_name, "Ipv4Addr")

    test_name = "TestLoadWithJson"
    test_key = "JsonTestKey"
    # Delete the methodology we are about to create just in case
    # there was an error on a previous run.
    test_meth_obj = meth_man_utils.get_stm_methodology_from_key(test_key)

    if test_meth_obj:
        # Delete installed test methodology
        cmd = ctor.CreateCommand("spirent.methodology.manager."
                                 "DeleteMethodologyCommand")
        cmd.Set("StmMethodology", test_meth_obj.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

    # Publish as a methodology
    cmd = ctor.CreateCommand("spirent.methodology.manager.PublishMethodologyCommand")
    cmd.Set("MethodologyName", test_name)
    cmd.Set("MethodologyKey", test_key)
    cmd.Set("MinPortCount", "0")
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

    meth_handle = UnitTestUtils.get_methodology_handle(test_name)
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
    cmd = ctor.CreateCommand("spirent.methodology.manager."
                             "LoadTestMethodologyCommand")
    meth = meth_man_utils.get_stm_methodology_from_key(test_key)
    assert meth is not None
    cmd.Set("StmMethodology", meth.GetObjectHandle())
    cmd.Set("InputJson", json_input)
    cmd.Execute()

    # Check the command sequence
    cmd_hnd_list = sequencer.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1

    tlgc = hnd_reg.Find(cmd_hnd_list[0])
    assert tlgc is not None
    assert tlgc.IsTypeOf(pkg_name + "manager.MethodologyGroupCommand") is True

    cmd_hnd_list = tlgc.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1

    create_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert create_cmd.IsTypeOf(pkg_name + cmd_name) is True

    # Check defaults
    assert create_cmd.Get("DeviceCount") == 1
    assert create_cmd.Get("RouterId") == "192.0.0.1"
    assert create_cmd.Get("Ipv4Addr") == "192.85.1.3"

    # Execute a MethodologyGroupCommand
    tlgc2 = ctor.CreateCommand(pkg_name + "manager.MethodologyGroupCommand")
    tlgc2.Set("InputJson", tlgc.Get("InputJson"))
    tlgc2.Execute()
    tlgc2.MarkDelete()

    # Check the new defaults
    assert create_cmd.Get("DeviceCount") == 101
    assert create_cmd.Get("RouterId") == "188.0.0.5"
    assert create_cmd.Get("Ipv4Addr") == "172.0.17.5"

    # Clean up
    meth = meth_man_utils.get_stm_methodology_from_key(test_key)
    cmd = ctor.CreateCommand("spirent.methodology.manager."
                             "DeleteMethodologyCommand")
    cmd.Set("StmMethodology", meth.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()
    plLogger.LogInfo("end")


def test_parse_txml_keys_values(stc):
    plLogger = PLLogger.GetLogger("test_parse_txml_keys_values")
    plLogger.LogInfo("begin")

    attr1 = "Object.Property1"
    attr2 = "Object.Property2"
    attr3 = "Object.Property3"
    attr4 = "Object.Property4"

    val1 = 12
    val2 = "twelve"
    val3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    val4 = "12"

    # Input XML
    input_xml = str(
        "<test>" +
        "<wizard displayName=\"Unit Test Parse Key Vals\" " +
        "description=\"test parsing key values in TXML\" " +
        "image=\"\">" +
        "<page displayName=\"stuff\" description=\"descript\" >" +
        "<group displayName=\"gbox\">" +
        "<property id=\"" + attr1 + "\" value=\"" + str(val1) + "\" " +
        "displayName=\"attr1\" />" +
        "<property id=\"" + attr2 + "\" value=\"" + str(val2) + "\" " +
        "displayName=\"attr2\" />" +
        "<property id=\"" + attr3 + "\" value=\"" + str(val3) + "\" " +
        "displayName=\"attr3\" />" +
        "</group></page>" +
        "<page displayName=\"page2\" description=\"descript\">" +
        "<group displayName=\"gbox\">" +
        "<property id=\"" + attr4 + "\" value=\"" + str(val4) + "\" " +
        "displayName=\"attr4\" />" +
        "</group></page></wizard></test>")

    plLogger.LogInfo("input_xml: " + str(input_xml))
    root = etree.fromstring(input_xml)
    assert root is not None

    key_val_dict, gui_key_val_dict = RunCmd.parse_txml_keys_values(root)
    assert key_val_dict is not None
    assert gui_key_val_dict == {}
    plLogger.LogInfo("key_val_dict: " + str(key_val_dict))
    assert len(key_val_dict.keys()) == 4

    # Check the keys
    for kv_pair in zip([attr1, attr2, attr3, attr4],
                       [str(val1), str(val2), str(val3), str(val4)]):
        assert kv_pair[0] in key_val_dict.keys()
        assert key_val_dict[kv_pair[0]] == kv_pair[1]


def test_parse_txml_table_keys_values(stc):
    plLogger = PLLogger.GetLogger("test_parse_table_txml_keys_values")
    plLogger.LogInfo("begin")

    attr1 = "Object.Property1"
    attr2 = "Object.Property2"
    attr3 = "Object.Property3"
    attr4 = "Object.Property4"

    val1 = 12
    val2 = "twelve"
    val3 = True
    val4 = "331"

    # Input XML
    input_xml = str(
        "<test>" +
        "<wizard displayName=\"Unit Test Parse Key Vals\" " +
        "description=\"test parsing key values in TXML\" " +
        "image=\"\">" +
        "<page displayName=\"stuff\" description=\"descript\" >" +
        "<group displayName=\"gbox\">" +
        "<property id=\"" + attr1 + "\" value=\"" + str(val1) + "\" " +
        "displayName=\"attr1\">" +
        "<data>13</data>" +
        "<data>14</data>" +
        "<data>15.5</data>" +
        "</property>" +
        "<property id=\"" + attr2 + "\" value=\"" + str(val2) + "\" " +
        "displayName=\"attr2\">" +
        "<data>thirteen</data>" +
        "<data>fourteen</data>" +
        "<data>fifteen and a half</data>" +
        "</property>" +
        "<property id=\"" + attr3 + "\" value=\"" + str(val3) + "\" " +
        "displayName=\"attr3\">" +
        "<data>True</data>" +
        "<data>False</data>" +
        "<data>True</data>" +
        "</property>" +
        "<property id=\"" + attr4 + "\" value=\"" + str(val4) + "\" " +
        "displayName=\"attr4\" />" +
        "</group></page></wizard></test>")

    plLogger.LogInfo("input_xml: " + str(input_xml))
    root = etree.fromstring(input_xml)
    assert root is not None

    key_val_dict, gui_key_val_dict = RunCmd.parse_txml_keys_values(root)
    assert key_val_dict is not None
    assert gui_key_val_dict == {}
    plLogger.LogInfo("key_val_dict: " + str(key_val_dict))
    assert len(key_val_dict.keys()) == 4

    # Check the key-value pairs (single property)
    assert attr4 in key_val_dict.keys()
    assert key_val_dict[attr4] == val4

    # Check the key-value pairs (table)
    for exp_kv_pair in zip([attr1, attr2, attr3],
                           [["13", "14", "15.5"],
                            ["thirteen", "fourteen",
                             "fifteen and a half"],
                            ["True", "False", "True"]]):
        assert exp_kv_pair[0] in key_val_dict.keys()
        assert key_val_dict[exp_kv_pair[0]] == exp_kv_pair[1]


def test_parse_port_groups():
    plLogger = PLLogger.GetLogger("test_parse_port_groups")
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    # project = stc_sys.GetObject("Project")
    # sequencer = CStcSystem.Instance().GetObject("Sequencer")
    # hnd_reg = CHandleRegistry.Instance()
    common_data_path = stc_sys.GetApplicationCommonDataPath()

    meth_name = "test_RunStmTestCaseCommand_test_parse_port_groups"
    test_name = "test_parse_port_groups"

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

    # Create a fake TXML file
    txml_content = get_test_txml()
    txml_file = os.path.join(test_dir, mgr_const.MM_META_FILE_NAME)
    f = open(txml_file, "w")
    f.write(txml_content)
    f.close()

    meth_man = stc_sys.GetObject("StmMethodologyManager")
    if meth_man is None:
        meth_man = ctor.Create("StmMethodologyManager", stc_sys)
    assert meth_man
    test_meth = ctor.Create("StmMethodology", meth_man)
    test_case = ctor.Create("StmTestCase", test_meth)
    test_case.Set("Path", txml_file)

    root = RunCmd.get_txml_file_root(txml_file)
    assert root is not None

    port_group_dict = RunCmd.parse_txml_port_groups(root)

    assert port_group_dict is not None
    assert len(port_group_dict.keys()) == 2
    assert "Tag.Name.1632" in port_group_dict.keys()
    assert "Tag.Name.1633" in port_group_dict.keys()

    assert len(port_group_dict["Tag.Name.1632"]) == 2
    assert "//10.14.16.27/1/1" in port_group_dict["Tag.Name.1632"]
    assert "//10.14.16.27/1/2" in port_group_dict["Tag.Name.1632"]

    assert len(port_group_dict["Tag.Name.1633"]) == 2
    assert "//10.14.16.27/2/1" in port_group_dict["Tag.Name.1633"]
    assert "//10.14.16.27/2/2" in port_group_dict["Tag.Name.1633"]

    # Test the list constructor for the MethdologyGroupCommand
    prop_val = RunCmd.build_port_group_list(port_group_dict)
    plLogger.LogInfo("key_val_list: " + str(prop_val))
    assert len(prop_val) == 2
    assert "Tag.Name.1632=//10.14.16.27/1/1,//10.14.16.27/1/2" in prop_val
    assert "Tag.Name.1633=//10.14.16.27/2/1,//10.14.16.27/2/2" in prop_val

    # Clean up the fake installed methodology
    if os.path.exists(os.path.join(common_data_path,
                                   mgr_const.MM_TEST_METH_DIR,
                                   meth_name)):
        meth_man_utils.methodology_rmdir(meth_name)


def test_create_and_tag_ports(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    target1 = ctor.Create('Tag', tags)
    target1.Set("Name", "EastPortGroup")
    target2 = ctor.Create('Tag', tags)
    target2.Set("Name", "WestPortGroup")

    # Expose properties (loaded at some other step)
    exposed_config = ctor.Create("ExposedConfig", project)

    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(target1, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", 'Tag')
    xp.Set("EPNameId", "Tag.Name.1")

    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(target2, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", 'Tag')
    xp.Set("EPNameId", "Tag.Name.2")

    port_list = ["Tag.Name.2=//offline/2/1,//offline/2/2", "Tag.Name.1=//1.2.3.4/1/1"]
    ports, offline = RunCmd.create_and_tag_ports(port_list)
    assert len(ports) == 3
    assert len(target2.GetObjects("Port", RelationType("UserTag", 1))) == 2
    assert len(target1.GetObjects("Port", RelationType("UserTag", 1))) == 1
    assert offline is True

    port_list = ["Tag.Name.2=//1.2.1.2/2/1", "Tag.Name.1=//1.2.3.4/1/1"]
    ports, offline = RunCmd.create_and_tag_ports(port_list)
    assert len(ports) == 2
    assert len(target2.GetObjects("Port", RelationType("UserTag", 1))) == 3
    assert len(target1.GetObjects("Port", RelationType("UserTag", 1))) == 2
    assert offline is False
    return


def test_parse_proc_funcs(stc):
    plLogger = PLLogger.GetLogger("test_parse_proc_funcs")

    pf_id = "procFunc1"
    ep_key1 = "Object.AlphaPlusBeta1"
    ep_key2 = "Object.AlphaTimesBeta200"
    ep_key3 = "Object.AlphaBetaAvg12"

    # Input XML
    input_xml = "<test>" + \
                "<processingFunctions>" + \
                "<processingFunction id=\"" + pf_id + "\" " + \
                "scriptFile=\"utProcFuncScript.py\" " + \
                "entryFunction=\"recombine_alpha_beta\">" + \
                "<input srcId=\"alpha\" scriptVarName=\"Alpha\" />" + \
                "<input srcId=\"beta\" />" + \
                "<input scriptVarName=\"myConst\" " + \
                "default=\"5\" />" + \
                "<output epKey=\"" + ep_key1 + "\" " + \
                "scriptVarName=\"AlphaPlusBeta\" />" + \
                "<output scriptVarName=\"AlphaTimesBeta\" " + \
                "epKey=\"" + ep_key2 + "\" />" + \
                "<output epKey=\"" + ep_key3 + "\" " + \
                "scriptVarName=\"AlphaBetaAvg\" />" + \
                "</processingFunction>" + \
                "</processingFunctions>" + \
                "</test>"
    root = etree.fromstring(input_xml)
    pf_dict = RunCmd.parse_txml_proc_funcs(root)

    plLogger.LogInfo("pf_dict: " + str(pf_dict))

    assert pf_dict is not None
    assert "id_list" in pf_dict.keys()
    assert pf_id in pf_dict.keys()

    assert "script" in pf_dict[pf_id].keys()
    assert pf_dict[pf_id]["script"] == "utProcFuncScript.py"
    assert "entry_fn" in pf_dict[pf_id].keys()
    assert pf_dict[pf_id]["entry_fn"] == "recombine_alpha_beta"

    assert "input_id_list" in pf_dict[pf_id].keys()
    assert len(pf_dict[pf_id]["input_id_list"]) == 3
    assert "in_1" in pf_dict[pf_id]["input_id_list"]
    assert "in_2" in pf_dict[pf_id]["input_id_list"]
    assert "in_3" in pf_dict[pf_id]["input_id_list"]

    assert "src_id" in pf_dict[pf_id]["in_1"].keys()
    assert pf_dict[pf_id]["in_1"]["src_id"] == "alpha"
    assert "script_var" in pf_dict[pf_id]["in_1"].keys()
    assert pf_dict[pf_id]["in_1"]["script_var"] == "Alpha"
    assert "default" in pf_dict[pf_id]["in_1"].keys()
    assert pf_dict[pf_id]["in_1"]["default"] is None

    assert "src_id" in pf_dict[pf_id]["in_2"].keys()
    assert pf_dict[pf_id]["in_2"]["src_id"] == "beta"
    assert "script_var" in pf_dict[pf_id]["in_2"].keys()
    assert pf_dict[pf_id]["in_2"]["script_var"] is None
    assert "default" in pf_dict[pf_id]["in_2"].keys()
    assert pf_dict[pf_id]["in_2"]["default"] is None

    assert "src_id" in pf_dict[pf_id]["in_3"].keys()
    assert pf_dict[pf_id]["in_3"]["src_id"] is None
    assert "script_var" in pf_dict[pf_id]["in_3"].keys()
    assert pf_dict[pf_id]["in_3"]["script_var"] == "myConst"
    assert "default" in pf_dict[pf_id]["in_3"].keys()
    assert pf_dict[pf_id]["in_3"]["default"] == "5"

    assert "output_id_list" in pf_dict[pf_id].keys()
    assert len(pf_dict[pf_id]["output_id_list"]) == 3
    assert "out_1" in pf_dict[pf_id]["output_id_list"]
    assert "out_2" in pf_dict[pf_id]["output_id_list"]
    assert "out_3" in pf_dict[pf_id]["output_id_list"]

    assert "ep_key" in pf_dict[pf_id]["out_1"].keys()
    assert pf_dict[pf_id]["out_1"]["ep_key"] == ep_key1
    assert "script_var" in pf_dict[pf_id]["out_1"].keys()
    assert pf_dict[pf_id]["out_1"]["script_var"] == "AlphaPlusBeta"

    assert "ep_key" in pf_dict[pf_id]["out_2"].keys()
    assert pf_dict[pf_id]["out_2"]["ep_key"] == ep_key2
    assert "script_var" in pf_dict[pf_id]["out_2"].keys()
    assert pf_dict[pf_id]["out_2"]["script_var"] == "AlphaTimesBeta"

    assert "ep_key" in pf_dict[pf_id]["out_3"].keys()
    assert pf_dict[pf_id]["out_3"]["ep_key"] == ep_key3
    assert "script_var" in pf_dict[pf_id]["out_3"].keys()
    assert pf_dict[pf_id]["out_3"]["script_var"] == "AlphaBetaAvg"


def test_run_txml_proc_func(stc):
    plLogger = PLLogger.GetLogger("test_run_txml_proc_func")

    mod_name = "unit_test_proc_funcs"
    pf_key = "procFunc1"
    pf_dict = {}
    pf_dict["id_list"] = [pf_key]
    pf_dict[pf_key] = {}
    pf_dict[pf_key]["script"] = "unit_test_proc_funcs" + ".py"
    pf_dict[pf_key]["entry_fn"] = "recombine_alpha_beta"
    pf_dict[pf_key]["input_id_list"] = ["in_1", "in_2", "in_3"]
    pf_dict[pf_key]["in_1"] = {"src_id": "alpha",
                               "script_var": "Alpha",
                               "default": None}
    pf_dict[pf_key]["in_2"] = {"src_id": "beta",
                               "script_var": None,
                               "default": None}
    pf_dict[pf_key]["in_3"] = {"src_id": None,
                               "script_var": "myConst",
                               "default": "5"}
    pf_dict[pf_key]["output_id_list"] = ["out_1", "out_2", "out_3"]
    pf_dict[pf_key]["out_1"] = {
        "ep_key": "Object.AlphaTimesBeta200",
        "script_var": "AlphaTimesBeta"}
    pf_dict[pf_key]["out_2"] = {
        "ep_key": "Object.AlphaBetaAvg12",
        "script_var": "AlphaBetaAvgPlusConst"}
    pf_dict[pf_key]["out_3"] = {
        "ep_key": "Object.AlphaPlusBeta1",
        "script_var": "AlphaPlusBeta"}

    kv_dict = {"someKey": "someVal",
               "anotherKey": "anotherVal"}
    gui_kv_dict = {"alpha": "5",
                   "beta": "10"}

    # Create unit test proc funcs file
    meth_home = meth_man_utils.get_methodology_base_dir()
    plLogger.LogInfo("meth_home: " + str(meth_home))
    script_dir = os.path.join(meth_home, "Scripts")
    plLogger.LogInfo("script_dir: " + str(script_dir))
    script_full_path = os.path.join(script_dir, mod_name + ".py")
    script_comp_full_path = os.path.join(script_dir, mod_name + ".pyc")
    plLogger.LogInfo("script_full_path: " + str(script_full_path))
    ret_val = False
    try:
        if not os.path.exists(script_dir):
            plLogger.LogInfo("making script dir...")
            os.makedirs(script_dir)
        with open(script_full_path, "w") as f:
            f.write(get_ut_proc_func_file_content())
        plLogger.LogInfo("wrote contents of file to " + str(script_full_path))
        ret_val = RunCmd.run_txml_proc_funcs(pf_dict, kv_dict, gui_kv_dict)
    finally:
        os.remove(script_full_path)
        if os.path.exists(script_comp_full_path):
            os.remove(script_comp_full_path)

    assert ret_val
    assert "someKey" in kv_dict.keys()
    assert "anotherKey" in kv_dict.keys()
    assert "Object.AlphaPlusBeta1" in kv_dict.keys()
    assert "Object.AlphaTimesBeta200" in kv_dict.keys()
    assert "Object.AlphaBetaAvg12" in kv_dict.keys()
    assert kv_dict["Object.AlphaPlusBeta1"] == "15"
    assert kv_dict["Object.AlphaTimesBeta200"] == "50"
    assert kv_dict["Object.AlphaBetaAvg12"] == "12.5"
    assert kv_dict["someKey"] == "someVal"
    assert kv_dict["anotherKey"] == "anotherVal"


def test_get_txml_proc_dict(stc):
    # Input XML
    input_xml = "<test>" + \
                "<processingFunctions>" + \
                "<processingDictionary inputDict='{\"test1\": \"blah1\"}'>" + \
                "</processingDictionary>" + \
                "<processingDictionary inputDict='{\"test2\": \"blah2\"}'>" + \
                "</processingDictionary>" + \
                "</processingFunctions>" + \
                "</test>"

    root = etree.fromstring(input_xml)
    input_dict_list = RunCmd.get_txml_proc_dicts(root)
    assert input_dict_list is not None
    assert len(input_dict_list) == 2
    assert input_dict_list[0]["test1"] == "blah1"
    assert input_dict_list[1]["test2"] == "blah2"


def test_parse_input_data(stc):
    kv_dict = {"someKey": "someVal",
               "anotherKey": ["one", "two"]}
    gui_kv_dict = {"weight": 5.0,
                   "beta": "10"}
    updated_input_dict = RunCmd.parse_input_data(get_original_input_dict(), kv_dict, gui_kv_dict)

    assert updated_input_dict["id"] == "Left.CreateProtocolMix.TableData"
    assert updated_input_dict["scriptFile"] == "txml_processing_functions.py"
    assert updated_input_dict["entryFunction"] == "config_table_data"
    customDict = {}
    customDict["EnableVlan"] = "someVal"
    customDict["Weight"] = 5.0
    assert updated_input_dict["input"]["customDict"] == customDict

    # Check interface dictionary list(ipv4 and eth)
    interfaceDict = updated_input_dict["input"]["interfaceDict"]
    assert len(interfaceDict) == 2

    # Check IPv4 Inteface
    ipv4 = {}
    ipv4["ParentTagName"] = "ttIpv4If"
    ipv4["ClassName"] = "Ipv4If"
    ipv4["StmPropertyModifierDict"] = {}
    ipv4["StmPropertyModifierDict"]["Address"] = {}
    ipv4["StmPropertyModifierDict"]["Address"]["Start"] = "someVal"
    ipv4["StmPropertyModifierDict"]["Address"]["Step"] = ["one", "two"]
    ipv4["StmPropertyModifierDict"]["Gateway"] = {}
    ipv4["StmPropertyModifierDict"]["Gateway"]["Start"] = "10"
    ipv4["StmPropertyModifierDict"]["Gateway"]["Step"] = "10"
    assert ipv4 in interfaceDict

    # Check EthII Interface
    eth = {}
    eth["ParentTagName"] = "ttEthIIIf"
    eth["ClassName"] = "EthIIIf"
    eth["StmPropertyModifierDict"] = {}
    eth["StmPropertyModifierDict"]["SourceMac"] = {}
    eth["StmPropertyModifierDict"]["SourceMac"]["Start"] = "someVal"
    eth["StmPropertyModifierDict"]["SourceMac"]["Step"] = ["one", "two"]
    assert eth in interfaceDict

    # Check protocol dictionary list(bgp and ldp)
    protocolDict = updated_input_dict["input"]["protocolDict"]
    assert len(protocolDict) == 2

    # Check BgpRouterConfig
    bgp = {}
    bgp["EnableProperty"] = "someVal"
    bgp["ParentTagName"] = "ttBgpRouterConfig"
    bgp["ClassName"] = "BgpRouterConfig"
    bgp["PropertyValueDict"] = {}
    bgp["PropertyValueDict"]["IpVersion"] = "someVal"
    bgp["PropertyValueDict"]["EnableBfd"] = ["one", "two"]
    bgp["StmPropertyModifierDict"] = {}
    bgp["StmPropertyModifierDict"]["AsNum"] = {}
    bgp["StmPropertyModifierDict"]["AsNum"]["Start"] = "10"
    bgp["StmPropertyModifierDict"]["AsNum"]["Step"] = "1"
    bgp["StmPropertyModifierDict"]["DutAsNum"] = {}
    bgp["StmPropertyModifierDict"]["DutAsNum"]["Start"] = "someVal"
    bgp["StmPropertyModifierDict"]["DutAsNum"]["Step"] = "1"
    assert bgp in protocolDict

    # Check LdpRouterConfig
    ldp = {}
    ldp["EnableProperty"] = "someVal"
    ldp["ParentTagName"] = "ttLdpRouterConfig"
    ldp["ClassName"] = "LdpRouterConfig"
    ldp["PropertyValueDict"] = {}
    ldp["PropertyValueDict"]["HelloVersion"] = "someVal"
    ldp["PropertyValueDict"]["EnableBfd"] = "10"
    assert ldp in protocolDict

    # Check output data
    output = {}
    output["scriptVarName"] = "TableData"
    output["epKey"] = "TestMethodologyCreateProtocolMixCommand3TableData"
    assert updated_input_dict["output"][0] == output


def test_run_txml_proc_util(stc):
    plLogger = PLLogger.GetLogger("test_run_txml_proc_util")

    mod_name = "unit_test_proc_funcs"
    pf_dict = [get_original_input_dict()]

    kv_dict = {"someKey": ["2", "4"],
               "anotherKey": ["3", "9"]}
    gui_kv_dict = {"weight": ["5.0", "60.0"],
                   "beta": ["10", "2"]}

    # Create unit test proc funcs file
    meth_home = meth_man_utils.get_methodology_base_dir()
    plLogger.LogInfo("meth_home: " + str(meth_home))
    script_dir = os.path.join(meth_home, "Scripts")
    plLogger.LogInfo("script_dir: " + str(script_dir))
    script_full_path = os.path.join(script_dir, mod_name + ".py")
    script_comp_full_path = os.path.join(script_dir, mod_name + ".pyc")
    plLogger.LogInfo("script_full_path: " + str(script_full_path))
    ret_val = False
    try:
        if not os.path.exists(script_dir):
            plLogger.LogInfo("making script dir...")
            os.makedirs(script_dir)
        with open(script_full_path, "w") as f:
            f.write(get_ut_proc_func_file_content())
        plLogger.LogInfo("wrote contents of file to " + str(script_full_path))
        ret_val = RunCmd.run_txml_proc_util(pf_dict, kv_dict, gui_kv_dict)
    finally:
        os.remove(script_full_path)
        if os.path.exists(script_comp_full_path):
            os.remove(script_comp_full_path)

    assert ret_val


def disabled_test_run_txml_proc_func_error_in_proc_func(stc):
    plLogger = PLLogger.GetLogger("test_run_txml_proc_func_error")
    mod_name = "unit_test_proc_funcs"
    pf_key = "procFunc1"
    pf_dict = {}
    pf_dict["id_list"] = [pf_key]
    pf_dict[pf_key] = {}
    pf_dict[pf_key]["script"] = "unit_test_proc_funcs" + ".py"
    pf_dict[pf_key]["entry_fn"] = "recombine_alpha_beta"
    pf_dict[pf_key]["input_id_list"] = ["in_1", "in_2", "in_3"]
    pf_dict[pf_key]["in_1"] = {"src_id": "alpha",
                               "script_var": "Alpha",
                               "default": None}
    pf_dict[pf_key]["in_2"] = {"src_id": "beta",
                               "script_var": None,
                               "default": None}
    pf_dict[pf_key]["in_3"] = {"src_id": None,
                               "script_var": "myConst",
                               "default": "5"}
    pf_dict[pf_key]["output_id_list"] = ["out_1", "out_2", "out_3"]
    pf_dict[pf_key]["out_1"] = {
        "ep_key": "Object.AlphaTimesBeta200",
        "script_var": "AlphaTimesBeta"}
    pf_dict[pf_key]["out_2"] = {
        "ep_key": "Object.AlphaBetaAvg12",
        "script_var": "AlphaBetaAvgPlusConst"}
    pf_dict[pf_key]["out_3"] = {
        "ep_key": "Object.AlphaPlusBeta1",
        "script_var": "AlphaPlusBeta"}

    kv_dict = {"someKey": "someVal",
               "anotherKey": "anotherVal"}
    gui_kv_dict = {"alpha": "a",
                   "beta": "b"}

    # Create unit test proc funcs file
    meth_home = meth_man_utils.get_methodology_base_dir()
    plLogger.LogInfo("meth_home: " + str(meth_home))
    script_dir = os.path.join(meth_home, "Scripts")
    plLogger.LogInfo("script_dir: " + str(script_dir))
    script_full_path = os.path.join(script_dir, mod_name + ".py")
    script_comp_full_path = os.path.join(script_dir, mod_name + ".pyc")
    plLogger.LogInfo("script_full_path: " + str(script_full_path))
    ret_val = False
    try:
        if not os.path.exists(script_dir):
            plLogger.LogInfo("making script dir...")
            os.makedirs(script_dir)
        with open(script_full_path, "w") as f:
            f.write(get_ut_proc_func_file_content())
        plLogger.LogInfo("wrote contents of file to " + str(script_full_path))
        ret_val = RunCmd.run_txml_proc_funcs(pf_dict, kv_dict, gui_kv_dict)
    finally:
        os.remove(script_full_path)
        if os.path.exists(script_comp_full_path):
            os.remove(script_comp_full_path)
    assert not ret_val

    # kv_dict should be unchanged
    assert "someKey" in kv_dict.keys()
    assert "anotherKey" in kv_dict.keys()
    assert kv_dict["someKey"] == "someVal"
    assert kv_dict["anotherKey"] == "anotherVal"


def get_ut_proc_func_file_content():
    return """
def recombine_alpha_beta(input_dict):
    alpha = input_dict["Alpha"]
    beta = input_dict["beta"]
    my_const = input_dict["myConst"]
    err_msg = ""
    output_dict = {}

    try:
        alpha = int(alpha)
        beta = int(beta)
        my_const = int(my_const)
        ab_sum = str(alpha + beta)
        ab_prod = str(alpha * beta)
        ab_avg = str(((alpha + beta)/2.0 + my_const))
        output_dict["AlphaTimesBeta"] = ab_prod
        output_dict["AlphaBetaAvgPlusConst"] = ab_avg
        output_dict["AlphaPlusBeta"] = ab_sum
    except ValueError:
        err_msg = "Invalid input, expected three numbers."
        output_dict = {}
    return output_dict, err_msg
"""


def get_new_test_txml():
    return "<test>" + \
        "<wizard " + \
        "displayName=\"BGP Route Reflector Test\" " + \
        "description=\"Configure and run a simple BGP Route Reflector test\" " + \
        "image=\"\">" + \
        "<page displayName=\"Route Reflector Template\" " + \
        "description=\"Configure the BGP Route Reflectors\" " + \
        "image=\"\">" + \
        "<group displayName=\"Route Reflector Template Load \">" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.CopiesPerParent.1\" " + \
        "value=\"5\" " + \
        "displayName=\"Copies Per Parent\" " + \
        "description=\"\"/>" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.XmlTemplate.1:" + \
        "StmPropertyModifier.ModifierInfo.1110:Start\" " + \
        "value=\"192.0.0.1\" " + \
        "displayName=\"\" " + \
        "description=\"\" />" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.XmlTemplate.1:" + \
        "StmPropertyModifier.ModifierInfo.1110:Step\" " + \
        "value=\"0.0.0.1\" " + \
        "displayName=\"\" " + \
        "description=\"\" />" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.XmlTemplate.1:" + \
        "StmPropertyModifier.ModifierInfo.1110:Repeat\" " + \
        "value=\"0\" " + \
        "displayName=\"\" " + \
        "description=\"\" />" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.XmlTemplate.1:" + \
        "StmPropertyModifier.ModifierInfo.1110:Recycle\" " + \
        "value=\"0\" " + \
        "displayName=\"\" " + \
        "description=\"\" />" + \
        "</group>" + \
        "<group displayName=\"Modify BGP Parameters\">" + \
        "<property id=\"spirent.methodology.ModifyTemplatePropertyCommand." + \
        "PropertyValueList.1:BgpRouterConfig.AsNum\" " + \
        "value=\"555\" " + \
        "displayName=\"AS Number\" " + \
        "description=\"\" />" + \
        "<property id=\"spirent.methodology.ModifyTemplatePropertyCommand." + \
        "PropertyValueList.1:BgpRouterConfig.PeerAs\" " + \
        "value=\"5\" " + \
        "displayName=\"Peer AS Number\" " + \
        "description=\"\" />" + \
        "</group>" + \
        "</page>" + \
        "<page displayName=\"Provider Edge Template\" " + \
        "description=\"Configure the Provider Edge\" " + \
        "image=\"\">" + \
        "<group displayName=\"Provider Edge Template\">" + \
        "<property id=\"spirent.methodology.LoadTemplateCommand.CopiesPerParent.1\" " + \
        "value=\"5\" " + \
        "displayName=\"Copies Per Parent\" " + \
        "description=\"\"/>" + \
        "</group>" + \
        "<group displayName=\"Modify BGP Parameters\">" + \
        "<property id=\"spirent.methodology.ModifyTemplatePropertyCommand." + \
        "PropertyValueList.1:BgpRouterConfig.AsNum\" " + \
        "value=\"5\" " + \
        "displayName=\"AS Number\" " + \
        "description=\"\" />" + \
        "<property id=\"spirent.methodology.ModifyTemplatePropertyCommand." + \
        "PropertyValueList.1:BgpRouterConfig.PeerAs\" " + \
        "value=\"555\" " + \
        "displayName=\"Peer AS Number\" " + \
        "description=\"\" />" + \
        "</group>" + \
        "</page>" + \
        "</wizard>" + \
        "</test>"


def get_test_txml():
    return "<test>" + \
        "<testInfo testMethodologyName=\"Forwarding\" " + \
        "description=\"My forwarding test\" " + \
        "testCaseName=\"original\" " + \
        "version=\"version_string\" " + \
        "imageName=\"diagram.png\">" + \
        "<labels>" + \
        "<label>throughput</label>" + \
        "<label>RFC2544</label>" + \
        "<label>benchmark</label>" + \
        "<label>BGP</label>" + \
        "</labels>" + \
        "</testInfo>" + \
        "<testResources>" + \
        "<resourceGroups>" + \
        "<resourceGroup name=\"chassisInfo\">" + \
        "<portGroups>" + \
        "<portGroup name=\"east\" id=\"Tag.Name.1632\">" + \
        "<port name=\"port1.location.2051\">" + \
        "<attribute name=\"location\" value=\"//10.14.16.27/1/1\"/>" + \
        "<property name=\"workload\" value=\"scale\"/>" + \
        "</port>" + \
        "<port name=\"port2.location.2052\">" + \
        "<attribute name=\"location\" value=\"//10.14.16.27/1/2\"/>" + \
        "<attribute name=\"workload\" value=\"performance\"/>" + \
        "</port>" + \
        "</portGroup>" + \
        "<portGroup name=\"west\" id=\"Tag.Name.1633\">" + \
        "<port name=\"port3.location.2053\">" + \
        "<attribute name=\"location\" value=\"//10.14.16.27/2/1\"/>" + \
        "<attribute name=\"workload\" value=\"scale\"/>" + \
        "</port>" + \
        "<port name=\"port4.location.2054\">" + \
        "<attribute name=\"location\" value=\"//10.14.16.27/2/2\"/>" + \
        "<attribute name=\"workload\" value=\"performance\"/>" + \
        "</port>" + \
        "</portGroup>" + \
        "</portGroups>" + \
        "<workloads>" + \
        "<workload name=\"scale\">" + \
        "<attribute name=\"minPerPortMemory\" value=\"24\"/>" + \
        "<attribute name=\"unitsMemory\" value=\"GB\"/>" + \
        "<attribute name=\"minPerPortStorage\" value=\"512\"/>" + \
        "<attribute name=\"unitsStorage\" value=\"MB\"/>" + \
        "<attribute name=\"minPerPortVCPU\" value=\"4\"/>" + \
        "<attribute name=\"unitsVCPU\" value=\"Spirent4\"/>" + \
        "<attribute name=\"perPortSpeeds\" value=\"10\"/>" + \
        "<attribute name=\"unitsPortSpeed\" value=\"Gbps\"/>" + \
        "</workload>" + \
        "<workload name=\"performance\">" + \
        "<attribute name=\"minPerPortMemory\" value=\"8\"/>" + \
        "<attribute name=\"unitsMemory\" value=\"GB\"/>" + \
        "<attribute name=\"minPerPortStorage\" value=\"512\"/>" + \
        "<attribute name=\"unitsStorage\" value=\"MB\"/>" + \
        "<attribute name=\"minPerPortVCPU\" value=\"6\"/>" + \
        "<attribute name=\"unitsVCPU\" value=\"Spirent3\"/>" + \
        "<attribute name=\"perPortSpeeds\" value=\"10,40,100\"/>" + \
        "<attribute name=\"unitsPortSpeed\" value=\"Gbps\"/>" + \
        "</workload>" + \
        "</workloads>" + \
        "</resourceGroup>" + \
        "</resourceGroups>" + \
        "</testResources>" + \
        "<wizard name=\"\" description=\"\" image=\"\">" + \
        "<page name=\"East Topology Template\" description=\"\" imageName=\"\">" + \
        "<group name=\"BGP Router Template\">" + \
        "<property name=\"LoadTemplateCommand.CopiesPerParent\" value=\"5\" />" + \
        "<property name=\"BgpRouterConfig.AsNum\" value=\"555\" tag=\"East Bgp Protocol\" />" + \
        "<property name=\"BgpRouterConfig.PeerAs\" value=\"5\" tag=\"East Bgp Protocol\" />" + \
        "</group>" + \
        "</page>" + \
        "<page name=\"West Topology Template\" description=\"description\" " + \
        "imageName=\"imageName.png\">" + \
        "<group name=\"BGP Router Template West Side\">" + \
        "<property name=\"LoadTemplateCommand.CopiesPerParent\" value=\"5\" />" + \
        "<property name=\"BgpRouterConfig.AsNum\" value=\"5\" tag=\"West Bgp Protocol\" />" + \
        "<property name=\"BgpRouterConfig.PeerAs\" value=\"555\" tag=\"West Bgp Protocol\" />" + \
        "</group>" + \
        "</page>" + \
        "<page name=\"Traffic\" description=\"\" imageName=\"\">" + \
        "<group name=\"Traffic\">" + \
        "<property name=\"spirent.trafficcenter.trafficprofilegroupcommand." + \
        "trafficpattern\" value=\"PAIR\" />" + \
        "<property name=\"spirent.trafficcenter.trafficprofilegroupcommand." + \
        "load\" value=\"100\" />" + \
        "<property name=\"spirent.trafficcenter.trafficprofilegroupcommand." + \
        "loadunits\" value=\"FRAMES_PER_SECOND\" />" + \
        "</group>" + \
        "<group>" + \
        "<property name=\"spirent.trafficcenter.createapplicationprofilecommand." + \
        "loadweight\" value=\"10\" />" + \
        "</group>" + \
        "<group>" + \
        "<property name=\"spirent.trafficcenter.createapplicationprofilecommand." + \
        "loadweight\" value=\"10\" />" + \
        "</group>" + \
        "</page>" + \
        "<page name=\"Test Parameters\" description=\"\" imageName=\"\">" + \
        "<group name=\"Traffic Settings\">" + \
        "<property name=\"WaitForTrafficProfileStartCommand.WaitTimeout\" value=\"564\" />" + \
        "<property name=\"WaitForTrafficProfileStartCommand.OtherProperty\" value=\"456\" />" + \
        "</group>" + \
        "<group>" + \
        "<property name=\"ObjectIteratorCommand.StartVal\" value=\"100\" />" + \
        "<property name=\"ObjectIteratorCommand.StepVal\" value=\"100\" />" + \
        "<property name=\"ObjectIteratorCommand.ValueType\" value=\"RANGE\" />" + \
        "</group>" + \
        "</page>" + \
        "</wizard>" + \
        "</test>"


def get_original_input_dict():
    return {
        "id": "Left.CreateProtocolMix.TableData",
        "scriptFile": "txml_processing_functions.py",
        "entryFunction": "config_table_data",
        "input": {
            "customDict": {
                "EnableVlan": "someKey",
                "Weight": "weight"
            },
            "interfaceDict": [{
                "ParentTagName": "ttIpv4If",
                "ClassName": "Ipv4If",
                "StmPropertyModifierDict": {
                    "Address": {
                        "Start": "someKey",
                        "Step": "anotherKey"
                    },
                    "Gateway": {
                        "Start": "beta",
                        "Step": "beta"
                    }
                }
            }, {
                "ParentTagName": "ttEthIIIf",
                "ClassName": "EthIIIf",
                "StmPropertyModifierDict": {
                    "SourceMac": {
                        "Start": "someKey",
                        "Step": "anotherKey"
                    }
                }
            }],
            "protocolDict": [{
                "EnableProperty": "someKey",
                "ParentTagName": "ttBgpRouterConfig",
                "ClassName": "BgpRouterConfig",
                "PropertyValueDict": {
                    "IpVersion": "someKey",
                    "EnableBfd": "anotherKey"
                },
                "StmPropertyModifierDict": {
                    "AsNum": {
                        "Start": "beta",
                        "Step": "1"
                    },
                    "DutAsNum": {
                        "Start": "someKey",
                        "Step": "1"
                    }
                }
            }, {
                "EnableProperty": "someKey",
                "ParentTagName": "ttLdpRouterConfig",
                "ClassName": "LdpRouterConfig",
                "PropertyValueDict": {
                    "HelloVersion": "someKey",
                    "EnableBfd": "beta"
                }
            }]
        },
        "output": [{
            "scriptVarName": "TableData",
            "epKey": "TestMethodologyCreateProtocolMixCommand3TableData"
        }]
    }
