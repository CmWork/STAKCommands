from StcIntPythonPL import *
import xml.etree.ElementTree as etree
from mock import MagicMock
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
import spirent.methodology.traffic.LoadTrafficTemplateCommand as command


PKG_BASE = 'spirent.methodology'
PKG = PKG_BASE + '.traffic'


def test_validate_defaults(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.LoadTrafficTemplateCommand', seq)
    assert False is cmd.Get('AutoExpandTemplate')
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.validate(cmd.Get('CopiesPerParent'),
                           cmd.GetCollection('TargetTagList'),
                           cmd.Get('TemplateXml'),
                           cmd.Get('TemplateXmlFileName'),
                           cmd.Get('TagPrefix'),
                           cmd.Get('AutoExpandTemplate'),
                           cmd.Get('EnableLoadFromFileName'),
                           cmd.Get('Weight'),
                           cmd.Get('StmTemplateMix'))
    assert '' == ret


def test_run(stc):
    test_xml = get_test_xml()

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="" />')
    cmd = ctor.Create(PKG + '.LoadTrafficTemplateCommand', seq)
    cmd.Set('TemplateXml', test_xml)
    cmd.Set('EnableLoadFromFileName', False)
    cmd.Set('StmTemplateMix', traf_mix.GetObjectHandle())
    command.get_this_cmd = MagicMock(return_value=cmd)

    # Create a contained command to check the StmTemplateConfig
    # gets copied in.
    mod_cmd = ctor.Create(PKG_BASE + '.ModifyTemplatePropertyCommand', cmd)
    cmd.SetCollection("CommandList", [mod_cmd.GetObjectHandle()])

    ret = command.run(cmd.Get('CopiesPerParent'),
                      cmd.GetCollection('TargetTagList'),
                      cmd.Get('TemplateXml'),
                      cmd.Get('TemplateXmlFileName'),
                      cmd.Get('TagPrefix'),
                      cmd.Get('AutoExpandTemplate'),
                      cmd.Get('EnableLoadFromFileName'),
                      cmd.Get('Weight'),
                      cmd.Get('StmTemplateMix'))
    assert True is ret
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    wl_str = mix_elem.get('WeightList')
    wl_float = [float(x) for x in wl_str.split()]
    assert 1 == len(wl_float)
    assert 10.0 == wl_float[0]
    obj_list = traf_mix.GetObjects('StmTemplateConfig')
    assert 1 == len(obj_list)

    # Verify the command set its output properly
    assert cmd.Get("StmTemplateConfig") == obj_list[0].GetObjectHandle()

    # Verify the command configured its children properly
    assert mod_cmd.Get("StmTemplateConfig") == obj_list[0].GetObjectHandle()

    # Check the parent
    parent_list = obj_list[0].GetObjects("Scriptable",
                                         RelationType("ParentChild", 1))
    assert len(parent_list) == 1
    assert parent_list[0].GetObjectHandle() == \
        traf_mix.GetObjectHandle()


def get_test_xml():
    return \
        """<Template>
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
       Name="ttStreamBlockLoadProfile">
      </Tag>
    </Tags>
    <StreamBlock id="2111" serializationBase="true"
     IsControlledByGenerator="TRUE"
     ControlledBy="generator"
     TrafficPattern="PAIR"
     EndpointMapping="ONE_TO_ONE"
     EnableStreamOnlyGeneration="TRUE"
     EnableBidirectionalTraffic="FALSE"
     EqualRxPortDistribution="TRUE"
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
     FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;&lt;""" + \
        """pdu name=&quot;eth1&quot; pdu=&quot;ethernet:Ethernet""" + \
        """II&quot;&gt;&lt;/pdu&gt;&lt;pdu name=&quot;ip_1&quot;""" + \
        """ pdu=&quot;ipv4:IPv4&quot;&gt;&lt;tosDiffserv name=&q""" + \
        """uot;anon_2117&quot;&gt;&lt;tos name=&quot;anon_2118&q""" + \
        """uot;&gt;&lt;/tos&gt;&lt;/tosDiffserv&gt;&lt;/pdu&gt;&""" + \
        """lt;/pdus&gt;&lt;/config&gt;&lt;/frame&gt;"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Basic StreamBlock">
      <Relation type="UserTag" target="1400"/>
      <Relation type="AffiliationStreamBlockLoadProfile" target="2112"/>
    </StreamBlock>
    <StreamBlockLoadProfile id="2112" serializationBase="true"
     Load="10"
     LoadUnit="PERCENT_LINE_RATE"
     BurstSize="1"
     InterFrameGap="12"
     InterFrameGapUnit="BYTES"
     StartDelay="0"
     Priority="0"
     Active="TRUE"
     LocalActive="TRUE"
     Name="StreamBlockLoadProfile 1">
      <Relation type="UserTag" target="1401"/>
    </StreamBlockLoadProfile>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""
