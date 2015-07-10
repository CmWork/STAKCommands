from ..utils import hardware_util


def test_split_port_location():
    csp = hardware_util.split_port_location("//1.0.0.1/1/1")
    assert csp == ("1.0.0.1", "1", "1")
    csp = hardware_util.split_port_location("//some-domain_name.com/1/1")
    assert csp == ("some-domain_name.com", "1", "1")
