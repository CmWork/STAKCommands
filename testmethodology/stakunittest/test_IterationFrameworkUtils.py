from StcIntPythonPL import *
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
import spirent.methodology.utils.iteration_framework_utils as iter_utils


TM_PKG = "spirent.methodology"


def check_iter_to_config_chain(iter_cmd, config_cmd_list):
    assert iter_cmd.IsTypeOf(TM_PKG + ".iteratorcommand")
    iter_prop_chain_list = iter_cmd.GetObjects("PropertyChainingConfig")
    assert iter_prop_chain_list is not None

    exp_target_list = []
    for config_cmd in config_cmd_list:
        assert config_cmd.IsTypeOf(TM_PKG + ".iteratorconfigcommand") is True
        exp_target_list.append(config_cmd.GetObjectHandle())

    found_curr_val = False
    found_iteration = False
    for prop_chain in iter_prop_chain_list:
        target_cmd = prop_chain.GetObject("Command", RelationType("PropertyChain"))
        assert target_cmd is not None
        if target_cmd.IsTypeOf(TM_PKG + ".IteratorConfigCommand") is False:
            continue
        assert target_cmd.GetObjectHandle() in exp_target_list

        curr_val_id = TM_PKG + ".iteratorcommand.currval"
        iteration_id = TM_PKG + ".iteratorcommand.iteration"
        if str(prop_chain.Get("SourcePropertyId")) == curr_val_id:
            temp = TM_PKG + ".iteratorconfigcommand.currval"
            assert str(prop_chain.Get("TargetPropertyId")) == temp
            found_curr_val = True
        elif str(prop_chain.Get("SourcePropertyId")) == iteration_id:
            temp = TM_PKG + ".iteratorconfigcommand.iteration"
            assert str(prop_chain.Get("TargetPropertyId")) == temp
            found_iteration = True

    assert found_curr_val is True
    assert found_iteration is True


def check_iter_to_valid_chain(iter_cmd, valid_cmd_list):
    assert iter_cmd.IsTypeOf(TM_PKG + ".iteratorcommand")
    iter_prop_chain_list = iter_cmd.GetObjects("PropertyChainingConfig")
    assert iter_prop_chain_list is not None

    exp_target_list = []
    for valid_cmd in valid_cmd_list:
        assert valid_cmd.IsTypeOf(TM_PKG + ".iteratorvalidatecommand")
        exp_target_list.append(valid_cmd.GetObjectHandle())

    for prop_chain in iter_prop_chain_list:
        target_cmd = prop_chain.GetObject("Command", RelationType("PropertyChain"))
        assert target_cmd is not None
        if target_cmd.IsTypeOf(TM_PKG + ".IteratorValidateCommand") is False:
            continue
        assert target_cmd.GetObjectHandle() in exp_target_list

        assert str(prop_chain.Get("SourcePropertyId")) == \
            TM_PKG + ".iteratorcommand.iteration"
        assert str(prop_chain.Get("TargetPropertyId")) == \
            TM_PKG + ".iteratorvalidatecommand.iteration"


def check_valid_to_iter_chain(valid_cmd, iter_cmd):
    assert iter_cmd.IsTypeOf(TM_PKG + ".iteratorcommand")
    assert valid_cmd.IsTypeOf(TM_PKG + ".iteratorvalidatecommand")
    valid_prop_chain_list = valid_cmd.GetObjects("PropertyChainingConfig")
    assert valid_prop_chain_list is not None
    assert len(valid_prop_chain_list) == 1
    prop_chain = valid_prop_chain_list[0]

    assert str(prop_chain.Get("SourcePropertyId")) == \
        TM_PKG + ".iteratorvalidatecommand.verdict"
    assert str(prop_chain.Get("TargetPropertyId")) == \
        TM_PKG + ".iteratorcommand.previterverdict"

    target_cmd = prop_chain.GetObject("Command", RelationType("PropertyChain"))
    assert target_cmd is not None
    assert target_cmd.IsTypeOf(TM_PKG + ".IteratorCommand")
    assert target_cmd.GetObjectHandle() == iter_cmd.GetObjectHandle()


