from StcIntPythonPL import *
import os
import sys
import json
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import ConfigTemplateStmPropertyModifierCommand as ConfModCmd
import spirent.methodology.utils.json_utils as json_utils


PKG = "spirent.methodology"


def test_validate(stc):
    res = ConfModCmd.validate("", "", "", "", "", "", "", "", "", "", "", "")
    assert res == ""


def test_reset(stc):
    res = ConfModCmd.reset()
    assert res


def get_default_mod_info():
    pv_dict = {}
    pv_dict["start"] = "192.85.1.3"
    pv_dict["step"] = "0.0.0.1"
    pv_dict["repeat"] = 0
    pv_dict["recycle"] = 0
    mod_dict = {}
    mod_dict["modifierType"] = "RANGE"
    mod_dict["objectName"] = "Ipv4If"
    mod_dict["propertyName"] = "Address"
    mod_dict["propertyValueDict"] = pv_dict
    return json.dumps(mod_dict)


def test_gen_range_modifier_json():
    # Minimal
    mi = ConfModCmd.gen_range_modifier_json("EmulatedDevice", "DeviceCount",
                                            ["10", "20", "30"], "40")
    assert mi != ""
    err_str, act_dict = json_utils.load_json(mi)
    assert err_str == ""
    pv_dict = {}
    pv_dict["start"] = ["10", "20", "30"]
    pv_dict["step"] = "40"
    exp_dict = {}
    exp_dict["objectName"] = "EmulatedDevice"
    exp_dict["propertyName"] = "DeviceCount"
    exp_dict["modifierType"] = "RANGE"
    exp_dict["propertyValueDict"] = pv_dict
    assert act_dict == exp_dict

    # Optional repeat, recycle, targetObjectStep, and reset
    mi = ConfModCmd.gen_range_modifier_json("EmulatedDevice", "DeviceCount",
                                            "10", "20", repeat=30,
                                            recycle=40, target_step="50",
                                            reset=True)
    assert mi != ""
    # res = json_utils.validate_json(
    #     mi, proc_func.get_range_modifier_json_schema())
    # assert res == ""
    err_str, act_dict = json_utils.load_json(mi)
    assert err_str == ""
    pv_dict = {}
    pv_dict["start"] = "10"
    pv_dict["step"] = "20"
    pv_dict["repeat"] = 30
    pv_dict["recycle"] = 40
    pv_dict["targetObjectStep"] = "50"
    pv_dict["resetOnNewTargetObject"] = True
    exp_dict = {}
    exp_dict["objectName"] = "EmulatedDevice"
    exp_dict["propertyName"] = "DeviceCount"
    exp_dict["modifierType"] = "RANGE"
    exp_dict["propertyValueDict"] = pv_dict
    assert act_dict == exp_dict


def test_match_modifier_to_obj_and_prop_names(stc):
    # Create an StmPropertyModifier element
    root = etree.fromstring("<StmPropertyModifier ModifierInfo=\"\" />")
    assert root is not None
    pv_dict = {}
    pv_dict["start"] = "1.2.3.4"
    pv_dict["step"] = "0.0.0.1"
    pv_dict["repeat"] = 4
    pv_dict["recycle"] = 6
    pv_dict["targetObjectStep"] = "0.1.0.0"
    pv_dict["resetOnNewTargetObject"] = False
    m_dict = {}
    m_dict["objectName"] = "Ipv4If"
    m_dict["propertyName"] = "Address"
    m_dict["modifierType"] = "RANGE"
    m_dict["propertyValueDict"] = pv_dict
    root.set("ModifierInfo", json.dumps(m_dict))

    # Matches object and property
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "Ipv4If", "Address")
    assert err_str == ""
    assert res == root

    # Matches object, no property specified
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "Ipv4If", "")
    assert err_str == ""
    assert res == root

    # Matches object, doesn't match property
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "Ipv4If", "AddrList")
    assert err_str == ""
    assert res is None

    # No object, matches property
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "", "Address")
    assert err_str == ""
    assert res == root

    # No object, doesn't match property
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "", "AddrList")
    assert err_str == ""
    assert res is None

    # No object or property specified
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "", "")
    assert err_str == ""
    assert res == root

    # Missing node
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        None, "EmulatedDevice", "DeviceCount")
    assert "Invalid ElementTree element" in err_str
    assert res is None

    # Missing ModifierInfo
    root = etree.fromstring("<StmPropertyModifier />")
    assert root is not None
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "EmulatedDevice", "DeviceCount")
    assert "Missing ModifierInfo attribute" in err_str
    assert res is None

    # Invalid JSON/doesn't match schema
    root = etree.fromstring("<StmPropertyModifier ModifierInfo=\"{}\" />")
    assert root is not None
    err_str, res = ConfModCmd.match_modifier_to_obj_and_prop_names(
        root, "EmulatedDevice", "DeviceCount")
    assert "Failed to validate ModifierInfo JSON" in err_str
    assert res is None


