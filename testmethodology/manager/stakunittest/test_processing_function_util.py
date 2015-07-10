from StcIntPythonPL import *
import spirent.methodology.manager.utils.processing_function_util \
    as process_util
import spirent.methodology.utils.json_utils as json_utils


# to be removed
def test_parse_interface_list_data(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('start.test_parse_interface_list_data')
    input_string = '''{
        "ParentTagName": "ttIpv4If",
        "ClassName": "Ipv4If",
        "PropertyValueDict": {
            "PrefixLength": ["22", "11"],
            "IfCountPerLowerIf": ["2", "1"]
        },
        "StmPropertyModifierDict": {
            "Address": {
                "Start": ["2.2.2.2", "0.0.0.0"],
                "Step": ["0.0.0.1", "0.0.0.0"]
            },
            "Gateway": {
                "Start": ["2.2.2.1", "0.0.0.0"],
                "Step": "0.0.1.0"
            }
        }
    }'''

    expected_prop_val = {}
    expected_prop_val["className"] = "Ipv4If"
    expected_prop_val["tagName"] = "ttIpv4If"
    expected_prop_val["propertyValueList"] = {}
    expected_prop_val["propertyValueList"]["PrefixLength"] = "22"
    expected_prop_val["propertyValueList"]["IfCountPerLowerIf"] = "2"

    expected_prop_mod1 = {}
    expected_prop_mod1["className"] = "Ipv4If"
    expected_prop_mod1["tagName"] = "ttIpv4If.Address"
    expected_prop_mod1["parentTagName"] = "ttIpv4If"
    expected_prop_mod1["propertyName"] = "Address"
    expected_prop_mod1["propertyValueList"] = {}
    expected_prop_mod1["propertyValueList"]["Start"] = "2.2.2.2"
    expected_prop_mod1["propertyValueList"]["Step"] = "0.0.0.1"

    expected_prop_mod2 = {}
    expected_prop_mod2["className"] = "Ipv4If"
    expected_prop_mod2["tagName"] = "ttIpv4If.Gateway"
    expected_prop_mod2["parentTagName"] = "ttIpv4If"
    expected_prop_mod2["propertyName"] = "Gateway"
    expected_prop_mod2["propertyValueList"] = {}
    expected_prop_mod2["propertyValueList"]["Start"] = "2.2.2.1"
    expected_prop_mod2["propertyValueList"]["Step"] = "0.0.1.0"

    err_str, input_table_data = json_utils.load_json(input_string)
    assert err_str == ""
    # Call parse on the first row
    res = process_util.parse_interface_data(input_table_data, 0)

    assert len(res["propertyValueList"]) == 1
    assert cmp(res["propertyValueList"][0], expected_prop_val) == 0

    assert len(res["stmPropertyModifierList"]) == 2
    assert expected_prop_mod1 in res["stmPropertyModifierList"]
    assert expected_prop_mod2 in res["stmPropertyModifierList"]


# to be removed
def test_parse_protocol_list_data(stc):
    input_string = '''{
        "EnableProperty": "Left.CreateProtocolMix.EnableBgp",
        "ParentTagName": "ttBgpRouterConfig",
        "ClassName": "BgpRouterConfig",
        "PropertyValueDict": {
          "IpVersion": ["BLAH", "IPV4"],
          "EnableBfd": ["False", "True"]
        },
        "StmPropertyModifierDict": {
          "AsNum": {
            "Start": ["0", "10"],
            "Step": ["0", "1"]
          },
          "DutAsNum": {
            "Start": ["0", "20"],
            "Step": "1"
          }
        }
      }'''

    expected_prop_val = {}
    expected_prop_val["className"] = "BgpRouterConfig"
    expected_prop_val["tagName"] = "ttBgpRouterConfig"
    expected_prop_val["propertyValueList"] = {}
    expected_prop_val["propertyValueList"]["IpVersion"] = "IPV4"
    expected_prop_val["propertyValueList"]["EnableBfd"] = "True"

    expected_prop_mod1 = {}
    expected_prop_mod1["className"] = "BgpRouterConfig"
    expected_prop_mod1["tagName"] = "ttBgpRouterConfig.AsNum"
    expected_prop_mod1["parentTagName"] = "ttBgpRouterConfig"
    expected_prop_mod1["propertyName"] = "AsNum"
    expected_prop_mod1["propertyValueList"] = {}
    expected_prop_mod1["propertyValueList"]["Start"] = "10"
    expected_prop_mod1["propertyValueList"]["Step"] = "1"

    expected_prop_mod2 = {}
    expected_prop_mod2["className"] = "BgpRouterConfig"
    expected_prop_mod2["tagName"] = "ttBgpRouterConfig.DutAsNum"
    expected_prop_mod2["parentTagName"] = "ttBgpRouterConfig"
    expected_prop_mod2["propertyName"] = "DutAsNum"
    expected_prop_mod2["propertyValueList"] = {}
    expected_prop_mod2["propertyValueList"]["Start"] = "20"
    expected_prop_mod2["propertyValueList"]["Step"] = "1"

    err_str, input_table_data = json_utils.load_json(input_string)
    assert err_str == ""

    # Call parse on the second row
    res = process_util.parse_protocol_data(input_table_data, 1)

    assert res["protocolSrcTag"] == "ttBgpRouterConfig"

    assert len(res["propertyValueList"]) == 1
    assert cmp(res["propertyValueList"][0], expected_prop_val) == 0

    assert len(res["stmPropertyModifierList"]) == 2
    assert expected_prop_mod1 in res["stmPropertyModifierList"]
    assert expected_prop_mod2 in res["stmPropertyModifierList"]


# NEW UNIT TESTS
def test_parse_prop_val_data(stc):
    input_string = '''{
        "ParentTagName": "ttIpv4If",
        "ClassName": "Ipv4If",
        "PropertyValueDict": {
            "PrefixLength": ["22", "11"],
            "IfCountPerLowerIf": ["2", "1"]
        }
    }'''

    expected_prop_val1 = {}
    expected_prop_val1["className"] = "Ipv4If"
    expected_prop_val1["tagName"] = "ttIpv4If"
    expected_prop_val1["propertyValueList"] = {}
    expected_prop_val1["propertyValueList"]["PrefixLength"] = "22"
    expected_prop_val1["propertyValueList"]["IfCountPerLowerIf"] = "2"

    expected_prop_val2 = {}
    expected_prop_val2["className"] = "Ipv4If"
    expected_prop_val2["tagName"] = "ttIpv4If"
    expected_prop_val2["propertyValueList"] = {}
    expected_prop_val2["propertyValueList"]["PrefixLength"] = "11"
    expected_prop_val2["propertyValueList"]["IfCountPerLowerIf"] = "1"

    err_str, input_table_data = json_utils.load_json(input_string)
    assert err_str == ""
    # Call parse on the first row
    res1 = process_util.parse_prop_val_data(input_table_data, 0)
    # Call parse on the second row
    res2 = process_util.parse_prop_val_data(input_table_data, 1)

    assert len(res1["propertyValueList"]) == 1
    assert cmp(res1["propertyValueList"][0], expected_prop_val1) == 0
    assert cmp(res2["propertyValueList"][0], expected_prop_val2) == 0


def test_parse_prop_mod_data(stc):
    input_string = '''{
        "ParentTagName": "ttIpv4If",
        "ClassName": "Ipv4If",
        "StmPropertyModifierDict": {
            "Address": {
                "Start": ["2.2.2.2", "3.3.3.3"],
                "Step": ["0.0.0.1", "0.0.0.0"]
            },
            "Gateway": {
                "Start": ["2.2.2.1", "3.3.3.1"],
                "Step": ["0.0.1.0", "0.0.0.1"]
            }
        }
    }'''

    expected_prop_row1_mod1 = {}
    expected_prop_row1_mod1["className"] = "Ipv4If"
    expected_prop_row1_mod1["tagName"] = "ttIpv4If.Address"
    expected_prop_row1_mod1["parentTagName"] = "ttIpv4If"
    expected_prop_row1_mod1["propertyName"] = "Address"
    expected_prop_row1_mod1["propertyValueList"] = {}
    expected_prop_row1_mod1["propertyValueList"]["Start"] = "2.2.2.2"
    expected_prop_row1_mod1["propertyValueList"]["Step"] = "0.0.0.1"

    expected_prop_row1_mod2 = {}
    expected_prop_row1_mod2["className"] = "Ipv4If"
    expected_prop_row1_mod2["tagName"] = "ttIpv4If.Gateway"
    expected_prop_row1_mod2["parentTagName"] = "ttIpv4If"
    expected_prop_row1_mod2["propertyName"] = "Gateway"
    expected_prop_row1_mod2["propertyValueList"] = {}
    expected_prop_row1_mod2["propertyValueList"]["Start"] = "2.2.2.1"
    expected_prop_row1_mod2["propertyValueList"]["Step"] = "0.0.1.0"

    expected_prop_row2_mod1 = {}
    expected_prop_row2_mod1["className"] = "Ipv4If"
    expected_prop_row2_mod1["tagName"] = "ttIpv4If.Address"
    expected_prop_row2_mod1["parentTagName"] = "ttIpv4If"
    expected_prop_row2_mod1["propertyName"] = "Address"
    expected_prop_row2_mod1["propertyValueList"] = {}
    expected_prop_row2_mod1["propertyValueList"]["Start"] = "3.3.3.3"
    expected_prop_row2_mod1["propertyValueList"]["Step"] = "0.0.0.0"

    expected_prop_row2_mod2 = {}
    expected_prop_row2_mod2["className"] = "Ipv4If"
    expected_prop_row2_mod2["tagName"] = "ttIpv4If.Gateway"
    expected_prop_row2_mod2["parentTagName"] = "ttIpv4If"
    expected_prop_row2_mod2["propertyName"] = "Gateway"
    expected_prop_row2_mod2["propertyValueList"] = {}
    expected_prop_row2_mod2["propertyValueList"]["Start"] = "3.3.3.1"
    expected_prop_row2_mod2["propertyValueList"]["Step"] = "0.0.0.1"

    err_str, input_table_data = json_utils.load_json(input_string)
    assert err_str == ""
    # Call parse on the first row
    res1 = process_util.parse_prop_mod_data(input_table_data, 0)
    # Call parse on the second row
    res2 = process_util.parse_prop_mod_data(input_table_data, 1)

    assert len(res1["stmPropertyModifierList"]) == 2
    assert expected_prop_row1_mod1 in res1["stmPropertyModifierList"]
    assert expected_prop_row1_mod2 in res1["stmPropertyModifierList"]

    assert len(res2["stmPropertyModifierList"]) == 2
    assert expected_prop_row2_mod1 in res2["stmPropertyModifierList"]
    assert expected_prop_row2_mod2 in res2["stmPropertyModifierList"]


def test_parse_merge_list_data(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('start.test_parse_merge_list_data')
    input_string = '''{
        "ClassName": "BgpRouterConfig",
        "ParentTagName": "ttBgpRouterConfig",
        "MergeSourceTemplateFile": "AllRouters.xml",
        "MergeTargetTag": "ttEmulatedDevice",
        "PropertyValueDict": {
            "IpVersion": "IPV6",
            "EnableBfd": "False"
        },
        "StmPropertyModifierDict": {
            "AsNum": {
                "Start": "10",
                "Step": "1"
            },
            "DutAsNum": {
                "Start": "20",
                "Step": "1"
            }
        }
    }'''

    expected_prop_val = {}
    expected_prop_val["className"] = "BgpRouterConfig"
    expected_prop_val["tagName"] = "ttBgpRouterConfig"
    expected_prop_val["propertyValueList"] = {}
    expected_prop_val["propertyValueList"]["IpVersion"] = "IPV6"
    expected_prop_val["propertyValueList"]["EnableBfd"] = "False"

    expected_prop_mod1 = {}
    expected_prop_mod1["className"] = "BgpRouterConfig"
    expected_prop_mod1["tagName"] = "ttBgpRouterConfig.AsNum"
    expected_prop_mod1["parentTagName"] = "ttBgpRouterConfig"
    expected_prop_mod1["propertyName"] = "AsNum"
    expected_prop_mod1["propertyValueList"] = {}
    expected_prop_mod1["propertyValueList"]["Start"] = "10"
    expected_prop_mod1["propertyValueList"]["Step"] = "1"

    expected_prop_mod2 = {}
    expected_prop_mod2["className"] = "BgpRouterConfig"
    expected_prop_mod2["tagName"] = "ttBgpRouterConfig.DutAsNum"
    expected_prop_mod2["parentTagName"] = "ttBgpRouterConfig"
    expected_prop_mod2["propertyName"] = "DutAsNum"
    expected_prop_mod2["propertyValueList"] = {}
    expected_prop_mod2["propertyValueList"]["Start"] = "20"
    expected_prop_mod2["propertyValueList"]["Step"] = "1"

    err_str, input_table_data = json_utils.load_json(input_string)
    assert err_str == ""
    res = process_util.parse_merge_list_data(input_table_data, 0)

    assert res["mergeSourceTag"] == "ttBgpRouterConfig"
    assert res["mergeTargetTag"] == "ttEmulatedDevice"

    assert len(res["propertyValueList"]) == 1
    assert cmp(res["propertyValueList"], [expected_prop_val]) == 0

    assert len(res["stmPropertyModifierList"]) == 2
    assert expected_prop_mod1 in res["stmPropertyModifierList"]
    assert expected_prop_mod2 in res["stmPropertyModifierList"]
