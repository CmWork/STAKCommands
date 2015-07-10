from StcIntPythonPL import *
import json
from utils import expand_util
import utils.config_builders.device_builder as device_builder


PKG = "spirent.methodology.trafficcenter"
PKG_METH = "spirent.methodology"
PKG_METH_TRF = PKG_METH + ".traffic"


def validate(TopologyConfig, NetworkProfileConfig,
             TrafficProfileConfig, EndpointConfig):
    return ''


def run(TopologyConfig, NetworkProfileConfig,
        TrafficProfileConfig, EndpointConfig):
    conf_data = json.loads(TopologyConfig)
    np_data = json.loads(NetworkProfileConfig)
    tp_data = json.loads(TrafficProfileConfig)
    ep_data = json.loads(EndpointConfig)

    plLogger = PLLogger.GetLogger("CreateTemplatesCommand.run")
    plLogger.LogInfo("conf_data: " + str(conf_data))
    plLogger.LogInfo("np_data: " + str(np_data))
    plLogger.LogInfo("tp_data: " + str(tp_data))
    plLogger.LogInfo("ep_data: " + str(ep_data))

    topo_map = handleTopologyData(conf_data)
    np_map = handleNetworkProfiles(topo_map, np_data)
    tp_map = handle_endpoints(topo_map, ep_data, np_map, conf_data)
    expand(topo_map, tp_map, np_map)

    return True


"""  Move this to TrafficCenterTestCommand
def build_port_groups(conf_data):
    tags = project.GetObject("Tags")

    # FIXME:
    # Handle the case where Tags doesn't exist
    # though this error might be fatal.
    if tags is None:
        plLogger.LogError("Could not find Tags object under Project!")
        return None

    for node_id in conf_data["id_list"]:
        tag = ctor.Create("Tag", tags)
        tag.Set("Name", conf_data[node_id + ",name"])
        tags.AddObject(tag, RelationType("UserTag"))
        port.AddObject(tag, RelationType("UserTag"))
"""


# {'name_list': ['West', 'East'],
#  '374343123': {'subnet_list': [('2345', [{'id': '4001', 'location': '//1.0.0.2/1/1'}])],
#  'name': 'East'},
#  '83749364': {'subnet_list': [('1234', [{'id': '4000', 'location': '//1.0.0.1/1/1'}])],
#  'name': 'West'}}
def handleTopologyData(conf_data):
    plLogger = PLLogger.GetLogger("handleTopologyData")
    plLogger.LogInfo("conf_data: " + str(conf_data))
    topo_map = {}
    topo_map["name_list"] = []
    # topo_nodes = dumps(conf_data["topology_nodes"])
    topo_nodes = dumps(conf_data)
    plLogger.LogInfo("topo_nodes: " + str(topo_nodes))
    for topo_node in topo_nodes:
        plLogger.LogInfo("topo_node: " + str(topo_node))
        node_name = dumps(topo_node["name"])
        name = dumps(topo_node["name"])
        topo_map["name_list"].append(node_name)
        topo_map[node_name] = {}

        subnet_item_list = dumps(topo_node["subnet_configs"])
        topo_map[node_name]["subnet_list"] = []
        for subnet_item in subnet_item_list:
            subnet_id = dumps(subnet_item["subnet"]["id"])
            port_list = dumps(subnet_item["ports"])
            subnet_name = dumps(subnet_item["subnet"]["name"])
            topo_map[name]["subnet_list"].append((subnet_id, port_list, subnet_name))

    plLogger.LogInfo("topo_map: " + str(topo_map))
    return topo_map


def handleNetworkProfiles(topo_map, network_profiles):
    plLogger = PLLogger.GetLogger("handleNetworkProfiles")
    plLogger.LogInfo("handleNetworkProfiles: ")
    np_map = {}
    for np in network_profiles:
        np_id, ep_tag = handleIpv4NetworkProfile(topo_map, np)
        np_map[np_id] = {}
        np_map[np_id]["ep_tag"] = ep_tag
    return np_map


def handleIpv4NetworkProfile(topo_map, np):
    plLogger = PLLogger.GetLogger("handleIpv4NetworkProfile")
    plLogger.LogInfo("start")
    plLogger.LogInfo("topo_map: " + str(topo_map))

    # topo_map:
    # {'name_list': ['West', 'East'],
    #  '374343123': {'subnet_list': [('2345', [{'id': '4001', 'location': '//1.0.0.2/1/1'}])],
    #  'name': 'East'},
    #  '83749364': {'subnet_list': [('1234', [{'id' :'4000', 'location': '//1.0.0.1/1/1'}])],
    #  'name': 'West'}}

    np_id, ipv4If_tag = device_builder.create_configs(np, topo_map)

    return np_id, ipv4If_tag


