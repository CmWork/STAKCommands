from StcIntPythonPL import *
import spirent.methodology.CreateProtocolMixCommand2 as CreateProtoMixCmd
import json
from mock import MagicMock
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils


PKG = "spirent.methodology"


def test_validate(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)
    CreateProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)
    res = CreateProtoMixCmd.validate("", "", "", False)
    assert res == ""


def test_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)

    cmd_hnd_list = cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + ".IterationGroupCommand")

    cmd_hnd_list = grp_cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf("SequencerWhileCommand")

    exp_cmd_hnd = while_cmd.Get("ExpressionCommand")
    exp_cmd = hnd_reg.Find(exp_cmd_hnd)
    assert exp_cmd
    assert exp_cmd.IsTypeOf(PKG + ".ObjectIteratorCommand")

    cmd_hnd_list = while_cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 2
    conf_cmd_hnd = cmd_hnd_list[0]
    conf_cmd = hnd_reg.Find(conf_cmd_hnd)
    assert conf_cmd
    assert conf_cmd.IsTypeOf(PKG + ".IteratorConfigMixParamsCommand")

    ctc_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert ctc_cmd
    assert ctc_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")


def test_re_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    # Create the command.  init() is called when the command is created
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)

    # Mock get_this_cmd
    CreateProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Check that init() was invoked
    cmd_hnd_list = cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + ".IterationGroupCommand")
    child_list = cmd.GetObjects("Command")
    assert len(child_list) == 1
    assert child_list[0].GetObjectHandle() == grp_cmd.GetObjectHandle()

    # Make some change in the contained sequence to simulate
    # an author modifying the contained sequence
    cmd_hnd_list = grp_cmd.GetCollection("CommandList")
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf("SequencerWhileCommand")

    cmd_hnd_list = while_cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 2

    iter_valid_cmd = ctor.Create(PKG + ".IteratorValidateCommand", while_cmd)
    cmd_hnd_list.append(iter_valid_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList", cmd_hnd_list)

    # Call init() again.  This is invoked when the command is "created"
    # again.  This appears to happen when a saved sequence with this
    # command in it is loaded.
    CreateProtoMixCmd.init()

    # Check that the original sequence did not change, that is,
    # the sequence wasn't pre-filled again.
    cmd_hnd_list = cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 1
    grp_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert grp_cmd.IsTypeOf(PKG + ".IterationGroupCommand")
    child_list = cmd.GetObjects("Command")
    assert len(child_list) == 1
    assert child_list[0].GetObjectHandle() == grp_cmd.GetObjectHandle()

    # Find the inserted command to prove that the original sequence
    # was not overwritten
    cmd_hnd_list = grp_cmd.GetCollection("CommandList")
    while_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert while_cmd.IsTypeOf("SequencerWhileCommand")
    cmd_hnd_list = while_cmd.GetCollection("CommandList")
    assert len(cmd_hnd_list) == 3

    conf_cmd = hnd_reg.Find(cmd_hnd_list[0])
    assert conf_cmd
    assert conf_cmd.IsTypeOf(PKG + ".IteratorConfigMixParamsCommand")

    ctc_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert ctc_cmd
    assert ctc_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")

    valid_cmd = hnd_reg.Find(cmd_hnd_list[2])
    assert valid_cmd
    assert valid_cmd.IsTypeOf(PKG + ".IteratorValidateCommand")


def test_run(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)

    plLogger = PLLogger.GetLogger("test_CreateProtocolMixCommand2.test_run")
    plLogger.LogInfo("start")

    CreateProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)
    ret_val = CreateProtoMixCmd.run(get_example_mix_info(), "UnitTestProtoMix", "", False)
    assert cmd.Get("Status") == ""
    assert ret_val
    
    # Check the created StmTemplateMix
    mix_hnd = cmd.Get('StmTemplateMix')
    mix = hnd_reg.Find(mix_hnd)
    assert mix
    assert mix.Get('MixInfo') == get_example_mix_info()
    
    # Find the tagged commands
    tag_json = cmd.Get("GroupCommandTagInfo")
    assert tag_json != ""
    tag_dict = json_utils.load_json(tag_json)

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["rowIterator"]])
    assert len(tagged_obj_list) == 1
    obj_iter = tagged_obj_list[0]
    assert obj_iter.IsTypeOf(PKG + ".ObjectIteratorCommand")
    assert obj_iter.Get("StepVal") == 1
    assert obj_iter.Get("MaxVal") == 0.0
    assert obj_iter.Get("MinVal") == 0.0
    assert obj_iter.Get("IterMode") == "STEP"
    assert obj_iter.Get("ValueType") == "RANGE"

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["rowConfigurator"]])
    assert len(tagged_obj_list) == 1
    config_cmd = tagged_obj_list[0]
    assert config_cmd.IsTypeOf(PKG + ".IteratorConfigMixParamsCommand")
    assert mix_hnd == config_cmd.Get('StmTemplateMix')

    # Check the created StmProtocolMix
    proto_mix_hnd = cmd.Get("StmTemplateMix")
    proto_mix = hnd_reg.Find(proto_mix_hnd)
    assert proto_mix

    # Check the Tag
    tags = project.GetObject("Tags")
    assert tags
    user_tag_list = tags.GetObjects("Tag")
    assert len(user_tag_list)
    exp_tag = None
    for user_tag in user_tag_list:
        if user_tag.Get("Name") == "UnitTestProtoMix":
            exp_tag = user_tag
            break
    assert exp_tag
    tag_target = exp_tag.GetObject("StmTemplateMix", RelationType("UserTag", 1))
    assert tag_target
    assert tag_target.GetObjectHandle() == proto_mix.GetObjectHandle()

    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["templateConfigurator"]])
    assert len(tagged_obj_list) == 1
    ctc_cmd = tagged_obj_list[0]
    assert ctc_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")
    ctc_input_mix_hnd = ctc_cmd.Get("StmTemplateMix")
    assert ctc_input_mix_hnd == proto_mix.GetObjectHandle()


