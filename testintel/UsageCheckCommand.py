"""Gathers resource usage information across all online ports and stores it"""
from StcIntPythonPL import (CScriptableCreator, CStcSystem, PLLogger,
                            RelationType)
import json
import traceback


def validate(TestPoint):
    """Validate the command: make sure TestPoint is not empty or missing
    and that all online ports have distinct names."""
    if not TestPoint:
        return "ERROR: TestPoint is missing"
    try:
        project = CStcSystem.Instance().GetObject('project')
        port_list = get_online_ports(project)
        name_list = [strip_location(port.Get("Name")) for port in port_list]
        if not are_names_valid(name_list):
            return "ERROR: Online port names must be distinct and meaningful"

    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return "ERROR: " + traceback.format_exc(1)

    return ""


def run(TestPoint):
    """Run method - get all online ports, collect bll and il info, store it"""
    try:
        project = CStcSystem.Instance().GetObject('project')
        usagelog = CStcSystem.Instance().GetLogOutputPath() + 'usage.log'
        port_list = get_online_ports(project)

        for (port, bll_usage, il_module, il_version, il_usage) in zip(
                port_list, get_bll_usage(port_list),
                get_il_module(port_list), get_il_version(port_list),
                get_il_usage(port_list)):
            result = {}
            result['Port'] = strip_location(port.Get("Name"))
            result['IlVersion'] = il_version
            result['Module'] = il_module
            result['TestPoint'] = TestPoint
            result.update(bll_usage)
            result.update(il_usage)
            store_usage(result, usagelog)

    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return False

    return True


def reset():
    """True means this command can be reset and re-run"""
    return True


def get_logger():
    """Get the UsageCheckCommand logger"""
    return PLLogger.GetLogger("UsageCheckCommand")


def get_online_ports(project):
    """Return a list of all the online ports"""
    port_list = project.GetObjects("Port")
    online_list = [port for port in port_list if port.Get("Online")]
    return online_list


def gen_physical_port_pairs(port_list):
    """Generator for all (port, phys_port) for the given logical ports"""
    for port in port_list:
        phys_port = port.GetObject('PhysicalPort',
                                   RelationType.ReverseDir("PhysicalLogical"))
        if phys_port:
            yield (port, phys_port)


def strip_location(name):
    """Remove location from port names. i.e. Foo //3/1/2 -> Foo"""
    name_list = name.split("//")
    if len(name_list) == 1:
        return name.strip()
    else:
        return "//".join(name_list[:len(name_list) - 1]).strip()


def are_names_valid(name_list):
    """True if all names are distinct and meaningful (i.e. not "Port")"""
    name_set = set(name_list)
    return "Port" not in name_set and len(name_set) == len(name_list)


def get_bll_usage(port_list):
    """Return UsageRegistryGet results formatted as a list of dicts"""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("UsageRegistryGet")
    output_list = []

    for port in port_list:
        cmd.Set("Port", port.GetObjectHandle())
        cmd.Execute()
        names = cmd.GetCollection("NameList")
        values = cmd.GetCollection("ValueList")
        output_list.append(dict(zip(names, values)))
        cmd.Reset()
    cmd.MarkDelete()
    return output_list


def get_cpu_perc_from_cpuload(output):
    """
    Get cpu usage (non-idle) from output of cpuload.
    Input looks like:
        "cpu user=890 nice=0 system=20 idle=70 iowait=0 irq=10 softirq=10"
    """
    stat_list = output.split()
    stat_dict = dict((value.split('=', 1)) for value in stat_list[1:])
    return sum(int(stat) for name, stat in stat_dict.iteritems()
               if name != 'idle') / 10


def get_cpu_ticks_from_cpuload(output_list):
    """Get cpu usage (non-idle) across cores from output of cpuload 0, total"""
    result = []
    total = 0
    for output in output_list:
        stat_list = output.split()
        stat_dict = dict((value.split('=', 1)) for value in stat_list[1:])
        if total == 0:
            total = sum(int(stat) for stat in stat_dict.itervalues())
        nonidle = sum(int(stat) for name, stat in stat_dict.iteritems()
                      if name != 'idle')
        result.append(nonidle)
    return result, total


def format_il_usage(output_list):
    """Takes list with output of cmds below and formats it into a dict"""
    result = []
    for output in output_list:
        lines = output.strip().split("\n")
        info = {}
        info['MemTotal'] = int(lines[0].split()[1])
        mem_free = int(lines[1].split()[1])
        info['MemUsed'] = info['MemTotal'] - mem_free
        info['LoadAvg1Min'] = float(lines[2].split()[0])
        cpu_tick_list, cpu_total = get_cpu_ticks_from_cpuload(lines[3:-1])
        info['CpuUsed'] = cpu_tick_list[0]
        for i, cpu_tick in enumerate(cpu_tick_list[1:]):
            info['CpuUsed'+str(i)] = cpu_tick
        info['CpuTotal'] = cpu_total
        info['CpuPercent'] = get_cpu_perc_from_cpuload(lines[-1])
        result.append(info)
    return result


def map_ports_to_portgroups(port_list):
    """Return a map of port group handle -> port (the last port if multiple)"""
    pgh_to_port = {}
    for port, phys_port in gen_physical_port_pairs(port_list):
        pgh_to_port[phys_port.GetParent().GetObjectHandle()] = port
    return pgh_to_port


def expand_per_port(per_pg_input_list, port_list, pgh_to_port):
    """Convert the per-port-group list into a per-port list by duping"""
    output_list = []
    pgh_to_output = dict(zip(pgh_to_port.keys(), per_pg_input_list))
    for port, phys_port in gen_physical_port_pairs(port_list):
        output = pgh_to_output[phys_port.GetParent().GetObjectHandle()]
        output_list.append(output)
    return output_list


def create_il_usage_command(port_list):
    """Create GenericExecution with proper command and port list"""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("GenericExecution")
    cmd.Set("Cmd",
            "cat /proc/meminfo | grep Mem; cat /proc/loadavg; "
            "cpu-load 0; cpu-load | head -n 1")
    cmd.SetCollection("PortList",
                      [port.GetObjectHandle() for port in port_list])
    return cmd


def get_il_usage(port_list):
    """Uses GenericExecution to check memory usage and CPU load"""
    pgh_to_port = map_ports_to_portgroups(port_list)
    sparse_port_list = pgh_to_port.values()
    cmd = create_il_usage_command(sparse_port_list)
    cmd.Execute()
    pg_output_list = format_il_usage(cmd.GetCollection("OutputList"))
    output_list = expand_per_port(pg_output_list, port_list, pgh_to_port)
    cmd.MarkDelete()
    return output_list


def get_tm_info(port_list, param):
    """Return the given physical test module property for each logical port"""
    output_list = []
    for port, phys_port in gen_physical_port_pairs(port_list):
        phys_tm = phys_port.GetParent().GetParent()
        output_list.append(phys_tm.Get(param))
    return output_list


def get_il_version(port_list):
    """Return a list of the test module version running on each port"""
    return get_tm_info(port_list, "FirmwareVersion")


def get_il_module(port_list):
    """Return a list of the test module model of each port"""
    return get_tm_info(port_list, "Model")


def store_usage(usage, log_path):
    """Log the usage information and append to a local file"""
    with open(log_path, "a") as log_file:
        log_file.write(json.dumps(usage))
        log_file.write("\n")
