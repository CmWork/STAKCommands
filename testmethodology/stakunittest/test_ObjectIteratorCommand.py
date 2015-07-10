from StcIntPythonPL import *


# Wrapper for run_obj_iter BINARY mode setting valueType to RANGE
def run_obj_iter_bin_range(start, step, max_val, iter_val, prev_res, curr_val, min_fail, max_pass):

    return run_obj_iter(start, step, max_val, iter_val, prev_res, curr_val, 0,
                        min_fail, max_pass, [], "BINARY", "RANGE")


# Wrapper for run_obj_iter BINARY mode setting valueType to LIST
def run_obj_iter_bin_list(iter_val, prev_res, curr_index, min_fail, max_pass, value_list):

    return run_obj_iter(0.0, 0.0, 0.0, iter_val, prev_res, 0, curr_index,
                        min_fail, max_pass, value_list, "BINARY", "LIST")


# Wrapper for run_obj_iter STEP mode setting valueType to RANGE
def run_obj_iter_step_range(start, step, max_val, iter_val, prev_res, curr_val):

    return run_obj_iter(start, step, max_val, iter_val, prev_res, curr_val, 0,
                        0.0, 0.0, [], "STEP", "RANGE")


# Wrapper for run_obj_iter STEP mode setting valueType to LIST
def run_obj_iter_step_list(iter_val, prev_res, curr_index, value_list):

    return run_obj_iter(0.0, 0.0, 0.0, iter_val, prev_res, 0, curr_index,
                        0.0, 0.0, value_list, "STEP", "LIST")


# Run the ObjectIteratorCommand in binary iteration mode
def run_obj_iter(start, step, max_val, iter_val, prev_res, curr_val, curr_index,
                 min_fail, max_pass, value_list, iter_mode, val_type):
    # Using this function treats the ObjectIteratorCommand
    # as being recreated each time it is executed.
    # Because of this, the state parameters must be
    # reset to the correct state before the command
    # can be run again.

    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("spirent.methodology.ObjectIterator")
    cmd.Set("MinVal", float(start))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step))
    cmd.Set("IterMode", iter_mode)
    cmd.Set("ValueType", val_type)
    cmd.SetCollection("ValueList", value_list)

    if iter_val > 0:
        cmd.Set("Iteration", iter_val)
        cmd.Set("PrevIterVerdict", prev_res)
        cmd.Set("CurrVal", float(curr_val))
        cmd.Set("CurrIndex", curr_index)
        cmd.Set("MinFail", min_fail)
        cmd.Set("MaxPass", max_pass)

    cmd.Execute()

    res = {"iteration": cmd.Get("Iteration"), "curr_val": cmd.Get("CurrVal"),
           "min_fail": cmd.Get("MinFail"), "max_pass": cmd.Get("MaxPass"),
           "state": cmd.Get("PassFailState"), "curr_index": cmd.Get("CurrIndex"),
           "is_converged": cmd.Get("IsConverged"),
           "converged_val": cmd.Get("ConvergedVal")}

    cmd.MarkDelete()

    return res


def test_range_binary_search_all_pass(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "802"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val,
                                 step_val,
                                 max_val,
                                 res["iteration"],
                                 True,
                                 res["curr_val"],
                                 res["min_fail"],
                                 res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1173"
    assert res["min_fail"] == float(1532)
    assert res["max_pass"] == float(802)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1355"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1173)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1446"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1355)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1495"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1446)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1516"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1495)
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1530"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1516)
    assert res["iteration"] == 7
    assert res["is_converged"] is False

    # Iteration 8
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1532"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1530)
    assert res["iteration"] == 8
    assert res["is_converged"] is False

    # Iteration 9 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 8 as nothing was run
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "1532"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1532)
    assert res["iteration"] == 8
    assert res["is_converged"] is True
    assert res["converged_val"] == "1532"


