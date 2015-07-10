from StcIntPythonPL import *
import config_utils
from .. import tag_name_util


plLogger = PLLogger.GetLogger("vlan_builder")


def handle_vlan_id_range_modifier(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    vlan_id = str(vlan_config["vlan_id"])
    vlan_id_step = vlan_config["vlan_id_step"]
    repeat_mode = vlan_config["vlan_id_repeat"]
    priority = str(vlan_config["priority"])
    ips_per_vlan = vlan_config["ips_per_vlan"]
    device_count = subnet["device_count_per_port"]

    add_object = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "vlanIf",
        "propertyValueList": {
            "IdStep": str(vlan_id_step),
            "Priority": priority,
            "IdRepeatCount": str(ips_per_vlan - 1)
        }
    }
    add_object_list = config_utils.get_add_object_list(template_config)
    add_object_list.append(add_object)
    vlan_port_step = 0
    if repeat_mode == "off":
        vlan_port_step = (
            int(device_count) // int(ips_per_vlan)
        ) * vlan_id_step

    stm_property_modifier = {
        "className": "VlanIf",
        "tagName": "vlanIf" + ".VlanId",
        "parentTagName": "vlanIf",
        "propertyName": "VlanId",
        "propertyValueList": {
            "Start": vlan_id,
            "Step": str(vlan_port_step),
            "ResetOnNewTargetObject": False
        }
    }
    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    stm_property_modifier_list.append(stm_property_modifier)


def handle_vlan_id_list_modifier(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    vlan_id = vlan_config["vlan_id"]
    vlan_id_step = vlan_config["vlan_id_step"]
    repeat_mode = vlan_config["vlan_id_repeat"]
    priority = str(vlan_config["priority"])
    ips_per_vlan = vlan_config["ips_per_vlan"]
    device_count = subnet["device_count_per_port"]

    current_id = vlan_id
    idx = 0
    total_idx = 0
    id_list = []
    while total_idx < device_count:
        if idx == ips_per_vlan:
            idx = 0
            current_id += vlan_id_step
        id_list.append(current_id)
        idx += 1
        total_idx += 1

    add_object = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "vlanIf",
        "propertyValueList": {
            "Priority": priority,
            "IsRange": "FALSE"
        }
    }
    add_object_list = config_utils.get_add_object_list(template_config)
    add_object_list.append(add_object)
    vlan_port_step = 0
    if repeat_mode == "off":
        vlan_port_step = current_id + vlan_id_step - vlan_id
    return (id_list, vlan_port_step)


def handle_qnq_vlan_range_modifier(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    outer_vlan_id = str(vlan_config["outer_vlan_id"])
    outer_vlan_id_step = vlan_config["outer_vlan_id_step"]
    outer_repeat_mode = str(vlan_config["outer_vlan_id_repeat"])
    outer_priority = str(vlan_config["outer_priority"])
    inner_vlan_id = str(vlan_config["inner_vlan_id"])
    inner_vlan_id_step = vlan_config["inner_vlan_id_step"]
    inner_repeat_mode = str(vlan_config["inner_vlan_id_repeat"])
    inner_priority = str(vlan_config["inner_priority"])
    ips_per_outer_vlan = vlan_config["ips_per_outer_vlan"]
    inner_vlans_per_outer_vlan = vlan_config["inner_vlans_per_outer_vlan"]
    device_count = subnet["device_count_per_port"]

    inner_repeat_count = (
        int(ips_per_outer_vlan) // int(inner_vlans_per_outer_vlan) - 1
    )
    inner_recycle_count = 0
    if inner_repeat_mode == "across_outer":
        inner_recycle_count = inner_vlans_per_outer_vlan - 1

    add_object_outer = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "outerVlan",
        "propertyValueList": {
            "IdStep": str(outer_vlan_id_step),
            "Priority": outer_priority,
            "IdRepeatCount": str(ips_per_outer_vlan - 1)
        }
    }
    add_object_inner = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "innerVlan",
        "propertyValueList": {
            "IdStep": str(inner_vlan_id_step),
            "Priority": inner_priority,
            "IdRepeatCount": str(inner_repeat_count),
            "IfRecycleCount": str(inner_recycle_count)
        }
    }

    add_object_list = config_utils.get_add_object_list(template_config)
    add_object_list.append(add_object_outer)
    add_object_list.append(add_object_inner)

    outer_port_step = 0
    inner_port_step = 0
    if outer_repeat_mode == "off":
        outer_port_step = (
            int(device_count) // int(ips_per_outer_vlan)
        ) * int(outer_vlan_id_step)
    if inner_repeat_mode == "off":
        inner_port_step = (
            int(device_count) // int(ips_per_outer_vlan)
        ) * int(inner_vlans_per_outer_vlan) * int(inner_vlan_id_step)

    stm_property_modifier_outer = {
        "className": "VlanIf",
        "tagName": "outerVlan" + ".VlanId",
        "parentTagName": "outerVlan",
        "propertyName": "VlanId",
        "propertyValueList": {
            "Start": outer_vlan_id,
            "Step": str(outer_port_step),
            "ResetOnNewTargetObject": False
        }
    }

    stm_property_modifier_inner = {
        "className": "VlanIf",
        "tagName": "innerVlan" + ".VlanId",
        "parentTagName": "innerVlan",
        "propertyName": "VlanId",
        "propertyValueList": {
            "Start": inner_vlan_id,
            "Step": str(inner_port_step),
            "ResetOnNewTargetObject": False
        }
    }

    stm_property_modifier_list = config_utils.get_stm_property_modifier_list(
        template_config
    )
    stm_property_modifier_list.append(stm_property_modifier_outer)
    stm_property_modifier_list.append(stm_property_modifier_inner)


