"""Virtual Deployment Service STAK library"""
from StcIntPythonPL import *
import traceback
import vcmlib
from utils import check
from utils import make_credentials


def validate(Server, Port,
             Provider, ProviderServer,
             ProviderUser, ProviderPassword, ProviderTenant):
    """command validate method returns string"""
    logger = PLLogger.GetLogger('spirent.vds')
    msg = ''
    msg = check(Server, 'Server', msg)
    msg = check(Port, 'Port', msg)
    msg = check(Provider, 'Provider', msg)
    msg = check(ProviderServer, 'ProviderServer', msg)
    msg = check(ProviderUser, 'ProviderUser', msg)
    if len(msg) != 0:
        msg = 'list sizes failed validation' + msg
        logger.LogError(msg)
        return msg
    return ''


def run(Server, Port,
        Provider, ProviderServer,
        ProviderUser, ProviderPassword, ProviderTenant):
    """command run method returns True/False"""
    logger = PLLogger.GetLogger('spirent.vds')
    credentials = make_credentials(Provider, ProviderServer, ProviderUser,
                                   ProviderPassword, ProviderTenant)
    try:
        size_info = vcmlib.listsizes(Server, Port, credentials)
        id_list = []
        name_list = []
        ram_list = []
        disk_list = []
        vcpus_list = []
        info = size_info['sizes']
        for size_dict in info:
            id_list.append(str(size_dict['id']))
            name_list.append(str(size_dict['name']))
            ram_list.append(str(size_dict['ram']))
            disk_list.append(str(size_dict['disk']))
            vcpus_list.append(str(size_dict['vcpus']))
        logger.LogInfo(str(id_list))
        logger.LogInfo(str(name_list))
        logger.LogInfo(str(ram_list))
        logger.LogInfo(str(disk_list))
        logger.LogInfo(str(vcpus_list))
        cmd = get_this_cmd()
        cmd.SetCollection('SizeIdList', id_list)
        cmd.SetCollection('SizeNameList', name_list)
        cmd.SetCollection('RamList', ram_list)
        cmd.SetCollection('DiskList', disk_list)
        cmd.SetCollection('VcpusList', vcpus_list)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('List Sizes Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.SetCollection('SizeIdList', [])
    cmd.SetCollection('SizeNameList', [])
    cmd.SetCollection('RamList', [])
    cmd.SetCollection('DiskList', [])
    cmd.SetCollection('VcpusList', [])
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
