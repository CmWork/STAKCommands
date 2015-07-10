"""Unit test ScalingGetValidPortTypesCommand"""

from StcIntPythonPL import (CScriptableCreator)
from ..ScalingGetValidPortTypesCommand import (
    PORT_TYPES, validate_filter, reset)


def test_reset():
    assert reset()


def test_filter():
    assert validate_filter(["MX-10G-S2"]) == ""
    assert validate_filter(["NOT-A-PORT"]) != ""


def test_invalid(stc):
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingGetValidPortTypes")
    command.Set("MinMemoryMb", 1024 * 1024)  # 1 TB
    command.Set("MinCores", 1024)            # 1 kCore
    command.Set("MinSpiMips", 1024 * 1024)   # 1 SpiTips?
    command.Execute()
    assert command.GetCollection("PortTypeList") == []


def test_defaults(stc):
    """The defaults should include every port type available"""
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingGetValidPortTypes")
    command.Execute()
    result = command.GetCollection("PortTypeList")
    assert "MX-10G-S2" in result
    assert "MX-10G-S4" in result
    assert "CM-1G-D4" in result


def test_minimums(stc):
    """The minimums should include every port type available"""
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingGetValidPortTypes")
    command.Set("MinMemoryMb", 1)  # 1 MB
    command.Set("MinCores", 1)     # 1 core
    command.Set("MinSpiMips", 1)   # 1 SpiMips
    command.Execute()
    result = command.GetCollection("PortTypeList")
    assert len(result) == len(PORT_TYPES)


def test_supervalid_filtered(stc):
    ctor = CScriptableCreator()
    command = ctor.CreateCommand("spirent.testintel.ScalingGetValidPortTypes")
    command.Set("MinMemoryMb", 1)  # 1 MB
    command.Set("MinCores", 1)     # 1 core
    command.Set("MinSpiMips", 1)   # 1 Mips
    command.SetCollection("FilterPortTypeList",
                          ["MX-10G-S2"])  # Only check this one
    command.Execute()
    result = command.GetCollection("PortTypeList")
    assert result == ["MX-10G-S2"]
