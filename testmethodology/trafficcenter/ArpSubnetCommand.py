from StcIntPythonPL import *
from utils import json_util
from spirent.methodology.utils import tag_utils
from spirent.core.utils.scriptable import AutoCommand
from utils import tag_name_util


plLogger = PLLogger.GetLogger("ArpSubnetCommand")


def get_streamblocks(subnet):
    tag_prefix = tag_name_util.get_subnet_tag_prefix(subnet)
    tag_name = tag_prefix + tag_name_util.get_dev_tag(subnet)
    devices = tag_utils.get_tagged_objects_from_string_names(
        [tag_name]
        )
    streamblock_hnds = []
    for device in devices:
        ip_if = device.GetObject("NetworkInterface", RelationType("TopLevelIf"))
        streamblocks = ip_if.GetObjects("StreamBlock",
                                        RelationType.ReverseDir("SrcBinding"))
        streamblock_hnds += [streamblock.GetObjectHandle() for streamblock
                             in streamblocks]
    return streamblock_hnds


def validate(TopologyConfig):
    return ''


def run_arp(streamblocks_to_arp):
    with AutoCommand("ArpNdStartCommand") as arp_cmd:
        arp_cmd.SetCollection("HandleList", streamblocks_to_arp)
        arp_cmd.Execute()
    with AutoCommand("ArpNdUpdateArpCacheCommand") as arp_update_cmd:
        arp_update_cmd.Execute()


def run(TopologyConfig):
    topology_nodes = json_util.loads(TopologyConfig)
    streamblocks_to_arp = []
    for topology_node in topology_nodes:
        subnet_configs = topology_node["subnet_configs"]
        for subnet_config in subnet_configs:
            subnet = subnet_config["subnet"]
            gateway_config = subnet["gateway_config"]
            gateway_config_type = gateway_config["_type"]
            if gateway_config_type == "Profile::GatewayArpConfig":
                streamblocks = get_streamblocks(subnet)
                streamblocks_to_arp += streamblocks
    streamblocks_to_arp = list(set(streamblocks_to_arp))
    if len(streamblocks_to_arp) > 0:
        run_arp(streamblocks_to_arp)
    return True


def reset():
    return True