def test_get_configurator_cmds(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    while_cmd = ctor.Create("SequencerWhileCommand", sequencer)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    valid_cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    # Not really valid but useful for testing
    config_cmd3 = ctor.Create(TM_PKG + ".IteratorConfigCommand", sequencer)
    while_cmd2 = ctor.Create("SequencerWhileCommand", sequencer)
    sequencer.SetCollection("CommandList",
                            [while_cmd.GetObjectHandle(),
                             config_cmd3.GetObjectHandle(),
                             while_cmd2.GetObjectHandle()])

    cmd_list = iter_utils.get_configurator_cmds(
        sequencer.GetCollection("CommandList"))
    assert cmd_list
    assert len(cmd_list) == 1
    assert cmd_list[0].GetObjectHandle() == config_cmd3.GetObjectHandle()

    cmd_list = iter_utils.get_configurator_cmds(
        while_cmd.GetCollection("CommandList"))
    assert cmd_list
    assert len(cmd_list) == 2
    for cmd in cmd_list:
        assert cmd.GetObjectHandle() in [config_cmd2.GetObjectHandle(),
                                         config_cmd.GetObjectHandle()]

    cmd_list = iter_utils.get_configurator_cmds(
        while_cmd2.GetCollection("CommandList"))
    assert len(cmd_list) == 0


def test_get_validator_cmds(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    while_cmd = ctor.Create("SequencerWhileCommand", sequencer)
    iter_cmd = ctor.Create(TM_PKG + ".IteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    valid_cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(), config_cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    # Not really valid but useful for testing
    valid_cmd2 = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)
    while_cmd2 = ctor.Create("SequencerWhileCommand", sequencer)
    sequencer.SetCollection("CommandList",
                            [while_cmd.GetObjectHandle(), valid_cmd2.GetObjectHandle(),
                             while_cmd2.GetObjectHandle()])

    cmd_list = iter_utils.get_validator_cmds(sequencer.GetCollection("CommandList"))
    assert cmd_list
    assert len(cmd_list) == 1
    assert cmd_list[0].GetObjectHandle() == valid_cmd2.GetObjectHandle()

    cmd_list = iter_utils.get_validator_cmds(while_cmd.GetCollection("CommandList"))
    assert cmd_list
    assert len(cmd_list) == 1
    assert cmd_list[0].GetObjectHandle() == valid_cmd.GetObjectHandle()

    cmd_list = iter_utils.get_validator_cmds(while_cmd2.GetCollection("CommandList"))
    assert len(cmd_list) == 0


def test_build_iterator_to_configurator_property_chains(stc):
    ctor = CScriptableCreator()

    iter_cmd = ctor.CreateCommand(TM_PKG + ".IteratorCommand")
    config_cmd = ctor.CreateCommand(TM_PKG + ".IteratorConfigCommand")
    config_cmd2 = ctor.CreateCommand(TM_PKG + ".IteratorConfigCommand")

    iter_utils.build_iterator_to_configurator_property_chains(iter_cmd, [config_cmd, config_cmd2])

    # Check the property chain objects on the iterator propagating to configurator
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])


def test_build_iterator_to_validator_property_chains(stc):
    ctor = CScriptableCreator()

    iter_cmd = ctor.CreateCommand(TM_PKG + ".IteratorCommand")
    valid_cmd = ctor.CreateCommand(TM_PKG + ".IteratorValidateCommand")

    iter_utils.build_iterator_to_validator_property_chains(iter_cmd, valid_cmd)

    # Check the property chain objects on the iterator
    # propagating to the validator
    check_iter_to_valid_chain(iter_cmd, [valid_cmd])


def test_build_validator_to_iterator_property_chains(stc):
    ctor = CScriptableCreator()

    iter_cmd = ctor.CreateCommand(TM_PKG + ".IteratorCommand")
    valid_cmd = ctor.CreateCommand(TM_PKG + ".IteratorValidateCommand")

    iter_utils.build_validator_to_iterator_property_chains(valid_cmd, iter_cmd)

    # Check the property chain objects on the iterator
    # propagating to configurator
    check_valid_to_iter_chain(valid_cmd, iter_cmd)