def test_find_matching_modifiers(stc):
    # Create some StmPropertyModifier elements

    # Ipv4If - Address
    ipv4_addr = etree.fromstring("<StmPropertyModifier ModifierInfo=\"\" />")
    assert ipv4_addr is not None
    pv_dict = {}
    pv_dict["start"] = "1.2.3.4"
    pv_dict["step"] = "0.0.0.1"
    m_dict = {}
    m_dict["objectName"] = "Ipv4If"
    m_dict["propertyName"] = "Address"
    m_dict["modifierType"] = "RANGE"
    m_dict["propertyValueDict"] = pv_dict
    ipv4_addr.set("ModifierInfo", json.dumps(m_dict))

    # Ipv4If - AddrList
    ipv4_addr_list = etree.fromstring(
        "<StmPropertyModifier ModifierInfo=\"\" />")
    assert ipv4_addr_list is not None
    pv_dict = {}
    pv_dict["start"] = ["1.2.3.4"]
    pv_dict["step"] = ["0.0.0.1"]
    m_dict = {}
    m_dict["objectName"] = "Ipv4If"
    m_dict["propertyName"] = "AddrList"
    m_dict["modifierType"] = "RANGE"
    m_dict["propertyValueDict"] = pv_dict
    ipv4_addr_list.set("ModifierInfo", json.dumps(m_dict))

    # EmulatedDevice - DeviceCount
    dev_count = etree.fromstring(
        "<StmPropertyModifier ModifierInfo=\"\" />")
    assert dev_count is not None
    pv_dict = {}
    pv_dict["start"] = "100"
    pv_dict["step"] = "30"
    m_dict = {}
    m_dict["objectName"] = "EmulatedDevice"
    m_dict["propertyName"] = "DeviceCount"
    m_dict["modifierType"] = "RANGE"
    m_dict["propertyValueDict"] = pv_dict
    dev_count.set("ModifierInfo", json.dumps(m_dict))

    mod_list = [ipv4_addr, ipv4_addr_list, dev_count]

    # Test with nothing in the list
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        [], "EmulatedDevice", "DeviceCount")
    assert err_str == ""
    assert match_list == []

    # Test with match on nothing
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        mod_list, "", "")
    assert err_str == ""
    assert len(match_list) == 3
    assert ipv4_addr in match_list
    assert ipv4_addr_list in match_list
    assert dev_count in match_list

    # Test with match on just EmulatedDevice (no property)
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        mod_list, "EmulatedDevice", "")
    assert err_str == ""
    assert len(match_list) == 1
    assert dev_count in match_list

    # Test with match on DeviceCount (no object)
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        mod_list, "EmulatedDevice", "")
    assert err_str == ""
    assert len(match_list) == 1
    assert dev_count in match_list

    # Test with match on Ipv4If (no object)
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        mod_list, "Ipv4If", "")
    assert err_str == ""
    assert len(match_list) == 2
    assert ipv4_addr in match_list
    assert ipv4_addr_list in match_list

    # Test with match on BgpRouterConfig and AsNum
    err_str, match_list = ConfModCmd.find_matching_modifiers(
        mod_list, "BgpRouterConfig", "AsNum")
    assert err_str == ""
    assert match_list == []


def test_check_obj_and_prop_names(stc):
    # No object or property specified
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "", "")
    assert err_str == ""
    assert obj == ""
    assert prop == ""

    # Object specified, no property specified
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "EmulatedDevice", "")
    assert err_str == ""
    assert obj == "EmulatedDevice"
    assert prop == ""

    # Object and property specified
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "EmulatedDevice", "DeviceCount")
    assert err_str == ""
    assert obj == "EmulatedDevice"
    assert prop == "DeviceCount"

    # Invalid object specified
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "InvalidObject", "")
    assert "Invalid object with ObjectName: InvalidObject" in err_str
    assert obj == "InvalidObject"
    assert prop == ""

    # Valid object, invalid property specified
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "EmulatedDevice", "InvalidProperty")
    assert "does not have a property called InvalidProperty" in err_str
    assert obj == "EmulatedDevice"
    assert prop == "InvalidProperty"

    # No object specified (no error caught)
    err_str, obj, prop = ConfModCmd.check_obj_and_prop_names(
        "", "InvalidProperty")
    assert err_str == ""
    assert obj == ""
    assert prop == "InvalidProperty"


