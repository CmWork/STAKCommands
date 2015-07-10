from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
import json
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.traffic.CreateTrafficMixCommand as CreateTMix2Cmd


TPKG = 'spirent.methodology.traffic'
PKG = 'spirent.methodology'


def test_validate(stc):
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    ctor = CScriptableCreator()
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)
    CreateTMix2Cmd.get_this_cmd = MagicMock(return_value=cmd)
    res = CreateTMix2Cmd.validate('', '', False,)
    assert res == ''


def test_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    ctor = CScriptableCreator()
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)

    cmd_hnd_list = cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + '.IterationGroupCommand')

    cmd_hnd_list = grp_cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 1
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf('SequencerWhileCommand')

    exp_cmd_hnd = while_cmd.Get('ExpressionCommand')
    exp_cmd = hnd_reg.Find(exp_cmd_hnd)
    assert exp_cmd
    assert exp_cmd.IsTypeOf(PKG + '.ObjectIteratorCommand')

    cmd_hnd_list = while_cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 2
    conf_cmd_hnd = cmd_hnd_list[0]
    conf_cmd = hnd_reg.Find(conf_cmd_hnd)
    assert conf_cmd
    assert conf_cmd.IsTypeOf(PKG + '.IteratorConfigMixParamsCommand')

    load_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert load_cmd
    assert load_cmd.IsTypeOf(PKG + '.CreateTemplateConfigCommand')


def test_re_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    ctor = CScriptableCreator()

    # Create the command.  init() is called when the command is created
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)

    # Mock get_this_cmd
    CreateTMix2Cmd.get_this_cmd = MagicMock(return_value=cmd)

    # Check that init() was invoked
    cmd_hnd_list = cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + '.IterationGroupCommand')
    child_list = cmd.GetObjects('Command')
    assert len(child_list) == 1
    assert child_list[0].GetObjectHandle() == grp_cmd.GetObjectHandle()

    # Make some change in the contained sequence to simulate
    # an author modifying the contained sequence
    cmd_hnd_list = grp_cmd.GetCollection('CommandList')
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf('SequencerWhileCommand')

    cmd_hnd_list = while_cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 2

    iter_valid_cmd = ctor.Create(PKG + '.IteratorValidateCommand', while_cmd)
    cmd_hnd_list.append(iter_valid_cmd.GetObjectHandle())
    while_cmd.SetCollection('CommandList', cmd_hnd_list)

    # Call init() again.  This is invoked when the command is 'created'
    # again.  This appears to happen when a saved sequence with this
    # command in it is loaded.
    CreateTMix2Cmd.init()

    # Check that the original sequence did not change, that is,
    # the sequence wasn't pre-filled again.
    cmd_hnd_list = cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + '.IterationGroupCommand')
    child_list = cmd.GetObjects('Command')
    assert len(child_list) == 1
    assert child_list[0].GetObjectHandle() == grp_cmd.GetObjectHandle()

    # Find the inserted command to prove that the original sequence
    # was not overwritten
    cmd_hnd_list = grp_cmd.GetCollection('CommandList')
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf('SequencerWhileCommand')
    cmd_hnd_list = while_cmd.GetCollection('CommandList')
    assert len(cmd_hnd_list) == 3

    conf_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert conf_cmd
    assert conf_cmd.IsTypeOf(PKG + '.IteratorConfigMixParamsCommand')

    load_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert load_cmd
    assert load_cmd.IsTypeOf(PKG + '.CreateTemplateConfigCommand')

    valid_cmd = hnd_reg.Find(cmd_hnd_list[2])
    assert valid_cmd
    assert valid_cmd.IsTypeOf(PKG + '.IteratorValidateCommand')


