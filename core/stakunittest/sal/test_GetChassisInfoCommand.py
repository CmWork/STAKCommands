from mock import patch, MagicMock
from StcIntPythonPL import UnitTestManager
utm = UnitTestManager.Instance()
utm.Init('base core')
from spirent.core.GetChassisInfoCommand import *
from StcPython import StcPython
stc = StcPython()


def test_validate():
    assert validate('', False) == ''


@patch('spirent.core.GetChassisInfoCommand._is_connected', MagicMock(return_value=True))
def test_create_info_dict():
    addr = '10.1.1.9'
    phy_man = stc.get('system1', 'children-physicalchassismanager')
    phy_chassis = stc.create('physicalchassis', under=phy_man, hostname=addr)
    phy_test_mod = stc.create('physicaltestmodule', under=phy_chassis)
    phy_port_group = stc.create('physicalportgroup', under=phy_test_mod)
    stc.create('physicalport', under=phy_port_group)
    stc.create('physicaltestmodule', under=phy_chassis)
    info = create_info_dict(addr)
    assert info != {}

    chassis_info = info.get('physicalchassis', '')
    assert chassis_info != {}
    assert chassis_info.get('Hostname') == addr
    # It's the same since we are giving the IP address.
    assert chassis_info.get('IpAddr') == addr

    phy_test_mods = chassis_info.get('physicaltestmodules', [])
    assert len(phy_test_mods) == 2

    phy_port_group = phy_test_mods[0].get('physicalportgroups', [])
    assert len(phy_port_group) == 1

    phy_port = phy_port_group[0].get('physicalports', [])
    assert len(phy_port) == 1


def test_run():
    assert run('10.1.1.1', False)


def test_create_info_dict_returns_empty_dict_when_no_connection():
    info = create_info_dict('xxx')
    assert info == {}

    phy_man = stc.get('system1', 'children-physicalchassismanager')
    addr = '10.1.1.10'
    stc.create('physicalchassis', under=phy_man, hostname=addr)
    info = create_info_dict(addr)
    assert info == {}


def test_reset():
    assert reset()
