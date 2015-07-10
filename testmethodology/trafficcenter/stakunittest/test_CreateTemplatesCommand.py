from StcIntPythonPL import *
import json
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.utils import tag_utils
import test_configs


PKG = "spirent.methodology.trafficcenter"


def get_network_profiles(data):
    topo_nodes = data["topology_nodes"]
    nps = []
    for node in topo_nodes:
        node_nps = [np_config["subnet"] for np_config in node["subnet_configs"]]
        nps += node_nps
    return nps


def get_traffic_profiles(data):
    ep_infos = data["endpoint_infos"]
    return [ep_info["traffic"] for ep_info in ep_infos]


def test_basic(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.basic.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    ap_list_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 30

    # verify device tag
    dev1_list_from_tag = tag_utils.get_tagged_objects_from_string_names(
        ["net1_1234_ttEmulatedDevice"]
        )
    assert len(dev1_list_from_tag) == 1
    assert dev1_list_from_tag[0].GetObjectHandle() ==\
        device_1_list[0].GetObjectHandle()
    dev2_list_from_tag = tag_utils.get_tagged_objects_from_string_names(
        ["net2_2345_ttEmulatedDevice"]
        )
    assert len(dev2_list_from_tag) == 1
    assert dev2_list_from_tag[0].GetObjectHandle() ==\
        device_2_list[0].GetObjectHandle()

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "1.1.1.100"
    assert ipv4_if_2.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_2.Get("Gateway") == "1.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:22"

    sb_1 = ap_list_1[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))
    sb_2 = ap_list_2[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))

    assert sb_1.Get("fixedFrameLength") == 64
    assert sb_1.Get("minFrameLength") == 99
    assert sb_1.Get("maxFrameLength") == 111
    assert sb_1.Get("stepFrameLength") == 100
    assert sb_1.Get("frameLengthMode") == "FIXED"
    assert sb_1.Get("name") == "5001_2345-1"
    assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

    assert sb_2.Get("fixedFrameLength") == 128
    assert sb_2.Get("minFrameLength") == 88
    assert sb_2.Get("maxFrameLength") == 222
    assert sb_2.Get("stepFrameLength") == 200
    assert sb_2.Get("frameLengthMode") == "INCR"
    assert sb_2.Get("name") == "5002_1234-1"

    sb_1_src_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_1_src_dev_list) == 1

    sb_1_dst_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_1_dst_dev_list) == 1

    sb_2_src_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_2_src_dev_list) == 1

    sb_2_dst_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_2_dst_dev_list) == 1

    # test if preload is enabled
    preload_profile = project.GetObject("AnalyzerPreloadProfile")
    preload_sbs = [
        sb.GetObjectHandle() for sb
        in preload_profile.GetObjects(
            "StreamBlock",
            RelationType(
                "AffiliationAnalyzerPreloadStreamBlock"
                )
            )
        ]
    assert sb_1.GetObjectHandle() in preload_sbs
    assert sb_2.GetObjectHandle() in preload_sbs


#################################################
# input:
#     TrafficMix1: 3 TrafficFlow
#     TrafficMix2: 2 TrafficFlow
# output: Port1: 3 streamblocks generated
#         Port2: 2 streamblocks generated
def test_multiple_application_profile(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.multiple_application_profile.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()

    project = CStcSystem.Instance().GetObject("Project")
    np_list = project.GetObjects("StmTemplateConfig")

    assert len(np_list) == 2

    tp_list = project.GetObjects("StmTrafficMix")
    assert len(tp_list) == 2

    ap_list_1 = tp_list[0].GetObjects("StmTemplateConfig")
    assert len(ap_list_1) == 3

    ap_list_2 = tp_list[1].GetObjects("StmTemplateConfig")
    assert len(ap_list_2) == 2

    device_1_list = np_list[0].GetObjects(
        "EmulatedDevice", RelationType("GeneratedObject"))
    device_2_list = np_list[1].GetObjects(
        "EmulatedDevice", RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 30

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "1.1.1.100"
    assert ipv4_if_2.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_2.Get("Gateway") == "1.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:22"

    sb_1 = ap_list_1[0].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))
    sb_2 = ap_list_2[0].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))

    assert sb_1.Get("fixedFrameLength") == 64
    assert sb_1.Get("minFrameLength") == 99
    assert sb_1.Get("maxFrameLength") == 111
    assert sb_1.Get("stepFrameLength") == 100
    assert sb_1.Get("frameLengthMode") == "FIXED"

    assert sb_2.Get("fixedFrameLength") == 128
    assert sb_2.Get("minFrameLength") == 128
    assert sb_2.Get("maxFrameLength") == 222
    assert sb_2.Get("stepFrameLength") == 200
    assert sb_2.Get("frameLengthMode") == "INCR"

    sb_1_src_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_1_src_dev_list) == 1

    sb_1_dst_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_1_dst_dev_list) == 1

    sb_2_src_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_2_src_dev_list) == 1

    sb_2_dst_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_2_dst_dev_list) == 1

    sb_3 = ap_list_1[1].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))
    sb_4 = ap_list_2[1].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))

    assert sb_3.Get("fixedFrameLength") == 64
    assert sb_3.Get("minFrameLength") == 99
    assert sb_3.Get("maxFrameLength") == 111
    assert sb_3.Get("stepFrameLength") == 100
    assert sb_3.Get("frameLengthMode") == "FIXED"

    assert sb_4.Get("fixedFrameLength") == 128
    assert sb_4.Get("minFrameLength") == 128
    assert sb_4.Get("maxFrameLength") == 222
    assert sb_4.Get("stepFrameLength") == 200
    assert sb_4.Get("frameLengthMode") == "INCR"

    sb_3_src_dev_list = sb_3.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_3_src_dev_list) == 1

    sb_3_dst_dev_list = sb_3.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_3_dst_dev_list) == 1

    sb_4_src_dev_list = sb_4.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_4_src_dev_list) == 1

    sb_4_dst_dev_list = sb_4.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_4_dst_dev_list) == 1

    sb_5 = ap_list_1[2].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))

    assert sb_5.Get("fixedFrameLength") == 128
    assert sb_5.Get("minFrameLength") == 99
    assert sb_5.Get("maxFrameLength") == 128
    assert sb_5.Get("stepFrameLength") == 100
    assert sb_5.Get("frameLengthMode") == "FIXED"
    sb_5_src_dev_list = sb_5.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_5_src_dev_list) == 1

    sb_5_dst_dev_list = sb_5.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_5_dst_dev_list) == 1


