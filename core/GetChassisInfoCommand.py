import json
import socket
import traceback
from StcPython import StcPython
stc = StcPython()


def validate(AddrList, AutoConnect):
    return ''


def run(AddrList, AutoConnect):
    try:
        cmd_hnd = _get_this_cmd()
        chassis_infos = []
        for addr in AddrList:
            connect_chassis(addr, AutoConnect)
            chassis_info = create_info_dict(addr)
            if chassis_info:
                chassis_infos.append(json.dumps(chassis_info))
            else:
                chassis_infos.append('')
        if cmd_hnd is not None:
            stc.config(cmd_hnd, ChassisInfoList=chassis_infos)
    except Exception:
        stc.log('ERROR', 'unhandled exception:\n' + traceback.format_exc())
        return False

    return True


def reset():
    return True


def connect_chassis(Addr, AutoConnect):
    if AutoConnect:
        try:
            stc.perform('ConnectToChassisCommand', AddrList=Addr)
        except:
            # Don't care.
            pass


def create_info_dict(Addr):
    phy_man = stc.get('system1', 'children-physicalchassismanager')
    chassis = stc.perform('GetObjects', ClassName='PhysicalChassis',
                          RootList=phy_man,
                          Condition='Hostname = %s' % Addr)['ObjectList']

    if not chassis:
        return {}
    info = {}
    chassis_info = stc.get(chassis)
    chassis_info['IpAddr'] = socket.gethostbyname(Addr)
    info['physicalchassis'] = chassis_info
    if not _is_connected(info['physicalchassis']):
        return {}
    info['physicalchassis']['physicaltestmodules'] = _get_children_info(chassis,
                                                                        'physicaltestmodule')
    for phy_test_mod in info['physicalchassis']['physicaltestmodules']:
        phy_test_mod['physicalportgroups'] = _get_children_info(phy_test_mod['Handle'],
                                                                'physicalportgroup')
        for phy_port_group in phy_test_mod['physicalportgroups']:
            phy_port_group['physicalports'] = _get_children_info(phy_port_group['Handle'],
                                                                 'physicalport')
    return info


def _is_connected(chassis):
    return chassis['IsConnected'].lower() != 'false'


def _get_children_info(handle, type):
    children = stc.get(handle, 'children-%s' % type)
    children_info = []
    for child in children.split(' '):
        if child:
            info = stc.get(child)
            info['Handle'] = child
            children_info.append(info)
    return children_info


def _get_this_cmd():
    try:
        thisCommand = __commandHandle__
    except NameError:
        return None
    return thisCommand