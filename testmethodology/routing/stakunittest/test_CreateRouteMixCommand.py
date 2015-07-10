from StcIntPythonPL import *
import spirent.methodology.routing.CreateRouteMixCommand as CreateRouteMixCmd
from mock import MagicMock, patch
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils


PKG = "spirent.methodology"
RPKG = PKG + ".routing"


def test_validate(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Signature
    # validate(TargetObjectList, TargetObjectTagList, MixInfo,
    #          MixTagName, AutoExpandTemplate)
    res = CreateRouteMixCmd.validate([], [], "", "", False)
    assert res == ""
    gtc_p.stop()


def test_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)

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

    tmpl_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert tmpl_cmd
    assert tmpl_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")


def test_re_init(stc):
    hnd_reg = CHandleRegistry.Instance()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()

    # Create the command.  init() is called when the command is created
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)

    # Mock get_this_cmd
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

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
    CreateRouteMixCmd.init()

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

    tmpl_cmd = hnd_reg.Find(cmd_hnd_list[1])
    assert tmpl_cmd
    assert tmpl_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")

    valid_cmd = hnd_reg.Find(cmd_hnd_list[2])
    assert valid_cmd
    assert valid_cmd.IsTypeOf(PKG + ".IteratorValidateCommand")
    gtc_p.stop()


def test_run(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)

    plLogger = PLLogger.GetLogger("test_CreateRouteMixCommand.test_run")
    plLogger.LogInfo("start")

    # Mock get_this_cmd
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Signature
    # run(TargetObjectList, TargetObjectTagList, MixInfo,
    #          MixTagName, AutoExpandTemplate)
    CreateRouteMixCmd.run([], [], get_example_table_data(),
                          "UnitTestRouteMix", False)

    # Check the created StmTemplateMix
    route_mix_hnd = cmd.Get("StmTemplateMix")
    route_mix = hnd_reg.Find(route_mix_hnd)
    assert route_mix

    # Check the Route Mix Tag
    tags = project.GetObject("Tags")
    assert tags
    user_tag_list = tags.GetObjects("Tag")
    assert len(user_tag_list)
    exp_tag = None
    for user_tag in user_tag_list:
        if user_tag.Get("Name") == "UnitTestRouteMix":
            exp_tag = user_tag
            break
    assert exp_tag
    tag_target = exp_tag.GetObject("StmTemplateMix", RelationType("UserTag", 1))
    assert tag_target
    assert tag_target.GetObjectHandle() == route_mix.GetObjectHandle()

    # Find the tagged commands
    tag_json = cmd.Get("GroupCommandTagInfo")
    assert tag_json != ""
    err_str, tag_dict = json_utils.load_json(tag_json)
    assert err_str == ""

    # Iterator
    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["rowIterator"]])
    assert len(tagged_obj_list) == 1
    obj_iter = tagged_obj_list[0]
    assert obj_iter.IsTypeOf(PKG + ".ObjectIteratorCommand")
    assert obj_iter.Get("StepVal") == 1.0
    assert obj_iter.Get("MaxVal") == 1.0
    assert obj_iter.Get("MinVal") == 0.0
    assert obj_iter.Get("IterMode") == "STEP"
    assert obj_iter.Get("ValueType") == "RANGE"

    # Configurator
    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["rowConfigurator"]])
    assert len(tagged_obj_list) == 1
    config_cmd = tagged_obj_list[0]
    assert config_cmd.IsTypeOf(
        PKG + ".IteratorConfigMixParamsCommand")
    assert config_cmd.Get("StmTemplateMix") == route_mix.GetObjectHandle()
    assert config_cmd.Get("TagData") == cmd.Get("GroupCommandTagInfo")

    # CreateTemplateConfigCommand
    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
        [tag_dict["templateConfigurator"]])
    assert len(tagged_obj_list) == 1
    tmpl_cmd = tagged_obj_list[0]
    assert tmpl_cmd.IsTypeOf(PKG + ".CreateTemplateConfigCommand")
    assert tmpl_cmd.Get("StmTemplateMix") == route_mix.GetObjectHandle()
    gtc_p.stop()


def test_run_fail(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)

    plLogger = PLLogger.GetLogger("test_CreateRouteMixCommand.test_run_fail")
    plLogger.LogInfo("start")

    # Mock get_this_cmd
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Signature
    # run(TargetObjectList, TargetObjectTagList, MixInfo,
    #          MixTagName, AutoExpandTemplate)

    # Invalid JSON
    res = CreateRouteMixCmd.run([], [], '{"invalid_json"}',
                                "UnitTestRouteMix", False)
    assert not res
    assert "is not valid JSON" in cmd.Get("Status")

    # Invalid Sequence
    iter_group_cmd = cmd.GetObject(PKG + ".IterationGroupCommand")
    tmpl_cmd2 = ctor.Create(PKG + ".CreateTemplateConfigCommand",
                            iter_group_cmd)
    cmd_list = iter_group_cmd.GetCollection("CommandList")
    cmd_list.append(tmpl_cmd2.GetObjectHandle())
    iter_group_cmd.SetCollection("CommandList", cmd_list)

    res = CreateRouteMixCmd.run([], [], get_example_table_data(),
                                "UnitTestRouteMix", False)
    assert not res
    assert "Invalid Sequence: " in cmd.Get("Status")
    gtc_p.stop()


def test_on_complete(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    route_mix = ctor.Create("StmTemplateMix", project)
    route_mix.Set("MixInfo", get_example_table_data())
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)
    cmd.Set("MixInfo", get_example_table_data())
    cmd.SetCollection("TargetObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("AutoExpandTemplateMix", False)
    cmd.Set("StmTemplateMix", route_mix.GetObjectHandle())

    # Mock get_this_cmd
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Call on_complete
    CreateRouteMixCmd.on_complete([])

    # Check the MixInfo
    mi = route_mix.Get("MixInfo")
    err_str, mi_dict = json_utils.load_json(mi)
    assert err_str == ""
    assert mi_dict.get("routeCount", 0) == 1000
    comp_list = mi_dict.get("components", [])
    assert len(comp_list) == 2
    gtc_p.stop()


def test_on_complete_fail(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    route_mix = ctor.Create("StmTemplateMix", project)
    route_mix.Set("MixInfo", get_example_table_data())
    cmd = ctor.Create(RPKG + ".CreateRouteMixCommand", sequencer)
    cmd.Set("MixInfo", get_example_table_data())
    cmd.SetCollection("TargetObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("AutoExpandTemplateMix", False)
    cmd.Set("StmTemplateMix", route_mix.GetObjectHandle())

    # Mock get_this_cmd
    gtc_p = patch(RPKG + ".CreateRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # "Fail" one of the child commands
    iter_group_cmd = cmd.GetObject(PKG + ".IterationGroupCommand")

    # Call on_complete
    res = CreateRouteMixCmd.on_complete([iter_group_cmd])
    assert not res
    assert "CreateRouteMixCommand.on_complete(): No additional" \
        in cmd.Get("Status")


# FIXME:
# Test on_complete_autoexpand
def d_test_on_complete_with_autoexpand(stc):
    pass


def test_reset():
    res = CreateRouteMixCmd.reset()
    assert res


def get_example_table_data():
    return """
{
    "routeCount": 1000,
    "components": [
        {
            "weight": "12",
            "baseTemplateFile": "AllRouters.xml"
        },
        {
            "weight": "12.1%",
            "baseTemplateFile": "AllRouters.xml"
        }
    ]
}
"""