def test_config_existing_modifier(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    # Default ModifierInfo
    def_mod_info = get_default_mod_info()
    tag_name = "ttIpv4If"

    # Source XML
    src_xml = "<Template>" + \
              "<DataModelXml><StcSystem id=\"1\">" + \
              "<Project id=\"2\">" + \
              "<Tags id=\"3\">" + \
              "<Tag id=\"1234\" Name=\"ttIpv4If.Address\" />" + \
              "<Tag id=\"1235\" Name=\"ttNegativeTest.Property\" />" + \
              "<Tag id=\"5\" Name=\"ttIpv4If\" />" + \
              "<Relation type=\"UserTag\" target=\"1234\" />" + \
              "<Relation type=\"UserTag\" target=\"1235\" />" + \
              "<Relation type=\"UserTag\" target=\"5\" />" + \
              "</Tags>" + \
              "<Ipv4If id=\"11\" Name=\"Ipv4If\">" + \
              "<StmPropertyModifier id=\"12\" " + \
              "TagName=\"" + tag_name + "\" " + \
              "ModifierInfo=\'" + def_mod_info + "\'>" + \
              "<Relation type=\"UserTag\" " + \
              "target=\"1234\" />" + \
              "</StmPropertyModifier>" + \
              "<StmPropertyModifier id=\"13\" " + \
              "TagName=\"" + tag_name + "\" " + \
              "ModifierInfo=\"\">" + \
              "<Relation type=\"UserTag\" " + \
              "target=\"1235\" />" + \
              "</StmPropertyModifier>" + \
              "<Relation type=\"UserTag\" target=\"5\" />" + \
              "</Ipv4If></Project>" + \
              "</StcSystem></DataModelXml></Template>"

    plLogger = PLLogger.GetLogger("test_config_existing_modifiers")
    plLogger.LogInfo("src_xml: " + str(src_xml))

    temp_conf = ctor.Create("StmTemplateConfig", project)
    temp_conf.Set("TemplateXml", src_xml)

    # Modify the existing XML
    cmd = ctor.CreateCommand(PKG +
                             ".ConfigTemplateStmPropertyModifierCommand")
    cmd.Set("StmTemplateConfig", temp_conf.GetObjectHandle())
    cmd.Set("TagName", "ttIpv4If.Address")
    cmd.Set("TargetObjectTagName", "ttIpv4If")
    cmd.Set("ModifierType", "RANGE")
    cmd.SetCollection("StartList", ["1.2.3.4"])
    cmd.SetCollection("StepList", ["5.6.7.8"])
    cmd.SetCollection("RepeatList", [55])
    cmd.SetCollection("RecycleList", [66])
    cmd.Execute()
    cmd.MarkDelete()

    plLogger.LogInfo("modified XML: ")
    plLogger.LogInfo(temp_conf.Get("TemplateXml"))

    # Check the modified template XML
    root = etree.fromstring(temp_conf.Get("TemplateXml"))
    assert root is not None
    prop_mod_ele_list = root.findall(".//StmPropertyModifier")
    assert len(prop_mod_ele_list) == 2

    neg_prop_mod_ele = None
    prop_mod_ele = None
    for ele in prop_mod_ele_list:
        if ele.get("id") == "12":
            prop_mod_ele = ele
        elif ele.get("id") == "13":
            neg_prop_mod_ele = ele
    assert neg_prop_mod_ele is not None
    assert prop_mod_ele is not None

    # Check the positive case (was modified)
    exp_pv_dict = {}
    exp_pv_dict["start"] = ["1.2.3.4"]
    exp_pv_dict["step"] = ["5.6.7.8"]
    exp_pv_dict["repeat"] = [55]
    exp_pv_dict["recycle"] = [66]
    exp_mod_dict = {}
    exp_mod_dict["modifierType"] = "RANGE"
    exp_mod_dict["objectName"] = "Ipv4If"
    exp_mod_dict["propertyName"] = "Address"
    exp_mod_dict["propertyValueDict"] = exp_pv_dict
    exp_mod_info = json.dumps(exp_mod_dict)

    plLogger.LogInfo("exp: " + exp_mod_info)
    plLogger.LogInfo("act: " + prop_mod_ele.get("ModifierInfo"))

    assert prop_mod_ele.get("ModifierInfo") == exp_mod_info

    # Check the negative case (was not modified)
    assert neg_prop_mod_ele.get("ModifierInfo") == ""


def test_insert_new_modifier(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    tag_name = "ttIpv4If"

    # Source XML
    src_xml = "<Template>" + \
              "<DataModelXml><StcSystem id=\"1\">" + \
              "<Project id=\"2\">" + \
              "<Tags id=\"3\">" + \
              "<Tag id=\"1235\" Name=\"ttNegativeTest.Property\" />" + \
              "<Tag id=\"5\" Name=\"ttIpv4If\" />" + \
              "<Relation type=\"UserTag\" target=\"5\" />" + \
              "</Tags>" + \
              "<Ipv4If id=\"11\" Name=\"Ipv4If\">" + \
              "<StmPropertyModifier id=\"13\" " + \
              "TagName=\"" + tag_name + "\" " + \
              "ModifierInfo=\"\">" + \
              "<Relation type=\"UserTag\" " + \
              "target=\"1235\" />" + \
              "</StmPropertyModifier>" + \
              "<Relation type=\"UserTag\" target=\"5\" />" + \
              "</Ipv4If></Project>" + \
              "</StcSystem></DataModelXml></Template>"

    plLogger = PLLogger.GetLogger("test_insert_new_modifier")
    plLogger.LogInfo("src_xml: " + str(src_xml))

    temp_conf = ctor.Create("StmTemplateConfig", project)
    temp_conf.Set("TemplateXml", src_xml)

    # Modify the existing XML to insert a modifier
    cmd = ctor.CreateCommand(PKG +
                             ".ConfigTemplateStmPropertyModifierCommand")
    cmd.Set("StmTemplateConfig", temp_conf.GetObjectHandle())
    cmd.Set("TagName", "ttIpv4If.Address")
    cmd.Set("TargetObjectTagName", "ttIpv4If")
    cmd.Set("ObjectName", "Ipv4If")
    cmd.Set("PropertyName", "Address")
    cmd.Set("ModifierType", "RANGE")
    cmd.SetCollection("StartList", ["1.2.3.4"])
    cmd.SetCollection("StepList", ["5.6.7.8"])
    cmd.SetCollection("RepeatList", [55])
    cmd.SetCollection("RecycleList", [66])
    cmd.Execute()
    cmd.MarkDelete()

    plLogger.LogInfo("modified XML: ")
    plLogger.LogInfo(temp_conf.Get("TemplateXml"))

    # Check the modified template XML
    root = etree.fromstring(temp_conf.Get("TemplateXml"))
    assert root is not None
    prop_mod_ele_list = root.findall(".//StmPropertyModifier")
    assert len(prop_mod_ele_list) == 2

    neg_prop_mod_ele = None
    prop_mod_ele = None
    for ele in prop_mod_ele_list:
        if ele.get("id") == "13":
            neg_prop_mod_ele = ele
        else:
            # Not sure what the ID will be as this is created
            prop_mod_ele = ele
    assert neg_prop_mod_ele is not None
    assert prop_mod_ele is not None

    # Check the positive case (was modified)
    act_mod_str = prop_mod_ele.get("ModifierInfo")
    err_str, act_mod_dict = json_utils.load_json(act_mod_str)
    assert err_str == ""

    exp_mod_str = """
{
  "modifierType": "RANGE",
  "objectName": "Ipv4If",
  "propertyName": "Address",
  "propertyValueDict": {
    "start": ["1.2.3.4"],
    "step": ["5.6.7.8"],
    "repeat": [55],
    "resetOnNewTargetObject": true,
    "recycle": [66]
  }
}
"""
    err_str, exp_mod_dict = json_utils.load_json(exp_mod_str)
    assert err_str == ""
    plLogger.LogInfo("exp: " + str(exp_mod_dict))
    plLogger.LogInfo("act: " + str(act_mod_dict))
    assert exp_mod_dict == act_mod_dict

    assert prop_mod_ele.get("TagName") == "ttIpv4If"

    # Check the negative case (was not modified)
    assert neg_prop_mod_ele.get("ModifierInfo") == ""
