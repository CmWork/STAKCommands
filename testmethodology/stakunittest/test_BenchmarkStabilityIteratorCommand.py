from StcIntPythonPL import *
from spirent.methodology.BenchmarkStabilityIteratorCommand import \
    validate


def test_validate():
    # Function prototype:
    # validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict,
    #          IterMode, StepVal, ValueType, ValueList,
    #          RepeatCount, SuccessPercent, EnableStabilityBackoff):
    res = validate(True, "1", "100", False,
                   "SEARCH", "2", "LIST", ["1", "2", "3"],
                   4, 100.0, True)
    assert res == ""
    # Check list contents
    res = validate(True, "1", "100", False,
                   "SEARCH", 2, "LIST", [],
                   4, 100.0, True)
    assert res == "ValueType is LIST so ValueList must contain elements."
    # Check Range MinVal and MaxVal
    res = validate(True, "100", "1", False,
                   "SEARCH", 2, "RANGE", [],
                   4, 100.0, True)
    assert res == "MinVal must be less than (or equal to) MaxVal."
    # Check Range for StepVal == 0
    res = validate(True, "1", "100", False,
                   "SEARCH", 0, "RANGE", [],
                   4, 100.0, True)
    assert res == "MinVal and MaxVal must be the same if StepVal is 0."
    # Check RepeatCount >= 1
    res = validate(True, "1", "100", False,
                   "SEARCH", 1, "RANGE", [],
                   0, 100.0, True)
    assert res == "RepeatCount must be at least 1."
    # Check SuccessPercent limits
    res = validate(True, "1", "100", False,
                   "SEARCH", 1, "RANGE", [],
                   1, -10.0, True)
    assert res == "SuccessPercent must be between 0 and 100 inclusive."
    res = validate(True, "1", "100", False,
                   "SEARCH", 1, "RANGE", [],
                   1, 101, True)
    assert res == "SuccessPercent must be between 0 and 100 inclusive."


