from StcIntPythonPL import *
import json
import jsonschema


# Convert unicode to string (originally from traffic center)
def dumps(data):
    if type(data) == unicode:
        return str(data)
    if type(data) == list:
        return [dumps(item) for item in data]
    if type(data) == dict:
        ret = {}
        for key, value in data.iteritems():
            new_key = dumps(key)
            new_val = dumps(value)
            ret[new_key] = new_val
        return ret
    return data


# Load JSON and convert from unicode
def load_json(json_str, object_pairs_hook_arg=None):
    plLogger = PLLogger.GetLogger("methodology")
    u_json_obj = None
    try:
        u_json_obj = json.loads(json_str,
                                object_pairs_hook=object_pairs_hook_arg)
    except:
        err_str = "JSON string: " + str(json_str) + \
            " is not valid JSON."
        plLogger.LogError(err_str)
        return err_str, {}
    return "", dumps(u_json_obj)


# Validate JSON str as valid JSON.  If schema_str is passed
# in, validate it is valid JSON and validate JSON str against it.
# Returns "" if no error, the string error if there is.
def validate_json(json_str, schema_str=None):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("json_utils.validate_json.start")
    plLogger.LogDebug("json_str: " + str(json_str))
    plLogger.LogDebug("schema_str: " + str(schema_str))

    json_obj = None
    try:
        json_obj = json.loads(json_str)
    except:
        return "JSON string: " + str(json_str) + \
            " is not valid JSON."
    if schema_str is not None:
        schema_obj = None
        try:
            schema_obj = json.loads(schema_str)
        except:
            return "Schema string: " + str(schema_str) + \
                " is not valid JSON."
        try:
            jsonschema.validate(json_obj, schema_obj)
        except jsonschema.ValidationError, err:
            return "JSON object does not conform to given " + \
                "schema: " + str(err)
    return ""
