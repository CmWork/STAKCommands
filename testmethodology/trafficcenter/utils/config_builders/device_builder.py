from .. import subnet_templates
from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import eth_builder
import ipv4_builder
import vlan_builder
import dhcp_builder
from .. import tag_name_util
import json
import config_utils
from spirent.methodology.utils import tag_utils


plLogger = PLLogger.GetLogger("device_builder")


def get_template_name(subnet):
    ip_config = subnet["ip_config"]
    if ip_config["_type"] == "Profile::Ipv4Config":
        return subnet_templates.TEMPLATE_LOOKUP["ipv4"]
    else:
        raise Exception("Error: subnet %s is not supported" % subnet["name"])


def create_config(subnet, template_name, tag_prefix):
    template_config = {}
    config_utils.init_config(template_config)
    template_config["baseTemplateFile"] = template_name
    template_config["tagPrefix"] = tag_prefix
    tag_name = tag_name_util.get_dev_tag(subnet)
    property_value = {
        "className": "EmulatedDevice",
        "tagName": tag_name,
        "propertyValueList": {
            "DeviceCount": str(subnet["device_count_per_port"])
        }
    }
    property_value_list = config_utils.get_property_value_list(template_config)
    property_value_list.append(property_value)
    return template_config


def patch_devices_with_vlan_list(vlan_list_config, tag_prefix):
    if vlan_list_config["type"] == "single":
        tag_name = tag_prefix + "vlanIf"
        vlans = tag_utils.get_tagged_objects_from_string_names(tag_name)
        vlan_list = vlan_list_config["vlan_list"]
        vlan_port_step = vlan_list_config["vlan_port_step"]
        for vlan in vlans:
            vlan.SetCollection("IdList", vlan_list)
            vlan_list = [vlan_id + vlan_port_step for vlan_id in vlan_list]
    elif vlan_list_config["type"] == "qnq":
        outer_tag_name = tag_prefix + "outerVlan"
        outer_vlans = tag_utils.get_tagged_objects_from_string_names(
            outer_tag_name
        )
        inner_tag_name = tag_prefix + "innerVlan"
        inner_vlans = tag_utils.get_tagged_objects_from_string_names(
            inner_tag_name
        )
        outer_vlan_list = vlan_list_config["outer_vlan_list"]
        inner_vlan_list = vlan_list_config["inner_vlan_list"]
        outer_port_step = vlan_list_config["outer_port_step"]
        inner_port_step = vlan_list_config["inner_port_step"]
        for vlan in outer_vlans:
            vlan.SetCollection("IdList", outer_vlan_list)
            outer_vlan_list = [vlan_id + outer_port_step for vlan_id
                               in outer_vlan_list]
        for vlan in inner_vlans:
            vlan.SetCollection("IdList", inner_vlan_list)
            inner_vlan_list = [vlan_id + inner_port_step for vlan_id
                               in inner_vlan_list]


def create_configs(subnet, topo_map):
    # topo_map:
    # {'name_list': ['West', 'East'],
    #  '374343123': {'subnet_list': [('2345', [{'id': '4001', 'location': '//1.0.0.2/1/1'}])],
    #  'name': 'East'},
    #  '83749364': {'subnet_list': [('1234', [{'id' :'4000', 'location': '//1.0.0.1/1/1'}])],
    #  'name': 'West'}}

    plLogger.LogInfo("create_config:")

    tag_prefix = tag_name_util.get_subnet_tag_prefix(subnet)
    # Find the tag name (in the topology_nodes structure)
    tag = ""
    for node_name in topo_map["name_list"]:
        for subnet_conf in topo_map[node_name]["subnet_list"]:
            if subnet_conf[0] == str(subnet["id"]):
                tag = str(node_name + "_" + subnet["name"] + "_" + subnet["id"])
                break
        if tag != "":
            break
    plLogger.LogInfo("tag name: " + tag)
    template_name = get_template_name(subnet)
    template_config = create_config(subnet, template_name, tag_prefix)
    eth_builder.build_eth_config(subnet, template_config)
    ipv4_builder.build_ipv4_config(subnet, template_config)
    vlan_list_config = None
    if subnet.get("vlan_config") is not None:
        vlan_list_config = vlan_builder.build_vlan_config(subnet,
                                                          template_config)
    if subnet["dhcp_enabled"]:
        dhcp_builder.build_dhcp_config(subnet, template_config)

    with AutoCommand(
        "spirent.methodology.CreateTemplateConfigCommand"
    ) as cmd:
        cmd.Set("InputJson", json.dumps(template_config))
        cmd.SetCollection("TargetTagList", [tag])
        cmd.Execute()
    if vlan_list_config is not None:
        patch_devices_with_vlan_list(vlan_list_config, tag_prefix)
    ipv4_if_tag = tag_prefix + tag_name_util.get_ipv4If_tag(subnet)
    return subnet["id"], ipv4_if_tag
