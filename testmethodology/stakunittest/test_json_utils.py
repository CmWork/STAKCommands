from StcIntPythonPL import *
import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), "STAKCommands",
                             "spirent", "methodology"))
import spirent.methodology.utils.json_utils as json_utils


def test_dumps():
    # Simple types
    t_dict = {}
    t_dict[unicode("scalar_str")] = unicode("str_val")
    t_dict[unicode("scalar_int")] = 123
    t_dict[unicode("list_str")] = [unicode("a"), unicode("b"),
                                   unicode("c"), unicode("d")]
    sub_dict = {}
    sub_dict["scalar_str"] = unicode("str_val2")
    sub_dict["list_str"] = [unicode("a2"), unicode("b2")]
    sub_dict["dict_str"] = {unicode("a"): unicode("1"),
                            unicode("b"): unicode("2")}
    t_dict[unicode("dict_str")] = sub_dict

    ret_val = json_utils.dumps(t_dict)
    for key in ret_val.keys():
        assert type(key) == str
    assert type(ret_val["scalar_str"]) == str
    assert type(ret_val["scalar_int"]) == int
    for item in ret_val["list_str"]:
        assert type(item) == str
    assert type(ret_val["dict_str"]["scalar_str"]) == str
    assert type(ret_val["dict_str"]["list_str"][0]) == str
    assert type(ret_val["dict_str"]["list_str"][1]) == str
    for key in ret_val["dict_str"]["dict_str"].keys():
        assert type(key) == str
    assert type(ret_val["dict_str"]["dict_str"]["a"]) == str
    assert type(ret_val["dict_str"]["dict_str"]["b"]) == str


def test_load_json():
    t_dict = {}
    t_dict["a"] = 1.0
    t_dict["b"] = "str_value"
    j_str = json.dumps(t_dict)
    # assert type(j_str) == str
    err_str, j_dict = json_utils.load_json(j_str)
    assert err_str == ""
    assert type(j_dict) == dict

    # Type testing of the contents of j_dict
    # is handled in test_dumps.

    # Invalid JSON
    t_dict = {"abc"}
    err_str, j_dict = json_utils.load_json(str(t_dict))
    assert "is not valid JSON." in err_str
    assert j_dict == {}


def test_validate_json(stc):
    plLogger = PLLogger.GetLogger("test_validate_json")
    plLogger.LogInfo("start")

    # Build a simple schema
    s_dict = {}
    s_dict["type"] = "object"
    s_dict["required"] = ["devTag", "weight", "modList"]
    s_dict["properties"] = {}
    s_dict["properties"]["devTag"] = {"type": "string"}
    s_dict["properties"]["age"] = {"type": "number"}
    s_dict["properties"]["weight"] = {"type": "number"}

    mod_dict = {}
    mod_dict["type"] = "array"
    mod_dict["items"] = {}
    mod_dict["items"]["type"] = "object"
    mod_dict["items"]["properties"] = {}
    mod_dict["items"]["properties"]["key"] = {"type": "string"}
    mod_dict["items"]["properties"]["name"] = {"type": "string"}
    mod_dict["items"]["required"] = ["key"]

    s_dict["properties"]["mod_list"] = mod_dict

    # Build sample JSON
    j_dict = {}
    j_dict["devTag"] = "devTag Name"
    j_dict["weight"] = 100.0
    j_dict["modList"] = []
    j_dict["modList"].append({"name": "me", "key": "me.123"})
    j_dict["modList"].append({"name": "you", "key": "you.123"})

    schema_str = json.dumps(s_dict)
    json_str = json.dumps(j_dict)
    plLogger.LogInfo("schema_str: " + schema_str)
    plLogger.LogInfo("json_str: " + json_str)

    # Positive Test (no schema)
    res = json_utils.validate_json(json_str)
    assert res == ""

    # Positive Test (with schema)
    res = json_utils.validate_json(json_str, schema_str)
    assert res == ""

    # Negative Test (invalid JSON)
    res = json_utils.validate_json("invalid_json_str")
    assert res.find("is not valid JSON.") != -1

    # Negative Test (valid JSON, invalid schema)
    res = json_utils.validate_json(json_str, "invalid_schema")
    assert res.find("Schema string: ") != -1

    # Negative Test (invalid JSON, valid schema)
    res = json_utils.validate_json("invalid_json", schema_str)
    assert res.find("is not valid JSON.") != -1

    # Build a different schema
    s_dict2 = {}
    s_dict2["type"] = "object"
    s_dict2["required"] = ["devTag", "weight", "yada"]
    s_dict2["properties"] = {}
    s_dict2["properties"]["devTag"] = {"type": "string"}
    s_dict2["properties"]["age"] = {"type": "number"}
    s_dict2["properties"]["weight"] = {"type": "number"}
    s_dict2["properties"]["yada"] = {"type": "number"}
    schema_str2 = json.dumps(s_dict2)

    # Validate schema
    res = json_utils.validate_json(schema_str2)
    assert res == ""

    # Negative Test (valid JSON, wrong schema)
    res = json_utils.validate_json(json_str, schema_str2)
    assert res.find("JSON object does not conform to given schema") != -1
