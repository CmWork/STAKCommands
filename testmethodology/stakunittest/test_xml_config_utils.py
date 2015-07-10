from StcIntPythonPL import *
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "STAKCommands",
                             "spirent", "methodology"))
import spirent.methodology.utils.xml_config_utils as xml_utils
import xml.etree.ElementTree as etree


def test_get_element():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)
    element = xml_utils.get_element(root, 'VlanIf')
    assert element is not None

    element = xml_utils.get_element(root, 'Invalid')
    assert element is None


def test_find_tag_elements():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)
    ele = xml_utils.find_tag_elements(root, "OuterVlan")
    assert ele is not None
    assert len(ele) == 1
    assert ele[0].get("Name") == "OuterVlan"
    ele = xml_utils.find_tag_elements(root, "ThirdStackedVlan")
    assert len(ele) == 0

    # Remove the Tags element
    project_ele_list = root.findall(".//" + "Project")
    assert len(project_ele_list) == 1
    project_ele = project_ele_list[0]
    assert project_ele is not None
    tags_ele_list = root.findall(".//" + "Tags")
    assert len(tags_ele_list) == 1
    project_ele.remove(tags_ele_list[0])

    # Run the search
    ele = xml_utils.find_tag_elements(root, "OuterVlan")
    assert len(ele) == 0


def test_build_tag_name_id_map():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    # Index on ID
    tag_dict = xml_utils.build_tag_name_id_map(root)
    assert len(tag_dict) == 10
    assert tag_dict["1204"] == "Host"
    assert tag_dict["1205"] == "Router"
    assert tag_dict["1206"] == "Client"
    assert tag_dict["1207"] == "Server"
    assert tag_dict["1208"] == "Core"
    assert tag_dict["1209"] == "Edge"
    assert tag_dict["1407"] == "OuterVlan"
    assert tag_dict["1409"] == "InnerVlan"
    assert tag_dict["1411"] == "Dhcpv4"
    assert tag_dict["1412"] == "TopLevelIf"

    # Index on Name
    tag_dict2 = xml_utils.build_tag_name_id_map(root,
                                                index_on_id=False)
    assert len(tag_dict2) == 10
    assert tag_dict2["Host"] == "1204"
    assert tag_dict2["Router"] == "1205"
    assert tag_dict2["Client"] == "1206"
    assert tag_dict2["Server"] == "1207"
    assert tag_dict2["Core"] == "1208"
    assert tag_dict2["Edge"] == "1209"
    assert tag_dict2["OuterVlan"] == "1407"
    assert tag_dict2["InnerVlan"] == "1409"
    assert tag_dict2["Dhcpv4"] == "1411"
    assert tag_dict2["TopLevelIf"] == "1412"


def test_find_tagged_elements():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    # Positive test
    outer_vlan_tag_ele = xml_utils.find_tag_elements(root, "OuterVlan")
    assert outer_vlan_tag_ele is not None
    assert len(outer_vlan_tag_ele) == 1
    tag_id = outer_vlan_tag_ele[0].get("id")
    assert tag_id is not None
    ele_list = xml_utils.find_tagged_elements(root, tag_id)
    assert len(ele_list) == 2
    found_tags = False
    found_vlanif = False
    for ele in ele_list:
        element_tag = ele.tag
        if element_tag == "VlanIf":
            found_vlanif = True
        elif element_tag == "Tags":
            found_tags = True
    assert found_tags
    assert found_vlanif

    # Negative test
    ele_list = xml_utils.find_tagged_elements(root, 0)
    assert len(ele_list) == 0

    # Add some extra tags
    eth_ele = root.find(".//" + "EthIIIf")
    assert eth_ele is not None
    new_tag = etree.Element("Relation")
    new_tag.set("target", tag_id)
    new_tag.set("type", "UserTag")
    eth_ele.append(new_tag)

    # Specify the element tag (positive test)
    ele_list = xml_utils.find_tagged_elements(root, tag_id,
                                              "EthIIIf")
    assert len(ele_list) == 1
    ele = ele_list[0]
    assert ele is not None
    assert ele.tag == "EthIIIf"
    ele_list = xml_utils.find_tagged_elements(root, tag_id,
                                              "Tags")
    assert len(ele_list) == 1
    ele = ele_list[0]
    assert ele is not None
    assert ele.tag == "Tags"

    # Specify the element tag (negative test)
    ele_list = xml_utils.find_tagged_elements(root, tag_id,
                                              "EmulatedDevice")
    assert len(ele_list) == 0


def test_find_tagged_elements_by_tag_name():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    # find_tagged_elements_by_tag_name returns Tags as well
    # because there is a UserTag relation to the Tag objects
    ele_list = xml_utils.find_tagged_elements_by_tag_name(root,
                                                          ["TopLevelIf"],
                                                          ignore_tags_element=False)
    assert len(ele_list) == 2
    found_tags = False
    found_ipv4 = False
    for ele in ele_list:
        if ele.tag == "Ipv4If":
            found_ipv4 = True
        elif ele.tag == "Tags":
            found_tags = True
    assert found_tags
    assert found_ipv4

    # Get multiple tagged elements
    ele_list = xml_utils.find_tagged_elements_by_tag_name(
        root, ["TopLevelIf", "Dhcpv4"], ignore_tags_element=False)
    assert len(ele_list) == 3
    found_ipv4 = False
    found_dhcp = False
    found_tags = False
    for ele in ele_list:
        if ele.tag == "Ipv4If":
            found_ipv4 = True
        elif ele.tag == "Dhcpv4BlockConfig":
            found_dhcp = True
        elif ele.tag == "Tags":
            found_tags = True
    assert found_ipv4
    assert found_dhcp
    assert found_tags

    # Get multiple tagged elements, ignore_tags_element (default)
    ele_list = xml_utils.find_tagged_elements_by_tag_name(
        root, ["TopLevelIf", "Dhcpv4"])
    assert len(ele_list) == 2
    found_ipv4 = False
    found_dhcp = False
    found_tags = False
    for ele in ele_list:
        if ele.tag == "Ipv4If":
            found_ipv4 = True
        elif ele.tag == "Dhcpv4BlockConfig":
            found_dhcp = True
        elif ele.tag == "Tags":
            found_tags = True
    assert found_ipv4
    assert found_dhcp
    assert not found_tags


