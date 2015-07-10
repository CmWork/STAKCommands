from StcIntPythonPL import *
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
from manager.utils.sequencer_utils import \
    MethodologyGroupCommandUtils as MethodologyGroupCommandUtils


def check_sequenceable_properties(sp, exp_val):
    # If SequenceableProperties is None, the expected value
    # must be True as that is the default (in which case no
    # SequenceableProperties object is necessary and might
    # not exist).
    if sp is None:
        assert exp_val is True
    assert sp.Get("AllowDelete") is exp_val
    assert sp.Get("AllowMove") is exp_val
    assert sp.Get("AllowUngroup") is exp_val
    assert sp.Get("AllowDisable") is exp_val
    assert sp.Get("ShowEditor") is exp_val


def test_bind_sequenceable_properties(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Call function with invalid command (nothing will happen)
    MethodologyGroupCommandUtils.bind_sequenceable_properties(None, True)

    # Create a command without sequenceable properties
    pkg = "spirent.methodology"
    cmd = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    assert cmd is not None
    sp = cmd.GetObject("SequenceableCommandProperties",
                       RelationType("SequenceableProperties"))
    assert sp is None

    # Call the bind_sequenceable_properties function
    # Make read only
    MethodologyGroupCommandUtils.bind_sequenceable_properties(cmd, False)
    sp = cmd.GetObject("SequenceableCommandProperties",
                       RelationType("SequenceableProperties"))
    assert sp is not None
    check_sequenceable_properties(sp, False)

    # Make writeable
    MethodologyGroupCommandUtils.bind_sequenceable_properties(cmd, True)
    check_sequenceable_properties(sp, True)


def test_set_sequenceable_properties(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # IterationGroupCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         LoadTemplateCommand
    #         IteratorValidateCommand

    pkg = "spirent.methodology"
    group_cmd = ctor.Create(pkg + ".IterationGroupCommand", sequencer)
    assert group_cmd is not None

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    assert while_cmd is not None
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", while_cmd)
    assert iter_cmd is not None
    config_cmd = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    assert config_cmd is not None
    net_prof_cmd = ctor.Create(pkg + ".LoadTemplateCommand", while_cmd)
    assert net_prof_cmd is not None
    valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand", while_cmd)
    assert valid_cmd is not None
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             net_prof_cmd.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])
    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle()])
    all_cmd_list = [group_cmd, while_cmd, iter_cmd,
                    config_cmd, net_prof_cmd, valid_cmd]

    MethodologyGroupCommandUtils.set_sequenceable_properties(
        sequencer.GetCollection("CommandList"), False)
    sp_list = sequencer.GetObjects("SequenceableCommandProperties")
    plLogger.LogInfo("sp_list contains: " + str(len(sp_list)))
    for cmd in all_cmd_list:
        sp = cmd.GetObject("SequenceableCommandProperties",
                           RelationType("SequenceableProperties"))
        plLogger.LogInfo("cmd: " + cmd.GetType())
        assert sp is not None
        check_sequenceable_properties(sp, False)

    MethodologyGroupCommandUtils.set_sequenceable_properties(
        sequencer.GetCollection("CommandList"), True)
    for cmd in all_cmd_list:
        sp = cmd.GetObject("SequenceableCommandProperties",
                           RelationType("SequenceableProperties"))
        assert sp is not None
        check_sequenceable_properties(sp, True)


def test_insert_top_level_group_command(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")
    hnd_reg = CHandleRegistry.Instance()

    # Sequencer Command List will look as follows:
    #
    # IterationGroupCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         LoadTemplateCommand
    #         IteratorValidateCommand
    # LoadTemplateCommand

    pkg = "spirent.methodology"
    mm_pkg = pkg + ".manager"
    group_cmd = ctor.Create(pkg + ".IterationGroupCommand", sequencer)
    assert group_cmd is not None

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    assert while_cmd is not None
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", while_cmd)
    assert iter_cmd is not None
    config_cmd = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    assert config_cmd is not None
    net_prof_cmd = ctor.Create(pkg + ".LoadTemplateCommand", while_cmd)
    assert net_prof_cmd is not None
    valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand", while_cmd)
    assert valid_cmd is not None
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             net_prof_cmd.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])

    net_prof_cmd2 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    assert net_prof_cmd2 is not None
    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle(),
                                            net_prof_cmd2.GetObjectHandle()])

    # Insert the MethodologyGroupCommand
    MethodologyGroupCommandUtils.insert_top_level_group_command()

    # Validate the new sequence
    new_cmd_hnd_list = sequencer.GetCollection("CommandList")
    assert len(new_cmd_hnd_list) == 1
    tlgc_hnd = new_cmd_hnd_list[0]
    assert tlgc_hnd is not 0
    tlgc = hnd_reg.Find(tlgc_hnd)
    assert tlgc is not None
    assert tlgc.IsTypeOf(mm_pkg + ".MethodologyGroupCommand")

    # The sequence should not have changed.
    new_group_cmd_list = tlgc.GetCollection("CommandList")
    assert new_group_cmd_list == [group_cmd.GetObjectHandle(),
                                  net_prof_cmd2.GetObjectHandle()]
    assert group_cmd.GetCollection("CommandList") == \
        [while_cmd.GetObjectHandle()]
    assert while_cmd.GetCollection("CommandList") == \
        [config_cmd.GetObjectHandle(),
         net_prof_cmd.GetObjectHandle(),
         valid_cmd.GetObjectHandle()]
    assert while_cmd.Get("ExpressionCommand") == iter_cmd.GetObjectHandle()


