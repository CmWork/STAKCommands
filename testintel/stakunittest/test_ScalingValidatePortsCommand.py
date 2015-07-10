"""Unit test ScalingValidatePortsCommand"""

from StcIntPythonPL import (CScriptableCreator)
from ..port_info import PhysicalPortMap
from ..ScalingValidatePortsCommand import (
    reset, extract_all_features, is_passed, process_locations,
    process_types, validate_json, validate_schema)


def test_validate_json():
    """Make sure json validation works"""
    assert validate_json("{}", "foo") == ({}, "")
    assert validate_json("{", "foo")[0] is None
    assert validate_json("{", "foo")[1] != ""
    assert validate_json('{"x":1,"y":2}', "foo") == ({'x': 1, 'y': 2}, "")
    assert validate_json('{"x":1,"y":2,}', "foo")[0] is None
    assert validate_json('{"x":1,"y":2,}', "foo")[1] != ""


def test_validate_schema():
    """Make sure schema validation works"""
    schema = {
        'type': 'object',
        'properties': {
            'foo': {'type': 'number'}
        },
        'required': ['foo']
    }
    assert validate_schema({"foo": 123}, schema) == ""
    assert validate_schema({"foo": "bar"}, schema) != ""
    assert validate_schema({"boo": 123}, schema) != ""


def test_extract_all_features():
    """Verify extract_all_features"""
    assert extract_all_features([]) == set([])
    profile_a = {
        "profileId": "a",
        "portLocations": ["//1.2.3.4/1/2", "//1.2.3.4/2/3"],
        "deviceCount": 100,
        "someFeature": 99,
        "otherFeature": 98,
    }
    profile_b = {
        u"profileId": u"b",
        u"portCount": 4,
        u"deviceCount": 100,
        u"fooFeature": 99,
        u"barFeature": 98,
    }
    assert extract_all_features([profile_a]) == set([
        "deviceCount", "someFeature", "otherFeature"])
    assert extract_all_features([profile_b]) == set([
        "deviceCount", "fooFeature", "barFeature"])
    assert extract_all_features([profile_a, profile_b]) == set([
        "deviceCount", "someFeature", "otherFeature", "fooFeature",
        "barFeature"])


def test_reset():
    assert reset()


def test_defaults():
    """Verify that running with defaults doesn't give a weird error"""
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingValidatePorts")
    command.Execute()
    assert command.Get("PassFailState") == "PASSED"
    assert command.Get("Verdict") == "[]"


def test_process_locations(monkeypatch):
    """Verify that running with port location returns a loc-based result."""
    profile_list = [
        {
            "profileId": "foo",
            "portLocations": [
                "//10.14.16.27/1/1",
                "//10.14.16.27/1/2",
            ],
            "deviceCount": 100,
        },
        {
            "profileId": "bar",
            "portCount": 3,
            "deviceCount": 100,
        }
    ]

    port_map = PhysicalPortMap()
    # keep it from actually connecting to 10.14.16.27
    monkeypatch.setattr(port_map, "has_physical_port", lambda loc: True)
    monkeypatch.setattr(port_map, "has_good_version", lambda loc: (True, ""))
    monkeypatch.setattr(port_map, "has_only_soft_fpga", lambda loc: False)

    result = process_locations(profile_list, port_map)
    # should only return result for foo, both ports
    assert len(result) == 1
    assert result[0]["profileId"] == profile_list[0]["profileId"]
    assert len(result[0]["portLocations"]) == 2
    result_locations = set([result[0]["portLocations"][0]["location"],
                            result[0]["portLocations"][1]["location"]])
    assert result_locations == set(profile_list[0]["portLocations"])
    assert "confidence" in result[0]["portLocations"][0]
    assert "reason" in result[0]["portLocations"][0]
    assert "confidence" in result[0]["portLocations"][1]
    assert "reason" in result[0]["portLocations"][1]


def test_port_count():
    """Verify that running with port count returns a list of port types."""
    profile_list = [
        {
            "profileId": "foo",
            "portLocations": [
                "//10.14.16.27/1/1",
                "//10.14.16.27/1/2",
            ],
            "deviceCount": 100,
        },
        {
            "profileId": "bar",
            "portCount": 3,
            "deviceCount": 100,
        }
    ]
    result = process_types(profile_list)
    # should only return result for bar
    assert len(result) == 1
    assert result[0]["profileId"] == profile_list[1]["profileId"]
    assert "portTypes" in result[0]
    assert len(result[0]["portTypes"]) > 0
    for types in result[0]["portTypes"]:
        assert "type" in types
        assert "confidence" in types
        assert types["confidence"] > 0


def test_is_passed():
    """Verify that the state is passed if and only if all confidence is 100"""
    assert is_passed([])
    verdict = [{
        "profileId": "foo",
        "portLocations": [{
            "location": "//10.1.2.3/1/1",
            "confidence": 100,
            "reason": ""
        }, {
            "location": "//10.1.2.3/2/1",
            "confidence": 100,
            "reason": ""
        }],
    }, {
        "profileId": "bar",
        "portLocations": [{
            "location": "//10.1.2.3/4/1",
            "confidence": 100,
            "reason": ""
        }]
    }]
    assert is_passed(verdict)
    # lower confidence in first profile/port
    verdict[0]["portLocations"][0]["confidence"] = 99
    assert not is_passed(verdict)
    # lower confidence in last profile/port
    verdict[0]["portLocations"][0]["confidence"] = 100
    verdict[1]["portLocations"][0]["confidence"] = 75
    assert not is_passed(verdict)
    # restore confidence
    verdict[1]["portLocations"][0]["confidence"] = 100
    assert is_passed(verdict)
