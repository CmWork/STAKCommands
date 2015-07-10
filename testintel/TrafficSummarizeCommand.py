"""Gathers and summarizes traffic usage for a given port"""
from StcIntPythonPL import (CHandleRegistry, CScriptableCreator, CStcSystem,
                            PLLogger)
from UsageCheckCommand import get_il_usage
import json
import traceback


def validate(Port, SoftStreamsOnly, QueryPort, LogFileName):
    """Validate the command: make sure Port is valid."""
    if not Port:
        return "ERROR: Port is missing"

    try:
        port = CHandleRegistry.Instance().Find(Port)
    except:
        return "ERROR: unable to find port handle %s" % Port

    if not port.IsTypeOf("port"):
        return "ERROR: Port %s is not a port handle"

    return ""


def run(Port, SoftStreamsOnly, QueryPort, LogFileName):
    """Run method: get all streamblocks, summarize and average info."""
    try:
        hnd_reg = CHandleRegistry.Instance()
        port = hnd_reg.Find(Port)

        info = {}
        info.update(get_port_stream_info(port, SoftStreamsOnly))
        if QueryPort:
            info.update(get_port_mem_info(port))

        this_hnd = hnd_reg.Find(__commandHandle__)  # pragma: no flakes
        this_hnd.SetCollection("NameList", info.keys())
        this_hnd.SetCollection("ValueList", info.values())

        if LogFileName:
            log_path = CStcSystem.Instance().GetLogOutputPath() + LogFileName
            store_info(info, log_path)

    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return False

    return True


def reset():
    """True means this command can be reset and re-run"""
    return True


def get_logger():
    """Get the TrafficSummarizeCommand logger"""
    return PLLogger.GetLogger("TrafficSummarizeComman")


def get_port_stream_info(port, soft_only):
    """Summarize stream info across a port"""
    stream_block_list = get_stream_blocks(port, soft_only)
    stream_block_count = float(len(stream_block_list))
    sum_stream_count = 0.0
    sum_flow_count = 0.0
    sum_modifier_count = 0.0
    for stream_block in stream_block_list:
        stream_info = get_stream_info(stream_block)
        sum_stream_count += stream_info["StreamCount"]
        sum_flow_count += stream_info["FlowCount"]
        sum_modifier_count += stream_info["ModifierCount"]

    rate_info = get_port_rate_info(port, soft_only)

    avg_mod_count = (0.0 if not stream_block_count else
                     sum_modifier_count / stream_block_count)

    return {"StreamBlockCount": stream_block_count,
            "StreamCount": sum_stream_count,
            "FlowCount": sum_flow_count,
            "FpsLoad": rate_info["FpsLoad"],
            "PercentLoad": rate_info["PercentLoad"],
            "AvgPacketSize": rate_info["AvgPacketSize"],
            "AvgModifierCount": avg_mod_count}


def get_fpga_capability(port):
    """
    Return fpga capability
    Result is one of 'HARD_ONLY', 'SOFT_ONLY', or 'SOFT_AND_HARD'.
    """
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("GetRcmCapability")
    cmd.SetCollection("Port", [port.GetObjectHandle()])
    cmd.Set("Service", "GA")
    cmd.Set("CapabilityKey", "analyzer/fpgaType")
    cmd.Execute()
    result_enum = cmd.GetCollection("Result")[0]
    # returns enum as "STRING NUMBER"
    result = result_enum.split()[0]
    cmd.MarkDelete()
    return result


def is_soft(fpga_cap, stream_block):
    """Return True iff the stream block is a soft one"""
    # First, check what kind of fpga the port has
    if fpga_cap == "HARD_ONLY":
        return False
    elif fpga_cap == "SOFT_ONLY":
        return True
    else:
        return not stream_block.Get("EnableHighSpeedResultAnalysis")


def get_stream_blocks(port, soft_only):
    """Return all (active) or (active + soft) stream blocks"""
    all_sb = port.GetObjects("streamblock")
    if soft_only:
        fpga_cap = get_fpga_capability(port)
        return [sb for sb in all_sb if (sb.Get("Active") and
                                        is_soft(fpga_cap, sb))]
    else:
        return [sb for sb in all_sb if sb.Get("Active")]