def test_get_parent():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    tag_list = root.findall(".//" + "Tag")
    assert len(tag_list) > 0
    parent = xml_utils.get_parent(root, tag_list[0])
    assert parent is not None
    assert parent.tag == "Tags"
    assert parent.get("id") == "1203"

    dhcp_list = root.findall(".//" + "Dhcpv4BlockConfig")
    assert len(dhcp_list) == 1
    rel_list = dhcp_list[0].findall(".//" + "Relation")
    assert len(rel_list) == 2
    parent = xml_utils.get_parent(root, rel_list[0])
    assert parent is not None
    assert parent.tag == "Dhcpv4BlockConfig"
    assert parent.get("id") == "2205"

    parent = xml_utils.get_parent(root, dhcp_list[0])
    assert parent is not None
    assert parent.tag == "EmulatedDevice"
    assert parent.get("id") == "2202"

    # Negative test
    parent = xml_utils.get_parent(None, None)
    assert parent is None

    # StcSystem
    stc_sys_ele_list = root.findall(".//StcSystem")
    assert len(stc_sys_ele_list) == 1
    parent = xml_utils.get_parent(root, stc_sys_ele_list[0])
    assert parent is None

    # Root
    parent = xml_utils.get_parent(root, root)
    assert parent is None


def test_get_child():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    child_ele = xml_utils.get_child(dev_ele, "Ipv4If")
    assert child_ele is not None
    assert child_ele.tag == "Ipv4If"
    child_ele = xml_utils.get_child(dev_ele, "FakeChild")
    assert child_ele is None
    child_ele = xml_utils.get_child(dev_ele, "VlanIf")
    assert child_ele is not None
    assert child_ele.tag == "VlanIf"

    # Should not look any deeper than immediate children
    proj_ele = root.find(".//Project")
    assert proj_ele is not None
    child_ele = xml_utils.get_child(proj_ele, "Ipv4If")
    assert child_ele is None


def test_get_children():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    dev_ele_list = root.findall(".//EmulatedDevice")
    assert len(dev_ele_list) == 1
    dev_ele = dev_ele_list[0]
    children_list = xml_utils.get_children(dev_ele, "Ipv4If")
    assert len(children_list) == 1
    assert children_list[0].tag == "Ipv4If"
    children_list = xml_utils.get_children(dev_ele, "FakeChild")
    assert len(children_list) == 0
    children_list = xml_utils.get_children(dev_ele, "VlanIf")
    assert len(children_list) == 2
    for child_ele in children_list:
        assert child_ele.tag == "VlanIf"

    # Should not look any deeper than immediate children
    proj_ele = root.find(".//Project")
    assert proj_ele is not None
    children_list = xml_utils.get_children(proj_ele, "VlanIf")
    assert len(children_list) == 0


def test_get_etree_copy():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    root_copy = xml_utils.get_etree_copy(root)
    assert root_copy is not None
    proj_ele = root.find(".//Project")
    assert proj_ele is not None
    proj_ele.set("Name", "Project Copy")
    proj_ele_copy = root_copy.find(".//Project")
    assert proj_ele_copy is not None
    assert proj_ele_copy.get("Name") == "Project 1"
    del root
    assert root_copy is not None


def test_get_max_object_id():
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)

    max_id = xml_utils.get_max_object_id(root, 0)
    assert max_id == 2205

    # Pass a value in that is greater than the max
    # of any id in the file - should return it back
    # due to the recursive nature of the function
    max_id = xml_utils.get_max_object_id(root, 2206)
    assert max_id == 2206

    # Insert a max value somewhere in the XML
    ipv4if_ele_list = root.findall(".//" + "Ipv4If")
    assert len(ipv4if_ele_list) == 1
    ipv4if_ele = ipv4if_ele_list[0]
    assert ipv4if_ele is not None
    ipv4if_ele.set("id", "10001")

    max_id = xml_utils.get_max_object_id(root, 0)
    assert max_id == 10001


def test_create_relation_element(stc):
    # Note this is not "real" STC XML
    test_xml = "<Tags id=\"1203\" " + \
               "Name=\"Tags 1\">" + \
               "<Relation type=\"UserTag\" target=\"1407\"/>" + \
               "<Relation type=\"UserTag\" target=\"1408\"/>" + \
               "<Tag id=\"1407\" " + \
               "Name=\"OuterVlan\">" + \
               "</Tag>" + \
               "<Tag id=\"1408\" " + \
               "Name=\"InnerVlan\">" + \
               "</Tag>" + \
               "</Tags>"
    root = etree.fromstring(test_xml)
    tag_list = root.findall(".//" + "Tag")
    assert len(tag_list) == 2
    inner_ele = None
    outer_ele = None
    for tag_ele in tag_list:
        if tag_ele.get("Name") == "OuterVlan":
            outer_ele = tag_ele
        elif tag_ele.get("Name") == "InnerVlan":
            inner_ele = tag_ele
    assert inner_ele is not None
    assert outer_ele is not None

    # (Don't actually do this - these aren't interfaces)
    # Build a fake relation from inner to outer:
    # InnerVlan -> StackedOnEndpoint-targets -> OuterVlan
    xml_utils.create_relation_element(inner_ele,
                                      "StackedOnEndpoint",
                                      outer_ele.get("id"))
    exp_xml = "<Tags Name=\"Tags 1\" " + \
              "id=\"1203\">" + \
              "<Relation target=\"1407\" type=\"UserTag\" />" + \
              "<Relation target=\"1408\" type=\"UserTag\" />" + \
              "<Tag Name=\"OuterVlan\" id=\"1407\" />" + \
              "<Tag Name=\"InnerVlan\" id=\"1408\">" + \
              "<Relation target=\"" + \
              str(outer_ele.get("id")) + "\" " + \
              "type=\"StackedOnEndpoint\" />" + \
              "</Tag>" + \
              "</Tags>"

    act_xml = etree.tostring(root)
    assert act_xml == exp_xml


