"""Virtual Deployment Service STAK library"""
from StcIntPythonPL import *
import traceback
import vcmlib
from utils import check
from utils import make_credentials


def validate(Server, Port, Provider, ProviderServer, ProviderUser,
             ProviderPassword, ProviderTenant, VirtualMachineName,
             SizeName, ImageName, LicenseServer, NtpServer, PortSpeed,
             Driver, IpAddr, Netmask, Gateway, Telnet, NetworkList,
             BootTimeoutSeconds, BootCheckSeconds, HostName,
             DatacenterName, DatastoreName, ResourcePoolName, Count):
    """command validate method returns string"""
    logger = PLLogger.GetLogger('spirent.vds')
    msg = ''
    msg = check(Server, 'Server', msg)
    msg = check(Port, 'Port', msg)
    msg = check(Provider, 'Provider', msg)
    msg = check(ProviderServer, 'ProviderServer', msg)
    msg = check(ProviderUser, 'ProviderUser', msg)
    msg = check(VirtualMachineName, 'VirtualMachineName', msg)
    msg = check(SizeName, 'SizeName', msg)
    msg = check(ImageName, 'ImageName', msg)
    if len(msg) != 0:
        msg = 'create VM failed validation' + msg
        logger.LogError(msg)
        return msg
    return ''


def run(Server, Port, Provider, ProviderServer, ProviderUser,
        ProviderPassword, ProviderTenant, VirtualMachineName,
        SizeName, ImageName, LicenseServer, NtpServer, PortSpeed,
        Driver, IpAddr, Netmask, Gateway, Telnet, NetworkList,
        BootTimeoutSeconds, BootCheckSeconds, HostName,
        DatacenterName, DatastoreName, ResourcePoolName, Count):
    """command run method returns True/False"""
    if NetworkList == '':
        NetworkList = []
    logger = PLLogger.GetLogger('spirent.vds')
    credentials = make_credentials(Provider, ProviderServer, ProviderUser,
                                   ProviderPassword, ProviderTenant)
    try:
        vm_info = vcmlib.virtualmachinecreate(Server, Port, credentials,
                                              VirtualMachineName, SizeName,
                                              ImageName, LicenseServer,
                                              NtpServer, PortSpeed,
                                              Driver, IpAddr, Netmask,
                                              Gateway, Telnet, NetworkList,
                                              BootTimeoutSeconds,
                                              BootCheckSeconds,
                                              HostName, DatacenterName,
                                              DatastoreName,
                                              ResourcePoolName,
                                              Count)
        running_list = vm_info['virtualmachine_running']
        running_list = [str(elem) for elem in running_list]
        id_list = vm_info['id']
        id_list = [str(elem) for elem in id_list]
        url_list = vm_info['url']
        url_list = [str(elem) for elem in url_list]
        logger.LogInfo(str(running_list))
        logger.LogInfo(str(id_list))
        logger.LogInfo(str(url_list))
        cmd = get_this_cmd()
        cmd.SetCollection('VirtualMachineRunning', running_list)
        cmd.SetCollection('VirtualMachineId', id_list)
        cmd.SetCollection('Url', url_list)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('Create VM Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.SetCollection('VirtualMachineRunning', [])
    cmd.SetCollection('VirtualMachineId', [])
    cmd.SetCollection('Url', [])
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
