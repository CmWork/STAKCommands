from StcIntPythonPL import *
import math
import json
import spirent.core.utils.IfUtils as if_utils
import data_model_utils as dm_utils
import json_utils


# Does range modification over copies of the template
def apply_range_modifier(container, modifier_ele):
    plLogger = PLLogger.GetLogger("methodology")

    if container is None:
        return "template_processing_functions.apply_range_modifier " + \
            "requires an StmTemplateConfig.  Received invalid element (None)."
    if not container.IsTypeOf("StmTemplateConfig"):
        return "template_processing_functions.apply_range_modifier " + \
            "requires an StmTemplateConfig.  Received an object of type: " + \
            container.GetType() + "."
    if modifier_ele is None:
        return "template_processing_functions.apply_range_modifier " + \
            "requires an ElementTree modifier_ele (ModifierInfo).   " + \
            "Received invalid element (None)."

    tag_name = modifier_ele.get("TagName")
    md_json = modifier_ele.get("ModifierInfo")

    if tag_name is None:
        return "TagName attribute is required in the ModifierInfo"
    if md_json is None:
        err_str = "ModifierInfo is required in the StmPropertyModifier: " + \
            str(modifier_ele)
        return err_str

    # Validate the ModifierInfo against the schema
    res = json_utils.validate_json(md_json,
                                   get_range_modifier_json_schema())
    if res != "":
        err_str = "ModifierInfo JSON is invalid or does not conform " + \
            "to the schema: " + res
        return err_str

    # Load the JSON
    err_str, md_dict = json_utils.load_json(md_json)
    if err_str != "":
        return err_str
    plLogger.LogDebug("md_dict: " + str(md_dict))

    obj_name = md_dict.get("objectName")
    prop_name = md_dict.get("propertyName")
    if not CMeta.ClassExists(obj_name):
        err_str = "Class " + obj_name + " does not exist."
        return err_str
    if prop_name not in CMeta.GetProperties(obj_name):
        err_str = "Property " + prop_name + " does not exist on " + \
            obj_name
        return err_str
    # prop_range = CMeta.GetPropertyRange(obj_name, prop_name)
    is_collection = dm_utils.is_property_collection(obj_name, prop_name)

    plLogger.LogDebug("obj_name: " + obj_name)
    plLogger.LogDebug("prop_name: " + prop_name)

    # Determine the property type
    prop_dict = CMeta.GetPropertyMeta(obj_name, prop_name)
    plLogger.LogDebug("prop_dict: " + str(prop_dict))
    prop_type = prop_dict["type"]

    # Process the propertyValueDict
    prop_val_dict = md_dict.get("propertyValueDict", {})

    # start (required)
    start = prop_val_dict["start"]
    if isinstance(start, basestring):
        start_list = [start]
    else:
        start_list = start

    # Truncate the list of start values based on whether the
    # property is a collection.
    if not is_collection:
        start_list = [start_list[0]]

    # Count for all lists will depend on how many items are
    # in the start_list
    count = len(start_list)

    # step (required)
    step = prop_val_dict["step"]
    if isinstance(step, basestring):
        step_list = [step]
    else:
        step_list = step

    # repeat
    repeat = prop_val_dict.get("repeat", None)
    if repeat is None:
        repeat = [0]
    if isinstance(repeat, int):
        repeat_list = [repeat]
    else:
        repeat_list = repeat

    # recycle
    recycle = prop_val_dict.get("recycle", None)
    if recycle is None:
        recycle = [0]
    if isinstance(recycle, int):
        recycle_list = [recycle]
    else:
        recycle_list = recycle

    # targetObjectStep (use default value if nothing specified)
    target_step = prop_val_dict.get("targetObjectStep", None)
    if target_step is None:
        err_str, zero_val = get_zero_value(prop_type)
        if err_str != "":
            plLogger.LogWarn(err_str)
        target_step = [str(zero_val)]
    if isinstance(target_step, basestring):
        target_step_list = [target_step]
    else:
        target_step_list = target_step

    # Default for reset is True
    reset = prop_val_dict.get("resetOnNewTargetObject", True)

    # Turn everything into lists and even them out based on start_list
    # prop_type takes precedence unless the required list/scalar is
    # unspecified.
    # len(start_list) determines list length; shorter lists will be
    # extended.  Longer lists will be truncated.
    # (start_list and start are processed above)
    step_list = build_range_parameter_list(is_collection,
                                           step_list, count=count)
    repeat_list = build_range_parameter_list(is_collection,
                                             repeat_list, count=count)
    recycle_list = build_range_parameter_list(is_collection,
                                              recycle_list, count=count)
    target_step_list = build_range_parameter_list(is_collection,
                                                  target_step_list,
                                                  count=count)
    # Check the values
    for val in start_list:
        res = check_value_type(prop_type, val)
        if res != "":
            return "Invalid value " + str(val) + \
                " in start: " + res
    for val in step_list:
        res = check_value_type(prop_type, val)
        if res != "":
            return "Invalid value " + str(val) + \
                " in step: " + res
    for val in target_step_list:
        res = check_value_type(prop_type, val)
        if res != "":
            return "Invalid value " + str(val) + \
                " in targetObjectStep: " + res

    plLogger.LogDebug("count: " + str(count))
    plLogger.LogDebug("is_collection: " + str(is_collection))
    plLogger.LogDebug("start_list: " + str(start_list))
    plLogger.LogDebug("step_list: " + str(step_list))
    plLogger.LogDebug("repeat_list: " + str(repeat_list))
    plLogger.LogDebug("recycle_list: " + str(recycle_list))
    plLogger.LogDebug("target_step_list: " + str(target_step_list))
    plLogger.LogDebug("reset: " + str(reset))

    target_dict = get_modify_objects(container, obj_name, tag_name)
    if target_dict == {}:
        plLogger.LogWarn("No objects to modify")
        return ""

    if prop_type == "u8" or \
       prop_type == "u16" or \
       prop_type == "u32" or \
       prop_type == "u64":
        handle_uint_range_update(
            target_dict, start_list, step_list, repeat_list,
            recycle_list, target_step_list, reset,
            obj_name, prop_name)
    elif prop_type == "ip" or prop_type == "ipv6":
        handle_ip_range_update(
            target_dict, start_list, step_list, repeat_list,
            recycle_list, target_step_list, reset,
            obj_name, prop_name)
    elif prop_type == "mac":
        handle_mac_range_update(
            target_dict, start_list, step_list, repeat_list,
            recycle_list, target_step_list, reset,
            obj_name, prop_name)
    else:
        return "Unsupported property type: " + prop_type + \
            ".  Please fix the template_processing_functions." + \
            "apply range modifier."
    return ""