# Test Object Iterator running binary search and converging
# on some value (1750) but stabilizing on another (1500)
# This test really tests the iteration parameter update
def test_bin_range(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 2000.0
    repeat_count = 2
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".BenchmarkStabilityIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("IterMode", "BINARY")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Iteration 1 (Search 1)
    plLogger.LogInfo("======= Iteration 1 ========")
    cmd.Execute()
    assert cmd.Get("Iteration") == 1
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "1500"
    assert cmd.Get("SearchIteration") == 1
    assert cmd.Get("SearchMaxPass") == 1000.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False

    # Iteration 2 (Search 2)
    plLogger.LogInfo("======= Iteration 2 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 2
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "1750"
    assert cmd.Get("SearchIteration") == 2
    assert cmd.Get("SearchMaxPass") == 1500.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False

    # Iteration 3 (Search 3)
    plLogger.LogInfo("======= Iteration 3 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "2000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False

    # Iteration 4 (Stability 1 Trial 1)
    # This is a fake iteration for the ObjectIterator as it
    # errors out.  This is the first iteration for the
    # StabilityBackoffIterator
    plLogger.LogInfo("======= Iteration 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 4
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1750"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 1
    assert cmd.Get("StabilityTrialNum") == 1
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    # Iteration 5 (Stability 1 Trial 2)
    plLogger.LogInfo("======= Iteration 5 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 5
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1750"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 1
    assert cmd.Get("StabilityTrialNum") == 2
    assert cmd.Get("StabilitySuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    # Iteration 6 (Stability 2 Trial 1)
    plLogger.LogInfo("======= Iteration 6 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 6
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1500"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 2
    assert cmd.Get("StabilityTrialNum") == 1
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    # Iteration 7 (Stability 2 Trial 2)
    plLogger.LogInfo("======= Iteration 7 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 7
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1500"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 2
    assert cmd.Get("StabilityTrialNum") == 2
    assert cmd.Get("StabilitySuccessCount") == 1
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    # Iteration 8 (Done)
    # Fake iteration to break out of both the
    # StabilityBackoffIteratorCommand and the
    # BenchmarkStabilityIteratorCommand
    plLogger.LogInfo("======= Iteration 8 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 7
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1500"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 2
    assert cmd.Get("StabilityTrialNum") == 2
    assert cmd.Get("StabilitySuccessCount") == 2
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is True
    assert cmd.Get("StableValue") == "1500"
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    # Clean up
    cmd.MarkDelete()


# Test Object Iterator running binary search "failing" to
# find a passing value (in other words, converge on MinVal
# and fail there).
def test_bin_range_search_fail(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 2000.0
    repeat_count = 2
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".BenchmarkStabilityIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("IterMode", "BINARY")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Start the ObjectIteratorCommand at Iteration 2
    cmd.Set("Iteration", 2)
    cmd.Set("CurrVal", "1250")
    cmd.Set("SearchIteration", 2)
    cmd.Set("SearchMaxPass", 1000.0)
    cmd.Set("SearchMinFail", 1250.0)

    # Iteration 3 (Search 3)
    plLogger.LogInfo("======= Iteration 1 ========")
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1000.0
    assert cmd.Get("SearchMinFail") == 1250.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False

    # Iteration 4 (Stability 1 Trial 1)
    # This is a fake iteration for the ObjectIterator as it
    # errors out.  This is the first iteration for the
    # StabilityBackoffIterator.  Since no converged value
    # was found, the StabilityBackoffIterator should not run.
    plLogger.LogInfo("======= Iteration 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1000.0
    assert cmd.Get("SearchMinFail") == 1000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False


# Test Object Iterator running binary search and converging
# on some value (1750) but failing to find a stable value
# This test really tests the iteration parameter update
def test_bin_range_stability_fail(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 2000.0
    repeat_count = 2
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".BenchmarkStabilityIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("IterMode", "BINARY")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])

    # Start with Iteration 7 in the stability test
    cmd.Set("Iteration", 6)
    cmd.Set("IterState", "STABILITY")
    cmd.Set("IsConverged", True)
    cmd.Set("CurrVal", "1500")
    cmd.Set("SearchIteration", 3)
    cmd.Set("SearchMaxPass", 1750.0)
    cmd.Set("SearchMinFail", 2000.0)
    cmd.Set("StabilityIteration", 2)
    cmd.Set("StabilityTrialNum", 1)

    # Iteration 7 (Stability 3 Trial 1)
    plLogger.LogInfo("======= Iteration 7 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 7
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1250"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 3
    assert cmd.Get("StabilityTrialNum") == 1
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True

    # Iteration 8 (Stability 4 Trial 1)
    plLogger.LogInfo("======= Iteration 8 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 8
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 4
    assert cmd.Get("StabilityTrialNum") == 1
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True

    # Iteration 9 (Done)
    # Fake iteration to break out of both the
    # StabilityBackoffIteratorCommand and the
    # BenchmarkStabilityIteratorCommand
    # As this test fails, there is no stable value found
    plLogger.LogInfo("======= Iteration 9 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 8
    assert cmd.Get("IterState") == "STABILITY"
    assert cmd.Get("CurrVal") == "1000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 4
    assert cmd.Get("StabilityTrialNum") == 1
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True

    # Clean up
    cmd.MarkDelete()


# Test Benchmark Stability Iterator skipping the
# Stability Backoff portion.
def test_bin_range_no_stability_backoff(stc):
    step_val = 250.0
    min_val = 1000.0
    max_val = 2000.0
    repeat_count = 2
    success = 100.0

    pkg = "spirent.methodology"
    plLogger = PLLogger.GetLogger('methodology')
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(pkg + ".BenchmarkStabilityIteratorCommand")
    cmd.Set("MinVal", float(min_val))
    cmd.Set("MaxVal", float(max_val))
    cmd.Set("StepVal", float(step_val))
    cmd.Set("IterMode", "BINARY")
    cmd.Set("RepeatCount", repeat_count)
    cmd.Set("SuccessPercent", float(success))
    cmd.Set("ValueType", "RANGE")
    cmd.SetCollection("ValueList", [])
    cmd.Set("EnableStabilityBackoff", False)

    # Start at iteration 3
    cmd.Set("Iteration", 2)
    cmd.Set("IterState", "SEARCH")
    cmd.Set("CurrVal", "1750")
    cmd.Set("SearchIteration", 2)
    cmd.Set("SearchMaxPass", 1500.0)
    cmd.Set("SearchMinFail", 2000.0)
    cmd.Set("StabilityIteration", 0)
    cmd.Set("StabilityTrialNum", 0)
    cmd.Set("StabilitySuccessCount", 0)

    # Iteration 3 (Search 3)
    plLogger.LogInfo("======= Iteration 3 ========")
    cmd.Set("PrevIterVerdict", True)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "2000"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "PASSED"
    assert cmd.Get("ResetState") is False
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is False

    # Iteration 4
    # This is a fake iteration for the ObjectIterator as it
    # errors out.  Since there is no StabilityBackoff,
    # the iteration should end.
    plLogger.LogInfo("======= Iteration 4 ========")
    cmd.Reset()
    cmd.Set("PrevIterVerdict", False)
    cmd.Execute()
    assert cmd.Get("Iteration") == 3
    assert cmd.Get("IterState") == "SEARCH"
    assert cmd.Get("CurrVal") == "1750"
    assert cmd.Get("SearchIteration") == 3
    assert cmd.Get("SearchMaxPass") == 1750.0
    assert cmd.Get("SearchMinFail") == 2000.0
    assert cmd.Get("StabilityIteration") == 0
    assert cmd.Get("StabilityTrialNum") == 0
    assert cmd.Get("StabilitySuccessCount") == 0
    assert cmd.Get("PassFailState") == "FAILED"
    assert cmd.Get("ResetState") is True
    assert cmd.Get("FoundStableValue") is False
    assert cmd.Get("IsConverged") is True
    assert cmd.Get("ConvergedVal") == "1750"

    cmd.MarkDelete()
