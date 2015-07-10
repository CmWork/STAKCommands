"""Preflight check utilities

Copyright (c) 2015 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

from spirent.core.utils.scriptable import AutoCommand

_CHECKERS = []


def reserve_all(port_map, locations):
    """Reserve all locations, return list of those that were previously not"""
    unreserved = port_map.get_unreserved(locations)
    port_map.reserve(unreserved)
    return unreserved


def check(port_map, locations):
    # reserve any unreserved ports
    to_release = reserve_all(port_map, locations)

    for checker in _CHECKERS:
        # execute check
        results = checker(port_map, locations)

        # store result in port map
        for result, location in zip(results, locations):
            port_map.memo(location).update(result)

    # release any previously-unreserved ports
    port_map.release(to_release)


def checker(func):
    """
    Decorator to add a checker to be called during preflight check.
    Doesn't actually modify the function itself at all.
    """
    _CHECKERS.append(func)
    return func


@checker
def execute(port_map, locations):
    """Execute the preflight test on the given locations."""
    with AutoCommand("GenericExecution") as cmd:
        ports = [port_map.get_physical_port(loc).GetObjectHandle()
                 for loc in locations]
        cmd.SetCollection("PortList", ports)
        cmd.Set("Cmd", "stream_bench | grep Copy | awk '{print $2}'; "
                       "cat /proc/meminfo | grep Mem | awk '{print $2}'")
        cmd.Execute()
        results = []
        for out in cmd.GetCollection("OutputList"):
            out_list = out.strip().split()
            if out_list:
                out_dict = {"preflight": float(out_list[0]),
                            "memtotal": int(out_list[1]),
                            "memfree": int(out_list[2])}
            else:
                # The port was unreserved, no results
                out_dict = {}
            results.append(out_dict)
    return results