def get_zero_value(prop_type):
    if prop_type == "u8" or \
       prop_type == "u16" or \
       prop_type == "u32" or \
       prop_type == "u64":
        return "", 0
    elif prop_type == "ip":
        return "", "0.0.0.0"
    elif prop_type == "ipv6":
        return "", "0::0"
    elif prop_type == "mac":
        return "", "00:00:00:00:00:00"

    # Unsupported type
    err_str = "Unsupported property type: " + prop_type + \
        ".  Please fix the template_processing_functions." + \
        "get_zero_value.  Returning 0."
    return err_str, 0


def check_value_type(prop_type, val):
    if prop_type == "u8" or prop_type == "u16" or \
       prop_type == "u32" or prop_type == "u64":
        try:
            val = int(val)
        except:
            return "Value " + str(val) + " is invalid for prop_type " + \
                prop_type
        min = 0
        if prop_type == "u8":
            max = pow(2, 8) - 1
        elif prop_type == "u16":
            max = pow(2, 16) - 1
        elif prop_type == "u32":
            max = pow(2, 32) - 1
        elif prop_type == "u64":
            max = pow(2, 64) - 1
        if val < min or val > max:
            return "Value " + str(val) + " is invalid for prop_type " + \
                prop_type + ".  Valid values are between " + str(min) + \
                " and " + str(max) + " inclusive."
    elif prop_type == "ip":
        if not if_utils.IsValidIpv4(val):
            return "Value " + str(val) + " is invalid for prop_type ip.  " + \
                "Value should be a valid IP address."
    elif prop_type == "ipv6":
        if not if_utils.IsValidIpv6(val):
            return "Value " + str(val) + " is invalid for prop_type ipv6.  " + \
                "Value should be a valid IPv6 address."
    elif prop_type == "mac":
        if not if_utils.IsValidMac(val):
            return "Value " + str(val) + " is invalid for prop_type mac.  " + \
                "Value should be a valid (colon delimited) MAC address."
    else:
        return "prop_type: " + prop_type + " is not yet supported.  " + \
            "Fix template_processing_functions.check_value_type"
    return ""


