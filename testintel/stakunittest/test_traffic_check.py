"""Unit test traffic_check"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(),
                             'STAKCommands', 'spirent', 'testintel'))
from traffic_check import (calc_baseline_factor, calc_max_fps, calc_mem_used,
                           calc_speed, check_max_speed, check_mem,
                           check_mem_advice, check_profile, check_rate,
                           check_rate_advice, Confidence, get_total_mem,
                           get_traffic_info, has_traffic, is_preflight_valid,
                           BASE_PREFLIGHT, SAFETY_FACTOR)


def test_calc_max_fps():
    # should be able to send at least 100 fps at 1024 bytes
    assert calc_max_fps(1, 1024) > 100
    # should be able to send more frames at 64 than 1024
    assert calc_max_fps(1, 64) > calc_max_fps(1, 1024)
    # should be able to send more frames with 1 stream than 100 streams
    assert calc_max_fps(1, 1024) > calc_max_fps(1000, 1024)


def test_calc_mem_used():
    # should be able to send at least 100 fps at 1024 bytes
    assert calc_mem_used(1, 1024) < 512000
    # should use less memory at 64 than 1024
    assert calc_mem_used(1, 64) < calc_mem_used(1, 1024)
    # should use less memory with 1 stream than 100 streams
    assert calc_mem_used(1, 1024) < calc_mem_used(1000, 1024)


def test_calc_speed():
    # 128 bytes at 1 fps is 1184 bps
    assert calc_speed(1, 128) == 1184
    # adding a byte adds 8 bits
    assert calc_speed(1, 129) == 8 + calc_speed(1, 128)
    # multiplying fps multiplies the result
    assert calc_speed(1000, 128) == 1000 * calc_speed(1, 128)


def test_check_max_speed():
    # starting with 0 confidence should always return 0 confidence
    assert check_max_speed(10000, 64, 1000**3, Confidence(0.0)).percent == 0.0

    # no fps should have no effect on confidence
    assert check_max_speed(0, 64, 1000**2,  Confidence(99.0)).percent == 99.0
    assert check_max_speed(0, 1000, 1000**2, Confidence(62.0)).percent == 62.0

    # oversubscribed means no confidence
    assert check_max_speed(1000, 1024, calc_speed(1000, 1024) - 1,
                           Confidence(100.0)).percent == 0.0

    # undersubscribed means no change to confidence
    assert check_max_speed(1000, 1024, calc_speed(1000, 1024) * 2,
                           Confidence(75.0)).percent == 75.0


def test_check_max_speed_reasons():
    # starting with a reason should return that reason (maybe with additions)
    assert "foo" in check_max_speed(1, 64, 1000**3,
                                    Confidence(reason="foo")).reason
    assert "foo" in check_max_speed(1000, 100, calc_speed(1000, 100)/2,
                                    Confidence(reason="foo")).reason

    # no fps should have no effect on reason
    assert check_max_speed(0, 64, 1000**2,
                           Confidence(99.0, "foo")).reason == "foo"
    assert check_max_speed(0, 1000, 1000**2,
                           Confidence(62.0, "foo")).reason == "foo"

    # oversubscribed means no confidence and a reason
    reason = check_max_speed(1000, 1024, calc_speed(1000, 1024) - 1,
                             Confidence()).reason

    assert "rate" in reason
    assert "max" in reason

    # undersubscribed means no effect on reason
    assert check_max_speed(1000, 1024, calc_speed(1000, 1024) * 2,
                           Confidence(75.0, "foo")).reason == "foo"


def test_check_rate():
    # starting with 0 confidence should always return 0 confidence
    assert check_rate(10, 1, 64, 1.0, Confidence(0.0)).percent == 0.0

    # no fps should have no effect on confidence
    assert check_rate(0, 1, 64, 1.0, Confidence(99.0)).percent == 99.0
    assert check_rate(0, 1000, 8192, 1.0, Confidence(62.0)).percent == 62.0

    # oversubscribed means no confidence
    assert check_rate(calc_max_fps(1, 1024) + 1, 1, 1024, 1.0,
                      Confidence(100.0)).percent == 0.0

    # undersubscribed means no change to confidence
    assert check_rate(calc_max_fps(1, 1024)/2, 1, 1024, 1.0,
                      Confidence(75.0)).percent == 75.0

    # in the middle means scaling confidence
    scaled_confidence = check_rate(calc_max_fps(1, 1024) *
                                   (1 + SAFETY_FACTOR) / 2,
                                   1, 1024, 1.0, Confidence(100.0)).percent
    assert round(scaled_confidence, 2) == 50.0

    # 50% baseline factor means less confidence
    assert check_rate(calc_max_fps(1, 1024), 1, 1024, 0.5,
                      Confidence(100.0)).percent < 100.0

    # 50% baseline factor means 50% less performance
    assert check_rate(SAFETY_FACTOR * calc_max_fps(1, 1024) / 2, 1, 1024,
                      0.5, Confidence(100.0)).percent == 100.0

    # 200% baseline factor means double performance (but it will never be 2)
    assert check_rate(SAFETY_FACTOR * calc_max_fps(1, 1024) * 2, 1, 1024,
                      2, Confidence(100.0)).percent == 100.0


def test_check_rate_reasons():
    # starting with a reason should return that reason (maybe with additions)
    assert "foo" in check_rate(10, 1, 64, 1.0, Confidence(reason="foo")).reason
    assert "foo" in check_rate(10, 1, 64, 1.0, Confidence(reason="foo")).reason
    assert "foo" in check_rate(calc_max_fps(1, 1024) + 1, 1, 1024, 1.0,
                               Confidence(reason="foo")).reason

    # no fps should have no effect on reason
    assert check_rate(0, 1, 64, 1.0, Confidence(99.0, "foo")).reason == "foo"
    assert check_rate(0, 1000, 8192, 1.0,
                      Confidence(62.0, "foo")).reason == "foo"

    # oversubscribed means no confidence and a reason
    reason = check_rate(calc_max_fps(1, 1024) + 1, 1, 1024, 1.0,
                        Confidence()).reason
    assert "rate" in reason
    assert "loss" in reason or "lost" in reason

    # undersubscribed means no effect on reason
    assert check_rate(calc_max_fps(1, 1024)/2, 1, 1024, 1.0,
                      Confidence(75.0, "foo")).reason == "foo"

    # in the middle means a reason
    scaled_reason = check_rate(calc_max_fps(1, 1024) *
                               (1 + SAFETY_FACTOR) / 2,
                               1, 1024, 1.0, Confidence()).reason
    assert "rate" in scaled_reason
    assert "loss" in scaled_reason or "lost" in scaled_reason


def test_check_rate_advice():
    assert "2 times too large" in check_rate_advice(1000, 500)
    assert "20 times too large" in check_rate_advice(10000, 500)
    assert "2.5 times too large" in check_rate_advice(1000, 400)
    assert "10% too large" in check_rate_advice(1100, 1000)
    assert "5% too large" in check_rate_advice(1049, 1000)
    assert "stream count" in check_rate_advice(1049, 0)
    assert "packet size" in check_rate_advice(1049, 0)
    assert "1% too large" in check_rate_advice(1001, 1000)


def test_check_mem():
    # starting with 0 confidence should always return 0 confidence
    assert check_mem(100000, 1, 64, Confidence(0.0)).percent == 0.0

    # huge mem should have no effect on confidence
    assert check_mem(1e10, 1, 64, Confidence(99.0)).percent == 99.0
    assert check_mem(1e10, 1000, 8192, Confidence(62.0)).percent == 62.0

    # oversubscribed means no confidence
    assert check_mem(calc_mem_used(1, 1024) - 1, 1, 1024,
                     Confidence(100.0)).percent == 0.0

    # undersubscribed means no change to confidence
    assert check_mem(calc_mem_used(1, 1024)*2, 1, 1024,
                     Confidence(75.0)).percent == 75.0

    # in the middle means scaling confidence
    scaled_confidence = check_mem(calc_mem_used(1, 1024) /
                                  ((1 + SAFETY_FACTOR) / 2),
                                  1, 1024, Confidence(100.0)).percent
    assert round(scaled_confidence, 2) == 50.0


def test_check_mem_reasons():
    # starting with a reason should return that reason (maybe with additions)
    assert "foo" in check_mem(5000000, 1, 64, Confidence(reason="foo")).reason
    assert "foo" in check_mem(0, 1, 64, Confidence(reason="foo")).reason

    # huge mem should have no effect on reason
    assert check_mem(1e10, 1, 64, Confidence(99.0, "foo")).reason == "foo"
    assert check_mem(1e10, 1000, 8192, Confidence(62.0, "foo")).reason == "foo"

    # oversubscribed means no confidence and a reason
    reason = check_mem(calc_mem_used(1, 1024) - 1, 1, 1024,
                       Confidence()).reason
    assert "memory" in reason

    # undersubscribed means no effect on reason
    assert check_mem(calc_mem_used(1, 1024)*2, 1, 1024,
                     Confidence(75.0, "foo")).reason == "foo"

    # in the middle means a reason
    scaled_reason = check_mem(calc_mem_used(1, 1024) /
                              ((1 + SAFETY_FACTOR) / 2),
                              1, 1024, Confidence()).reason
    assert "memory" in scaled_reason


def test_check_mem_advice():
    assert "2 times larger" in check_mem_advice(1000, 500)
    assert "20 times larger" in check_mem_advice(10000, 500)
    assert "2.5 times larger" in check_mem_advice(1000, 400)
    assert "10% larger" in check_mem_advice(1100, 1000)
    assert "5% larger" in check_mem_advice(1049, 1000)
    assert "1% larger" in check_mem_advice(1001, 1000)


class MockPhysicalPortMap(object):
    def __init__(self):
        self.memo_data = {}
        self.mock_has_physical_port = True

    def has_physical_port(self, location):
        return self.mock_has_physical_port

    def has_only_soft_fpga(self, location):
        return True

    def has_good_version(self, location):
        return (True, "")

    def memo(self, location):
        if location not in self.memo_data:
            self.memo_data[location] = {}
        return self.memo_data[location]


def test_check_profile():
    # just do one check to make sure the plumbing is working
    # test_check_* functions above are more thorough and direct
    port_map = MockPhysicalPortMap()
    profile = {"streamCount": 1, "avgPacketSize": 1024,
               "avgFramesPerSecond": calc_max_fps(1, 1024)}
    confidence = check_profile(profile, port_map, "1.2.3.4/1/1", Confidence())
    assert confidence.percent == 0.0
    assert "reserved" in confidence.reason


def test_check_profile_unconnected():
    port_map = MockPhysicalPortMap()
    port_map.mock_has_physical_port = False
    profile = {"streamCount": 1, "avgPacketSize": 64, "avgFramesPerSecond": 1}
    confidence = check_profile(profile, port_map, "1.2.3.4/1/1",
                               Confidence(100.0, "old reason"))
    assert confidence.percent == 0.0
    assert "old reason" in confidence.reason
    assert "connect" in confidence.reason


def test_get_traffic_info():
    profile = {"avgFramesPerSecond": 1, "streamCount": 2, "avgPacketSize": 3,
               "other": 4}
    assert get_traffic_info(profile) == (1, 2, 3)

    profile.pop("avgFramesPerSecond")
    assert get_traffic_info(profile) == (None, 2, 3)

    profile.pop("avgPacketSize")
    assert get_traffic_info(profile) == (None, 2, None)

    profile.pop("streamCount")
    assert get_traffic_info(profile) == (None, None, None)


def test_has_traffic():
    profile = {"avgFramesPerSecond": 1, "streamCount": 2, "avgPacketSize": 3,
               "other": 4}
    assert has_traffic(profile)

    profile.pop("streamCount")
    assert not has_traffic(profile)

    profile["streamCount"] = 2
    profile.pop("avgFramesPerSecond")
    assert not has_traffic(profile)

    profile["avgFramesPerSecond"] = 1
    profile.pop("avgPacketSize")
    assert not has_traffic(profile)


def test_calc_baseline_factor():
    port_map = MockPhysicalPortMap()
    location = "here"
    port_map.memo(location)["preflight"] = BASE_PREFLIGHT
    assert calc_baseline_factor(port_map, location) == 1.0
    # > BASE should return 1.0 as well
    port_map.memo(location)["preflight"] = BASE_PREFLIGHT * 2
    assert calc_baseline_factor(port_map, location) == 1.0
    # < BASE should be scaled linearly
    port_map.memo(location)["preflight"] = BASE_PREFLIGHT / 2
    assert calc_baseline_factor(port_map, location) == 0.5


def test_get_total_mem():
    port_map = MockPhysicalPortMap()
    location = "here"
    port_map.memo(location)["memtotal"] = 1000000
    assert get_total_mem(port_map, location) == 1000000


def test_is_preflight_valid():
    port_map = MockPhysicalPortMap()
    location = "here"
    assert not is_preflight_valid(port_map, location)
    port_map.memo(location)["memtotal"] = 1000000
    assert not is_preflight_valid(port_map, location)
    port_map.memo(location)["preflight"] = 6000
    assert is_preflight_valid(port_map, location)


def test_confidence():
    conf = Confidence()
    assert conf.percent == 100
    assert conf.reason == ""
    assert conf is conf.update(50, "foo")
    assert conf.percent == 50
    assert conf.reason == "foo"
    assert conf is conf.update(50, "bar")
    assert conf.percent == 25
    assert conf.reason == "foo bar"
    assert conf is conf.update(0, "boo")
    assert conf.percent == 0
    assert conf.reason == "foo bar boo"
