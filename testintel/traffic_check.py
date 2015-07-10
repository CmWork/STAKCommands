"""Traffic rule checking

Copyright (c) 2014-2015 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

import port_info
from traffic_rules import (PARAMS, SAFETY_FACTOR, BASE_PREFLIGHT)


class Confidence(object):
    def __init__(self, percent=100.0, reason=""):
        self.percent = percent
        self.reason = reason

    def update(self, percent, reason):
        """
        Update the percent by multiplying, the reason by appending.
        Return self so we can call this and return in one line.
        """
        self.percent *= percent / 100.0
        if self.reason:
            self.reason += " " + reason
        else:
            self.reason = reason
        return self


def calc_max_fps(StreamCount, AvgPacketSize):
    """Calculate fps based on regression data"""
    params = PARAMS['rate']
    return (params[0] + params[1] * StreamCount + params[2] * AvgPacketSize)


def calc_mem_used(StreamCount, AvgPacketSize):
    """Calculate mem used by traffic based on regression data"""
    params = PARAMS['memory']
    return (params[0] + params[1] * StreamCount + params[2] * AvgPacketSize)


def calc_speed(Fps, AvgPacketSize):
    """
    Calculate L1 bit rate with a given fps and packet size.
    Note that 'packet' size is number of bytes in the L2 (Ethernet) frame.
    Speed returned is L1 bps assuming ethernet with 20 bytes of preamble/fcs.
    """
    frame_size = AvgPacketSize + 20
    return frame_size * 8 * Fps


def get_soft_locations(port_map, locations):
    return [loc for loc in locations if
            port_map.has_physical_port(loc) and
            port_map.has_good_version(loc)[0] and
            port_map.has_only_soft_fpga(loc)]


def get_traffic_info(profile):
    """Return (fps, streamCount, packetSize) for the given profile"""
    fps = profile.get('avgFramesPerSecond', None)
    streamCount = profile.get('streamCount', None)
    packetSize = profile.get('avgPacketSize', None)
    return (fps, streamCount, packetSize)


def has_traffic(profile):
    """True if the given profile has traffic configured."""
    return all(get_traffic_info(profile))


def check_profile(profile, port_map, location, confidence):
    """If the given profile contains traffic features, check them."""
    if not port_map.has_physical_port(location):
        return confidence.update(0, "Could not connect to port.")

    if not port_map.has_good_version(location)[0]:
        return confidence.update(0, port_map.has_good_version(location)[1])

    if not port_map.has_only_soft_fpga(location):
        # Physical ports should always run fine
        return confidence

    fps, streamCount, packetSize = get_traffic_info(profile)
    if all((fps, streamCount, packetSize)):
        if not is_preflight_valid(port_map, location):
            return confidence.update(0, "Port could not be reserved "
                                     "for preflight test.")

        max_speed = port_map.get_max_speed(location)
        confidence = check_max_speed(fps, packetSize, max_speed, confidence)

        baseline_factor = calc_baseline_factor(port_map, location)
        confidence = check_rate(fps, streamCount, packetSize, baseline_factor,
                                confidence)

        total_mem = get_total_mem(port_map, location)
        confidence = check_mem(total_mem, streamCount, packetSize, confidence)
    return confidence


def check_max_speed(Fps, AvgPacketSize, max_speed, confidence=None):
    """
    Check that the average rate does not exceed the maximum speed.
    Returns a conf. of 100.0 (avg <= max) or 0.0 (avg > max)
    Note there is no scaling and we don't compare the expected
    maximum, just the expected average.
    """
    if confidence is None:
        confidence = Confidence()
    avg_speed = calc_speed(Fps, AvgPacketSize)
    if avg_speed > max_speed:
        speed_str = port_info.convert_val_to_speed(max_speed)
        return confidence.update(0, "Configured packet rate is greater than "
                                    "the maximum speed (%s) supported by the "
                                    "port." % speed_str)
    return confidence


def check_rate(Fps, StreamCount, AvgPacketSize, baseline_factor,
               confidence=None):
    """
    Check that the Fps is valid given the StreamCount and AvgPacketSize.
    Returns a number from 100.0 (should def. work) to 0.0 (likely won't work).
    """
    if confidence is None:
        confidence = Confidence()

    max_fps = baseline_factor * calc_max_fps(StreamCount, AvgPacketSize)
    if Fps <= max_fps * SAFETY_FACTOR:
        # should be fine, return confidence unchanged
        return confidence
    elif Fps > max_fps:
        # too much traffic, return no confidence
        advice = check_rate_advice(Fps, max_fps)
        return confidence.update(0, "Internal packet loss is predicted at the "
                                    "configured frame rate, based on the "
                                    "stream count and average packet size. "
                                    + advice)
    else:
        # in the middle, interpolate
        fps_range = max_fps * (1 - SAFETY_FACTOR)
        fps_diff = max_fps - Fps
        confidence_factor = float(fps_diff) / fps_range
        return confidence.update(confidence_factor * 100,
                                 "Internal packet loss may occur at the "
                                 "configured frame rate.")


def check_rate_advice(Fps, max_fps):
    """
    Generate advice based on the requested Fps and max predicted fps.
    """
    if max_fps <= 1:
        return ("The stream count and/or average packet size must be lowered "
                "in order to support any frame rate without predicted loss.")

    factor = float(Fps) / max_fps
    if factor >= 1.5:
        return ("The frame rate of %d is approximately %.2g times too large."
                % (Fps, factor))
    else:
        percent = (factor - 1) * 100
        if int(percent) == 0:
            percent = 1
        return ("The frame rate of %d is approximately %d%% too large."
                % (Fps, percent + 0.5))


def check_mem(total_mem, StreamCount, AvgPacketSize, confidence=None):
    """
    Check that the total memory is enough for the given StreamCount, AvgPktSz.
    Returns a number from 100.0 (should def. work) to 0.0 (likely won't work).
    """
    if confidence is None:
        confidence = Confidence()

    mem_required = calc_mem_used(StreamCount, AvgPacketSize)
    if mem_required <= total_mem * SAFETY_FACTOR:
        # should be fine, return confidence unchanged
        return confidence
    elif mem_required > total_mem:
        # not enough mem, return no confidence
        advice = check_mem_advice(mem_required, total_mem)
        return confidence.update(0, "The port will likely run out of "
                                 "memory. " + advice)
    else:
        # in the middle, interpolate
        mem_range = total_mem * (1 - SAFETY_FACTOR)
        mem_diff = total_mem - mem_required
        confidence_factor = float(mem_diff) / mem_range
        return confidence.update(confidence_factor * 100,
                                 "The port will be low on memory.")


def check_mem_advice(mem_required, total_mem):
    """
    Generate advice based on the required and total memory.
    """
    if not total_mem:
        # Shouldn't happen: prevent divide by zero in unit test
        return "The total memory is invalid (0 bytes)."
    factor = float(mem_required) / total_mem
    if factor >= 1.5:
        return ("The total memory of %g Mbytes should be approximately "
                "%.2g times larger." % (total_mem / 1024, factor))
    else:
        percent = (factor - 1) * 100
        if int(percent) == 0:
            percent = 1
        return ("The total memory of %g Mbytes should be approximately "
                "%d%% larger." % (total_mem / 1024, percent + 0.5))


def calc_baseline_factor(port_map, location):
    """
    Return the baseline factor for the given location.
    This is calculated by comparing the preflight value just returned
    with the one stored locally (from the ports used to calculate the
    params above). If the given port is more powerful than the base,
    we do nothing (because we can't be sure if the extra power actually
    helps). If the given port is less powerful than the base, we scale down.
    """
    loc_preflight = port_map.memo(location)["preflight"]
    if loc_preflight >= BASE_PREFLIGHT:
        return 1.0
    else:
        return float(loc_preflight) / BASE_PREFLIGHT


def get_total_mem(port_map, location):
    """
    Return the total memory for the given location.
    Retrieved during the preflight test and stored in the port_map.
    """
    return port_map.memo(location)["memtotal"]


def is_preflight_valid(port_map, location):
    """
    Return whether the preflight test passed or failed (or was never run).
    """
    memo = port_map.memo(location)
    return ("preflight" in memo and "memtotal" in memo)
