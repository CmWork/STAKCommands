from StcIntPythonPL import *
from .. import tag_name_util
import config_utils


plLogger = PLLogger.GetLogger("eth_builder")


def handle_physical_interface_mac(template_config, subnet):
    tag_name = tag_name_util.get_ethIIIf_tag(subnet)
    property_value = {
        "className": "EthIIIf",
        "tagName": tag_name,
        "propertyValueList": {
            "UseDefaultPhyMac": "TRUE"
        }
    }
    property_value_list = config_utils.get_property_value_list(template_config)
    property_value_list.append(property_value)


def build_eth_config(subnet, template_config):
    plLogger.LogInfo("build_eth_config: ")

    config_utils.init_config(template_config)

    mac_port_step = None
    if subnet["mac_config"]["_type"] != "Profile::UniqueMacConfig":
        mac_port_step = subnet["mac_config"]["mac_port_step"]

    mac_config = subnet["mac_config"]
    dev_count = subnet["device_count_per_port"]
    if mac_config["_type"] == "Profile::UniqueMacConfig":
        if dev_count > 1:
            # randomize mac is handled outside of this command
            return
        else:
            handle_physical_interface_mac(template_config, subnet)
            return
    plLogger.LogInfo(str(mac_config))
    mac = str(mac_config["mac"])
    mac_step = str(mac_config["mac_step"])

    tag_name = tag_name_util.get_ethIIIf_tag(subnet)

    property_value = {
        "className": "EthIIIf",
        "tagName": tag_name,
        "propertyValueList": {
            "SrcMacStep": mac_step
        }
    }
    property_value_list = config_utils.get_property_value_list(template_config)
    property_value_list.append(property_value)

    stm_property_modifier = {
        "className": "EthIIIf",
        "tagName": tag_name + ".SourceMac",
        "parentTagName": tag_name,
        "propertyName": "SourceMac",
        "propertyValueList": {
            "Start": mac,
            "Step": mac_port_step,
            "ResetOnNewTargetObject": False
        }
    }
    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    stm_property_modifier_list.append(stm_property_modifier)
