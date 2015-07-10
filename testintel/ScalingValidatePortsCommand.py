"""Calculates resource requirements given feature reqs across ports"""
from StcIntPythonPL import (CHandleRegistry, PLLogger)
from ScalingCheckResourcesCommand import validate_features
import json
import jsonschema
import port_info
import preflight
import traceback
import traffic_check


_NON_FEATURES = set(['profileId', 'portCount', 'portLocations'])


def validate_schema(obj, schema):
    """Make sure the object matches the schema"""
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError, err:
        return str(err)
    return ""


def validate_json(obj_str, obj_name):
    """Validate json is valid. Returns (result, "") or (None, error_str)"""
    obj = None
    try:
        obj = json.loads(obj_str)
    except:
        return (None, "ERROR: %s is not a valid JSON string" % (obj_name,))
    return (obj, "")


def validate(Profile, ProfileSchema, VerdictSchema):
    """Validate the command"""
    profile, error = validate_json(Profile, "Profile")
    if profile is None:
        return error

    prof_schema, error = validate_json(ProfileSchema, "ProfileSchema")
    if prof_schema is None:
        return error

    result = validate_schema(profile, prof_schema)
    if result:
        return result

    features = extract_all_features(profile['portProfiles'])
    result = validate_features(features)
    if result:
        return result

    return ""


def run(Profile, ProfileSchema, VerdictSchema):
    """Run method - calculate resources for all ports and validate"""
    try:
        hnd_reg = CHandleRegistry.Instance()
        this_hnd = hnd_reg.Find(__commandHandle__)  # pragma: no flakes
        prof = json.loads(Profile)
        verdict_schema = json.loads(VerdictSchema)
        verdict = process(prof["portProfiles"])
        schema_invalid = validate_schema(verdict, verdict_schema)
        if schema_invalid:
            get_logger().LogError("ERROR: " + schema_invalid)
            return False
        this_hnd.Set("Verdict", json.dumps(verdict))
        # TODO: validate that IL version matches BLL version
        #       validate that RCM limits are followed for ports given
        #       validate that scaling limits are followed for ports given
        #       return possible ports when ports are not given
        return is_passed(verdict)
    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return False


def reset():
    """True means this command can be reset and re-run."""
    return True


def get_logger():
    """Get the test intel logger."""
    return PLLogger.GetLogger("testintel")


def extract_all_features(profile_list):
    """Return all the features in all the profiles as a set."""
    features = set()
    for profile in profile_list:
        features.update(profile.keys())

    # convert JSON unicode to str
    features = set((str(f) for f in features))

    # remove known non-feature keys
    features.difference_update(_NON_FEATURES)
    return features


def calc_confidence(profile, port_map, location):
    confidence = traffic_check.Confidence()
    confidence = traffic_check.check_profile(profile, port_map, location,
                                             confidence)
    return confidence


def process_locations(profile_list, port_map=None):
    """Process profiles with port locations and return list of verdicts."""
    result = []
    if not port_map:
        port_map = port_info.PhysicalPortMap()

    # pre-check
    location_list = []
    for profile in profile_list:
        if "portLocations" in profile:
            if traffic_check.has_traffic(profile):
                location_list += [str(loc) for loc in profile["portLocations"]]
    preflight.check(port_map,
                    traffic_check.get_soft_locations(port_map, location_list))

    # actual check
    for profile in profile_list:
        if "portLocations" in profile:
            prof_result = {"profileId": profile["profileId"],
                           "portLocations": []}
            location_list = [str(loc) for loc in profile["portLocations"]]
            for location in location_list:
                confidence = calc_confidence(profile, port_map, location)
                prof_result["portLocations"].append({
                    "location": location,
                    "confidence": confidence.percent,
                    "reason": confidence.reason})
            result.append(prof_result)

    return result


def process_types(profile_list):
    """Process profiles with port types and return list of verdicts."""
    # Just filling in fake data for now
    # TODO: real data
    result = []
    all_port_types = ["FOO-1492B", "SUX-9000"]
    for profile in profile_list:
        if "portCount" in profile:
            prof_result = {"profileId": profile["profileId"],
                           "portTypes": []}
            for port_type in all_port_types:
                prof_result["portTypes"].append({"type": port_type,
                                                 "confidence": 100})
            result.append(prof_result)

    return result


def process(profile_list):
    """Process profiles and return verdicts."""
    result = []
    result.extend(process_locations(profile_list))
    result.extend(process_types(profile_list))
    return result


def is_passed(verdict):
    """Return False if the verdict has any confidence < 100"""
    for profile in verdict:
        for locations in profile["portLocations"]:
            if "confidence" not in locations or locations["confidence"] < 100:
                return False
    return True
