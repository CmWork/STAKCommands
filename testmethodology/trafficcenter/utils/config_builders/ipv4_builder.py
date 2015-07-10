from StcIntPythonPL import *
from .. import tag_name_util
import config_utils


plLogger = PLLogger.GetLogger("ipv4_builder")


def process_gateway_arp_config(subnet, template_config, gw_port_step):
    ipv4_tag = tag_name_util.get_ipv4If_tag(subnet)
    gateway_config = subnet["gateway_config"]
    gw_ip_config = gateway_config.get("ip_config")
    gw = str(gw_ip_config["ipv4"])
    stm_property_modifier = {
        "className": "Ipv4If",
        "tagName": ipv4_tag + ".Gateway",
        "parentTagName": ipv4_tag,
        "propertyName": "Gateway",
        "propertyValueList": {
            "Start": gw,
            "Step": gw_port_step,
            "ResetOnNewTargetObject": False
        }
    }
    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    stm_property_modifier_list.append(stm_property_modifier)


def process_gateway_mac_config(subnet,
                               template_config,
                               gw_mac_port_step):
    ipv4_tag = tag_name_util.get_ipv4If_tag(subnet)
    gateway_config = subnet["gateway_config"]
    gw_mac = str(gateway_config["mac"])
    stm_property_modifier = {
        "className": "Ipv4If",
        "tagName": ipv4_tag + ".GatewayMac",
        "parentTagName": ipv4_tag,
        "propertyName": "GatewayMac",
        "propertyValueList": {
            "Start": gw_mac,
            "Step": gw_mac_port_step,
            "ResetOnNewTargetObject": False
        }
    }
    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    stm_property_modifier_list.append(stm_property_modifier)


def build_ipv4_config(subnet, template_config):
    plLogger.LogInfo("build_ipv4_config: ")

    config_utils.init_config(template_config)

    gateway_type = subnet["gateway_config"]["_type"]
    ip_config = subnet["ip_config"]
    ipv4_port_step = ip_config["ipv4_port_step"]
    gateway_ipv4_port_step = None
    gateway_mac_port_step = None
    gateway_config = subnet["gateway_config"]
    if gateway_type == "Profile::GatewayArpConfig":
        gw_ip_config = gateway_config.get("ip_config")
        gateway_ipv4_port_step = gw_ip_config["ipv4_port_step"]
    elif gateway_type == "Profile::GatewayMacConfig":
        gateway_mac_port_step = gateway_config["mac_port_step"]
    gateway_config = subnet["gateway_config"]
    ip_config = subnet["ip_config"]
    gateway_type = gateway_config["_type"]
    gw_ip_config = gateway_config.get("ip_config")

    ipv4 = str(ip_config["ipv4"])
    ipv4_step = str(ip_config["ipv4_step"])
    prefix = str(ip_config["prefix"])
    pri = 0
    if "control_plane_priority" in ip_config:
        pri_str = str(ip_config["control_plane_priority"])
        if pri_str == "routine":
            pri = 0
        elif pri_str == "high":
            pri = 32
        else:
            pri = 0
    # Modify the Ipv4If parameters
    # Attach StmPropertyModifier objects to the Address and Gateway
    # fields.
    # Address
    tag_name = tag_name_util.get_ipv4If_tag(subnet)
    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    property_value_list = config_utils.get_property_value_list(template_config)

    ipv4_stm_property_modifier = {
        "className": "Ipv4If",
        "tagName": tag_name + ".Address",
        "parentTagName": tag_name,
        "propertyName": "Address",
        "propertyValueList": {
            "Start": ipv4,
            "Step": ipv4_port_step,
            "ResetOnNewTargetObject": False
        }
    }
    stm_property_modifier_list.append(ipv4_stm_property_modifier)

    # Gateway
    # Profile::GatewayDhcpConfig is handled in dhcp_builder
    if gateway_type == "Profile::GatewayArpConfig":
        process_gateway_arp_config(subnet,
                                   template_config,
                                   gateway_ipv4_port_step)
    elif gateway_type == "Profile::GatewayMacConfig":
        process_gateway_mac_config(subnet,
                                   template_config,
                                   gateway_mac_port_step)
    # Modify any other parameters not on the StmPropertyModifier
    ipv4_property_value = {
        "className": "Ipv4If",
        "tagName": tag_name,
        "propertyValueList": {
            "AddrStep": ipv4_step,
            "PrefixLength": prefix,
            "Tos": str(pri)
        }
    }
    if gateway_type == "Profile::GatewayArpConfig":
        gw_step = str(gw_ip_config["ipv4_step"])
        ipv4_property_value["propertyValueList"]["GatewayStep"] = gw_step
    elif gateway_type == "Profile::GatewayMacConfig":
        ipv4_property_value["propertyValueList"]["ResolveGatewayMac"] = "FALSE"
    property_value_list.append(ipv4_property_value)
