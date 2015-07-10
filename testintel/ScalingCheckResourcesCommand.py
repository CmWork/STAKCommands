"""Calculates resource requirements given feature reqs for a single port"""
from StcIntPythonPL import (CHandleRegistry, PLLogger)
import feature
import traceback


def validate(FeatureNameList, FeatureValueList):
    """Validate the command: make sure lists lengths match and names are all
    valid."""
    result = validate_lengths(FeatureNameList, FeatureValueList)
    if result:
        return result

    result = validate_features(FeatureNameList)
    if result:
        return result

    return ""


def validate_lengths(names, values):
    """Empty string if lengths are equal, else error message."""
    if len(names) != len(values):
        return ("ERROR: FeatureNameList and FeatureValueList must have the " +
                "same length")

    return ""


def validate_features(feature_names):
    """Empty string if all features are valid, else error message."""
    for feature_name in feature_names:
        result = validate_feature(feature_name)
        if result:
            return result

    return ""


def validate_feature(feature_name):
    """Empty string if all feature is valid, else error message."""
    if feature_name not in feature.features():
        return ("ERROR: feature %s is unknown. Should be one of %s" %
                (feature_name, ", ".join(feature.features())))

    return ""


def run(FeatureNameList, FeatureValueList):
    """Run method - calculate outputs"""
    try:
        hnd_reg = CHandleRegistry.Instance()
        this_hnd = hnd_reg.Find(__commandHandle__)  # pragma: no flakes
        this_hnd.Set("MinMemoryMb", 512)
        this_hnd.Set("MinCores", 1)
        this_hnd.Set("MinSpiMips", 500)
    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return False

    return True


def reset():
    """True means this command can be reset and re-run"""
    return True


def get_logger():
    """Get the test intel logger"""
    return PLLogger.GetLogger("testintel")
