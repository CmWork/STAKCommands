from StcIntPythonPL import *
import math

# This command iterates in reverse order from maximum value to minimum value,
# repeating each value RepeatCount times.


# Determine if the current value is stable (to report passing)
def is_value_stable(trial_num, success_count,
                    repeat_count, success_percent):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    # repeat_count = total number of trials
    # trial_num = number of trials run so far
    # repeat_count - trial_num = number of trials remaining
    # success_count = number of successes so far
    # success_percent = acceptable passing percent (for stable value)

    if trial_num < success_count:
        # Not enough minimum trials run yet
        plLogger.LogDebug(" not enough trials conducted yet to even consider done")
        return False

    # Find the minimum number of successful trials that need to have
    # been done in order to be considered stable
    min_pass_trials = int(math.ceil(repeat_count * success_percent * 0.01))
    plLogger.LogDebug("min_pass_trials: " + str(min_pass_trials))
    plLogger.LogDebug("success_count: " + str(success_count))

    if success_count < min_pass_trials:
        # Not enough passing trials have been conducted yet
        plLogger.LogDebug(" not enough passing trials yet")
        return False

    percent_success = 100 * (float(success_count) / float(repeat_count))
    plLogger.LogDebug("percent_success: " + str(percent_success))
    if percent_success >= success_percent:
        plLogger.LogDebug(" percent_success is >= success_percent  <- We are done!")
        # Current value is stable
        return True
    return False


# Determine if the current iteration is done (too many
# trials have failed to bother continuing this particular
# iteration)
def end_iteration_early(trial_num, success_count,
                        repeat_count, success_percent):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")
    # Determine if there are enough trials left such that if they all passed,
    # the iteration could potentially pass.

    # repeat_count = total number of trials
    # trial_num = number of trials run so far
    # repeat_count - trial_num = number of trials remaining
    # success_count = number of successes so far
    # success_percent = acceptable passing percent (for stable value)

    trials_left = int(repeat_count - trial_num)
    min_pass_trials = int(math.ceil(repeat_count * success_percent * 0.01))
    plLogger.LogDebug("trials_left: " + str(trials_left))
    plLogger.LogDebug("min_pass_trials: " + str(min_pass_trials))
    plLogger.LogDebug("success_count: " + str(success_count))

    num_pass_still_needed = min_pass_trials - int(success_count)

    plLogger.LogDebug("num_pass_still_needed: " + str(num_pass_still_needed))

    if trials_left >= num_pass_still_needed:
        plLogger.LogDebug("trials_left >= num_pass_still_needed")
        return False
    plLogger.LogDebug("trials_left < num_pass_still_needed")
    return True