def test_on_complete(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    proto_mix = ctor.Create("StmProtocolMix", project)
    proto_mix.Set("MixInfo", get_example_mix_info())
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)
    cmd.Set("MixInfo", get_example_mix_info())
    cmd.Set("MixTagName", "test_StmProtoMix")
    cmd.Set("PortGroupTagList", "port group tag")
    cmd.Set('StmTemplateMix', proto_mix.GetObjectHandle())
    cmd.Set("AutoExpandTemplateMix", False)
    CreateProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)
    CreateProtoMixCmd.on_complete([])

    # Check the MixInfo
    mi = proto_mix.Get("MixInfo")
    mi_dict = json_utils.load_json(mi)
    assert "deviceCount" in mi_dict.keys()
    assert mi_dict["deviceCount"] == 100
    assert "components" in mi_dict.keys()
    ti_count = 0
    for item in mi_dict["components"]:
        assert "weight" in item.keys()
        assert item["weight"] == "12.1 %"
        assert "devicesPerBlock" in item.keys()
        assert item["devicesPerBlock"] == 0
        assert "baseTemplateFile" in item.keys()
        assert item["baseTemplateFile"] == "IPv4_NoVlan.xml"
        ti_count = ti_count + 1
    assert ti_count == 1


def test_on_complete_multi_row(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start_test_on_complete_multi_row")

    # Create MixInfo with multiple rows
    mix_info = json_utils.load_json(get_example_mix_info())
    components = mix_info["components"]

    # Duplicate row 4x and change weight
    row_template = components[0]
    row_1 = dict.copy(row_template)
    row_1["weight"] = "50.0 %"
    row_2 = dict.copy(row_template)
    row_2["weight"] = "25.0 %"
    row_3 = dict.copy(row_template)
    row_3["weight"] = "15.0 %"
    row_4 = dict.copy(row_template)
    row_4["weight"] = "10.0 %"
    
    mix_info["components"] = [row_1, row_2, row_3, row_4]
    proto_mix = ctor.Create("StmProtocolMix", project)
    proto_mix.Set("MixInfo", str(json.dumps(mix_info)))
    cmd = ctor.Create(PKG + ".CreateProtocolMixCommand2", sequencer)
    cmd.Set("MixInfo", str(mix_info))
    cmd.Set("MixTagName", "test_StmProtoMix_multirows")
    cmd.Set("PortGroupTagList", "port group tag")
    cmd.Set('StmTemplateMix', proto_mix.GetObjectHandle())
    cmd.Set("AutoExpandTemplateMix", False)
    CreateProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)
    CreateProtoMixCmd.on_complete([])

    # Check the MixInfo
    mi = proto_mix.Get("MixInfo")
    mi_dict = json_utils.load_json(mi)
    plLogger.LogInfo("mi: " + str(mi))
    plLogger.LogInfo("mi_dict: " + str(mi_dict))
    assert "deviceCount" in mi_dict.keys()
    assert mi_dict["deviceCount"] == 100
    assert "components" in mi_dict.keys()
    assert len(mi_dict["components"]) == 4
    a_row_1 = mi_dict["components"][0]
    assert a_row_1["weight"] == "50.0 %"
    a_row_2 = mi_dict["components"][1]
    assert a_row_2["weight"] == "25.0 %"
    a_row_3 = mi_dict["components"][2]
    assert a_row_3["weight"] == "15.0 %"
    a_row_4 = mi_dict["components"][3]
    assert a_row_4["weight"] == "10.0 %"


