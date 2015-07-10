from StcIntPythonPL import *
from utils import json_util
from utils import hardware_util
from utils import mac_util


plLogger = PLLogger.GetLogger("AdjustMacCommand")


def validate(TopologyConfig):
    return ''


def run(TopologyConfig):
    topology_nodes = json_util.loads(TopologyConfig)
    for topology_node in topology_nodes:
        subnet_configs = topology_node["subnet_configs"]
        for subnet_config in subnet_configs:
            subnet = subnet_config["subnet"]
            mac_config = subnet["mac_config"]
            mac_config_type = mac_config["_type"]
            if mac_config_type == "Profile::UniqueMacConfig":
                if subnet["device_count_per_port"] == 1:
                    handle_physical_interface(subnet_config)
                elif subnet["device_count_per_port"] > 1:
                    handle_randomize_mac(subnet_config)
                else:
                    raise Exception("invalid device_count_per_port")
    return True


def handle_randomize_mac(subnet_config):
    mac_util.randomize_source_mac(subnet_config["subnet"])


def search_ports(location):
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")
    ports = project.GetObjects("Port")
    return [port.GetObjectHandle() for port in ports if port.Get("Location") == location]


def handle_physical_interface(subnet_config):
    ports = subnet_config["ports"]
    vport_list = []
    hport_list = []
    for port in ports:
        ip = hardware_util.split_port_location(
            port["location"]
        )[0]
        if hardware_util.is_virtual(ip):
            found = search_ports(port["location"])
            if found is None or len(found) == 0:
                raise Exception("Cannot find port %s" % port["location"])
            port_hnd = found[0]
            vport_list.append(port_hnd)
        else:
            hport_list.append(port)
    if len(vport_list) > 0:
        mac_util.detect_source_mac(vport_list)
    if len(hport_list) > 0:
        subnet_config["ports"] = hport_list
        handle_randomize_mac(subnet_config)


def reset():
    return True