def validate(StepVal, RepeatCount, SuccessPercent, ValueType,
             ValueList, BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
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


def run(StepVal, RepeatCount, SuccessPercent, ValueType,
        ValueList, BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run")

    hnd_reg = CHandleRegistry.Instance()
    if hnd_reg is None:
        plLogger.LogError("ERROR: Could not get an instance of the " +
                          "HandleRegistry")
        return False

    this_cmd = hnd_reg.Find(__commandHandle__)
    if this_cmd is None:
        plLogger.LogError("ERROR: Could not find this command " +
                          "(StabilityBackoffIteratorCommand) in the " +
                          "HandleRegistry")
        return False

    # Break on fail (set the previous values and exit -
    # most of the values are state and don't have to be reset)
    if BreakOnFail and PrevIterVerdict is False:
        if ValueType == "LIST":
            this_cmd.Set("CurrVal", ValueList[this_cmd.Get("CurrIndex")])
        this_cmd.Set("PassFailState", "FAILED")
        return False

    # The value and type of next_val and prev_search_val depend on ValueType.  If ValueType
    # is LIST, then these two variables are an indexes and probably ints (returned as
    # an unsigned ints).  If ValueType is a RANGE, these two variables are floats/doubles.
    next_val = None
    prev_search_val = None

    # Determine if the state parameters should be reset
    if this_cmd.Get("ResetState"):
        plLogger.LogDebug(" resetting StabilityStepIteratorCommand's state")
        iteration = 0
        prev_val = ""
        success_count = 0
        trial_num = 0
        if ValueType == "LIST":
            curr_index = len(ValueList)
    else:
        plLogger.LogDebug(" using the existing state properties")
        # Get the state properties
        iteration = this_cmd.Get("Iteration")
        prev_val = this_cmd.Get("CurrVal")
        curr_index = this_cmd.Get("CurrIndex")
        success_count = this_cmd.Get("SuccessCount")
        trial_num = this_cmd.Get("TrialNum")

    # Initialize iteration data
    # Treat Lists like Ranges by setting MinVal and MaxVal appropriately
    if ValueType == "LIST":
        # Treat this as a range with a MinVal = 0, StepVal = 1, MaxVal = len(ValueList) -1
        MinVal = 0
        StepVal = 1
        MaxVal = len(ValueList) - 1

    # Range
    if ValueType == "RANGE":
        plLogger.LogDebug("Range type value set")
        plLogger.LogDebug(" min/step/max: " + str(MinVal) + "/" +
                          str(StepVal) + "/" + str(MaxVal))
        if iteration == 0:
            prev_search_val = float(MaxVal)
        else:
            prev_search_val = float(prev_val)

    # List
    elif ValueType == "LIST":
        plLogger.LogDebug("List type value set")
        plLogger.LogDebug(" list: " + str(ValueList))
        if iteration == 0:
            prev_search_val = MaxVal
        else:
            prev_search_val = curr_index

    plLogger.LogDebug(" current iteration: " + str(iteration))
    plLogger.LogDebug(" current trial: " + str(trial_num))
    plLogger.LogDebug(" previous iteration res: " + str(PrevIterVerdict))
    plLogger.LogDebug(" previous val/index: " + str(prev_val))
    plLogger.LogDebug(" success_count: " + str(success_count))
    plLogger.LogDebug(" trial_num: " + str(trial_num))
    plLogger.LogDebug(" prev_search_val: " + str(prev_search_val))

    # Determine what to do first based on the PrevIterVerdict
    if (iteration > 0) and (PrevIterVerdict is True):
        # Previous iteration passed
        plLogger.LogDebug("prev trial passed")
        success_count = success_count + 1

        if is_value_stable(trial_num, success_count,
                           RepeatCount, SuccessPercent):
            # We are done
            plLogger.LogDebug(" value is stable <- We are done!")

            if ValueType == "LIST":
                this_cmd.Set("StableValue",
                             str(ValueList[prev_search_val]))
                this_cmd.Set("CurrVal",
                             str(ValueList[prev_search_val]))
                this_cmd.Set("CurrIndex", prev_search_val)
            else:
                this_cmd.Set("StableValue", prev_search_val)
                this_cmd.Set("CurrVal", prev_search_val)

            # Return FAILED (break the loop)
            this_cmd.Set("Iteration", iteration)
            this_cmd.Set("SuccessCount", success_count)
            this_cmd.Set("TrialNum", trial_num)
            this_cmd.Set("FoundStableValue", True)
            this_cmd.Set("PassFailState", "FAILED")
            this_cmd.Set("ResetState", True)
            return False

    # Now determine if the previous trial was the last one of that set
    # This will determine if we have to change the current value
    if trial_num == RepeatCount:
        plLogger.LogDebug("trial_num == RepeatCount")

        # First, determine if we are done.
        # Since trial_num == RepeatCount,
        # if prev_search_val also equals MinVal,
        # we can't backoff anymore.  No more values
        # or trials left to run.
        if prev_search_val == MinVal:
            # We are done
            plLogger.LogDebug(" prev_search_val == MinVal <- We are done!")

            # If we get to this point, we've failed to find
            # a stable value
            plLogger.LogDebug(" failed to find a stable value")

            if ValueType == "LIST":
                this_cmd.Set("CurrVal",
                             str(ValueList[prev_search_val]))
                this_cmd.Set("CurrIndex", prev_search_val)
            else:
                this_cmd.Set("CurrVal", prev_search_val)

            # Return FAILED (break the loop)
            this_cmd.Set("SuccessCount", success_count)
            this_cmd.Set("Iteration", iteration)
            this_cmd.Set("TrialNum", trial_num)
            this_cmd.Set("FoundStableValue", False)
            this_cmd.Set("PassFailState", "FAILED")
            this_cmd.Set("ResetState", True)
            return False

        # Update the counts and find the next value
        # by stepping backwards
        trial_num = 1
        iteration = iteration + 1
        success_count = 0
        next_val = prev_search_val - StepVal
        if next_val < MinVal:
            next_val = MinVal
    else:
        plLogger.LogDebug("trial_num != RepeatCount")
        if end_iteration_early(trial_num, success_count,
                               RepeatCount, SuccessPercent):
            plLogger.LogDebug("end_iteration_early")

            if prev_search_val == MinVal:
                plLogger.LogDebug("Already at MinVal with not enough trials " +
                                  "left for a stable value to be found.")
                plLogger.LogDebug(" -> end the test")

                # End the loop - this test entirely failed
                if ValueType == "LIST":
                    this_cmd.Set("StableValue",
                                 str(ValueList[prev_search_val]))
                    this_cmd.Set("CurrVal",
                                 str(ValueList[prev_search_val]))
                    this_cmd.Set("CurrIndex", prev_search_val)
                else:
                    this_cmd.Set("StableValue", prev_search_val)
                    this_cmd.Set("CurrVal", prev_search_val)

                this_cmd.Set("SuccessCount", success_count)
                this_cmd.Set("Iteration", iteration)
                this_cmd.Set("TrialNum", trial_num)
                this_cmd.Set("FoundStableValue", False)
                this_cmd.Set("PassFailState", "FAILED")
                this_cmd.Set("ResetState", True)
                return False
            else:
                # Update the counts and find the next value
                # by stepping backwards
                trial_num = 1
                iteration = iteration + 1
                success_count = 0
                next_val = prev_search_val - StepVal
                if next_val < MinVal:
                    next_val = MinVal
        else:
            plLogger.LogDebug(" increase the trial_num")
            # Increase the trial_num
            trial_num = trial_num + 1

            # next_val does not change
            next_val = prev_search_val

    # This should only ever be executed once
    if iteration == 0:
        iteration = iteration + 1

    # Update the iteration (only should be updated when "PASSED" is returned)
    plLogger.LogDebug(" next_val (CurrVal) being set to: " + str(next_val))

    # Set the output parameters including state properties
    if ValueType == "RANGE":
        this_cmd.Set("CurrVal", next_val)
    else:
        this_cmd.Set("CurrVal", str(ValueList[next_val]))
        this_cmd.Set("CurrIndex", next_val)
    this_cmd.Set("Iteration", iteration)

    this_cmd.Set("SuccessCount", success_count)
    this_cmd.Set("TrialNum", trial_num)

    # Return PASSED (keep looping)
    this_cmd.Set("PassFailState", "PASSED")
    this_cmd.Set("ResetState", False)
    return True


def reset():

    return True
