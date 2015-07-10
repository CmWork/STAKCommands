"""Unit test port_info"""

import pytest
from StcIntPythonPL import (CScriptableCreator, CStcSystem)
from ..port_info import (PhysicalPortMap, convert_supported_to_max,
                         convert_speed_to_val, convert_val_to_speed)


def test_canonize():
    assert PhysicalPortMap._canonize("1.2.3.4/1/1") == "//1.2.3.4/1/1"
    assert PhysicalPortMap._canonize("/1.2.3.4/1/1") == "//1.2.3.4/1/1"
    assert PhysicalPortMap._canonize("//1.2.3.4/1/1") == "//1.2.3.4/1/1"
    assert PhysicalPortMap._canonize(" //1.2.3.4/1/1") == "//1.2.3.4/1/1"
    assert PhysicalPortMap._canonize(" /1.2.3.4/1/1 ") == "//1.2.3.4/1/1"


def test_get_chassis():
    assert PhysicalPortMap._get_chassis("1.2.3.4/1/1") == "1.2.3.4"
    assert PhysicalPortMap._get_chassis(" //foo/1/1") == "foo"


def test_add_chassis_to_map(stc):
    ctor = CScriptableCreator()
    pcm = CStcSystem.Instance().GetObject("PhysicalChassisManager")
    pc0 = ctor.Create("PhysicalChassis", pcm)
    ptm0 = ctor.Create("PhysicalTestModule", pc0)
    ppg0 = ctor.Create("PhysicalPortGroup", ptm0)
    pp0 = ctor.Create("PhysicalPort", ppg0)
    pp0.Set("location", "1.2.3.4/1/1")
    port_map = PhysicalPortMap()

    # add new chassis
    pc1 = ctor.Create("PhysicalChassis", pcm)
    ptm1 = ctor.Create("PhysicalTestModule", pc1)
    ppg1 = ctor.Create("PhysicalPortGroup", ptm1)
    pp1 = ctor.Create("PhysicalPort", ppg1)
    pp1.Set("location", "1.2.3.5/2/2")

    # prevent an actual chassis connect
    port_map.tried_chassis.add("1.2.3.5")

    assert port_map.has_physical_port("1.2.3.4/1/1")
    assert not port_map.has_physical_port("1.2.3.5/2/2")

    port_map.add_chassis(pc1)
    assert port_map.has_physical_port("1.2.3.4/1/1")
    assert port_map.has_physical_port("1.2.3.5/2/2")


def make_ports():
    ctor = CScriptableCreator()
    pcm = CStcSystem.Instance().GetObject("PhysicalChassisManager")
    pc0 = ctor.Create("PhysicalChassis", pcm)
    pc1 = ctor.Create("PhysicalChassis", pcm)
    ptm0_0 = ctor.Create("PhysicalTestModule", pc0)
    ptm0_1 = ctor.Create("PhysicalTestModule", pc0)
    ptm1_0 = ctor.Create("PhysicalTestModule", pc1)
    ppg0_0_0 = ctor.Create("PhysicalPortGroup", ptm0_0)
    ppg0_0_1 = ctor.Create("PhysicalPortGroup", ptm0_0)
    ppg0_1_0 = ctor.Create("PhysicalPortGroup", ptm0_1)
    ppg1_0_0 = ctor.Create("PhysicalPortGroup", ptm1_0)
    pp0_0_0_0 = ctor.Create("PhysicalPort", ppg0_0_0)
    pp0_0_0_0.Set("location", "1.2.3.4/1/1")
    pp0_0_0_1 = ctor.Create("PhysicalPort", ppg0_0_0)
    pp0_0_0_1.Set("location", "1.2.3.4/1/2")
    pp0_0_1_0 = ctor.Create("PhysicalPort", ppg0_0_1)
    pp0_0_1_0.Set("location", "1.2.3.4/1/3")
    pp0_1_0_0 = ctor.Create("PhysicalPort", ppg0_1_0)
    pp0_1_0_0.Set("location", "1.2.3.4/2/1")
    pp1_0_0_0 = ctor.Create("PhysicalPort", ppg1_0_0)
    pp1_0_0_0.Set("location", "SOMEHOST/1/1")


def test_has_physical_port(stc):
    make_ports()
    port_map = PhysicalPortMap()
    port_map.tried_chassis.add("somehost")
    assert port_map.has_physical_port("/1.2.3.4/1/1")
    assert port_map.has_physical_port(" 1.2.3.4/1/1 ")
    assert port_map.has_physical_port("//1.2.3.4/1/2")
    assert port_map.has_physical_port("SOMEHOST/1/1")
    assert port_map.has_physical_port("somehost/1/1")
    assert not port_map.has_physical_port("somehost/1/2")


def test_get_physical_port(stc):
    make_ports()
    port_map = PhysicalPortMap()
    phys_port = port_map.get_physical_port("//1.2.3.4/1/1")
    assert phys_port is not None
    assert phys_port.Get("location") == "//1.2.3.4/1/1"


def test_get_test_module(stc):
    make_ports()
    port_map = PhysicalPortMap()
    test_module0 = port_map.get_test_module("//1.2.3.4/1/1")
    test_module1 = port_map.get_test_module("//1.2.3.4/1/2")
    test_module2 = port_map.get_test_module("//1.2.3.4/1/3")
    assert test_module0 is not None
    assert test_module0.GetObjectHandle() == test_module1.GetObjectHandle()
    assert test_module0.GetObjectHandle() == test_module2.GetObjectHandle()


