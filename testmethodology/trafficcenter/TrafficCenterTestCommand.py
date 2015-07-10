from StcIntPythonPL import *
import json
from spirent.core.utils.scriptable import AutoCommand


PKG = "spirent.methodology.trafficcenter"
PKG_CORE = "spirent.core"


def validate(TestConfig):
    return ''


def run(TestConfig):
    data = json.loads(TestConfig)
    plLogger = PLLogger.GetLogger("TrafficCenterTestCommand")
    plLogger.LogInfo("TestConfig: " + str(TestConfig))
    plLogger.LogInfo("config_data: " + str(data))
    topo_config = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_pattern = data["traffic_pattern"] if "traffic_pattern" in data else None
    traffic_profiles = get_traffic_profiles(data, traffic_pattern)
    endpoint_infos = data["endpoint_infos"]
    duration = data["duration"]

    configure_stc_system()
    createTestSequence(topo_config,
                       duration,
                       network_profiles,
                       traffic_profiles,
                       endpoint_infos)

    return True


def get_network_profiles(data):
    topo_nodes = data["topology_nodes"]
    nps = []
    for node in topo_nodes:
        node_nps = [np_config["subnet"] for np_config in node["subnet_configs"]]
        nps += node_nps
    return nps


def get_traffic_profiles(data, traffic_pattern):
    plLogger = PLLogger.GetLogger('get_traffic_profiles')
    ep_infos = data["endpoint_infos"]
    if len(ep_infos) == 2:
        tm1 = ep_infos[0]
        tm2 = ep_infos[1]
        # when 2 trafficmixes have identical id
        if tm1["traffic"]["id"] == tm2["traffic"]["id"]:
            plLogger.LogInfo("2 trafficmixes have same id.")
            index = 0
            for ep_info in ep_infos:
                ep_info["traffic"]["id"] = ep_info["traffic"]["id"] + str(index)
                index = index + 1

    if traffic_pattern is not None:
        for ep_info in ep_infos:
            ep_info["traffic"]["traffic_pattern"] = traffic_pattern

    return [ep_info["traffic"] for ep_info in ep_infos]


# Mock this to run unit tests
def getVirtualPorts():
    with AutoCommand(PKG_CORE + ".CreateAndReserveVirtualPortsCommand") as create_cmd:
        create_cmd.Set("User", "Sherlock")
        create_cmd.Execute()
        port_list = create_cmd.GetCollection("Ports")
    return port_list


def detachPorts(port_hnd_list):
    with AutoCommand("DetachPortsCommand") as detach_cmd:
        detach_cmd.SetCollection("PortList", port_hnd_list)
        detach_cmd.Execute()


# Mock this to run unit tests
def attachPorts(port_hnd_list):
    with AutoCommand("AttachPortsCommand") as attach_cmd:
        attach_cmd.SetCollection("PortList", port_hnd_list)
        attach_cmd.Set("AutoConnect", True)
        attach_cmd.Set("ContinueOnFailure", True)
        attach_cmd.Execute()


def isPortListEmpty(config):
    topo_nodes = dumps(config)
    if len(topo_nodes) == 0:
        return True
    for topo_node in topo_nodes:
        subnet_item_list = dumps(topo_node["subnet_configs"])
        for subnet_item in subnet_item_list:
            if "ports" in subnet_item.keys():
                port_item_list = dumps(subnet_item["ports"])
                if len(port_item_list) == 0:
                    return True
            else:
                return True
    return False


def disconnectPorts(config):
    detachPorts(attach_list)


def configure_stc_system():
    stcSys = CStcSystem.Instance()
    """ Setup Relese all ports on error to False
        Any port going offline will still stop the sequencer
        but FATAL error will not be thrown so client connection
        stay alive to get user error log.
    """
    project = stcSys.GetObject('project')
    portOptions = project.GetObject('PortOptions')
    portOptions.Set('ReleaseAllPortsOnError', False)

    sequencer = stcSys.GetObject("sequencer")
    sequencer.Set("ErrorHandler", "STOP_ON_ERROR")


