from StcIntPythonPL import *
import ast
import json
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.manager.utils.processing_function_util as process_util


# TO BE REMOVED
# input_dict:
# Enable: enable or disable the modifier.  If disabled, an empty ModInfo is returned.
# Start: modifier start value
# Step: modifier step value
# Repeat: modifier repeat value (opt - defaults to 0)
# Recycle: modifier recycle value (opt - defaults to 0)
# PropName: (datamodel) name of the property being modified
# ObjName: (datamodel) name of the object being modified
#
# output_dict:
# ModInfo: List containing the StmPropertyModifier.ModifierInfo
#   that can go directly into the ModifyTemplatePropertyCommand
def config_range_prop_modifier(input_dict):
    err_msg = ""
    output_dict = {}
    enable = True
    if "Enable" in input_dict.keys():
        try:
            enable = ast.literal_eval(input_dict["Enable"])
        except ValueError:
            err_msg = "Enable must be set to True or False, not " + \
                      input_dict["Enable"] + "."
            return output_dict, err_msg
    if not enable:
        output_dict["ModInfo"] = []
        output_dict["TagNameList"] = []
        return output_dict, err_msg
    if "Start" not in input_dict.keys():
        err_msg = "Start value is required.  " + \
                  "Could not find \"Start\" in the input dictionary."
        return output_dict, err_msg
    if "Step" not in input_dict.keys():
        err_msg = "Step value is required.  " + \
                  "Could not find \"Step\" in the input dictionary."
        return output_dict, err_msg
    if "ObjName" not in input_dict.keys():
        err_msg = "ObjName value is required.  " + \
                  "Could not find \"ObjName\" in the input dictionary."
        return output_dict, err_msg
    if "PropName" not in input_dict.keys():
        err_msg = "PropName value is required.  " + \
                  "Could not find \"PropName\" in the input dictionary."
        return output_dict, err_msg
    start = input_dict["Start"]
    step = input_dict["Step"]
    repeat = "0"
    recycle = "0"
    if "Repeat" in input_dict.keys():
        repeat = input_dict["Repeat"]
    if "Recycle" in input_dict.keys():
        recycle = input_dict["Recycle"]
    obj_name = input_dict["ObjName"]
    prop_name = input_dict["PropName"]

    # ModifierInfo must be configured as escaped XML
    mod_info = "&lt;Modifier " + \
               "ModifierType=&quot;RANGE&quot; " + \
               "PropertyName=&quot;" + prop_name + "&quot; " + \
               "ObjectName=&quot;" + obj_name + "&quot;&gt; " + \
               "&lt;Start&gt;" + start + "&lt;/Start&gt; " + \
               "&lt;Step&gt;" + step + "&lt;/Step&gt; " + \
               "&lt;Repeat&gt;" + repeat + \
               "&lt;/Repeat&gt; " + \
               "&lt;Recycle&gt;" + recycle + \
               "&lt;/Recycle&gt;" + \
               "&lt;/Modifier&gt;"
    output_dict["ModInfoPropList"] = ["StmPropertyModifier.ModifierInfo"]
    output_dict["ModInfoValList"] = [mod_info]
    return output_dict, err_msg


# TO BE REMOVED
# input_dict:
# EnableVlan: (bool) enable VLAN
#
# output_dict:
# TemplateFileName: name of the template file that corresponds
#   to the input flags
def config_template_filename(input_dict):
    output_dict = {}
    err_msg = ""
    enable_vlan = False
    if "EnableVlan" in input_dict:
        if input_dict["EnableVlan"] != "True" and \
           input_dict["EnableVlan"] != "False":
            err_msg = "Expected EnableVlan to be True or False, not " + \
                      str(enable_vlan) + "."
            return output_dict, err_msg
        if input_dict["EnableVlan"] == "True":
            enable_vlan = True
    template_file = "IPv4_NoVlan.xml"
    if enable_vlan:
        template_file = "IPv4_Vlan.xml"
    output_dict["TemplateFileName"] = template_file
    return output_dict, err_msg


