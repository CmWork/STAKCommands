from StcIntPythonPL import *


def validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict,
             IterMode, StepVal, ValueType, ValueList,
             RepeatCount, SuccessPercent, EnableStabilityBackoff):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("validate")

    if ValueType == "LIST":
        if len(ValueList) < 1:
            return "ValueType is LIST so ValueList must contain elements."
    elif ValueType == "RANGE":
        if StepVal == 0.0:
            if MinVal != MaxVal:
                return "MinVal and MaxVal must be the same if StepVal is 0."
        if MinVal > MaxVal:
            return "MinVal must be less than (or equal to) MaxVal."
    if RepeatCount < 1:
        return "RepeatCount must be at least 1."
    if SuccessPercent < 0 or SuccessPercent > 100:
        return "SuccessPercent must be between 0 and 100 inclusive."
    return ""


def run(BreakOnFail, MinVal, MaxVal, PrevIterVerdict,
        IterMode, StepVal, ValueType, ValueList,
        RepeatCount, SuccessPercent, EnableStabilityBackoff):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    hnd_reg = CHandleRegistry.Instance()
    if hnd_reg is None:
        plLogger.LogError("ERROR: Could not get an instance of the " +
                          "HandleRegistry")
        return False
    ctor = CScriptableCreator()

    # Get this command
    this_cmd = hnd_reg.Find(__commandHandle__)
    if this_cmd is None:
        plLogger.LogError("ERROR: Could not find this command " +
                          "(BenchmarkStabilityIteratorCommand) in the " +
                          "HandleRegistry")
        return False

    if this_cmd.Get("ResetState"):
        plLogger.LogDebug(" reset BenchmarkStabilityIteratorCommand's state")
        iteration = 0
        iter_state = "SEARCH"
        curr_val = ""
        curr_index = 0
        search_iteration = 0
        search_min_fail = 0.0
        search_max_pass = 0.0
        stability_iteration = 0
        stability_trial_num = 0
        stability_success_count = 0
        is_converged = False
        converged_val = ""
    else:
        plLogger.LogDebug(" use the existing state values")
        # Get the state properties
        iteration = this_cmd.Get("Iteration")
        iter_state = this_cmd.Get("IterState")
        curr_val = this_cmd.Get("CurrVal")
        curr_index = this_cmd.Get("CurrIndex")
        search_iteration = this_cmd.Get("SearchIteration")
        search_min_fail = this_cmd.Get("SearchMinFail")
        search_max_pass = this_cmd.Get("SearchMaxPass")
        stability_iteration = this_cmd.Get("StabilityIteration")
        stability_trial_num = this_cmd.Get("StabilityTrialNum")
        stability_success_count = this_cmd.Get("StabilitySuccessCount")
        is_converged = this_cmd.Get("IsConverged")
        converged_val = this_cmd.Get("ConvergedVal")

    # Call the correct iterator depending on the current status
    pkg = "spirent.methodology"
    is_done = False
    is_stable = False
    stable_value = None
    if iter_state == "SEARCH":
        # Call the ObjectIteratorCommand

        # State properties need to be explicitly configured since the
        # iterator command is created each time this command
        # (the BenchmarkStabilityIteratorCommand) is looped.
        it_cmd = ctor.CreateCommand(pkg + ".ObjectIteratorCommand")
        if it_cmd is None:
            plLogger.LogError("ERROR: Could not create an " +
                              "ObjectIteratorCommand")
            return False

        it_cmd.Set("Iteration", search_iteration)
        it_cmd.Set("IterMode", IterMode)
        it_cmd.Set("ValueType", ValueType)
        it_cmd.SetCollection("ValueList", ValueList)
        it_cmd.Set("MinVal", MinVal)
        it_cmd.Set("MaxVal", MaxVal)
        it_cmd.Set("StepVal", StepVal)
        it_cmd.Set("BreakOnFail", BreakOnFail)
        it_cmd.Set("Iteration", iteration)
        it_cmd.Set("PrevIterVerdict", PrevIterVerdict)
        it_cmd.Set("CurrVal", curr_val)
        it_cmd.Set("CurrIndex", curr_index)
        it_cmd.Set("MinFail", search_min_fail)
        it_cmd.Set("MaxPass", search_max_pass)

        it_cmd.Execute()

        # Done looping
        if it_cmd.Get("PassFailState") == "FAILED":
            # Need to determine if the ObjectIteratorCommand
            # converged to a useful value or not.
            if it_cmd.Get("IsConverged"):
                curr_val = it_cmd.Get("ConvergedVal")
                is_converged = True
                converged_val = curr_val
                iter_state = "STABILITY"
            else:
                # Skip the Stability Test and exit
                is_done = True
        else:
            # Extract the state parameters
            curr_val = it_cmd.Get("CurrVal")

        curr_index = it_cmd.Get("CurrIndex")
        search_iteration = it_cmd.Get("Iteration")
        search_min_fail = it_cmd.Get("MinFail")
        search_max_pass = it_cmd.Get("MaxPass")

        # Clean up
        it_cmd.MarkDelete()

    # Note that when we switch from search to stability iteration mode,
    # both the preceeding if (for "SEARCH") and the following one
    # (for "STABILITY") are run.  The "last" iteration of the
    # ObjectIteratorCommand is not a "real" iteration in that it is normally
    # run to break out of the while loop.  For this command though, the
    # StabilityBackoffIteratorCommand must start on this "fake" last
    # iteration of the ObjectIteratorCommand.
    if iter_state == "STABILITY":
        if not EnableStabilityBackoff:
            # Set the command's iteration state back to SEARCH
            # as stability was never done.
            iter_state = "SEARCH"
            is_done = True
        else:
            # Call the StabilityBackoffIteratorCommand

            # State properties need to be explicitly configured since the
            # iterator command is created each time this command
            # (the BenchmarkStabilityIteratorCommand) is looped.
            bk_cmd = ctor.CreateCommand(pkg +
                                        ".StabilityBackoffIteratorCommand")

            if bk_cmd is None:
                plLogger.LogError("ERROR: Could not create a " +
                                  "StabilityBackoffIteratorCommand")
                return False

            bk_cmd.Set("ValueType", ValueType)
            bk_cmd.SetCollection("ValueList", ValueList)
            bk_cmd.Set("MinVal", MinVal)
            bk_cmd.Set("MaxVal", curr_val)
            bk_cmd.Set("StepVal", StepVal)
            bk_cmd.Set("BreakOnFail", BreakOnFail)
            bk_cmd.Set("Iteration", stability_iteration)
            bk_cmd.Set("PrevIterVerdict", PrevIterVerdict)
            bk_cmd.Set("CurrVal", curr_val)
            bk_cmd.Set("CurrIndex", curr_index)
            bk_cmd.Set("TrialNum", stability_trial_num)
            bk_cmd.Set("SuccessCount", stability_success_count)
            bk_cmd.Set("SuccessPercent", SuccessPercent)
            bk_cmd.Set("RepeatCount", RepeatCount)
            bk_cmd.Execute()

            # Done looping
            if bk_cmd.Get("PassFailState") == "FAILED":
                plLogger.LogDebug("Stability is done!")
                is_done = True
                is_stable = bk_cmd.Get("FoundStableValue")
                stable_value = bk_cmd.Get("StableValue")

            # Extract the state parameters
            curr_val = bk_cmd.Get("CurrVal")
            curr_index = bk_cmd.Get("CurrIndex")
            stability_iteration = bk_cmd.Get("Iteration")
            stability_trial_num = bk_cmd.Get("TrialNum")
            stability_success_count = bk_cmd.Get("SuccessCount")

            # Clean up
            bk_cmd.MarkDelete()

    # Update the BenchmarkStabilityIteratorCommand's iteration count.
    # This count includes trials done by the
    # StabilityBackoffIteratorCommand
    if not is_done:
        iteration = iteration + 1

    # Set up state and output parameters
    this_cmd.Set("Iteration", iteration)
    this_cmd.Set("CurrVal", curr_val)
    this_cmd.Set("CurrIndex", curr_index)
    this_cmd.Set("IterState", iter_state)
    this_cmd.Set("SearchIteration", search_iteration)
    this_cmd.Set("SearchMinFail", search_min_fail)
    this_cmd.Set("SearchMaxPass", search_max_pass)
    this_cmd.Set("StabilityIteration", stability_iteration)
    this_cmd.Set("StabilityTrialNum", stability_trial_num)
    this_cmd.Set("StabilitySuccessCount", stability_success_count)
    this_cmd.Set("IsConverged", is_converged)
    this_cmd.Set("ConvergedVal", converged_val)

    # Keep on looping if not done
    if is_done:
        plLogger.LogDebug("Benchmark stability is done!")
        this_cmd.Set("PassFailState", "FAILED")
        this_cmd.Set("FoundStableValue", is_stable)
        if is_stable:
            this_cmd.Set("StableValue", stable_value)
        this_cmd.Set("ResetState", True)
        return False
    else:
        this_cmd.Set("PassFailState", "PASSED")
        this_cmd.Set("ResetState", False)
    return True


def reset():
    return True
