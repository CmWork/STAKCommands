from StcIntPythonPL import *
import xml.etree.ElementTree as etree


def test_run(stc):
    # Test XML
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    pkg = "spirent.methodology"

    template = ctor.Create("StmTemplateConfig", project)
    assert template is not None
    template.Set("TemplateXml", test_xml)

    # Check the XML (basic checks)
    root = etree.fromstring(test_xml)
    vlan_ele_list = root.findall(".//VlanIf")
    assert len(vlan_ele_list) == 2

    found_1500 = False
    found_2000 = False
    for vlan_ele in vlan_ele_list:
        if vlan_ele.get("VlanId") == "1500":
            found_1500 = True
        elif vlan_ele.get("VlanId") == "2000":
            found_2000 = True
    assert found_1500
    assert found_2000

    # Add an additional object
    prop_list = ["VlanId", "IdStep"]
    val_list = ["333", "563"]
    cmd = ctor.CreateCommand(pkg + ".AddTemplateObjectCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.Set("ParentTagName", "DHCP Client")
    cmd.Set("TagName", "ThirdStackedVlan")
    cmd.Set("ClassName", "VlanIf")
    cmd.SetCollection("PropertyList", prop_list)
    cmd.SetCollection("ValueList", val_list)
    cmd.Execute()
    cmd.MarkDelete()

    # Test the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    vlan_ele_list = root.findall(".//VlanIf")
    assert len(vlan_ele_list) == 3

    found_1500 = False
    found_2000 = False
    third_ele = None
    for vlan_ele in vlan_ele_list:
        if vlan_ele.get("VlanId") == "1500":
            found_1500 = True
        elif vlan_ele.get("VlanId") == "2000":
            found_2000 = True
        else:
            third_ele = vlan_ele
    assert found_1500
    assert found_2000
    assert third_ele.get("VlanId") == "333"
    assert third_ele.get("IdStep") == "563"

    # Check the Tags
    tags_ele = root.find(".//Tags")
    assert tags_ele is not None
    found_vlan_tag = False
    for child in tags_ele:
        if child.tag == "Tag":
            if child.get("Name") == "ThirdStackedVlan":
                found_vlan_tag = True
                tag_id = child.get("id")
    assert found_vlan_tag is True

    # Check the Tag
    third_ele_child_list = list(third_ele)
    assert len(third_ele_child_list) == 1
    rel_ele = third_ele_child_list[0]
    assert rel_ele.tag == "Relation"
    assert rel_ele.get("type") == "UserTag"
    assert rel_ele.get("target") == tag_id
    assert tag_id == "2206"

    # Add object with ugly property value list
    prop_list = ["TagName", "ModifierInfo"]
    val_list = ["Normal Tag Name With Spaces",
                "Equals=Equals with Space = Equals"]
    cmd = ctor.CreateCommand(pkg + ".AddTemplateObjectCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.Set("ParentTagName", "DHCP Client")
    cmd.Set("TagName", "UglyPropValList")
    cmd.Set("ClassName", "StmPropertyModifier")
    cmd.SetCollection("PropertyList", prop_list)
    cmd.SetCollection("ValueList", val_list)
    cmd.Execute()
    cmd.MarkDelete()


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
