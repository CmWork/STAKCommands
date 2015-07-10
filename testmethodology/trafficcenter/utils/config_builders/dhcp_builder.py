from StcIntPythonPL import *
import config_utils
from .. import tag_name_util


plLogger = PLLogger.GetLogger("dhcp_builder")


def build_dhcp_config(subnet, template_config):
    plLogger.LogInfo("build_dhcp_config: ")

    if not subnet["dhcp_enabled"]:
        plLogger.LogInfo("dhcp disabled")
        return

    config_utils.init_config(template_config)
    tag_name = None
    dev_tag_name = tag_name_util.get_dev_tag(subnet)
    if subnet["ip_config"]["_type"] == "Profile::Ipv4Config":
        tag_name = tag_name_util.get_dhcpv4_tag(subnet)
    else:
        raise Exception("DHCP for Ipv6 is not supported")

    merge_list = config_utils.get_merge_list(template_config)
    merge_list.append(
        {
            "mergeSourceTemplateFile": "Access_Protocols.xml",
            "mergeSourceTag": tag_name,
            "mergeTargetTag": dev_tag_name
        }
    )

    if subnet["gateway_config"]["_type"] == "Profile::GatewayDhcpConfig":
        option_list = ["1", "3", "6", "15", "33", "44"]
        property_value = {
            "className": "Dhcpv4BlockConfig",
            "tagName": tag_name,
            "propertyValueList": {
                "OptionList": option_list,
                "EnableRouterOption": "TRUE"
            }
        }
        property_value_list = config_utils.get_property_value_list(
            template_config
        )
        property_value_list.append(property_value)
