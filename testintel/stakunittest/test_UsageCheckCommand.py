"""Unit test UsageCheckCommand"""

from StcIntPythonPL import (CScriptableCreator, CStcSystem, RelationType)
from ..UsageCheckCommand import (are_names_valid, create_il_usage_command,
                                 expand_per_port, format_il_usage,
                                 get_bll_usage, get_cpu_ticks_from_cpuload,
                                 get_cpu_perc_from_cpuload, get_online_ports,
                                 gen_physical_port_pairs, get_tm_info,
                                 map_ports_to_portgroups, reset, store_usage,
                                 strip_location, validate)

import os
import tempfile


def test_validate(stc):
    assert len(validate("")) != 0
    assert validate("whatever") == ""


def test_reset():
    assert reset()


def test_get_online_ports(stc):
    project = CStcSystem.Instance().GetObject('project')
    assert get_online_ports(project) == []
    # can't test this further without actually bringing ports online


def test_strip_location():
    # Happens when there are multiple online chassis
    assert strip_location("Foo //1.2.3.4/5/6") == "Foo"
    assert strip_location("Foo/Bar/Boop //2.2.2.2/3/4") == "Foo/Bar/Boop"
    # Happens when all ports are on the same chassis
    assert strip_location("Foo //1/2") == "Foo"
    assert strip_location("Foo/Bar/Boop //3/4") == "Foo/Bar/Boop"
    # Happens when appendlocation is false
    assert strip_location("Foo") == "Foo"
    assert strip_location("Foo/Bar/Boop") == "Foo/Bar/Boop"
    # Extra space
    assert strip_location(" Foo ") == "Foo"
    assert strip_location(" Foo/Bar/Boop ") == "Foo/Bar/Boop"


def test_are_names_valid():
    assert are_names_valid(["Foo", "Bar", "Boobar"])
    assert not are_names_valid(["Foo", "Bar", "Port"])
    assert not are_names_valid(["Foo", "Bar", "Foo"])


def test_get_bll_usage(stc):
    project = CStcSystem.Instance().GetObject("project")
    port1 = CScriptableCreator().Create("port", project)
    port2 = CScriptableCreator().Create("port", project)
    assert get_bll_usage([port1, port2]) == [{}, {}]
    # can't test this further without actually applying stuff


def test_get_cpu_perc_from_cpuload():
    """Verify that get_cpu... returns sum of non-idle"""
    output = "cpu user=130 nice=5 system=20 idle=830 iowait=15 irq=0 softirq=0"
    assert get_cpu_perc_from_cpuload(output) == 17
    # change values
    output = "cpu user=890 nice=0 system=20 idle=70 iowait=0 irq=10 softirq=10"
    assert get_cpu_perc_from_cpuload(output) == 93
    # remove some columns
    output = "cpu user=900 nice=10 system=20 idle=70"
    assert get_cpu_perc_from_cpuload(output) == 93


def test_get_cpu_ticks_from_cpuload():
    """Verify that get_cpu... returns (sum(!idle), total) from each line"""
    output = \
        "cpu user=140 nice=10 system=20 idle=830 iowait=0 irq=0 softirq=0\n" \
        "cpu0 user=50 nice=0 system=0 idle=940 iowait=10 irq=0 softirq=0\n" \
        "cpu1 user=10 nice=0 system=10 idle=970 iowait=0 irq=10 softirq=0\n" \
        "cpu2 user=80 nice=0 system=0 idle=910 iowait=0 irq=0 softirq=10\n"
    assert get_cpu_ticks_from_cpuload(output.splitlines()) == (
        [170, 60, 30, 90], 1000)
    # change values
    output = \
        "cpu user=900 nice=0 system=20 idle=70 iowait=10 irq=0 softirq=0\n" \
        "cpu0 user=900 nice=0 system=20 idle=70 iowait=0 irq=0 softirq=10\n"
    assert get_cpu_ticks_from_cpuload(output.splitlines()) == (
        [930, 930], 1000)
    # remove some columns
    output = \
        "cpu user=900 nice=20 system=10 idle=70\n" \
        "cpu0 user=900 nice=0 system=30 idle=70\n"
    assert get_cpu_ticks_from_cpuload(output.splitlines()) == (
        [930, 930], 1000)


