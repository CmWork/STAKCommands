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
        msg = 'VM destroy failed validation' + msg
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
        vm_info = vcmlib.virtualmachinedestroy(Server, Port, credentials,
                                               VirtualMachineId)
        logger.LogInfo('virtualMachinePresent ' +
                       str(vm_info['virtualmachine_present']))
        cmd = get_this_cmd()
        cmd.Set('VirtualMachinePresent',
                str(vm_info['virtualmachine_present']))
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('Destroy VM Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.Set('VirtualMachinePresent', True)
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
