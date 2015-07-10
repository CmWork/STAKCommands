from StcIntPythonPL import *
import json
import spirent.methodology.utils.json_utils as json_utils


# to be removed
def parse_interface_data(interface_dict, row_idx):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.processing_function_util.parse_interface_data')

    # Each object in the input dictionary corresponds to an
    # object in a list
    data_obj = {}

    # Validate the interface_dict against the schema
    res = json_utils.validate_json(json.dumps(interface_dict),
                                   get_iterface_dict_schema())
    if res != "":
        plLogger.LogError(res)
        return data_obj

    parent_tag_name = interface_dict["ParentTagName"]
    class_name = interface_dict["ClassName"]
    main_prop_val_list = []
    main_prop_mod_list = []

    if "PropertyValueDict" in interface_dict:
        main_prop_val_obj = {}
        main_prop_val_obj["className"] = class_name
        main_prop_val_obj["tagName"] = parent_tag_name
        sub_prop_val_obj = {}
        for key in interface_dict["PropertyValueDict"]:
            if type(interface_dict["PropertyValueDict"][key]) is list:
                sub_prop_val_obj[key] = interface_dict["PropertyValueDict"][key][row_idx]
            else:
                sub_prop_val_obj[key] = interface_dict["PropertyValueDict"][key]
        main_prop_val_obj["propertyValueList"] = sub_prop_val_obj
        main_prop_val_list.append(main_prop_val_obj)

        data_obj["propertyValueList"] = main_prop_val_list

    if "StmPropertyModifierDict" in interface_dict:
        for key in interface_dict["StmPropertyModifierDict"]:
            property_name = key
            property_info = interface_dict["StmPropertyModifierDict"][key]
            prop_mod_obj = {}
            prop_mod_obj["className"] = class_name
            prop_mod_obj["tagName"] = parent_tag_name + "." + property_name
            prop_mod_obj["parentTagName"] = parent_tag_name
            prop_mod_obj["propertyName"] = property_name
            prop_val_list_obj = {}
            for prop in property_info:
                if type(property_info[prop]) is list:
                    prop_val_list_obj[prop] = property_info[prop][row_idx]
                else:
                    prop_val_list_obj[prop] = property_info[prop]
            prop_mod_obj["propertyValueList"] = prop_val_list_obj
            main_prop_mod_list.append(prop_mod_obj)

        data_obj["stmPropertyModifierList"] = main_prop_mod_list

    plLogger.LogDebug('end.processing_function_util.parse_interface_data')
    return data_obj


# to be removed
def parse_protocol_data(protocol_dict, row_idx):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.processing_function_util.parse_protocol_data')

    # Each object in the input dictionary corresponds to an
    # object in the protocol list
    data_obj = {}

    # Validate the protocol_dict against the schema
    res = json_utils.validate_json(json.dumps(protocol_dict),
                                   get_protocol_dict_schema())
    if res != "":
        plLogger.LogError(res)
        return data_obj

    parent_tag_name = protocol_dict["ParentTagName"]
    data_obj["protocolSrcTag"] = parent_tag_name
    class_name = protocol_dict["ClassName"]
    main_prop_val_list = []
    main_prop_mod_list = []

    if "PropertyValueDict" in protocol_dict:
        main_prop_val_obj = {}
        main_prop_val_obj["className"] = class_name
        main_prop_val_obj["tagName"] = parent_tag_name
        sub_prop_val_obj = {}
        for key in protocol_dict["PropertyValueDict"]:
            if type(protocol_dict["PropertyValueDict"][key]) is list:
                sub_prop_val_obj[key] = protocol_dict["PropertyValueDict"][key][row_idx]
            else:
                sub_prop_val_obj[key] = protocol_dict["PropertyValueDict"][key]
        main_prop_val_obj["propertyValueList"] = sub_prop_val_obj
        main_prop_val_list.append(main_prop_val_obj)

        data_obj["propertyValueList"] = main_prop_val_list

    if "StmPropertyModifierDict" in protocol_dict:
        for key in protocol_dict["StmPropertyModifierDict"]:
            property_name = key
            property_info = protocol_dict["StmPropertyModifierDict"][key]
            prop_mod_obj = {}
            prop_mod_obj["className"] = class_name
            prop_mod_obj["tagName"] = parent_tag_name + "." + property_name
            prop_mod_obj["parentTagName"] = parent_tag_name
            prop_mod_obj["propertyName"] = property_name
            prop_val_list_obj = {}
            for prop in property_info:
                if type(property_info[prop]) is list:
                    prop_val_list_obj[prop] = property_info[prop][row_idx]
                else:
                    prop_val_list_obj[prop] = property_info[prop]
            prop_mod_obj["propertyValueList"] = prop_val_list_obj
            main_prop_mod_list.append(prop_mod_obj)

        data_obj["stmPropertyModifierList"] = main_prop_mod_list

    plLogger.LogDebug('end.processing_function_util.parse_protocol_data')
    return data_obj


# to be removed
def get_iterface_dict_schema():
    return '''{
        "type": "object",
        "properties": {
            "ParentTagName": {
                "type": "string"
            },
            "ClassName": {
                "type": "string"
            },
            "PropertyValueDict": {
                "type": "object"
            },
            "StmPropertyModifierDict": {
                "type": "object"
            }
        },
        "required": [
            "ParentTagName",
            "ClassName"
        ]
    }'''