def test_format_il_usage():
    output = "MemTotal:      3871756 kB\nMemFree:       3460344 kB\n" \
        "0.31 0.09 0.02 1/104 29164\n" \
        "cpu user=140 nice=0 system=30 idle=830 iowait=0 irq=0 softirq=0\n" \
        "cpu0 user=50 nice=0 system=10 idle=940 iowait=0 irq=0 softirq=0\n" \
        "cpu1 user=10 nice=0 system=20 idle=970 iowait=0 irq=0 softirq=0\n" \
        "cpu2 user=80 nice=0 system=10 idle=910 iowait=0 irq=0 softirq=0\n" \
        "cpu user=140 nice=0 system=30 idle=830 iowait=0 irq=0 softirq=0\n"
    result0, result1 = format_il_usage([output, output])
    assert result0 == result1
    assert result0['MemTotal'] == 3871756
    assert result0['MemUsed'] == 3871756 - 3460344
    assert result0['LoadAvg1Min'] == 0.31
    assert result0['CpuPercent'] == 17
    assert result0['CpuUsed'] == 170
    assert result0['CpuUsed0'] == 60
    assert result0['CpuUsed1'] == 30
    assert result0['CpuUsed2'] == 90
    assert result0['CpuTotal'] == 1000


def test_gen_physical_port_pairs(stc):
    system = CStcSystem.Instance()
    project = system.GetObject("project")
    ctor = CScriptableCreator()
    port_list = [ctor.Create("port", project) for _ in range(3)]
    phys_chassis_mgr = system.GetObject("physicalchassismanager")
    phys_chassis = ctor.Create("physicalchassis", phys_chassis_mgr)
    phys_tm_list = [ctor.Create("physicaltestmodule", phys_chassis)
                    for _ in range(2)]
    phys_pg_list = [ctor.Create("physicalportgroup", phys_tm)
                    for phys_tm in phys_tm_list]
    phys_port_list = [ctor.Create("physicalport", phys_pg)
                      for phys_pg in (phys_pg_list[0], phys_pg_list[1],
                                      phys_pg_list[1])]
    for port, phys_port in zip(port_list, phys_port_list):
        port.AddObject(phys_port, RelationType.ReverseDir("PhysicalLogical"))
    # Lag ports don't have a physical port but they may still be 'online'
    port_list.append(ctor.Create("port", project))

    pairs = gen_physical_port_pairs(port_list)
    assert len(list(pairs)) == len(port_list) - 1
    for pair, phys_port in zip(pairs, phys_port_list):
        assert pair[1] == phys_port
        assert pair[0] == phys_port.GetObject('Port',
                                              RelationType('PhysicalLogical'))


def test_map_ports_to_portgroups(stc):
    system = CStcSystem.Instance()
    project = system.GetObject("project")
    ctor = CScriptableCreator()
    port_list = [ctor.Create("port", project) for _ in range(3)]
    phys_chassis_mgr = system.GetObject("physicalchassismanager")
    phys_chassis = ctor.Create("physicalchassis", phys_chassis_mgr)
    phys_tm_list = [ctor.Create("physicaltestmodule", phys_chassis)
                    for _ in range(2)]
    phys_pg_list = [ctor.Create("physicalportgroup", phys_tm)
                    for phys_tm in phys_tm_list]
    phys_port_list = [ctor.Create("physicalport", phys_pg)
                      for phys_pg in (phys_pg_list[0], phys_pg_list[1],
                                      phys_pg_list[1])]
    for port, phys_port in zip(port_list, phys_port_list):
        port.AddObject(phys_port, RelationType.ReverseDir("PhysicalLogical"))
    # the mapper should combine all ports sharing a physical parent,
    # leaving the last
    pg_map = map_ports_to_portgroups(port_list)
    pg_hnd_list = [phys_pg.GetObjectHandle() for phys_pg in phys_pg_list]
    assert pg_map == {pg_hnd_list[0]: port_list[0],
                      pg_hnd_list[1]: port_list[2]}


