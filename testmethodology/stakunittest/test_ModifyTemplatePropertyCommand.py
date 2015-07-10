from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import spirent.methodology.utils.xml_config_utils as xml_utils
PKG = "spirent.methodology"


# Returns back the inner and outer VLAN elements specified
# by the XML at the bottom of this file.
def get_vlan_elements(root):
    inner_vlan_tag_name = "InnerVlan"
    outer_vlan_tag_name = "OuterVlan"
    outer_vlan_tag_id = None
    inner_vlan_tag_id = None

    tag_ele_list = root.findall(".//Tag")
    for tag in tag_ele_list:
        if tag.get("Name") == outer_vlan_tag_name:
            outer_vlan_tag_id = tag.get("id")
        elif tag.get("Name") == inner_vlan_tag_name:
            inner_vlan_tag_id = tag.get("id")

    vlan_ele_list = root.findall(".//VlanIf")
    outer_vlan_ele = None
    inner_vlan_ele = None
    for vlan_ele in vlan_ele_list:
        assert vlan_ele is not None
        for child_ele in vlan_ele:
            if child_ele.tag == "Relation":
                if child_ele.get("type") == "UserTag":
                    if child_ele.get("target") == outer_vlan_tag_id:
                        outer_vlan_ele = vlan_ele
                    elif child_ele.get("target") == inner_vlan_tag_id:
                        inner_vlan_ele = vlan_ele
    return outer_vlan_ele, inner_vlan_ele


