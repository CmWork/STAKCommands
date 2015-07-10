from StcIntPythonPL import *
from mock import MagicMock
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.traffictest.LoadAclTrafficRulesCommand as Cmd1
import spirent.methodology.traffic.LoadTrafficTemplateCommand as Cmd2
import spirent.methodology.ModifyTemplatePropertyCommand as Cmd3
import spirent.methodology.traffic.ExpandTrafficMix1Command as Cmd4


PKG = 'spirent.methodology'
TPKG = PKG + '.traffic'
TTPKG = PKG + '.traffictest'


def test_validate(stc):
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject('Sequencer')
    ctor = CScriptableCreator()
    command1 = ctor.Create(TTPKG + '.LoadAclTrafficRulesCommand', sequencer)
    command2 = ctor.Create(TPKG + '.LoadTrafficTemplateCommand', sequencer)
    Cmd1.get_this_cmd = MagicMock(return_value=command1)
    Cmd2.get_this_cmd = MagicMock(return_value=command2)

    rules = 'test_CsvTraffic.rules'
    try:
        with open(rules, "w") as f:
            f.write(rules_file_content1())
        msg = Cmd1.validate(1, [], template1(), '', '', False, False, None, 0.0, rules, 1, True)
        assert msg == ''
        msg = Cmd1.validate(1, [], template1(), '', '', False, False, None, 0.0, rules, 0, True)
        assert msg != ''
    finally:
        os.remove(rules)
    return


def test_run(stc):
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject('Sequencer')
    ctor = CScriptableCreator()
    command1 = ctor.Create(TTPKG + '.LoadAclTrafficRulesCommand', sequencer)
    command2 = ctor.Create(TPKG + '.LoadTrafficTemplateCommand', sequencer)
    command3 = ctor.Create(PKG + '.ModifyTemplatePropertyCommand', sequencer)
    command4 = ctor.Create(TPKG + '.ExpandTrafficMix1Command', sequencer)
    Cmd1.get_this_cmd = MagicMock(return_value=command1)
    Cmd2.get_this_cmd = MagicMock(return_value=command2)
    Cmd3.get_this_cmd = MagicMock(return_value=command3)
    Cmd4.get_this_cmd = MagicMock(return_value=command4)

    traf_mix = ctor.Create('StmTrafficMix', proj)
    assert traf_mix is not None
    mix_info = {'Load': str(100.0), 'LoadUnit': 'PERCENT_LINE_RATE', 'WeightList': ''}
    mix_elem = etree.Element('MixInfo', mix_info)
    assert mix_elem is not None
    xml = etree.tostring(mix_elem)
    traf_mix.Set('MixInfo', xml)
    assert xml == traf_mix.Get('MixInfo')
    mix = traf_mix.GetObjectHandle()
    assert mix is not None

    rules = 'test_CsvTraffic.rules'
    try:
        with open(rules, "w") as f:
            f.write(rules_file_content1())

        msg = Cmd1.validate(1, [], template1(), '', '', False, False, mix, 0.0, rules, 1, True)
        assert msg == ''
        assert Cmd1.run(1, [], template1(), '', 'bad', False, False, mix, 40.0, rules, 2, True)

        Cmd4.run(mix)

        e = etree.fromstring(traf_mix.Get('MixInfo'))
        assert e is not None
        for w in e.get('WeightList').split(' '):
            assert float(w) == 4.0

        sb_list = tag_utils.get_tagged_objects_from_string_names(['badttStreamBlock'])
        assert len(sb_list) == 10
        for sb in sb_list:
            load_prof = sb.GetObject('StreamBlockLoadProfile',
                                     RelationType('AffiliationStreamBlockLoadProfile'))
            assert load_prof.Get('Load') == 4.0
        rm_list = tag_utils.get_tagged_objects_from_string_names(['badttDstMac'])
        assert len(rm_list) == 10
        for rm, v in zip(rm_list, ['00:01:02:03:04:05',
                                   '00:01:02:03:FE:FF',
                                   '00:01:02:03:FF:FF',
                                   '00:00:01:00:00:01',
                                   '00:00:01:00:00:01',
                                   '00:01:02:03:04:05',
                                   '00:01:02:03:FE:FE',
                                   '00:01:02:03:FF:FE',
                                   '00:00:01:00:00:01',
                                   '00:00:01:00:00:01']):
            assert rm.Get('Data') == v
        rm_list = tag_utils.get_tagged_objects_from_string_names(['badttSrcMac'])
        assert len(rm_list) == 10
        for rm, v in zip(rm_list, ['00:01:02:03:33:FF',
                                   '00:01:02:03:FF:00',
                                   '00:01:02:04:00:00',
                                   '00:10:94:00:00:01',
                                   '00:10:94:00:00:01',
                                   '00:01:02:03:33:FF',
                                   '00:01:02:03:FF:01',
                                   '00:01:02:04:00:01',
                                   '00:10:94:00:00:01',
                                   '00:10:94:00:00:01']):
            assert rm.Get('Data') == v
        rm_list = tag_utils.get_tagged_objects_from_string_names(['badttDstIpAddr'])
        assert len(rm_list) == 10
        for rm, v in zip(rm_list, ['1.1.1.1',
                                   '3.1.2.0',
                                   '4.1.2.0',
                                   '193.85.1.3',
                                   '193.85.1.3',
                                   '1.1.1.1',
                                   '3.1.2.1',
                                   '4.1.2.1',
                                   '193.85.1.3',
                                   '193.85.1.3']):
            assert rm.Get('Data') == v
        rm_list = tag_utils.get_tagged_objects_from_string_names(['badttSrcIpAddr'])
        assert len(rm_list) == 10
        for rm, v in zip(rm_list, ['4.1.1.1',
                                   '6.1.0.255',
                                   '5.1.2.0',
                                   '41.1.1.1',
                                   '12.1.1.1',
                                   '4.1.1.1',
                                   '6.1.0.254',
                                   '5.1.2.1',
                                   '41.1.1.1',
                                   '12.1.1.1']):
            assert rm.Get('Data') == v
    finally:
        os.remove(rules)
    return


