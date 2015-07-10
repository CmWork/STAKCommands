import math

from StcIntPythonPL import *
import IteratorCommand as base


def calc_abs_resolution(min_val, max_val, res, res_mode):
    """
    Calculate and return the absolute resolution
    """
    if res_mode == "PERCENT":
        #        plLogger.LogInfo(" search space is " + str(min_fail - max_pass))
        #        plLogger.LogInfo(" full range is " + str(max_val - min_val))
        #        plLogger.LogInfo(" percent is " + str((min_fail - max_pass) /
        #        (max_val - min_val) * 100.0))
        return (res / 100.0) * (max_val - min_val)
    elif res_mode == "ABSOLUTE":
        return res


# Determine if min_fail and max_pass are within resolution range
def is_resolution(min_fail, max_pass, abs_res):
    #    plLogger = PLLogger.GetLogger('methodology')
    #    plLogger.LogInfo("is_resolution: ")
    #        plLogger.LogInfo(" search space is " + str(min_fail - max_pass))
    return min_fail - max_pass < abs_res


def round_to_resolution(val, resolution):
    """
    Round to the nearest resolution.
    e.g. if resolution is 1, round to the nearest integer
    Only works if resolution is has 1 or 2 nonzero digits and those digits
    are a 1, 2, 25, or 5. So, 1, 50, 2, .1, .05 work, but .3, 4, 11 do not.
    """
    sig_digits = str(resolution).strip('0.')
    if sig_digits == '1':
        round_to = -int(round(math.log(resolution, 10)))
        return round(val, round_to)
    elif sig_digits == '2':
        round_to = -int(round(math.log(resolution/2, 10)))
        return round(val/2, round_to) * 2
    elif sig_digits == '5':
        round_to = -int(round(math.log(resolution*2, 10)))
        return round(val*2, round_to) / 2
    elif sig_digits in ['25', '2.5']:
        round_to = -int(round(math.log(resolution*4, 10)))
        return round(val*4, round_to) / 4
    else:
        return val


def validate_rounding(MinVal, MaxVal, res, res_mode, round_res):
    """Validate that the rounding resolution is calc-able and makes sense."""
    if not round_res:
        return ""

    abs_res = calc_abs_resolution(float(MinVal), float(MaxVal), res, res_mode)

    if round_res * 2 > abs_res:
        # if it's too close to res we can't ever reach res
        return ("RoundingResolution (%g) is invalid: should be 0 or <= 1/2 "
                "of Resolution (%g)" % (round_res, abs_res))

    sig_digits = str(round_res).strip('0.')
    if sig_digits not in ['1', '2', '5', '25', '2.5']:
        return ("RoundingResolution (%g) is unsupported: should be one of "
                "1, 2, 5, or 25 times 10 to a power." % (round_res,))

    return ""


# This command does RFC 2544-style (throughput) binary search
def validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict,
             Resolution, ResolutionMode, RoundingResolution):

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate RateIteratorCommand")

    if MinVal > MaxVal:
        return "ERROR: MinVal must be less than or equal to MaxVal."

    # Call base class for validation
    res = base.validate(BreakOnFail, MinVal, MaxVal, PrevIterVerdict)
    if res is not "":
        return res

    # Check Rounding Resolution
    res = validate_rounding(MinVal, MaxVal, Resolution,
                            ResolutionMode, RoundingResolution)
    if res is not "":
        return res

    return ""