def test_run_single_tag(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert inner_vlan_ele.get("VlanId") == "2000"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "192.85.1.3"

    # Modify the OuterVlan
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["VlanIf.VlanId"])
    cmd.SetCollection("ValueList", ["999"])
    cmd.SetCollection("TagNameList", ["OuterVlan"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert inner_vlan_ele.get("VlanId") == "2000"

    # Modify the InnerVlan
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["VlanIf.VlanId",
                                       "VlanIf.IdStep",
                                       "VlanIf.Priority"])
    cmd.SetCollection("ValueList", ["123", "321", "5"])
    cmd.SetCollection("TagNameList", ["InnerVlan"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert outer_vlan_ele.get("IdStep") == "1"
    assert outer_vlan_ele.get("Priority") == "7"
    assert inner_vlan_ele.get("VlanId") == "123"
    assert inner_vlan_ele.get("IdStep") == "321"
    assert inner_vlan_ele.get("Priority") == "5"

    failed = False
    fail_message = ""
    # Modify a property on an untagged object (should fail)
    with AutoCommand(PKG + '.ModifyTemplatePropertyCommand') as cmd:
        try:
            cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            cmd.SetCollection("PropertyList", ["VlanIf.VlanId",
                                               "Ipv4If.Address"])
            cmd.SetCollection("ValueList", ["1501", "65.65.65.1"])
            cmd.SetCollection("TagNameList", ["InnerVlan"])
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Did not find object Ipv4If in list of tagged objects' in fail_message:
                failed = True
    if not failed:
        raise AssertionError('ModifyTemplatePropertyCommand failed with ' +
                             'unexpected error: "' + fail_message + '"')

    failed = False
    fail_message = ""
    # Modify a property using invalid tag list (objects don't match) - should fail
    with AutoCommand(PKG + '.ModifyTemplatePropertyCommand') as cmd:
        try:
            cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            cmd.SetCollection("PropertyList", ["VlanIf.VlanId"])
            cmd.SetCollection("ValueList", ["1502"])
            cmd.SetCollection("TagNameList", ["TopLevelIf"])
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Did not find object VlanIf in list of tagged objects' in fail_message:
                failed = True
    if not failed:
        raise AssertionError('ModifyTemplatePropertyCommand failed with ' +
                             'unexpected error: "' + fail_message + '"')


def test_run_multiple_tags(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert inner_vlan_ele.get("VlanId") == "2000"

    # Modify both vlans
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["VlanIf.VlanId"])
    cmd.SetCollection("ValueList", ["999"])
    cmd.SetCollection("TagNameList", ["OuterVlan", "InnerVlan"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert inner_vlan_ele.get("VlanId") == "999"


def test_run_invalid_prop_val_list(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert inner_vlan_ele.get("VlanId") == "2000"

    # Modify both vlans
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["VlanIf.VlanId"])
    cmd.SetCollection("ValueList", ["abc"])
    cmd.SetCollection("TagNameList", ["OuterVlan", "InnerVlan"])
    cmd.Execute()
    assert cmd.Get("PassFailState") == "FAILED"
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert inner_vlan_ele.get("VlanId") == "2000"


def test_run_multiple_tags_multiple_properties(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert outer_vlan_ele.get("Priority") == "7"
    assert inner_vlan_ele.get("VlanId") == "2000"
    assert inner_vlan_ele.get("Priority") == "7"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "192.85.1.3"

    prop_val_list = [("VlanIf.VlanId", "999"),
                     ("VlanIf.Priority", "1"),
                     ("Ipv4If.Address", "57.57.57.57")]

    # Modify both vlans
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
    cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
    cmd.SetCollection("TagNameList", ["OuterVlan", "InnerVlan",
                                      "TopLevelIf"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert outer_vlan_ele.get("Priority") == "1"
    assert inner_vlan_ele.get("VlanId") == "999"
    assert inner_vlan_ele.get("Priority") == "1"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "57.57.57.57"

    prop_val_list = [("VlanIf.VlanId", "333"),
                     ("Ipv4If.Address", "11.11.11.11"),
                     ("VlanIf.Priority", "3")]

    # Use only the InnerVlan tag and verify the outer vlan values are not modified
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
    cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
    cmd.SetCollection("TagNameList", ["InnerVlan", "TopLevelIf"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert outer_vlan_ele.get("Priority") == "1"
    assert inner_vlan_ele.get("VlanId") == "333"
    assert inner_vlan_ele.get("Priority") == "3"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "11.11.11.11"


def test_run_no_tag_specified(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert inner_vlan_ele.get("VlanId") == "2000"

    # Call ModifyTemplatePropertyCommand but don't specify the Tag
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["VlanIf.VlanId"])
    cmd.SetCollection("ValueList", ["999"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    # All VlanIfs should have been modified
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "999"
    assert inner_vlan_ele.get("VlanId") == "999"

    # Call ModifyTemplatePropertyCommand on an element
    # that isn't tagged at all (in the XML)
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", ["EthIIIf.SourceMac"])
    cmd.SetCollection("ValueList", ["00:00:00:00:00:01"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    # All EthIIIfs should have been modified
    root = etree.fromstring(template.Get("TemplateXml"))
    ethiiif_list = root.findall(".//EthIIIf")
    assert len(ethiiif_list) == 1
    assert ethiiif_list[0].get("SourceMac") == "00:00:00:00:00:01"


def test_run_invalid_tags_multiple_properties(stc):
    # Test XML
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"
    template = ctor.Create("StmTemplateConfig", project)
    template.Set("TemplateXml", test_xml)

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "1500"
    assert outer_vlan_ele.get("Priority") == "7"
    assert inner_vlan_ele.get("VlanId") == "2000"
    assert inner_vlan_ele.get("Priority") == "7"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "192.85.1.3"

    prop_val_list = [("VlanIf.VlanId", "555"),
                     ("Ipv4If.Address", "32.32.32.32"),
                     ("VlanIf.Priority", "4")]

    # In TagNameList have a duplicate tag and two invalid tags
    cmd = ctor.CreateCommand(pkg + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
    cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
    cmd.SetCollection("TagNameList", ["OuterVlan", "InnerVlan",
                                      "TopLevelIf", "OuterVlan", "asdf", ""])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    outer_vlan_ele, inner_vlan_ele = get_vlan_elements(root)
    ipv4_ele = xml_utils.get_element(root, "Ipv4If")
    assert outer_vlan_ele is not None
    assert inner_vlan_ele is not None
    assert outer_vlan_ele.get("VlanId") == "555"
    assert outer_vlan_ele.get("Priority") == "4"
    assert inner_vlan_ele.get("VlanId") == "555"
    assert inner_vlan_ele.get("Priority") == "4"
    assert ipv4_ele is not None
    assert ipv4_ele.get("Address") == "32.32.32.32"

    prop_val_list = [("VlanIf.VlanId", "888"),
                     ("Ipv4If.Address", "45.45.45.45"),
                     ("VlanIf.Priority", "2")]

    failed = False
    fail_message = ""
    # Set TagNameList to an empty string
    with AutoCommand(PKG + '.ModifyTemplatePropertyCommand') as cmd:
        try:
            cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
            cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
            cmd.SetCollection("TagNameList", [""])
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Did not find object VlanIf in list of tagged objects' in fail_message:
                failed = True
    if not failed:
        raise AssertionError('ModifyTemplatePropertyCommand failed with ' +
                             'unexpected error: "' + fail_message + '"')

    prop_val_list = [("Ipv4If.Address", "45.45.45.45"),
                     ("VlanIf.VlanId", "888"),
                     ("VlanIf.Priority", "2")]

    failed = False
    fail_message = ""
    # Set TagNameList to an invalid string
    with AutoCommand(PKG + '.ModifyTemplatePropertyCommand') as cmd:
        try:
            cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
            cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
            cmd.SetCollection("TagNameList", ["blah"])
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Did not find object Ipv4If in list of tagged objects' in fail_message:
                failed = True
    if not failed:
        raise AssertionError('ModifyTemplatePropertyCommand failed with ' +
                             'unexpected error: "' + fail_message + '"')

    prop_val_list = [("Ipv4If.Address", "45.45.45.45"),
                     ("VlanIf.VlanId", "888"),
                     ("VlanIf.Priority", "2")]

    failed = False
    fail_message = ""
    # Set TagNameList to a valid tag but doesn't correspond to any of the objects to modify
    with AutoCommand(PKG + '.ModifyTemplatePropertyCommand') as cmd:
        try:
            cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            cmd.SetCollection("PropertyList", [pv[0] for pv in prop_val_list])
            cmd.SetCollection("ValueList", [pv[1] for pv in prop_val_list])
            cmd.SetCollection("TagNameList", ["Dhcpv4"])
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Did not find object Ipv4If in list of tagged objects' in fail_message:
                failed = True
    if not failed:
        raise AssertionError('ModifyTemplatePropertyCommand failed with ' +
                             'unexpected error: "' + fail_message + '"')


# FIXME:
# Do something about this:
def get_test_xml():
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
      <Relation type="UserTag" target="2409"/>
      <Relation type="UserTag" target="1411"/>
      <Relation type="UserTag" target="1412"/>
      <Relation type="UserTag" target="1206"/>
      <Tag id="1206"
       Active="TRUE"
       LocalActive="TRUE"
       Name="DHCP Client">
      </Tag>
      <Tag id="1407"
       Active="TRUE"
       LocalActive="TRUE"
       Name="OuterVlan">
      </Tag>
      <Tag id="1409"
       Active="TRUE"
       LocalActive="TRUE"
       Name="InnerVlan">
      </Tag>
      <Tag id="2409"
       Active="TRUE"
       LocalActive="TRUE"
       Name="InnerVlan2409">
      </Tag>
      <Tag id="1411"
       Active="TRUE"
       LocalActive="TRUE"
       Name="Dhcpv4">
      </Tag>
      <Tag id="1412"
       Active="TRUE"
       LocalActive="TRUE"
       Name="TopLevelIf">
      </Tag>
    </Tags>
    <EmulatedDevice id="2202" serializationBase="true"
     DeviceCount="1"
     EnablePingResponse="FALSE"
     RouterId="192.0.0.1"
     RouterIdStep="0.0.0.1"
     Ipv6RouterId="2000::1"
     Ipv6RouterIdStep="::1"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Device 1">
      <Relation type="UserTag" target="1206"/>
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Ipv4If id="2203"
       Address="192.85.1.3"
       AddrStep="0.0.0.1"
       AddrStepMask="255.255.255.255"
       SkipReserved="TRUE"
       AddrList=""
       AddrRepeatCount="0"
       AddrResolver="Dhcpv4"
       PrefixLength="24"
       UsePortDefaultIpv4Gateway="FALSE"
       Gateway="192.85.1.1"
       GatewayStep="0.0.0.0"
       GatewayRepeatCount="0"
       GatewayRecycleCount="0"
       UseIpAddrRangeSettingsForGateway="FALSE"
       GatewayList=""
       ResolveGatewayMac="TRUE"
       GatewayMac="00:00:01:00:00:01"
       GatewayMacResolver="default"
       Ttl="255"
       TosType="TOS"
       Tos="192"
       NeedsAuthentication="FALSE"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="IPv4 3">
        <Relation type="StackedOnEndpoint" target="1405"/>
        <Relation type="UserTag" target="1412"/>
      </Ipv4If>
      <EthIIIf id="2204"
       SourceMac="00:10:94:00:00:01"
       SrcMacStep="00:00:00:00:00:01"
       SrcMacList=""
       SrcMacStepMask="00:00:ff:ff:ff:ff"
       SrcMacRepeatCount="0"
       Authenticator="default"
       UseDefaultPhyMac="FALSE"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="EthernetII 3">
      </EthIIIf>
      <VlanIf id="1404"
       VlanId="1500"
       IdStep="1"
       IdList=""
       IdRepeatCount="0"
       IdResolver="default"
       Priority="7"
       Cfi="0"
       Tpid="33024"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="VLAN 1">
        <Relation type="UserTag" target="1407"/>
        <Relation type="StackedOnEndpoint" target="2204"/>
      </VlanIf>
      <VlanIf id="1405"
       VlanId="2000"
       IdStep="1"
       IdList=""
       IdRepeatCount="0"
       IdResolver="default"
       Priority="7"
       Cfi="0"
       Tpid="33024"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="VLAN 2">
        <Relation type="UserTag" target="1409"/>
        <Relation type="UserTag" target="2409"/>
        <Relation type="StackedOnEndpoint" target="1404"/>
      </VlanIf>
      <Dhcpv4BlockConfig id="2205"
       HostName="client_@p-@b-@s"
       DefaultHostAddrPrefixLength="24"
       OptionList="1 6 15 33 44"
       EnableRouterOption="FALSE"
       EnableArpServerId="FALSE"
       UseBroadcastFlag="TRUE"
       EnableRelayAgent="FALSE"
       ClientRelayAgent="FALSE"
       RelayAgentIpv4AddrMask="255.255.0.0"
       RelayAgentIpv4Addr="0.0.0.0"
       RelayAgentIpv4AddrStep="0.0.0.1"
       RelayServerIpv4Addr="0.0.0.0"
       RelayServerIpv4AddrStep="0.0.0.1"
       RelayPoolIpv4Addr="0.0.0.0"
       RelayPoolIpv4AddrStep="0.0.1.0"
       EnableCircuitId="FALSE"
       CircuitId="circuitId_@p"
       EnableRemoteId="FALSE"
       RemoteId="remoteId_@p-@b-@s"
       RelayClientMacAddrStart="00:10:01:00:00:01"
       RelayClientMacAddrStep="00:00:00:00:00:01"
       RelayClientMacAddrMask="00:00:00:ff:ff:ff"
       EnableAutoRetry="FALSE"
       RetryAttempts="4"
       ExportAddrToLinkedClients="FALSE"
       UseClientMacAddrForDataplane="FALSE"
       UsePartialBlockState="FALSE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="DHCP 1">
        <Relation type="UserTag" target="1411"/>
        <Relation type="UsesIf" target="2203"/>
      </Dhcpv4BlockConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""