def rules_file_content1():
    return '''DstMACOp,DstMAC,SrcMACOp,SrcMAC,DstIPAddrOp,DstIPAddr,SrcIPAddrOp,SrcIPAddr,\
L4Type,DstPortOp,DstPort,SrcPortOp,SrcPort,Action
=,00:01:02:03:04:05,=,00:01:02:03:33:FF,=,1.1.1.1,=,4.1.1.1,TCP,<,80,>,80,ACCEPT
>,00:01:02:03:FF:00,<,00:01:02:03:FE:FF,<,3.1.1.255,>,6.1.1.0,TCP,<,880,>,880,DENY
<,00:01:02:04:00:00,>,00:01:02:03:FF:FF,>,4.1.1.255,>,5.1.1.255,TCP,=,840,=,840,ACCEPT
,,,,,,=,41.1.1.1,TCP,=,80,,,ACCEPT
,,,,,,=,12.1.1.1,TCP,=,80,,,ACCEPT
'''


def template1():
    return '''
<Template>
<Description />
<Image />
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
    <Relation type="DefaultSelection" target="16"/>
    <Tags id="1208" serializationBase="true"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Relation type="UserTag" target="1"/>
      <Relation type="UserTag" target="2"/>
      <Relation type="UserTag" target="3"/>
      <Relation type="UserTag" target="4"/>
      <Relation type="UserTag" target="5"/>
      <Relation type="UserTag" target="6"/>
      <Tag id="1400"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttStreamBlock">
      </Tag>
      <Tag id="1"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttDstMac">
      </Tag>
      <Tag id="2"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttSrcMac">
      </Tag>
      <Tag id="3"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttDstIpAddr">
      </Tag>
      <Tag id="4"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttSrcIpAddr">
      </Tag>
      <Tag id="5"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttDstPort">
      </Tag>
      <Tag id="6"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttSrcPort">
      </Tag>
    </Tags>
    <StreamBlock id="3129" serializationBase="true"
     IsControlledByGenerator="TRUE"
     ControlledBy="generator"
     TrafficPattern="PAIR"
     EndpointMapping="ONE_TO_ONE"
     EnableStreamOnlyGeneration="TRUE"
     EnableBidirectionalTraffic="FALSE"
     EqualRxPortDistribution="FALSE"
     EnableTxPortSendingTrafficToSelf="FALSE"
     EnableControlPlane="FALSE"
     InsertSig="TRUE"
     FrameLengthMode="FIXED"
     FixedFrameLength="128"
     MinFrameLength="128"
     MaxFrameLength="256"
     StepFrameLength="1"
     FillType="CONSTANT"
     ConstantFillPattern="0"
     EnableFcsErrorInsertion="FALSE"
     Filter=""
     ShowAllHeaders="TRUE"
     AllowInvalidHeaders="FALSE"
     AutoSelectTunnel="FALSE"
     ByPassSimpleIpSubnetChecking="FALSE"
     EnableHighSpeedResultAnalysis="TRUE"
     EnableBackBoneTrafficSendToSelf="TRUE"
     EnableResolveDestMacAddress="TRUE"
     AdvancedInterleavingGroup="0"
     DisableTunnelBinding="FALSE"
     FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;
      &lt;pdu name=&quot;ethernet_3113&quot; pdu=&quot;ethernet:EthernetII&quot;&gt;
      &lt;preamble minByteLength=&quot;4&quot; &gt;55555555555555d5&lt;/preamble&gt;
      &lt;dstMac&gt;00:00:01:00:00:01&lt;/dstMac&gt;
      &lt;srcMac&gt;00:10:94:00:00:01&lt;/srcMac&gt;
      &lt;/pdu&gt;&lt;pdu name=&quot;ipv4_3094&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
      &lt;totalLength&gt;20&lt;/totalLength&gt;&lt;ttl&gt;255&lt;/ttl&gt;
      &lt;checksum&gt;14195&lt;/checksum&gt;&lt;sourceAddr&gt;192.85.1.3&lt;/sourceAddr&gt;
      &lt;destAddr&gt;193.85.1.3&lt;/destAddr&gt;&lt;prefixLength&gt;24&lt;/prefixLength&gt;
      &lt;destPrefixLength&gt;24&lt;/destPrefixLength&gt;
      &lt;gateway&gt;192.85.1.1&lt;/gateway&gt;
      &lt;tosDiffserv name=&quot;anon_3193&quot;&gt;
      &lt;tos name=&quot;anon_3194&quot;&gt;&lt;precedence&gt;6&lt;/precedence&gt;
      &lt;dBit&gt;0&lt;/dBit&gt;&lt;tBit&gt;0&lt;/tBit&gt;
      &lt;rBit&gt;0&lt;/rBit&gt;&lt;mBit&gt;0&lt;/mBit&gt;
      &lt;reserved&gt;0&lt;/reserved&gt;&lt;/tos&gt;
      &lt;/tosDiffserv&gt;&lt;/pdu&gt;
      &lt;pdu name=&quot;proto1&quot; pdu=&quot;tcp:Tcp&quot;&gt;
      &lt;sourcePort&gt;1024&lt;/sourcePort&gt;
      &lt;destPort&gt;1024&lt;/destPort&gt;
      &lt;/pdu&gt;&lt;/pdus&gt;&lt;/config&gt;&lt;/frame&gt;"
     Active="TRUE"
     LocalActive="TRUE"
     Name="StreamBlock 7-3">
      <Relation type="UserTag" target="1400"/>
        <RangeModifier id="3155"
       ModifierMode="INCR"
       Mask="00:00:FF:FF:FF:FF"
       StepValue="00:00:00:00:00:01"
       RecycleCount="1"
       RepeatCount="0"
       Data="00:00:01:00:00:01"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="ethernet_3113.dstMac"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 7">
        <Relation type="UserTag" target="1"/>
      </RangeModifier>
      <RangeModifier id="3156"
       ModifierMode="INCR"
       Mask="00:00:FF:FF:FF:FF"
       StepValue="00:00:00:00:00:01"
       RecycleCount="1"
       RepeatCount="0"
       Data="00:10:94:00:00:01"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="ethernet_3113.srcMac"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 8">
        <Relation type="UserTag" target="2"/>
      </RangeModifier>
      <RangeModifier id="3157"
       ModifierMode="INCR"
       Mask="255.255.255.255"
       StepValue="0.0.0.1"
       RecycleCount="1"
       RepeatCount="0"
       Data="192.85.1.3"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="ipv4_3094.sourceAddr"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 9">
        <Relation type="UserTag" target="4"/>
      </RangeModifier>
      <RangeModifier id="3160"
       ModifierMode="INCR"
       Mask="255.255.255.255"
       StepValue="0.0.0.1"
       RecycleCount="1"
       RepeatCount="0"
       Data="193.85.1.3"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="ipv4_3094.destAddr"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 12">
        <Relation type="UserTag" target="3"/>
      </RangeModifier>
      <RangeModifier id="3158"
       ModifierMode="INCR"
       Mask="65535"
       StepValue="1"
       RecycleCount="1"
       RepeatCount="0"
       Data="1024"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="proto1.sourcePort"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 10">
        <Relation type="UserTag" target="6"/>
      </RangeModifier>
      <RangeModifier id="3159"
       ModifierMode="INCR"
       Mask="65535"
       StepValue="1"
       RecycleCount="1"
       RepeatCount="0"
       Data="1024"
       DataType="NATIVE"
       EnableStream="FALSE"
       Offset="0"
       OffsetReference="proto1.destPort"
       Active="TRUE"
       LocalActive="TRUE"
       Name="RangeModifier 11">
        <Relation type="UserTag" target="5"/>
      </RangeModifier>
    </StreamBlock>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
'''