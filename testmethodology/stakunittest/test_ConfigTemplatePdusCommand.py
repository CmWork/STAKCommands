from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.ConfigTemplatePdusCommand as CfgPdusCmd


PKG = 'spirent.methodology'


def test_process_pdus(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo('test_ConfigTemplatePdusCommand.test_process_pdus()')

    # Test case to show that we can change the sourceAddr of the IPv4 PDU.
    # Single StreamBlock in the template tagged with ttStreamBlock.
    root = etree.fromstring(template_1())
    p, v = pdus_1()
    assert CfgPdusCmd.process_pdus(p, v, root.find('.//StreamBlock'))
    r = etree.fromstring(root.find('.//StreamBlock').get('FrameConfig'))
    assert r.find('.//sourceAddr').text == '3.2.3.2'

    # Test case to show that we can change the sourceAddr of the IPv4 PDU
    # for the ttStreamBlock tagged StreamBlock, but not touch the ttStreamBlock2
    # tagged StreamBlock.
    root = etree.fromstring(template_2())
    assert CfgPdusCmd.process_pdus(p, v, root.find('.//StreamBlock'))
    for sb, t in zip(root.findall('.//StreamBlock'), ['3.2.3.2', '4.4.4.4']):
        r = etree.fromstring(sb.get('FrameConfig'))
        assert r.find('.//sourceAddr').text == t

    # Test case to show that we can change the sourceAddr of the IPv4 PDU
    # for both StreamBlocks independently.
    root = etree.fromstring(template_2())
    ps, vs = pdus_2()
    for sb, p, v in zip(root.findall('.//StreamBlock'), ps, vs):
        assert CfgPdusCmd.process_pdus([p], [v], sb)
    for sb, t in zip(root.findall('.//StreamBlock'), ['3.2.3.2', '1.4.1.4']):
        r = etree.fromstring(sb.get('FrameConfig'))
        assert r.find('.//sourceAddr').text == t


def test_run(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo('test_ConfigTemplatePdusCommand.test_run()')

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()

    cmd = ctor.Create(PKG + ".ConfigTemplatePdusCommand", sequencer)
    CfgPdusCmd.get_this_cmd = MagicMock(return_value=cmd)

    template = ctor.Create("StmTemplateConfig", project)
    template.Set('TemplateXml', template_2())

    p, v = pdus_1()
    assert CfgPdusCmd.run(template.GetObjectHandle(),
                          ['ttStreamBlock', 'ttStreamBlock2'], p, v)
    root = etree.fromstring(template.Get('TemplateXml'))
    for sb in root.findall('.//StreamBlock'):
        r = etree.fromstring(sb.get('FrameConfig'))
        assert '3.2.3.2' == r.find('.//sourceAddr').text

    p, v = pdus_1_badpv()
    assert not CfgPdusCmd.run(template.GetObjectHandle(), ['ttStreamBlock'], p, v)

    p, v = pdus_1_badref()
    assert not CfgPdusCmd.run(template.GetObjectHandle(), ['ttStreamBlock'], p, v)

    p, v = pdus_1()
    assert not CfgPdusCmd.run(project.GetObjectHandle(), ['ttStreamBlock'], p, v)


def pdus_1_badpv():
    return ['ipv4_5265.sourceAddr'], ['3.2.3.2', '3.2.3.2']


def pdus_1_badref():
    return ['ipv4_5265x.sourceAddr'], ['3.2.3.2']


def pdus_1():
    return ['ipv4_5265.sourceAddr'], ['3.2.3.2']


def pdus_2():
    return ['ipv4_5265.sourceAddr', 'ipv4_5265.sourceAddr'], ['3.2.3.2', '1.4.1.4']


def template_1():
    return '''<Template>
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
    <Relation type="DefaultSelection" target="1168"/>
    <Tags id="1208" serializationBase="true"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Tag id="1400"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttStreamBlock">
      </Tag>
    </Tags>
    <StreamBlock id="5263" serializationBase="true"
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
     ShowAllHeaders="FALSE"
     AllowInvalidHeaders="FALSE"
     AutoSelectTunnel="FALSE"
     ByPassSimpleIpSubnetChecking="FALSE"
     EnableHighSpeedResultAnalysis="TRUE"
     EnableBackBoneTrafficSendToSelf="TRUE"
     EnableResolveDestMacAddress="TRUE"
     AdvancedInterleavingGroup="0"
     DisableTunnelBinding="FALSE"
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
     Active="TRUE"
     LocalActive="TRUE"
     Name="Basic StreamBlock With Modifiers">
      <Relation type="UserTag" target="1400"/>
    </StreamBlock>
  </Project>
</StcSystem>
</DataModelXml>
</Template>'''


def template_2():
    return '''<Template>
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
    <Relation type="DefaultSelection" target="1168"/>
    <Tags id="1208" serializationBase="true"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Relation type="UserTag" target="1401"/>
      <Tag id="1400"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttStreamBlock">
      </Tag>
      <Tag id="1401"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttStreamBlock2">
      </Tag>
    </Tags>
    <StreamBlock id="5263" serializationBase="true"
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
     ShowAllHeaders="FALSE"
     AllowInvalidHeaders="FALSE"
     AutoSelectTunnel="FALSE"
     ByPassSimpleIpSubnetChecking="FALSE"
     EnableHighSpeedResultAnalysis="TRUE"
     EnableBackBoneTrafficSendToSelf="TRUE"
     EnableResolveDestMacAddress="TRUE"
     AdvancedInterleavingGroup="0"
     DisableTunnelBinding="FALSE"
     FrameConfig="&lt;frame&gt;&lt;config&gt;
&lt;pdus&gt;&lt;pdu name=&quot;ipv4_5265&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
&lt;totalLength&gt;20&lt;/totalLength&gt;
&lt;fragOffset&gt;0&lt;/fragOffset&gt;
&lt;ttl&gt;255&lt;/ttl&gt;&lt;checksum&gt;14204&lt;/checksum&gt;
&lt;sourceAddr&gt;3.3.3.3&lt;/sourceAddr&gt;
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
     Active="TRUE"
     LocalActive="TRUE"
     Name="Basic StreamBlock With Modifiers">
      <Relation type="UserTag" target="1401"/>
    </StreamBlock>
    <StreamBlock id="15263" serializationBase="true"
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
     ShowAllHeaders="FALSE"
     AllowInvalidHeaders="FALSE"
     AutoSelectTunnel="FALSE"
     ByPassSimpleIpSubnetChecking="FALSE"
     EnableHighSpeedResultAnalysis="TRUE"
     EnableBackBoneTrafficSendToSelf="TRUE"
     EnableResolveDestMacAddress="TRUE"
     AdvancedInterleavingGroup="0"
     DisableTunnelBinding="FALSE"
     FrameConfig="&lt;frame&gt;&lt;config&gt;
&lt;pdus&gt;&lt;pdu name=&quot;ipv4_5265&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
&lt;totalLength&gt;20&lt;/totalLength&gt;
&lt;fragOffset&gt;0&lt;/fragOffset&gt;
&lt;ttl&gt;255&lt;/ttl&gt;&lt;checksum&gt;14204&lt;/checksum&gt;
&lt;sourceAddr&gt;4.4.4.4&lt;/sourceAddr&gt;
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
     Active="TRUE"
     LocalActive="TRUE"
     Name="Basic StreamBlock With Modifiers">
      <Relation type="UserTag" target="1400"/>
    </StreamBlock>
  </Project>
</StcSystem>
</DataModelXml>
</Template>'''