def make_list(s):
    if type(s) is list:
        return s
    return [s]


# input_dict: input dictionary from txml with property ids replaced with user input values
#
# output_dict: dictionary of json data formatted for the CreateProtocolMixCommand
def config_protocol_table_data(input_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.txml_processing_functions.config_protocol_table_data')

    output_dict = {}
    err_msg = ""
    json_data_list = {}

    plLogger.LogDebug('input_dict: ' + str(input_dict))

    # Validate the input_dict
    res = validate_input_dict(input_dict)
    if res != "":
        return output_dict, res

    devCnt = input_dict["input"]["customDict"]["DeviceCount"]
    json_data_list["deviceCount"] = int(devCnt)

    # Loop through each row in the txml table
    weight_list = make_list(input_dict["input"]["customDict"]["Weight"])

    component_list = []
    for row_idx, weight in enumerate(weight_list):
        comp_dict = {}
        comp_dict["weight"] = str(weight)
        if "TagPrefix" in input_dict["input"]["customDict"]:
            comp_dict["tagPrefix"] = input_dict["input"]["customDict"]["TagPrefix"]

        dev_per_block = make_list(input_dict["input"]["customDict"]["DevPerBlock"])[row_idx]
        comp_dict["devicesPerBlock"] = int(dev_per_block)

        enable_vlan = make_list(input_dict["input"]["customDict"]["EnableVlan"])[row_idx]
        ip_stack = "Dual"
        if "IpStack" in input_dict["input"]["customDict"]:
            ip_stack = make_list(input_dict["input"]["customDict"]["IpStack"])[row_idx]
        plLogger.LogInfo("using " + str(ip_stack) + " as the IP stack")
        if ast.literal_eval(enable_vlan):
            comp_dict["baseTemplateFile"] = str(ip_stack) + "_Vlan.xml"
        else:
            comp_dict["baseTemplateFile"] = str(ip_stack) + "_NoVlan.xml"

        enable_bfd = False
        bfd_protocol = {}
        modify_list = []
        mergeList = []
        propertyValueList = []
        stmPropertyModifierList = []

        # Loop through the interfaceDict in the input_dict and add to
        # stmPropertyModifierList & propertyValueList in output_dict
        for interface in input_dict["input"]["interfaceDict"]:

            # Don't add the VlanIf if EnableVlan is False
            if interface["ClassName"] == "VlanIf" and \
               ast.literal_eval(enable_vlan) is False:
                continue

            # Don't process IPv4 if we're using an IPv6 stack
            if interface["ClassName"] == "Ipv4If" and str(ip_stack) == "IPV6":
                continue

            # Don't process IPv6 if we're using an IPv4 stack
            if interface["ClassName"] == "Ipv6If" and str(ip_stack) == "IPV4":
                continue

            if "PropertyValueDict" in interface:
                prop_val_dict = process_util.parse_prop_val_data(interface, row_idx)
                propertyValueList.extend(prop_val_dict["propertyValueList"])

            if "StmPropertyModifierDict" in interface:
                prop_mod_dict = process_util.parse_prop_mod_data(interface, row_idx)
                stmPropertyModifierList.extend(prop_mod_dict["stmPropertyModifierList"])

        # Loop through the protocolDict in the input_dict and add to
        # mergeList in the output_dict
        for protocol in input_dict["input"]["protocolDict"]:
            protocol["MergeSourceTag"] = protocol["ParentTagName"]
            protocol["MergeSourceTemplateFile"] = "AllRouters.xml"
            protocol["MergeTargetTag"] = "ttEmulatedDevice"
            # Add the protocol to the protocolList if it is enabled
            if "EnableProperty" in protocol.keys():
                if ast.literal_eval(make_list(protocol["EnableProperty"])[row_idx]):
                    if "EnableBfd" in protocol["PropertyValueDict"].keys():
                        enable_bfd |= ast.literal_eval(
                            make_list(protocol["PropertyValueDict"]["EnableBfd"])[row_idx])
                        mergeList.append(process_util.parse_merge_list_data(protocol, row_idx))

            # BfdRouterConfig will be handled after all other protocols are parsed
            if protocol["ClassName"] == "BfdRouterConfig":
                bfd_protocol = protocol

        # Bfd is added to the protocolList if bfd is enabled in at least one protocol and
        # the BfdRouterConfig information is defined in input_dict
        if enable_bfd is True and len(bfd_protocol) != 0:
            mergeList.append(process_util.parse_merge_list_data(bfd_protocol, row_idx))

        modify_list.append({"mergeList": mergeList})
        modify_list.append({"propertyValueList": propertyValueList})
        modify_list.append({"stmPropertyModifierList": stmPropertyModifierList})
        comp_dict["modifyList"] = modify_list
        component_list.append(comp_dict)

    json_data_list["components"] = component_list

    # f = open('out.txt', 'w')
    # f.write(json.dumps(json_data_list))

    output_dict["TableData"] = json.dumps(json_data_list)
    plLogger.LogDebug('output_dict: ' + str(output_dict))
    plLogger.LogDebug('end.txml_processing_functions.config_table_data')
    return output_dict, err_msg


# TO BE REMOVED
def config_table_data(input_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.txml_processing_functions.config_table_data')

    output_dict = {}
    err_msg = ""
    json_data_list = []

    plLogger.LogDebug('input_dict: ' + str(input_dict))

    # Validate the input_dict
    res = validate_input_dict(input_dict)
    if res != "":
        return output_dict, res

    # Loop through each row in the txml table
    weight_list = input_dict["input"]["customDict"]["Weight"]

    for row_idx, weight in enumerate(weight_list):
        json_data = {}
        json_data["weight"] = float(weight)

        enable_vlan = input_dict["input"]["customDict"]["EnableVlan"][row_idx]
        if ast.literal_eval(enable_vlan):
            json_data["baseTemplateFile"] = "Dual_Vlan.xml"
        else:
            json_data["baseTemplateFile"] = "Dual_NoVlan.xml"

        json_data["protocolTemplateFile"] = "AllRouters.xml"
        json_data["deviceTag"] = "ttEmulatedDevice"
        json_data["useBlock"] = False
        enable_bfd = False
        bfd_protocol = {}
        json_data["interfaceList"] = []
        json_data["protocolList"] = []

        # Loop through the interfaceDict in the input_dict and
        # add each interface to the interfaceList in the output_dict
        for interface in input_dict["input"]["interfaceDict"]:
            # Don't add the VlanIf if EnableVlan is False
            if interface["ClassName"] == "VlanIf" and \
               ast.literal_eval(enable_vlan) is False:
                continue
            else:
                json_data["interfaceList"].append(
                    process_util.parse_interface_data(interface, row_idx))

        # Loop through the protocolDict in the input_dict and
        # add each protocol to the protocolList in the output_dict
        for protocol in input_dict["input"]["protocolDict"]:
            # Add the protocol to the protocolList if it is enabled
            if "EnableProperty" in protocol.keys():
                if ast.literal_eval(protocol["EnableProperty"][row_idx]):
                    if "EnableBfd" in protocol["PropertyValueDict"].keys():
                        enable_bfd |= ast.literal_eval(
                            protocol["PropertyValueDict"]["EnableBfd"][row_idx])
                    json_data["protocolList"].append(
                        process_util.parse_protocol_data(protocol, row_idx))

            # BfdRouterConfig will be handled after all other protocols are parsed
            if protocol["ClassName"] == "BfdRouterConfig":
                bfd_protocol = protocol

        # Bfd is added to the protocolList if bfd is enabled in at least one protocol and
        # the BfdRouterConfig information is defined in input_dict
        if enable_bfd is True and len(bfd_protocol) != 0:
            json_data["protocolList"].append(
                process_util.parse_protocol_data(bfd_protocol, row_idx))

        json_data_list.append(json_data)

    # f = open('out.txt', 'w')
    # f.write(json.dumps(json_data_list))
    # f.write(str(json_data_list))

    output_dict["TableData"] = json.dumps(json_data_list)
    plLogger.LogDebug('output_dict: ' + str(output_dict))
    plLogger.LogDebug('end.txml_processing_functions.config_table_data')
    return output_dict, err_msg


# Validate that the input_dict follows the defined schema and the number or rows are consistent
def validate_input_dict(input_dict):
    # Validate the input_dict against the schema
    res = json_utils.validate_json(json.dumps(input_dict),
                                   get_datamodel_dict_schema())
    if res != "":
        return res

    weight_list = input_dict["input"]["customDict"]["Weight"]
    num_rows = len(weight_list)

    res = is_valid_rows(input_dict["input"]["customDict"]["EnableVlan"], num_rows, "EnableVlan")
    if res != "":
        return res

    dict_list = [input_dict["input"]["interfaceDict"], input_dict["input"]["protocolDict"]]
    # Loop through the interfaceDict in the input_dict
    for input_dict_list in dict_list:
        for dict in input_dict_list:
            if "EnableProperty" in dict:
                res = is_valid_rows(dict["EnableProperty"], num_rows, "EnableProperty")
                if res != "":
                    return res

            res = is_valid_rows(dict["ParentTagName"], num_rows, "ParentTagName")
            if res != "":
                return res

            res = is_valid_rows(dict["ClassName"], num_rows, "ClassName")
            if res != "":
                return res

            if "PropertyValueDict" in dict:
                for key in dict["PropertyValueDict"]:
                    res = is_valid_rows(dict["PropertyValueDict"][key], num_rows, key)
                    if res != "":
                        return res

            if "StmPropertyModifierDict" in dict:
                for key in dict["StmPropertyModifierDict"]:
                    property_info = dict["StmPropertyModifierDict"][key]
                    for prop in property_info:
                        res = is_valid_rows(property_info[prop], num_rows, prop)
                        if res != "":
                            return res
    return ""


def is_valid_rows(value, row_len, property_name):
    if type(value) is list:
        value_len = len(value)
        if value_len != row_len:
            return "Expected " + str(row_len) + " elements in " + \
                property_name + ", but got " + str(value_len)
    return ""


# TODO: update
# input_dict:
# DeviceCount: DeviceCount (int)
#
# output_dict:
# Dev1: Device Count 1
# Dev2: Device Count 2
def config_device_count(input_dict):
    output_dict = {}
    err_msg = ""

    output_dict["Dev1"] = input_dict["DeviceCount"]
    output_dict["Dev2"] = input_dict["DeviceCount"]
    return output_dict, err_msg


# TODO: update
# input_dict:
# TrafficLoad: Traffic Load (int)
#
# output_dict:
# Load1: Traffic Load 1
# Load2: Traffic Load 2
def config_traffic_load(input_dict):
    output_dict = {}
    err_msg = ""

    output_dict["Load1"] = input_dict["TrafficLoad"]
    output_dict["Load2"] = input_dict["TrafficLoad"]
    return output_dict, err_msg


# input_dict:
# TestType: Test Type (bool) SCALABILITY/BENCHMARK
# MinDeviceCount: Min Device Count for iterator min value
# MaxDeviceCount: Max Device Count for iterator max value
#
# output_dict:
# Dev1: Device Count 1
# Dev2: Device Count 2
def config_device_iterator_value(input_dict):
    output_dict = {}
    err_msg = ""

    dict_keys = input_dict.keys()
    if "TestType" in dict_keys:
        if input_dict["TestType"] == "SCALABILITY":
            output_dict["minDev"] = input_dict["ScaleDeviceCount"]
            output_dict["maxDev"] = input_dict["ScaleDeviceCount"]
        if input_dict["TestType"] == "BENCHMARK":
            output_dict["minDev"] = input_dict["MinDeviceCount"]
            output_dict["maxDev"] = input_dict["MaxDeviceCount"]

    return output_dict, err_msg


# input_dict:
# InputKey: string
#
# output_dict:
# OutputKey: string
def copy_value_to_sequence(input_dict):
    output_dict = {}
    err_msg = ""

    output_dict["OutputKey"] = input_dict["InputKey"]
    return output_dict, err_msg


# input_dict:
# InputKey: string
#
# output_dict:
# OutputKey: string
def copy_dict_to_sequence(input_dict):
    output_dict = {}
    err_msg = ""

    output_dict["OutputKey"] = json.dumps(input_dict["InputKey"])
    return output_dict, err_msg


def copy_input_to_sequence(input_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.copy_dict_to_sequence')

    output_dict = {}
    err_msg = ""

    input = input_dict["input"]
    output_dict["OutputKey"] = input["InputKey"]
    return output_dict, err_msg


# input_dict:
# InputKey: string
#
# output_dict:
# OutputKey: list
def copy_string_to_list(input_dict):
    output_dict = {}
    err_msg = ""

    try:
        val_list = ast.literal_eval(input_dict["InputKey"])
        if isinstance(val_list, list):
            val_list = [str(x) for x in val_list]
            output_dict["OutputKey"] = val_list
    except ValueError:
        err_msg = "Was not able to handle input, " + \
            str(input_dict["InputKey"]) + " as a python list."
    return output_dict, err_msg


def get_datamodel_dict_schema():
    return '''
    {
        "type": "object",
        "properties": {
            "id": {
                "type": "string"
            },
            "scriptFile": {
                "type": "string"
            },
            "entryFunction": {
                "type": "string"
            },
            "input": {
                "type": "object",
                "properties": {
                    "customDict": {
                        "type": "object"
                    },
                    "iterfaceDict": {
                        "type": "array",
                        "items": {
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
                    },
                    "protocolDict": {
                        "type": "array",
                        "items": {
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
                    },
                    "protocolMergeDict": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "MergeSourceTag": {
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
                                "MergeSourceTag",
                                "MergeTargetTag"
                            ]
                        }
                    }
                }
            },
            "output": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scriptVarName": {
                            "type": "string"
                        },
                        "epKey": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
    '''


"""
if __name__ == "__main__":
    input_dict = {'Ipv4Addr': ["1.1.1.2", "2.2.2.2", "3.3.3.2"],
                  'Ipv4AddrStep': ["0.0.10.0", "0.0.20.0", "0.0.30.0"],
                  'Ipv4GwAddr': ["1.1.1.1", "2.2.2.1", "3.3.3.1"],
                  'Ipv4GwAddrStep': ["0.0.10.0", "0.0.20.0",
                                     "0.0.30.0"],
                  'Ipv4RtrId': ["11.11.11.11", "22.22.22.1",
                                "33.33.33.1"],
                  'Ipv4RtrIdStep': ["11.11.11.11", "11.11.11.11",
                                    "11.11.11.11"],
                  'MacAddr': ["00:10:95:00:00:01", "00:11:95:00:00:01",
                              "00:12:95:00:00:01"],
                  'MacAddrStep': ["00:00:00:00:00:01",
                                  "00:00:00:00:00:01",
                                  "00:00:00:00:00:01"],
                  'Weight': [10.0, 20.0, 30.0],
                  'EnableBgp': [True, False, True],
                  'EnableOspfv2': [True, True, False],
                  'BgpAsNum': [10, 20, 30],
                  'BgpDutAsNum': [10, 20, 30],
                  'Ospfv2AreaId': ["0.0.0.0", "0.0.0.1", "0.0.0.2"],
                  'Ospfv2RouterPriority': [0, 50, 100]}
    config_table_data(input_dict)
    input_dict = {'TestType': "BENCHMARK",
                  'MinDeviceCount': 10,
                  'MaxDeviceCount': 20}
    config_device_iterator_value(input_dict)
"""
