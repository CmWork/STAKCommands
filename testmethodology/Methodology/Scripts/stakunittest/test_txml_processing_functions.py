from StcIntPythonPL import *
import spirent.methodology.Methodology.Scripts.txml_processing_functions as proc_func
import json
import spirent.methodology.utils.json_utils as json_utils


def test_protocol_table_data(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.txml_processing_functions.test_protocol_table_data')
    input_string = get_input_string()
    output_dict, err_msg = proc_func.config_protocol_table_data(json.loads(input_string))

    err_str, table_data = json_utils.load_json(output_dict["TableData"])
    assert err_str == ""
    # Two rows in the table (Bgp/Bfd and Ospfv2)
    assert len(table_data) == 2

    # Check first mix with BFD & BFD enabled
    table_dict = table_data["components"][0]
    assert table_dict["weight"] == "10"
    assert table_dict["devicesPerBlock"] == 1
    assert table_dict["baseTemplateFile"] == "Dual_Vlan.xml"

    # Check contents of the modifyList (mergeList, stmPropertyModifierList, propertyValueList)
    modList = table_dict["modifyList"]
    assert len(modList) == 3

    # Check contents of propertyValueList
    prop_val_dict = modList[1]
    assert len(prop_val_dict["propertyValueList"]) == 0

    # Check contents of stmPropertyModifierList has three
    # stmPropertyModifiers (Address, Gateway, Vlan)
    stm_prop_dict = modList[2]
    stm_prop_list = stm_prop_dict["stmPropertyModifierList"]
    assert len(stm_prop_list) == 3

    # Check the stmPropertyModifier for Address
    ipv4_address = {}
    ipv4_address["tagName"] = "ttIpv4If.Address"
    ipv4_address["className"] = "Ipv4If"
    ipv4_address["propertyName"] = "Address"
    ipv4_address["parentTagName"] = "ttIpv4If"
    ipv4_address["propertyValueList"] = {}
    ipv4_address["propertyValueList"]["Start"] = "1.1.1.2"
    ipv4_address["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_address in stm_prop_list

    # Check the stmPropertyModifier for Gateway
    ipv4_gateway = {}
    ipv4_gateway["tagName"] = "ttIpv4If.Gateway"
    ipv4_gateway["className"] = "Ipv4If"
    ipv4_gateway["propertyName"] = "Gateway"
    ipv4_gateway["parentTagName"] = "ttIpv4If"
    ipv4_gateway["propertyValueList"] = {}
    ipv4_gateway["propertyValueList"]["Start"] = "1.1.1.1"
    ipv4_gateway["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_gateway in stm_prop_list

    # Check the stmPropertyModifier for Vlan
    vlan = {}
    vlan["tagName"] = "ttVlanIf.VlanId"
    vlan["className"] = "VlanIf"
    vlan["propertyName"] = "VlanId"
    vlan["parentTagName"] = "ttVlanIf"
    vlan["propertyValueList"] = {}
    vlan["propertyValueList"]["Start"] = "100"
    vlan["propertyValueList"]["Step"] = "0"
    assert vlan in stm_prop_list

    # Check that mergeList contains BFD, BGP
    # Check contents of propertyValueList
    merge_dict = modList[0]
    merge_list = merge_dict["mergeList"]
    assert len(merge_list) == 2

    # Verify merge content for BGP protocol
    bgp_dict = merge_list[0]
    assert bgp_dict["mergeSourceTag"] == "ttBgpRouterConfig"
    assert bgp_dict["mergeSourceTemplateFile"] == "AllRouters.xml"
    assert bgp_dict["mergeTargetTag"] == "ttEmulatedDevice"

    # Check that BgpRouterConfig contains two propertyModifiers(AsNum and DutAsNum)
    bgp_stm_mod_list = bgp_dict["stmPropertyModifierList"]
    assert len(bgp_stm_mod_list) == 2

    # Check the AsNum propertyModifier
    as_num = {}
    as_num["tagName"] = "ttBgpRouterConfig.AsNum"
    as_num["className"] = "BgpRouterConfig"
    as_num["propertyName"] = "AsNum"
    as_num["parentTagName"] = "ttBgpRouterConfig"
    as_num["propertyValueList"] = {}
    as_num["propertyValueList"]["Start"] = "100"
    as_num["propertyValueList"]["Step"] = "1"
    assert as_num in bgp_stm_mod_list

    # Check the DutAsNum propertyModifier
    dut_as_num = {}
    dut_as_num["tagName"] = "ttBgpRouterConfig.DutAsNum"
    dut_as_num["className"] = "BgpRouterConfig"
    dut_as_num["propertyName"] = "DutAsNum"
    dut_as_num["parentTagName"] = "ttBgpRouterConfig"
    dut_as_num["propertyValueList"] = {}
    dut_as_num["propertyValueList"]["Start"] = "100"
    dut_as_num["propertyValueList"]["Step"] = "1"
    assert dut_as_num in bgp_stm_mod_list

    # Check BgpRouterConfigs propertyValueList
    bgp_prop_val_list = bgp_dict["propertyValueList"]
    assert len(bgp_prop_val_list) == 1
    bgp_prop_val = bgp_prop_val_list[0]
    assert bgp_prop_val["className"] == "BgpRouterConfig"
    assert bgp_prop_val["tagName"] == "ttBgpRouterConfig"
    assert bgp_prop_val["propertyValueList"]["IpVersion"] == "IPV4"
    assert bgp_prop_val["propertyValueList"]["EnableBfd"] == "True"

    # Check the BfdRouterConfig
    bfd_dict = merge_list[1]
    assert bfd_dict["mergeSourceTag"] == "ttBfdRouterConfig"
    assert bfd_dict["mergeSourceTemplateFile"] == "AllRouters.xml"
    assert bfd_dict["mergeTargetTag"] == "ttEmulatedDevice"

    # Check BfdRouterConfigs propertyValueList
    bfd_prop_val_list = bfd_dict["propertyValueList"]
    assert len(bfd_prop_val_list) == 1
    bgp_prop_val = bfd_prop_val_list[0]
    assert bgp_prop_val["className"] == "BfdRouterConfig"
    assert bgp_prop_val["tagName"] == "ttBfdRouterConfig"
    assert bgp_prop_val["propertyValueList"]["DetectMultiplier"] == "1"
    assert bgp_prop_val["propertyValueList"]["TxInterval"] == "2"
    assert bgp_prop_val["propertyValueList"]["RxInterval"] == "3"

    # Check second mix with Ospfv2 enabled
    table_dict = table_data["components"][1]
    assert table_dict["weight"] == "20"
    assert table_dict["devicesPerBlock"] == 5
    assert table_dict["baseTemplateFile"] == "Dual_Vlan.xml"

    # Check contents of stmPropertyModifierList has three
    # stmPropertyModifiers (Address, Gateway, Vlan)
    modList = table_dict["modifyList"]
    stm_prop_dict = modList[2]
    stm_prop_list = stm_prop_dict["stmPropertyModifierList"]
    assert len(stm_prop_list) == 3

    # Check the stmPropertyModifier for Address
    ipv4_address = {}
    ipv4_address["tagName"] = "ttIpv4If.Address"
    ipv4_address["className"] = "Ipv4If"
    ipv4_address["propertyName"] = "Address"
    ipv4_address["parentTagName"] = "ttIpv4If"
    ipv4_address["propertyValueList"] = {}
    ipv4_address["propertyValueList"]["Start"] = "1.1.1.2"
    ipv4_address["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_address in stm_prop_list

    # Check the stmPropertyModifier for Gateway
    ipv4_gateway = {}
    ipv4_gateway["tagName"] = "ttIpv4If.Gateway"
    ipv4_gateway["className"] = "Ipv4If"
    ipv4_gateway["propertyName"] = "Gateway"
    ipv4_gateway["parentTagName"] = "ttIpv4If"
    ipv4_gateway["propertyValueList"] = {}
    ipv4_gateway["propertyValueList"]["Start"] = "1.1.1.1"
    ipv4_gateway["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_gateway in stm_prop_list

    # Check that mergeList contains OSPFv2
    # Check contents of propertyValueList
    merge_dict = modList[0]
    merge_list = merge_dict["mergeList"]
    assert len(merge_list) == 1

    # Verify merge content for Ospfv2 protocol
    ospfv2_dict = merge_list[0]
    assert ospfv2_dict["mergeSourceTag"] == "ttOspfv2RouterConfig"
    assert ospfv2_dict["mergeSourceTemplateFile"] == "AllRouters.xml"
    assert ospfv2_dict["mergeTargetTag"] == "ttEmulatedDevice"

    # Check that Ospfv2RouterConfig contains one propertyModifiers (AreaId)
    ospfv2_stm_mod_list = ospfv2_dict["stmPropertyModifierList"]
    assert len(ospfv2_stm_mod_list) == 1

    # Check the AreaId propertyModifier
    area_id = {}
    area_id["tagName"] = "ttOspfv2RouterConfig.AreaId"
    area_id["className"] = "Ospfv2RouterConfig"
    area_id["propertyName"] = "AreaId"
    area_id["parentTagName"] = "ttOspfv2RouterConfig"
    area_id["propertyValueList"] = {}
    area_id["propertyValueList"]["Start"] = "3"
    area_id["propertyValueList"]["Step"] = "0"
    assert area_id in ospfv2_stm_mod_list

    # Check Ospfv2RouterConfig propertyValueList
    ospfv2_prop_val_list = ospfv2_dict["propertyValueList"]
    assert len(ospfv2_prop_val_list) == 1
    ospfv2_prop_val = ospfv2_prop_val_list[0]
    assert ospfv2_prop_val["className"] == "Ospfv2RouterConfig"
    assert ospfv2_prop_val["tagName"] == "ttOspfv2RouterConfig"
    assert ospfv2_prop_val["propertyValueList"]["EnableBfd"] == "False"


# TO BE REMOVED
def test_config_table_data(stc):
    input_string = get_input_string()
    output_dict, err_msg = proc_func.config_table_data(json.loads(input_string))

    err_str, table_data = json_utils.load_json(output_dict["TableData"])
    assert err_str == ""
    # Two rows in the table (Bgp and Ospfv2)
    assert len(table_data) == 2

    # Check first mix with Bgp enabled
    table_dict = table_data[0]
    assert table_dict["weight"] == 10.0
    assert table_dict["useBlock"] is False
    assert table_dict["deviceTag"] == "ttEmulatedDevice"
    assert table_dict["baseTemplateFile"] == "Dual_Vlan.xml"
    assert table_dict["protocolTemplateFile"] == "AllRouters.xml"

    # Check that the interfaceList contains two network interfaces(Ipv4 and VLAN)
    interfaceList = table_dict["interfaceList"]
    assert len(interfaceList) == 2

    # Check the IPv4 interface
    ipv4 = interfaceList[0]
    assert len(ipv4) == 1

    # Check that IPv4 has two propertyModifiers(Address and Gateway)
    propModList = ipv4["stmPropertyModifierList"]
    assert len(propModList) == 2

    # Check the propertyModifier for Address
    ipv4_address = {}
    ipv4_address["tagName"] = "ttIpv4If.Address"
    ipv4_address["className"] = "Ipv4If"
    ipv4_address["propertyName"] = "Address"
    ipv4_address["parentTagName"] = "ttIpv4If"
    ipv4_address["propertyValueList"] = {}
    ipv4_address["propertyValueList"]["Start"] = "1.1.1.2"
    ipv4_address["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_address in propModList

    # Check the propertyModifier for Gateway
    ipv4_gateway = {}
    ipv4_gateway["tagName"] = "ttIpv4If.Gateway"
    ipv4_gateway["className"] = "Ipv4If"
    ipv4_gateway["propertyName"] = "Gateway"
    ipv4_gateway["parentTagName"] = "ttIpv4If"
    ipv4_gateway["propertyValueList"] = {}
    ipv4_gateway["propertyValueList"]["Start"] = "1.1.1.1"
    ipv4_gateway["propertyValueList"]["Step"] = "0.0.1.0"
    assert ipv4_gateway in propModList

    # Check the Vlan interface
    interface = interfaceList[1]
    assert len(interface) == 1

    # Check that the propertyModifierList contains one propertyModifier(VlanId)
    propModList = interface["stmPropertyModifierList"]
    assert len(propModList) == 1

    # Check the VlanId propertyModifier
    vlan = {}
    vlan["tagName"] = "ttVlanIf.VlanId"
    vlan["className"] = "VlanIf"
    vlan["propertyName"] = "VlanId"
    vlan["parentTagName"] = "ttVlanIf"
    vlan["propertyValueList"] = {}
    vlan["propertyValueList"]["Start"] = "100"
    vlan["propertyValueList"]["Step"] = "0"
    assert vlan in propModList

    # Check that ProtocolList contains BFD, BGP
    protocolList = table_dict["protocolList"]
    assert len(protocolList) == 2

    bgp = protocolList[0]
    assert bgp["protocolSrcTag"] == "ttBgpRouterConfig"

    # Check that BgpRouterConfig contains two propertyModifiers(AsNum and DutAsNum)
    propModList = bgp["stmPropertyModifierList"]
    assert len(propModList) == 2

    # Check the AsNum propertyModifier
    as_num = {}
    as_num["tagName"] = "ttBgpRouterConfig.AsNum"
    as_num["className"] = "BgpRouterConfig"
    as_num["propertyName"] = "AsNum"
    as_num["parentTagName"] = "ttBgpRouterConfig"
    as_num["propertyValueList"] = {}
    as_num["propertyValueList"]["Start"] = "100"
    as_num["propertyValueList"]["Step"] = "1"
    assert as_num in propModList

    # Check the DutAsNum propertyModifier
    dut_as_num = {}
    dut_as_num["tagName"] = "ttBgpRouterConfig.DutAsNum"
    dut_as_num["className"] = "BgpRouterConfig"
    dut_as_num["propertyName"] = "DutAsNum"
    dut_as_num["parentTagName"] = "ttBgpRouterConfig"
    dut_as_num["propertyValueList"] = {}
    dut_as_num["propertyValueList"]["Start"] = "100"
    dut_as_num["propertyValueList"]["Step"] = "1"
    assert dut_as_num in propModList

    # Check BgpRouterConfigs propertyValueList
    propValList = bgp["propertyValueList"]
    assert len(propValList) == 1
    propVal = propValList[0]
    assert propVal["className"] == "BgpRouterConfig"
    assert propVal["tagName"] == "ttBgpRouterConfig"
    assert propVal["propertyValueList"]["IpVersion"] == "IPV4"
    assert propVal["propertyValueList"]["EnableBfd"] == "True"

    # Check the BfdRouterConfig
    bfd = protocolList[1]

    assert bfd["protocolSrcTag"] == "ttBfdRouterConfig"

    # Check BfdRouterConfigs propertyValueList
    propValList = bfd["propertyValueList"]
    assert len(propValList) == 1
    propVal = propValList[0]
    assert propVal["className"] == "BfdRouterConfig"
    assert propVal["tagName"] == "ttBfdRouterConfig"
    assert propVal["propertyValueList"]["DetectMultiplier"] == "1"
    assert propVal["propertyValueList"]["TxInterval"] == "2"
    assert propVal["propertyValueList"]["RxInterval"] == "3"

    # Check second mix with Ospfv2 enabled
    table_dict = table_data[1]
    assert table_dict["weight"] == 20.0
    assert table_dict["useBlock"] is False
    assert table_dict["deviceTag"] == "ttEmulatedDevice"
    assert table_dict["baseTemplateFile"] == "Dual_Vlan.xml"
    assert table_dict["protocolTemplateFile"] == "AllRouters.xml"

    protocolList = table_dict["protocolList"]

    # Check the Ospfv2RouterConfig
    ospfv2 = protocolList[0]
    assert ospfv2["protocolSrcTag"] == "ttOspfv2RouterConfig"

    # Check Ospfv2RouterConfig propertyValueList
    propValList = ospfv2["propertyValueList"]
    assert len(propValList) == 1
    propVal = propValList[0]
    assert propVal["className"] == "Ospfv2RouterConfig"
    assert propVal["tagName"] == "ttOspfv2RouterConfig"
    assert propVal["propertyValueList"]["EnableBfd"] == "False"

    # Check that Ospfv2RouterConfig contains 1 propertyModifier (AreaId)
    propModList = ospfv2["stmPropertyModifierList"]
    assert len(propModList) == 1

    area_id = {}
    area_id["tagName"] = "ttOspfv2RouterConfig.AreaId"
    area_id["className"] = "Ospfv2RouterConfig"
    area_id["propertyName"] = "AreaId"
    area_id["parentTagName"] = "ttOspfv2RouterConfig"
    area_id["propertyValueList"] = {}
    area_id["propertyValueList"]["Start"] = "3"
    area_id["propertyValueList"]["Step"] = "0"
    assert area_id in propModList


def test_validate_config_table_data(stc):
    input_string = get_bad_input_string()
    output_dict, err_msg = proc_func.config_table_data(json.loads(input_string))
    assert "Expected 2 elements in Start, but got 1" in err_msg


def get_input_string():
    return '''
{
    "id": "Right.CreateProtocolMix.TableData",
    "entryFunction": "config_table_data",
    "input": {
        "customDict": {
            "EnableVlan": ["True", "True"],
            "Weight": ["10", "20"],
            "DeviceCount": "100",
            "DevPerBlock": ["1", "5"],
            "TagPrefix": "Left_"
        },
        "interfaceDict": [
            {
                "ClassName": "Ipv4If",
                "ParentTagName": "ttIpv4If",
                "StmPropertyModifierDict": {
                    "Gateway": {
                        "Start": ["1.1.1.1", "1.1.1.1"],
                        "Step": ["0.0.1.0", "0.0.1.0"]
                    },
                    "Address": {
                        "Start": ["1.1.1.2", "1.1.1.2"],
                        "Step": ["0.0.1.0", "0.0.1.0"]
                    }
                }
            },
            {
                "ClassName": "VlanIf",
                "ParentTagName": "ttVlanIf",
                "StmPropertyModifierDict": {
                    "VlanId": {
                        "Start": ["100", "100"],
                        "Step": ["0", "1"]
                    }
                }
            }
        ],
        "protocolDict": [
            {
                "ClassName": "BlahConfig",
                "ParentTagName": "ttBlahConfig",
                "EnableProperty": ["False", "False"],
                "StmPropertyModifierDict": {
                    "DutAsNum": {
                        "Start": "100",
                        "Step": "1"
                    },
                    "AsNum": {
                        "Start": "100",
                        "Step": "1"
                    }
                }
            },
            {
                "ClassName": "BfdRouterConfig",
                "ParentTagName": "ttBfdRouterConfig",
                "PropertyValueDict": {
                    "DetectMultiplier": ["1", "99"],
                    "TxInterval": ["2", "99"],
                    "RxInterval": ["3", "99"]
                }
            },
            {
                "ClassName": "BgpRouterConfig",
                "ParentTagName": "ttBgpRouterConfig",
                "EnableProperty": ["True", "False"],
                "StmPropertyModifierDict": {
                    "DutAsNum": {
                        "Start": ["100", "0"],
                        "Step": ["1", "0"]
                    },
                    "AsNum": {
                        "Start": ["100", "0"],
                        "Step": ["1", "0"]
                    }
                },
                "PropertyValueDict": {
                    "IpVersion": ["IPV4", "IPV4"],
                    "EnableBfd": ["True", "False"]
                }
            },
            {
                "ClassName": "Ospfv2RouterConfig",
                "ParentTagName": "ttOspfv2RouterConfig",
                "EnableProperty": ["False", "True"],
                "StmPropertyModifierDict": {
                    "AreaId": {
                        "Start": ["0", "3"],
                        "Step": ["1", "0"]
                    }
                },
                "PropertyValueDict": {
                    "EnableBfd": ["True", "False"]
                }
            }
        ]
    },
    "scriptFile": "txml_processing_functions.py",
    "output": [
        {
            "epKey": "TestMethodologyCreateProtocolMixCommand4TableData",
            "scriptVarName": "TableData"
        }
    ]
}
'''


def get_bad_input_string():
    return '''
{
    "id": "Right.CreateProtocolMix.TableData",
    "entryFunction": "config_table_data",
    "input": {
        "customDict": {
            "EnableVlan": ["True", "True"],
            "Weight": ["10", "20"]
        },
        "interfaceDict": [
            {
                "ClassName": "Ipv4If",
                "ParentTagName": "ttIpv4If",
                "StmPropertyModifierDict": {
                    "Gateway": {
                        "Start": ["1.1.1.1"],
                        "Step": ["0.0.1.0", "0.0.1.0"]
                    },
                    "Address": {
                        "Start": ["1.1.1.2", "1.1.1.2"],
                        "Step": ["0.0.1.0", "0.0.1.0"]
                    }
                }
            },
            {
                "ClassName": "VlanIf",
                "ParentTagName": "ttVlanIf",
                "StmPropertyModifierDict": {
                    "VlanId": {
                        "Start": ["100", "100"],
                        "Step": ["0", "1"]
                    }
                }
            }
        ],
        "protocolDict": [
            {
                "ClassName": "BlahConfig",
                "ParentTagName": "ttBlahConfig",
                "EnableProperty": ["False", "False"],
                "StmPropertyModifierDict": {
                    "DutAsNum": {
                        "Start": "100",
                        "Step": "1"
                    },
                    "AsNum": {
                        "Start": "100",
                        "Step": "1"
                    }
                }
            },
            {
                "ClassName": "BfdRouterConfig",
                "ParentTagName": "ttBfdRouterConfig",
                "PropertyValueDict": {
                    "DetectMultiplier": ["1", "99"],
                    "TxInterval": ["2", "99"],
                    "RxInterval": ["3", "99"]
                }
            },
            {
                "ClassName": "BgpRouterConfig",
                "ParentTagName": "ttBgpRouterConfig",
                "EnableProperty": ["True", "False"],
                "StmPropertyModifierDict": {
                    "DutAsNum": {
                        "Start": ["100", "0"],
                        "Step": ["1", "0"]
                    },
                    "AsNum": {
                        "Start": ["100", "0"],
                        "Step": ["1", "0"]
                    }
                },
                "PropertyValueDict": {
                    "IpVersion": ["IPV4", "IPV4"],
                    "EnableBfd": ["True", "False"]
                }
            },
            {
                "ClassName": "Ospfv2RouterConfig",
                "ParentTagName": "ttOspfv2RouterConfig",
                "EnableProperty": ["False", "True"],
                "PropertyValueDict": {
                    "AreaId": ["0", "3"],
                    "EnableBfd": ["True", "False"]
                }
            }
        ]
    },
    "scriptFile": "txml_processing_functions.py",
    "output": [
        {
            "epKey": "TestMethodologyCreateProtocolMixCommand4TableData",
            "scriptVarName": "TableData"
        }
    ]
}
'''