def test_strip_modifiers(stc):
    test_xml = get_sample_test_xml()
    root = etree.fromstring(test_xml)
    mod_list = root.findall(".//" + "StmPropertyModifier")
    assert len(mod_list) == 9
    stripped_xml = xml_utils.strip_modifiers(test_xml)
    root = etree.fromstring(stripped_xml)
    mod_list = root.findall(".//" + "StmPropertyModifier")
    assert len(mod_list) == 0


def test_escape_xml():
    xml_str = "<Property attribute1=\"value\" " + \
              "attribute2=\'value2\'>" + \
              "<Prop2 value=\"&\" />" + \
              "</Property>"
    mod_str = xml_utils.escape_xml(xml_str)
    assert mod_str == "&lt;Property attribute1=&quot;value&quot; " + \
        "attribute2=&apos;value2&apos;&gt;&lt;Prop2 value=&quot;&amp;&quot; " + \
        "/&gt;&lt;/Property&gt;"


def test_unescape_xml():
    xml_str = "&lt;Property attribute1=&quot;value&quot; " + \
              "attribute2=&apos;value2&apos;&gt;&lt;Prop2 " + \
              "value=&quot;&amp;&quot; " + \
              "/&gt;&lt;/Property&gt;"
    mod_str = xml_utils.unescape_xml(xml_str)
    assert mod_str == "<Property attribute1=\"value\" " + \
        "attribute2=\'value2\'>" + \
        "<Prop2 value=\"&\" />" + \
        "</Property>"


def test_parse_property_value_list():
    prop_val_list = []
    res = xml_utils.parse_property_value_list(prop_val_list)
    assert res == ({"obj_list": []}, "")

    # Single Type
    vlan_val_list = ["VlanIf.VlanId=123", "VlanIf.IdStep=321",
                     "VlanIf.Priority=5"]
    res, msg = xml_utils.parse_property_value_list(vlan_val_list)
    assert msg == ""
    key_list = res.keys()
    assert "VlanIf.VlanId" in key_list
    assert "VlanIf.IdStep" in key_list
    assert "VlanIf.Priority" in key_list
    assert res["VlanIf.VlanId"] == "123"
    assert res["VlanIf.IdStep"] == "321"
    assert res["VlanIf.Priority"] == "5"
    assert len(res["obj_list"]) == 1
    assert "VlanIf" in res["obj_list"]
    assert len(res["VlanIf"]) == 3
    assert "VlanId" in res["VlanIf"]
    assert "IdStep" in res["VlanIf"]
    assert "Priority" in res["VlanIf"]

    # Multiple Types
    prop_val_list = ["VlanIf.VlanId=111", "Ipv4If.Address=44.44.44.44",
                     "VlanIf.Priority=2", "BgpRouterConfig.AsNum=400"]
    res2, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == ""
    key_list = res2.keys()
    assert "VlanIf.VlanId" in key_list
    assert "VlanIf.Priority" in key_list
    assert "Ipv4If.Address" in key_list
    assert "BgpRouterConfig.AsNum" in key_list
    assert res2["VlanIf.VlanId"] == "111"
    assert res2["VlanIf.Priority"] == "2"
    assert res2["Ipv4If.Address"] == "44.44.44.44"
    assert res2["BgpRouterConfig.AsNum"] == "400"
    assert len(res2["obj_list"]) == 3
    assert "VlanIf" in res2["obj_list"]
    assert "Ipv4If" in res2["obj_list"]
    assert "BgpRouterConfig" in res2["obj_list"]
    assert len(res2["VlanIf"]) == 2
    assert len(res2["Ipv4If"]) == 1
    assert len(res2["BgpRouterConfig"]) == 1
    assert "VlanId" in res2["VlanIf"]
    assert "Priority" in res2["VlanIf"]
    assert "Address" in res2["Ipv4If"]
    assert "AsNum" in res2["BgpRouterConfig"]

    # Invalid Class name
    prop_val_list = ["BgpRouterConfig.AsNum=132",
                     "InvalidClassName.VlanId=111",
                     "Ipv4If.Address=44.44.44.44"]
    res3, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Invalid classname: InvalidClassName specified " + \
        "in property value list."
    assert res3 is None

    # Invalid Property name
    prop_val_list = ["BgpRouterConfig.AsNum=123",
                     "VlanIf.InvalidProperty=123",
                     "Ipv4If.Address=44.44.44.44"]
    res4, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Property InvalidProperty not found in class VlanIf"
    assert res4 is None

    # Invalid Value (int)
    prop_val_list = ["BgpRouterConfig.AsNum=abc",
                     "VlanIf.VlanId=111"]
    res5, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Value abc is not valid for property AsNum on " + \
        "class BgpRouterConfig: " + \
        "Invalid uint16 \"abc\": should be decimal or 0x " + \
        "followed by hexadecimal"
    assert res5 is None

    # Invalid Value (ip)
    prop_val_list = ["Ipv4If.Address=a.b.c.d"]
    res6, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Value a.b.c.d is not valid for property Address " + \
        "on class Ipv4If: " + \
        "Error during conversion: Cannot convert IP address " + \
        "\"a.b.c.d\". Expecting a dotted decimal IPv4 address " + \
        "(e.g. 10.1.2.3)"
    assert res6 is None

    # Invalid bool
    prop_val_list = ["Ipv4If.IsRange=YEAH_RIGHT"]
    res7, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Value YEAH_RIGHT is not valid for property IsRange " + \
        "on class Ipv4If: " + \
        "Error during conversion: Cannot convert bool \"YEAH_RIGHT\". " + \
        "Expecting true, on, yes, 1, or false, off, no, 0"
    assert res7 is None

    # Invalid enum
    prop_val_list = ["BfdRouterConfig.ScaleMode=NOT_NORMAL"]
    res9, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Invalid value NOT_NORMAL given for property " + \
        "ScaleMode on class BfdRouterConfig"
    assert res9 is None

    # Several invalid values (only the first one triggers an error)
    prop_val_list = ["Ipv4If.Address=1.2.3.4",
                     "VlanIf.VlanId=huh",
                     "FakeClass.FakeProperty=FakeValue"]
    res8, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert msg == "Value huh is not valid for property VlanId " + \
        "on class VlanIf: " + \
        "Invalid uint16 \"huh\": should be decimal or 0x followed " + \
        "by hexadecimal"
    assert res8 is None

    # Value has spaces in it
    prop_val_list = ["EmulatedDevice.Name=SPIRENT TEST"]
    res9, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert res9 is not None
    key_list = res9.keys()
    assert "EmulatedDevice.Name" in key_list
    assert res9["EmulatedDevice"] == ["Name"]
    assert res9["EmulatedDevice.Name"] == "SPIRENT TEST"
    assert res9["obj_list"] == ["EmulatedDevice"]

    # StmPropertyModifier
    mod_info = "\"&lt;Modifier " + \
               "ModifierType=&quot;RANGE&quot; " + \
               "PropertyName=&quot;Address&quot; " + \
               "ObjectName=&quot;Ipv6If&quot;&gt; " + \
               "&lt;Start&gt;1111::2&lt;/Start&gt; " + \
               "&lt;Step&gt;::1&lt;/Step&gt; " + \
               "&lt;Repeat&gt;0&lt;/Repeat&gt; " + \
               "&lt;Recycle&gt;0&lt;/Recycle&gt;" + \
               "&lt;/Modifier&gt;\""
    prop_val_list = ["StmPropertyModifier.ModifierInfo=" +
                     mod_info]
    res10, msg = xml_utils.parse_property_value_list(prop_val_list)
    assert res10 is not None
    key_list = res10.keys()
    assert "StmPropertyModifier.ModifierInfo" in key_list
    assert res10["StmPropertyModifier"] == ["ModifierInfo"]
    assert res10["StmPropertyModifier.ModifierInfo"] == \
        mod_info
    assert res10["obj_list"] == ["StmPropertyModifier"]