def test_get_max_speed(stc):
    make_ports()
    port_map = PhysicalPortMap()
    test_module0 = port_map.get_test_module("//1.2.3.4/1/1")
    test_module0.Set("Model", "EDM-1003B")
    test_module1 = port_map.get_test_module("//1.2.3.4/2/1")
    test_module1.Set("Model", "MX2-40G-Q3")

    assert port_map.get_max_speed("//1.2.3.4/1/1") == 1000**3
    assert port_map.get_max_speed("//1.2.3.4/2/1") == 40*1000**3


def test_convert_supported_to_max():
    assert convert_supported_to_max('1G 1') == 1000000000
    assert convert_supported_to_max('1G 1 1K 2') == 1000000000
    assert convert_supported_to_max('1G 1 2G 2') == 2000000000
    assert convert_supported_to_max('5G 1 2G 2') == 5000000000
    assert convert_supported_to_max('5G 1 2G 2 1M 3') == 5000000000


def test_convert_speed_to_val():
    assert convert_speed_to_val('1G') == 1000000000
    assert convert_speed_to_val('2G') == 2000000000
    assert convert_speed_to_val('40G') == 40000000000
    assert convert_speed_to_val('10M') == 10000000
    assert convert_speed_to_val('100M') == 100000000
    assert convert_speed_to_val('44K') == 44000
    assert convert_speed_to_val('1T') == 1000**4
    assert convert_speed_to_val('0T') == 0
    pytest.raises(ValueError, convert_speed_to_val, '1U')


def test_convert_val_to_speed():
    assert convert_val_to_speed(1000000000) == '1 Gbps'
    assert convert_val_to_speed(2000000000) == '2 Gbps'
    assert convert_val_to_speed(40000000000) == '40 Gbps'
    assert convert_val_to_speed(10000000) == '10 Mbps'
    assert convert_val_to_speed(100000000) == '100 Mbps'
    assert convert_val_to_speed(44000) == '44 Kbps'
    assert convert_val_to_speed(1000**4) == '1 Tbps'
    assert convert_val_to_speed(1500) == '1.5 Kbps'
    assert convert_val_to_speed(100) == '100 bps'
    assert convert_val_to_speed(0) == '0 bps'
    assert convert_val_to_speed(-100) == '-100 bps'
    # does not support metric prefixes for more negative numbers
    pytest.raises(ValueError, convert_val_to_speed, 1000**6)


def test_has_only_soft_fpga():
    make_ports()
    port_map = PhysicalPortMap()
    test_module0 = port_map.get_test_module("//1.2.3.4/1/1")
    test_module0.Set("PartNum", "EDM-1003B")
    test_module0.Set("ProductFamily", "RAVEN")
    test_module1 = port_map.get_test_module("//1.2.3.4/2/1")
    test_module1.Set("PartNum", "VM-1G-V1-1P")
    test_module1.Set("ProductFamily", "VTC")
    test_module2 = port_map.get_test_module("//somehost/1/1")
    test_module2.Set("PartNum", "STCA-1G-V1")
    test_module2.Set("ProductFamily", "STCA")
    assert not port_map.has_only_soft_fpga("//1.2.3.4/1/1")
    assert port_map.has_only_soft_fpga("//1.2.3.4/2/1")
    assert port_map.has_only_soft_fpga("//somehost/1/1")


def test_has_good_version():
    make_ports()
    port_map = PhysicalPortMap()
    test_module0 = port_map.get_test_module("//1.2.3.4/1/1")
    test_module0.Set("IsFirmwareVersionValid", True)
    test_module0.Set("FirmwareVersionStatus", "Sweet")
    test_module1 = port_map.get_test_module("//1.2.3.4/2/1")
    test_module1.Set("IsFirmwareVersionValid", False)
    test_module1.Set("FirmwareVersionStatus", "Fubar")
    assert port_map.has_good_version("//1.2.3.4/1/1")[0]
    assert port_map.has_good_version("//1.2.3.4/1/1")[1] == ""
    assert not port_map.has_good_version("//1.2.3.4/2/1")[0]
    assert port_map.has_good_version("//1.2.3.4/2/1")[1] == "Fubar"


def test_get_unreserved(stc, monkeypatch):
    make_ports()
    port_map = PhysicalPortMap()

    def mock_is_reserved(port):
        location = port.Get("Location")
        return "4/1/2" in location or "4/1/3" in location

    monkeypatch.setattr(port_map, "is_reserved", mock_is_reserved)
    assert port_map.get_unreserved([]) == []
    assert port_map.get_unreserved(["1.2.3.4/2/1"]) == ["1.2.3.4/2/1"]
    assert port_map.get_unreserved(["1.2.3.4/1/2"]) == []
    assert port_map.get_unreserved(["1.2.3.4/1/1", "1.2.3.4/1/2",
                                    "1.2.3.4/1/3"]) == ["1.2.3.4/1/1"]


def test_memo():
    port_map = PhysicalPortMap()
    port_map.memo('1.2.3.4/1/1')['foo'] = 'bar'
    port_map.memo('1.2.3.4/1/2')['foo'] = 'boo'
    assert port_map.memo('//1.2.3.4/1/1') == {'foo': 'bar'}
    assert port_map.memo('//1.2.3.4/1/2') == {'foo': 'boo'}
    assert port_map.memo('//1.2.3.4/1/3') == {}
