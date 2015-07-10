from StcIntPythonPL import *
from mock import MagicMock
import spirent.methodology.IteratorValidateCommand \
    as IteratorValidateCommand
from spirent.methodology.results.ResultInterface \
    import ResultInterface as RI
import spirent.methodology.results.stakunittest.result_unit_test_utils \
    as test_utils
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_mgr_utils


PKG = "spirent.methodology"


def test_cmd_basic_functions(stc):
    ctor = CScriptableCreator()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")

    # Iteration Group Command
    group_cmd = ctor.Create(PKG + ".IterationGroupCommand", sequencer)
    assert group_cmd

    # Sequencer While Command
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    assert while_cmd

    # Iterator Command
    iter_cmd = ctor.Create(PKG + ".ObjectIteratorCommand", while_cmd)
    assert iter_cmd

    # Iterator Validate Command
    valid_cmd = ctor.Create(PKG + ".IteratorValidateCommand", while_cmd)

    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList", [valid_cmd.GetObjectHandle()])

    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])

    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle()])

    # Mock get_this_cmd
    IteratorValidateCommand.get_this_cmd = MagicMock(return_value=valid_cmd)

    # Call the different parts of the command and verify the results
    iteration = 10
    res = IteratorValidateCommand.validate(iteration)
    assert res == ""

    res = IteratorValidateCommand.run(iteration)
    assert res is True
    assert valid_cmd.Get("Verdict") is True

    res = IteratorValidateCommand.reset()
    assert res is True


def test_cmd_with_res_fmwk(stc):
    ctor = CScriptableCreator()
    sequencer = CStcSystem.Instance().GetObject("Sequencer")

    # Set up an iteration group
    group_cmd = ctor.Create(PKG + ".IterationGroupCommand", sequencer)
    assert group_cmd
    while_cmd = ctor.Create("SequencerWhileCommand", group_cmd)
    assert while_cmd
    iter_cmd = ctor.Create(PKG + ".ObjectIteratorCommand", while_cmd)
    valid_cmd = ctor.Create(PKG + ".IteratorValidateCommand", while_cmd)

    while_cmd.Set("ExpressionCommand", iter_cmd.GetObjectHandle())
    while_cmd.SetCollection("CommandList", [valid_cmd.GetObjectHandle()])
    group_cmd.SetCollection("CommandList", [while_cmd.GetObjectHandle()])
    sequencer.SetCollection("CommandList", [group_cmd.GetObjectHandle()])

    # Setup the methodology manager and the active test case
    meth_mgr = meth_mgr_utils.get_meth_manager()
    assert meth_mgr is not None
    methodology = ctor.Create("StmMethodology", meth_mgr)
    test_case = ctor.Create("StmTestCase", methodology)
    meth_mgr_utils.set_active_test_case(test_case)
    test_case_res = meth_mgr_utils.get_stm_test_result()
    assert test_case_res is not None

    # Mock get_this_cmd
    IteratorValidateCommand.get_this_cmd = MagicMock(return_value=valid_cmd)

    # Set up the results framework (passing iteration)
    RI.create_test()
    RI.start_test()
    fs = 128
    fs_iter_id = 1
    fs_iter_hnd = iter_cmd.GetObjectHandle()
    RI.set_iterator_current_value(fs_iter_hnd, "FrameSize", fs, fs_iter_id)
    RI.add_provider_result(test_utils.dummy_verify_result_passed)
    RI.complete_iteration()

    # Call the different parts of the command and verify the results
    res = IteratorValidateCommand.run(fs_iter_id)
    assert res is True
    assert valid_cmd.Get("Verdict") is True

    # Failed iteration
    RI.set_iterator_current_value(fs_iter_hnd, "FrameSize",
                                  fs + 128, fs_iter_id + 1)
    RI.add_provider_result(test_utils.dummy_verify_result_failed)
    RI.complete_iteration()

    res = IteratorValidateCommand.run(fs_iter_id + 1)
    assert res is True
    assert valid_cmd.Get("Verdict") is False