def test_parse_prop_and_val_list():
    prop_list = []
    val_list = []
    a_dict, res = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert res == ""
    assert a_dict == {"obj_list": []}

    # Invalid number of list entries
    prop_list = ["project.name"]
    val_list = []
    a_dict, res = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert res == "PropertyList and ValueList must have the " + \
        "same number of elements."
    assert a_dict is None

    # Invalid property entry
    prop_list = ["project"]
    val_list = ["My Project"]
    a_dict, res = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert res == "Format of PropertyList item project is invalid.  " + \
        "Item should be in the form Object.Property."
    assert a_dict is None

    # Invalid classname
    prop_list = ["InvalidClassName.InvalidProperty"]
    val_list = ["Invalid Value"]
    a_dict, res = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert res == "Invalid classname: InvalidClassName specified " + \
        "in PropertyList."
    assert a_dict is None

    # Invalid property
    prop_list = ["VlanIf.InvalidProperty"]
    val_list = ["InvalidValue"]
    a_dict, res = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert res == "Property InvalidProperty not found in class VlanIf"
    assert a_dict is None

    # Invalid value (int)
    prop_list = ["BgpRouterConfig.AsNum", "VlanIf.VlanId"]
    val_list = ["abc", 111]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == "Value abc is not valid for property AsNum on " + \
        "class BgpRouterConfig: " + \
        "Invalid uint16 \"abc\": should be decimal or 0x " + \
        "followed by hexadecimal"
    assert a_dict is None

    # Invalid value (ip)
    prop_list = ["Ipv4If.Address"]
    val_list = ["a.b.c.d"]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == "Value a.b.c.d is not valid for property Address " + \
        "on class Ipv4If: " + \
        "Error during conversion: Cannot convert IP address " + \
        "\"a.b.c.d\". Expecting a dotted decimal IPv4 address " + \
        "(e.g. 10.1.2.3)"
    assert a_dict is None

    # Invalid bool
    prop_list = ["Ipv4If.IsRange"]
    val_list = ["YEAH_RIGHT"]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == "Value YEAH_RIGHT is not valid for property IsRange " + \
        "on class Ipv4If: " + \
        "Error during conversion: Cannot convert bool \"YEAH_RIGHT\". " + \
        "Expecting true, on, yes, 1, or false, off, no, 0"
    assert a_dict is None

    # Invalid enum
    prop_list = ["BfdRouterConfig.ScaleMode"]
    val_list = ["NOT_NORMAL"]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == "Invalid value NOT_NORMAL given for property " + \
        "ScaleMode on class BfdRouterConfig"
    assert a_dict is None

    # Several invalid values (only the first one triggers an error)
    prop_list = ["Ipv4If.Address", "VlanIf.VlanId",
                 "FakeClass.FakeProperty"]
    val_list = ["1.2.3.4", "huh", "FakeValue"]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == "Value huh is not valid for property VlanId " + \
        "on class VlanIf: " + \
        "Invalid uint16 \"huh\": should be decimal or 0x followed " + \
        "by hexadecimal"
    assert a_dict is None

    # Single Class
    prop_list = ["VlanIf.VlanId", "VlanIf.IdStep",
                 "VlanIf.Priority"]
    val_list = [123, 321, "5"]
    res, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == ""
    key_list = res.keys()
    assert "VlanIf.VlanId" in key_list
    assert "VlanIf.IdStep" in key_list
    assert "VlanIf.Priority" in key_list
    assert res["VlanIf.VlanId"] == 123
    assert res["VlanIf.IdStep"] == 321
    assert res["VlanIf.Priority"] == "5"
    assert len(res["obj_list"]) == 1
    assert "VlanIf" in res["obj_list"]
    assert len(res["VlanIf"]) == 3
    assert "VlanId" in res["VlanIf"]
    assert "IdStep" in res["VlanIf"]
    assert "Priority" in res["VlanIf"]

    # Multiple Classes
    prop_list = ["VlanIf.VlanId", "Ipv4If.Address",
                 "VlanIf.Priority", "BgpRouterConfig.AsNum"]
    val_list = [111, "44.44.44.44", 2, 400]
    res, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == ""
    key_list = res.keys()
    assert "VlanIf.VlanId" in key_list
    assert "VlanIf.Priority" in key_list
    assert "Ipv4If.Address" in key_list
    assert "BgpRouterConfig.AsNum" in key_list
    assert res["VlanIf.VlanId"] == 111
    assert res["VlanIf.Priority"] == 2
    assert res["Ipv4If.Address"] == "44.44.44.44"
    assert res["BgpRouterConfig.AsNum"] == 400
    assert len(res["obj_list"]) == 3
    assert "VlanIf" in res["obj_list"]
    assert "Ipv4If" in res["obj_list"]
    assert "BgpRouterConfig" in res["obj_list"]
    assert len(res["VlanIf"]) == 2
    assert len(res["Ipv4If"]) == 1
    assert len(res["BgpRouterConfig"]) == 1
    assert "VlanId" in res["VlanIf"]
    assert "Priority" in res["VlanIf"]
    assert "Address" in res["Ipv4If"]
    assert "AsNum" in res["BgpRouterConfig"]

    # Value has spaces in it
    prop_list = ["EmulatedDevice.Name"]
    val_list = ["SPIRENT TEST"]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert a_dict is not None
    key_list = a_dict.keys()
    assert "EmulatedDevice.Name" in key_list
    assert a_dict["EmulatedDevice"] == ["Name"]
    assert a_dict["EmulatedDevice.Name"] == "SPIRENT TEST"
    assert a_dict["obj_list"] == ["EmulatedDevice"]

    # StmPropertyModifier
    mod_info = "\"&lt;Modifier " + \
               "ModifierType=&quot;RANGE&quot; " + \
               "PropertyName=&quot;Address&quot; " + \
               "ObjectName=&quot;Ipv6If&quot;&gt; " + \
               "&lt;Start&gt;1111::2&lt;/Start&gt; " + \
               "&lt;Step&gt;::1&lt;/Step&gt; " + \
               "&lt;Repeat&gt;0&lt;/Repeat&gt; " + \
               "&lt;Recycle&gt;0&lt;/Recycle&gt;" + \
               "&lt;/Modifier&gt;\""
    prop_list = ["StmPropertyModifier.ModifierInfo"]
    val_list = [mod_info]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == ""
    assert a_dict is not None
    key_list = a_dict.keys()
    assert "StmPropertyModifier.ModifierInfo" in key_list
    assert a_dict["StmPropertyModifier"] == ["ModifierInfo"]
    assert a_dict["StmPropertyModifier.ModifierInfo"] == mod_info
    assert a_dict["obj_list"] == ["StmPropertyModifier"]

    # Multiple periods (ie STAK Command name)
    pkg = "spirent.methodology"
    class_name = pkg + ".ModifyTemplatePropertyCommand"
    prop_list = [class_name + ".PropertyList"]
    val_list = [[22]]
    a_dict, msg = xml_utils.parse_prop_and_val_list(prop_list, val_list)
    assert msg == ""
    assert a_dict is not None
    key_list = a_dict.keys()
    assert class_name + ".PropertyList" in key_list
    assert class_name in key_list
    assert a_dict[class_name] == ["PropertyList"]
    assert a_dict[class_name + ".PropertyList"] == [22]
    assert a_dict["obj_list"] == [class_name]