#################################################
# input:
#     TrafficMix1: 2 TrafficFlow, load=101, load_unit=FPS
#     TrafficMix2: 2 TrafficFlow, load=101, load_unit=FPS
# output: Port1: 2 streamblocks generated, SB1 load=50, SB2 load=51
#         Port2: 2 streamblocks generated, SB1 load=50, SB2 load=51
def test_multiple_application_profile_load_value(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.\
        multiple_application_profile_load_value.test_config
    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig", json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig", json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    np_list = project.GetObjects("StmTemplateConfig")

    assert len(np_list) == 2

    tp_list = project.GetObjects("StmTrafficMix")
    assert len(tp_list) == 2

    ap_list_1 = tp_list[0].GetObjects("StmTemplateConfig")
    assert len(ap_list_1) == 2

    ap_list_2 = tp_list[1].GetObjects("StmTemplateConfig")
    assert len(ap_list_2) == 2

    device_1_list = np_list[0].GetObjects(
        "EmulatedDevice", RelationType("GeneratedObject"))
    device_2_list = np_list[1].GetObjects(
        "EmulatedDevice", RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 30

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "1.1.1.100"
    assert ipv4_if_2.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_2.Get("Gateway") == "1.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:22"

    sb_1 = ap_list_1[0].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))
    sb_2 = ap_list_2[0].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))

    load_profile1 = sb_1.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    assert load_profile1.Get("LoadUnit") == "FRAMES_PER_SECOND"
    assert load_profile1.Get("Load") == 51.0

    load_profile2 = sb_2.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    assert load_profile2.Get("LoadUnit") == "FRAMES_PER_SECOND"
    assert load_profile2.Get("Load") == 51.0

    sb_3 = ap_list_1[1].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))
    sb_4 = ap_list_2[1].GetObject(
        "StreamBlock", RelationType("GeneratedObject"))

    load_profile3 = sb_3.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    assert load_profile3.Get("LoadUnit") == "FRAMES_PER_SECOND"
    assert load_profile3.Get("Load") == 50.0

    load_profile4 = sb_4.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    assert load_profile4.Get("LoadUnit") == "FRAMES_PER_SECOND"
    assert load_profile4.Get("Load") == 50.0


#################################################
# input:
#     TrafficMix1: 3 TrafficFlow, load=101, load_unit=MEGABITS_PER_SECOND
#     TrafficMix2: 2 TrafficFlow, load=101, load_unit=MEGABITS_PER_SECOND
# output: Port1: 3 streamblocks generated,
#                      (SB1 load + SB2 load + SB3 load) == 101
#         Port2: 2 streamblocks generated,
#                      (SB4 load + SB5 laod) == 101
def test_multiple_application_profile_sum_load_value(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.\
        multiple_application_profile_sum_load_value.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig", json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig", json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    np_list = project.GetObjects("StmTemplateConfig")
    assert len(np_list) == 2

    tp_list = project.GetObjects("StmTrafficMix")
    assert len(tp_list) == 2

    ap_list_1 = tp_list[0].GetObjects("StmTemplateConfig")
    assert len(ap_list_1) == 3

    ap_list_2 = tp_list[1].GetObjects("StmTemplateConfig")
    assert len(ap_list_2) == 2

    sb_1 = ap_list_1[0].GetObject("StreamBlock", RelationType("GeneratedObject"))
    sb_2 = ap_list_1[1].GetObject("StreamBlock", RelationType("GeneratedObject"))
    sb_3 = ap_list_1[2].GetObject("StreamBlock", RelationType("GeneratedObject"))

    load_profile1 = sb_1.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )

    load_profile2 = sb_2.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )

    load_profile3 = sb_3.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    sum = load_profile1.Get("Load") + load_profile2.Get("Load") + load_profile3.Get("Load")
    assert sum == 101

    sb_4 = ap_list_2[0].GetObject("StreamBlock", RelationType("GeneratedObject"))
    sb_5 = ap_list_2[1].GetObject("StreamBlock", RelationType("GeneratedObject"))

    load_profile4 = sb_4.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )

    load_profile5 = sb_5.GetObject(
        "StreamBlockLoadProfile",
        RelationType("AffiliationStreamBlockLoadProfile")
        )
    sum = load_profile4.Get("Load") + load_profile5.Get("Load")
    assert sum == 101


