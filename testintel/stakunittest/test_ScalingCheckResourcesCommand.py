"""Unit test ScalingCheckResourcesCommand"""

from StcIntPythonPL import (CScriptableCreator)
from ..ScalingCheckResourcesCommand import (
    reset, validate_lengths, validate_features)

# import os


def test_validate_lengths():
    assert validate_lengths(["foo", "bar"], [1, 2, 3]) != ""
    assert validate_lengths(["foo", "bar"], [1, 2]) == ""


def test_validate_features():
    assert validate_features(["deviceCount"]) == ""
    assert validate_features(["notARealFeature"]) != ""


def test_reset():
    assert reset()


def test_mins(stc):
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingCheckResources")
    command.SetCollection("FeatureNameList", ["deviceCount"])
    command.SetCollection("FeatureValueList", ["1"])
    command.Execute()
    assert command.Get("MinMemoryMb") >= 512
    assert command.Get("MinCores") >= 1
    assert command.Get("MinSpiMips") >= 1