def test_get_sequencer_while_expression_cmd(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", sequencer)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    valid_cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(), config_cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    act_cmd = iter_utils.get_sequencer_while_expression_cmd(while_cmd)
    assert act_cmd is not None
    assert act_cmd.GetObjectHandle() == iter_cmd.GetObjectHandle()

    # PassFailCommand (returns None)
    while_cmd2 = ctor.Create("SequencerWhileCommand", sequencer)
    pass_fail_cmd = ctor.Create("Dhcpv6BindWaitCommand", while_cmd2)
    config_cmd3 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd2)
    config_cmd4 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd2)
    valid_cmd2 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd2)
    while_cmd2.Set("ExpressionCommand", pass_fail_cmd.GetObjectHandle())
    while_cmd2.SetCollection("CommandList",
                             [config_cmd3.GetObjectHandle(), config_cmd4.GetObjectHandle(),
                              valid_cmd2.GetObjectHandle()])
    act_cmd = iter_utils.get_sequencer_while_expression_cmd(while_cmd2)
    assert act_cmd is None


def test_build_iteration_framework_property_chains_simple(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # IteratorValidateCommand
    # SequencerWhileCommand
    #     ObjectIteratorCommand
    #     IteratorConfigCommand
    #     IteratorConfigCommand
    #     CreateTemplateConfigCommand
    #     IteratorValidateCommand
    # IteratorValidateCommand

    cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", sequencer)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    cmd2 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd)
    valid_cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])

    cmd4 = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)
    sequencer.SetCollection("CommandList", [cmd.GetObjectHandle(),
                                            while_cmd.GetObjectHandle(),
                                            cmd4.GetObjectHandle()])

    # Build the property chains
    iter_utils.build_iteration_framework_property_chains(
        sequencer.GetCollection("CommandList"))

    # Check the property chains
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])
    check_valid_to_iter_chain(valid_cmd, iter_cmd)
    check_iter_to_valid_chain(iter_cmd, [valid_cmd])


def test_build_iteration_framework_property_chains_simple_group(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # IteratorValidateCommand
    # SequencerGroupCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         IteratorConfigCommand
    #         CreateTemplateConfigCommand
    #         IteratorValidateCommand
    #     IteratorValidateCommand
    # IteratorValidateCommand

    cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)

    # SequencerGroupCommand
    group_cmd = ctor.Create("SequencerGroupCommand", sequencer)

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    cmd2 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd)
    valid_cmd = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])

    cmd4 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd)

    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle(),
                                            cmd4.GetObjectHandle()])

    cmd5 = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)

    sequencer.SetCollection("CommandList", [cmd.GetObjectHandle(),
                                            group_cmd.GetObjectHandle(),
                                            cmd5.GetObjectHandle()])

    # Build the property chains
    iter_utils.build_iteration_framework_property_chains(
        sequencer.GetCollection("CommandList"))

    # Check the property chains
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])
    check_valid_to_iter_chain(valid_cmd, iter_cmd)
    check_iter_to_valid_chain(iter_cmd, [valid_cmd])