def test_expand_per_port(stc):
    system = CStcSystem.Instance()
    project = system.GetObject("project")
    ctor = CScriptableCreator()
    port_list = [ctor.Create("port", project) for _ in range(3)]
    phys_chassis_mgr = system.GetObject("physicalchassismanager")
    phys_chassis = ctor.Create("physicalchassis", phys_chassis_mgr)
    phys_tm_list = [ctor.Create("physicaltestmodule", phys_chassis)
                    for _ in range(2)]
    phys_pg_list = [ctor.Create("physicalportgroup", phys_tm)
                    for phys_tm in phys_tm_list]
    phys_port_list = [ctor.Create("physicalport", phys_pg)
                      for phys_pg in (phys_pg_list[0], phys_pg_list[1],
                                      phys_pg_list[1])]
    for port, phys_port in zip(port_list, phys_port_list):
        port.AddObject(phys_port, RelationType.ReverseDir("PhysicalLogical"))
    pg_list = ["Results", "RESULTS"]
    pgh_to_port = {phys_pg_list[0].GetObjectHandle(): port_list[0],
                   phys_pg_list[1].GetObjectHandle(): port_list[2]}
    # this should take the Results for port1 and port3 and duplicate port3's
    # result for port2, which shares the same port group
    output_list = expand_per_port(pg_list, port_list, pgh_to_port)
    # depends on ordering of keys -- in practice the lists are in the same
    # order as the dict
    if pgh_to_port.keys()[0] == phys_pg_list[0].GetObjectHandle():
        assert output_list == ["Results", "RESULTS", "RESULTS"]
    else:
        assert output_list == ["RESULTS", "Results", "Results"]


def test_create_il_usage_command(stc):
    project = CStcSystem.Instance().GetObject("project")
    port1 = CScriptableCreator().Create("port", project)
    port2 = CScriptableCreator().Create("port", project)
    cmd = create_il_usage_command([port1, port2])
    port_list = cmd.GetCollection("PortList")
    assert port1.GetObjectHandle() in port_list
    assert port2.GetObjectHandle() in port_list
    cmd_cmd = cmd.Get("cmd")
    # just generally verify, don't specifically check the string exactly
    assert "meminfo" in cmd_cmd
    assert "loadavg" in cmd_cmd
    assert "cpu-load" in cmd_cmd
    cmd.MarkDelete()


def test_get_tm_info(stc):
    system = CStcSystem.Instance()
    project = system.GetObject("project")
    ctor = CScriptableCreator()
    port1 = ctor.Create("port", project)
    port2 = ctor.Create("port", project)
    phys_chassis_mgr = system.GetObject("physicalchassismanager")
    phys_chassis = ctor.Create("physicalchassis", phys_chassis_mgr)
    phys_tm1 = ctor.Create("physicaltestmodule", phys_chassis)
    phys_tm2 = ctor.Create("physicaltestmodule", phys_chassis)
    phys_pg1 = ctor.Create("physicalportgroup", phys_tm1)
    phys_pg2 = ctor.Create("physicalportgroup", phys_tm2)
    phys_port1 = ctor.Create("physicalport", phys_pg1)
    phys_port2 = ctor.Create("physicalport", phys_pg2)
    port1.AddObject(phys_port1, RelationType.ReverseDir("PhysicalLogical"))
    port2.AddObject(phys_port2, RelationType.ReverseDir("PhysicalLogical"))
    phys_tm1.Set("Name", "Booya!")
    phys_tm2.Set("Name", "Sucka!")
    assert get_tm_info([port1, port2], "Name") == ["Booya!", "Sucka!"]


def test_store_usage():
    usage_file = tempfile.NamedTemporaryFile(delete=False)
    usage_file.close()
    store_usage({'test': 123, 'foo': 'bar'}, usage_file.name)
    with open(usage_file.name, "r") as usage_after:
        line = usage_after.readline()
        assert '"test": 123' in line
        assert '"foo": "bar"' in line
    os.unlink(usage_file.name)