def handle_qnq_vlan_list_modifier(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    outer_vlan_id = vlan_config["outer_vlan_id"]
    outer_vlan_id_step = vlan_config["outer_vlan_id_step"]
    outer_repeat_mode = str(vlan_config["outer_vlan_id_repeat"])
    outer_priority = str(vlan_config["outer_priority"])
    inner_vlan_id = vlan_config["inner_vlan_id"]
    inner_vlan_id_step = vlan_config["inner_vlan_id_step"]
    inner_repeat_mode = str(vlan_config["inner_vlan_id_repeat"])
    inner_priority = str(vlan_config["inner_priority"])
    ips_per_outer_vlan = vlan_config["ips_per_outer_vlan"]
    inner_vlans_per_outer_vlan = vlan_config["inner_vlans_per_outer_vlan"]
    device_count = subnet["device_count_per_port"]

    add_object_outer = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "outerVlan",
        "propertyValueList": {
            "Priority": outer_priority,
            "IsRange": "FALSE"
        }
    }
    add_object_inner = {
        "className": "VlanIf",
        "parentTagName": "ttEmulatedDevice",
        "tagName": "innerVlan",
        "propertyValueList": {
            "Priority": inner_priority,
            "IsRange": "FALSE"
        }
    }

    add_object_list = config_utils.get_add_object_list(template_config)
    add_object_list.append(add_object_outer)
    add_object_list.append(add_object_inner)

    outer_vlan_list = []
    current_outer_vlan = outer_vlan_id
    i = 0
    while i < device_count:
        j = 0
        while j < ips_per_outer_vlan and i < device_count:
            outer_vlan_list.append(current_outer_vlan)
            i += 1
            j += 1
        current_outer_vlan += outer_vlan_id_step
    inners_per_ip = int(ips_per_outer_vlan) // int(inner_vlans_per_outer_vlan)
    extra_inners = int(ips_per_outer_vlan) % int(inner_vlans_per_outer_vlan)

    i = 0
    current_inner_vlan = inner_vlan_id
    inner_vlan_list = []
    while i < device_count:
        j = 0
        while j < ips_per_outer_vlan and i < device_count:
            k = 0
            while (
                k < inner_vlans_per_outer_vlan and
                j < ips_per_outer_vlan and
                i < device_count
            ):
                l = 0
                repeat_cnt = inners_per_ip
                if k < extra_inners:
                    repeat_cnt = inners_per_ip + 1
                while (
                    l < repeat_cnt and
                    k < inner_vlans_per_outer_vlan and
                    j < ips_per_outer_vlan and
                    i < device_count
                ):
                    inner_vlan_list.append(current_inner_vlan)
                    i += 1
                    j += 1
                    l += 1
                k += 1
                current_inner_vlan += inner_vlan_id_step
        if inner_repeat_mode == "across_outer":
            current_inner_vlan = inner_vlan_id

    outer_port_step = 0
    inner_port_step = 0
    if outer_repeat_mode == "off":
        outer_port_step = current_outer_vlan - outer_vlan_id
    if inner_repeat_mode == "off":
        inner_port_step = current_inner_vlan - inner_vlan_id
    return (outer_vlan_list, inner_vlan_list, outer_port_step, inner_port_step)


