from StcIntPythonPL import *
from mock import MagicMock
import json
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
import spirent.methodology.IteratorConfigMixParamsCommand \
    as IteratorConfig
import spirent.methodology.utils.json_utils as json_utils


PKG = "spirent.methodology"

'''
StmTemplateMix, TagData, ObjectList,
        IgnoreEmptyTags, TagList, CurrVal, Iteration
'''


def test_validate(stc):
    res = IteratorConfig.validate("", "", "", "", "", "", "")
    assert res == ""


def test_mandatory(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    plLogger = PLLogger.GetLogger("test_mandatory")
    plLogger.LogInfo("start")

    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set('MixInfo', get_example_mix_info())
    cmd = ctor.CreateCommand(PKG + ".IteratorConfigMixParamsCommand")
    IteratorConfig.get_this_cmd = MagicMock(return_value=cmd)

    # Missing StmTemplateMix Parameter
    res = IteratorConfig.run(None, get_example_tag_data(),
                             "", "", "", "0", "")
    assert res is False

    # Invalid StmTemplateMix Parameter
    res = IteratorConfig.run(0, get_example_tag_data(),
                             "", "", "", "0", "")
    assert res is False

    # Missing 'templateConfigurator' in TagData
    res = IteratorConfig.run(trf_mix.GetObjectHandle(), "",
                             "", "", "", "0", "")
    assert res is False


def test_invalid_json(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    plLogger = PLLogger.GetLogger("test_run")
    plLogger.LogInfo("start")

    # Create Needed Objects/Commands
    mix = ctor.Create("StmTemplateMix", project)
    mix.Set('MixInfo', '{}')
    cmd = ctor.CreateCommand(PKG + ".IteratorConfigMixParamsCommand")
    IteratorConfig.get_this_cmd = MagicMock(return_value=cmd)
    assert not IteratorConfig.run(mix.GetObjectHandle(), '', '', '', '', '0', '')


def test_run(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    plLogger = PLLogger.GetLogger("test_run")
    plLogger.LogInfo("start")

    # Create Tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    trf_mix_tag = ctor.Create("Tag", tags)
    trf_mix_tag.Set('Name', "ttTemplateMix")
    temp_conf_tag = ctor.Create("Tag", tags)
    temp_conf_tag.Set("Name", "ttCreateTemplateConfigCommand")

    # Create Needed Objects/Commands
    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set('MixInfo', get_example_mix_info())
    trf_mix.AddObject(trf_mix_tag, RelationType("UserTag"))
    temp_conf_cmd = ctor.CreateCommand(PKG + ".CreateTemplateConfigCommand")
    temp_conf_cmd.AddObject(temp_conf_tag, RelationType("UserTag"))
    iter_cfg_cmd = ctor.CreateCommand(PKG + ".IteratorConfigMixParamsCommand")
    IteratorConfig.get_this_cmd = MagicMock(return_value=iter_cfg_cmd)

    # Parse example mix info
    json_str = get_example_mix_info()
    err_str, json_obj = json_utils.load_json(json_str)
    assert err_str == ""
    table_data = json_obj["components"]
    assert len(table_data) == 2

    # Row 1
    res = IteratorConfig.run(trf_mix.GetObjectHandle(), get_example_tag_data(),
                             "", "", "", "0", "")
    assert res is True

    # Validate CreateTemplateConfigCommand
    row1_str = get_expected_row1_inputJson()
    err_str, row1 = json_utils.load_json(row1_str)
    assert err_str == ""
    assert temp_conf_cmd.Get("StmTemplateMix") == trf_mix.GetObjectHandle()
    assert temp_conf_cmd.Get("InputJson") == json.dumps(row1)
    assert not temp_conf_cmd.Get("AutoExpandTemplate")

    # Row 2
    res = IteratorConfig.run(trf_mix.GetObjectHandle(), get_example_tag_data(),
                             "", "", "", "1", "")
    assert res is True

    # Validate CreateTemplateConfigCommand
    row2_str = get_expected_row2_inputJson()
    err_str, row2 = json_utils.load_json(row2_str)
    assert err_str == ""
    assert temp_conf_cmd.Get("StmTemplateMix") == trf_mix.GetObjectHandle()
    assert temp_conf_cmd.Get("InputJson") == json.dumps(row2)
    assert not temp_conf_cmd.Get("AutoExpandTemplate")


def get_example_mix_info():
    return '''
{
    "load": 50,
    "loadUnits": "FRAMES_PER_SECOND",
    "deviceCount": 100,
    "routeCount": 10,
    "components": [
        {
            "weight": "50%",
            "staticValue": 1,
            "useBlock": true,
            "useStaticValue": false,
            "baseTemplateFile": "IPv4_NoVlan.xml",
            "tagPrefix": "Right_Pppoe_",
            "modifyList": [
                {
                    "mergeList": [
                        {
                            "mergeSourceTag": "ttPppoeIf",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        },
                        {
                            "mergeSourceTag": "ttPppIf",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        },
                        {
                            "mergeSourceTag": "ttPppoeClientBlockConfig",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        }
                    ]
                },
                {
                    "pduModifierList": [
                        {
                            "templateElementTagName": "ttStreamBlock",
                            "value": "33.33.33.33",
                            "offsetReference": "ipv4_5265.sourceAddr"
                        },
                        {
                            "templateElementTagName": "ttStreamBlock",
                            "value": "44.44.44.44",
                            "offsetReference": "ipv4_5265.destAddr"
                        }
                    ]
                },
                {
                    "relationList": [
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttIpv4If",
                            "removeRelation": true,
                            "targetTag": "ttEthIIIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttIpv4If",
                            "targetTag": "ttPppIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttPppIf",
                            "targetTag": "ttPppoeIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttPppoeIf",
                            "targetTag": "ttEthIIIf"
                        }
                    ]
                }
            ]
        },
        {
            "weight": "50%",
            "staticValue": 1,
            "useBlock": true,
            "useStaticValue": false,
            "baseTemplateFile": "IPv4_NoVlan.xml",
            "tagPrefix": "Left_Pppoe_",
            "modifyList": [
                {
                    "mergeList": [
                        {
                            "mergeSourceTag": "ttPppoeIf",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        },
                        {
                            "mergeSourceTag": "ttPppIf",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        },
                        {
                            "mergeSourceTag": "ttPppoeClientBlockConfig",
                            "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                            "mergeTargetTag": "ttEmulatedDevice"
                        }
                    ]
                },
                {
                    "pduModifierList": [
                        {
                            "templateElementTagName": "ttStreamBlock",
                            "value": "44.44.44.44",
                            "offsetReference": "ipv4_5265.sourceAddr"
                        },
                        {
                            "templateElementTagName": "ttStreamBlock",
                            "value": "33.33.33.33",
                            "offsetReference": "ipv4_5265.destAddr"
                        }
                    ]
                },
                {
                    "relationList": [
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttIpv4If",
                            "removeRelation": true,
                            "targetTag": "ttEthIIIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttIpv4If",
                            "targetTag": "ttPppIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttPppIf",
                            "targetTag": "ttPppoeIf"
                        },
                        {
                            "relationType": "StackedOnEndpoint",
                            "sourceTag": "ttPppoeIf",
                            "targetTag": "ttEthIIIf"
                        }
                    ]
                }
            ]
        }
    ],
    "postExpand": {
        "relationList": {
            "relationType": "UsesIf",
            "sourceTag": "ttPppoeClientBlockConfig",
            "targetTag": "ttPppoeIf"
        },
        "streamBlockExpand": {},
        "routeImportExpand": {},
        "linkList": {}
    }
}
'''


def get_expected_row1_inputJson():
    return '''
{
    "weight": "50%",
    "staticValue": 1,
    "useBlock": true,
    "useStaticValue": false,
    "baseTemplateFile": "IPv4_NoVlan.xml",
    "tagPrefix": "Right_Pppoe_",
    "modifyList": [
        {
            "mergeList": [
                {
                    "mergeSourceTag": "ttPppoeIf",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                },
                {
                    "mergeSourceTag": "ttPppIf",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                },
                {
                    "mergeSourceTag": "ttPppoeClientBlockConfig",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                }
            ]
        },
        {
            "pduModifierList": [
                {
                    "templateElementTagName": "ttStreamBlock",
                    "value": "33.33.33.33",
                    "offsetReference": "ipv4_5265.sourceAddr"
                },
                {
                    "templateElementTagName": "ttStreamBlock",
                    "value": "44.44.44.44",
                    "offsetReference": "ipv4_5265.destAddr"
                }
            ]
        },
        {
            "relationList": [
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttIpv4If",
                    "removeRelation": true,
                    "targetTag": "ttEthIIIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttIpv4If",
                    "targetTag": "ttPppIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttPppIf",
                    "targetTag": "ttPppoeIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttPppoeIf",
                    "targetTag": "ttEthIIIf"
                }
            ]
        }
    ]
}
'''


def get_expected_row2_inputJson():
    return '''
{
    "weight": "50%",
    "staticValue": 1,
    "useBlock": true,
    "useStaticValue": false,
    "baseTemplateFile": "IPv4_NoVlan.xml",
    "tagPrefix": "Left_Pppoe_",
    "modifyList": [
        {
            "mergeList": [
                {
                    "mergeSourceTag": "ttPppoeIf",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                },
                {
                    "mergeSourceTag": "ttPppIf",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                },
                {
                    "mergeSourceTag": "ttPppoeClientBlockConfig",
                    "mergeSourceTemplateFile": "unit_test_pppoe_template.xml",
                    "mergeTargetTag": "ttEmulatedDevice"
                }
            ]
        },
        {
            "pduModifierList": [
                {
                    "templateElementTagName": "ttStreamBlock",
                    "value": "44.44.44.44",
                    "offsetReference": "ipv4_5265.sourceAddr"
                },
                {
                    "templateElementTagName": "ttStreamBlock",
                    "value": "33.33.33.33",
                    "offsetReference": "ipv4_5265.destAddr"
                }
            ]
        },
        {
            "relationList": [
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttIpv4If",
                    "removeRelation": true,
                    "targetTag": "ttEthIIIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttIpv4If",
                    "targetTag": "ttPppIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttPppIf",
                    "targetTag": "ttPppoeIf"
                },
                {
                    "relationType": "StackedOnEndpoint",
                    "sourceTag": "ttPppoeIf",
                    "targetTag": "ttEthIIIf"
                }
            ]
        }
    ]
}
'''


def get_example_tag_data():
    return '''
{
    "templateConfigurator": "ttCreateTemplateConfigCommand",
    "stmTemplateMix": "ttTemplateMix"
}
'''