def get_stream_info(streamblock):
    """Call the StreamBlockGetInfo command, return {#streams, #flows, #mods}"""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("StreamBlockGetInfo")
    cmd.Set("streamblock", streamblock.GetObjectHandle())
    cmd.Execute()
    mod_count = len(streamblock.GetObjects("Modifier"))
    retval = {"StreamCount": cmd.Get("TotalStreamCount"),
              "FlowCount": cmd.Get("TotalFlowCount"),
              "ModifierCount": mod_count}
    cmd.MarkDelete()
    return retval


def get_port_rate_info(port, soft_only):
    generator = port.GetObject("Generator")
    gen_config = generator.GetObject("GeneratorConfig")

    sched_mode = gen_config.Get("SchedulingMode")

    sched_handler = {"PORT_BASED": get_port_based_rate_info,
                     "RATE_BASED": get_rate_based_rate_info,
                     "PRIORITY_BASED": get_priority_based_rate_info,
                     "MANUAL_BASED": get_manual_based_rate_info}

    return sched_handler[sched_mode](port, soft_only)


def get_port_based_rate_info(port, soft_only):
    generator = port.GetObject("Generator")
    gen_config = generator.GetObject("GeneratorConfig")
    if gen_config.Get("LoadMode") == "FIXED":
        sum_percent_rate = gen_config.Get("PercentageLoad")
        sum_bit_rate = gen_config.Get("L2Rate")
        sum_packet_rate = gen_config.Get("FpsLoad")
    else:
        sum_percent_rate = gen_config.Get("AvgPercentageLoad")
        sum_bit_rate = gen_config.Get("AvgL2Rate")
        sum_packet_rate = gen_config.Get("AvgFpsLoad")

    if sum_packet_rate:
        avg_packet_size = round(sum_bit_rate / 8.0 / sum_packet_rate, 2)
    else:
        # no packets, no size
        avg_packet_size = 0.0

    return {"FpsLoad": sum_packet_rate,
            "PercentLoad": sum_percent_rate,
            "AvgPacketSize": avg_packet_size}


def get_rate_based_rate_info(port, soft_only):
    stream_block_list = get_stream_blocks(port, soft_only)
    sum_percent_rate, sum_bit_rate, sum_packet_rate = (0, 0, 0)
    for stream_block in stream_block_list:
        sum_percent_rate += stream_block.Get("PercentageLoad")
        sum_bit_rate += stream_block.Get("l2Rate")
        sum_packet_rate += stream_block.Get("FpsLoad")

    if sum_packet_rate:
        avg_packet_size = round(sum_bit_rate / 8.0 / sum_packet_rate, 2)
    else:
        # no packets, no size
        avg_packet_size = 0.0

    return {"FpsLoad": sum_packet_rate,
            "PercentLoad": sum_percent_rate,
            "AvgPacketSize": avg_packet_size}


def get_priority_based_rate_info(port, soft_only):
    stream_block_list = get_stream_blocks(port, soft_only)
    sum_bit_rate, sum_packet_rate, sum_percent_rate = (0, 0, 0)
    for stream_block in stream_block_list:
        percent_rate = stream_block.Get("PercentageLoad")
        if sum_percent_rate + percent_rate < 100:
            sum_percent_rate += percent_rate
            sum_bit_rate += stream_block.Get("l2Rate")
            sum_packet_rate += stream_block.Get("FpsLoad")
        else:
            actual_percent_rate = 100.0 - sum_percent_rate
            sum_percent_rate = 100.0
            ratio = actual_percent_rate / percent_rate
            sum_bit_rate += ratio * stream_block.Get("l2Rate")
            sum_packet_rate += ratio * stream_block.Get("FpsLoad")
            break

    if sum_packet_rate:
        avg_packet_size = round(sum_bit_rate / 8.0 / sum_packet_rate, 2)
    else:
        # no packets, no size
        avg_packet_size = 0.0

    return {"FpsLoad": sum_packet_rate,
            "PercentLoad": sum_percent_rate,
            "AvgPacketSize": avg_packet_size}


def get_manual_based_rate_info(port):
    # TODO - implement. Requires walking the schedule and computing
    #        various gaps and rates and loops.
    raise NotImplementedError("Manual scheduling not supported by summarize")


def get_port_mem_info(port):
    """Retrieve memory usage information from the port."""
    il_usage = get_il_usage([port])[0]
    return {'MemUsed': float(il_usage['MemUsed']),
            'MemTotal': float(il_usage['MemTotal'])}


def store_info(info, log_path):
    """Log the traffic summary info by appending to a local file"""
    with open(log_path, "a") as log_file:
        log_file.write(json.dumps(info))
        log_file.write("\n")
