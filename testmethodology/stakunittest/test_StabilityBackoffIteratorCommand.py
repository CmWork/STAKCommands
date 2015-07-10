from StcIntPythonPL import *
from spirent.methodology.StabilityBackoffIteratorCommand import \
    is_value_stable, end_iteration_early, validate


def test_is_value_stable():
    # Function prototype:
    # is_value_stable(trial_num, success_count, repeat_count, success_percent)
    assert is_value_stable(4, 4, 4, 100.0) is True
    assert is_value_stable(3, 3, 4, 100.0) is False
    assert is_value_stable(2, 2, 4, 100.0) is False
    assert is_value_stable(3, 3, 4, 76.0) is False
    assert is_value_stable(3, 3, 4, 74.0) is True


def test_end_iteration_early(stc):
    # Function prototype:
    # end_iteration_early(trial_num, success_count, repeat_count, success_percent)
    assert end_iteration_early(1, 1, 4, 100.0) is False
    assert end_iteration_early(1, 0, 4, 100.0) is True
    assert end_iteration_early(2, 2, 4, 74.0) is False
    assert end_iteration_early(2, 2, 4, 76.0) is False
    assert end_iteration_early(3, 2, 4, 76.0) is True


def test_validate(stc):
    # Function prototype:
    # validate(StepVal, RepeatCount, SuccessPercent, ValueType,
    #          ValueList, BreakOnFail, MinVal, MaxVal, PrevIterVerdict)
    res = validate(1, "1", 100, "LIST",
                   ["1", "2", "3"], True, "1", "2", False)
    assert res == ""
    # Check list contents
    res = validate(1, 1, 100.0, "LIST",
                   [], True, "1", "2", False)
    assert res == "ValueType is LIST so ValueList must contain elements."
    # Check Range MinVal and MaxVal
    res = validate(1, 1, 100.0, "RANGE",
                   [], True, "2", "1", False)
    assert res == "MinVal must be less than (or equal to) MaxVal."
    # Check Range for StepVal == 0
    res = validate(0, 1, 100.0, "RANGE",
                   [], True, "1", "2", False)
    assert res == "MinVal and MaxVal must be the same if StepVal is 0."
    # Check RepeatCount >= 1
    res = validate(1, 0, 100.0, "RANGE",
                   [], True, "1", "2", False)
    assert res == "RepeatCount must be at least 1."
    res = validate(1, 1, -10.0, "RANGE",
                   [], True, "1", "2", False)
    # Check SuccessPercent limits
    assert res == "SuccessPercent must be between 0 and 100 inclusive."
    res = validate(1, 1, 101, "RANGE",
                   [], True, "1", "2", False)
    assert res == "SuccessPercent must be between 0 and 100 inclusive."


