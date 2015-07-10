"""Unit test TrafficSummarizeCommand"""

from StcIntPythonPL import (CHandleRegistry, CScriptableCreator,
                            CStcSystem, RelationType)
import sys
import os
sys.path.append(os.path.join(os.getcwd(),
                             'STAKCommands', 'spirent', 'testintel'))
import TrafficSummarizeCommand as tsc


def test_validate(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)
    assert tsc.validate(port.GetObjectHandle(), True, False, "") == ""
    assert tsc.validate(port.GetObjectHandle(), False, True, "") == ""
    assert tsc.validate(project.GetObjectHandle(), True, True, "") != ""
    assert tsc.validate("blah", True, False, "") != ""
    assert tsc.validate("", True, True, "") != ""


def test_reset():
    assert tsc.reset()


def create_devices(port, count):
    """Create a bunch of generic devices affiliated with port."""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("DeviceCreate")
    cmd.Set("DeviceCount", count)
    cmd.Set("Port", port.GetObjectHandle())
    cmd.Execute()
    # should always have exactly one item in the list
    dev_hnd = cmd.GetCollection("ReturnList")[0]
    cmd.MarkDelete()
    return CHandleRegistry.Instance().Find(dev_hnd)


def update_generator(generator):
    """Execute the GeneratorUpdate command (after modifying rates)."""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("GeneratorUpdate")
    cmd.Set("Generator", generator.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()


def test_get_fpga_capability(stc):
    ctor = CScriptableCreator()
    system = CStcSystem.Instance()
    project = system.GetObject("project")
    port = ctor.Create("port", project)
    phys_cm = system.GetObject("PhysicalChassisManager")
    phys_chassis = ctor.Create("PhysicalChassis", phys_cm)
    phys_tm = ctor.Create("PhysicalTestModule", phys_chassis)
    phys_pg = ctor.Create("PhysicalPortGroup", phys_tm)
    phys_port = ctor.Create("PhysicalPort", phys_pg)
    phys_port.AddObject(port, RelationType("PhysicalLogical"))
    phys_tm.Set("Model", "DX-10G-S32")
    phys_tm.Set("ProductFamily", "Thunderbird")
    assert tsc.get_fpga_capability(port) == "SOFT_AND_HARD"
    phys_tm.Set("Model", "VM-1G-V1-1P")
    phys_tm.Set("ProductFamily", "VTC")
    assert tsc.get_fpga_capability(port) == "SOFT_ONLY"
    phys_tm.Set("Model", "CV-10G-S8")
    phys_tm.Set("ProductFamily", "Pyro")
    assert tsc.get_fpga_capability(port) == "HARD_ONLY"


def test_is_soft(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # one hard and one soft streamblock
    streamblocks = [ctor.Create("streamblock", port),
                    ctor.Create("streamblock", port)]
    streamblocks[1].Set("EnableHighSpeedResultAnalysis", False)

    # HARD_ONLY
    assert not tsc.is_soft('HARD_ONLY', streamblocks[0])
    assert not tsc.is_soft('HARD_ONLY', streamblocks[1])

    # if a port supports both it supports both
    assert not tsc.is_soft('SOFT_AND_HARD', streamblocks[0])
    assert tsc.is_soft('SOFT_AND_HARD', streamblocks[1])

    # virtual/STCA ports are soft only
    assert tsc.is_soft('SOFT_ONLY', streamblocks[0])
    assert tsc.is_soft('SOFT_ONLY', streamblocks[1])


def test_get_stream_blocks(stc, monkeypatch):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    def soft_and_hard(port):
        return "SOFT_AND_HARD"
    monkeypatch.setattr(tsc, "get_fpga_capability", soft_and_hard)

    # single (hard) streamblock
    streamblocks = [ctor.Create("streamblock", port)]

    # compare handles, proxies are not necessarily comparable
    all_streamblocks = tsc.get_stream_blocks(port, False)
    soft_streamblocks = tsc.get_stream_blocks(port, True)
    assert ([sb.GetObjectHandle() for sb in all_streamblocks] ==
            [streamblocks[0].GetObjectHandle()])
    assert soft_streamblocks == []

    # one hard, one soft
    streamblocks += [ctor.Create("streamblock", port)]
    streamblocks[1].Set("EnableHighSpeedResultAnalysis", False)

    all_streamblocks = tsc.get_stream_blocks(port, False)
    soft_streamblocks = tsc.get_stream_blocks(port, True)
    assert ([sb.GetObjectHandle() for sb in all_streamblocks] ==
            [sb.GetObjectHandle() for sb in streamblocks])
    assert ([sb.GetObjectHandle() for sb in soft_streamblocks] ==
            [streamblocks[1].GetObjectHandle()])

    # one hard, one soft, one hard inactive, one soft inactive
    streamblocks += [ctor.Create("streamblock", port)]
    streamblocks += [ctor.Create("streamblock", port)]
    streamblocks[2].Set("Active", False)
    streamblocks[3].Set("Active", False)
    streamblocks[3].Set("EnableHighSpeedResultAnalysis", False)

    all_streamblocks = tsc.get_stream_blocks(port, False)
    soft_streamblocks = tsc.get_stream_blocks(port, True)
    assert ([sb.GetObjectHandle() for sb in all_streamblocks] ==
            [streamblocks[0].GetObjectHandle(),
             streamblocks[1].GetObjectHandle()])
    assert ([sb.GetObjectHandle() for sb in soft_streamblocks] ==
            [streamblocks[1].GetObjectHandle()])


def test_get_port_stream_info(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # single streamblock
    streamblocks = [ctor.Create("streamblock", port)]
    assert tsc.get_port_stream_info(port, False)["StreamBlockCount"] == 1
    assert tsc.get_port_stream_info(port, False)["StreamCount"] == 1
    assert tsc.get_port_stream_info(port, False)["FlowCount"] == 1

    # additional streamblock
    streamblocks += [ctor.Create("streamblock", port)]
    assert tsc.get_port_stream_info(port, False)["StreamBlockCount"] == 2
    assert tsc.get_port_stream_info(port, False)["StreamCount"] == 2
    assert tsc.get_port_stream_info(port, False)["FlowCount"] == 2

    # bind first stream with 100 devices
    other_port = ctor.Create("port", project)
    dev = create_devices(port, 100)
    ip = dev.GetObject("ipv4if")
    other_dev = create_devices(other_port, 100)
    other_ip = other_dev.GetObject("ipv4if")
    streamblocks[0].AddObject(ip, RelationType("srcbinding"))
    streamblocks[0].AddObject(other_ip, RelationType("dstbinding"))
    assert tsc.get_port_stream_info(port, False)["StreamBlockCount"] == 2
    assert tsc.get_port_stream_info(port, False)["StreamCount"] == 101
    assert tsc.get_port_stream_info(port, False)["FlowCount"] == 101


def test_get_port_stream_info_mod_count(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # none
    assert tsc.get_port_stream_info(port, False)["AvgModifierCount"] == 0

    # single streamblock
    streamblocks = [ctor.Create("streamblock", port)]
    assert tsc.get_port_stream_info(port, False)["AvgModifierCount"] == 0

    # add a range modifier
    range_mod = ctor.Create("rangemodifier", streamblocks[0])
    range_mod.Set("OffsetReference", "ip_1.tosDiffserv.tos")
    range_mod.Set("Mask", "1")

    assert tsc.get_port_stream_info(port, False)["AvgModifierCount"] == 1

    # add a table modifier
    ctor.Create("tablemodifier", streamblocks[0])
    assert tsc.get_port_stream_info(port, False)["AvgModifierCount"] == 2

    # add a stream block
    streamblocks += [ctor.Create("streamblock", port)]
    assert tsc.get_port_stream_info(port, False)["AvgModifierCount"] == 1

    # add another stream block
    streamblocks += [ctor.Create("streamblock", port)]
    assert (round(tsc.get_port_stream_info(port, False)["AvgModifierCount"], 2)
            == 0.67)


def test_get_port_rate_info_port_based(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # default streamblock
    ctor.Create("streamblock", port)
    assert tsc.get_port_rate_info(port, False)["FpsLoad"] == 84459
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 10
    assert tsc.get_port_rate_info(port, False)["AvgPacketSize"] == 128

    generator = port.GetObject("generator")
    gen_config = generator.GetObject("generatorconfig")

    # set fixed port rate
    gen_config.Set("FixedLoad", 1.0)
    update_generator(generator)
    assert tsc.get_port_rate_info(port, False)["FpsLoad"] == 8445
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 1
    assert tsc.get_port_rate_info(port, False)["AvgPacketSize"] == 128

    # set random port rate
    gen_config.Set("RandomMinLoad", 1.0)
    gen_config.Set("RandomMaxLoad", 3.0)
    gen_config.Set("LoadMode", "RANDOM")
    update_generator(generator)
    assert tsc.get_port_rate_info(port, False)["FpsLoad"] == 16891
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 2
    assert tsc.get_port_rate_info(port, False)["AvgPacketSize"] == 128


def test_get_port_rate_info_rate_based(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # default streamblock
    streamblocks = [ctor.Create("streamblock", port)]
    assert tsc.get_port_rate_info(port, False)["FpsLoad"] == 84459
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 10
    assert tsc.get_port_rate_info(port, False)["AvgPacketSize"] == 128

    generator = port.GetObject("generator")
    gen_config = generator.GetObject("generatorconfig")

    # set fixed port rate - should be ignored
    gen_config.Set("FixedLoad", 1.0)

    # set block rate
    gen_config.Set("SchedulingMode", "RATE_BASED")
    streamblocks[0].Set("Load", 3.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 25338
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 3
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # inactive streamblock
    streamblocks += [ctor.Create("streamblock", port)]
    streamblocks[1].Set("Active", False)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 25338
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 3
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # two active streamblocks
    streamblocks[1].Set("Active", True)
    streamblocks[1].Set("Load", 2.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 42230
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # different lengths
    streamblocks[0].Set("FixedFrameLength", 168)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 36839
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 149.66)

    # random lengths
    streamblocks[0].Set("FrameLengthMode", "INCR")
    streamblocks[0].Set("MinFrameLength", 64)
    streamblocks[0].Set("MaxFrameLength", 1024)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 23541
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 245.5)


def test_get_port_rate_info_priority_based(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)

    # default streamblock
    streamblocks = [ctor.Create("streamblock", port)]
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 84459
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 10
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    generator = port.GetObject("generator")
    gen_config = generator.GetObject("generatorconfig")

    # set fixed port rate - should be ignored
    gen_config.Set("FixedLoad", 1.0)

    # priority mode -- until it's oversubscribed, the same as rate mode
    gen_config.Set("SchedulingMode", "PRIORITY_BASED")
    streamblocks[0].Set("Load", 3.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 25338
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 3
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # inactive streamblock
    streamblocks += [ctor.Create("streamblock", port)]
    streamblocks[1].Set("Active", False)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 25338
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 3
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # two active streamblocks
    streamblocks[1].Set("Active", True)
    streamblocks[1].Set("Load", 2.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 42230
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 128)

    # different lengths
    streamblocks[0].Set("FixedFrameLength", 168)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 36839
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 149.66)

    # random lengths
    streamblocks[0].Set("FrameLengthMode", "INCR")
    streamblocks[0].Set("MinFrameLength", 64)
    streamblocks[0].Set("MaxFrameLength", 1024)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 23541
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 5
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 245.5)
    streamblocks[0].Set("FrameLengthMode", "FIXED")

    # oversubscribe first streamblock - second one not sent
    streamblocks[0].Set("Load", 101.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 664894
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 100
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 168)

    # oversubscribe second streamblock - first still sent
    streamblocks[0].Set("Load", 50.0)
    streamblocks[1].Set("Load", 100.0)
    update_generator(generator)
    assert round(tsc.get_port_rate_info(port, False)["FpsLoad"], 0) == 754744
    assert tsc.get_port_rate_info(port, False)["PercentLoad"] == 100
    assert (round(tsc.get_port_rate_info(port, False)["AvgPacketSize"], 2)
            == 145.62)


def test_run(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("project")
    port = ctor.Create("port", project)
    ctor.Create("streamblock", port)
    cmd = ctor.CreateCommand("spirent.testintel.TrafficSummarize")
    cmd.Set("Port", port.GetObjectHandle())
    cmd.Set("SoftStreamsOnly", False)
    cmd.Execute()
    result = dict(zip(cmd.GetCollection("NameList"),
                      cmd.GetCollection("ValueList")))
    assert result['StreamBlockCount'] == 1
    assert result['StreamCount'] == 1
    assert result['FlowCount'] == 1
    assert result['PercentLoad'] == 10.0
    assert round(result['FpsLoad'], 0) == 84459
    assert result['AvgPacketSize'] == 128
    assert result['AvgModifierCount'] == 0
