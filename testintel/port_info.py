"""Port information utilities

Copyright (c) 2015 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

from StcIntPythonPL import (CHandleRegistry, CStcSystem)
from spirent.core.utils.scriptable import AutoCommand
from itertools import chain
import re


# Metric prefixes
PREFIXES = '_KMGTP'


class PhysicalPortMap(object):
    """Map of location to physical port."""
    def __init__(self):
        self.memo_data = {}
        self.tried_chassis = set()
        self.update_port_map()

    def update_port_map(self):
        """Refresh the map with all known ports"""
        pcm = CStcSystem.Instance().GetObject('PhysicalChassisManager')
        pc_list = pcm.GetObjects('PhysicalChassis')
        self.port_map = {}
        map(self.add_chassis, pc_list)

    def add_chassis(self, chassis):
        """Add a new chassis to the map"""
        tm_list = chassis.GetObjects('PhysicalTestModule')
        pg_iter = chain.from_iterable(tm.GetObjects('PhysicalPortGroup')
                                      for tm in tm_list)
        port_iter = chain.from_iterable(pg.GetObjects('PhysicalPort')
                                        for pg in pg_iter)
        self.port_map.update((self._canonize(port.Get('location')), port)
                             for port in port_iter)

    @staticmethod
    def _canonize(location):
        """Make location canonical (lower case with no whitespace), s/w //"""
        location = location.lower().strip()
        if location[0:2] != "//":
            if location[0:1] == "/":
                location = "/" + location
            else:
                location = "//" + location
        return location

    @classmethod
    def _get_chassis(cls, location):
        """Strip out chassis from location"""
        location = cls._canonize(location)
        return location.split('/')[2]

    def has_physical_port(self, location):
        """True if the location has a physical port"""
        location = self._canonize(location)
        has = location in self.port_map
        if has:
            return has
        return self.try_connect(location)

    def get_physical_port(self, location):
        """Return the location's physical port"""
        return self.port_map.get(self._canonize(location))

    def get_test_module(self, location):
        """Return the location's physical test module"""
        port = self.port_map.get(self._canonize(location))
        if not port:
            return None
        port_group = port.GetParent()
        test_module = port_group.GetParent()
        return test_module

    def get_max_speed(self, location):
        """Return the location's maximum supported speed in bps"""
        phys_port = self.get_physical_port(location)

        with AutoCommand("GetRcmCapability") as cmd:
            cmd.SetCollection("Port", [phys_port.GetObjectHandle()])
            cmd.Set("Service", "PortGroup")
            cmd.Set("CapabilityKey", "port/LAN/speed")
            cmd.Execute()
            speeds = cmd.GetCollection("Result")[0]
        return convert_supported_to_max(speeds)

    def try_connect(self, location):
        """Try to connect to the chassis, return True if the port exists"""
        chassis = self._get_chassis(location)
        if chassis in self.tried_chassis:
            # Already tried connecting
            return False

        with AutoCommand("ConnectToChassis") as cmd:
            cmd.SetCollection("AddrList", [chassis])
            self.tried_chassis.add(chassis)
            try:
                cmd.Execute()
            except:
                # failed to connect - we don't care why
                return False
            new_chassis_hdl = cmd.GetCollection("OutputChassisList")[0]
            hdl_reg = CHandleRegistry.Instance()
            new_chassis = hdl_reg.Find(new_chassis_hdl)
            self.add_chassis(new_chassis)
        return self.has_physical_port(location)

    def has_good_version(self, location):
        """
        Returns (True, "") if the port's version is compatible.
        Otherwise returns (False, message) with message explaining the version
        issue.
        """
        if not self.has_physical_port(location):
            raise ValueError("unable to connect to port at %s" % location)

        test_module = self.get_test_module(location)
        valid = test_module.Get("IsFirmwareVersionValid")
        return (valid,
                "" if valid else test_module.Get("FirmwareVersionStatus"))

    def has_only_soft_fpga(self, location):
        """True if the given port has no hardware fpga."""
        if not self.has_physical_port(location):
            raise ValueError("unable to connect to port at %s" % location)

        test_module = self.get_test_module(location)
        family = test_module.Get("ProductFamily")
        return family in ["STCA", "VTC"]

    def reserve(self, locations):
        """Reserve the given ports."""
        with AutoCommand("ReservePort") as cmd:
            cmd.SetCollection("Location", locations)
            try:
                cmd.Execute()
            except:
                # one or more failed to reserve, continue
                # failure will be caught by preflight returning ""
                pass

    def release(self, locations):
        """Release the given ports."""
        with AutoCommand("ReleasePort") as cmd:
            cmd.SetCollection("Location", locations)
            cmd.Execute()

    @classmethod
    def is_reserved(cls, phys_port):
        """True if the given physical port object is reserved."""
        phys_port_group = phys_port.GetParent()
        return phys_port_group.Get("ReservedByUser")

    def get_unreserved(self, locations):
        """Retrieve the subset of locations that is unreserved."""
        unreserved = []
        for location in locations:
            phys_port = self.get_physical_port(location)
            if not phys_port:
                # silently skip unknown ports
                continue
            if not self.is_reserved(phys_port):
                unreserved.append(location)
        return unreserved

    def memo(self, location):
        """Return the memo (dict for noting stuff) for the given location."""
        location = self._canonize(location)
        if location not in self.memo_data:
            self.memo_data[location] = {}
        return self.memo_data[location]


def convert_supported_to_max(speeds):
    """
    Convert rcm port/LAN/speed enum string to max speed value.
    GetRcmCapability returns "name value name value...".
    """
    speed_list = speeds.split()
    max_speed = 0
    for speed in speed_list[::2]:
        speed = convert_speed_to_val(speed)
        max_speed = speed if speed > max_speed else max_speed
    return max_speed


def convert_speed_to_val(speed):
    """Convert speed in the form e.g. 10G into a number."""
    m = re.search('([0-9]+)([A-Z]+)\Z', speed)
    if not m:
        raise ValueError("Improper speed of %s found" % speed)
    num, prefix = m.groups()
    if prefix not in PREFIXES[1:]:
        raise ValueError("Unknown speed prefix in %s" % speed)
    return int(num) * 1000**PREFIXES.find(prefix)


def convert_val_to_speed(val):
    """Convert numerical bps to string representation, e.g. 10 Gbps"""
    pref_index = 0
    scaled = val
    while scaled >= 1000.0:
        scaled = scaled / 1000.0
        pref_index += 1
        if pref_index > len(PREFIXES) - 1:
            raise ValueError("Unprintable speed: %g" % val)
    if pref_index == 0:
        return "%d bps" % val
    return "%g %sbps" % (scaled, PREFIXES[pref_index])