def test_build_iteration_framework_property_chains_complex(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # SequencerGroupCommand
    #     CreateTemplateConfigCommand
    #     CreateTemplateConfigCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         IteratorConfigCommand
    #         CreateTemplateConfigCommand
    #         WaitForPropertyValueCommand
    #         SequencerGroupCommand
    #             SequencerWhileCommand
    #                 ObjectIteratorCommand
    #                 IteratorConfigCommand
    #                 IteratorValidateCommand
    #             SequencerGroupCommand
    #                 SequencerWhileCommand
    #                     Dhcpv6BindWaitCommand
    #                     CreateTemplateConfigCommand
    #                     IteratorValidateCommand
    #                     SequencerGroupCommand
    #                         SequencerWhileCommand
    #                             ObjectIteratorCommand
    #                             IteratorValidateCommand
    #                 CreateTemplateConfigCommand
    #             IteratorValidateCommand
    #         IteratorValidateCommand
    #     IteratorValidateCommand
    #     IteratorValidateCommand
    # IteratorValidateCommand

    # Group Command
    group_cmd5 = ctor.Create("SequencerGroupCommand", sequencer)

    # Set up a sequence
    cmd1 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd5)
    cmd2 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd5)

    # (outer) IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd5)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)

    cmd3 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd)
    cmd4 = ctor.Create(TM_PKG + ".WaitForPropertyValueCommand", while_cmd)

    # Group Command
    group_cmd = ctor.Create("SequencerGroupCommand", while_cmd)

    # (inner) IteratorCommand
    while_cmd2 = ctor.Create("SequencerWhileCommand", group_cmd)
    iter_cmd2 = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd2)
    config_cmd3 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd2)
    valid_cmd2 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd2)
    while_cmd2.Set("ExpressionCommand", iter_cmd2.GetObjectHandle())
    while_cmd2.SetCollection("CommandList",
                             [config_cmd3.GetObjectHandle(),
                              valid_cmd2.GetObjectHandle()])

    # (inner) Group Command
    group_cmd2 = ctor.Create("SequencerGroupCommand", group_cmd)

    while_cmd3 = ctor.Create("SequencerWhileCommand", group_cmd2)
    pass_fail_cmd = ctor.Create("Dhcpv6BindWaitCommand", while_cmd3)
    cmd5 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd3)

    # Nested combined command
    group_cmd15 = ctor.Create("SequencerGroupCommand", while_cmd3)
    while_cmd15 = ctor.Create("SequencerWhileCommand", group_cmd15)
    combined_cmd15 = ctor.Create(TM_PKG + ".ObjectIteratorCommand",
                                 while_cmd15)
    valid_cmd15 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd15)

    while_cmd15.Set("ExpressionCommand", combined_cmd15.GetObjectHandle())
    while_cmd15.SetCollection("CommandList", [valid_cmd15.GetObjectHandle()])

    group_cmd15.SetCollection("CommandList", [while_cmd15.GetObjectHandle()])

    valid_cmd3 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd3)
    while_cmd3.Set("ExpressionCommand", pass_fail_cmd.GetObjectHandle())
    while_cmd3.SetCollection("CommandList", [cmd5.GetObjectHandle(),
                                             group_cmd15.GetObjectHandle(),
                                             valid_cmd3.GetObjectHandle()])

    cmd6 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd2)

    group_cmd2.SetCollection("CommandList", [while_cmd3.GetObjectHandle(),
                                             cmd6.GetObjectHandle()])

    cmd7 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd)

    group_cmd.SetCollection("CommandList",
                            [while_cmd2.GetObjectHandle(),
                             group_cmd2.GetObjectHandle(),
                             cmd7.GetObjectHandle()])

    valid_cmd4 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)

    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             cmd3.GetObjectHandle(), cmd4.GetObjectHandle(),
                             group_cmd.GetObjectHandle(),
                             valid_cmd4.GetObjectHandle()])

    cmd8 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd5)
    cmd9 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd5)

    group_cmd5.SetCollection("CommandList",
                             [cmd1.GetObjectHandle(),
                              cmd2.GetObjectHandle(),
                              while_cmd.GetObjectHandle(),
                              cmd8.GetObjectHandle(),
                              cmd9.GetObjectHandle()])
    cmd10 = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)

    sequencer.SetCollection("CommandList",
                            [group_cmd5.GetObjectHandle(),
                             cmd10.GetObjectHandle()])

    # Build the property chains
    iter_utils.build_iteration_framework_property_chains(
        sequencer.GetCollection("CommandList"))

    # Check the property chains
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])
    check_valid_to_iter_chain(valid_cmd4, iter_cmd)
    check_iter_to_valid_chain(iter_cmd, [valid_cmd4])

    check_iter_to_config_chain(iter_cmd2, [config_cmd3])
    check_valid_to_iter_chain(valid_cmd2, iter_cmd2)
    check_iter_to_valid_chain(iter_cmd2, [valid_cmd2])

    # Check lack of property chains (negative test)
    prop_chain_list = while_cmd3.GetObjects("PropertyChainingConfig")
    assert prop_chain_list == []