def test_get_handle_props(stc):
    # Test a valid BLL command
    hnd_props = xml_utils.get_handle_props("ArpNdStartCommand")
    assert len(hnd_props) > 0
    assert "Handle" in hnd_props
    assert "HandleList" in hnd_props
    assert "EncapList" in hnd_props
    assert "ArpNdOption" not in hnd_props
    assert "ArpNdState" not in hnd_props
    assert "ForceArp" not in hnd_props

    # Test a STAK command
    pkg = "spirent.methodology"
    hnd_props = xml_utils.get_handle_props(pkg + ".ModifyTemplatePropertyCommand")
    assert len(hnd_props) > 0
    assert "StmTemplateConfig" in hnd_props
    assert "TagNameList" not in hnd_props
    assert "PropertyValueList" not in hnd_props

    # Test an invalid object
    hnd_props = xml_utils.get_handle_props("blah")
    assert len(hnd_props) == 0


def test_build_id_map(stc):
    # Use the test_xml to build a map
    root = etree.fromstring(get_sample_test_xml())
    id_map = {}
    xml_utils.build_id_map(root, id_map)
    plLogger = PLLogger.GetLogger("test_build_id_map")
    plLogger.LogInfo("id_map: " + str(id_map))
    assert "1" in id_map.keys()
    assert id_map["1"] == root.find(".//StcSystem")
    assert "2" in id_map.keys()
    assert id_map["2"] == root.find(".//Project")
    assert "1409" in id_map.keys()
    assert id_map["1409"] in root.findall(".//Tag")
    assert "11" in id_map.keys()
    assert id_map["11"] in root.findall(".//StmPropertyModifier")
    assert "17" in id_map.keys()
    assert id_map["17"] in root.findall(".//StmPropertyModifier")


