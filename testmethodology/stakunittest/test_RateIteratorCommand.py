from StcIntPythonPL import *


# Run the RateIteratorCommand
def run_rate_iter(min_val, max_val, iter_val, prev_res,
                  curr_val, min_fail, max_pass, res, res_mode):
    # Using this function treats the RateIteratorCommand as being
    # recreated each time it is executed.
    # Because of this, the state parameters must be reset to the
    # correct state before the command
    # can be run again.

    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("spirent.methodology.RateIterator")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("Resolution", float(res))
    cmd.Set("ResolutionMode", res_mode)

    if iter_val > 0:
        cmd.Set("Iteration", iter_val)
        cmd.Set("PrevIterVerdict", prev_res)
        cmd.Set("CurrVal", float(curr_val))
        cmd.Set("MinFail", min_fail)
        cmd.Set("MaxPass", max_pass)

    cmd.Execute()
    res = {"iteration": cmd.Get("Iteration"),
           "curr_val": cmd.Get("CurrVal"),
           "min_fail": cmd.Get("MinFail"),
           "max_pass": cmd.Get("MaxPass"),
           "state": cmd.Get("PassFailState"),
           "is_converged": cmd.Get("IsConverged"),
           "converged_val": cmd.Get("ConvergedVal")}

    cmd.MarkDelete()

    return res


def test_calc_asb_resolution():
    from ..RateIteratorCommand import calc_abs_resolution

    assert calc_abs_resolution(1.0, 10.0, 20.0, "PERCENT") == 1.8
    assert calc_abs_resolution(0.0, 10.0, 20.0, "PERCENT") == 2.0
    assert calc_abs_resolution(1.0, 10.0, 2.0, "ABSOLUTE") == 2.0


def test_is_resolution():
    from ..RateIteratorCommand import is_resolution

    assert is_resolution(8.0, 3.0, 2.0) is False
    assert is_resolution(8.0, 7.0, 2.0) is True
    assert is_resolution(10.0, 9.0, 2.0) is True


