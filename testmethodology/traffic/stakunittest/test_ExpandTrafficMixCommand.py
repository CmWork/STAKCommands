from StcIntPythonPL import *
import json


PKG = "spirent.methodology.traffic"


def test_expand_trf_mix(stc):
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
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingTagList": [west_ip_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 250,
                 "loadUnits": "FRAMES_PER_SECOND",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "75%",
                                 "postExpandModify":
                                 [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_2_src_1_dst(stc):
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

    # East Device 1
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

    # West Device 1
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

    # East Device 2
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
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingTagList": [west_ip_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_1_src_2_dst(stc):
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

    # East Device 1
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

    # West Device 1
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

    # West Device 2
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
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingTagList": [west_ip_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_bidir_explicit(stc):
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
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingTagList": [east_ip_tag.Get("Name"),
                                                               west_ip_tag.Get("Name")
                                                               ],
                                         "dstBindingTagList": [west_ip_tag.Get("Name"),
                                                               east_ip_tag.Get("Name")
                                                               ]
                                         }
                     }

    json_dict = {"load": 250,
                 "loadUnits": "FRAMES_PER_SECOND",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "75%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }

    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    # East -> West
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

    # West -> East
    sb_list = port2.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObject("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObject("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert src_binding.GetObjectHandle() == ipv4if2.GetObjectHandle()
    assert dst_binding.GetObjectHandle() == ipv4if1.GetObjectHandle()
    exp_dst_port = sb.GetObject('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert exp_dst_port.GetObjectHandle() == port1.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')


def test_expand_trf_mix_raw(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port_list = []
    for loc in ['//10.14.16.27/2/1', '//10.14.16.27/2/2']:
        port = ctor.Create('Port', project)
        port.Set('Location', loc)
        phy = ctor.Create('EthernetCopper', port)
        port.AddObject(phy, RelationType('ActivePhy'))
        port_list.append(port)

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    group_tag_list = ['East Port Group', 'West Port Group']
    for tag_name, port in zip(group_tag_list, port_list):
        tag_obj = ctor.Create('Tag', tags)
        tag_obj.Set('Name', tag_name)
        tags.AddObject(tag_obj, RelationType('UserTag'))
        port.AddObject(tag_obj, RelationType('UserTag'))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.
    json_dict = {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "Ipv4_Stream.xml",
                "weight": "75%",
                "expand":
                {
                    "targetTagList": [
                        "East Port Group"
                        ]
                }
            }
        ]
    }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    sb_list = project.GetObjects("StreamBlock")
    assert not sb_list
    sb_list = port_list[0].GetObjects("StreamBlock")
    assert not sb_list
    sb_list = port_list[1].GetObjects("StreamBlock")
    assert not sb_list

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert not sb_list

    # Check the generated objects
    sb_list = port_list[0].GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObject("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObject("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is None
    assert dst_binding is None
    exp_dst_port = sb.GetObject('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is None
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')

    # port2 should have nothing
    sb_list = port_list[1].GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_bidir_flag(stc):
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
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingTagList": [west_ip_tag.Get("Name")],
                                         "bidirectional": True
                                         }
                     }

    json_dict = {"load": 250,
                 "loadUnits": "FRAMES_PER_SECOND",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "75%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }

    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    # East -> West
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

    # West -> East
    sb_list = port2.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObject("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObject("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert src_binding.GetObjectHandle() == ipv4if2.GetObjectHandle()
    assert dst_binding.GetObjectHandle() == ipv4if1.GetObjectHandle()
    exp_dst_port = sb.GetObject('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert exp_dst_port.GetObjectHandle() == port1.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')


def test_expand_trf_mix_mesh(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    east_port_group_tag = ctor.Create("Tag", tags)
    east_port_group_tag.Set("Name", "East Port Group")
    port1.AddObject(east_port_group_tag, RelationType("UserTag"))
    tags.AddObject(east_port_group_tag, RelationType("UserTag"))

    east_ip_tag = ctor.Create("Tag", tags)
    east_ip_tag.Set("Name", "East Ipv4If")
    east_dev_tag = ctor.Create("Tag", tags)
    east_dev_tag.Set("Name", "East Dev")
    # East Devices
    dev = []
    ipv4if = []
    ethiiif = []
    for i in [0, 1, 2, 3]:
        dev.append(ctor.Create("EmulatedDevice", project))
        ipv4if.append(ctor.Create("Ipv4If", dev[i]))
        ethiiif.append(ctor.Create("EthIIIf", dev[i]))
        ipv4if[i].AddObject(ethiiif[i], RelationType("StackedOnEndpoint"))
        dev[i].AddObject(ipv4if[i], RelationType("PrimaryIf"))
        dev[i].AddObject(ethiiif[i], RelationType("TopLevelIf"))
        dev[i].AddObject(port1, RelationType("AffiliationPort"))
        dev[i].AddObject(east_dev_tag, RelationType("UserTag"))
        ipv4if[i].AddObject(east_ip_tag, RelationType("UserTag"))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_mesh_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.
    json_dict = {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "Ipv4_Stream.xml",
                "weight": "75%",
                "postExpandModify": [
                    {
                        "streamBlockExpand": {
                            "endpointMapping": {
                                "srcBindingTagList": ["East Ipv4If"],
                                "dstBindingTagList": ["East Ipv4If"]
                            }
                        }
                    }
                ]
            }
        ]
    }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    # East -> West
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb is not None
    src_binding = sb.GetObject("NetworkInterface", RelationType("SrcBinding"))
    dst_binding = sb.GetObject("NetworkInterface", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert src_binding.GetObjectHandle() == ipv4if[0].GetObjectHandle()
    assert dst_binding.GetObjectHandle() == ipv4if[1].GetObjectHandle()
    exp_dst_port = sb.GetObject('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert exp_dst_port.GetObjectHandle() == port1.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')


def test_expand_trf_mix_bindingclass_if_bind_emu(stc):
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

    # East Device 1
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

    # West Device 1
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

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingClassList": ["Ipv4If"],
                                         "srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingClassList": ["Ipv4If"],
                                         "dstBindingTagList": [west_dev_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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
    assert len(src_binding) == 1
    assert len(dst_binding) == 1
    assert src_binding[0].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert dst_binding[0].GetObjectHandle() == ipv4if2.GetObjectHandle()
    exp_dst_port = sb.GetObjects('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert len(exp_dst_port) == 1
    assert exp_dst_port[0].GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_bindingclass_dst_1if_3routes(stc):
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

    # West Device Router/Routes
    router = ctor.Create("BgpRouterConfig", dev2)
    router_tag = ctor.Create("Tag", tags)
    router_tag.Set("Name", "West Router")
    router.AddObject(router_tag, RelationType("UserTag"))
    route1 = ctor.Create("BgpIpv4RouteConfig", router)
    route2 = ctor.Create("BgpIpv4RouteConfig", router)
    route3 = ctor.Create("BgpIpv4RouteConfig", router)

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingClassList": ["Ipv4If"],
                                         "srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingClassList": ["Ipv4If", "Ipv4NetworkBlock"],
                                         "dstBindingTagList": [west_dev_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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
    dst_binding = sb.GetObjects("NetworkEndpoint", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert len(src_binding) == 4
    assert len(dst_binding) == 4
    assert src_binding[0].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert src_binding[1].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert src_binding[2].GetObjectHandle() == ipv4if1.GetObjectHandle()

    assert dst_binding[0].GetObjectHandle() == ipv4if2.GetObjectHandle()
    route_hnd1 = route1.GetObject('Ipv4NetworkBlock').GetObjectHandle()
    assert dst_binding[1].GetObjectHandle() == route_hnd1
    route_hnd2 = route2.GetObject('Ipv4NetworkBlock').GetObjectHandle()
    assert dst_binding[2].GetObjectHandle() == route_hnd2
    route_hnd3 = route3.GetObject('Ipv4NetworkBlock').GetObjectHandle()
    assert dst_binding[3].GetObjectHandle() == route_hnd3

    exp_dst_port = sb.GetObjects('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert len(exp_dst_port) == 1
    assert exp_dst_port[0].GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_bindingclass_mix(stc):
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

    # West Device Router/Routes
    proto_mix = ctor.Create("StmProtocolMix", project)
    tmpl_cfg = ctor.Create("StmTemplateConfig", proto_mix)
    tmpl_cfg.AddObject(dev2, RelationType("GeneratedObject"))
    proto_mix_tag = ctor.Create("Tag", tags)
    proto_mix_tag.Set("Name", "West proto_mix")
    dev2.AddObject(proto_mix_tag, RelationType("UserTag"))

    # Create an StmTrafficMix object as if the endpoints have
    # already been added and the topology templates have already
    # been expanded.
    trf_mix = ctor.Create("StmTrafficMix", project)

    # Create a child StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", trf_mix)
    container.Set("TemplateXml", get_trf_template())

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingClassList": ["Ipv4If"],
                                         "srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingClassList": ["Ipv4If", "Ipv4NetworkBlock"],
                                         "dstBindingTagList": [proto_mix_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
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
    dst_binding = sb.GetObjects("NetworkEndpoint", RelationType("DstBinding"))
    assert src_binding is not None
    assert dst_binding is not None
    assert len(src_binding) == 1
    assert len(dst_binding) == 1
    assert src_binding[0].GetObjectHandle() == ipv4if1.GetObjectHandle()
    assert dst_binding[0].GetObjectHandle() == ipv4if2.GetObjectHandle()
    exp_dst_port = sb.GetObjects('Port', RelationType('ExpectedRx'))
    assert exp_dst_port is not None
    assert len(exp_dst_port) == 1
    assert exp_dst_port[0].GetObjectHandle() == port2.GetObjectHandle()
    tag_list = sb.GetObjects('Tag', RelationType('UserTag'))
    assert 1 == len(tag_list)
    assert 'ttStreamBlock' == tag_list[0].Get('Name')

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)


def test_expand_trf_mix_no_bindingclass_fail(stc):
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

    # East Device 1
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

    # West Device 1
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

    # Build the InputJson that would have come in from the
    # CreateTrafficMixCommand.

    post_mod_dict = {"endpointMapping": {"srcBindingClassList": ["Ipv4If"],
                                         "srcBindingTagList": [east_ip_tag.Get("Name")],
                                         "dstBindingTagList": [west_dev_tag.Get("Name")]
                                         }
                     }

    json_dict = {"load": 10.0,
                 "loadUnits": "PERCENT_LINE_RATE",
                 "components": [{"baseTemplateFile": "Ipv4_Stream.xml",
                                 "weight": "10%",
                                 "postExpandModify": [{"streamBlockExpand": post_mod_dict}]
                                 }
                                ]
                 }
    trf_mix.Set("MixInfo", json.dumps(json_dict))

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandTrafficMixCommand")
    cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the lack of any project-level streamblocks
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # Check the generated objects
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 0

    # port2 should have nothing
    sb_list = port2.GetObjects("StreamBlock")
    assert len(sb_list) == 0


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
      <Tag id="1400"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttStreamBlock">
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
    </StreamBlock>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""


def get_trf_mesh_template():
    return '''
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
   ConfigurationFileName=""
   Active="TRUE"
   LocalActive="TRUE"
   Name="Project 1">
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
      <StreamBlock id="2997" serializationBase="true"
       IsControlledByGenerator="TRUE"
       ControlledBy="generator"
       TrafficPattern="MESH"
       EndpointMapping="ONE_TO_MANY"
       EnableStreamOnlyGeneration="TRUE"
       EnableBidirectionalTraffic="FALSE"
       EqualRxPortDistribution="FALSE"
       EnableTxPortSendingTrafficToSelf="TRUE"
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
       Filter="EthernetII"
       ShowAllHeaders="FALSE"
       AllowInvalidHeaders="FALSE"
       AutoSelectTunnel="FALSE"
       ByPassSimpleIpSubnetChecking="TRUE"
       EnableHighSpeedResultAnalysis="TRUE"
       EnableBackBoneTrafficSendToSelf="FALSE"
       EnableResolveDestMacAddress="TRUE"
       AdvancedInterleavingGroup="0"
       DisableTunnelBinding="FALSE"
       FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;&lt;pdu
name=&quot;ethernet_2977&quot;
pdu=&quot;ethernet:EthernetII&quot;&gt;
&lt;preamble minByteLength=&quot;4&quot;
&gt;55555555555555d5&lt;/preamble&gt;
&lt;dstMac&gt;00:10:94:00:00:0c&lt;/dstMac&gt;
&lt;srcMac&gt;00:10:94:00:00:0b&lt;/srcMac&gt;
&lt;/pdu&gt;
&lt;/pdus&gt;
&lt;/config&gt;&lt;/frame&gt;"
       Active="TRUE"
       LocalActive="TRUE"
       Name="StreamBlock 1-13">
          <Relation type="UserTag" target="1400"/>
      </StreamBlock>
  </Project>
</StcSystem>
'''
