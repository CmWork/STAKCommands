"""Unit test preflight"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(),
                             'STAKCommands', 'spirent', 'testintel'))
import preflight


class MockPhysicalPortMap(object):
    def __init__(self):
        self.reserve_loc = []
        self.release_loc = []
        self.unreserved_loc = []
        self.memo_data = {}

    def get_unreserved(self, locations):
        loc_set = set(locations)
        unreserved_set = set(self.unreserved_loc)
        return list(loc_set.intersection(unreserved_set))

    def reserve(self, locations):
        self.reserve_loc = locations

    def release(self, locations):
        self.release_loc = locations

    def memo(self, location):
        if location not in self.memo_data:
            self.memo_data[location] = {}
        return self.memo_data[location]


def test_reserve_all():
    port_map = MockPhysicalPortMap()
    port_map.unreserved_loc = ["foo"]
    assert (preflight.reserve_all(port_map, ["foo", "bar"]) ==
            port_map.unreserved_loc)
    assert port_map.reserve_loc == ["foo"]


def test_check(monkeypatch):
    executed_locations = []

    def mock_execute(port_map, locations):
        executed_locations.extend(locations)
        mock_result = {"preflight": 1000.0,
                       "memtotal": 500000,
                       "memfree": 400000}
        return [mock_result for loc in locations]

    monkeypatch.setattr(preflight, "_CHECKERS", [mock_execute])
    port_map = MockPhysicalPortMap()
    port_map.unreserved_loc = ["foo"]
    preflight.check(port_map, ["foo", "bar"])
    assert set(executed_locations) == {"foo", "bar"}
    assert port_map.reserve_loc == ["foo"]
    assert port_map.release_loc == ["foo"]
    assert "preflight" in port_map.memo("foo")
    assert port_map.memo("foo")["preflight"] == 1000
    assert port_map.memo("foo")["memtotal"] == 500000
    assert port_map.memo("foo")["memfree"] == 400000
    assert "preflight" in port_map.memo("bar")
    assert port_map.memo("bar")["preflight"] == 1000
    assert port_map.memo("bar")["memtotal"] == 500000
    assert port_map.memo("bar")["memfree"] == 400000
