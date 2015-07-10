"""Virtual Deployment Service STAK library"""
from StcIntPythonPL import *
import traceback
import vcmlib
from utils import check
from utils import make_credentials


def validate(Server, Port,
             Provider, ProviderServer,
             ProviderUser, ProviderPassword, ProviderTenant,
             VirtualMachineId):
    """command validate method returns string"""
    logger = PLLogger.GetLogger('spirent.vds')
    msg = ''
    msg = check(Server, 'Server', msg)
    msg = check(Port, 'Port', msg)
    msg = check(Provider, 'Provider', msg)
    msg = check(ProviderServer, 'ProviderServer', msg)
    msg = check(ProviderUser, 'ProviderUser', msg)
    msg = check(VirtualMachineId, 'VirtualMachineId', msg)
    if len(msg) != 0:
        msg = 'VM info failed validation' + msg
        logger.LogError(msg)
        return msg
    return ''


def run(Server, Port,
        Provider, ProviderServer,
        ProviderUser, ProviderPassword, ProviderTenant,
        VirtualMachineId):
    """command run method returns True/False"""
    logger = PLLogger.GetLogger('spirent.vds')
    credentials = make_credentials(Provider, ProviderServer, ProviderUser,
                                   ProviderPassword, ProviderTenant)
    try:
        vm_info = vcmlib.virtualmachineinfo(Server, Port, credentials,
                                            VirtualMachineId)
        ip_list = []
        net_list = []
        network_list = vm_info['virtualmachine_ips']
        for net_dict in network_list:
            ip_list.append(str(net_dict['ip_address']))
            net_list.append(str(net_dict['network_name']))
        logger.LogInfo('virtualMachineFound ' +
                       str(vm_info['virtualmachine_found']))
        logger.LogInfo(str(ip_list))
        logger.LogInfo(str(net_list))
        cmd = get_this_cmd()
        cmd.Set('VirtualMachineFound', str(vm_info['virtualmachine_found']))
        cmd.SetCollection('AddrList', ip_list)
        cmd.SetCollection('NetworkList', net_list)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('VM Info Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.Set('VirtualMachineFound', False)
    cmd.SetCollection('AddrList', [])
    cmd.SetCollection('NetworkList', [])
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
