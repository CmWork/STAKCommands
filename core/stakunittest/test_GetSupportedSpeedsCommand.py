import pytest
import sqlite3
from StcIntPythonPL import CStcSystem, CScriptableCreator
from spirent.core.GetSupportedSpeedsCommand import *
from spirent.core.utils.scriptable import AutoCommand


def test_validate(stc, resource_cleanup):
    assert validate(9999, 'LAN') == 'PhyTestModule is required'
    assert validate(CStcSystem.Instance().GetObjectHandle(), 'LAN') == 'Invalid PhyTestModule'

    phy_test_module = _create_test_module()
    assert validate(phy_test_module.GetObjectHandle(), 'LAN') == ''


def test_changeling(stc, resource_cleanup):
    phy_test_module = _create_test_module('DX2-100G-P4')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 3
        assert speeds[0] == '10G:8'
        assert speeds[1] == '40G:2'
        assert speeds[2] == '100G:1'


def test_non_changeling(stc, resource_cleanup):
    phy_test_module = _create_test_module('VM-1G-V1-1P')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 1
        assert speeds[0] == '1G:1'


def test_non_changeling_multi_speed(stc, resource_cleanup):
    phy_test_module = _create_test_module('CM-1G-D12')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 3
        assert speeds == ['10M:1', '100M:1', '1G:1']


def test_single_speed_changeling(stc, resource_cleanup):
    phy_test_module = _create_test_module('DX2-100GO-P4')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 1
        assert speeds[0] == '100G:1'


def test_nic_45_46(stc, resource_cleanup):
    # single port cards... defaults to PhyType speed
    phy_test_module = _create_test_module('NIC-45')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 1
        assert speeds[0] == '100G:1'

    phy_test_module = _create_test_module('NIC-46')
    with AutoCommand('spirent.core.GetSupportedSpeedsCommand') as cmd:
        cmd.Set('PhyTestModule', phy_test_module.GetObjectHandle())
        cmd.Execute()
        speeds = cmd.GetCollection('SpeedInfoList')
        assert len(speeds) == 1
        assert speeds[0] == '100G:1'


# Not really unit tests. Just sanity checks, if we need to test something out real quick.
skip_sanity_check = pytest.mark.skipif(True, reason='sanity check only')


@skip_sanity_check
def test_all_changeling_has_corresponding_enabled_ports(stc):
    # Make sure nobody does anything to RCM that gives us a big surprise.
    try:
        conn = sqlite3.connect(rcm_path())
        cursor = conn.cursor()
        cursor.execute("SELECT key, value from capability where key like \
                       '%/TestModule/TestModule/supportsEnabledPortCountFeature' \
                       and value = 'true'")
        results = cursor.fetchall()
        assert results
        part_nums = [r[0].split('/')[0] for r in results]
        for part_num in part_nums:
            enabled = get_enabled_ports(part_num, cursor)
            # single port cards.
            if part_num not in ['NIC-45', 'NIC-46']:
                assert enabled.find('none') == -1
    finally:
        if conn:
            conn.close()


@skip_sanity_check
def test_all_non_changeling_has_default_lan_speed(stc):
    # Make sure nobody does anything to RCM that gives us a big surprise.
    try:
        conn = sqlite3.connect(rcm_path())
        cursor = conn.cursor()
        cursor.execute("SELECT key, value from capability where key like \
                       '%/TestModule/TestModule/supportsEnabledPortCountFeature' \
                       and value = 'false'")
        results = cursor.fetchall()
        assert results
        part_nums = [r[0].split('/')[0] for r in results]
        for part_num in part_nums:
            key = '%s/Default/PortGroup/L2L3/port/LAN/speed' % part_num
            cursor.execute("SELECT value from capability where key='%s'" % key)
            result = cursor.fetchone()
            assert result
            if part_num not in ['WAN-2002A', 'WAN-2003A']:
                assert result[0].find('none') == -1
    finally:
        if conn:
            conn.close()


def _rcm_path():
    rcm_db = os.path.join(CStcSystem.GetApplicationInstallPath(), 'RcmDb', 'RCM.db')
    return os.path.normpath(rcm_db)


def test_reset():
    assert reset()


def _create_test_module(part_num='VM-1G-V1-1P'):
    ctor = CScriptableCreator()
    phy_manager = CStcSystem.Instance().GetObject('physicalchassismanager')
    phy_chassis = ctor.Create('physicalchassis', phy_manager)
    phy_test_module = ctor.Create('physicaltestmodule', phy_chassis)
    phy_test_module.Set('PartNum', part_num)
    phy_test_module.Set('PortGroupSize', 1)
    return phy_test_module
