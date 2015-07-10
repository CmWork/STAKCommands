from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
import json
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology', 'manager'))
import MethodologyGroupCommand as MethGrp


PKG = "spirent.methodology.manager"


def test_split_key_value_pair(stc):
    ctor = CScriptableCreator()

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    MethGrp.get_this_cmd = MagicMock(return_value=cmd)

    k, v = MethGrp.split_key_value_pair("Any.sort:of.key=value")
    assert k == 'Any.sort:of.key'
    assert v == 'value'

    k, v = MethGrp.split_key_value_pair("Any.sort:of.key=value=morevalue")
    assert k == 'Any.sort:of.key'
    assert v == 'value=morevalue'
    return


def test_load_xmlroot_from_file(stc):
    ctor = CScriptableCreator()

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    MethGrp.get_this_cmd = MagicMock(return_value=cmd)

    filename = "test_MethodologyGroupCommand_2.xml"
    try:
        with open(filename, "w") as f:
            f.write('<root id="3"/>')

        root = MethGrp.load_xmlroot_from_file("test_MethodologyGroupCommand_2.xml")

        assert root is not None
        assert len(root.findall('.//')) == 0
        assert root.Get('id') == '3'
        assert root.Get('name') == 'root'
    finally:
        os.remove(filename)
        return


def test_prop_modify(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd_name = "spirent.methodology.LoadTemplateCommand"

    # Build Sequence
    load_cmd = ctor.Create(cmd_name, sequencer)
    load_cmd.Set('TemplateXml', get_test_xml())
    load_cmd.Set('EnableLoadFromFilename', False)

    # Expose properties (loaded at some other step)
    exposed_config = ctor.Create("ExposedConfig", project)

    # Changing a property of the object itself...
    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(load_cmd, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", cmd_name)
    xp.Set("EPNameId", "spirent.methodology.LoadTemplateCommand.TagPrefix.0")
    xp.Set("EPPropertyId", "spirent.methodology.LoadTemplateCommand.TagPrefix")
    xp.Set("EPClassId", "spirent.methodology.loadtemplatecommand")

    json_dict = {}
    json_dict["spirent.methodology.LoadTemplateCommand.TagPrefix.0"] = "MyTagPrefix"

    KeyValuePairs = json.dumps(json_dict)

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    cmd.Set("KeyValueJson", KeyValuePairs)
    cmd.Execute()
    assert load_cmd.Get('TagPrefix') == 'MyTagPrefix'
    return


def test_prop_list_modify_collection(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd_name = "spirent.methodology.ObjectIteratorCommand"

    # Build Sequence
    iter_cmd = ctor.Create(cmd_name, sequencer)
    iter_cmd.SetCollection("ValueList", ["1", "2", "3"])

    # Expose properties (loaded at some other step)
    exposed_config = ctor.Create("ExposedConfig", project)

    # Changing a property of the object itself...
    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(iter_cmd, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", cmd_name)
    xp.Set("EPNameId", "Some_Unique_String_Name")
    xp.Set("EPPropertyId", cmd_name + ".ValueList")
    xp.Set("EPClassId", cmd_name.lower())

    json_dict = {}
    json_dict["Some_Unique_String_Name"] = ["4", "5", "6"]

    KeyValuePairs = json.dumps(json_dict)

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    cmd.Set("KeyValueJson", KeyValuePairs)
    cmd.Execute()

    # Internally, this is a list of strings
    assert iter_cmd.GetCollection("ValueList") == ["4", "5", "6"]
    return


def test_miss_prop_modify(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd_name = "spirent.methodology.LoadTemplateCommand"

    # Build Sequence
    load_cmd = ctor.Create(cmd_name, sequencer)
    load_cmd.Set('TemplateXml', get_test_xml())
    load_cmd.Set('EnableLoadFromFilename', False)

    # Expose properties (loaded at some other step)
    exposed_config = ctor.Create("ExposedConfig", project)

    # Changing a property of the object itself...
    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(load_cmd, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", cmd_name)
    xp.Set("EPNameId", "spirent.methodology.LoadTemplateCommand.TagPrefix.0")
    xp.Set("EPPropertyId", "spirent.methodology.LoadTemplateCommand.TagPrefix")
    xp.Set("EPClassId", "spirent.methodology.loadtemplatecommand")

    json_dict = {}
    json_dict["spirent.methodology.LoadTemplateCommand.Tagit.0"] = "MyTagPrefix"

    KeyValuePairs = json.dumps(json_dict)

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    cmd.Set("KeyValueJson", KeyValuePairs)
    cmd.Execute()
    assert load_cmd.Get('TagPrefix') == ""
    return


def test_many_modify(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd_name = "spirent.methodology.LoadTemplateCommand"

    # Build Sequence
    load_cmd = ctor.Create(cmd_name, sequencer)
    load_cmd.Set('TemplateXml', get_test_xml())
    load_cmd.Set('EnableLoadFromFilename', False)

    # Expose properties (loaded at some other step)
    exposed_config = ctor.Create("ExposedConfig", project)

    # Changing a property of the object itself...
    xp = ctor.Create("ExposedProperty", exposed_config)
    xp.AddObject(load_cmd, RelationType("ScriptableExposedProperty"))
    xp.Set("EPClassId", cmd_name)
    xp.Set("EPNameId", "spirent.methodology.LoadTemplateCommand.TagPrefix.0")
    xp.Set("EPPropertyId", "spirent.methodology.LoadTemplateCommand.TagPrefix")
    xp.Set("EPClassId", "spirent.methodology.loadtemplatecommand")

    json_dict = {}
    json_dict["spirent.methodology.LoadTemplateCommand.TagPrefix.0"] = "MyTagPrefix"

    KeyValuePairs = json.dumps(json_dict)

    cmd = ctor.CreateCommand(PKG + ".MethodologyGroupCommand")
    cmd.Set("KeyValueJson", KeyValuePairs)
    cmd.Execute()

    assert load_cmd.Get('TagPrefix') == 'MyTagPrefix'
    return


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
