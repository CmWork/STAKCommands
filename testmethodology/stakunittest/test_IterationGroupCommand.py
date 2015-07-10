from StcIntPythonPL import *
import sys
import os
from mock import MagicMock
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))
from test_IterationFrameworkUtils import check_iter_to_config_chain \
    as check_iter_to_config_chain
from test_IterationFrameworkUtils import check_iter_to_valid_chain \
    as check_iter_to_valid_chain
from test_IterationFrameworkUtils import check_valid_to_iter_chain \
    as check_valid_to_iter_chain
import IterationGroupCommand


def test_cmd_iterator_configurator_run(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_cmd_run")

    # Sequencer Command List will look as follows:
    #
    # IterationGroupCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         IteratorConfigCommand
    #         CreateTemplateConfigCommand
    #         IteratorValidateCommand

    pkg = "spirent.methodology"
    group_cmd = ctor.Create(pkg + ".IterationGroupCommand", sequencer)

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    cmd2 = ctor.Create(pkg + ".CreateTemplateConfigCommand", while_cmd)
    valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])

    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle()])

    # Use MagicMock and run() instead of starting the sequencer
    # Seems to be more stable.
    #
    #    # Insert a breakpoint on the while_cmd (will cause the group command to
    #    # do a run() but no more than that)
    #    sequencer.SetCollection("BreakpointList", [while_cmd.GetObjectHandle()])

    #    # Start the Sequencer
    #    seq_start = ctor.CreateCommand("SequencerStart")
    #    seq_start.Execute()
    #    seq_start.MarkDelete()

    #    # Wait for the sequencer to finish (this comes from the WaitForPropertyValueCommand)
    #    res = ut_utils.wait_for_object_state([sequencer.GetObjectHandle()], "Sequencer",
    #                                         "State", "PAUSE", 5, 30)
    #    assert res is True

    # Mock the get_this_cmd() function
    IterationGroupCommand.get_this_cmd = MagicMock(return_value=group_cmd)

    # Call run
    IterationGroupCommand.run([])

    # Check the property chain objects on the iterator propagating to the configurator
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])

    # Check the property chain objects on the iterator propagating to the validator
    check_iter_to_valid_chain(iter_cmd, [valid_cmd])

    # Check the property chain objects on the validator propagating back to the iterator
    check_valid_to_iter_chain(valid_cmd, iter_cmd)

    # # Stop the sequencer
    # seq_stop = ctor.CreateCommand("SequencerStop")
    # seq_stop.Execute()
    # seq_stop.MarkDelete()
    # res = ut_utils.wait_for_object_state([sequencer.GetObjectHandle()], "Sequencer",
    #                                      "State", "IDLE", 5, 30)
    # assert sequencer.Get("State") == "IDLE"


def test_nested_groups(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("test_cmd_run")
    project = stc_sys.GetObject("Project")

    # Sequencer Command List will look as follows:
    #
    # IterationGroupCommand
    #     SequencerWhileCommand
    #         ObjectIteratorCommand
    #         IteratorConfigCommand
    #         IteratorConfigCommand
    #         IterationGroupCommand
    #             SequencerWhileCommand
    #                 ObjectIteratorCommand
    #                 IteratorConfigCommand
    #                 CreateTemplateConfigCommand
    #                 IteratorValidateCommand
    #         CreateTemplateConfigCommand
    #         IteratorValidateCommand

    pkg = "spirent.methodology"
    group_cmd = ctor.Create(pkg + ".IterationGroupCommand", sequencer)
    group_cmd.SetCollection("ObjectList", [project.GetObjectHandle()])

    # IteratorCommand
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand", while_cmd)
    config_cmd = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)
    config_cmd2 = ctor.Create(pkg + ".IteratorConfigCommand", while_cmd)

    # Contained iteration group
    inner_group_cmd = ctor.Create(pkg + ".IterationGroupCommand", while_cmd)
    inner_while_cmd = ctor.Create("SequencerWhileCommand", inner_group_cmd)
    inner_iter_cmd = ctor.Create(pkg + ".ObjectIteratorCommand",
                                 inner_while_cmd)
    inner_config_cmd = ctor.Create(pkg + ".IteratorConfigCommand",
                                   inner_while_cmd)
    inner_cmd2 = ctor.Create(pkg + ".CreateTemplateConfigCommand",
                             inner_while_cmd)
    inner_valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand",
                                  inner_while_cmd)

    inner_while_cmd.Set("ExpressionCommand", inner_iter_cmd.GetObjectHandle())
    inner_while_cmd.SetCollection("CommandList",
                                  [inner_config_cmd.GetObjectHandle(),
                                   inner_cmd2.GetObjectHandle(),
                                   inner_valid_cmd.GetObjectHandle()])

    cmd2 = ctor.Create(pkg + ".CreateTemplateConfigCommand", while_cmd)
    valid_cmd = ctor.Create(pkg + ".IteratorValidateCommand", while_cmd)
    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList",
                            [config_cmd.GetObjectHandle(),
                             config_cmd2.GetObjectHandle(),
                             inner_group_cmd.GetObjectHandle(),
                             cmd2.GetObjectHandle(),
                             valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])

    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle()])

    # Mock the get_this_cmd() function
    IterationGroupCommand.get_this_cmd = MagicMock(return_value=group_cmd)

    # Call run
    IterationGroupCommand.run([])

    assert len(iter_cmd.GetObjects("PropertyChainingConfig")) > 0

    # Check the property chain objects on the iterator propagating
    # to the configurator
    check_iter_to_config_chain(iter_cmd, [config_cmd, config_cmd2])

    # Check the property chain objects on the iterator propagating
    # to the validator
    check_iter_to_valid_chain(iter_cmd, [valid_cmd])

    # Check the property chain objects on the validator propagating
    # back to the iterator
    check_valid_to_iter_chain(valid_cmd, iter_cmd)

    # Check that the inner IterationGroupCommand does NOT have
    # property chains.  This command does not recursively build
    # property chains - the inner group's chains will be built
    # when it is run.
    assert len(inner_iter_cmd.GetObjects("PropertyChainingConfig")) == 0
    assert len(inner_config_cmd.GetObjects("PropertyChainingConfig")) == 0
    assert len(inner_valid_cmd.GetObjects("PropertyChainingConfig")) == 0

    # Check the inner IterationGroupCommand's ObjectList:
    assert inner_group_cmd.GetCollection("ObjectList") == [project.GetObjectHandle()]