def test_run(stc):
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)

    plLogger = PLLogger.GetLogger('test_CreateTrafficMixCommand.test_run')
    plLogger.LogInfo('start')

    CreateTMix2Cmd.get_this_cmd = MagicMock(return_value=cmd)
    CreateTMix2Cmd.run(mix_info(), 'TheMix', False)

    # Check the created StmTemplateMix
    mix_hnd = cmd.Get('StmTemplateMix')
    mix = hnd_reg.Find(mix_hnd)
    assert mix
    assert mix.Get('MixInfo') == mix_info()

    # Find the tagged commands
    tag_json = cmd.Get('GroupCommandTagInfo')
    assert tag_json != ''
    err_str, tag_dict = json_utils.load_json(tag_json)
    assert err_str == ""

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict['rowIterator']])
    assert len(tagged_obj_list) == 1
    obj_iter = tagged_obj_list[0]
    assert obj_iter.IsTypeOf(PKG + '.ObjectIteratorCommand')
    assert obj_iter.Get('StepVal') == 1.0
    assert obj_iter.Get('MaxVal') == 0.0
    assert obj_iter.Get('MinVal') == 0.0
    assert obj_iter.Get('IterMode') == 'STEP'
    assert obj_iter.Get('ValueType') == 'RANGE'

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict['rowConfigurator']])
    assert len(tagged_obj_list) == 1
    config_cmd = tagged_obj_list[0]
    assert config_cmd.IsTypeOf(PKG + '.IteratorConfigMixParamsCommand')
    assert mix_hnd == config_cmd.Get('StmTemplateMix')

    # Check the Tag
    tags = project.GetObject('Tags')
    assert tags
    user_tag_list = tags.GetObjects('Tag')
    assert len(user_tag_list)
    exp_tag = None
    for user_tag in user_tag_list:
        if user_tag.Get('Name') == 'TheMix':
            exp_tag = user_tag
            break
    assert exp_tag
    tag_target = exp_tag.GetObject('StmTemplateMix', RelationType('UserTag', 1))
    assert tag_target
    assert tag_target.GetObjectHandle() == mix.GetObjectHandle()

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict['templateConfigurator']])
    assert len(tagged_obj_list) == 1
    load_cmd = tagged_obj_list[0]
    assert load_cmd.IsTypeOf(PKG + '.CreateTemplateConfigCommand')
    load_input_mix_hnd = load_cmd.Get('StmTemplateMix')
    assert load_input_mix_hnd == mix.GetObjectHandle()


def mix_info():
    return '''
{
  "load": 50,
  "loadUnits": "FRAMES_PER_SECOND",
  "components": [
    {
      "weight": "50%",
      "baseTemplateFile": "test_stream.xml"
    }
  ]
}'''


def test_on_complete(stc):
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    mix = ctor.Create('StmProtocolMix', project)
    mix.Set("MixInfo", mix_info())
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)
    cmd.Set('MixTagName', 'TheMix')
    cmd.Set('StmTemplateMix', mix.GetObjectHandle())
    cmd.Set('AutoExpandTemplateMix', False)
    cmd.Set("GroupCommandTagInfo", "{\"fakeJson\": 3}")
    CreateTMix2Cmd.get_this_cmd = MagicMock(return_value=cmd)
    # Verify that no failed children will pass...
    res = CreateTMix2Cmd.on_complete([])
    assert cmd.Get("Status") == ""
    assert res
    # Verify that any element in the list (representing a child command)
    # is interpreted as a failed command and will fail...
    res = CreateTMix2Cmd.on_complete([1])
    assert not res