def get_example_mix_info():
    return """
{
    "deviceCount": 100,
    "components": [
        {
            "devicesPerBlock": 0,
            "modifyList": [
                {
                    "mergeList": [
                        {
                            "propertyValueList": [
                                {
                                    "className": "BgpRouterConfig",
                                    "tagName": "ttBgpRouterConfig",
                                    "propertyValueList": {
                                        "IpVersion": "IPV4",
                                        "EnableBfd": "True"
                                    }
                                }
                            ],
                            "mergeSourceTag": "ttBgpRouterConfig",
                            "mergeSourceTemplateFile": "AllRouters.xml",
                            "stmPropertyModifierList": [
                                {
                                    "className": "BgpRouterConfig",
                                    "propertyName": "DutAsNum",
                                    "parentTagName": "ttBgpRouterConfig",
                                    "tagName": "ttBgpRouterConfig.DutAsNum",
                                    "propertyValueList": {
                                        "Start": "100",
                                        "Step": "1"
                                    }
                                },
                                {
                                    "className": "BgpRouterConfig",
                                    "propertyName": "AsNum",
                                    "parentTagName": "ttBgpRouterConfig",
                                    "tagName": "ttBgpRouterConfig.AsNum",
                                    "propertyValueList": {
                                        "Start": "100",
                                        "Step": "1"
                                    }
                                }
                            ],
                            "mergeTargetTag": "ttEmulatedDevice"
                        }
                    ]
                },
                {
                    "propertyValueList": []
                },
                {
                    "stmPropertyModifierList": [
                        {
                            "className": "Ipv4If",
                            "propertyName": "Gateway",
                            "parentTagName": "ttIpv4If",
                            "tagName": "ttIpv4If.Gateway",
                            "propertyValueList": {
                                "Start": "2.2.2.1",
                                "Step": "0.0.1.0",
                                "Repeat": "5"
                            }
                        },
                        {
                            "className": "Ipv4If",
                            "propertyName": "Address",
                            "parentTagName": "ttIpv4If",
                            "tagName": "ttIpv4If.Address",
                            "propertyValueList": {
                                "Start": "2.2.2.2",
                                "Step": "0.0.1.0"
                            }
                        }
                    ]
                }
            ],
            "weight": "12.1 %",
            "baseTemplateFile": "IPv4_NoVlan.xml"
        }
    ]
}
"""