# to be removed
def get_protocol_dict_schema():
    return '''
        {
          "type": "object",
          "properties": {
            "ParentTagName": {
              "type": "string"
            },
            "ClassName": {
              "type": "string"
            },
            "PropertyValueDict": {
              "type": "object"
            },
            "StmPropertyModifierDict": {
              "type": "object"
            }
          },
          "required": [
            "ParentTagName",
            "ClassName"
          ]
        }
    '''


# NEW UTILS
def parse_prop_val_data(prop_val_dict, row_idx):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.processing_function_util.parse_prop_value_data')

    # Each object in the input dictionary corresponds to an
    # object in the interface list
    data_obj = {}

    # Validate the prop_val_dict against the schema
    res = json_utils.validate_json(json.dumps(prop_val_dict),
                                   get_property_dict_schema())
    if res != "":
        plLogger.LogError(res)
        return data_obj

    main_prop_val_list = []
    if "PropertyValueDict" in prop_val_dict:
        main_prop_val_obj = {}
        main_prop_val_obj["className"] = prop_val_dict["ClassName"]
        main_prop_val_obj["tagName"] = prop_val_dict["ParentTagName"]
        sub_prop_val_obj = {}
        for key in prop_val_dict["PropertyValueDict"]:
            if type(prop_val_dict["PropertyValueDict"][key]) is list:
                sub_prop_val_obj[key] = prop_val_dict["PropertyValueDict"][key][row_idx]
            else:
                sub_prop_val_obj[key] = prop_val_dict["PropertyValueDict"][key]
        main_prop_val_obj["propertyValueList"] = sub_prop_val_obj
        main_prop_val_list.append(main_prop_val_obj)

        data_obj["propertyValueList"] = main_prop_val_list

    plLogger.LogDebug('end.processing_function_util.parse_prop_value_data')
    return data_obj


def parse_prop_mod_data(prop_mod_dict, row_idx):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.processing_function_util.parse_prop_mod_data')

    # Each object in the input dictionary corresponds to an
    # object in the interface list
    data_obj = {}

    # Validate the prop_mod_dict against the schema
    res = json_utils.validate_json(json.dumps(prop_mod_dict),
                                   get_property_dict_schema())
    if res != "":
        plLogger.LogError(res)
        return data_obj

    parent_tag_name = prop_mod_dict["ParentTagName"]
    class_name = prop_mod_dict["ClassName"]
    main_prop_mod_list = []

    if "StmPropertyModifierDict" in prop_mod_dict:
        for key in prop_mod_dict["StmPropertyModifierDict"]:
            property_name = key
            property_info = prop_mod_dict["StmPropertyModifierDict"][key]
            prop_mod_obj = {}
            prop_mod_obj["className"] = class_name
            prop_mod_obj["tagName"] = parent_tag_name + "." + property_name
            prop_mod_obj["parentTagName"] = parent_tag_name
            prop_mod_obj["propertyName"] = property_name
            prop_val_list_obj = {}
            for prop in property_info:
                if type(property_info[prop]) is list:
                    prop_val_list_obj[prop] = property_info[prop][row_idx]
                else:
                    prop_val_list_obj[prop] = property_info[prop]
            prop_mod_obj["propertyValueList"] = prop_val_list_obj
            main_prop_mod_list.append(prop_mod_obj)

        data_obj["stmPropertyModifierList"] = main_prop_mod_list

    plLogger.LogDebug('end.processing_function_util.parse_prop_mod_data')
    return data_obj


def parse_merge_list_data(merge_list_dict, row_idx):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.processing_function_util.parse_merge_list_data')

    # Each object in the input dictionary corresponds to an
    # object in the interface list
    data_obj = {}

    # Validate the merge_list_dict against the schema
    res = json_utils.validate_json(json.dumps(merge_list_dict),
                                   get_merge_list_schema())
    if res != "":
        plLogger.LogError(res)
        return data_obj

    data_obj["mergeSourceTag"] = merge_list_dict["ParentTagName"]
    data_obj["mergeTargetTag"] = merge_list_dict["MergeTargetTag"]
    data_obj["mergeSourceTemplateFile"] = merge_list_dict["MergeSourceTemplateFile"]

    if "PropertyValueDict" in merge_list_dict:
        prop_val_list = parse_prop_val_data(merge_list_dict, row_idx)
        data_obj["propertyValueList"] = prop_val_list["propertyValueList"]

    if "StmPropertyModifierDict" in merge_list_dict:
        prop_mod_list = parse_prop_mod_data(merge_list_dict, row_idx)
        data_obj["stmPropertyModifierList"] = prop_mod_list["stmPropertyModifierList"]

    plLogger.LogDebug('end.processing_function_util.parse_merge_list_data')
    return data_obj


def get_property_dict_schema():
    return '''{
        "type": "object",
        "properties": {
            "ParentTagName": {
                "type": "string"
            },
            "ClassName": {
                "type": "string"
            },
            "PropertyValueDict": {
                "type": "object"
            },
            "StmPropertyModifierDict": {
                "type": "object"
            }
        },
        "required": [
            "ParentTagName",
            "ClassName"
        ]
    }'''


def get_merge_list_schema():
    return '''{
        "type": "object",
        "properties": {
            "ClassName": {
                "type": "string"
            },
            "ParentTagName": {
                "type": "string"
            },
            "MergeSourceTemplateFile": {
                "type": "string"
            },
            "MergeTargetTag": {
                "type": "string"
            },
            "PropertyValueDict": {
                "type": "object"
            },
            "StmPropertyModifierDict": {
                "type": "object"
            }
        },
        "required": [
            "ClassName",
            "ParentTagName",
            "MergeTargetTag",
            "MergeSourceTemplateFile"
        ]
    }'''
