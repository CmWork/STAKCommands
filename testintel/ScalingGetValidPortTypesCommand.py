"""Returns valid port types (part numbers) for given resource requirementst"""
from StcIntPythonPL import (CHandleRegistry, PLLogger)
from collections import namedtuple
import traceback


# TODO: move into a separate file, retrieve values from system
PortType = namedtuple('PortType', ['part', 'mem', 'cores', 'mips'])

PORT_TYPES = [
    PortType("MX-10G-S2", 2048, 4, 600),
    PortType("MX-10G-S4", 1024, 4, 500),
    PortType("CM-1G-D4",  512, 1, 100),
]


def validate_filter(port_type_list):
    """Return an error if any of the port types don't exist."""
    diff_set = set(port_type_list) - set(port.part for port in PORT_TYPES)
    if diff_set:
        return "{} not among known port part numbers".format(diff_set)
    return ""


def validate(MinMemoryMb, MinCores, MinSpiMips, FilterPortTypeList):
    """Validate the command: validate filter"""
    result = validate_filter(FilterPortTypeList)
    if result:
        return result

    return ""


def find_matching_ports(mem, cores, mips, part_list):
    """Return a list of part numbers with the required attributes.

    part_list is used as a filter. If empty or None all matching part
    numbers will be returned.
    """
    if part_list:
        all_matching = find_matching_ports(mem, cores, mips, [])
        return (set(all_matching) & set(part_list))
    else:
        return (port.part for port in PORT_TYPES if (
                port.mem >= mem and port.cores >= cores and port.mips >= mips))


def run(MinMemoryMb, MinCores, MinSpiMips, FilterPortTypeList):
    """Run method - calculate outputs"""
    try:
        hnd_reg = CHandleRegistry.Instance()
        this_hnd = hnd_reg.Find(__commandHandle__)  # pragma: no flakes
        this_hnd.SetCollection("PortTypeList", list(find_matching_ports(
            MinMemoryMb, MinCores, MinSpiMips, FilterPortTypeList)))
    except:
        stack_trace = traceback.format_exc()
        get_logger().LogError("error: " + stack_trace)
        return False

    return True


def reset():
    """True means this command can be reset and re-run"""
    return True


def get_logger():
    """Get the test intel logger"""
    return PLLogger.GetLogger("testintel")