def get_modify_objects(tmpl, obj_name, tag_name):
    # Find the stuff attached to the template
    # Filter based on object and tag
    plLogger = PLLogger.GetLogger("methodology")
    gen_obj_list = tmpl.GetObjects("Scriptable",
                                   RelationType("GeneratedObject"))
    plLogger.LogDebug("gen_obj_list contains: " + str(len(gen_obj_list)))

    # Filter and sort the objects based on the target.
    # Normally this is based on the parent (target) of the generated
    # object except for the case of the EmulatedDevice.
    # For objects of type EmulatedDevice, the parent is Project
    # and this function will sort based on the AffiliationPort.
    target_obj_dict = {}
    for gen_obj in gen_obj_list:
        # Find the target object
        parent = None
        if gen_obj.IsTypeOf("EmulatedDevice"):
            parent = gen_obj.GetObject(
                "Port", RelationType("AffiliationPort"))
            if parent is None:
                # Use the parent (probably project1)
                parent = gen_obj.GetParent()
        else:
            parent = gen_obj.GetParent()
        if parent is None:
            # Only StcSystem should ever fall through here
            plLogger.LogWarn("Skipping modification of " +
                             gen_obj.Get("Name") + " as it has " +
                             "no valid parent.")
            continue
        parent_hnd = parent.GetObjectHandle()

        # Use ProcessInputHandleVec to find the objects of interest
        gen_hnd = gen_obj.GetObjectHandle()
        filtered_obj_list = CCommandEx.ProcessInputHandleVec(obj_name,
                                                             [gen_hnd])
        plLogger.LogDebug("filtered_obj_list contains: " +
                          str(len(filtered_obj_list)))

        filtered_tagged_obj_list = []
        for filtered_obj in filtered_obj_list:
            tag_list = filtered_obj.GetObjects("Tag", RelationType("UserTag"))
            for tag in tag_list:
                if tag is None or tag.Get("Name") != tag_name:
                    continue
                filtered_tagged_obj_list.append(filtered_obj)
        plLogger.LogDebug("filtered_tagged_obj_list contains: " +
                          str(len(filtered_tagged_obj_list)))
        if len(filtered_tagged_obj_list):
            if parent_hnd not in target_obj_dict.keys():
                target_obj_dict[parent_hnd] = []
            target_obj_dict[parent_hnd].extend(filtered_tagged_obj_list)

    # Generated objects will be sorted by their handle.
    for key in target_obj_dict.keys():
        s_obj_list = target_obj_dict[key]
        hnd_dict = {}
        for s_obj in s_obj_list:
            hnd_dict[s_obj.GetObjectHandle()] = s_obj

        # Sort on handles
        sorted_hnd_list = sorted(hnd_dict)

        # Rebuild the target_obj_dict
        target_obj_dict[key] = [hnd_dict[hnd] for hnd in sorted_hnd_list]
    return target_obj_dict


def build_range_parameter_list(is_collection, list_param, count=1):
    ret_list = []
    if is_collection:
        if len(list_param) > count:
            ret_list = list_param[0:count]
        elif len(list_param) < count:
            rep_count = int(math.ceil(count * 1.0 / len(list_param)))
            ret_list = (list_param * rep_count)[0:count]
        else:
            ret_list = list_param
    else:
        ret_list = [list_param[0]]
    return ret_list


