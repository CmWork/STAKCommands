import traceback
from StcIntPythonPL import *
from utils import json_util
from spirent.methodology.utils import tag_utils
from spirent.core.utils.scriptable import AutoCommand
from utils import tag_name_util


def get_devices(subnet):
    tag_prefix = tag_name_util.get_subnet_tag_prefix(subnet)
    tag_name = tag_prefix + tag_name_util.get_dev_tag(subnet)
    devices = tag_utils.get_tagged_objects_from_string_names(
        [tag_name]
        )
    return [device.GetObjectHandle() for device in devices]


def validate(TopologyConfig):
    return ''


def run_dhcp(device_handle_list):
    with AutoCommand("Dhcpv4BindCommand") as dhcp_bind_cmd:
        dhcp_bind_cmd.SetCollection("BlockList", device_handle_list)
        dhcp_bind_cmd.Execute()
    with AutoCommand("Dhcpv4BindWaitCommand") as dhcp_cmd:
        dhcp_cmd.SetCollection("ObjectList", device_handle_list)
        dhcp_cmd.Execute()


def run(TopologyConfig):
    logger = _get_logger()
    cmd = _get_this_cmd()
    if cmd:
        cmd.Set('ErrorOnFailure', True)

    try:
        topology_nodes = json_util.loads(TopologyConfig)
        device_handle_list = []
        for topology_node in topology_nodes:
            subnet_configs = topology_node["subnet_configs"]
            for subnet_config in subnet_configs:
                subnet = subnet_config["subnet"]
                if subnet["dhcp_enabled"]:
                    devices = get_devices(subnet)
                    device_handle_list += devices
        device_handle_list = list(set(device_handle_list))
        if len(device_handle_list) > 0:
            run_dhcp(device_handle_list)
    except RuntimeError as e:
        logger.LogError(str(e))
        if cmd:
            cmd.Set("Status", str(e))
        return False
    except:
        logger.LogError("unhandled exception:" + traceback.format_exc())
        return False

    return True


def reset():
    return True


def _get_logger():
    return PLLogger.GetLogger("spirent.methodology.trafficcenter.BindDhcpSubnetCommand")


def _get_this_cmd():
    try:
        this_command = CHandleRegistry.Instance().Find(__commandHandle__)
    except NameError:
        return None
    return this_command
