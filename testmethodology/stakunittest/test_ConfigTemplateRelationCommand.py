from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import spirent.methodology.utils.xml_config_utils as xml_utils


def test_bad_relation(stc):
    # Test XML
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'
    template = ctor.Create('StmTemplateConfig', project)
    template.Set('TemplateXml', test_xml)

    failed = False
    fail_message = ""
    # Add a fake relation
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'TopLevelIf')
        cmd.Set('TargetTagName', 'Dhcpv4')
        cmd.Set('RelationName', 'FakeRelation')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'not a valid relation' in fail_message:
                failed = True
    if not failed:
        if fail_message != "":
            raise AssertionError('ConfigTemplateRelationCommand failed with ' +
                                 'unexpected error: "' + fail_message + '"')
        else:
            raise AssertionError('ConfigTemplateRelationCommand did not ' +
                                 'fail as expected')


def test_wrong_relation(stc):
    # Test XML
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'
    template = ctor.Create('StmTemplateConfig', project)
    template.Set('TemplateXml', test_xml)

    failed = False
    fail_message = ""
    # Add an invalid relation
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'TopLevelIf')
        cmd.Set('TargetTagName', 'Dhcpv4')
        cmd.Set('RelationName', 'ResultChild')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'is not valid between' in fail_message:
                failed = True
    if not failed:
        if fail_message != "":
            raise AssertionError('ConfigTemplateRelationCommand failed with ' +
                                 'unexpected error: "' + fail_message + '"')
        else:
            raise AssertionError('ConfigTemplateRelationCommand did not ' +
                                 'fail as expected')


def test_invalid_tag(stc):
    test_xml = get_test_xml()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'
    template = ctor.Create('StmTemplateConfig', project)
    template.Set('TemplateXml', test_xml)

    # Add an invalid source tag
    passFailState = ''
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'BadTag')
        cmd.Set('TargetTagName', 'EthIIIf')
        cmd.Set('RelationName', 'UsesIf')
        cmd.Set('RemoveRelation', False)
        cmd.Execute()
        passFailState = cmd.Get('PassFailState')

    assert passFailState == 'FAILED'

    # Add an invalid target tag
    passFailState = ''
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'Dhcpv4')
        cmd.Set('TargetTagName', 'BadTag')
        cmd.Set('RelationName', 'UsesIf')
        cmd.Set('RemoveRelation', False)
        cmd.Execute()
        passFailState = cmd.Get('PassFailState')

    assert passFailState == 'FAILED'


def test_run(stc):
    # Test XML
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'
    template = ctor.Create('StmTemplateConfig', project)
    template.Set('TemplateXml', test_xml)

    # Add a valid (but strange) relation between Dhcp and Ethernet
    passFailState = ''
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'Dhcpv4')
        cmd.Set('TargetTagName', 'EthIIIf')
        cmd.Set('RelationName', 'UsesIf')
        cmd.Set('RemoveRelation', False)
        cmd.Execute()
        passFailState = cmd.Get('PassFailState')

    assert passFailState == 'PASSED'
    # Check the XML
    root = etree.fromstring(template.Get('TemplateXml'))
    assert root is not None
    dhcpv4 = xml_utils.get_element(root, 'Dhcpv4BlockConfig')
    # There will be an already existing UsesIf relation as well as the new one
    rel_list = []
    for child_ele in dhcpv4:
        if child_ele.tag == 'Relation' and \
           child_ele.get('type') == 'UsesIf':
            rel_list.append(child_ele.get('target'))
    assert '2204' in rel_list

    # Remove a relation
    passFailState = ''
    with AutoCommand(pkg + '.ConfigTemplateRelationCommand') as cmd:
        cmd.Set('StmTemplateConfig', template.GetObjectHandle())
        cmd.Set('SrcTagName', 'Dhcpv4')
        cmd.Set('TargetTagName', 'TopLevelIf')
        cmd.Set('RelationName', 'UsesIf')
        cmd.Set('RemoveRelation', True)
        cmd.Execute()
        passFailState = cmd.Get('PassFailState')

    assert passFailState == 'PASSED'
    # Check the XML
    root = etree.fromstring(template.Get("TemplateXml"))
    assert root is not None
    ipv4_ele = xml_utils.get_element(root, 'Ipv4If')
    dhcp_ele = xml_utils.get_element(root, 'Dhcpv4BlockConfig')
    assert ipv4_ele is not None
    assert dhcp_ele is not None
    rel_list = []
    # need to add condition to check target handle since we added ethiiif
    for child_ele in dhcp_ele:
        if child_ele.tag == 'Relation' and \
           child_ele.get('type') == 'UsesIf':
            rel_list.append(child_ele.get('target'))
    assert '2203' not in rel_list


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
      <Relation type="UserTag" target="1411"/>
      <Relation type="UserTag" target="1412"/>
      <Relation type="UserTag" target="1414"/>
      <Relation type="DefaultTag" target="1206"/>
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
      <Tag id="1414"
       Active="TRUE"
       LocalActive="TRUE"
       Name="EthIIIf">
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
        <Relation type="UserTag" target="1414"/>
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