def handle_uint_range_update(target_dict, start_list, step_list,
                             repeat_list, recycle_list,
                             target_step_list, reset,
                             obj_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug(" process unsigned integer...")
    plLogger.LogDebug("  object: " + obj_name + "   property: " + prop_name)

    # Hack due to CMeta.GetPropertyRange("EmulatedDevice", "DeviceCount")
    # failing due to an invalid cast from hex (boost::lexical_cast<int>
    # is failing due to hex input).
    try:
        prop_range = CMeta.GetPropertyRange(obj_name, prop_name)
    except:
        prop_range = None
    is_collection = dm_utils.is_property_collection(obj_name, prop_name)
    plLogger.LogDebug("  prop_range: " + str(prop_range))
    plLogger.LogDebug("  is_collection: " + str(is_collection))

    pattern_iter = 0
    target_count = 0

    # Make a distinct COPY of start_list into curr_start_list so that
    # the curr_start_list doesn't change each time start_list does.
    # curr_start_list is used to keep track of the starting values
    # for a particular target object given reset and target_step_list.
    curr_start_list = list(start_list)

    for target_key in sorted(target_dict):
        curr_mod_obj_list = target_dict[target_key]
        if reset:
            # Reset the pattern generator
            pattern_iter = 0

        # Update start_list with target_step_list
        start_iter = 0
        for start, target_step in zip(curr_start_list, target_step_list):
            start_list[start_iter] = str(int(start) +
                                         int(target_step) * target_count)
            start_iter = start_iter + 1
        plLogger.LogDebug("curr_start_list: " + str(curr_start_list))
        plLogger.LogDebug("start_list: " + str(start_list))
        plLogger.LogDebug("target_count: " + str(target_count))
        plLogger.LogDebug("target_step_list: " + str(target_step_list))

        # Iterate over the objects to be modified (per target object)
        for mod_obj in curr_mod_obj_list:
            list_pos = 0
            val_list = []

            # Iterate over the elements in the start_list (list_pos)
            for start in start_list:
                int_list = if_utils.expand_int_pattern(
                    pattern_iter, 1,
                    int(start_list[list_pos]),
                    int(step_list[list_pos]),
                    int(repeat_list[list_pos]),
                    int(recycle_list[list_pos]))
                plLogger.LogDebug(" setting next int to: " + str(int_list[0]))
                num = int_list[0]
                if prop_range is not None:
                    min_val, max_val = prop_range[0], prop_range[1]
                    if num < min_val or num > max_val:
                        num = min_val + \
                            (num - min_val) % (max_val - min_val + 1)
                val_list.append(num)
                list_pos = list_pos + 1
            if is_collection is True:
                mod_obj.SetCollection(prop_name, val_list)
            else:
                mod_obj.Set(prop_name, val_list[0])
            pattern_iter = pattern_iter + 1
        target_count = target_count + 1


def handle_ip_range_update(target_dict, start_list, step_list,
                           repeat_list, recycle_list,
                           target_step_list, reset,
                           obj_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug(" process ip...")
    plLogger.LogDebug("  object: " + obj_name + "   property: " + prop_name)

    is_collection = dm_utils.is_property_collection(obj_name, prop_name)
    plLogger.LogDebug("  is_collection: " + str(is_collection))

    pattern_iter = 0
    target_count = 0

    # Make a distinct COPY of start_list into curr_start_list so that
    # the curr_start_list doesn't change each time start_list does.
    # curr_start_list is used to keep track of the starting values
    # for a particular target object given reset and target_step_list.
    curr_start_list = list(start_list)

    for target_key in sorted(target_dict):
        curr_mod_obj_list = target_dict[target_key]
        if reset:
            # Reset the pattern generator
            pattern_iter = 0

        # Update start_list with target_step_list
        start_iter = 0
        for start, target_step in zip(curr_start_list, target_step_list):
            start_list[start_iter] = if_utils.expand_ip_pattern(
                target_count, 1, str(start), str(target_step), 0, 0)[0]
            start_iter = start_iter + 1
        plLogger.LogDebug("curr_start_list: " + str(curr_start_list))
        plLogger.LogDebug("start_list: " + str(start_list))
        plLogger.LogDebug("target_count: " + str(target_count))
        plLogger.LogDebug("target_step_list: " + str(target_step_list))

        # Iterate over the objects to be modified (per target object)
        for mod_obj in curr_mod_obj_list:
            list_pos = 0
            val_list = []

            # Iterate over the elements in the start_list (list_pos)
            for start in start_list:
                ip_list = if_utils.expand_ip_pattern(
                    pattern_iter, 1,
                    start_list[list_pos],
                    step_list[list_pos],
                    int(repeat_list[list_pos]),
                    int(recycle_list[list_pos]))
                plLogger.LogDebug(" setting next ip to: " + str(ip_list[0]))
                val_list.append(ip_list[0])
                list_pos = list_pos + 1
            if is_collection is True:
                mod_obj.SetCollection(prop_name, val_list)
            else:
                mod_obj.Set(prop_name, val_list[0])
            pattern_iter = pattern_iter + 1
        target_count = target_count + 1


def handle_mac_range_update(target_dict, start_list, step_list,
                            repeat_list, recycle_list,
                            target_step_list, reset,
                            obj_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug(" process mac...")
    plLogger.LogDebug("  object: " + obj_name + "   property: " + prop_name)

    is_collection = dm_utils.is_property_collection(obj_name, prop_name)
    plLogger.LogDebug("  is_collection: " + str(is_collection))

    pattern_iter = 0
    target_count = 0

    # Make a distinct COPY of start_list into curr_start_list so that
    # the curr_start_list doesn't change each time start_list does.
    # curr_start_list is used to keep track of the starting values
    # for a particular target object given reset and target_step_list.
    curr_start_list = list(start_list)

    for target_key in sorted(target_dict):
        curr_mod_obj_list = target_dict[target_key]
        if reset:
            # Reset the pattern generator
            pattern_iter = 0

        # Update start_list with target_step_list
        start_iter = 0
        for start, target_step in zip(curr_start_list, target_step_list):
            start_list[start_iter] = if_utils.expand_mac_pattern(
                target_count, 1, str(start), str(target_step), 0, 0)[0]
            start_iter = start_iter + 1

        # Iterate over the objects to be modified (per target object)
        for mod_obj in curr_mod_obj_list:
            list_pos = 0
            val_list = []

            # Iterate over the elements in the start_list (list_pos)
            for start in start_list:
                mac_list = if_utils.expand_mac_pattern(
                    pattern_iter, 1,
                    start_list[list_pos],
                    step_list[list_pos],
                    int(repeat_list[list_pos]),
                    int(recycle_list[list_pos]))
                plLogger.LogDebug(" setting next mac to: " + str(mac_list[0]))
                val_list.append(mac_list[0])
                list_pos = list_pos + 1
            if is_collection is True:
                mod_obj.SetCollection(prop_name, val_list)
            else:
                mod_obj.Set(prop_name, val_list[0])
            pattern_iter = pattern_iter + 1
        target_count = target_count + 1


def get_range_modifier_json_schema():

    info = {}
    info["objectName"] = "Name of the object type that contains " + \
        "the property to be modified."
    info["propertyName"] = "Name of the property to be modified."
    info["modifierType"] = "Type of modifier to apply.  Currently, " + \
        "only RANGE is supported."
    info["propertyValueDict"] = "Properties specific to the type " + \
        "of modifier being applied."
    info["start"] = "Scalar start value or list of start values.  " + \
        "When a list is used, the number of values in the list " + \
        "indicate how long the generated list will be."
    info["step"] = "Scalar step value or list of step values.  " + \
        "When a list is specified, these are applied to elements " + \
        "in the same index in the start list.  If there are not " + \
        "enough values, the values are repeated."
    info["repeat"] = "Scalar repeat value or list of repeat values.  " + \
        "When a list is specified, these are applied to elements " + \
        "in the same index in the start list.  If there are not " + \
        "enough values, the values are repeated."
    info["recycle"] = "Scalar repeat value or list of repeat values.  " + \
        "When a list is specified, these are applied to elements " + \
        "in the same index in the start list.  If there are not " + \
        "enough values, the values are repeated."
    info["targetObjectStep"] = "Scalar target object step value or " + \
        "list of target object step values.  This step will be applied " + \
        "when a new target (usually parent) object of the objects " + \
        "being modified is encountered.  Usually used with " + \
        "resetOnNewTargetObject.  When a list is specified, these " + \
        "are applied to elements in the same index in the " + \
        "start list.  If there are not enough values, the values " + \
        "are repeated."
    info["resetOnNewTargetObject"] = "Reset the start value each time " + \
        "a new target (usually parent) object of the objects being " + \
        "modified is encountered."

    schema_str = """
{
  "title": "Schema for range-type ModifierInfo of the StmPropertyModifier.",
  "type": "object",
  "properties": {
    "objectName": {
      "type": "string"
    },
    "propertyName": {
      "type": "string"
    },
    "modifierType": {
      "enum": [
        "RANGE"
      ]
    },
    "propertyValueDict": {
      "type": "object",
      "properties": {
        "start": {
          "oneOf": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          ]
        },
        "step": {
          "oneOf": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          ]
        },
        "repeat": {
          "oneOf": [
            {
              "type": "integer"
            },
            {
              "type": "array",
              "items": {
                "type": "integer"
              }
            }
          ]
        },
        "recycle": {
          "oneOf": [
            {
              "type": "integer"
            },
            {
              "type": "array",
              "items": {
                "type": "integer"
              }
            }
          ]
        },
        "targetObjectStep": {
          "oneOf": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          ]
        },
        "resetOnNewTargetObject": {
          "type": "boolean"
        }
      },
      "required": [
        "start",
        "step"
      ]
    }
  },
  "required": [
    "objectName",
    "propertyName",
    "modifierType",
    "propertyValueDict"
  ]
}
"""
    err_str, j_schema = json_utils.load_json(schema_str)
    prop_dict = j_schema["properties"]
    for key in ["propertyName", "objectName", "modifierType",
                "propertyValueDict"]:
        prop_dict[key]["description"] = info[key]
    pv_prop_dict = prop_dict["propertyValueDict"]["properties"]
    for key in ["start", "step", "repeat", "recycle",
                "targetObjectStep", "resetOnNewTargetObject"]:
        pv_prop_dict[key]["description"] = info[key]
    return json.dumps(j_schema)