def test_renormalize_xml_obj_ids(stc):
    plLogger = PLLogger.GetLogger("test_renormalize_xml_obj_ids")
    plLogger.LogInfo("start")
    seq_xml = get_sample_seq_xml()
    root = etree.fromstring(seq_xml)
    assert root is not None

    # Call with default
    xml_utils.renormalize_xml_obj_ids(root)
    max_id = xml_utils.get_max_object_id(root, 0)
    assert max_id == 34

    # Check Object IDs
    sys_ele = root.find(".//StcSystem")
    assert sys_ele is not None
    assert sys_ele.get("id") == "1"
    project_ele = root.find(".//Project")
    assert project_ele is not None
    assert project_ele.get("id") == "2"
    port_ele = root.find(".//Port")
    assert port_ele is not None
    assert port_ele.get("id") == "14"
    iter_cmd_ele = root.find(".//spirent.methodology.ObjectIteratorCommand")
    assert iter_cmd_ele is not None
    assert iter_cmd_ele.get("id") == "23"
    gen_start_cmd_ele = root.find(".//GeneratorStartCommand")
    assert gen_start_cmd_ele is not None
    assert gen_start_cmd_ele.get("id") == "26"
    gen_start_wait_cmd_ele = root.find(".//GeneratorWaitForStartCommand")
    assert gen_start_wait_cmd_ele is not None
    assert gen_start_wait_cmd_ele.get("id") == "27"
    ana_stop_cmd_ele = root.find(".//AnalyzerStopCommand")
    assert ana_stop_cmd_ele is not None
    assert ana_stop_cmd_ele.get("id") == "32"

    # Check Tags
    tags_ele = root.find(".//Tags")
    assert tags_ele is not None
    assert tags_ele.get("id") == "3"
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 8
    ctc_tag_ele = None
    gen_start_tag_ele = None
    gen_stop_tag_ele = None
    ana_stop_tag_ele = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "stSmCreateTemplateConfig":
            assert tag_ele.get("id") == "4"
            ctc_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stGeneratorStart":
            assert tag_ele.get("id") == "8"
            gen_start_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stGeneratorStop":
            assert tag_ele.get("id") == "9"
            gen_stop_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stAnalyzerStop":
            assert tag_ele.get("id") == "11"
            ana_stop_tag_ele = tag_ele
    assert ctc_tag_ele is not None
    assert gen_start_tag_ele is not None
    assert gen_stop_tag_ele is not None
    assert ana_stop_tag_ele is not None

    # Check relations - UserTag
    rel_ele_list = gen_start_cmd_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "UserTag"
    assert rel_ele.get("target") == "8"
    rel_ele_list = ana_stop_cmd_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "UserTag"
    assert rel_ele.get("target") == "11"

    # Check relations - Other
    rel_ele_list = port_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "ActivePhy"
    assert rel_ele.get("target") == "20"
    seq_ele = root.find(".//Sequencer")
    assert seq_ele is not None
    assert seq_ele.get("id") == "21"
    rel_ele_list = xml_utils.get_children(seq_ele, "Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "SequencerFinalizeType"
    assert rel_ele.get("target") == "34"

    # Check properties
    assert seq_ele.get("CommandList") == "33 22"
    assert gen_start_cmd_ele.get("GeneratorList") == "15"
    assert gen_start_wait_cmd_ele.get("GeneratorList") == "14"
    assert ana_stop_cmd_ele.get("AnalyzerList") == "17"
    while_cmd_ele = seq_ele.find(".//SequencerWhileCommand")
    assert while_cmd_ele is not None
    assert while_cmd_ele.get("CommandList") == "24 25 26 27 28 29 30 31 32"

    # Call with different start ID
    xml_utils.renormalize_xml_obj_ids(root, start_id=100)
    max_id = xml_utils.get_max_object_id(root, 0)
    assert max_id == 133

    # Check Object IDs
    sys_ele = root.find(".//StcSystem")
    assert sys_ele is not None
    assert sys_ele.get("id") == "100"
    project_ele = root.find(".//Project")
    assert project_ele is not None
    assert project_ele.get("id") == "101"
    port_ele = root.find(".//Port")
    assert port_ele is not None
    assert port_ele.get("id") == "113"
    iter_cmd_ele = root.find(".//spirent.methodology.ObjectIteratorCommand")
    assert iter_cmd_ele is not None
    assert iter_cmd_ele.get("id") == "122"
    gen_start_cmd_ele = root.find(".//GeneratorStartCommand")
    assert gen_start_cmd_ele is not None
    assert gen_start_cmd_ele.get("id") == "125"
    gen_start_wait_cmd_ele = root.find(".//GeneratorWaitForStartCommand")
    assert gen_start_wait_cmd_ele is not None
    assert gen_start_wait_cmd_ele.get("id") == "126"
    ana_stop_cmd_ele = root.find(".//AnalyzerStopCommand")
    assert ana_stop_cmd_ele is not None
    assert ana_stop_cmd_ele.get("id") == "131"

    # Check Tags
    tags_ele = root.find(".//Tags")
    assert tags_ele is not None
    assert tags_ele.get("id") == "102"
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 8
    ctc_tag_ele = None
    gen_start_tag_ele = None
    gen_stop_tag_ele = None
    ana_stop_tag_ele = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "stSmCreateTemplateConfig":
            assert tag_ele.get("id") == "103"
            ctc_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stGeneratorStart":
            assert tag_ele.get("id") == "107"
            gen_start_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stGeneratorStop":
            assert tag_ele.get("id") == "108"
            gen_stop_tag_ele = tag_ele
        elif tag_ele.get("Name") == "stAnalyzerStop":
            assert tag_ele.get("id") == "110"
            ana_stop_tag_ele = tag_ele
    assert ctc_tag_ele is not None
    assert gen_start_tag_ele is not None
    assert gen_stop_tag_ele is not None
    assert ana_stop_tag_ele is not None

    # Check relations - UserTag
    rel_ele_list = gen_start_cmd_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "UserTag"
    assert rel_ele.get("target") == "107"
    rel_ele_list = ana_stop_cmd_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "UserTag"
    assert rel_ele.get("target") == "110"

    # Check relations - Other
    rel_ele_list = port_ele.findall(".//Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "ActivePhy"
    assert rel_ele.get("target") == "119"
    seq_ele = root.find(".//Sequencer")
    assert seq_ele is not None
    assert seq_ele.get("id") == "120"
    rel_ele_list = xml_utils.get_children(seq_ele, "Relation")
    assert len(rel_ele_list) == 1
    rel_ele = rel_ele_list[0]
    assert rel_ele.get("type") == "SequencerFinalizeType"
    assert rel_ele.get("target") == "133"

    # Check properties
    assert seq_ele.get("CommandList") == "132 121"
    assert gen_start_cmd_ele.get("GeneratorList") == "114"
    assert gen_start_wait_cmd_ele.get("GeneratorList") == "113"
    assert ana_stop_cmd_ele.get("AnalyzerList") == "116"
    while_cmd_ele = seq_ele.find(".//SequencerWhileCommand")
    assert while_cmd_ele is not None
    assert while_cmd_ele.get("CommandList") == \
        "123 124 125 126 127 128 129 130 131"

    # Special case of a 0 handle (the invalid STC handle)
    # being propagated (won't load if it is an empty string)
    ctc_ele = seq_ele.find(
        ".//spirent.methodology.CreateTemplateConfigCommand")
    assert ctc_ele is not None
    assert ctc_ele.get("StmTemplateMix") == "0"


def get_sample_test_xml():
    return """
<Template>
<Diagram/>
<Description/>
<DataModelXml>
<StcSystem id="1"
 InSimulationMode="FALSE"
 UseSmbMessaging="FALSE"
 ApplicationName="TestCenter"
 Active="TRUE"
 LocalActive="TRUE"
 Name="StcSystem 1">
  <Project id="2"
   TableViewData=""
   TestMode="L2L3"
   SelectedTechnologyProfiles=""
   ConfigurationFileName="Untitled.tcc"
   Active="TRUE"
   LocalActive="TRUE"
   Name="Project 1">
    <Relation type="DefaultSelection" target="15"/>
    <Tags id="1203" serializationBase="true"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1407"/>
      <Relation type="UserTag" target="1409"/>
      <Relation type="UserTag" target="1411"/>
      <Relation type="UserTag" target="1412"/>
      <Relation type="DefaultTag" target="1204"/>
      <Relation type="DefaultTag" target="1205"/>
      <Relation type="DefaultTag" target="1206"/>
      <Relation type="DefaultTag" target="1207"/>
      <Relation type="DefaultTag" target="1208"/>
      <Relation type="DefaultTag" target="1209"/>
      <Tag id="1204" Name="Host"></Tag>
      <Tag id="1205" Name="Router"></Tag>
      <Tag id="1206" Name="Client"></Tag>
      <Tag id="1207" Name="Server"></Tag>
      <Tag id="1208" Name="Core"></Tag>
      <Tag id="1209" Name="Edge"></Tag>
      <Tag id="1407" Name="OuterVlan"></Tag>
      <Tag id="1409" Name="InnerVlan"></Tag>
      <Tag id="1411" Name="Dhcpv4"></Tag>
      <Tag id="1412" Name="TopLevelIf"></Tag>
    </Tags>
    <EmulatedDevice id="2202" serializationBase="true" Name="Device 1">
      <Relation type="UserTag" target="1206"/>
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Ipv4If id="2203" Name="IPv4 3">
        <Relation type="StackedOnEndpoint" target="1405"/>
        <Relation type="UserTag" target="1412"/>
        <StmPropertyModifier id="11"
        ModifierInfo=""
        Name="StmPropertyModifier1">
        </StmPropertyModifier>
      </Ipv4If>
      <EthIIIf id="2204" Name="EthernetII 3">
      </EthIIIf>
      <VlanIf id="1404"
       VlanId="1500" Name="VLAN 1">
        <Relation type="UserTag" target="1407"/>
        <Relation type="StackedOnEndpoint" target="2204"/>
        <StmPropertyModifier id="12"
        ModifierInfo=""
        Name="StmPropertyModifier2">
        </StmPropertyModifier>
      </VlanIf>
      <VlanIf id="1405"
       VlanId="2000" Name="VLAN 2">
        <Relation type="UserTag" target="1409"/>
        <Relation type="StackedOnEndpoint" target="1404"/>
        <StmPropertyModifier id="13"
        Name="StmPropertyModifier3">
        </StmPropertyModifier>
      </VlanIf>
      <Dhcpv4BlockConfig id="2205" Name="DHCP 1">
        <Relation type="UserTag" target="1411"/>
        <Relation type="UsesIf" target="2203"/>
        <StmPropertyModifier id="14"
        ModifierInfo=""
        Name="StmPropertyModifier4">
        </StmPropertyModifier>
      </Dhcpv4BlockConfig>
      <StmPropertyModifier id="15"
      ModifierInfo=""
      Name="StmPropertyModifier5">
      </StmPropertyModifier>
      <StmPropertyModifier id="15"
      ModifierInfo=""
      Name="StmPropertyModifier6">
      </StmPropertyModifier>
      <StmPropertyModifier id="16"
      ModifierInfo=""
      Name="StmPropertyModifier7">
      </StmPropertyModifier>
      <StmPropertyModifier id="17"
      ModifierInfo=""
      Name="StmPropertyModifier8">
      </StmPropertyModifier>
      <StmPropertyModifier id="18"
      ModifierInfo=""
      Name="StmPropertyModifier9">
      </StmPropertyModifier>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""


def get_sample_seq_xml():
    return """
<Template>
<Diagram/>
<Description/>
<DataModelXml>
<StcSystem id="1" serializationBase="true" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Tags id="1332" Name="Tags 1">
      <Relation type="UserTag" target="1631"/>
      <Relation type="UserTag" target="1639"/>
      <Relation type="UserTag" target="1644"/>
      <Relation type="UserTag" target="1649"/>
      <Relation type="UserTag" target="1654"/>
      <Relation type="UserTag" target="1661"/>
      <Relation type="UserTag" target="1666"/>
      <Relation type="UserTag" target="1671"/>
      <Tag id="1631" Name="stSmCreateTemplateConfig"></Tag>
      <Tag id="1639" Name="stWhileCommand"></Tag>
      <Tag id="1644" Name="stSmIteratorConfigPropertyValue"></Tag>
      <Tag id="1649" Name="stResultsClearAll"></Tag>
      <Tag id="1654" Name="stGeneratorStart"></Tag>
      <Tag id="1661" Name="stGeneratorStop"></Tag>
      <Tag id="1666" Name="stVerifyResultsValue"></Tag>
      <Tag id="1671" Name="stAnalyzerStop"></Tag>
    </Tags>
    <ExposedConfig id="1592" Name="ExposedConfig 1">
      <ExposedProperty id="1674"
       EPNameId="Wait1WaitTimeSecs"
       EPPropertyName="Wait Time (secs)"
       EPClassId="waitcommand"
       EPPropertyId="waitcommand.waittime"
       EPDefaultValue="30"
       EPLabel="Wait Time (secs)"
       Name="ExposedProperty 1">
        <Relation type="ScriptableExposedProperty" target="3333"/>
      </ExposedProperty>
    </ExposedConfig>
    <Port id="1900" Name="Port 1 //9/1">
      <Relation type="ActivePhy" target="2611"/>
      <Generator id="1909" Name="Traffic Generator 1">
        <GeneratorConfig id="1910" Name="Generator Configuration 1">
        </GeneratorConfig>
      </Generator>
      <Analyzer id="1911" Name="Traffic Analyzer 1">
        <AnalyzerConfig id="1912" Name="Advanced Settings 1">
        </AnalyzerConfig>
      </Analyzer>
      <EthernetCopper id="1943" Name="Ethernet Copper Phy 1">
      </EthernetCopper>
      <Ethernet10GigCopper id="2611">
      </Ethernet10GigCopper>
    </Port>
  </Project>
  <Sequencer id="11"
   CommandList="3339 3335"
   BreakpointList=""
   DisabledCommandList=""
   CleanupCommand="2957"
   Name="Sequencer 1">
    <Relation type="SequencerFinalizeType" target="2957"/>
    <SequencerWhileCommand id="3335"
     ExpressionCommand="3337"
     Condition="PASSED"
     CommandList="3338 3326 3327 3328 3333 3329 3330 3331 3332"
     ExecutionMode="BACKGROUND"
     GroupCategory="REGULAR_COMMAND"
     Name="While">
      <Relation type="UserTag" target="1639"/>
      <spirent.methodology.ObjectIteratorCommand id="3337"
       IterMode="STEP"
       StepVal="10"
       ValueType="RANGE"
       ValueList=""
       BreakOnFail="FALSE"
       MinVal="0"
       MaxVal="100"
       PrevIterVerdict="TRUE"
       CommandName=""
       PackageName="spirent"
       Name="Iterators: Object Iterator Command">
      </spirent.methodology.ObjectIteratorCommand>
      <spirent.methodology.IteratorConfigPropertyValueCommand id="3338"
       ClassName=""
       PropertyName=""
       ObjectList=""
       IgnoreEmptyTags="FALSE"
       TagList=""
       CurrVal=""
       Iteration="0"
       CommandName=""
       PackageName="spirent"
       Name="Configurators: Iterator Config Property Value Command 1">
        <Relation type="UserTag" target="1644"/>
      </spirent.methodology.IteratorConfigPropertyValueCommand>
      <ResultsClearAllCommand id="3326"
       Project="0"
       PortList="1900"
       Name="Clear All Results 1">
        <Relation type="UserTag" target="1649"/>
      </ResultsClearAllCommand>
      <GeneratorStartCommand id="3327"
       GeneratorList="1909"
       Name="Start Traffic 1">
        <Relation type="UserTag" target="1654"/>
      </GeneratorStartCommand>
      <GeneratorWaitForStartCommand id="3328"
       GeneratorList="1900"
       WaitTimeout="5400"
       Name="Wait For Traffic Start 1">
      </GeneratorWaitForStartCommand>
      <WaitCommand id="3333"
       WaitTime="30"
       Name="Wait 1">
      </WaitCommand>
      <GeneratorStopCommand id="3329"
       GeneratorList="1909"
       Name="Stop Traffic 1">
      </GeneratorStopCommand>
      <GeneratorWaitForStopCommand id="3330"
       GeneratorList="2"
       WaitTimeout="604800"
       Name="Wait For Traffic Stop 1">
        <Relation type="UserTag" target="1661"/>
      </GeneratorWaitForStopCommand>
      <VerifyResultsValueCommand id="3331"
       WaitTimeout="0"
       InvertComparison="FALSE"
       Name="Verify Result Value 1">
        <Relation type="UserTag" target="1666"/>
      </VerifyResultsValueCommand>
      <AnalyzerStopCommand id="3332"
       AnalyzerList="1911"
       Name="Stop Analyzer 1">
        <Relation type="UserTag" target="1671"/>
      </AnalyzerStopCommand>
    </SequencerWhileCommand>
    <spirent.methodology.CreateTemplateConfigCommand id="3339"
     AutoExpandTemplate="TRUE"
     StmTemplateMix="0"
     InputJson="{&quot;baseTemplateFile&quot;: &quot;IPv4_NoVlan.xml&quot;}"
     CopiesPerParent="1"
     SrcTagList=""
     TargetTagList=""
     CommandName=""
     PackageName="spirent"
     Name="Create Template Config Command 12">
      <Relation type="UserTag" target="1631"/>
    </spirent.methodology.CreateTemplateConfigCommand>
  </Sequencer>
  <SequencerGroupCommand id="2957" Name="Cleanup Commands">
  </SequencerGroupCommand>
</StcSystem>
</DataModelXml>
</Template>
"""