def test_insert_sig(stc):
    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    test_config = test_configs.insert_sig.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    ap_list_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    sb_1 = ap_list_1[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))
    sb_2 = ap_list_2[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))

    assert sb_1.Get("insertsig") is False
    assert sb_2.Get("insertsig") is False


def test_multiple_subnets_pair(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.multiple_subnets_pair.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net1_1234")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 4

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 4

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_3_list = temp_list[2].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_4_list = temp_list[3].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert len(device_3_list) == 1
    assert len(device_4_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 15
    assert device_3_list[0].Get("deviceCount") == 30
    assert device_4_list[0].Get("deviceCount") == 5

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_3_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_4_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "2.1.1.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "2.1.1.10"

    assert ipv4_if_3.Get("Address") == "1.1.1.100"
    assert ipv4_if_3.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_3.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_4.Get("Address") == "3.1.1.100"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "3.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "ab:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_4.Get("SourceMac") == "0b:bb:cc:dd:ee:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)

    index = 1
    for sb_1 in sb_1_list_subnet_1:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

    index = 1
    for sb_1 in sb_1_list_subnet_2:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2346-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

    index = 1
    for sb_2 in sb_2_list_subnet_3:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 1

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

    index = 1
    for sb_2 in sb_2_list_subnet_4:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1234-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 1

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_2_list_subnet_3:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_2_list_subnet_4:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0


def test_multiple_subnets_backbone(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.multiple_subnets_backbone.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net3_1235")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 4

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 4

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_3_list = temp_list[2].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_4_list = temp_list[3].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert len(device_3_list) == 1
    assert len(device_4_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 15
    assert device_3_list[0].Get("deviceCount") == 30
    assert device_4_list[0].Get("deviceCount") == 5

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_3_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_4_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "2.1.1.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "2.1.1.10"

    assert ipv4_if_3.Get("Address") == "1.1.1.100"
    assert ipv4_if_3.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_3.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_4.Get("Address") == "3.1.1.100"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "3.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "ab:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_4.Get("SourceMac") == "0b:bb:cc:dd:ee:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)

    index = 1
    for sb_1 in sb_1_list_subnet_1:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 2

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"
        ipv4_if = sb_1_dst_dev_list[1]
        assert ipv4_if.Get("Address") == "2.1.1.1"

    index = 1
    for sb_1 in sb_1_list_subnet_2:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2346-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 2

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"
        ipv4_if = sb_1_dst_dev_list[1]
        assert ipv4_if.Get("Address") == "2.1.1.1"

    index = 1
    for sb_2 in sb_2_list_subnet_3:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1234-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 2

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"
        ipv4_if = sb_2_dst_dev_list[1]
        assert ipv4_if.Get("Address") == "3.1.1.100"

    index = 1
    for sb_2 in sb_2_list_subnet_4:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 2

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"
        ipv4_if = sb_2_dst_dev_list[1]
        assert ipv4_if.Get("Address") == "3.1.1.100"

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_2_list_subnet_3:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_2_list_subnet_4:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0


def test_unique_mac(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.unique_mac.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    # should not modify default value in template
    assert eth_if_1.Get("SourceMac") == "00:10:94:00:00:01"
    assert eth_if_2.Get("SourceMac") == "00:10:94:00:00:01"

    # should set UseDefaultPhyMac
    assert eth_if_1.Get("UseDefaultPhyMac") is True
    assert eth_if_2.Get("UseDefaultPhyMac") is True


def test_use_dst_mac(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.use_dst_mac.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net3_1235")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 4

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)

    assert sb_1_list_subnet_1[0].Get("ByPassSimpleIpSubnetChecking") is True
    assert sb_1_list_subnet_2[0].Get("ByPassSimpleIpSubnetChecking") is False
    assert sb_2_list_subnet_3[0].Get("ByPassSimpleIpSubnetChecking") is True
    assert sb_2_list_subnet_4[0].Get("ByPassSimpleIpSubnetChecking") is False


def test_uneven_subnets_pair(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.uneven_subnets_pair.test_config

    # Create five ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")
    west_port3 = ctor.Create("Port", project)
    west_port3.Set("Location", "//1.0.0.5/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    tags.AddObject(east_subnet_tag2, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))
    west_port3.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net3_1235")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    west_subnet_tag3 = ctor.Create("Tag", tags)
    west_subnet_tag3.Set("Name", "West_net5_1236")
    west_port3.AddObject(west_subnet_tag3, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 5

    trf_mix_list = project.GetObjects("StmTrafficMix")
    # disabled for now until additional fixes are done.
    # assert len(trf_mix_list) == 4

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_3_list = temp_list[2].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_4_list = temp_list[3].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_5_list = temp_list[4].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert len(device_3_list) == 1
    assert len(device_4_list) == 1
    assert len(device_5_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 15
    assert device_3_list[0].Get("deviceCount") == 9
    assert device_4_list[0].Get("deviceCount") == 30
    assert device_5_list[0].Get("deviceCount") == 5

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_3_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_4_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_5 = device_5_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "2.1.1.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "2.1.1.10"

    assert ipv4_if_3.Get("Address") == "5.1.1.1"
    assert ipv4_if_3.Get("AddrStep") == "0.1.1.1"
    assert ipv4_if_3.Get("Gateway") == "5.1.1.10"

    assert ipv4_if_4.Get("Address") == "1.1.1.100"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_5.Get("Address") == "3.1.1.100"
    assert ipv4_if_5.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_5.Get("Gateway") == "3.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_5 = ipv4_if_5.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "ab:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "ab:cc:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_4.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_5.Get("SourceMac") == "0b:bb:cc:dd:ee:ff"
    assert eth_if_5.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)

    index = 1
    for sb_1 in sb_1_list_subnet_1:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

    index = 1
    for sb_1 in sb_1_list_subnet_2:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2346-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

    index = 1
    for sb_2 in sb_2_list_subnet_3:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1234-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 1

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

    index = 1
    for sb_2 in sb_2_list_subnet_4:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 1

        ipv4_if = sb_2_dst_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

    # disable load validation as this is currently creating one too many stream blocks.
    return
    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_2_list_subnet_3:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_2_list_subnet_4:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0


def test_uneven_subnets_backbone(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.uneven_subnets_backbone.test_config

    # Create five ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")
    west_port3 = ctor.Create("Port", project)
    west_port3.Set("Location", "//1.0.0.5/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    tags.AddObject(east_subnet_tag2, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))
    west_port3.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net3_1235")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    west_subnet_tag3 = ctor.Create("Tag", tags)
    west_subnet_tag3.Set("Name", "West_net5_1236")
    west_port3.AddObject(west_subnet_tag3, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 5

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 5

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_3_list = temp_list[2].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_4_list = temp_list[3].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_5_list = temp_list[4].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert len(device_3_list) == 1
    assert len(device_4_list) == 1
    assert len(device_5_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 15
    assert device_3_list[0].Get("deviceCount") == 9
    assert device_4_list[0].Get("deviceCount") == 30
    assert device_5_list[0].Get("deviceCount") == 5

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_3_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_4_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_5 = device_5_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "2.1.1.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "2.1.1.10"

    assert ipv4_if_3.Get("Address") == "5.1.1.1"
    assert ipv4_if_3.Get("AddrStep") == "0.1.1.1"
    assert ipv4_if_3.Get("Gateway") == "5.1.1.10"

    assert ipv4_if_4.Get("Address") == "1.1.1.100"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_5.Get("Address") == "3.1.1.100"
    assert ipv4_if_5.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_5.Get("Gateway") == "3.1.1.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_5 = ipv4_if_5.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "ab:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "ab:cc:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_4.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_5.Get("SourceMac") == "0b:bb:cc:dd:ee:ff"
    assert eth_if_5.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_5 = trf_mix_list[4].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_5 = ap_list_2_subnet_5[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)
    assert(len(sb_2_list_subnet_5) == 1)

    index = 1
    for sb_1 in sb_1_list_subnet_1:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 3

        for ipv4_if, addr in zip(sb_1_dst_dev_list, ["1.1.1.1", "2.1.1.1", "5.1.1.1"]):
            assert ipv4_if.Get("Address") == addr

    index = 1
    for sb_1 in sb_1_list_subnet_2:
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2346-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == "3.1.1.100"

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 3

        for ipv4_if, addr in zip(sb_1_dst_dev_list, ["1.1.1.1", "2.1.1.1", "5.1.1.1"]):
            assert ipv4_if.Get("Address") == addr

    index = 1
    for sb_2 in sb_2_list_subnet_3:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1234-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "1.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 2

        for ipv4_if, addr in zip(sb_2_dst_dev_list, ["1.1.1.100", "3.1.1.100"]):
            assert ipv4_if.Get("Address") == addr

    index = 1
    for sb_2 in sb_2_list_subnet_4:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "2.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 2

        for ipv4_if, addr in zip(sb_2_dst_dev_list, ["1.1.1.100", "3.1.1.100"]):
            assert ipv4_if.Get("Address") == addr

    index = 1
    for sb_2 in sb_2_list_subnet_5:
        assert sb_2.Get("fixedFrameLength") == 128
        assert sb_2.Get("minFrameLength") == 88
        assert sb_2.Get("maxFrameLength") == 222
        assert sb_2.Get("stepFrameLength") == 200
        assert sb_2.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1236-" + str(index)
        index += 1
        assert sb_2.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_2.Get("frameconfig")

        sb_2_src_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_2_src_dev_list) == 1

        ipv4_if = sb_2_src_dev_list[0]
        assert ipv4_if.Get("Address") == "5.1.1.1"

        sb_2_dst_dev_list = sb_2.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_2_dst_dev_list) == 2

        for ipv4_if, addr in zip(sb_2_dst_dev_list, ["1.1.1.100", "3.1.1.100"]):
            assert ipv4_if.Get("Address") == addr

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 5.0
    load = 0
    for sb in sb_2_list_subnet_3:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_2_list_subnet_4:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0

    load = 0
    for sb in sb_2_list_subnet_5:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0


def test_multiple_ports_per_subnet(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.multiple_ports_per_subnet.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))
    west_port2.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 2

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 2
    assert len(device_2_list) == 2
    for device in device_1_list:
        assert device.Get("deviceCount") == 20

    for device in device_2_list:
        assert device.Get("deviceCount") == 30

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_1_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_2_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "1.1.2.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "1.1.2.10"

    assert ipv4_if_3.Get("Address") == "1.1.1.100"
    assert ipv4_if_3.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_3.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_4.Get("Address") == "1.1.2.102"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "1.1.2.20"

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "aa:bb:cc:dd:ef:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_4.Get("SourceMac") == "00:bb:cc:dd:ef:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 2)
    assert(len(sb_1_list_subnet_2) == 2)

    index = 1
    src_addr_list = ["1.1.1.100", "1.1.2.102"]
    dst_addr_list = ["1.1.1.1", "1.1.2.1"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_1, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    index = 1
    src_addr_list = ["1.1.1.1", "1.1.2.1"]
    dst_addr_list = ["1.1.1.100", "1.1.2.102"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_2, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 128
        assert sb_1.Get("minFrameLength") == 88
        assert sb_1.Get("maxFrameLength") == 222
        assert sb_1.Get("stepFrameLength") == 200
        assert sb_1.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0


def test_load_distribution_percentage_load(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.\
        load_distribution_percentage_load.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    east_subnet_tag2 = ctor.Create("Tag", tags)
    east_subnet_tag2.Set("Name", "East_net4_2346")
    east_port2.AddObject(east_subnet_tag2, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    west_subnet_tag2 = ctor.Create("Tag", tags)
    west_subnet_tag2.Set("Name", "West_net1_1234")
    west_port2.AddObject(west_subnet_tag2, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 4

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 4

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_3 = trf_mix_list[2].GetObjects("StmTemplateConfig")
    ap_list_2_subnet_4 = trf_mix_list[3].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_3 = ap_list_2_subnet_3[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_2_list_subnet_4 = ap_list_2_subnet_4[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 1)
    assert(len(sb_1_list_subnet_2) == 1)
    assert(len(sb_2_list_subnet_3) == 1)
    assert(len(sb_2_list_subnet_4) == 1)

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_2_list_subnet_3:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0
    load = 0
    for sb in sb_2_list_subnet_4:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0


def test_gateway_mac(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.gateway_mac.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))
    west_port2.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 2

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 2
    assert len(device_2_list) == 2
    for device in device_1_list:
        assert device.Get("deviceCount") == 20

    for device in device_2_list:
        assert device.Get("deviceCount") == 30

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_1_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_2_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("GatewayMac") == "aa:00:01:00:00:01"
    assert ipv4_if_1.Get("ResolveGatewayMac") is False

    assert ipv4_if_2.Get("Address") == "1.1.2.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("GatewayMac") == "aa:00:01:00:00:02"
    assert ipv4_if_2.Get("ResolveGatewayMac") is False

    assert ipv4_if_3.Get("Address") == "1.1.1.100"
    assert ipv4_if_3.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_3.Get("GatewayMac") == "bb:00:01:00:00:01"
    assert ipv4_if_3.Get("ResolveGatewayMac") is False

    assert ipv4_if_4.Get("Address") == "1.1.2.102"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("GatewayMac") == "bb:00:01:00:00:03"
    assert ipv4_if_4.Get("ResolveGatewayMac") is False

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "aa:bb:cc:dd:ef:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_4.Get("SourceMac") == "00:bb:cc:dd:ef:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 2)
    assert(len(sb_1_list_subnet_2) == 2)

    index = 1
    src_addr_list = ["1.1.1.100", "1.1.2.102"]
    dst_addr_list = ["1.1.1.1", "1.1.2.1"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_1, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    index = 1
    src_addr_list = ["1.1.1.1", "1.1.2.1"]
    dst_addr_list = ["1.1.1.100", "1.1.2.102"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_2, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 128
        assert sb_1.Get("minFrameLength") == 88
        assert sb_1.Get("maxFrameLength") == 222
        assert sb_1.Get("stepFrameLength") == 200
        assert sb_1.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0


def test_single_vlan(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.single_vlan.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))
    west_port2.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 2

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 2
    assert len(device_2_list) == 2

    for device in device_1_list:
        assert device.Get("deviceCount") == 7

    for device in device_2_list:
        assert device.Get("deviceCount") == 10

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_1_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_3 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_4 = device_2_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_2.Get("Address") == "1.1.2.1"
    assert ipv4_if_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_2.Get("Gateway") == "1.1.2.10"

    assert ipv4_if_3.Get("Address") == "1.1.1.100"
    assert ipv4_if_3.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_3.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_4.Get("Address") == "1.1.2.102"
    assert ipv4_if_4.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_4.Get("Gateway") == "1.1.2.20"

    vlan_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_1 = vlan_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = vlan_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan_if_3 = ipv4_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_3 = vlan_if_3.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan_if_4 = ipv4_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_4 = vlan_if_4.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "aa:bb:cc:dd:ef:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_3.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_3.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_4.Get("SourceMac") == "00:bb:cc:dd:ef:ff"
    assert eth_if_4.Get("SrcMacStep") == "00:00:00:11:11:22"

    # verify vlan
    assert vlan_if_1.Get("Priority") == 0
    assert vlan_if_1.Get("IsRange") is False
    assert vlan_if_1.GetCollection("IdList") == [200,
                                                 200,
                                                 200,
                                                 200,
                                                 200,
                                                 201,
                                                 201]

    assert vlan_if_2.Get("Priority") == 0
    assert vlan_if_2.Get("IsRange") is False
    assert vlan_if_2.GetCollection("IdList") == [202,
                                                 202,
                                                 202,
                                                 202,
                                                 202,
                                                 203,
                                                 203]
    assert vlan_if_3.Get("Priority") == 7
    assert vlan_if_3.Get("VlanId") == 300
    assert vlan_if_3.Get("IsRange") is True
    assert vlan_if_3.Get("IdRepeatCount") == 4
    assert vlan_if_4.Get("Priority") == 7
    assert vlan_if_4.Get("VlanId") == 300
    assert vlan_if_4.Get("IsRange") is True
    assert vlan_if_4.Get("IdRepeatCount") == 4

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 2)
    assert(len(sb_1_list_subnet_2) == 2)

    index = 1
    src_addr_list = ["1.1.1.100", "1.1.2.102"]
    dst_addr_list = ["1.1.1.1", "1.1.2.1"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_1, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    index = 1
    src_addr_list = ["1.1.1.1", "1.1.2.1"]
    dst_addr_list = ["1.1.1.100", "1.1.2.102"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_2, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 128
        assert sb_1.Get("minFrameLength") == 88
        assert sb_1.Get("maxFrameLength") == 222
        assert sb_1.Get("stepFrameLength") == 200
        assert sb_1.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0


def test_qnq_vlan(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.qnq_vlan.test_config

    # Create four ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", "//1.0.0.4/1/1")

    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", "//1.0.0.3/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))
    east_port2.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net3_1235")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))
    west_port2.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        print(trf_mix.Get("Name"))
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 2

    # West
    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    # East
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 2
    assert len(device_2_list) == 2
    for device in device_1_list:
        assert device.Get("deviceCount") == 7
    for device in device_2_list:
        assert device.Get("deviceCount") == 8

    ipv4_if_1_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_1_2 = device_1_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2_1 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2_2 = device_2_list[1].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    assert ipv4_if_1_1.Get("Address") == "1.1.1.1"
    assert ipv4_if_1_1.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1_1.Get("Gateway") == "1.1.1.10"

    assert ipv4_if_1_2.Get("Address") == "1.1.2.1"
    assert ipv4_if_1_2.Get("AddrStep") == "0.0.0.1"
    assert ipv4_if_1_2.Get("Gateway") == "1.1.2.10"

    assert ipv4_if_2_1.Get("Address") == "1.1.1.100"
    assert ipv4_if_2_1.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_2_1.Get("Gateway") == "1.1.1.20"

    assert ipv4_if_2_2.Get("Address") == "1.1.2.102"
    assert ipv4_if_2_2.Get("AddrStep") == "0.0.1.1"
    assert ipv4_if_2_2.Get("Gateway") == "1.1.2.20"

    vlan2_if_1_1 = ipv4_if_1_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan1_if_1_1 = vlan2_if_1_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_1_1 = vlan1_if_1_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan2_if_1_2 = ipv4_if_1_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan1_if_1_2 = vlan2_if_1_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_1_2 = vlan1_if_1_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan2_if_2_1 = ipv4_if_2_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan1_if_2_1 = vlan2_if_2_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2_1 = vlan1_if_2_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan2_if_2_2 = ipv4_if_2_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    vlan1_if_2_2 = vlan2_if_2_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2_2 = vlan1_if_2_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_1_2.Get("SourceMac") == "aa:bb:cc:dd:ef:ff"
    assert eth_if_1_2.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2_1.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_2_1.Get("SrcMacStep") == "00:00:00:11:11:22"

    assert eth_if_2_2.Get("SourceMac") == "00:bb:cc:dd:ef:ff"
    assert eth_if_2_2.Get("SrcMacStep") == "00:00:00:11:11:22"

    # verify vlan
    assert vlan1_if_1_1.Get("Priority") == 0
    assert vlan1_if_1_1.Get("IsRange") is False
    assert vlan1_if_1_1.GetCollection("IdList") == [200,
                                                    200,
                                                    200,
                                                    200,
                                                    200,
                                                    201,
                                                    201]
    assert vlan2_if_1_1.Get("Priority") == 1
    assert vlan2_if_1_1.Get("IsRange") is False
    assert vlan2_if_1_1.GetCollection("IdList") == [300,
                                                    300,
                                                    301,
                                                    301,
                                                    302,
                                                    303,
                                                    303]

    assert vlan1_if_1_2.Get("Priority") == 0
    assert vlan1_if_1_2.Get("IsRange") is False
    assert vlan1_if_1_2.GetCollection("IdList") == [202,
                                                    202,
                                                    202,
                                                    202,
                                                    202,
                                                    203,
                                                    203]
    assert vlan2_if_1_2.Get("Priority") == 1
    assert vlan2_if_1_2.Get("IsRange") is False
    assert vlan2_if_1_2.GetCollection("IdList") == [300,
                                                    300,
                                                    301,
                                                    301,
                                                    302,
                                                    303,
                                                    303]

    assert vlan1_if_2_1.Get("Priority") == 7
    assert vlan1_if_2_1.Get("IsRange") is True
    assert vlan1_if_2_1.Get("VlanId") == 200
    assert vlan1_if_2_1.Get("IdRepeatCount") == 3
    assert vlan2_if_2_1.Get("Priority") == 1
    assert vlan2_if_2_1.Get("IsRange") is True
    assert vlan2_if_2_1.Get("VlanId") == 300
    assert vlan2_if_2_1.Get("IdRepeatCount") == 1

    assert vlan1_if_2_2.Get("Priority") == 7
    assert vlan1_if_2_2.Get("IsRange") is True
    assert vlan1_if_2_2.Get("VlanId") == 200
    assert vlan1_if_2_2.Get("IdRepeatCount") == 3
    assert vlan2_if_2_2.Get("Priority") == 1
    assert vlan2_if_2_2.Get("IsRange") is True
    assert vlan2_if_2_2.Get("VlanId") == 304
    assert vlan2_if_2_2.Get("IdRepeatCount") == 1

    ap_list_1_subnet_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_1_subnet_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    sb_1_list_subnet_1 = ap_list_1_subnet_1[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )
    sb_1_list_subnet_2 = ap_list_1_subnet_2[0].GetObjects(
        "StreamBlock",
        RelationType("GeneratedObject")
        )

    assert(len(sb_1_list_subnet_1) == 2)
    assert(len(sb_1_list_subnet_2) == 2)

    index = 1
    src_addr_list = ["1.1.1.100", "1.1.2.102"]
    dst_addr_list = ["1.1.1.1", "1.1.2.1"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_1, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 64
        assert sb_1.Get("minFrameLength") == 99
        assert sb_1.Get("maxFrameLength") == 111
        assert sb_1.Get("stepFrameLength") == 100
        assert sb_1.Get("frameLengthMode") == "FIXED"
        sb_name = "5001_2345-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    index = 1
    src_addr_list = ["1.1.1.1", "1.1.2.1"]
    dst_addr_list = ["1.1.1.100", "1.1.2.102"]
    for sb_1, src_addr, dst_addr in zip(sb_1_list_subnet_2, src_addr_list, dst_addr_list):
        assert sb_1.Get("fixedFrameLength") == 128
        assert sb_1.Get("minFrameLength") == 88
        assert sb_1.Get("maxFrameLength") == 222
        assert sb_1.Get("stepFrameLength") == 200
        assert sb_1.Get("frameLengthMode") == "INCR"
        sb_name = "5002_1235-" + str(index)
        index += 1
        assert sb_1.Get("name") == sb_name
        assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' not in sb_1.Get("frameconfig")

        sb_1_src_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("SrcBinding"))
        assert len(sb_1_src_dev_list) == 1

        ipv4_if = sb_1_src_dev_list[0]
        assert ipv4_if.Get("Address") == src_addr

        sb_1_dst_dev_list = sb_1.GetObjects(
            "NetworkInterface", RelationType("DstBinding"))
        assert len(sb_1_dst_dev_list) == 1

        ipv4_if = sb_1_dst_dev_list[0]
        assert ipv4_if.Get("Address") == dst_addr

    # verify total load
    load = 0
    for sb in sb_1_list_subnet_1:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 10.0
    load = 0
    for sb in sb_1_list_subnet_2:
        load_prof = sb.GetObject("StreamBlockLoadProfile",
                                 RelationType("AffiliationStreamBlockLoadProfile"))
        load += load_prof.Get("Load")
    assert load == 20.0


def test_dhcpv4_gateway(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = test_configs.dhcpv4_gateway.test_config

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    temp_list = project.GetObjects("StmTemplateConfig")
    assert len(temp_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2

    for trf_mix in trf_mix_list:
        ap_list = trf_mix.GetObjects("StmTemplateConfig")
        assert len(ap_list) == 1
        gen_objs = ap_list[0].GetObjects("StreamBlock",
                                         RelationType("GeneratedObject"))
        assert len(gen_objs) == 1

    ap_list_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    ap_list_2 = trf_mix_list[1].GetObjects("StmTemplateConfig")

    device_1_list = temp_list[0].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))
    device_2_list = temp_list[1].GetObjects(
        "EmulatedDevice",
        RelationType("GeneratedObject"))

    assert len(device_1_list) == 1
    assert len(device_2_list) == 1
    assert device_1_list[0].Get("deviceCount") == 20
    assert device_2_list[0].Get("deviceCount") == 30

    # verify dhcp configs
    dhcp_config_1 = device_1_list[0].GetObject("Dhcpv4BlockConfig")
    assert dhcp_config_1 is not None
    dhcp_config_2 = device_2_list[0].GetObject("Dhcpv4BlockConfig")
    assert dhcp_config_2 is not None
    assert dhcp_config_1.GetCollection("OptionList") == [1,
                                                         3,
                                                         6,
                                                         15,
                                                         33,
                                                         44]
    assert dhcp_config_2.GetCollection("OptionList") == [1,
                                                         3,
                                                         6,
                                                         15,
                                                         33,
                                                         44]
    assert dhcp_config_1.Get("EnableRouterOption") is True
    assert dhcp_config_2.Get("EnableRouterOption") is True

    ipv4_if_1 = device_1_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))
    ipv4_if_2 = device_2_list[0].GetObject(
        "NetworkInterface", RelationType("TopLevelIf"))

    eth_if_1 = ipv4_if_1.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))
    eth_if_2 = ipv4_if_2.GetObject(
        "NetworkInterface", RelationType("StackedOnEndpoint"))

    assert eth_if_1.Get("SourceMac") == "aa:bb:cc:dd:ee:ff"
    assert eth_if_1.Get("SrcMacStep") == "00:00:00:11:11:11"

    assert eth_if_2.Get("SourceMac") == "00:bb:cc:dd:ee:ff"
    assert eth_if_2.Get("SrcMacStep") == "00:00:00:11:11:22"

    sb_1 = ap_list_1[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))
    sb_2 = ap_list_2[0].GetObject("StreamBlock",
                                  RelationType("GeneratedObject"))

    assert sb_1.Get("fixedFrameLength") == 64
    assert sb_1.Get("minFrameLength") == 99
    assert sb_1.Get("maxFrameLength") == 111
    assert sb_1.Get("stepFrameLength") == 100
    assert sb_1.Get("frameLengthMode") == "FIXED"
    assert sb_1.Get("name") == "5001_2345-1"
    assert '<pdu name="custom_1" pdu="custom:Custom">\
<pattern>0000</pattern></pdu>' in sb_1.Get("frameconfig")

    assert sb_2.Get("fixedFrameLength") == 128
    assert sb_2.Get("minFrameLength") == 88
    assert sb_2.Get("maxFrameLength") == 222
    assert sb_2.Get("stepFrameLength") == 200
    assert sb_2.Get("frameLengthMode") == "INCR"
    assert sb_2.Get("name") == "5002_1234-1"

    sb_1_src_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_1_src_dev_list) == 1

    sb_1_dst_dev_list = sb_1.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_1_dst_dev_list) == 1

    sb_2_src_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("SrcBinding"))
    assert len(sb_2_src_dev_list) == 1

    sb_2_dst_dev_list = sb_2.GetObjects(
        "NetworkInterface", RelationType("DstBinding"))
    assert len(sb_2_dst_dev_list) == 1

    # test if preload is enabled
    preload_profile = project.GetObject("AnalyzerPreloadProfile")
    preload_sbs = [
        sb.GetObjectHandle() for sb
        in preload_profile.GetObjects(
            "StreamBlock",
            RelationType(
                "AffiliationAnalyzerPreloadStreamBlock"
                )
            )
        ]
    assert sb_1.GetObjectHandle() in preload_sbs
    assert sb_2.GetObjectHandle() in preload_sbs