def test_get_all_configurator_recursive(stc):
    ctor = CScriptableCreator()

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    # Sequencer Command List will look as follows:
    #
    # SequencerGroupCommand
    #     CreateTemplateConfigCommand
    #     CreateTemplateConfigCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         IteratorConfigCommand
    #         CreateTemplateConfigCommand
    #         WaitForPropertyValueCommand
    #         SequencerGroupCommand
    #             SequencerWhileCommand
    #                 ObjectIteratorCommand
    #                 IteratorConfigCommand
    #                 IteratorValidateCommand
    #             SequencerGroupCommand
    #                 SequencerWhileCommand
    #                     Dhcpv6BindWaitCommand
    #                     CreateTemplateConfigCommand
    #                     IteratorValidateCommand
    #                     SequencerGroupCommand
    #                         SequencerWhileCommand
    #                             ObjectIteratorCommand
    #                             IteratorValidateCommand
    #                 CreateTemplateConfigCommand
    #             IteratorValidateCommand
    #         IteratorValidateCommand
    #     IteratorValidateCommand
    #     IteratorValidateCommand
    # IteratorValidateCommand

    # Group Command
    group_cmd5 = ctor.Create("SequencerGroupCommand", sequencer)

    # Set up a sequence
    cmd1 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd5)
    cmd2 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd5)

    # (outer) IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd5)
    iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd)

    cmd3 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd)
    cmd4 = ctor.Create(TM_PKG + ".WaitForPropertyValueCommand", while_cmd)

    # Group Command
    group_cmd = ctor.Create("SequencerGroupCommand", while_cmd)

    # (inner) IteratorCommand
    while_cmd2 = ctor.Create("SequencerWhileCommand", group_cmd)
    iter_cmd2 = ctor.Create(TM_PKG + ".ObjectIteratorCommand", while_cmd2)
    config_cmd3 = ctor.Create(TM_PKG + ".IteratorConfigCommand", while_cmd2)
    valid_cmd2 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd2)
    while_cmd2.Set("ExpressionCommand", iter_cmd2.GetObjectHandle())
    while_cmd2.SetCollection("CommandList",
                             [config_cmd3.GetObjectHandle(),
                              valid_cmd2.GetObjectHandle()])

    # (inner) Group Command
    group_cmd2 = ctor.Create("SequencerGroupCommand", group_cmd)

    while_cmd3 = ctor.Create("SequencerWhileCommand", group_cmd2)
    pass_fail_cmd = ctor.Create("Dhcpv6BindWaitCommand", while_cmd3)
    cmd5 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", while_cmd3)

    # Nested iterator command
    group_cmd15 = ctor.Create("SequencerGroupCommand", while_cmd3)
    while_cmd15 = ctor.Create("SequencerWhileCommand", group_cmd15)
    nested_iter_cmd = ctor.Create(TM_PKG + ".ObjectIteratorCommand",
                                  while_cmd15)
    valid_cmd15 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd15)

    while_cmd15.Set("ExpressionCommand", nested_iter_cmd.GetObjectHandle())
    while_cmd15.SetCollection("CommandList", [valid_cmd15.GetObjectHandle()])

    group_cmd15.SetCollection("CommandList", [while_cmd15.GetObjectHandle()])

    valid_cmd3 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd3)
    while_cmd3.Set("ExpressionCommand", pass_fail_cmd.GetObjectHandle())
    while_cmd3.SetCollection("CommandList", [cmd5.GetObjectHandle(),
                                             group_cmd15.GetObjectHandle(),
                                             valid_cmd3.GetObjectHandle()])

    cmd6 = ctor.Create(TM_PKG + ".CreateTemplateConfigCommand", group_cmd2)

    group_cmd2.SetCollection("CommandList", [while_cmd3.GetObjectHandle(),
                                             cmd6.GetObjectHandle()])

    cmd7 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd)

    group_cmd.SetCollection("CommandList",
                            [while_cmd2.GetObjectHandle(),
                             group_cmd2.GetObjectHandle(),
                             cmd7.GetObjectHandle()])

    valid_cmd4 = ctor.Create(TM_PKG + ".IteratorValidateCommand", while_cmd)

    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             cmd3.GetObjectHandle(),
                             cmd4.GetObjectHandle(),
                             group_cmd.GetObjectHandle(),
                             valid_cmd4.GetObjectHandle()])

    cmd8 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd5)
    cmd9 = ctor.Create(TM_PKG + ".IteratorValidateCommand", group_cmd5)

    group_cmd5.SetCollection("CommandList", [cmd1.GetObjectHandle(),
                                             cmd2.GetObjectHandle(),
                                             while_cmd.GetObjectHandle(),
                                             cmd8.GetObjectHandle(),
                                             cmd9.GetObjectHandle()])
    cmd10 = ctor.Create(TM_PKG + ".IteratorValidateCommand", sequencer)

    sequencer.SetCollection("CommandList", [group_cmd5.GetObjectHandle(),
                                            cmd10.GetObjectHandle()])

    # Find all the IteratorConfigCommands
    act_cmd_list = \
        iter_utils.get_all_configurator_cmds(
            sequencer.GetCollection("CommandList"))

    # Check the output
    assert len(act_cmd_list) == 3
    act_cmd_hnd_list = []
    for cmd in act_cmd_list:
        act_cmd_hnd_list.append(cmd.GetObjectHandle())
    assert config_cmd.GetObjectHandle() in act_cmd_hnd_list
    assert config_cmd2.GetObjectHandle() in act_cmd_hnd_list
    assert config_cmd3.GetObjectHandle() in act_cmd_hnd_list