def test_autoexpand(stc):
    stc_sys = CStcSystem.Instance()
    sequencer = CStcSystem.Instance().GetObject('Sequencer')
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    etcu1 = ctor.Create("EthernetCopper", port1)
    port1.AddObject(etcu1, RelationType("ActivePhy"))
    etcu2 = ctor.Create("EthernetCopper", port2)
    port2.AddObject(etcu2, RelationType("ActivePhy"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    east_port_group_tag = ctor.Create("Tag", tags)
    east_port_group_tag.Set("Name", "East Port Group")
    west_port_group_tag = ctor.Create("Tag", tags)
    west_port_group_tag.Set("Name", "West Port Group")
    port1.AddObject(east_port_group_tag, RelationType("UserTag"))
    port2.AddObject(west_port_group_tag, RelationType("UserTag"))
    tags.AddObject(east_port_group_tag, RelationType("UserTag"))
    tags.AddObject(west_port_group_tag, RelationType("UserTag"))

    # East Device
    dev1 = ctor.Create("EmulatedDevice", project)
    ipv4if1 = ctor.Create("Ipv4If", dev1)
    ethiiif1 = ctor.Create("EthIIIf", dev1)
    ipv4if1.AddObject(ethiiif1, RelationType("StackedOnEndpoint"))
    dev1.AddObject(ipv4if1, RelationType("PrimaryIf"))
    dev1.AddObject(ethiiif1, RelationType("TopLevelIf"))
    dev1.AddObject(port1, RelationType("AffiliationPort"))
    east_ip_tag = ctor.Create("Tag", tags)
    east_ip_tag.Set("Name", "East Ipv4If")
    east_dev_tag = ctor.Create("Tag", tags)
    east_dev_tag.Set("Name", "East Dev")
    dev1.AddObject(east_dev_tag, RelationType("UserTag"))
    ipv4if1.AddObject(east_ip_tag, RelationType("UserTag"))

    # West Device
    dev2 = ctor.Create("EmulatedDevice", project)
    ipv4if2 = ctor.Create("Ipv4If", dev2)
    ethiiif2 = ctor.Create("EthIIIf", dev2)
    ipv4if2.AddObject(ethiiif2, RelationType("StackedOnEndpoint"))
    dev2.AddObject(ipv4if2, RelationType("PrimaryIf"))
    dev2.AddObject(ethiiif2, RelationType("TopLevelIf"))
    dev2.AddObject(port2, RelationType("AffiliationPort"))
    west_ip_tag = ctor.Create("Tag", tags)
    west_ip_tag.Set("Name", "West Ipv4If")
    west_dev_tag = ctor.Create("Tag", tags)
    west_dev_tag.Set("Name", "West Dev")
    dev2.AddObject(west_dev_tag, RelationType("UserTag"))
    ipv4if2.AddObject(west_ip_tag, RelationType("UserTag"))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson
    json_dict = {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "Ipv4_Streams.xml",
                "weight": "75%",
                "postExpandModify": [
                    {
                        "streamBlockExpand": {
                            "endpointMapping": {
                                "srcBindingTagList": [east_ip_tag.Get("Name")],
                                "dstBindingTagList": [west_ip_tag.Get("Name")]
                            }
                        }
                    }
                ]
            }
        ]
    }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Create CreateTrafficMixCommand and execute on_complete with auto expand
    cmd = ctor.Create(TPKG + '.CreateTrafficMixCommand', sequencer)
    cmd.Set('MixTagName', 'TheMix')
    cmd.Set('StmTemplateMix', trf_mix.GetObjectHandle())
    cmd.Set('AutoExpandTemplateMix', True)
    cmd.Set("GroupCommandTagInfo", "{\"fakeJson\": 3}")
    CreateTMix2Cmd.get_this_cmd = MagicMock(return_value=cmd)
    res = CreateTMix2Cmd.on_complete([])
    assert cmd.Get("Status") == ""
    assert res

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObject("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObject("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert src_binding.GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert dst_binding.GetObjectHandle() == ipv4if2.GetObjectHandle()
    exp_dst_port = sb.GetObject('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert exp_dst_port.GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def get_trf_template():
    return """
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
     FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;
&lt;pdu name=&quot;eth1&quot; pdu=&quot;ethernet:EthernetII&quot;&gt;
&lt;/pdu&gt;&lt;pdu name=&quot;ip_1&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
&lt;tosDiffserv name=&quot;anon_2117&quot;&gt;
&lt;tos name=&quot;anon_2118&quot;&gt;&lt;/tos&gt;&lt;/tosDiffserv&gt;
&lt;/pdu&gt;&lt;/pdus&gt;&lt;/config&gt;&lt;/frame&gt;"
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