def run(BreakOnFail, MinVal, MaxVal, PrevIterVerdict,
        Resolution, ResolutionMode, RoundingResolution):

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run RateIteratorCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)

    # Break on fail (set the previous values and exit - most of the values
    # are state and don't have to be reset)
    if BreakOnFail and PrevIterVerdict is False:
        this_cmd.Set("ResetState", True)
        this_cmd.Set("PassFailState", "FAILED")
        return False

    # Determine if the state parameters should be reset
    resetState = this_cmd.Get("ResetState")

    if resetState:
        plLogger.LogInfo(" resetting RateIteratorCommand's state")
        iteration = 0
        max_pass = 0.0
        min_fail = 0.0
        prev_val = ""
        this_cmd.Set("IsConverged", False)
        this_cmd.Set("ConvergedVal", "")
        this_cmd.Set("ResetState", False)
    else:
        plLogger.LogInfo(" using the existing state properties")
        # Get the state properties
        max_pass = float(this_cmd.Get("MaxPass"))
        min_fail = float(this_cmd.Get("MinFail"))
        iteration = this_cmd.Get("Iteration")
        prev_val = this_cmd.Get("CurrVal")

    min_val = float(MinVal)
    max_val = float(MaxVal)

    #    plLogger.LogInfo(" current iteration: " + str(iteration))
    #    plLogger.LogInfo(" previous iteration res: " + str(PrevIterVerdict))
    #    plLogger.LogInfo(" previous val/index: " + str(prev_val))
    #    plLogger.LogInfo(" max_pass/min_fail: " + str(max_pass) + "/" + str(min_fail))
    #    plLogger.LogInfo(" Resolution: " + str(Resolution))

    # Initialize the search space as necessary
    if iteration == 0:
        plLogger.LogInfo("iteration 0")
        min_fail = max_val
        max_pass = min_val
        prev_val = float("nan")
    else:
        plLogger.LogInfo("iteration " + str(iteration))
        prev_val = float(prev_val)
        if PrevIterVerdict is True:
            max_pass = prev_val
        else:
            min_fail = prev_val

    #    plLogger.LogInfo(" after initialize search space...")
    #    plLogger.LogInfo(" prev_val: " + str(prev_val))
    #    plLogger.LogInfo(" MinVal/MaxVal: " + str(MinVal) + "/" + str(MaxVal))
    #    plLogger.LogInfo(" max_pass/min_fail: " + str(max_pass) + "/" + str(min_fail))

    # This exit covers the cases where the test has converged on either min_val or max_val
    if max_val == prev_val or min_val == prev_val:
        # We are done
        this_cmd.Set("Iteration", iteration)
        this_cmd.Set("MinFail", float(min_fail))
        this_cmd.Set("MaxPass", float(max_pass))
        this_cmd.Set("CurrVal", str(prev_val))
        this_cmd.Set("ResetState", True)
        if PrevIterVerdict:
            this_cmd.Set("IsConverged", True)
            this_cmd.Set("ConvergedVal", this_cmd.Get("CurrVal"))
        elif max_val == prev_val and iteration > 1:
            # if we converged on the max_val and it failed,
            # return the last passing iteration value (if there is one)
            this_cmd.Set("IsConverged", True)
            this_cmd.Set("ConvergedVal", str(this_cmd.Get("MaxPass")))
        else:
            this_cmd.Set("IsConverged", False)

        # Return FAILED (break the loop)
        this_cmd.Set("PassFailState", "FAILED")
        return False

    # Determine if is_resolution
    abs_res = calc_abs_resolution(min_val, max_val, Resolution, ResolutionMode)
    is_res = is_resolution(min_fail, max_pass, abs_res)

    #    plLogger.LogInfo(" iteration: " + str(iteration))
    #    plLogger.LogInfo(" current is_resolution (results of previous iter): " + str(is_res))

    # Even if we're in resolution, if its the first iteration and min != max,
    # than do at least one binary search instead of going straight to max or min.
    # This handles the case when resolution > start range
    if is_res and not (iteration == 0 and min_fail != max_pass):
        plLogger.LogInfo(" we are in resolution!")
        # Special case where all iterations passed or failed (converge on min_val or max_val).
        # When is_resolution == True, jump to min or max depending on if all previous iterations
        # passed or failed (one more iteration must be run).
        if min_fail == max_val:
            # All iterations have passed thus far
            plLogger.LogInfo(" converging on the max_val...jump directly there")
            curr_val = max_val

        elif max_pass == min_val:
            # All iterations have failed thus far
            plLogger.LogInfo(" converging on the min_val...jump directly there")
            curr_val = min_val
        else:
            # This exit covers the cases where the test converges on some value between
            # MinVal and MaxVal
            plLogger.LogInfo(" converging on some value between min and max...")
            this_cmd.Set("Iteration", iteration)
            this_cmd.Set("MinFail", float(min_fail))
            this_cmd.Set("MaxPass", float(max_pass))
            this_cmd.Set("CurrVal", str(max_pass))
            this_cmd.Set("IsConverged", True)
            this_cmd.Set("ConvergedVal", this_cmd.Get("CurrVal"))
            this_cmd.Set("ResetState", True)

            # Return FAILED (break the loop)
            this_cmd.Set("PassFailState", "FAILED")
            return False
    else:
        # Find the new mathematical halfway point
        curr_val = (min_fail + max_pass) / 2.0
        if RoundingResolution:
            curr_val = round_to_resolution(curr_val, RoundingResolution)

    # Update the iteration (only should be updated when "PASSED" is returned)
    iteration = iteration + 1
    plLogger.LogInfo(" curr_val being set to: " + str(curr_val) +
                     " with type " + str(type(curr_val)))

    # Set the output parameters including state properties
    this_cmd.Set("Iteration", iteration)
    this_cmd.Set("MinFail", float(min_fail))
    this_cmd.Set("MaxPass", float(max_pass))
    this_cmd.Set("CurrVal", str(curr_val))

    n_curr_val = this_cmd.Get("CurrVal")
    plLogger.LogInfo(" read currVal out again and got: " + str(n_curr_val))

    # Return PASSED (keep looping)
    this_cmd.Set("PassFailState", "PASSED")
    return True


def reset():

    return True
