import math
from StcIntPythonPL import *
import IteratorCommand as base


# This command iterates over a set of (discrete) objects
def validate(IterMode, StepVal, ValueType, ValueList,
             BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate ObjectIteratorCommand")

    # Call base class for validation
    res = base.validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict)
    if res is not "":
        return res

    if ValueType == "LIST":
        if len(ValueList) < 1:
            return "ERROR: ValueType is LIST so ValueList must contain elements"
    elif ValueType == "RANGE":
        if StepVal == 0:
            if MinVal != MaxVal:
                return "ERROR: MinVal and MaxVal must be the same if StepVal is 0."
        if MinVal > MaxVal:
            return "ERROR: MinVal must be less than (or equal to) MaxVal."
    return ''


def run(IterMode, StepVal, ValueType, ValueList,
        BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run ObjectIteratorCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)

    # Determine if the state parameters should be reset
    resetState = this_cmd.Get("ResetState")

    # Break on fail (set the previous values and exit -
    # most of the values are state and don't have to be reset)
    if BreakOnFail and PrevIterVerdict is False and resetState is False:
        # LIST
        if ValueType == "LIST":
            this_cmd.Set("CurrVal", ValueList[this_cmd.Get("CurrIndex")])
        this_cmd.Set("PassFailState", "FAILED")
        this_cmd.Set("ResetState", True)
        return False

    # The value and type of curr_val and prev_search_val depend on ValueType.  If ValueType
    # is LIST, then these two variables are an indexes and probably ints (returned as
    # an unsigned ints).  If ValueType is a RANGE, these two variables are floats/doubles.
    curr_val = None
    prev_search_val = None

    if resetState:
        plLogger.LogInfo(" resetting ObjectIteratorCommand's state")
        iteration = 0
        max_pass = 0.0
        min_fail = 0.0
        prev_val = ""
        currIndex = 0
        this_cmd.Set("IsConverged", False)
        this_cmd.Set("ConvergedVal", "")
        this_cmd.Set("ResetState", False)
    else:
        plLogger.LogInfo(" using the existing state properties")
        # Get the state properties
        max_pass = this_cmd.Get("MaxPass")
        min_fail = this_cmd.Get("MinFail")
        iteration = this_cmd.Get("Iteration")
        prev_val = this_cmd.Get("CurrVal")
        currIndex = this_cmd.Get("CurrIndex")

    plLogger.LogInfo(" current iteration: " + str(iteration))
    plLogger.LogInfo(" previous iteration res: " + str(PrevIterVerdict))
    plLogger.LogInfo(" previous val/index: " + str(prev_val))
    plLogger.LogInfo(" max_pass/min_fail/prev_val: " + str(max_pass) + "/" +
                     str(min_fail) + "/" + str(prev_val))

    # Range
    if ValueType == "RANGE":
        plLogger.LogInfo("Range type value set")
        plLogger.LogInfo(" min/step/max: " + str(MinVal) + "/" +
                         str(StepVal) + "/" + str(MaxVal))

        if iteration == 0:
            prev_search_val = float("nan")
        else:
            prev_search_val = float(prev_val)

    # List
    elif ValueType == "LIST":
        plLogger.LogInfo("List type value set")
        plLogger.LogInfo(" list: " + str(ValueList))

        # Treat this as a range with a MinVal = 0, StepVal = 1, MaxVal = len(ValueList) -1
        MinVal = 0
        StepVal = 1
        MaxVal = len(ValueList) - 1

        if iteration == 0:
            prev_search_val = -1
        else:
            prev_search_val = currIndex

    # Step
    if IterMode == "STEP":
        plLogger.LogInfo("Step iteration mode")

        # This exit covers the cases where the test has already run MaxVal
        if MaxVal == prev_search_val:
            # We are done

            this_cmd.Set("Iteration", iteration)

            # RANGE
            if ValueType == "RANGE":
                this_cmd.Set("CurrVal", prev_search_val)
            elif ValueType == "LIST":
                # LIST
                this_cmd.Set("CurrVal", ValueList[int(prev_search_val)])
                this_cmd.Set("CurrIndex", prev_search_val)
            this_cmd.Set("IsConverged", True)
            this_cmd.Set("ConvergedVal", this_cmd.Get("CurrVal"))

            # Return FAILED (break the loop)
            this_cmd.Set("PassFailState", "FAILED")
            this_cmd.Set("ResetState", True)
            return False

        # Initialize
        min_fail = 0.0
        max_pass = 0.0

        if iteration == 0:
            plLogger.LogInfo("iteration 0")
            curr_val = MinVal

        else:
            curr_val = prev_search_val + StepVal

        if curr_val > MaxVal:
            curr_val = MaxVal

    # Binary
    elif IterMode == "BINARY":
        plLogger.LogInfo("Binary iteration mode")

        # Initialize
        if iteration == 0:
            plLogger.LogInfo("iteration 0")
            min_fail = MaxVal
            max_pass = MinVal

        else:
            plLogger.LogInfo("iteration " + str(iteration))
            if PrevIterVerdict is True:
                max_pass = prev_search_val
            else:
                min_fail = prev_search_val

            # This exit covers the cases where the test converges on some value between
            # MinVal and MaxVal
            if max_pass != MinVal and min_fail != MaxVal:
                if min_fail - max_pass == StepVal:
                    # We are done here unless the min_fail is to be run again
                    this_cmd.Set("Iteration", iteration)
                    this_cmd.Set("MinFail", float(min_fail))
                    this_cmd.Set("MaxPass", float(max_pass))

                    # RANGE
                    if ValueType == "RANGE":
                        this_cmd.Set("CurrVal", prev_search_val)
                    elif ValueType == "LIST":
                        # LIST
                        this_cmd.Set("CurrVal", ValueList[int(prev_search_val)])
                        this_cmd.Set("CurrIndex", prev_search_val)
                    this_cmd.Set("IsConverged", True)
                    this_cmd.Set("ConvergedVal", this_cmd.Get("CurrVal"))

                    # Return FAILED (break the loop)
                    this_cmd.Set("PassFailState", "FAILED")
                    this_cmd.Set("ResetState", True)
                    return False

        plLogger.LogInfo(" min_fail/max_pass: " + str(min_fail) + "/" + str(max_pass))
        plLogger.LogInfo(" prev_search_val: " + str(prev_search_val))
        plLogger.LogInfo(" MaxVal: " + str(type(MaxVal)))

        # This exit covers the cases where the test converges on either MinVal or MaxVal
        if MaxVal == prev_search_val or MinVal == prev_search_val:
            # We are done
            this_cmd.Set("Iteration", iteration)
            this_cmd.Set("MinFail", float(min_fail))
            this_cmd.Set("MaxPass", float(max_pass))

            # RANGE
            if ValueType == "RANGE":
                this_cmd.Set("CurrVal", prev_search_val)
            elif ValueType == "LIST":
                this_cmd.Set("CurrVal", ValueList[int(prev_search_val)])
                this_cmd.Set("CurrIndex", prev_search_val)
            if PrevIterVerdict:
                # When we hit this case, it means we converged on the MaxVal
                this_cmd.Set("IsConverged", True)
                this_cmd.Set("ConvergedVal", this_cmd.Get("CurrVal"))
            elif max_pass != MinVal:
                # When we hit this case, it means that we converged on one value less
                # than MaxVal
                this_cmd.Set("IsConverged", True)
                this_cmd.Set("ConvergedVal", max_pass)

            # Return FAILED (break the loop)
            this_cmd.Set("PassFailState", "FAILED")
            this_cmd.Set("ResetState", True)
            return False

        # Find the new mathematical halfway point
        raw_curr_val = (min_fail + max_pass) / 2.0

        # Subtract out the MinVal (test range start) to "normalize" to 0
        norm_raw_curr_val = raw_curr_val - MinVal

        # Find the number of steps to take (given the step size) by taking the
        # ceiling of the normalized value divided by the step size
        if StepVal == 0:
            plLogger.LogInfo("StepVal is 0...infinite loop? "
                             "The only way this is valid is if MinVal == MaxVal")
            step_count = 0.0
        else:
            step_count = math.ceil(norm_raw_curr_val / StepVal)

        # curr_val is now given by the MinVal + StepVal * step_count
        curr_val = MinVal + (StepVal * step_count)

        # curr_val can't be greater than MaxVal...if it is, we go straight to MaxVal and will
        # finish the test in the next iteration
        if curr_val > MaxVal:
            curr_val = MaxVal

        # if curr_val == prev_search_val then we are also almost finished here....
        # This means that min_fail and max_pass are one StepVal apart.
        if curr_val == prev_search_val:
            if PrevIterVerdict is False:
                curr_val = max_pass
            else:
                curr_val = min_fail

    # Update the iteration (only should be updated when "PASSED" is returned)
    iteration = iteration + 1
    plLogger.LogInfo(" curr_val being set to: " + str(curr_val))

    # Set the output parameters including state properties
    this_cmd.Set("Iteration", iteration)
    this_cmd.Set("MinFail", float(min_fail))
    this_cmd.Set("MaxPass", float(max_pass))

    if ValueType == "RANGE":
        this_cmd.Set("CurrVal", curr_val)
    elif ValueType == "LIST":
        this_cmd.Set("CurrVal", ValueList[int(curr_val)])
        this_cmd.Set("CurrIndex", int(curr_val))

    # Return PASSED (keep looping)
    this_cmd.Set("PassFailState", "PASSED")
    this_cmd.Set("ResetState", False)
    return True


def reset():

    return True
