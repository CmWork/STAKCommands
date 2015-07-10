from StcIntPythonPL import *
from mock import MagicMock, patch
import os
import sys
import json
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import spirent.methodology.CreateTemplateConfigCommand as CreateTempConfCmd
import spirent.methodology.utils.json_utils as json_utils
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as MethManUtils
import spirent.methodology.utils.template_processing_functions as proc_func


PKG = "spirent.methodology"


def test_validate(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    cmd = ctor.Create(PKG + ".CreateTemplateConfigCommand",
                      sequencer)
    CreateTempConfCmd.get_this_cmd = MagicMock(return_value=cmd)

    res = CreateTempConfCmd.validate(None, "", False, 1, [], [])
    assert res == ""


def test_reset(stc):
    res = CreateTempConfCmd.reset()
    assert res


def test_run_validation(stc):
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger("test_run_validation")
    plLogger.LogInfo("start")
    cmd = ctor.Create(PKG + ".CreateTemplateConfigCommand",
                      sequencer)
    CreateTempConfCmd.get_this_cmd = MagicMock(return_value=cmd)

    # CreateTemplateConfigCommand.run() signature:
    # run(StmTemplateMix, InputJson, AutoExpandTemplate,
    #     CopiesPerParent, SrcTagList, TargetTagList)

    # Check Input JSON is not ""
    res = CreateTempConfCmd.run(None, "", False, 10, [], [])
    assert not res
    assert cmd.Get("Status") == "InputJson is an empty string."

    # Check Input JSON is not valid JSON
    invalid_json = "InvalidJson String"
    res = CreateTempConfCmd.run(None, invalid_json, False,
                                10, [], [])
    assert not res
    assert "InputJson is invalid or does not conform to the schema: " + \
        "JSON string: " + invalid_json + " is not valid JSON." \
        in cmd.Get("Status")

    # Check Input JSON does not match schema
    res = CreateTempConfCmd.run(None, "{}", False,
                                10, [], [])
    assert not res
    assert "is a required property" in cmd.Get("Status")

    # Check StmTemplateConfig handle
    # Find an invalid handle
    invalid_handle = 1214323
    while hnd_reg.Find(invalid_handle) is not None:
        invalid_handle = invalid_handle + 3
    res = CreateTempConfCmd.run(invalid_handle, cmd.Get("InputJson"),
                                False, 10, [], [])
    assert not res
    assert cmd.Get("Status") == "StmTemplateMix with given handle: " + \
        str(invalid_handle) + " is invalid."

    # Check StmTemplateConfig handle is wrong type
    res = CreateTempConfCmd.run(cmd.GetObjectHandle(), cmd.Get("InputJson"),
                                False, 10, [], [])
    assert not res
    assert "If StmTemplateMix is specified, object must be an StmTemplateMix." \
        in cmd.Get("Status")

    # Check "" is valid StmTemplateConfig handle (indicates use project)
    res = CreateTempConfCmd.run("", cmd.Get("InputJson"),
                                False, 10, [], [])
    assert res

    # Check 0 is valid StmTemplateConfig handle (indicates use project)
    res = CreateTempConfCmd.run(0, cmd.Get("InputJson"),
                                False, 10, [], [])
    assert res

    # Check invalid baseTemplateFile (invalid XML, doesn't exist, etc)
    input_json = json.loads(cmd.Get("InputJson"))
    input_json["baseTemplateFile"] = "ut_invalid_xml_file.xml"
    res = CreateTempConfCmd.run(0, json.dumps(input_json),
                                False, 10, [], [])
    assert not res
    assert "Was unable to load template XML from " in cmd.Get("Status")


def test_run_sub_cmd_fail(stc):
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    plLogger = PLLogger.GetLogger("test_run_validation")
    plLogger.LogInfo("start")
    cmd = ctor.Create(PKG + ".CreateTemplateConfigCommand",
                      sequencer)

    # Create a patch to limit mock to this unit test
    gtc_p = patch(PKG + ".CreateTemplateConfigCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # CreateTemplateConfigCommand.run() signature:
    # run(StmTemplateMix, InputJson, AutoExpandTemplate,
    #     CopiesPerParent, SrcTagList, TargetTagList)

    # Check the MergeTemplateCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_merge",
              new=MagicMock(return_value=False))
    p.start()

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttProtocolConfig"
    merge_info_dict["mergeSourceTemplateFile"] = "fake_file.xml"
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to merge XML into the StmTemplateConfig given" \
        in cmd.Get("Status")
    p.stop()

    # Check the AddTemplateObjectCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_objectlist",
              new=MagicMock(return_value=False))
    p.start()

    # Add Info
    add_info_dict = {}
    add_info_dict["className"] = "Scriptable"
    add_info_dict["parentTagName"] = "ParentScriptable"
    add_info_dict["tagName"] = "TagName"

    modify_list = []
    modify_list.append({"addObjectList": [add_info_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to add object into the StmTemplateConfig given" \
        in cmd.Get("Status")
    p.stop()

    # Check the ModifyTemplatePropertyCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_modify",
              new=MagicMock(return_value=False))
    p.start()

    # Property Value List
    pv_dict = {}
    pv_dict["className"] = "Dhcpv4ServerConfig"
    pv_dict["tagName"] = "ttDhcpv4ServerConfig"
    pv_dict["propertyValueList"] = {}
    pv_dict["propertyValueList"]["MinAllowedLeaseTime"] = "601"

    modify_list = []
    modify_list.append({"propertyValueList": [pv_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to modify properties in the StmTemplateConfig given" \
        in cmd.Get("Status")
    p.stop()

    # Check the ConfigTemplateStmPropertyModifierCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_config_prop_modifier",
              new=MagicMock(return_value=False))
    p.start()

    # StmPropertyModifierList
    lease = {}
    lease["tagName"] = "ttDhcpv4ServerConfig.LeaseTime"
    lease["className"] = "Dhcpv4ServerConfig"
    lease["propertyName"] = "LeaseTime"
    lease["parentTagName"] = "ttDhcpv4ServerConfig"
    lease["propertyValueList"] = {}
    lease["propertyValueList"]["Start"] = "1001"
    lease["propertyValueList"]["Step"] = "102"

    modify_list = []
    modify_list.append({"stmPropertyModifierList": [lease]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to add or configure StmPropertyModifier objects " + \
        "in the StmTemplateConfig given" in cmd.Get("Status")
    p.stop()

    # Check the ConfigTemplatePdusCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_config_pdu",
              new=MagicMock(return_value=False))
    p.start()

    # PDU Config
    src_dict = {}
    src_dict["templateElementTagName"] = "ttStreamBlock"
    src_dict["offsetReference"] = "ipv4_5265.sourceAddr"
    src_dict["value"] = "33.33.33.33"

    modify_list = []
    modify_list.append({"pduModifierList": [src_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "Ipv4_Stream.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to modify PDU data in a streamblock's FrameConfig " \
        in cmd.Get("Status")
    p.stop()

    # Check the ConfigTemplateRelationCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_config_relation",
              new=MagicMock(return_value=False))
    p.start()

    # Relation Info
    uses_if_dict = {}
    uses_if_dict["relationType"] = "UsesIf"
    uses_if_dict["sourceTag"] = "ttDhcpv4ServerConfig"
    uses_if_dict["targetTag"] = "ttIpv4If"

    modify_list = []
    modify_list.append({"relationList": [uses_if_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    res = CreateTempConfCmd.run(0, json.dumps(mix_part),
                                False, 10, [], [])
    assert not res
    assert "Failed to add or remove a relation in the StmTemplateConfig" \
        in cmd.Get("Status")
    p.stop()

    # Check the ExpandTemplateCommand failing
    p = patch(PKG + ".CreateTemplateConfigCommand.run_expand",
              new=MagicMock(return_value=False))
    p.start()

    res = CreateTempConfCmd.run(0, cmd.Get("InputJson"),
                                True, 10, [], [])
    assert not res
    assert cmd.Get("Status") == "Failed to expand the StmTemplateConfig."
    p.stop()

    gtc_p.stop()


def check_prop_mod_ele(prop_mod_ele, parent_tag_name, mod_type, obj_name,
                       prop_name, start, step, repeat, recycle, mod_tag):
    assert prop_mod_ele is not None
    assert prop_mod_ele.get("TagName") == parent_tag_name
    mod_info = prop_mod_ele.get("ModifierInfo")
    plLogger = PLLogger.GetLogger("check_prop_mod_ele")
    plLogger.LogInfo("mod_info: " + str(mod_info))
    res = json_utils.validate_json(
        mod_info, proc_func.get_range_modifier_json_schema())
    assert res == ""
    err_str, md_dict = json_utils.load_json(mod_info)
    assert err_str == ""
    assert md_dict is not None
    assert md_dict.get("modifierType") == mod_type
    assert md_dict.get("propertyName") == prop_name
    assert md_dict.get("objectName") == obj_name
    pv_dict = md_dict["propertyValueDict"]
    assert pv_dict["start"] == [str(start)]
    assert pv_dict["step"] == [str(step)]
    assert pv_dict["repeat"] == [repeat]
    assert pv_dict["recycle"] == [recycle]

    rel_ele = None
    for child in prop_mod_ele:
        if child.tag == "Relation" and \
           child.get("type") == "UserTag":
            rel_ele = child
            break
    assert rel_ele is not None
    assert rel_ele.get("target") == mod_tag.get("id")


def add_unit_test_template(filename, xml_str):
    template_dir = MethManUtils.get_topology_template_home_dir()
    filenamePath = os.path.join(template_dir, filename)
    plLogger = PLLogger.GetLogger("add_unit_test_template")
    try:
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        if os.path.isfile(filenamePath):
            remove_unit_test_template(filename)
        with open(filenamePath, "w") as f:
            f.write(xml_str)
    except:
        plLogger.LogError("Failed to add template for the unit test.")
        return False
    return True


def remove_unit_test_template(filename):
    template_dir = MethManUtils.get_topology_template_home_dir()
    filenamePath = os.path.join(template_dir, filename)
    if os.path.isfile(filenamePath):
        os.remove(filenamePath)


def test_cmd_default(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_cmd_default")
    plLogger.LogInfo("test_cmd_default")

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")

    input_json_str = cmd.Get("InputJson")
    err_str, input_json = json_utils.load_json(input_json_str)
    assert err_str == ""
    assert "baseTemplateFile" in input_json.keys()
    assert input_json["baseTemplateFile"] == "IPv4_NoVlan.xml"

    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None
    cmd.MarkDelete()

    gen_obj_list = template.GetObjects("Scriptable",
                                       RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 1
    dev = gen_obj_list[0]
    assert dev.IsTypeOf("EmulatedDevice")
    assert dev.GetParent().GetObjectHandle() == project.GetObjectHandle()
    assert dev.Get("DeviceCount") == 1


def test_run_merge_modify_separate_modify_operations(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_merge_modify")
    plLogger.LogInfo("test_run_modify")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    merge_info_dict["mergeSourceTemplateFile"] = proto_template_file
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Property Value Lists
    proto_pv_dict = {}
    proto_pv_dict["className"] = "Dhcpv4ServerConfig"
    proto_pv_dict["tagName"] = "ttDhcpv4ServerConfig"
    proto_pv_dict["propertyValueList"] = {}
    proto_pv_dict["propertyValueList"]["MinAllowedLeaseTime"] = "601"
    proto_pv_dict["propertyValueList"]["RenewalTimePercent"] = "51"

    pool_pv_dict = {}
    pool_pv_dict["tagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["className"] = "Dhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["propertyValueList"] = {}
    pool_pv_dict["propertyValueList"]["PrefixLength"] = "17"
    pool_pv_dict["propertyValueList"]["NetworkCount"] = "21"

    # Template Modifiers
    lease = {}
    lease["tagName"] = "ttDhcpv4ServerConfig.LeaseTime"
    lease["className"] = "Dhcpv4ServerConfig"
    lease["propertyName"] = "LeaseTime"
    lease["parentTagName"] = "ttDhcpv4ServerConfig"
    lease["propertyValueList"] = {}
    lease["propertyValueList"]["Start"] = "1001"
    lease["propertyValueList"]["Step"] = "102"

    host_count = {}
    host_count["tagName"] = "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"
    host_count["className"] = "Dhcpv4ServerDefaultPoolConfig"
    host_count["propertyName"] = "HostAddrCount"
    host_count["parentTagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    host_count["propertyValueList"] = {}
    host_count["propertyValueList"]["Start"] = "21"
    host_count["propertyValueList"]["Step"] = "22"
    host_count["propertyValueList"]["Repeat"] = 23
    host_count["propertyValueList"]["Recycle"] = 24

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})
    modify_list.append({"propertyValueList":
                        [proto_pv_dict, pool_pv_dict]})
    modify_list.append({"stmPropertyModifierList":
                        [lease, host_count]})
    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 7
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    dhcp_server_lease_tag = None
    dhcp_server_pool_count_tag = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig"):
            dhcp_server_pool_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerConfig.LeaseTime"):
            dhcp_server_lease_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"):
            dhcp_server_pool_count_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None
    assert dhcp_server_lease_tag is not None
    assert dhcp_server_pool_count_tag is not None

    # Check the Dhcpv4ServerConfig (protocol merge)
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
            break
    assert dhcp_server_ele is not None
    assert dhcp_server_ele.get("MinAllowedLeaseTime") == "601"
    assert dhcp_server_ele.get("RenewalTimePercent") == "51"

    prop_mod_list = []
    for child in dhcp_server_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerConfig",
                       "RANGE",
                       "Dhcpv4ServerConfig", "LeaseTime",
                       "1001", "102", 0, 0,
                       dhcp_server_lease_tag)

    # Check the Dhcpv4ServerDefaultPoolConfig (protocol merge)
    default_pool_ele = None
    for child in dhcp_server_ele:
        if child.tag == "Dhcpv4ServerDefaultPoolConfig":
            default_pool_ele = child
            break
    assert default_pool_ele is not None
    assert default_pool_ele.get("PrefixLength") == "17"
    assert default_pool_ele.get("NetworkCount") == "21"

    prop_mod_list = []
    for child in default_pool_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerDefaultPoolConfig",
                       "RANGE",
                       "Dhcpv4ServerDefaultPoolConfig", "HostAddrCount",
                       "21", "22", 23, 24,
                       dhcp_server_pool_count_tag)
    # Clean up
    remove_unit_test_template(proto_template_file)


def test_run_merge_modify_same_modify_operation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_merge_modify")
    plLogger.LogInfo("test_run_modify")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    merge_info_dict["mergeSourceTemplateFile"] = proto_template_file
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Property Value Lists
    proto_pv_dict = {}
    proto_pv_dict["className"] = "Dhcpv4ServerConfig"
    proto_pv_dict["tagName"] = "ttDhcpv4ServerConfig"
    proto_pv_dict["propertyValueList"] = {}
    proto_pv_dict["propertyValueList"]["MinAllowedLeaseTime"] = "601"
    proto_pv_dict["propertyValueList"]["RenewalTimePercent"] = "51"

    pool_pv_dict = {}
    pool_pv_dict["tagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["className"] = "Dhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["propertyValueList"] = {}
    pool_pv_dict["propertyValueList"]["PrefixLength"] = "17"
    pool_pv_dict["propertyValueList"]["NetworkCount"] = "21"

    # Template Modifiers
    lease = {}
    lease["tagName"] = "ttDhcpv4ServerConfig.LeaseTime"
    lease["className"] = "Dhcpv4ServerConfig"
    lease["propertyName"] = "LeaseTime"
    lease["parentTagName"] = "ttDhcpv4ServerConfig"
    lease["propertyValueList"] = {}
    lease["propertyValueList"]["Start"] = "1001"
    lease["propertyValueList"]["Step"] = "102"

    host_count = {}
    host_count["tagName"] = "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"
    host_count["className"] = "Dhcpv4ServerDefaultPoolConfig"
    host_count["propertyName"] = "HostAddrCount"
    host_count["parentTagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    host_count["propertyValueList"] = {}
    host_count["propertyValueList"]["Start"] = "21"
    host_count["propertyValueList"]["Step"] = "22"
    host_count["propertyValueList"]["Repeat"] = 23
    host_count["propertyValueList"]["Recycle"] = 24

    merge_info_dict["propertyValueList"] = [proto_pv_dict, pool_pv_dict]
    merge_info_dict["stmPropertyModifierList"] = [lease, host_count]

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})

    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 7
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    dhcp_server_lease_tag = None
    dhcp_server_pool_count_tag = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig"):
            dhcp_server_pool_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerConfig.LeaseTime"):
            dhcp_server_lease_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"):
            dhcp_server_pool_count_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None
    assert dhcp_server_lease_tag is not None
    assert dhcp_server_pool_count_tag is not None

    # Check the Dhcpv4ServerConfig (protocol merge)
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
            break
    assert dhcp_server_ele is not None
    assert dhcp_server_ele.get("MinAllowedLeaseTime") == "601"
    assert dhcp_server_ele.get("RenewalTimePercent") == "51"

    prop_mod_list = []
    for child in dhcp_server_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerConfig",
                       "RANGE",
                       "Dhcpv4ServerConfig", "LeaseTime",
                       "1001", "102", 0, 0,
                       dhcp_server_lease_tag)

    # Check the Dhcpv4ServerDefaultPoolConfig (protocol merge)
    default_pool_ele = None
    for child in dhcp_server_ele:
        if child.tag == "Dhcpv4ServerDefaultPoolConfig":
            default_pool_ele = child
            break
    assert default_pool_ele is not None
    assert default_pool_ele.get("PrefixLength") == "17"
    assert default_pool_ele.get("NetworkCount") == "21"

    prop_mod_list = []
    for child in default_pool_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerDefaultPoolConfig",
                       "RANGE",
                       "Dhcpv4ServerDefaultPoolConfig", "HostAddrCount",
                       "21", "22", 23, 24,
                       dhcp_server_pool_count_tag)
    # Clean up
    remove_unit_test_template(proto_template_file)


def test_run_merge_rel_list(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_merge_rel_list")
    plLogger.LogInfo("test_run_merge_rel_list")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    merge_info_dict["mergeSourceTemplateFile"] = proto_template_file
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Relation Info
    uses_if_dict = {}
    uses_if_dict["relationType"] = "UsesIf"
    uses_if_dict["sourceTag"] = "ttDhcpv4ServerConfig"
    uses_if_dict["targetTag"] = "ttIpv4If"

    tli_dict = {}
    tli_dict["relationType"] = "TopLevelIf"
    tli_dict["sourceTag"] = "ttEmulatedDevice"
    tli_dict["targetTag"] = "ttIpv4If"
    tli_dict["removeRelation"] = True

    fake_rel_dict = {}
    fake_rel_dict["relationType"] = "StackedOnEndpoint"
    fake_rel_dict["sourceTag"] = "ttEthIIIf"
    fake_rel_dict["targetTag"] = "ttIpv4If"

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})
    modify_list.append({"relationList":
                        [uses_if_dict, tli_dict, fake_rel_dict]})
    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["tagPrefix"] = "Left_Mix2_Row3_"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", False)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 5
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    for tag_ele in tag_ele_list:
        plLogger.LogDebug("tag_ele name: " + tag_ele.get("Name"))
        if tag_ele.get("Name") == "Left_Mix2_Row3_ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "Left_Mix2_Row3_ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "Left_Mix2_Row3_ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "Left_Mix2_Row3_ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "Left_Mix2_Row3_ttDhcpv4ServerDefaultPoolConfig"):
            dhcp_server_pool_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None

    # EmulatedDevice
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]

    # Children of EmulatedDevice
    ipv4_ele = None
    eth_ele = None
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
        elif child.tag == "Ipv4If":
            ipv4_ele = child
        elif child.tag == "EthIIIf":
            eth_ele = child
    assert ipv4_ele is not None
    assert eth_ele is not None
    assert dhcp_server_ele is not None

    # UsesIf relation
    rel_list = dhcp_server_ele.findall(".//Relation")
    assert len(rel_list) > 0
    uses_rel = None
    for rel in rel_list:
        if rel.get("type") == "UsesIf":
            uses_rel = rel
            break
    assert uses_rel is not None
    assert uses_rel.get("target") == ipv4_ele.get("id")

    # Missing TLI
    tli_rel = None
    rel_list = dev_ele.findall(".//Relation")
    for rel in rel_list:
        if rel.get("type") == "TopLevelIf":
            if rel.get("target") == ipv4_ele.get("id"):
                tli_rel = rel
                break
    assert tli_rel is None

    # Out of Order Stack
    oos_rel = None
    rel_list = eth_ele.findall(".//Relation")
    for rel in rel_list:
        if rel.get("type") == "StackedOnEndpoint":
            if rel.get("target") == ipv4_ele.get("id"):
                oos_rel = rel
                break
    assert oos_rel is not None

    # Clean up
    remove_unit_test_template(proto_template_file)


def test_run_no_prop_val_list(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_no_prop_val_list")
    plLogger.LogInfo("test_run_no_prop_val_list")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    merge_info_dict["mergeSourceTemplateFile"] = proto_template_file
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Template Modifiers
    lease = {}
    lease["tagName"] = "ttDhcpv4ServerConfig.LeaseTime"
    lease["className"] = "Dhcpv4ServerConfig"
    lease["propertyName"] = "LeaseTime"
    lease["parentTagName"] = "ttDhcpv4ServerConfig"
    lease["propertyValueList"] = {}
    lease["propertyValueList"]["Start"] = "1001"
    lease["propertyValueList"]["Step"] = "102"

    host_count = {}
    host_count["tagName"] = "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"
    host_count["className"] = "Dhcpv4ServerDefaultPoolConfig"
    host_count["propertyName"] = "HostAddrCount"
    host_count["parentTagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    host_count["propertyValueList"] = {}
    host_count["propertyValueList"]["Start"] = "21"
    host_count["propertyValueList"]["Step"] = "22"
    host_count["propertyValueList"]["Repeat"] = 23
    host_count["propertyValueList"]["Recycle"] = 24

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})
    modify_list.append({"stmPropertyModifierList":
                        [lease, host_count]})
    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 7
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    dhcp_server_lease_tag = None
    dhcp_server_pool_count_tag = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig"):
            dhcp_server_pool_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerConfig.LeaseTime"):
            dhcp_server_lease_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"):
            dhcp_server_pool_count_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None
    assert dhcp_server_lease_tag is not None
    assert dhcp_server_pool_count_tag is not None

    # Check the Dhcpv4ServerConfig (protocol merge)
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
            break
    assert dhcp_server_ele is not None

    prop_mod_list = []
    for child in dhcp_server_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerConfig",
                       "RANGE",
                       "Dhcpv4ServerConfig", "LeaseTime",
                       "1001", "102", 0, 0,
                       dhcp_server_lease_tag)

    # Check the Dhcpv4ServerDefaultPoolConfig (protocol merge)
    default_pool_ele = None
    for child in dhcp_server_ele:
        if child.tag == "Dhcpv4ServerDefaultPoolConfig":
            default_pool_ele = child
            break
    assert default_pool_ele is not None

    prop_mod_list = []
    for child in default_pool_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "ttDhcpv4ServerDefaultPoolConfig",
                       "RANGE",
                       "Dhcpv4ServerDefaultPoolConfig", "HostAddrCount",
                       "21", "22", 23, 24,
                       dhcp_server_pool_count_tag)
    # Clean up
    remove_unit_test_template(proto_template_file)


def test_run_no_stm_prop_modifiers(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_no_stm_prop_modifiers")
    plLogger.LogInfo("test_run_no_stm_prop_modifiers")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    merge_info_dict = {}
    merge_info_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    merge_info_dict["mergeSourceTemplateFile"] = proto_template_file
    merge_info_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Property Value Lists
    proto_pv_dict = {}
    proto_pv_dict["className"] = "Dhcpv4ServerConfig"
    proto_pv_dict["tagName"] = "ttDhcpv4ServerConfig"
    proto_pv_dict["propertyValueList"] = {}
    proto_pv_dict["propertyValueList"]["MinAllowedLeaseTime"] = "601"
    proto_pv_dict["propertyValueList"]["RenewalTimePercent"] = "51"

    pool_pv_dict = {}
    pool_pv_dict["tagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["className"] = "Dhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["propertyValueList"] = {}
    pool_pv_dict["propertyValueList"]["PrefixLength"] = "17"
    pool_pv_dict["propertyValueList"]["NetworkCount"] = "21"

    modify_list = []
    modify_list.append({"mergeList": [merge_info_dict]})
    modify_list.append({"propertyValueList":
                        [proto_pv_dict, pool_pv_dict]})
    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 5
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif (tag_ele.get("Name") ==
              "ttDhcpv4ServerDefaultPoolConfig"):
            dhcp_server_pool_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None

    # Check the Dhcpv4ServerConfig (protocol merge)
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
            break
    assert dhcp_server_ele is not None
    assert dhcp_server_ele.get("MinAllowedLeaseTime") == "601"
    assert dhcp_server_ele.get("RenewalTimePercent") == "51"

    # Check the Dhcpv4ServerDefaultPoolConfig (protocol merge)
    default_pool_ele = None
    for child in dhcp_server_ele:
        if child.tag == "Dhcpv4ServerDefaultPoolConfig":
            default_pool_ele = child
            break
    assert default_pool_ele is not None
    assert default_pool_ele.get("PrefixLength") == "17"
    assert default_pool_ele.get("NetworkCount") == "21"

    # Clean up
    remove_unit_test_template(proto_template_file)


def test_run_multi_protocol(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_run_multi_protocol")
    plLogger.LogInfo("test_run_multi_protocol")

    # Create a unit test protocol template
    proto_template = get_proto_template()
    proto_template_file = "unit_test_dhcpv4_bgp_template.xml"
    assert add_unit_test_template(proto_template_file, proto_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    dhcp_merge_dict = {}
    dhcp_merge_dict["mergeSourceTag"] = "ttDhcpv4ServerConfig"
    dhcp_merge_dict["mergeSourceTemplateFile"] = proto_template_file
    dhcp_merge_dict["mergeTargetTag"] = "ttEmulatedDevice"

    bgp_merge_dict = {}
    bgp_merge_dict["mergeSourceTag"] = "ttBgpRouterConfig"
    bgp_merge_dict["mergeSourceTemplateFile"] = proto_template_file
    bgp_merge_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Property Value Lists
    proto_pv_dict = {}
    proto_pv_dict["className"] = "Dhcpv4ServerConfig"
    proto_pv_dict["tagName"] = "ttDhcpv4ServerConfig"
    proto_pv_dict["propertyValueList"] = {}
    proto_pv_dict["propertyValueList"]["MinAllowedLeaseTime"] = "601"
    proto_pv_dict["propertyValueList"]["RenewalTimePercent"] = "51"

    pool_pv_dict = {}
    pool_pv_dict["tagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["className"] = "Dhcpv4ServerDefaultPoolConfig"
    pool_pv_dict["propertyValueList"] = {}
    pool_pv_dict["propertyValueList"]["PrefixLength"] = "17"
    pool_pv_dict["propertyValueList"]["NetworkCount"] = "21"

    bgp_pv_dict = {}
    bgp_pv_dict["className"] = "BgpRouterConfig"
    bgp_pv_dict["tagName"] = "ttBgpRouterConfig"
    bgp_pv_dict["propertyValueList"] = {}
    bgp_pv_dict["propertyValueList"]["AsNum"] = "602"

    # Template Modifiers
    lease = {}
    lease["tagName"] = "ttDhcpv4ServerConfig.LeaseTime"
    lease["className"] = "Dhcpv4ServerConfig"
    lease["propertyName"] = "LeaseTime"
    lease["parentTagName"] = "ttDhcpv4ServerConfig"
    lease["propertyValueList"] = {}
    lease["propertyValueList"]["Start"] = "1001"
    lease["propertyValueList"]["Step"] = "102"

    host_count = {}
    host_count["tagName"] = "ttDhcpv4ServerDefaultPoolConfig.HostAddrCount"
    host_count["className"] = "Dhcpv4ServerDefaultPoolConfig"
    host_count["propertyName"] = "HostAddrCount"
    host_count["parentTagName"] = "ttDhcpv4ServerDefaultPoolConfig"
    host_count["propertyValueList"] = {}
    host_count["propertyValueList"]["Start"] = "21"
    host_count["propertyValueList"]["Step"] = "22"
    host_count["propertyValueList"]["Repeat"] = 23
    host_count["propertyValueList"]["Recycle"] = 24

    dut_as = {}
    dut_as["tagName"] = "ttBgpRouterConfig.DutAsNum"
    dut_as["className"] = "BgpRouterConfig"
    dut_as["propertyName"] = "DutAsNum"
    dut_as["parentTagName"] = "ttBgpRouterConfig"
    dut_as["propertyValueList"] = {}
    dut_as["propertyValueList"]["Start"] = "2002"
    dut_as["propertyValueList"]["Step"] = "202"
    dut_as["propertyValueList"]["Repeat"] = 200
    dut_as["propertyValueList"]["Recycle"] = 201

    modify_list = []
    modify_list.append({"mergeList": [dhcp_merge_dict, bgp_merge_dict]})
    modify_list.append({"propertyValueList":
                        [proto_pv_dict, pool_pv_dict]})
    modify_list.append({"propertyValueList":
                        [bgp_pv_dict]})
    modify_list.append({"stmPropertyModifierList":
                        [lease, host_count, dut_as]})

    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["tagPrefix"] = "North_"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()
    plLogger.LogInfo("DONE: templateXML: " +
                     str(template.Get("TemplateXml")))

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall('.//Tag')
    tag_name_list = [t.get('Name') for t in tag_ele_list]
    assert len(tag_name_list) == 12
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    dhcp_server_tag = None
    dhcp_server_pool_tag = None
    dhcp_server_lease_tag = None
    dhcp_server_pool_count_tag = None
    bgp_router_tag = None
    bgp_route_tag = None
    net_block_tag = None
    net_block_start_ip_tag = None
    bgp_dut_as_tag = None

    for tag_name, tag_ele in zip(tag_name_list, tag_ele_list):
        if tag_name == "North_ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_name == "North_ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_name == "North_ttEthIIIf":
            eth_tag = tag_ele
        elif tag_name == "North_ttDhcpv4ServerConfig":
            dhcp_server_tag = tag_ele
        elif tag_name == "North_ttDhcpv4ServerDefaultPoolConfig":
            dhcp_server_pool_tag = tag_ele
        elif tag_name == "North_ttDhcpv4ServerConfig.LeaseTime":
            dhcp_server_lease_tag = tag_ele
        elif tag_name == "North_ttDhcpv4ServerDefaultPoolConfig.HostAddrCount":
            dhcp_server_pool_count_tag = tag_ele
        elif tag_name == "North_ttBgpRouterConfig":
            bgp_router_tag = tag_ele
        elif tag_name == "North_ttBgpIpv4RouteConfig":
            bgp_route_tag = tag_ele
        elif tag_name == "North_ttIpv4NetworkBlock":
            net_block_tag = tag_ele
        elif tag_name == "North_ttIpv4NetworkBlock.StartIpList":
            net_block_start_ip_tag = tag_ele
        elif tag_name == "North_ttBgpRouterConfig.DutAsNum":
            bgp_dut_as_tag = tag_ele
    assert dev_tag is not None
    assert eth_tag is not None
    assert ipv4_tag is not None
    assert dhcp_server_tag is not None
    assert dhcp_server_pool_tag is not None
    assert dhcp_server_lease_tag is not None
    assert dhcp_server_pool_count_tag is not None
    assert bgp_router_tag is not None
    assert bgp_route_tag is not None
    assert net_block_tag is not None
    assert net_block_start_ip_tag is not None
    assert bgp_dut_as_tag is not None

    # Check the Dhcpv4ServerConfig (protocol merge)
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    dhcp_server_ele = None
    for child in dev_ele:
        if child.tag == "Dhcpv4ServerConfig":
            dhcp_server_ele = child
            break
    assert dhcp_server_ele is not None
    assert dhcp_server_ele.get("MinAllowedLeaseTime") == "601"
    assert dhcp_server_ele.get("RenewalTimePercent") == "51"

    prop_mod_list = []
    for child in dhcp_server_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "North_ttDhcpv4ServerConfig",
                       "RANGE",
                       "Dhcpv4ServerConfig", "LeaseTime",
                       "1001", "102", 0, 0,
                       dhcp_server_lease_tag)

    # Check the Dhcpv4ServerDefaultPoolConfig (protocol merge)
    default_pool_ele = None
    for child in dhcp_server_ele:
        if child.tag == "Dhcpv4ServerDefaultPoolConfig":
            default_pool_ele = child
            break
    assert default_pool_ele is not None
    assert default_pool_ele.get("PrefixLength") == "17"
    assert default_pool_ele.get("NetworkCount") == "21"

    prop_mod_list = []
    for child in default_pool_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "North_ttDhcpv4ServerDefaultPoolConfig",
                       "RANGE",
                       "Dhcpv4ServerDefaultPoolConfig", "HostAddrCount",
                       "21", "22", 23, 24,
                       dhcp_server_pool_count_tag)

    # Check the BgpRouterConfig (protocol merge)
    bgp_router_ele = None
    for child in dev_ele:
        if child.tag == "BgpRouterConfig":
            bgp_router_ele = child
            break
    assert bgp_router_ele is not None
    assert bgp_router_ele.get("AsNum") == "602"

    prop_mod_list = []
    for child in bgp_router_ele:
        if child.tag == "StmPropertyModifier":
            prop_mod_list.append(child)
    assert len(prop_mod_list) == 1
    prop_mod = prop_mod_list[0]
    assert prop_mod is not None
    check_prop_mod_ele(prop_mod,
                       "North_ttBgpRouterConfig",
                       "RANGE",
                       "BgpRouterConfig", "DutAsNum",
                       "2002", "202", 200, 201,
                       bgp_dut_as_tag)


def test_add_object(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    plLogger = PLLogger.GetLogger("test_add_object")
    plLogger.LogInfo("test_add_object")

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")

    input_json_str = cmd.Get("InputJson")
    err_str, input_json = json_utils.load_json(input_json_str)
    assert err_str == ""
    assert 'baseTemplateFile' in input_json
    assert input_json['baseTemplateFile'] == 'IPv4_NoVlan.xml'
    # Add an add object section
    input_json['modifyList'] = [
        {
            'addObjectList': [
                {
                    'className': 'Rfc4814EthIIIfDecorator',
                    'parentTagName': 'ttEthIIIf',
                    'tagName': 'ttRfc4814EthIIIfDecorator',
                    'propertyValueList': {
                        'RandomSeedValue': '128'
                    }
                }
            ]
        }
    ]
    cmd.Set('InputJson', json.dumps(input_json))
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None
    cmd.MarkDelete()

    gen_obj_list = template.GetObjects("Scriptable",
                                       RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 1
    dev = gen_obj_list[0]
    assert dev.IsTypeOf("EmulatedDevice")
    assert dev.GetParent().GetObjectHandle() == project.GetObjectHandle()
    assert dev.Get('DeviceCount') == 1
    eth = dev.GetObject('EthIIIf')
    assert eth is not None
    modifier = eth.GetObject('Rfc4814EthIIIfDecorator')
    assert modifier is not None
    assert 128, modifier.Get('RandomSeedValue')


def test_pppoe_protocol_device_creation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_pppoe_protocol_device_creation")
    plLogger.LogInfo("test_pppoe_protocol_device_creation")

    # Create a unit test protocol template
    pppoe_template = get_pppoe_template()
    pppoe_template_file = "unit_test_pppoe_template.xml"
    assert add_unit_test_template(pppoe_template_file, pppoe_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Merge Info
    pppoe_merge_dict = {}
    pppoe_merge_dict["mergeSourceTag"] = "ttPppoeIf"
    pppoe_merge_dict["mergeSourceTemplateFile"] = pppoe_template_file
    pppoe_merge_dict["mergeTargetTag"] = "ttEmulatedDevice"
    ppp_merge_dict = {}
    ppp_merge_dict["mergeSourceTag"] = "ttPppIf"
    ppp_merge_dict["mergeSourceTemplateFile"] = pppoe_template_file
    ppp_merge_dict["mergeTargetTag"] = "ttEmulatedDevice"
    proto_merge_dict = {}
    proto_merge_dict["mergeSourceTag"] = "ttPppoeClientBlockConfig"
    proto_merge_dict["mergeSourceTemplateFile"] = pppoe_template_file
    proto_merge_dict["mergeTargetTag"] = "ttEmulatedDevice"

    # Relation Info
    rm_ipv4_soe_eth_dict = {}
    rm_ipv4_soe_eth_dict["relationType"] = "StackedOnEndpoint"
    rm_ipv4_soe_eth_dict["sourceTag"] = "ttIpv4If"
    rm_ipv4_soe_eth_dict["targetTag"] = "ttEthIIIf"
    rm_ipv4_soe_eth_dict["removeRelation"] = True
    ipv4_soe_ppp_dict = {}
    ipv4_soe_ppp_dict["relationType"] = "StackedOnEndpoint"
    ipv4_soe_ppp_dict["sourceTag"] = "ttIpv4If"
    ipv4_soe_ppp_dict["targetTag"] = "ttPppIf"
    ppp_soe_pppoe_dict = {}
    ppp_soe_pppoe_dict["relationType"] = "StackedOnEndpoint"
    ppp_soe_pppoe_dict["sourceTag"] = "ttPppIf"
    ppp_soe_pppoe_dict["targetTag"] = "ttPppoeIf"
    pppoe_soe_eth_dict = {}
    pppoe_soe_eth_dict["relationType"] = "StackedOnEndpoint"
    pppoe_soe_eth_dict["sourceTag"] = "ttPppoeIf"
    pppoe_soe_eth_dict["targetTag"] = "ttEthIIIf"

    modify_list = []
    modify_list.append({"mergeList": [pppoe_merge_dict,
                                      ppp_merge_dict,
                                      proto_merge_dict]})
    modify_list.append({"relationList": [rm_ipv4_soe_eth_dict,
                                         ipv4_soe_ppp_dict,
                                         ppp_soe_pppoe_dict,
                                         pppoe_soe_eth_dict]})
    mix_part = {}
    mix_part["weight"] = 50
    mix_part["staticValue"] = 1
    mix_part["useStaticValue"] = False
    mix_part["baseTemplateFile"] = "IPv4_NoVlan.xml"
    mix_part["tagPrefix"] = "Right_Pppoe_"
    mix_part["modifyList"] = modify_list
    mix_part["useBlock"] = True

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    # Check the tags
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 6
    dev_tag = None
    ipv4_tag = None
    eth_tag = None
    pppoe_tag = None
    ppp_tag = None
    proto_tag = None
    for tag_ele in tag_ele_list:
        plLogger.LogDebug("tag_ele name: " + tag_ele.get("Name"))
        if tag_ele.get("Name") == "Right_Pppoe_ttEmulatedDevice":
            dev_tag = tag_ele
        elif tag_ele.get("Name") == "Right_Pppoe_ttIpv4If":
            ipv4_tag = tag_ele
        elif tag_ele.get("Name") == "Right_Pppoe_ttEthIIIf":
            eth_tag = tag_ele
        elif tag_ele.get("Name") == "Right_Pppoe_ttPppoeIf":
            pppoe_tag = tag_ele
        elif tag_ele.get("Name") == "Right_Pppoe_ttPppIf":
            ppp_tag = tag_ele
        elif tag_ele.get("Name") == "Right_Pppoe_ttPppoeClientBlockConfig":
            proto_tag = tag_ele
    assert dev_tag is not None
    assert ipv4_tag is not None
    assert eth_tag is not None
    assert pppoe_tag is not None
    assert ppp_tag is not None
    assert proto_tag is not None

    # EmulatedDevice
    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]

    # Children of EmulatedDevice
    ipv4_ele = None
    eth_ele = None
    pppoe_ele = None
    ppp_ele = None
    proto_ele = None
    for child in dev_ele:
        if child.tag == "PppoeClientBlockConfig":
            proto_ele = child
        elif child.tag == "Ipv4If":
            ipv4_ele = child
        elif child.tag == "EthIIIf":
            eth_ele = child
        elif child.tag == "PppoeIf":
            pppoe_ele = child
        elif child.tag == "PppIf":
            ppp_ele = child
    assert ipv4_ele is not None
    assert eth_ele is not None
    assert proto_ele is not None
    assert pppoe_ele is not None
    assert ppp_ele is not None

    # Interface Stack
    rel_list = ipv4_ele.findall(".//Relation")
    stack_count = 0
    tag_count = 0
    for rel in rel_list:
        if rel.get("type") == "StackedOnEndpoint":
            assert rel.get("target") == ppp_ele.get("id")
            stack_count = stack_count + 1
        elif rel.get("type") == "UserTag":
            assert rel.get("target") == ipv4_tag.get("id")
            tag_count = tag_count + 1
    assert stack_count == 1
    assert tag_count == 1
    rel_list = ppp_ele.findall(".//Relation")
    stack_count = 0
    tag_count = 0
    for rel in rel_list:
        if rel.get("type") == "StackedOnEndpoint":
            assert rel.get("target") == pppoe_ele.get("id")
            stack_count = stack_count + 1
        elif rel.get("type") == "UserTag":
            assert rel.get("target") == ppp_tag.get("id")
            tag_count = tag_count + 1
    assert stack_count == 1
    assert tag_count == 1
    rel_list = pppoe_ele.findall(".//Relation")
    stack_count = 0
    tag_count = 0
    for rel in rel_list:
        if rel.get("type") == "StackedOnEndpoint":
            assert rel.get("target") == eth_ele.get("id")
            stack_count = stack_count + 1
        elif rel.get("type") == "UserTag":
            assert rel.get("target") == pppoe_tag.get("id")
            tag_count = tag_count + 1
    assert stack_count == 1
    assert tag_count == 1
    rel_list = eth_ele.findall(".//Relation")
    stack_count = 0
    tag_count = 0
    for rel in rel_list:
        if rel.get("type") == "StackedOnEndpoint":
            stack_count = stack_count + 1
        elif rel.get("type") == "UserTag":
            assert rel.get("target") == eth_tag.get("id")
            tag_count = tag_count + 1
    assert stack_count == 0
    assert tag_count == 1

    # Clean up
    remove_unit_test_template(pppoe_template_file)


def test_config_pdus(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_config_pdus")
    plLogger.LogInfo("test_config_pdus")

    # Create a unit test protocol template
    sb_template = get_streamblock_template()
    sb_template_file = "unit_test_streamblock_template.xml"
    assert add_unit_test_template(sb_template_file, sb_template)

    # Create Ports and tag them
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    etcu = ctor.Create("EthernetCopper", port1)
    port1.AddObject(etcu, RelationType("ActivePhy"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    # Build the input JSON structure

    # Modify PDU Info
    src_dict = {}
    src_dict["templateElementTagName"] = "ttStreamBlock"
    src_dict["offsetReference"] = "ipv4_5265.sourceAddr"
    src_dict["value"] = "33.33.33.33"
    dst_dict = {}
    dst_dict["templateElementTagName"] = "ttStreamBlock"
    dst_dict["offsetReference"] = "ipv4_5265.destAddr"
    dst_dict["value"] = "44.44.44.44"

    modify_list = []
    modify_list.append({"pduModifierList": [src_dict, dst_dict]})

    mix_part = {}
    mix_part["baseTemplateFile"] = sb_template_file
    mix_part["tagPrefix"] = "My_Streamblock_"
    mix_part["modifyList"] = modify_list

    plLogger.LogInfo("mix_part: " + str(mix_part))
    input_json = json.dumps(mix_part)

    cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    cmd.Set("AutoExpandTemplate", True)
    cmd.Set("InputJson", input_json)
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()

    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    assert template is not None

    cmd.MarkDelete()

    # Check the template
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None

    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 1
    sb_tag = None
    for tag_ele in tag_ele_list:
        plLogger.LogDebug("tag_ele name: " + tag_ele.get("Name"))
        if tag_ele.get("Name") == "My_Streamblock_ttStreamBlock":
            sb_tag = tag_ele
    assert sb_tag is not None

    # StreamBlock
    sb_ele_list = root.findall(".//StreamBlock")
    assert len(sb_ele_list) == 1
    sb_ele = sb_ele_list[0]
    rel_list = sb_ele.findall(".//Relation")
    assert len(rel_list) > 0
    found_tag = False
    for rel in rel_list:
        if rel.get("type") == "UserTag":
            assert rel.get("target") == sb_tag.get("id")
            found_tag = True
    assert found_tag

    # Check the FrameConfig
    root = etree.fromstring(sb_ele.get("FrameConfig"))
    assert root.find(".//sourceAddr").text == "33.33.33.33"
    assert root.find(".//destAddr").text == "44.44.44.44"

    # Clean up
    remove_unit_test_template(sb_template_file)


def test_get_prop_val_lists(stc):
    pv_dict = {
        "PrefixLengthDist": [1] * 32,
        "Count": "32"
    }
    prop_list, val_list = CreateTempConfCmd.get_prop_val_lists(pv_dict,
                                                               'Ipv4RouteGenParams')
    # We can't guarantee order within a dict, unless we make it ordered
    assert 'Ipv4RouteGenParams.PrefixLengthDist' in prop_list
    assert 'Ipv4RouteGenParams.Count' in prop_list
    assert '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1' in val_list
    assert '32' in val_list
    # Change it to a list of strings of 1, should have the same result
    pv_dict = {
        "PrefixLengthDist": ['1'] * 32,
        "Count": "32"
    }
    # Don't prepend a prefix
    prop_list, val_list = CreateTempConfCmd.get_prop_val_lists(pv_dict)
    # We can't guarantee order within a dict, unless we make it ordered
    assert 'PrefixLengthDist' in prop_list
    assert 'Count' in prop_list
    assert '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1' in val_list
    assert '32' in val_list


def get_proto_template():
    return """
<Template>
<Description />
<Image />
<DataModelXml>
<StcSystem id="1">
  <Project id="2">
    <Tags id="1203">
      <Relation type="UserTag" target="1494"/>
      <Relation type="UserTag" target="1495"/>
      <Relation type="UserTag" target="1496"/>
      <Relation type="UserTag" target="1411"/>
      <Relation type="UserTag" target="1507"/>
      <Relation type="UserTag" target="1508"/>
      <Relation type="UserTag" target="1509"/>
      <Tag id="1494" Name="ttDhcpv4BlockConfig"></Tag>
      <Tag id="1495" Name="ttDhcpv4ServerConfig"></Tag>
      <Tag id="1496" Name="ttDhcpv4ServerDefaultPoolConfig"></Tag>
      <Tag id="1411" Name="ttBgpRouterConfig" />
      <Tag id="1507" Name="ttBgpIpv4RouteConfig" />
      <Tag id="1508" Name="ttIpv4NetworkBlock" />
      <Tag id="1509" Name="ttIpv4NetworkBlock.StartIpList" />
    </Tags>
    <EmulatedDevice id="2202">
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Dhcpv4BlockConfig id="2205">
        <Relation type="UsesIf" target="2203"/>
        <Relation type="UserTag" target="1494"/>
      </Dhcpv4BlockConfig>
      <Dhcpv4ServerConfig id="2206">
        <Relation type="UsesIf" target="2203"/>
        <Relation type="UserTag" target="1495"/>
        <Dhcpv4ServerDefaultPoolConfig id="2207">
          <Relation type="UserTag" target="1496"/>
        </Dhcpv4ServerDefaultPoolConfig>
      </Dhcpv4ServerConfig>
      <BgpRouterConfig id="22205" Active="TRUE" Name="BGP 1">
        <BgpIpv4RouteConfig Active="TRUE" NextHop="192.85.5.1" id="2909">
          <Relation target="1507" type="UserTag" />
          <Ipv4NetworkBlock Active="TRUE" NetworkCount="2000000"
             StartIpList="131.0.0.0" id="3090">
            <Relation target="1508" type="UserTag" />
            <StmPropertyModifier ModifierInfo='{
  "modifierType": "RANGE",
  "propertyName": "StartIpList",
  "objectName": "Ipv4NetworkBlock",
  "propertyValueDict": {
    "start": "131.0.0.0",
    "step": "0.1.0.0",
    "repeat": 0
    "recycle": 0
  }
}'
               TagName="ttIpv4NetworkBlock" id="1116">
              <Relation target="1509" type="UserTag" />
            </StmPropertyModifier>
          </Ipv4NetworkBlock>
          <BgpVpnRouteConfig Active="TRUE" VrfCount="1" id="3091">
          </BgpVpnRouteConfig>
        </BgpIpv4RouteConfig>
        <Relation type="UserTag" target="1411"/>
      </BgpRouterConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""


def get_pppoe_template():
    return """
<StcSystem id="1"
 Name="StcSystem 1">
  <Project id="2"
   Name="Project 1">
    <Tags id="1203">
      <Relation type="UserTag" target="1510"/>
      <Relation type="UserTag" target="1511"/>
      <Relation type="UserTag" target="1512"/>
      <Relation type="UserTag" target="1513"/>
      <Relation type="UserTag" target="1514"/>
      <Relation type="UserTag" target="1515"/>
      <Tag id="1510" Name="ttEmulatedDevice"/>
      <Tag id="1511" Name="ttIpv4If"/>
      <Tag id="1512" Name="ttEthIIIf"/>
      <Tag id="1513" Name="ttPppoeIf"/>
      <Tag id="1514" Name="ttPppIf"/>
      <Tag id="1515" Name="ttPppoeClientBlockConfig"/>
    </Tags>
    <EmulatedDevice id="2258" serializationBase="true" Name="Device 1">
      <Relation type="TopLevelIf" target="2259"/>
      <Relation type="PrimaryIf" target="2259"/>
      <Relation type="UserTag" target="1510"/>
      <Ipv4If id="2259" Name="IPv4 2">
        <Relation type="StackedOnEndpoint" target="1433"/>
        <Relation type="UserTag" target="1511"/>
      </Ipv4If>
      <EthIIIf id="2260" Name="EthernetII 2">
        <Relation type="UserTag" target="1512"/>
      </EthIIIf>
      <PppoeIf id="1432" Name="PPPoE 1">
        <Relation type="StackedOnEndpoint" target="2260"/>
        <Relation type="UserTag" target="1513"/>
      </PppoeIf>
      <PppIf id="1433" Name="PPP 3">
        <Relation type="StackedOnEndpoint" target="1432"/>
        <Relation type="UserTag" target="1514"/>
      </PppIf>
      <PppoeClientBlockConfig id="2261"
       Name="PppoeClientBlockConfig 1">
        <Relation type="UsesIf" target="2259"/>
        <Relation type="UserTag" target="1515"/>
      </PppoeClientBlockConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
"""


def get_streamblock_template():
    return """
<Template>
<Description />
<Image />
<DataModelXml>
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Relation type="DefaultSelection" target="1168"/>
    <Tags id="1208" Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Tag id="1400" Name="ttStreamBlock">
      </Tag>
    </Tags>
    <StreamBlock id="5263" serializationBase="true"
     FrameConfig="&lt;frame&gt;&lt;config&gt;
&lt;pdus&gt;&lt;pdu name=&quot;ipv4_5265&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
&lt;totalLength&gt;20&lt;/totalLength&gt;
&lt;fragOffset&gt;0&lt;/fragOffset&gt;
&lt;ttl&gt;255&lt;/ttl&gt;&lt;checksum&gt;14204&lt;/checksum&gt;
&lt;sourceAddr&gt;192.85.1.1&lt;/sourceAddr&gt;
&lt;destAddr&gt;192.85.1.3&lt;/destAddr&gt;
&lt;prefixLength&gt;24&lt;/prefixLength&gt;
&lt;destPrefixLength&gt;24&lt;/destPrefixLength&gt;
&lt;gateway&gt;192.85.1.1&lt;/gateway&gt;
&lt;tosDiffserv name=&quot;anon_5582&quot;&gt;
&lt;tos name=&quot;anon_5583&quot;&gt;
&lt;precedence&gt;6&lt;/precedence&gt;
&lt;dBit&gt;0&lt;/dBit&gt;
&lt;tBit&gt;0&lt;/tBit&gt;
&lt;rBit&gt;0&lt;/rBit&gt;
&lt;mBit&gt;0&lt;/mBit&gt;
&lt;reserved&gt;0&lt;/reserved&gt;
&lt;/tos&gt;&lt;/tosDiffserv&gt;
&lt;flags name=&quot;anon_5584&quot;&gt;
&lt;mfBit&gt;0&lt;/mfBit&gt;
&lt;/flags&gt;&lt;/pdu&gt;
&lt;/pdus&gt;&lt;/config&gt;
&lt;/frame&gt;"
     Name="Streamblock">
      <Relation type="UserTag" target="1400"/>
    </StreamBlock>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""