# Test iterator where all trials and iterations pass.  In this case,
# the first value (max_val) will be reported as the stable value
# after repeat_count number of trials are run (all in Iteration 1).
def test_backoff_range_all_pass(stc):
    step_val = 493.0
    min_val = 67.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 3
    plLogger.LogInfo("======= Iteration 1 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 4 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 1 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("StableValue") == "1532"
    assert cmd.Get("FoundStableValue") is True

    # Clean up
    cmd.MarkDelete()


# Test iterator where all trials and iterations fail.  This test is
# set up so that the first trial of every iteration fails.  Since
# SuccessPercent is set to 100%, this means that the iterator moves
# on to the next iteration after the first trial fails.
# After all values are tested (to min_val), the iterator "fails"
# and reports that no stable value is found.
def test_backoff_range_all_fail(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 1
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1282"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 1
    plLogger.LogInfo("======= Iteration 3 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1032"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 1
    plLogger.LogInfo("======= Iteration 4 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 2 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 4 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test iterator where the last iteration is the one that produces
# the stable value.
def test_backoff_range_stable_on_last_value(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Set up the iterator to start at the beginning of the fourth
    # iteration (that is, the third iteration ended because it failed)
    cmd.Set("PrevIterVerdict", False)
    cmd.Set("Iteration", 3)
    cmd.Set("TrialNum", 1)
    cmd.Set("ResetState", False)
    cmd.Set("CurrVal", "1032.0")
    cmd.Set("SuccessCount", 0)

    # Iteration 4 Trial 1
    plLogger.LogInfo("======= Iteration 4 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 2
    plLogger.LogInfo("======= Iteration 4 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 3
    plLogger.LogInfo("======= Iteration 4 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 4 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 4 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True
    assert cmd.Get("StableValue") == "1000"

    # Clean up
    cmd.MarkDelete()


# Test iterator where the very last trial of the last iteration
# fails, forcing the iterator to determine that a stable value
# could not be found.
def test_backoff_range_fail_on_very_last_trial(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Set up the iterator to start at the beginning of the fourth
    # iteration (that is, the third iteration ended because it failed)
    cmd.Set("PrevIterVerdict", False)
    cmd.Set("Iteration", 3)
    cmd.Set("TrialNum", 1)
    cmd.Set("ResetState", False)
    cmd.Set("CurrVal", "1032.0")
    cmd.Set("SuccessCount", 0)

    # Iteration 4 Trial 1 (pass)
    plLogger.LogInfo("======= Iteration 4 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 2 (pass)
    plLogger.LogInfo("======= Iteration 4 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 3 (pass)
    plLogger.LogInfo("======= Iteration 4 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 4 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 4 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test iterator under conditions were various trials fail
# as the iteration proceeds (eventually a stable value is found)
def test_backoff_range_mix_pass_fail(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2 (Iter 1 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 1 (Iter 1 Trial 2 failed)
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1282"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 2 (Iter 2 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 2 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1282"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 3 (Iter 2 Trial 2 passed)
    plLogger.LogInfo("======= Iteration 2 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1282"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 1 (Iter 2 Trial 3 failed)
    plLogger.LogInfo("======= Iteration 3 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1032"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 2 (Iter 3 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1032"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 3 (Iter 3 Trial 2 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1032"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 4 (Iter 3 Trial 3 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1032"
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True
    assert cmd.Get("StableValue") == "1032"

    # Clean up
    cmd.MarkDelete()


# Test iterator under conditions were less than 100% SuccessPercent is
# required.  In this case, some of the trials pass, some fail, but a
# stable value should be found.
def test_backoff_range_pass_less_than_hundred_percent(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 10
    success = 30

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2 (Trial 1 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 3 (Trial 2 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 4 (Trial 3 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 4
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 5 (Trial 4 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 5 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 5
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 6 (Trial 5 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 6 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 6
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 7 (Trial 6 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 7 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 6
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True

    # Clean up
    cmd.MarkDelete()


# Test iterator under conditions were less than 100% SuccessPercent is
# required.  In this case, some of the trials pass, some fail, but the
# iteration will get to a point where there aren't enough trials left in
# the iteration to find a stable value.  It should fail at that point
# and return no stable value found.
def test_backoff_range_fail_on_lack_of_trials(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1532.0
    repeat_count = 10
    success = 30

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Set up the iterator to start at the beginning of the sixth
    # trial with five failed trials
    cmd.Set("PrevIterVerdict", True)
    cmd.Set("Iteration", 1)
    cmd.Set("TrialNum", 5)
    cmd.Set("ResetState", False)
    cmd.Set("CurrVal", "1532.0")
    cmd.Set("SuccessCount", 0)

    # Iteration 1 Trial 6
    plLogger.LogInfo("======= Iteration 1 Trial 6 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 6
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 7
    plLogger.LogInfo("======= Iteration 1 Trial 7 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 7
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 8
    plLogger.LogInfo("======= Iteration 1 Trial 8 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 8
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 9
    plLogger.LogInfo("======= Iteration 1 Trial 9 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 9
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 1
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1282"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # (Rest of iteration should proceed as normal)

    # Clean up
    cmd.MarkDelete()


# Test the iterator under the really unusual conditions where
# the min and max values are the same.  In this case, it is only
# really interesting if the iterator ultimately fails.
def test_backoff_range_single_value_fail(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 1000.0
    repeat_count = 3
    success = 100

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 3
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test the iterator's ResetState.  When ResetState is set to true,
# all state parameters should be reset so that the iterator run
# from the beginning again.
def test_backoff_range_reset_state(stc):
    step_val = 493.0
    min_val = 67.0
    max_val = 1532.0
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Set some junk state data in the iterator as well
    # as ResetState to make sure things get reset
    # and the iterator is runable again.
    # (for when this iterator is nested in another)
    cmd.Set("PrevIterVerdict", True)
    cmd.Set("Iteration", 3)
    cmd.Set("TrialNum", 3)
    cmd.Set("CurrVal", max_val)
    cmd.Set("SuccessCount", 2)
    cmd.Set("ResetState", True)

    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1532"
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test iterator where all trials and iterations pass when using
# a list of values.  The list is iterated over backwards and it is
# the last value in the list that will be reported as being stable.
def test_backoff_list_all_pass(stc):
    val_list = ["0a", "1b", "2c", "3d"]
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "LIST")
    cmd.SetCollection("ValueList", val_list)

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 3
    plLogger.LogInfo("======= Iteration 1 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 4 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 1 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("StableValue") == "3d"
    assert cmd.Get("FoundStableValue") is True

    # Clean up
    cmd.MarkDelete()


# Test iterator where all trials and iterations fail when using
# a list of values.  The test is set up so that the first trial
# of every iteration fails.  Since SuccessPercent is set to 100%,
# this means that the iterator moves on to the next iteration
# after the first trial fails.  The iterator will eventually fail
# on the min_val and report no stable value.
def test_backoff_list_all_fail(stc):
    val_list = ["0a", "1b", "2c", "3d"]
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "LIST")
    cmd.SetCollection("ValueList", val_list)

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 1
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "2c"
    assert cmd.Get("CurrIndex") == 2
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 1
    plLogger.LogInfo("======= Iteration 3 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1b"
    assert cmd.Get("CurrIndex") == 1
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 1
    plLogger.LogInfo("======= Iteration 4 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "0a"
    assert cmd.Get("CurrIndex") == 0
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 4 Trial 2 (not a real trial; run to break out of loop)
    plLogger.LogInfo("======= Iteration 4 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "0a"
    assert cmd.Get("CurrIndex") == 0
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test iterator under conditions were various trials fail
# as the iteration proceeds (eventually a stable value is found)
def test_backoff_list_mix_pass_fail(stc):
    val_list = ["0a", "1b", "2c", "3d"]
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "LIST")
    cmd.SetCollection("ValueList", val_list)

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2 (Iter 1 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 1 (Iter 1 Trial 2 failed)
    plLogger.LogInfo("======= Iteration 2 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "2c"
    assert cmd.Get("CurrIndex") == 2
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 2 (Iter 2 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 2 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "2c"
    assert cmd.Get("CurrIndex") == 2
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 2 Trial 3 (Iter 2 Trial 2 passed)
    plLogger.LogInfo("======= Iteration 2 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "2c"
    assert cmd.Get("CurrIndex") == 2
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 1 (Iter 2 Trial 3 failed)
    plLogger.LogInfo("======= Iteration 3 Trial 1 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "1b"
    assert cmd.Get("CurrIndex") == 1
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 2 (Iter 3 Trial 1 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "1b"
    assert cmd.Get("CurrIndex") == 1
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 3 (Iter 3 Trial 2 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1b"
    assert cmd.Get("CurrIndex") == 1
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 3 Trial 4 (Iter 3 Trial 3 passed)
    plLogger.LogInfo("======= Iteration 3 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "1b"
    assert cmd.Get("CurrIndex") == 1
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True
    assert cmd.Get("StableValue") == "1b"

    # Clean up
    cmd.MarkDelete()


# Test the iterator's ResetState.  When ResetState is set to true,
# all state parameters should be reset so that the iterator run
# from the beginning again.
def test_backoff_list_reset_state(stc):
    val_list = ["0a", "1b", "2c", "3d"]
    repeat_count = 3
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "LIST")
    cmd.SetCollection("ValueList", val_list)

    # Set some junk state data in the iterator as well
    # as ResetState to make sure things get reset
    # and the iterator is runable again.
    # (for when this iterator is nested in another)
    cmd.Set("PrevIterVerdict", True)
    cmd.Set("Iteration", 3)
    cmd.Set("TrialNum", 3)
    cmd.Set("CurrVal", "0a")
    cmd.Set("CurrIndex", 0)
    cmd.Set("SuccessCount", 2)
    cmd.Set("ResetState", True)

    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Clean up
    cmd.MarkDelete()


# Test iterator under conditions were less than 100% SuccessPercent is
# required.  In this case, some of the trials pass, some fail, but a
# stable value should be found.
def test_backoff_list_pass_less_than_hundred_percent(stc):
    val_list = ["0a", "1b", "2c", "3d"]
    repeat_count = 10
    success = 30

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".StabilityBackoffIteratorCommand")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "LIST")
    cmd.SetCollection("ValueList", val_list)

    # Iteration 1 Trial 1
    plLogger.LogInfo("======= Iteration 1 Trial 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 1
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 2 (Trial 1 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 2
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 3 (Trial 2 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 3
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 4 (Trial 3 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 4
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 5 (Trial 4 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 5 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 5
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 6 (Trial 5 failed)
    plLogger.LogInfo("======= Iteration 1 Trial 6 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 6
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 2
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False

    # Iteration 1 Trial 7 (Trial 6 passed)
    plLogger.LogInfo("======= Iteration 1 Trial 7 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("TrialNum") == 6
    assert cmd.Get("CurrVal") == "3d"
    assert cmd.Get("CurrIndex") == 3
    assert cmd.Get("SuccessCount") == 3
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True

    # Clean up
    cmd.MarkDelete()
