from StcIntPythonPL import *


PKG = "spirent.methodology.traffic"


def test_expand_trf_mix(stc):
    test_xml = get_trf_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

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
    tmi = "<MixInfo Load=\"10.0\" LoadUnit=\"PERCENT_LINE_RATE\" " + \
          "WeightList=\"10\">" + \
          "<Endpoints>" + \
          "<SrcEndpoint>" + str(east_ip_tag.Get("Name")) + \
          "</SrcEndpoint>" + \
          "<DstEndpoint>" + str(west_ip_tag.Get("Name")) + \
          "</DstEndpoint>" + \
          "</Endpoints></MixInfo>"
    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set("MixInfo", tmi)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMix1Command")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

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

#    # Check the generated objects
#    # Tags should not be in the list
#    gen_obj_list = container.GetObjects("Scriptable",
#                                        RelationType("GeneratedObject"))
#    assert len(gen_obj_list) == 3
#    for obj in gen_obj_list:
#        assert obj.IsTypeOf("Tags") is False
#        assert obj.IsTypeOf("EmulatedDevice")

#    # port4 should have nothing
#    dev_list = port4.GetObjects("EmulatedDevice",
#                                RelationType("AffiliationPort", 1))
#    assert len(dev_list) == 0

#    # Check tags
#    tag_list = tags.GetObjects("Tag")
#    assert len(tag_list) == 13
#    exp_tag_names = ["Host", "Router", "Edge", "Core", "Client",
#                     "Server", "EastPortGroup", "OuterVlan",
#                     "InnerVlan", "Dhcpv4", "TopLevelIf",
#                     "DHCP Client", "Ipv4If.Address"]
#    for tag in tag_list:
#        assert tag.Get("Name") in exp_tag_names


def test_expand_trf_mix_src_2_dest_1(stc):
    test_xml = get_trf_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

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

    # East Device -1
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

    # West Device -1
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

    # East Device -2
    dev3 = ctor.Create("EmulatedDevice", project)
    ipv4if3 = ctor.Create("Ipv4If", dev3)
    ethiiif3 = ctor.Create("EthIIIf", dev3)
    ipv4if3.AddObject(ethiiif3, RelationType("StackedOnEndpoint"))
    dev3.AddObject(ipv4if3, RelationType("PrimaryIf"))
    dev3.AddObject(ethiiif3, RelationType("TopLevelIf"))
    dev3.AddObject(port1, RelationType("AffiliationPort"))
    dev3.AddObject(east_dev_tag, RelationType("UserTag"))
    ipv4if3.AddObject(east_ip_tag, RelationType("UserTag"))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    tmi = "<MixInfo Load=\"10.0\" LoadUnit=\"PERCENT_LINE_RATE\" " + \
          "WeightList=\"10\">" + \
          "<Endpoints>" + \
          "<SrcEndpoint>" + str(east_ip_tag.Get("Name")) + \
          "</SrcEndpoint>" + \
          "<DstEndpoint>" + str(west_ip_tag.Get("Name")) + \
          "</DstEndpoint>" + \
          "</Endpoints></MixInfo>"
    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set("MixInfo", tmi)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMix1Command")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObjects("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObjects("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert len(src_binding) == 2
    assert len(dst_binding) == 2
    assert src_binding[0].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert src_binding[1].GetObjectHandle() == ipv4if3.GetObjectHandle()
    assert dst_binding[0].GetObjectHandle() == ipv4if2.GetObjectHandle()
    assert dst_binding[1].GetObjectHandle() == ipv4if2.GetObjectHandle()
    exp_dst_port = sb.GetObjects('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert len(exp_dst_port) == 1
    assert exp_dst_port[0].GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')


def test_expand_trf_mix_src_1_dest_2(stc):
    test_xml = get_trf_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

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

    # East Device -1
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

    # West Device -1
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

    # West Device -2
    dev3 = ctor.Create("EmulatedDevice", project)
    ipv4if3 = ctor.Create("Ipv4If", dev3)
    ethiiif3 = ctor.Create("EthIIIf", dev3)
    ipv4if3.AddObject(ethiiif3, RelationType("StackedOnEndpoint"))
    dev3.AddObject(ipv4if3, RelationType("PrimaryIf"))
    dev3.AddObject(ethiiif3, RelationType("TopLevelIf"))
    dev3.AddObject(port2, RelationType("AffiliationPort"))
    dev3.AddObject(west_dev_tag, RelationType("UserTag"))
    ipv4if3.AddObject(west_ip_tag, RelationType("UserTag"))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    tmi = "<MixInfo Load=\"10.0\" LoadUnit=\"PERCENT_LINE_RATE\" " + \
          "WeightList=\"10\">" + \
          "<Endpoints>" + \
          "<SrcEndpoint>" + str(east_ip_tag.Get("Name")) + \
          "</SrcEndpoint>" + \
          "<DstEndpoint>" + str(west_ip_tag.Get("Name")) + \
          "</DstEndpoint>" + \
          "</Endpoints></MixInfo>"
    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set("MixInfo", tmi)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMix1Command")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObjects("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObjects("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert len(src_binding) == 2
    assert len(dst_binding) == 2
    assert src_binding[0].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert src_binding[1].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert dst_binding[0].GetObjectHandle() == ipv4if2.GetObjectHandle()
    assert dst_binding[1].GetObjectHandle() == ipv4if3.GetObjectHandle()
    exp_dst_port = sb.GetObjects('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert len(exp_dst_port) == 1
    assert exp_dst_port[0].GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')


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