def test_range_binary_search_all_fail(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, False, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "802"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "438"
    assert float(res["min_fail"]) == float(802)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "256"
    assert float(res["min_fail"]) == float(438)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "165"
    assert float(res["min_fail"]) == float(256)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "116"
    assert float(res["min_fail"]) == float(165)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "95"
    assert float(res["min_fail"]) == float(116)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "81"
    assert float(res["min_fail"]) == float(95)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 7
    assert res["is_converged"] is False

    # Iteration 8
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "74"
    assert float(res["min_fail"]) == float(81)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 8
    assert res["is_converged"] is False

    # Iteration 9
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67"
    assert float(res["min_fail"]) == float(74)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 9
    assert res["is_converged"] is False

    # Iteration 10 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 9 as nothing was run
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67"
    assert float(res["min_fail"]) == float(67)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 9
    assert res["is_converged"] is False


def test_range_binary_search_rotate_pass_fail(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "802"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(1532)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1173"
    assert float(res["max_pass"]) == float(802)
    assert float(res["min_fail"]) == float(1532)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "991"
    assert float(res["max_pass"]) == float(802)
    assert float(res["min_fail"]) == float(1173)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1082"
    assert float(res["max_pass"]) == float(991)
    assert float(res["min_fail"]) == float(1173)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1040"
    assert float(res["max_pass"]) == float(991)
    assert float(res["min_fail"]) == float(1082)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1061"
    assert float(res["max_pass"]) == float(1040)
    assert float(res["min_fail"]) == float(1082)
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1054"
    assert float(res["max_pass"]) == float(1040)
    assert float(res["min_fail"]) == float(1061)
    assert res["iteration"] == 7
    assert res["is_converged"] is False

    # Iteration 8 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 8 as nothing was run
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "1054"
    assert float(res["max_pass"]) == float(1054)
    assert float(res["min_fail"]) == float(1061)
    assert res["iteration"] == 7
    assert res["is_converged"] is True
    assert res["converged_val"] == "1054"


def test_range_binary_search_rotate_fail_pass(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "802"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(1532)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "438"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(802)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "620"
    assert float(res["max_pass"]) == float(438)
    assert float(res["min_fail"]) == float(802)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "529"
    assert float(res["max_pass"]) == float(438)
    assert float(res["min_fail"]) == float(620)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "578"
    assert float(res["max_pass"]) == float(529)
    assert float(res["min_fail"]) == float(620)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "557"
    assert float(res["max_pass"]) == float(529)
    assert float(res["min_fail"]) == float(578)
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "571"
    assert float(res["max_pass"]) == float(557)
    assert float(res["min_fail"]) == float(578)
    assert res["iteration"] == 7
    assert res["is_converged"] is False

    # Iteration 8
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "564"
    assert float(res["max_pass"]) == float(557)
    assert float(res["min_fail"]) == float(571)
    assert res["iteration"] == 8
    assert res["is_converged"] is False

    # Iteration 9 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 8 as nothing was run
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "564"
    assert float(res["max_pass"]) == float(564)
    assert float(res["min_fail"]) == float(571)
    assert res["iteration"] == 8
    assert res["is_converged"] is True
    assert res["converged_val"] == "564"


def test_range_binary_search_single_val(stc):
    # Min and Max are equal, step size is 0 (or really is a "don't care")
    step_val = 0.0
    min_val = 67.0
    max_val = 67.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False


def test_range_binary_search_single_val_pass(stc):
    # Min and Max are equal, step size is 0 (or really is a "don't care")
    step_val = 0.0
    min_val = 67.0
    max_val = 67.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 True, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is True
    assert res["converged_val"] == "67"


def test_range_binary_search_single_val_step_nonzero(stc):
    # Min and Max are equal, step size is 1.
    # Apparently this makes a difference
    step_val = 1.0
    min_val = 67.0
    max_val = 67.0
    min_fail = 0.0
    max_pass = 0.0

    # Iteration 1
    res = run_obj_iter_bin_range(min_val, step_val, max_val, 0, True, "", min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"],
                                 False, res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67"
    assert float(res["max_pass"]) == float(67)
    assert float(res["min_fail"]) == float(67)
    assert res["iteration"] == 1
    assert res["is_converged"] is False


# Test fail on MaxVal, converge on one step less than that (so test
# running on all passing values until the MaxVal to converge on the
# value one step smaller than MaxVal).
def test_range_binary_search_fail_on_max_val(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Start after Iteration 7
    max_pass = 1516.0
    min_fail = 1532.0
    curr_val = 1530.0
    iteration = 7

    # Iteration 8 (fail this iteration)
    res = run_obj_iter_bin_range(min_val, step_val, max_val, iteration, True,
                                 curr_val, min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1532"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1530)
    assert res["iteration"] == 8
    assert res["is_converged"] is False

    # Iteration 9 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 8 as nothing was run.  Should have converged on 1530
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], False,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "1532"
    assert float(res["min_fail"]) == float(1532)
    assert float(res["max_pass"]) == float(1530)
    assert res["iteration"] == 8
    assert res["is_converged"] is True
    assert res["converged_val"] == "1530"


# Test pass on MinVal, converge on the MinVal (so test
# running on all failing values until the MinVal and passes there)
def test_range_binary_search_pass_on_min_val(stc):
    step_val = 7.0
    min_val = 67.0
    max_val = 1532.0
    min_fail = 0.0
    max_pass = 0.0

    # Start after Iteration 8
    max_pass = 67.0
    min_fail = 81.0
    curr_val = 74.0
    iteration = 8

    # Iteration 9
    res = run_obj_iter_bin_range(min_val, step_val, max_val, iteration, False,
                                 curr_val, min_fail, max_pass)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67"
    assert float(res["min_fail"]) == float(74)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 9
    assert res["is_converged"] is False

    # Iteration 10 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 9 as nothing was run
    res = run_obj_iter_bin_range(min_val, step_val, max_val, res["iteration"], True,
                                 res["curr_val"], res["min_fail"], res["max_pass"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67"
    assert float(res["min_fail"]) == float(74)
    assert float(res["max_pass"]) == float(67)
    assert res["iteration"] == 9
    assert res["is_converged"] is True
    assert res["converged_val"] == "67"


def test_list_binary_search_all_pass(stc):
    value_list = ["0a", "1b", "2c", "3d", "4e", "5f", "6g", "7h", "8i", "9j",
                  "10k", "11l", "12m", "13n", "14o", "15p", "16q", "17r"]

    # Iteration 1
    res = run_obj_iter_bin_list(0, True, "", 0.0, 0.0, value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "9j"
    assert res["curr_index"] == 9
    assert res["min_fail"] == float(17)
    assert res["max_pass"] == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "13n"
    assert res["curr_index"] == 13
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(9)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "15p"
    assert res["curr_index"] == 15
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(13)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "16q"
    assert res["curr_index"] == 16
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(15)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "17r"
    assert res["curr_index"] == 17
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(16)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 5 as nothing was run
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "17r"
    assert res["curr_index"] == 17
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(17)
    assert res["iteration"] == 5
    assert res["is_converged"] is True
    assert res["converged_val"] == "17r"


def test_list_binary_search_all_fail(stc):

    value_list = ["0a", "1b", "2c", "3d", "4e", "5f", "6g", "7h", "8i", "9j",
                  "10k", "11l", "12m", "13n", "14o", "15p", "16q", "17r"]

    # Iteration 1
    res = run_obj_iter_bin_list(0, True, "", 0.0, 0.0, value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "9j"
    assert res["curr_index"] == 9
    assert res["min_fail"] == float(17)
    assert res["max_pass"] == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "5f"
    assert res["curr_index"] == 5
    assert float(res["min_fail"]) == float(9)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "3d"
    assert res["curr_index"] == 3
    assert float(res["min_fail"]) == float(5)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "2c"
    assert res["curr_index"] == 2
    assert float(res["min_fail"]) == float(3)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1b"
    assert res["curr_index"] == 1
    assert float(res["min_fail"]) == float(2)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert float(res["min_fail"]) == float(1)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 6 as nothing was run
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert float(res["min_fail"]) == float(0)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 6
    assert res["is_converged"] is False


def test_list_binary_search_pass_fail(stc):
    value_list = ["0a", "1b", "2c", "3d", "4e", "5f", "6g", "7h", "8i", "9j",
                  "10k", "11l", "12m", "13n", "14o", "15p", "16q", "17r"]

    # Iteration 1
    res = run_obj_iter_bin_list(0, True, "", 0.0, 0.0, value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "9j"
    assert res["curr_index"] == 9
    assert res["min_fail"] == float(17)
    assert res["max_pass"] == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "13n"
    assert res["curr_index"] == 13
    assert float(res["min_fail"]) == float(17)
    assert float(res["max_pass"]) == float(9)
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "11l"
    assert res["curr_index"] == 11
    assert float(res["min_fail"]) == float(13)
    assert float(res["max_pass"]) == float(9)
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "10k"
    assert res["curr_index"] == 10
    assert float(res["min_fail"]) == float(11)
    assert float(res["max_pass"]) == float(9)
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 4 as nothing was run
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "10k"
    assert res["curr_index"] == 10
    assert float(res["min_fail"]) == float(11)
    assert float(res["max_pass"]) == float(10)
    assert res["iteration"] == 4
    assert res["is_converged"] is True
    assert res["converged_val"] == "10k"


def test_list_binary_search_single_val_pass(stc):
    value_list = ["0a"]

    # Iteration 1
    res = run_obj_iter_bin_list(0, True, "", 0.0, 0.0, value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert res["min_fail"] == float(0)
    assert res["max_pass"] == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_list(res["iteration"], True,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert float(res["min_fail"]) == float(0)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is True
    assert res["converged_val"] == "0a"


def test_list_binary_search_single_val_fail(stc):
    value_list = ["0a"]

    # Iteration 1
    res = run_obj_iter_bin_list(0, True, "", 0.0, 0.0, value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert res["min_fail"] == float(0)
    assert res["max_pass"] == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_bin_list(res["iteration"], False,
                                res["curr_index"], res["min_fail"], res["max_pass"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "0a"
    assert res["curr_index"] == 0
    assert float(res["min_fail"]) == float(0)
    assert float(res["max_pass"]) == float(0)
    assert res["iteration"] == 1
    assert res["is_converged"] is False


def test_step_range(stc):
    step_val = 9.0
    min_val = 7.0
    max_val = 33.0

    # Iteration 1
    res = run_obj_iter_step_range(min_val, step_val, max_val, 0, True, "")
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "7"
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_step_range(min_val, step_val, max_val,
                                  res["iteration"], True, res["curr_val"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "16"
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_step_range(min_val, step_val, max_val,
                                  res["iteration"], True, res["curr_val"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "25"
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_step_range(min_val, step_val, max_val,
                                  res["iteration"], True, res["curr_val"])
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "33"
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 4 as nothing was run
    res = run_obj_iter_step_range(min_val, step_val, max_val,
                                  res["iteration"], True, res["curr_val"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "33"
    assert res["iteration"] == 4
    assert res["is_converged"] is True
    assert res["converged_val"] == "33"


def test_step_range_single_val(stc):
    step_val = 0.0
    min_val = 7.0
    max_val = 7.0

    # Iteration 1
    res = run_obj_iter_step_range(min_val, step_val, max_val, 0, True, "")
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "7"
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_step_range(min_val, step_val, max_val,
                                  res["iteration"], True, res["curr_val"])
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "7"
    assert res["iteration"] == 1
    assert res["is_converged"] is True
    assert res["converged_val"] == "7"


def test_step_list(stc):
    value_list = ["4e", "5f", "6g", "7h"]

    # Iteration 1
    res = run_obj_iter_step_list(0, True, "", value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "4e"
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "5f"
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "6g"
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "7h"
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 4 as nothing was run
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "7h"
    assert res["iteration"] == 4
    assert res["is_converged"] is True
    assert res["converged_val"] == "7h"


def test_step_list_single_val(stc):
    value_list = ["4e"]

    # Iteration 1
    res = run_obj_iter_step_list(0, True, "", value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "4e"
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "4e"
    assert res["iteration"] == 1
    assert res["is_converged"] is True
    assert res["converged_val"] == "4e"


def test_break_on_fail(stc):
    value_list = ["4e", "5f", "6g", "7h"]

    # Iteration 1
    res = run_obj_iter_step_list(0, True, "", value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "4e"
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_obj_iter_step_list(res["iteration"], True, res["curr_index"], value_list)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "5f"
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 - Test the BreakOnFail parameter.
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("spirent.methodology.ObjectIterator")
    cmd.Set("IterMode", "STEP")
    cmd.Set("ValueType", "LIST")
    cmd.Set("CurrIndex", res["curr_index"])
    cmd.Set("Iteration", res["iteration"])
    cmd.SetCollection("ValueList", value_list)
    cmd.Set("BreakOnFail", True)
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("CurrVal") == "5f"
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("IsConverged") is False
    assert cmd.Get("ResetState") is True

    cmd.MarkDelete()


def test_reset_iterator_state(stc):
    pkg = "spirent.methodology"
    ctor = CScriptableCreator()

    # Use defaults and check reset state isn't set yet
    # (it shouldn't be using defaults)
    cmd = ctor.CreateCommand(pkg + ".ObjectIteratorCommand")
    cmd.Execute()

    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("IsConverged") is False
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("ResetState") is False
    assert cmd.Get("CurrVal") == "0"

    # Set up the command to simulate a "last" iteration
    cmd.Reset()
    cmd.Set("Iteration", 10)
    cmd.Set("IterMode", "BINARY")
    cmd.Set("MaxVal", "1000")
    cmd.Set("MinVal", "100")
    cmd.Set("StepVal", "100")
    cmd.Set("MaxPass", 500.0)
    cmd.Set("MinFail", 600.0)
    cmd.Set("CurrVal", "500")
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 10
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "500"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("PassFailState") == "FAILED"

    # Run the command again and check that it is reset
    cmd.Reset()
    cmd.Execute()
    assert cmd.Get("IsConverged") is False
    assert cmd.Get("ConvergedVal") == ""
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("ResetState") is False
    assert cmd.Get("PassFailState") == "PASSED"

    # Clean up
    cmd.MarkDelete()