def process_single_vlan(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    ips_per_vlan = vlan_config["ips_per_vlan"]
    device_count = subnet["device_count_per_port"]

    vlan_list_config = None
    if device_count < ips_per_vlan:
        raise Exception("invalid vlan config")

    # use range modifier if the vlan counts are good
    # this will prevent generating long list of vlan ids
    # if the counts do not fit range modifier, list modifier will be used
    if device_count % ips_per_vlan == 0:
        handle_vlan_id_range_modifier(subnet, template_config)
    else:
        (
            vlan_list,
            vlan_port_step
        ) = handle_vlan_id_list_modifier(subnet, template_config)
        vlan_list_config = {
            "type": "single",
            "vlan_list": vlan_list,
            "vlan_port_step": vlan_port_step
        }

    relations = [
        {
            "sourceTag": tag_name_util.get_ipv4If_tag(subnet),
            "targetTag": tag_name_util.get_ethIIIf_tag(subnet),
            "relationType": "StackedOnEndpoint",
            "removeRelation": True
        },
        {
            "sourceTag": "ttIpv4If",
            "targetTag": "vlanIf",
            "relationType": "StackedOnEndpoint"
        },
        {
            "sourceTag": "vlanIf",
            "targetTag": tag_name_util.get_ethIIIf_tag(subnet),
            "relationType": "StackedOnEndpoint"
        }
    ]

    relation_list = config_utils.get_relation_list(template_config)
    relation_list += relations
    return vlan_list_config


def process_qnq_vlan(subnet, template_config):
    vlan_config = subnet["vlan_config"]
    ips_per_outer_vlan = vlan_config["ips_per_outer_vlan"]
    inner_vlans_per_outer_vlan = vlan_config["inner_vlans_per_outer_vlan"]
    device_count = subnet["device_count_per_port"]

    vlan_list_config = None
    if (
        device_count < ips_per_outer_vlan or
        ips_per_outer_vlan < inner_vlans_per_outer_vlan
    ):
        raise Exception("invalid vlan config")

    # use range modifier if the vlan counts are good
    # this will prevent generating long list of vlan ids
    # if the counts do not fit range modifier, list modifier will be used
    if (
        device_count % ips_per_outer_vlan == 0 and
        ips_per_outer_vlan % inner_vlans_per_outer_vlan == 0
    ):
        handle_qnq_vlan_range_modifier(subnet, template_config)
    else:
        (
            outer_vlan_list,
            inner_vlan_list,
            outer_port_step,
            inner_port_step
        ) = handle_qnq_vlan_list_modifier(
            subnet,
            template_config
        )
        vlan_list_config = {
            "type": "qnq",
            "outer_vlan_list": outer_vlan_list,
            "inner_vlan_list": inner_vlan_list,
            "outer_port_step": outer_port_step,
            "inner_port_step": inner_port_step
        }

    relations = [
        {
            "sourceTag": tag_name_util.get_ipv4If_tag(subnet),
            "targetTag": tag_name_util.get_ethIIIf_tag(subnet),
            "relationType": "StackedOnEndpoint",
            "removeRelation": True
        },
        {
            "sourceTag": tag_name_util.get_ipv4If_tag(subnet),
            "targetTag": "innerVlan",
            "relationType": "StackedOnEndpoint"
        },
        {
            "sourceTag": "innerVlan",
            "targetTag": "outerVlan",
            "relationType": "StackedOnEndpoint"
        },
        {
            "sourceTag": "outerVlan",
            "targetTag": tag_name_util.get_ethIIIf_tag(subnet),
            "relationType": "StackedOnEndpoint"
        }
    ]

    relation_list = config_utils.get_relation_list(template_config)
    relation_list += relations
    return vlan_list_config


def build_vlan_config(subnet, template_config):
    plLogger.LogInfo("build_vlan_config: ")
    vlan_config = subnet["vlan_config"]
    vlan_type = vlan_config["_type"]
    if vlan_type == "Profile::NoVlanConfig":
        return None
    if vlan_type == "Profile::SingleVlanConfig":
        return process_single_vlan(subnet, template_config)
    elif vlan_type == "Profile::QnqVlanConfig":
        return process_qnq_vlan(subnet, template_config)
