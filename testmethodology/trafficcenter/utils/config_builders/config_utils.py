def get_property_value_list(template_config):
    try:
        return (
            item["propertyValueList"] for item
            in template_config["modifyList"]
            if "propertyValueList" in item
        ).next()
    except:
        return None


def get_stm_property_modifier_list(template_config):
    try:
        return (
            item["stmPropertyModifierList"] for item
            in template_config["modifyList"]
            if "stmPropertyModifierList" in item
        ).next()
    except:
        return None


def get_add_object_list(template_config):
    try:
        return (
            item["addObjectList"] for item
            in template_config["modifyList"]
            if "addObjectList" in item
        ).next()
    except:
        return None


def get_relation_list(template_config):
    try:
        return (
            item["relationList"] for item
            in template_config["modifyList"]
            if "relationList" in item
        ).next()
    except:
        return None


def get_merge_list(template_config):
    try:
        return (
            item["mergeList"] for item
            in template_config["modifyList"]
            if "mergeList" in item
        ).next()
    except:
        return None


def init_config(template_config):
    if template_config.get("modifyList") is None:
        template_config["modifyList"] = [
            {"mergeList": []},
            {"addObjectList": []},
            {"propertyValueList": []},
            {"stmPropertyModifierList": []},
            {"relationList": []}
        ]
    if get_property_value_list(template_config) is None:
        template_config["modifyList"].append(
            {"propertyValueList": []}
        )
    if get_stm_property_modifier_list(template_config) is None:
        template_config["modifyList"].append(
            {"stmPropertyModifierList": []}
        )
    if get_add_object_list(template_config) is None:
        template_config["modifyList"].append(
            {"addObjectList": []}
        )
    if get_relation_list(template_config) is None:
        template_config["modifyList"].append(
            {"relationList": []}
        )
    if get_merge_list(template_config) is None:
        template_config["modifyList"].append(
            {"mergeList": []}
        )