def createTestSequence(topo_config,
                       duration,
                       network_profiles,
                       traffic_profiles,
                       endpoint_infos):
    stcSys = CStcSystem.Instance()
    cmd_list = []
    ctor = CScriptableCreator()

    reserve_cmd = ctor.CreateCommand(PKG + ".ReservePortsCommand")
    reserve_cmd.Set("TopologyConfig", json.dumps(topo_config))
    cmd_list.append(reserve_cmd.GetObjectHandle())

    cmd = ctor.CreateCommand(PKG + ".CreateTemplatesCommand")
    cmd.Set("TopologyConfig", json.dumps(topo_config))
    cmd.Set("NetworkProfileConfig", json.dumps(network_profiles))
    cmd.Set("TrafficProfileConfig", json.dumps(traffic_profiles))
    cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
    cmd_list.append(cmd.GetObjectHandle())

    adj_mac_cmd = ctor.CreateCommand(PKG + ".AdjustMacCommand")
    adj_mac_cmd.Set("TopologyConfig", json.dumps(topo_config))
    cmd_list.append(adj_mac_cmd.GetObjectHandle())

    bind_dhcp_cmd = ctor.CreateCommand(PKG + ".BindDhcpSubnetCommand")
    bind_dhcp_cmd.Set("TopologyConfig", json.dumps(topo_config))
    cmd_list.append(bind_dhcp_cmd.GetObjectHandle())

    arp_cmd = ctor.CreateCommand(PKG + ".ArpSubnetCommand")
    arp_cmd.Set("TopologyConfig", json.dumps(topo_config))
    cmd_list.append(arp_cmd.GetObjectHandle())

    set_duration_cmd = ctor.CreateCommand(PKG + ".SetTrafficDurationCommand")
    set_duration_cmd.Set("Duration", float(duration))
    cmd_list.append(set_duration_cmd.GetObjectHandle())

    tp_start_cmd = ctor.CreateCommand("GeneratorStartCommand")
    cmd_list.append(tp_start_cmd.GetObjectHandle())

    wait_tp_stop_cmd = ctor.CreateCommand("GeneratorWaitForStopCommand")
    wait_tp_stop_cmd.Set("WaitTimeout", float(duration) + 120)
    cmd_list.append(wait_tp_stop_cmd.GetObjectHandle())

    wait_delay_cmd = ctor.CreateCommand("WaitCommand")
    delay = 10
    wait_delay_cmd.Set("WaitTime", float(delay))
    cmd_list.append(wait_delay_cmd.GetObjectHandle())

    with AutoCommand("SequencerInsertCommand") as seq_insert_cmd:
        seq_insert_cmd.SetCollection("CommandList", cmd_list)
        seq_insert_cmd.Execute()

    # Move ReleasePortsCommand to UI, since Generating Report function still needs ports info
    # Remove DetachAndStopVirtualPortsCommand later
    group_cmd = stcSys.GetObject("SequencerGroupCommand")
    # release_dhcp_cmd = ctor.CreateCommand(PKG + ".ReleaseDhcpSubnetCommand")
    release_dhcp_cmd = ctor.Create(PKG + ".ReleaseDhcpSubnetCommand", group_cmd)
    release_dhcp_cmd.Set("TopologyConfig", json.dumps(topo_config))
    # cmd_list.append(release_dhcp_cmd.GetObjectHandle())
    group_cmd.SetCollection("CommandList", [release_dhcp_cmd.GetObjectHandle()])
    # plLogger.LogInfo("SequencerGroupCommand: " + str(group_cmd.GetObjectHandle()))
    # if is_port_list_empty:
    #    plLogger.LogInfo("---DetachAndStopVirtualPortsCommand")
    #    tear_down_cmd = ctor.Create("spirent.core.DetachAndStopVirtualPortsCommand", group_cmd)
    #    tear_down_cmd.Set("User", "meth-Sherlock")
    #    group_cmd.SetCollection("CommandList", [tear_down_cmd.GetObjectHandle()])
    # else:
    #    tear_down_cmd = ctor.Create(PKG + ".ReleasePortsCommand", group_cmd)
    #    group_cmd.SetCollection("CommandList", [tear_down_cmd.GetObjectHandle()])


def set_cmd_property(cmd, cmd_prop, config, config_input,
                     unicode_to_string=True):
    if config.get(config_input) is not None:
        if unicode_to_string is True:
            cmd.Set(cmd_prop, dumps(config[config_input]))
        else:
            cmd.Set(cmd_prop, json.dumps(config[config_input]))


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


def reset():
    return True
