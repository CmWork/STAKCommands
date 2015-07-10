from StcIntPythonPL import *
from mock import MagicMock
# from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import spirent.methodology.utils.xml_config_utils as xml_utils


def disabled_maybe_delete_test_validate(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()

    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    LoadTemplateCommand.get_this_cmd = MagicMock(return_value=cmd)

    res = LoadTemplateCommand.validate(1, [], test_xml, "", "", True, False)
    assert res == ""

    # Test a situation where AutoExpandTemplate is true and
    # there is an ExpandTemplateCommand in the group

    exp_cmd = ctor.Create(pkg + ".ExpandTemplateCommand", cmd)
    cmd.SetCollection("CommandList", [exp_cmd.GetObjectHandle()])

    res = LoadTemplateCommand.validate(1, [], test_xml, "", "", True, False)
    assert res == ""


def test_renormalize_xml_obj_ids(stc):
    root = etree.fromstring(get_test_xml())
    xml_utils.renormalize_xml_obj_ids(root)
    vlan_ele_list = root.findall(".//VlanIf")
    assert len(vlan_ele_list) == 2

    # VlanIf IDs should be 13 and 14
    obj_id_list = []
    for vlan_ele in vlan_ele_list:
        obj_id_list.append(vlan_ele.get("id"))
    assert len(obj_id_list) == 2
    assert "13" in obj_id_list
    assert "14" in obj_id_list

    # Ipv4If should be 11
    ipv4if_ele = root.find(".//Ipv4If")
    assert ipv4if_ele is not None
    assert ipv4if_ele.get("id") == "11"

    stacked_on_rel = None
    user_tag_rel = None
    for child in ipv4if_ele:
        if child.tag != "Relation":
            continue
        if child.get("type") == "StackedOnEndpoint":
            stacked_on_rel = child
        elif child.get("type") == "UserTag":
            user_tag_rel = child
    assert stacked_on_rel is not None
    assert user_tag_rel is not None

    # Should be stacked on 14 (one of the VlanIfs)
    assert stacked_on_rel.get("target") == "14"

    # Should be tagged with 8 (TopLevelIf tag)
    assert user_tag_rel.get("target") == "8"

    # Check the tag
    tag_ele_list = root.findall(".//Tag")
    assert len(tag_ele_list) == 5
    top_level_if_tag = None
    for tag_ele in tag_ele_list:
        if tag_ele.get("Name") == "TopLevelIf":
            top_level_if_tag = tag_ele
            break
    assert top_level_if_tag is not None
    assert top_level_if_tag.get("id") == "8"


def test_merge_run(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()
    merge_xml = get_test_merge_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    # Create a template object
    temp_conf = ctor.Create("StmTemplateConfig", project)
    temp_conf.Set("TemplateXml", test_xml)

    # Test when TemplateXml String is not defined
    cmd = ctor.CreateCommand(pkg + ".MergeTemplateCommand")
    cmd.Set("StmTemplateConfig", temp_conf.GetObjectHandle())
    cmd.Set("TemplateXml", "")
    cmd.Set("EnableLoadFromFileName", False)
    cmd.SetCollection("SrcTagList", ["Bgp"])
    cmd.SetCollection("TargetTagList", ["DHCP Client"])
    cmd.Set("TagPrefix", "New_")
    cmd.Execute()
    assert cmd.Get("PassFailState") == "FAILED"
    cmd.MarkDelete()

    root = etree.fromstring(temp_conf.Get("TemplateXml"))
    assert root != ""

    cmd = ctor.CreateCommand(pkg + ".MergeTemplateCommand")
    cmd.Set("StmTemplateConfig", temp_conf.GetObjectHandle())
    cmd.Set("TemplateXml", merge_xml)
    cmd.Set("EnableLoadFromFileName", False)
    cmd.SetCollection("SrcTagList", ["Bgp"])
    cmd.SetCollection("TargetTagList", ["DHCP Client"])
    cmd.Set("TagPrefix", "New_")
    cmd.Execute()
    cmd.MarkDelete()

    root = etree.fromstring(temp_conf.Get("TemplateXml"))
    assert root is not None

    # Check Tags
    tags = root.find(".//Tags")
    assert tags is not None
    tag_list = tags.findall(".//Tag")
    assert len(tag_list) == 9
    found_dhcp = False
    found_bgp = False
    found_inner_vlan = False
    found_netblock = False
    found_netblock_prop = False
    found_bgp_dev_tag = False
    for tag_ele in tag_list:
        assert tag_ele.tag == "Tag"
        if tag_ele.get("Name") == "Dhcpv4":
            assert tag_ele.get("id") == "7"
            found_dhcp = True
        elif tag_ele.get("Name") == "InnerVlan":
            assert tag_ele.get("id") == "6"
            found_inner_vlan = True
        elif tag_ele.get("Name") == "New_Bgp":
            assert tag_ele.get("id") == "16"
            found_bgp = True
        elif tag_ele.get("Name") == "New_Ipv4NetworkBlock":
            assert tag_ele.get("id") == "18"
            found_netblock = True
        elif (tag_ele.get("Name") ==
              "New_Ipv4NetworkBlock.StartIpList"):
            assert tag_ele.get("id") == "19"
            found_netblock_prop = True
        elif (tag_ele.get("Name") ==
              "BGP Router"):
            found_bgp_dev_tag = True

    assert found_dhcp
    assert found_bgp
    assert found_inner_vlan
    assert found_netblock
    assert found_netblock_prop
    assert not found_bgp_dev_tag

    # Check the UserTag relation
    exp_target_list = ["4", "5", "6", "7", "8", "16", "17", "18", "19"]
    act_target_list = []
    for ele in tags:
        if ele.tag == "Relation" and \
           ele.get("type") == "UserTag":
            act_target_list.append(ele.get("target"))
    assert len(act_target_list) == 9
    assert set(exp_target_list) == set(act_target_list)

    # Check the BgpRouterConfig
    bgp_proto_list = root.findall(".//BgpRouterConfig")
    assert len(bgp_proto_list) == 1
    bgp_proto = bgp_proto_list[0]
    assert bgp_proto is not None
    assert bgp_proto.get("id") == "20"
    parent = xml_utils.get_parent(root, bgp_proto)
    assert parent is not None
    assert parent.tag == "EmulatedDevice"
    assert parent.get("id") == "9"
    rel_list = xml_utils.get_children(bgp_proto, "Relation")

    # Note that the BgpRouterConfig's UsesIf relation is removed
    # as it points to a NetworkInterface that does not exist
    # once the BgpRouterConfig is merged into the target template
    assert len(rel_list) == 1
    for rel in rel_list:
        if rel.get("type") == "UserTag":
            assert rel.get("target") == "16"
    route_conf = xml_utils.get_child(bgp_proto, "BgpIpv4RouteConfig")
    assert route_conf is not None
    rel_list = xml_utils.get_children(route_conf, "Relation")
    assert len(rel_list) == 1
    assert rel_list[0].get("type") == "UserTag"
    assert rel_list[0].get("target") == "17"

    net_block = xml_utils.get_child(route_conf, "Ipv4NetworkBlock")
    assert net_block is not None
    rel_list = xml_utils.get_children(net_block, "Relation")
    assert len(rel_list) == 1
    assert rel_list[0].get("type") == "UserTag"
    assert rel_list[0].get("target") == "18"

    prop_mod = xml_utils.get_child(net_block, "StmPropertyModifier")
    assert prop_mod is not None
    assert prop_mod.get("TagName") == "New_Ipv4NetworkBlock"

    assert prop_mod.get("id") == "23"
    rel_list = xml_utils.get_children(prop_mod, "Relation")
    assert len(rel_list) == 1
    assert rel_list[0].get("type") == "UserTag"
    assert rel_list[0].get("target") == "19"


def get_test_merge_xml():
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
      <Relation type="UserTag" target="1507"/>
      <Relation type="UserTag" target="1508"/>
      <Tag id="1206"
       Active="TRUE"
       LocalActive="TRUE"
       Name="BGP Router">
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
       Name="Bgp">
      </Tag>
      <Tag id="1507"
       Active="TRUE"
       LocalActive="TRUE"
       Name="BgpRouteConfig">
      </Tag>
      <Tag id="1508"
       Active="TRUE"
       LocalActive="TRUE"
       Name="Ipv4NetworkBlock">
      </Tag>
      <Tag id="1509"
       Active="TRUE"
       LocalActive="TRUE"
       Name="Ipv4NetworkBlock.StartIpList">
      </Tag>
      <Tag id="1412"
       Active="TRUE"
       LocalActive="TRUE"
       Name="TopLevelIf">
      </Tag>
    </Tags>
    <EmulatedDevice id="2202" serializationBase="true"
     DeviceCount="1"
     Name="Device 1">
      <StmPropertyModifier id="51110" TagName="ttEmulatedDevice2"
      ModifierInfo="&lt;Modifier ModifierType=&quot;RANGE&quot;
      PropertyName=&quot;RouterId&quot;
      ObjectName=&quot;EmulatedDevice&quot;&gt; &lt;Start&gt;2.2.2.2&lt;/Start&gt;
      &lt;Step&gt;0.0.0.1&lt;/Step&gt; &lt;Repeat&gt;0&lt;/Repeat&gt;
      &lt;Recycle&gt;0&lt;/Recycle&gt; &lt;Relation type=&quot;UserTag&quot;
      target=&quot;3500&quot;/&gt; &lt;/Modifier&gt;"/>
      <Relation type="UserTag" target="1206"/>
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Ipv4If id="2203"
       Address="192.85.1.3"
       Name="IPv4 3">
        <Relation type="StackedOnEndpoint" target="1405"/>
        <Relation type="UserTag" target="1412"/>
      </Ipv4If>
      <EthIIIf id="2204"
       SourceMac="00:10:94:00:00:01"
       Name="EthernetII 3">
      </EthIIIf>
      <VlanIf id="1404"
       VlanId="1515"
       IdStep="1"
       Name="VLAN 1">
        <Relation type="UserTag" target="1407"/>
        <Relation type="StackedOnEndpoint" target="2204"/>
      </VlanIf>
      <VlanIf id="1405"
       VlanId="2222"
       IdStep="1"
       Name="VLAN 2">
        <Relation type="UserTag" target="1409"/>
        <Relation type="StackedOnEndpoint" target="1404"/>
      </VlanIf>
      <BgpRouterConfig id="22205"
       Active="TRUE"
       LocalActive="TRUE"
       Name="BGP 1">
        <BgpIpv4RouteConfig Active="TRUE" NextHop="192.85.5.1" id="2909">
          <Relation target="1507" type="UserTag" />
          <Ipv4NetworkBlock Active="TRUE" NetworkCount="2000000"
             StartIpList="131.0.0.0" id="3090">
            <Relation target="1508" type="UserTag" />
            <StmPropertyModifier ModifierInfo="&lt;Modifier
               ModifierType=&quot;RANGE&quot;
               PropertyName=&quot;StartIpList&quot;
               ObjectName=&quot;Ipv4NetworkBlock&quot;&gt;
               &lt;Start&gt;131.0.0.0&lt;/Start&gt;
               &lt;Step&gt;0.1.0.0&lt;/Step&gt;
               &lt;Repeat&gt;0&lt;/Repeat&gt;
               &lt;Recycle&gt;0&lt;/Recycle&gt;&lt;/Modifier&gt;"
               TagName="Ipv4NetworkBlock" id="1116">
              <Relation target="1509" type="UserTag" />
            </StmPropertyModifier>
          </Ipv4NetworkBlock>
          <BgpVpnRouteConfig Active="TRUE" VrfCount="1" id="3091">
          </BgpVpnRouteConfig>
        </BgpIpv4RouteConfig>
        <Relation type="UserTag" target="1411"/>
        <Relation type="UsesIf" target="2203"/>
      </BgpRouterConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""


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
      <StmPropertyModifier id="51110" TagName="ttEmulatedDevice2"
      ModifierInfo="&lt;Modifier ModifierType=&quot;RANGE&quot;
      PropertyName=&quot;RouterId&quot;
      ObjectName=&quot;EmulatedDevice&quot;&gt; &lt;Start&gt;2.2.2.2&lt;/Start&gt;
      &lt;Step&gt;0.0.0.1&lt;/Step&gt; &lt;Repeat&gt;0&lt;/Repeat&gt;
      &lt;Recycle&gt;0&lt;/Recycle&gt; &lt;Relation type=&quot;UserTag&quot;
      target=&quot;3500&quot;/&gt; &lt;/Modifier&gt;"/>
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
