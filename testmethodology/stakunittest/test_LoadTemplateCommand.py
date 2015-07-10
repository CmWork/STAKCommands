from StcIntPythonPL import *
from mock import MagicMock
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import LoadTemplateCommand as LoadCmd
import spirent.methodology.utils.xml_config_utils as xml_utils


def test_validate(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()

    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    res = LoadCmd.validate(1, [], test_xml, "", "", True, False, 0)
    assert res == ""


def test_validate_contained_cmds(stc):
    pkg = "spirent.methodology"
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)

    # Test the situation where there is an ExpandTemplateCommand
    # in the group
    exp_cmd = ctor.Create(pkg + ".ExpandTemplateCommand", cmd)
    cmd.SetCollection("CommandList", [exp_cmd.GetObjectHandle()])
    res = LoadCmd.validate_contained_cmds(cmd)
    assert "spirent.methodology.ExpandTemplateCommand is " + \
        "not allowed " in res

    # Test the situation where there is an invalid command
    # in the group.
    other_cmd = ctor.Create("ArpNdStartCommand", cmd)
    cmd.SetCollection("CommandList", [other_cmd.GetObjectHandle()])
    res = LoadCmd.validate_contained_cmds(cmd)
    assert "Command arpndstartcommand not in the set of " in res


def test_load_run(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd.SetCollection('TargetTagList', ['meports'])
    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Create the tag for the ports...
    tags = project.GetObject("Tags")
    tagMePorts = ctor.Create("Tag", tags)
    tagMePorts.Set("Name", "meports")
    tags.AddObject(tagMePorts, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port1.AddObject(tagMePorts, RelationType("UserTag"))
    res = LoadCmd.run(1, ["meports"], test_xml, "", "", True, False, 0)
    assert res is True

    # Verify the StmTemplateConfig object was correctly created...
    container_hnd = cmd.Get("StmTemplateConfig")
    assert container_hnd is not 0
    container = hnd_reg.Find(container_hnd)
    assert container is not None
    assert container.IsTypeOf("StmTemplateConfig")
    assert container.Get("TemplateXml") == test_xml
    return


def test_no_template_source(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd.SetCollection('TargetTagList', ['meports'])
    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Create the tag for the ports...
    tags = project.GetObject("Tags")
    tagMePorts = ctor.Create("Tag", tags)
    tagMePorts.Set("Name", "meports")
    tags.AddObject(tagMePorts, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port1.AddObject(tagMePorts, RelationType("UserTag"))
    res = LoadCmd.run(1, ["meports"], test_xml, "", "", True, True, 0)
    assert res is False
    return


def test_load_on_complete_auto_expand(stc):
    pkg = "spirent.methodology"
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    # Create the tag for the ports...
    tags = project.GetObject("Tags")
    tagMePorts = ctor.Create("Tag", tags)
    tagMePorts.Set("Name", "meports")
    tags.AddObject(tagMePorts, RelationType("UserTag"))

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port1.AddObject(tagMePorts, RelationType("UserTag"))

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)
    cmd.Set("StmTemplateConfig", container.GetObjectHandle())

    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Test AutoExpandTemplate when disabled
    cmd.Set("AutoExpandTemplate", False)
    cmd.Set("EnableLoadFromFilename", False)
    cmd.SetCollection("TargetTagList", ["meports"])
    res = LoadCmd.on_complete([])
    assert res is True

    # Verify that nothing was created
    created_stuff = container.GetObjects("Scriptable",
                                         RelationType("GeneratedObject"))
    assert len(created_stuff) == 0

    # Test AutoExpandTemplate when enabled
    cmd.Set("AutoExpandTemplate", True)
    cmd.SetCollection("TargetTagList", ["meports"])
    res = LoadCmd.on_complete([])
    assert res is True

    # Done with the command object...
    cmd.MarkDelete()

    # Verify that something was created
    created_stuff = container.GetObjects("Scriptable",
                                         RelationType("GeneratedObject"))
    assert len(created_stuff) == 1
    created_stuff_hnd_list = []
    for created_thing in created_stuff:
        created_stuff_hnd_list.append(created_thing.GetObjectHandle())

    dev = project.GetObject("EmulatedDevice")

    assert tags.GetObjectHandle() not in created_stuff_hnd_list
    assert dev.GetObjectHandle() in created_stuff_hnd_list

    # Note that the created_stuff is tested in the expand command
    # and does not need to be repeated here.
    return


def test_load_file(stc):
    pkg = "spirent.methodology"

    test_xml = get_test_xml()
    with open("TemplateXmlTestFile.xml", "w") as f:
        f.write(test_xml)
    assert os.path.isfile("TemplateXmlTestFile.xml")

    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd.Set("AutoExpandTemplate", False)
    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    res = LoadCmd.run(
        1, "", "<xxx/>",
        os.path.join(os.getcwd(), "TemplateXmlTestFile.xml"),
        "", False, True, 0)
    assert res is True
    StmTemplateConfig = hnd_reg.Find(cmd.Get("StmTemplateConfig"))
    assert StmTemplateConfig is not None
    xml = StmTemplateConfig.Get("TemplateXml")
    assert xml == test_xml
    os.remove("TemplateXmlTestFile.xml")
    assert not os.path.isfile("TemplateXmlTestFile.xml")
    return


def test_load_nonfile(stc):
    pkg = "spirent.methodology"

    test_xml = get_test_xml()
    neg_test_xml = "<xxx/>"
    with open("TemplateXmlTestFile.xml", "w") as f:
        f.write(neg_test_xml)
    assert os.path.isfile("TemplateXmlTestFile.xml")

    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd.Set("AutoExpandTemplate", False)
    LoadCmd.get_this_cmd = MagicMock(return_value=cmd)

    res = LoadCmd.run(
        1, "", test_xml,
        os.path.join(os.getcwd(), "IncorrectFileName.xml"),
        "", False, True, 0)
    # Note carefully the name of the file above is incorrect...
    assert res is False
    StmTemplateConfig = hnd_reg.Find(cmd.Get("StmTemplateConfig"))
    assert StmTemplateConfig is None
    os.remove("TemplateXmlTestFile.xml")
    assert not os.path.isfile("TemplateXmlTestFile.xml")
    return


def test_tag_prefix(stc):
    # Test XML:
    test_xml = get_test_xml()

    hnd_reg = CHandleRegistry.Instance()

    pkg = 'spirent.methodology'
    prefix = 'Test_'
    container_hnd = 0
    with AutoCommand(pkg + '.LoadTemplateCommand') as cmd:
        cmd.Set('TemplateXml', test_xml)
        cmd.Set('EnableLoadFromFilename', False)
        cmd.Set('TagPrefix', prefix)
        cmd.Set('AutoExpandTemplate', False)
        cmd.Execute()
        container_hnd = cmd.Get('StmTemplateConfig')
    assert container_hnd != 0
    container = hnd_reg.Find(container_hnd)
    assert container is not None
    assert container.IsTypeOf('StmTemplateConfig')

    orig_root = etree.fromstring(test_xml)
    orig_user_tag_list = xml_utils.get_tag_handle_list(orig_root, 'UserTag')
    orig_tag_list = xml_utils.find_tag_elements(orig_root)
    orig_name_list = []
    for tag in orig_tag_list:
        if int(tag.get('id')) in orig_user_tag_list:
            orig_name_list.append(tag.get('Name'))
    mod_root = etree.fromstring(container.Get('TemplateXml'))
    mod_user_tag_list = xml_utils.get_tag_handle_list(mod_root, 'UserTag')
    mod_tag_list = xml_utils.find_tag_elements(mod_root)
    mod_name_list = []
    for tag in mod_tag_list:
        if int(tag.get('id')) in mod_user_tag_list:
            mod_name_list.append(tag.get('Name'))
    pref_name_list = [prefix + name for name in orig_name_list]
    assert orig_user_tag_list == mod_user_tag_list
    assert pref_name_list == mod_name_list

    orig_name_list = []
    for ele in orig_root.findall('.//StmPropertyModifier'):
        orig_name_list.append(prefix + ele.get('TagName'))
    mod_name_list = []
    for ele in mod_root.findall('.//StmPropertyModifier'):
        mod_name_list.append(ele.get('TagName'))
    assert orig_name_list == mod_name_list
    return


def test_config_contained_cmds(stc):
    pkg = "spirent.methodology"
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    add_cmd = ctor.Create(pkg + ".AddTemplateObjectCommand", cmd)
    conf_cmd = ctor.Create(pkg + ".ConfigTemplateRelationCommand", cmd)
    mod_cmd = ctor.Create(pkg + ".ModifyTemplatePropertyCommand", cmd)
    del_cmd = ctor.Create(pkg + ".DeleteTemplateObjectCommand", cmd)
    exp_cmd = ctor.Create(pkg + ".ExpandTemplateCommand", cmd)
    add_cmd2 = ctor.Create(pkg + ".AddTemplateObjectCommand", cmd)
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", cmd)
    mrg_cmd = ctor.Create(pkg + ".MergeTemplateCommand", cmd)
    add_cmd3 = ctor.Create(pkg + ".AddTemplateObjectCommand", sequencer)
    modifier_cmd = ctor.Create(pkg + ".ConfigTemplateStmPropertyModifierCommand",
                               cmd)
    cmd.SetCollection("CommandList", [add_cmd.GetObjectHandle(),
                                      conf_cmd.GetObjectHandle(),
                                      mod_cmd.GetObjectHandle(),
                                      del_cmd.GetObjectHandle(),
                                      exp_cmd.GetObjectHandle(),
                                      add_cmd2.GetObjectHandle(),
                                      iter_cmd.GetObjectHandle(),
                                      mrg_cmd.GetObjectHandle(),
                                      modifier_cmd.GetObjectHandle()])
    sequencer.SetCollection("CommandList", [cmd.GetObjectHandle(),
                                            add_cmd3.GetObjectHandle()])

    container = ctor.Create("StmTemplateConfig", project)
    res = LoadCmd.config_contained_cmds(cmd, container)

    # Note that the ExpandTemplateCommand is skipped.  It would have
    # errored on validate if validate was called first.
    assert res == 7

    # Check the normal commands
    for contained_cmd in [add_cmd, conf_cmd, mod_cmd,
                          del_cmd, add_cmd2, mrg_cmd,
                          modifier_cmd]:
        assert contained_cmd.Get("StmTemplateConfig") == \
            container.GetObjectHandle()

    # Check the ExpandTemplateCommand
    # Nothing is configured for this since it isn't a valid command
    # in this group.
    assert len(exp_cmd.GetCollection("StmTemplateConfigList")) == 0

    # Check the negative test case
    assert add_cmd3.Get("StmTemplateConfig") == 0
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
      ModifierInfo='{
  "modifierType": "RANGE",
  "propertyName": "RouterId",
  "objectName": "EmulatedDevice",
  "propertyValueDict": {
    "start": "2.2.2.2",
    "step": "0.0.0.1",
    "repeat": 0,
    "recycle": 0,
    "resetOnNewTargetObject": false
  }
}'/>
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