def test_all_pass(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.5
    res_mode = "PERCENT"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val,
                        res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "799.5"
    assert float(res["min_fail"]) == 1532.0
    assert float(res["max_pass"]) == 67.0
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True,
                        res["curr_val"], res["min_fail"], res["max_pass"],
                        res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1165.75"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1348.875"
    assert res["max_pass"] == 1165.75
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1440.4375"
    assert res["max_pass"] == 1348.875
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1486.21875"
    assert res["max_pass"] == 1440.4375
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1532.0"
    assert res["max_pass"] == 1486.21875
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7 (not a real iteration - this will break out of
    # the SequencerWhileCommand) the "iteration" should still be 5
    # as nothing was run
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "1532.0"
    assert res["max_pass"] == 1532.0
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 6
    assert res["is_converged"] is True
    assert res["converged_val"] == "1532.0"


def test_all_fail(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.5
    res_mode = "PERCENT"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0,
                        res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "799.5"
    assert float(res["min_fail"]) == 1532.0
    assert float(res["max_pass"]) == 67.0
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "433.25"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 799.5
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "250.125"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 433.25
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "158.5625"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 250.125
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_rate_iter(min_val, max_val, res["iteration"],
                        False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "112.78125"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 158.5625
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "67.0"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 112.78125
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7 (not a real iteration - this will break out of the SequencerWhileCommand)
    # the "iteration" should still be 5 as nothing was run
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "67.0"
    assert res["max_pass"] == 67.0
    assert res["min_fail"] == 67.0
    assert res["iteration"] == 6
    assert res["is_converged"] is False
    assert res["converged_val"] is ""


def test_pass_fail_mix(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.5
    res_mode = "PERCENT"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "799.5"
    assert float(res["min_fail"]) == 1532.0
    assert float(res["max_pass"]) == 67.0
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1165.75"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "982.625"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1165.75
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1074.1875"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1165.75
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1028.40625"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1074.1875
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "982.625"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1028.40625
    assert res["iteration"] == 5
    assert res["is_converged"] is True
    assert res["converged_val"] == "982.625"


def test_pass_fail_mix_res_absolute(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.8
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "799.5"
    assert float(res["min_fail"]) == 1532.0
    assert float(res["max_pass"]) == 67.0
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1165.75"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "982.625"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1165.75
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1074.1875"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1165.75
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1028.40625"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1074.1875
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1005.515625"
    assert res["max_pass"] == 982.625
    assert res["min_fail"] == 1028.40625
    assert res["iteration"] == 6
    assert res["is_converged"] is False

    # Iteration 7
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1016.9609375"
    assert res["max_pass"] == 1005.515625
    assert res["min_fail"] == 1028.40625
    assert res["iteration"] == 7
    assert res["is_converged"] is False

    # Iteration 8
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1011.23828125"
    assert res["max_pass"] == 1005.515625
    assert res["min_fail"] == 1016.9609375
    assert res["iteration"] == 8
    assert res["is_converged"] is False

    # Iteration 9 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "1011.23828125"
    assert res["max_pass"] == 1011.23828125
    assert res["min_fail"] == 1016.9609375
    assert res["iteration"] == 8
    assert res["is_converged"] is True
    assert res["converged_val"] == "1011.23828125"


def test_fail_on_max_res_absolute(stc):
    min_val = 1
    max_val = 2
    res_val = 0.1
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1.5"
    assert float(res["max_pass"]) == 1
    assert float(res["min_fail"]) == 2
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1.75"
    assert res["max_pass"] == 1.5
    assert res["min_fail"] == 2
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1.875"
    assert res["max_pass"] == 1.75
    assert res["min_fail"] == 2
    assert res["iteration"] == 3
    assert res["is_converged"] is False

    # Iteration 4
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1.9375"
    assert res["max_pass"] == 1.875
    assert res["min_fail"] == 2
    assert res["iteration"] == 4
    assert res["is_converged"] is False

    # Iteration 5
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "2.0"
    assert res["max_pass"] == 1.9375
    assert res["min_fail"] == 2
    assert res["iteration"] == 5
    assert res["is_converged"] is False

    # Iteration 6 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "2.0"
    assert res["max_pass"] == 1.9375
    assert res["min_fail"] == 2
    assert res["iteration"] == 5
    assert res["is_converged"] is True
    assert res["converged_val"] == "1.9375"


def test_min_equal_max_all_pass(stc):
    min_val = 2
    max_val = 2
    res_val = 1
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "2.0"
    assert float(res["max_pass"]) == 2
    assert float(res["min_fail"]) == 2
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "2.0"
    assert res["max_pass"] == 2
    assert res["min_fail"] == 2
    assert res["iteration"] == 1
    assert res["is_converged"] is True
    assert res["converged_val"] == "2.0"


def test_min_equal_max_all_fail(stc):
    min_val = 2
    max_val = 2
    res_val = 0
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "2.0"
    assert float(res["max_pass"]) == 2
    assert float(res["min_fail"]) == 2
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "2.0"
    assert res["max_pass"] == 2
    assert res["min_fail"] == 2
    assert res["iteration"] == 1
    assert res["is_converged"] is False
    assert res["converged_val"] == ""


def test_res_equal_to_range_all_pass(stc):
    min_val = 30
    max_val = 40
    res_val = 10
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 40.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "40.0"


def test_res_equal_to_range_all_fail(stc):
    min_val = 30
    max_val = 40
    res_val = 10
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 30.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False
    assert res["converged_val"] == ""


def test_res_equal_to_range_mix_pass_fail(stc):
    min_val = 30
    max_val = 40
    res_val = 10
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "35.0"


def test_res_equal_to_range_mix_fail_pass(stc):
    min_val = 30
    max_val = 40
    res_val = 10
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "30.0"


# The next four test cases test when resolution is greater than the start range
# The behavior of this scenario should be the same as when resolution equals start range

def test_res_greater_than_range_all_pass(stc):
    min_val = 30
    max_val = 40
    res_val = 100
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 40.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "40.0"


def test_res_greater_than_range_all_fail(stc):
    min_val = 30
    max_val = 40
    res_val = 100
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 30.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False
    assert res["converged_val"] == ""


def test_res_greater_than_range_mix_pass_fail(stc):
    min_val = 30
    max_val = 40
    res_val = 100
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "40.0"
    assert res["max_pass"] == 35.0
    assert res["min_fail"] == 40
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "35.0"


def test_res_greater_than_range_mix_fail_pass(stc):
    min_val = 30
    max_val = 40
    res_val = 100
    res_mode = "ABSOLUTE"

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "35.0"
    assert float(res["max_pass"]) == 30
    assert float(res["min_fail"]) == 40
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], False, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 (not a real iteration - this will break out of the SequencerWhileCommand)
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "FAILED"
    assert res["curr_val"] == "30.0"
    assert res["max_pass"] == 30
    assert res["min_fail"] == 35.0
    assert res["iteration"] == 2
    assert res["is_converged"] is True
    assert res["converged_val"] == "30.0"


def test_break_on_fail(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.5
    res_mode = "PERCENT"

    ctor = CScriptableCreator()

    # Iteration 1
    res = run_rate_iter(min_val, max_val, 0, True, "", 0.0, 0.0, res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "799.5"
    assert float(res["min_fail"]) == 1532.0
    assert float(res["max_pass"]) == 67.0
    assert res["iteration"] == 1
    assert res["is_converged"] is False

    # Iteration 2
    res = run_rate_iter(min_val, max_val, res["iteration"], True, res["curr_val"],
                        res["min_fail"], res["max_pass"], res_val, res_mode)
    assert res["state"] == "PASSED"
    assert res["curr_val"] == "1165.75"
    assert res["max_pass"] == 799.5
    assert res["min_fail"] == 1532.0
    assert res["iteration"] == 2
    assert res["is_converged"] is False

    # Iteration 3 - Test the BreakOnFail parameter
    cmd = ctor.CreateCommand("spirent.methodology.RateIterator")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("Resolution", float(res_val))
    cmd.Set("ResolutionMode", res_mode)
    cmd.Set("Iteration", 2)
    cmd.Set("PrevIterVerdict", False)
    cmd.Set("CurrVal", res["curr_val"])
    cmd.Set("MinFail", res["min_fail"])
    cmd.Set("MaxPass", res["max_pass"])
    cmd.Set("BreakOnFail", True)
    cmd.Execute()
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("CurrVal") == "1165.75"
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("ResetState") is True
    assert cmd.Get("IsConverged") is False
    assert cmd.Get("ConvergedVal") is ""

    cmd.MarkDelete()


def test_reset_iterator_state(stc):
    min_val = 67.0
    max_val = 1532.0
    res_val = 5.5
    res_mode = "PERCENT"

    pkg = "spirent.methodology"
    ctor = CScriptableCreator()

    # Use defaults and check reset state isn't set yet
    # (it shouldn't be using defaults)
    cmd = ctor.CreateCommand(pkg + ".RateIteratorCommand")
    cmd.Execute()

    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("IsConverged") is False
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("ResetState") is False
    assert cmd.Get("CurrVal") == "50.0"

    # Set up the command to simulate a "last" iteration
    cmd.Reset()
    cmd.Set("Iteration", 5)
    cmd.Set("MaxVal", max_val)
    cmd.Set("MinVal", min_val)
    cmd.Set("Resolution", res_val)
    cmd.Set("ResolutionMode", res_mode)
    cmd.Set("MaxPass", 982.625)
    cmd.Set("MinFail", 1074.1875)
    cmd.Set("CurrVal", "1028.40625")
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()

    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("Iteration") == 5
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1028.40625"
    assert cmd.Get("ResetState") is True

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


def test_validate():
    from ..RateIteratorCommand import validate
    # Min < Max
    assert validate(False, 1, 10, True, 1, "ABSOLUTE", 0) == ""
    # Min == Max
    assert validate(False, 10, 10, True, 1, "ABSOLUTE", 0) == ""
    # Min > Max
    assert validate(False, 10, 1, True, 1, "ABSOLUTE", 0) == "ERROR: MinVal must be less " + \
                                                             "than or equal to MaxVal."


def test_validate_rounding():
    from ..RateIteratorCommand import validate_rounding
    # No rounding: OK
    assert validate_rounding(0, 10, 1, "ABSOLUTE", 0) == ""

    # Rounding with round res == res, not OK
    assert validate_rounding(0, 10, 1, "ABSOLUTE", 1) != ""
    assert validate_rounding(0, 10, 1, "PERCENT", 0.1) != ""

    # Rounding with round res == 1/2 res, OK
    assert validate_rounding(0, 10, 1, "ABSOLUTE", 0.5) == ""
    assert validate_rounding(0, 10, 1, "PERCENT", 0.05) == ""

    # Rounding resolutions of only 1, 2, 5, 25 * 10^x supported
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 5) == ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 2.5) == ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 2) == ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 1) == ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 0.1) == ""

    assert validate_rounding(0, 100, 10, "ABSOLUTE", 4) != ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 2.2) != ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 3) != ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 1.1) != ""
    assert validate_rounding(0, 100, 10, "ABSOLUTE", 0.6) != ""