def handleTrafficProfiles(traffic_profiles):
    plLogger = PLLogger.GetLogger("handleTrafficProfiles")
    plLogger.LogInfo("handleTrafficProfiles: start")
    tp_map = {}
    for tp in traffic_profiles:
        tp_id, handle = handleTrafficProfile(tp)
        tp_map[tp_id] = handle

    plLogger.LogInfo("handleTrafficProfiles: tp_map len: " + str(len(tp_map)))
    return tp_map


def create_traffic_mix(load, load_unit, tag_name):
    plLogger = PLLogger.GetLogger("create_traffic_mix")
    plLogger.LogInfo("create_traffic_mix: start")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    # Create an StmTemplateConfig
    cmd = ctor.CreateCommand(PKG_METH_TRF + ".CreateTrafficMix1Command")
    cmd.Set("Load", load)
    cmd.Set("LoadUnit", load_unit)
    cmd.Set("MixTagName", tag_name)
    cmd.Set("AutoExpandTemplateMix", False)

    cmd.Execute()
    tm_hnd = cmd.Get("StmTemplateMix")
    plLogger.LogInfo("StmTemplateMix handle: " + str(tm_hnd))
    tm = hnd_reg.Find(tm_hnd)
    cmd.MarkDelete()
    return tm


def create_traffic_template_config(template_file, tag_prefix, trf_mix):
    plLogger = PLLogger.GetLogger("create_traffic_template_config")
    plLogger.LogInfo("create_traffic_template_config: start")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    # Create an StmTemplateConfig
    cmd = ctor.CreateCommand(PKG_METH_TRF + ".LoadTrafficTemplateCommand")
    cmd.Set("TemplateXmlFileName", template_file)
    cmd.Set("AutoExpandTemplate", False)
    cmd.Set("EnableLoadFromFilename", True)
    cmd.Set("TagPrefix", tag_prefix)
    if trf_mix is not None:
        cmd.Set("StmTemplateMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    template_hnd = cmd.Get("StmTemplateConfig")
    template = hnd_reg.Find(template_hnd)
    cmd.MarkDelete()
    return template


def configure_streamblock_params(template, sb_tag, trf_flow, traffic_pattern, subnet):
    plLogger = PLLogger.GetLogger("configure_streamblock_params")
    plLogger.LogInfo("configure_streamblock_params: start")
    ctor = CScriptableCreator()

    # flow_id = dumps(trf_flow["_id"])
    weight = dumps(trf_flow["weight"])
    fixed_len = dumps(trf_flow["fixed_frame_length"])
    max_len = dumps(trf_flow["max_frame_length"])
    min_len = dumps(trf_flow["min_frame_length"])
    step_len = dumps(trf_flow["step_frame_length"])
    frame_len_mode = "FIXED"
    name = dumps(trf_flow["id"] + "_" + subnet["id"])
    insert_sig = trf_flow.get("insert_sig")
    frame_config = trf_flow.get("frame_config")
    gateway_config_type = subnet["gateway_config"]["_type"]
    by_pass = "FALSE"
    if gateway_config_type == "Profile::GatewayUseDestConfig":
        by_pass = "TRUE"
    if "frame_length_mode" in trf_flow.keys():
        mode = dumps(trf_flow["frame_length_mode"])
        if mode == 1:
            frame_len_mode = "FIXED"
        elif mode == 2:
            frame_len_mode = "INCR"
        elif mode == 3:
            frame_len_mode = "DECR"
        elif mode == 4:
            frame_len_mode = "IMIX"
        elif mode == 5:
            frame_len_mode = "RANDOM"
        elif mode == 6:
            frame_len_mode = "AUTO"
        else:
            frame_len_mode = "FIXED"
    plLogger.LogInfo("frame_length_mode: " + str(frame_len_mode))
    # Modify properties on the project-level streamblock
    cmd = ctor.CreateCommand(PKG_METH + ".ModifyTemplatePropertyCommand")
    cmd.Set("StmTemplateConfig", template.GetObjectHandle())
    cmd.SetCollection("TagNameList", [sb_tag])
    conf_list = [("StreamBlock.FixedFrameLength", str(fixed_len)),
                 ("StreamBlock.MaxFrameLength", str(max_len)),
                 ("StreamBlock.MinFrameLength", str(min_len)),
                 ("StreamBlock.StepFrameLength", str(step_len)),
                 ("StreamBlock.FrameLengthMode", str(frame_len_mode)),
                 ("StreamBlock.TrafficPattern", str(traffic_pattern)),
                 ("StreamBlock.Name", str(name)),
                 ("StreamBlock.ByPassSimpleIpSubnetChecking", by_pass)]
    if insert_sig is False:
        conf_list.append(("StreamBlock.InsertSig", "FALSE"))
    if frame_config is not None:
        conf_list.append(("StreamBlock.FrameConfig", str(frame_config)))
    cmd.SetCollection("PropertyList", [pv[0] for pv in conf_list])
    cmd.SetCollection("ValueList", [pv[1] for pv in conf_list])
    cmd.Execute()
    cmd.MarkDelete()

    # Weight is stored in the weight list in the StmTrafficMix
    return weight


def get_per_subnet_load(subnet_configs, load, load_unit):
    # Assumptions:
    # - A port is only used by one subnet.
    # - Load is evenly distributed across ports in a
    #   topology node except for percentage load.
    # - Each subnet creates a project level stream
    #   block. When the stream block is expanded on
    #   the ports, the load is applied for each expanded stream
    #   block. So the load specified at the project
    #   level stream block must be the load for a port.
    # Limitations:
    # Does not handle speed differences between ports.

    # The percentage is percentage of available bandwidth
    # So we return the load as is.
    if load_unit == "PERCENT_LINE_RATE":
        return load

    port_cnt = 0
    for subnet_config in subnet_configs:
        port_cnt += len(subnet_config["ports"])

    per_subnet_load = float(load)/port_cnt
    return per_subnet_load


def handleTrafficProfile(tp, src, dst, topo_data, np_map):
    tp_map = {}
    plLogger = PLLogger.GetLogger("handleTrafficProfile")
    plLogger.LogInfo("handleTrafficProfile: tp: " + str(tp))

    tp_id = dumps(tp["id"])
    tp_map[tp_id] = {"src_subnets": [],
                     "dst_tags": []}
    plLogger.LogInfo("handleTrafficProfile: tp_id: " + str(tp_id))
    load = dumps(tp["load"])
    load_unit = "PERCENT_LINE_RATE"
    if "load_unit" in tp.keys():
        units = dumps(tp["load_unit"])
        if units == 0:
            load_unit = "PERCENT_LINE_RATE"
        elif units == 1:
            load_unit = "FRAMES_PER_SECOND"
        elif units == 5:
            load_unit = "BITS_PER_SECOND"
        elif units == 6:
            load_unit = "KILOBITS_PER_SECOND"
        elif units == 7:
            load_unit = "MEGABITS_PER_SECOND"
        else:
            load_unit = "PERCENT_LINE_RATE"

    traffic_pattern = "PAIR"
    if "traffic_pattern" in tp.keys():
        pattern = dumps(tp["traffic_pattern"])
        if pattern == 0:
            traffic_pattern = "PAIR"
        elif pattern == 2:
            traffic_pattern = "BACKBONE"
        else:
            traffic_pattern = "PAIR"

    trf_flows = tp["traffic_flows"]
    sb_tag = "ttStreamBlock"

    plLogger.LogInfo("trf_flows len: " + str(len(trf_flows)))

    topo_nodes = dumps(topo_data)
    src_topo_list = [topo_node for topo_node in topo_nodes if topo_node["name"] == src]
    dst_topo_list = [topo_node for topo_node in topo_nodes if topo_node["name"] == dst]
    if len(src_topo_list) == 0:
        raise Exception("Cannot find topology side: %s" % src)
    if len(dst_topo_list) == 0:
        raise Exception("Cannot find topology side: %s" % dst)
    src_topo = src_topo_list[0]
    dst_topo = dst_topo_list[0]
    subnet_configs = src_topo["subnet_configs"]
    dst_subnet_configs = dst_topo["subnet_configs"]
    dst_tags = []
    for dst_subnet_config in dst_subnet_configs:
        dst_subnet = dst_subnet_config["subnet"]
        dst_tags.append(np_map[dst_subnet["id"]]["ep_tag"])
    subnet_load = get_per_subnet_load(subnet_configs, load, load_unit)
    for subnet_config in subnet_configs:
        subnet = subnet_config["subnet"]
        # create a traffic mix for each source subnet
        trf_mix = create_traffic_mix(float(load), load_unit, str(tp_id))
        weight_list = []
        for trf_flow in trf_flows:
            # FIXME:
            # May want to use a flow_name for tag prefixing....
            flow_id = dumps(trf_flow["id"])
            plLogger.LogInfo("flow_id: " + str(flow_id))

            tag_prefix = flow_id + "_" + subnet["id"]
            template = create_traffic_template_config("Ipv4_Stream.xml",
                                                      tag_prefix, trf_mix)
            weight = configure_streamblock_params(template,
                                                  tag_prefix + sb_tag,
                                                  trf_flow,
                                                  traffic_pattern,
                                                  subnet)
            plLogger.LogInfo("weight: " + str(weight))
            weight_list.append(weight)
        # Create WeightList string
        w_list = ""
        for weight in weight_list:
            w_list = w_list + str(weight) + " "

        # Update the StmTrafficMix
        mix_info = "<MixInfo Load=\"" + str(subnet_load) + "\" " + \
                   "LoadUnit=\"" + load_unit + "\" " + \
                   "WeightList=\"" + w_list + "\" />"
        plLogger.LogInfo("mix_info: " + str(mix_info))
        trf_mix.Set("MixInfo", mix_info)
        src_tag = np_map[subnet["id"]]["ep_tag"]

        tp_map[tp_id]["src_subnets"].append({
            "traffix_mix": trf_mix.GetObjectHandle(),
            "src_tag": src_tag
            })
    tp_map[tp_id]["dst_tags"] = dst_tags
    return tp_map


def handle_endpoints(topo_map, ep_data, np_map, topo_data):
    tp_map = {}
    plLogger = PLLogger.GetLogger("handle_endpoints")
    plLogger.LogInfo("handle_endpoints: start")
    plLogger = PLLogger.GetLogger("handle_endpoints")
    plLogger.LogInfo("topo_map: " + str(topo_map))
    plLogger.LogInfo("ep_data: " + str(ep_data))
    plLogger.LogInfo("tp_map: " + str(tp_map))
    plLogger.LogInfo("np_map: " + str(np_map))

    # topo_map:
    # {'name_list': ['West', 'East'],
    #  '374343123': {'subnet_list': [('2345', [{'id': '4001', 'location': '//1.0.0.2/1/1'}])],
    #  'name': 'East'},
    #  '83749364': {'subnet_list': [('1234', [{'id' :'4000', 'location': '//1.0.0.1/1/1'}])],
    #  'name': 'West'}}

    # ep_data: [{u'src': u'East', u'dst': u'West', u'traffic': {...}},
    #           {u'src': u'West', u'East': u'374343123', u'traffic': {...}}]
    # tp_map: {'2468': 664L, '1357': 658L}
    # na_map: {'1234': {'ep_tag': 'net1_1234_ttIpv4If', 'handles': [960L]},
    #          '2345': {'ep_tag': 'net2_1234_ttIpv4If', 'handles': [968L]}}

    for ep in ep_data:
        src = dumps(ep["src"])
        dst = dumps(ep["dst"])
        trf = dumps(ep["traffic"]["id"])
        tp = dumps(ep["traffic"])
        cur_tp_map = handleTrafficProfile(tp, src, dst, topo_data, np_map)
        tp_map.update(cur_tp_map)

        plLogger.LogInfo("src: " + str(src))
        plLogger.LogInfo("dst: " + str(dst))
        plLogger.LogInfo("trf: " + str(trf))

    plLogger.LogInfo("handle_endpoints: end")
    return tp_map


def expand(topo_map, tp_map, np_map):
    # topo_map:
    # {'name_list': ['West', 'East'],
    #  '374343123': {'subnet_list': [('2345', [{'id': '4001', 'location': '//1.0.0.2/1/1'}])],
    #  'name': 'East'},
    #  '83749364': {'subnet_list': [('1234', [{'id' :'4000', 'location': '//1.0.0.1/1/1'}])],
    #  'name': 'West'}}

    # ep_data: [{u'src': u'East', u'dst': u'West', u'traffic': {...}},
    #           {u'src': u'West', u'East': u'374343123', u'traffic': {...}}]
    # tp_map: {'2468': 664L, '1357': 658L}
    #         {'1234': {'ep_tag': 'net1ttIpv4If', 'handle': 960L},
    #          '2345': {'ep_tag': 'net2ttIpv4If', 'handle': 968L}}

    # Expand the traffic mixes
    for tp_subnet in tp_map.values():
        expand_util.expand_traffic_mix_group(tp_subnet)


def reset():
    return True


# Convert unicode to string
def dumps(data):
    if type(data) == unicode:
        return str(data)
    if type(data) == list:
        return [dumps(item) for item in data]
    if type(data) == dict:
        ret = {}
        for key, value in data.iteritems():
            new_key = dumps(key)
            new_val = dumps(value)
            ret[new_key] = new_val
        return ret
    return data