def test_remove_top_level_group_command(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")
    hnd_reg = CHandleRegistry.Instance()

    # Sequencer Command List will look as follows:
    #
    # MethodologyGroupCommand
    #     IterationGroupCommand
    #         SequencerWhileCommand
    #             ObjectIteratorCommand
    #             IteratorConfigCommand
    #             LoadTemplateCommand
    #             IteratorValidateCommand
    #     LoadTemplateCommand

    pkg = "spirent.methodology"
    mm_pkg = pkg + ".manager"

    tlgc = ctor.Create(mm_pkg + ".MethodologyGroupCommand", sequencer)
    assert tlgc is not None
    group_cmd = ctor.Create(pkg + ".IterationGroupCommand", sequencer)
    assert group_cmd is not None

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    assert while_cmd is not None
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", while_cmd)
    assert iter_cmd is not None
    config_cmd = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    assert config_cmd is not None
    net_prof_cmd = ctor.Create(pkg + ".LoadTemplateCommand", while_cmd)
    assert net_prof_cmd is not None
    valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand", while_cmd)
    assert valid_cmd is not None
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             net_prof_cmd.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])

    net_prof_cmd2 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    tlgc.SetCollection("CommandList", [group_cmd.GetObjectHandle(),
                                       net_prof_cmd2.GetObjectHandle()])
    sequencer.SetCollection("CommandList", [tlgc.GetObjectHandle()])

    # Remove the MethodologyGroupCommand
    MethodologyGroupCommandUtils.remove_top_level_group_command()

    # Validate the new sequence
    new_cmd_hnd_list = sequencer.GetCollection("CommandList")
    assert len(new_cmd_hnd_list) == 2

    c_group_cmd_hnd = new_cmd_hnd_list[0]
    c_net_prof_cmd_hnd2 = new_cmd_hnd_list[1]
    assert c_group_cmd_hnd is not 0
    assert c_net_prof_cmd_hnd2 is not 0

    c_group_cmd = hnd_reg.Find(c_group_cmd_hnd)
    c_net_prof_cmd2 = hnd_reg.Find(c_net_prof_cmd_hnd2)
    assert c_group_cmd is not None
    assert c_net_prof_cmd2 is not None

    assert c_group_cmd.GetObjectHandle() == group_cmd.GetObjectHandle()
    assert c_net_prof_cmd2.GetObjectHandle() == net_prof_cmd2.GetObjectHandle()

    # The sequence should not have changed
    assert c_group_cmd.GetCollection("CommandList") == \
        [while_cmd.GetObjectHandle()]
    assert while_cmd.GetCollection("CommandList") == \
        [config_cmd.GetObjectHandle(),
         net_prof_cmd.GetObjectHandle(),
         valid_cmd.GetObjectHandle()]
    assert while_cmd.Get("ExpressionCommand") == iter_cmd.GetObjectHandle()


def test_find_top_level_group_command(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # DeleteTemplatesAndGeneratedObjectsCommand
    # MethodologyGroupCommand
    # DeleteTemplatesAndGeneratedObjectsCommand

    pkg = "spirent.methodology"
    mm_pkg = pkg + ".manager"
    del_cmd1 = ctor.Create(pkg + ".DeleteTemplatesAndGeneratedObjectsCommand",
                           sequencer)
    tlgc = ctor.Create(mm_pkg + ".MethodologyGroupCommand", sequencer)
    del_cmd2 = ctor.Create(pkg + ".DeleteTemplatesAndGeneratedObjectsCommand",
                           sequencer)

    sequencer.SetCollection("CommandList", [del_cmd1.GetObjectHandle(),
                                            tlgc.GetObjectHandle(),
                                            del_cmd2.GetObjectHandle()])

    found_cmd = MethodologyGroupCommandUtils.find_top_level_group_command()
    assert found_cmd is not None
    assert found_cmd.GetObjectHandle() == tlgc.GetObjectHandle()