def test_frame_size_parser():
    res = iter_utils.parse_iterate_mode_input("fixed(135)")
    assert res is not None
    assert res["type"] == "fixed"
    assert res["start"] == "135"
    res = iter_utils.parse_iterate_mode_input("fixed ( 135    )")
    assert res is not None
    assert res["type"] == "fixed"
    assert res["start"] == "135"
    res = iter_utils.parse_iterate_mode_input("incr(128,64,1024)")
    assert res is not None
    assert res["type"] == "incr"
    assert res["start"] == "128"
    assert res["step"] == "64"
    assert res["end"] == "1024"
    res = iter_utils.parse_iterate_mode_input("incr (128 ,64 ,1024 )")
    assert res["type"] == "incr"
    assert res["start"] == "128"
    assert res["step"] == "64"
    assert res["end"] == "1024"
    res = iter_utils.parse_iterate_mode_input("rand(128,256)")
    assert res["type"] == "rand"
    assert res["start"] == "128"
    assert res["end"] == "256"
    res = iter_utils.parse_iterate_mode_input("rand ( 128 , 256)")
    assert res["type"] == "rand"
    assert res["start"] == "128"
    assert res["end"] == "256"
    res = iter_utils.parse_iterate_mode_input("imix(spirent)")
    assert res["type"] == "imix"
    assert res["name"] == "spirent"
    res = iter_utils.parse_iterate_mode_input(" imix (spirent )")
    assert res["type"] == "imix"
    assert res["name"] == "spirent"
    res = iter_utils.parse_iterate_mode_input("fixedrand (342)")
    assert res is None
    res = iter_utils.parse_iterate_mode_input("(128, 256)")
    assert res is None
    res = iter_utils.parse_iterate_mode_input("fixed(256")

    # Enhancement to allow integer frame sizes
    # that are implicitly of the fixed type
    res = iter_utils.parse_iterate_mode_input("123")
    assert res["type"] == "fixed"
    assert res["start"] == "123"
    res = iter_utils.parse_iterate_mode_input("123.4")
    assert res["type"] == "fixed"
    assert res["start"] == "123.4"
    res = iter_utils.parse_iterate_mode_input("123.0")
    assert res["type"] == "fixed"
    assert res["start"] == "123.0"
