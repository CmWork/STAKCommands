import os
import sqlite3
import traceback
from StcIntPythonPL import PLLogger, CStcSystem, CHandleRegistry

CMD_NAME = 'spirent.core.GetSupportedSpeedsCommand'


def validate(PhyTestModule, PhyType):
    test_module = CHandleRegistry.Instance().Find(PhyTestModule)
    if test_module is None:
        return 'PhyTestModule is required'
    if not test_module.IsTypeOf('PhysicalTestModule'):
        return 'Invalid PhyTestModule'
    return ''


def run(PhyTestModule, PhyType):
    logger = _get_logger()
    try:
        test_module = CHandleRegistry.Instance().Find(PhyTestModule)
        part_num = test_module.Get('PartNum')
        rcm_db = rcm_path()
        logger.LogInfo('Opening connection to RCM DB ' + rcm_db)
        conn = sqlite3.connect(rcm_db)
        cursor = conn.cursor()
        if is_changeling_module(part_num, cursor):
            speeds = get_enabled_ports(part_num, cursor)
            if speeds.find('none') == 0:
                # NIC-45 and NIC-46 are single port cards,
                # breaking the RCM rules apparently.
                speeds = get_phy_type_based_speed(PhyType, test_module, cursor)
        else:
            speeds = get_phy_type_based_speed(PhyType, test_module, cursor)
        _set_speeds(speeds)

    except RuntimeError as e:
        logger.LogError('error: ' + str(e))
        return False
    except Exception:
        logger.LogError('unhandled exception:\n' + traceback.format_exc())
        return False
    finally:
        if conn:
            logger.LogInfo('Closing connection to RCM DB ' + rcm_db)
            conn.close()

    return True


def reset():
    return True


def rcm_path():
    rcm_db = os.path.join(CStcSystem.GetApplicationInstallPath(), 'RcmDb', 'RCM.db')
    return os.path.normpath(rcm_db)


def is_changeling_module(part_num, cursor):
    key = '%s/TestModule/TestModule/supportsEnabledPortCountFeature' % part_num
    cursor.execute("SELECT value from capability where key='%s'" % key)
    result = cursor.fetchone()
    return result is not None and result[0] == 'true'


def get_enabled_ports(part_num, cursor):
    key = '%s/Default/PortGroup/L2L3/portGroup/enabledPorts' % part_num
    cursor.execute("SELECT value from capability where key='%s'" % key)
    result = cursor.fetchone()
    return result[0]


def get_phy_type_based_speed(phy_type, test_module, cursor):
    key = '%s/Default/PortGroup/L2L3/port/%s/speed' % (test_module.Get('PartNum'), phy_type)
    cursor.execute("SELECT value from capability where key='%s'" % key)
    result = cursor.fetchone()
    speeds = result[0].split(';')
    # We take the port group size from the data model because
    # some module's mode can be altered, which changes the port group size.
    # For example, Shadowcat mode can be changed via the Equipment View in STC.
    portGroupSize = test_module.Get('PortGroupSize')
    return ';'.join(['%s:%s' % (speed.split(':')[0], portGroupSize) for speed in speeds])


def _set_speeds(speeds):
    cmd = _get_this_cmd()
    if cmd:
        cmd.SetCollection('SpeedInfoList', str(speeds).split(';'))


def _get_logger():
    return PLLogger.GetLogger(CMD_NAME)


def _get_this_cmd():
    try:
        thisCommand = CHandleRegistry.Instance().Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand