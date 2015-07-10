"""Virtual Deployment Service STAK library"""
from StcIntPythonPL import *
import traceback
import vcmlib
from utils import check


def validate(Server, Port):
    """command validate method returns string"""
    logger = PLLogger.GetLogger('spirent.vds')
    msg = ''
    msg = check(Server, 'Server', msg)
    msg = check(Port, 'Port', msg)
    if len(msg) != 0:
        msg = 'list versions failed validation' + msg
        logger.LogError(msg)
        return msg
    return ''


def run(Server, Port):
    """command run method returns True/False"""
    logger = PLLogger.GetLogger('spirent.vds')
    try:
        version_info = vcmlib.listversions(Server, Port)
        api_versions = version_info['api_versions']
        status_list = []
        version_list = []
        for ver in api_versions:
            status_list.append(str(ver['status']))
            version_list.append(str(ver['version']))
        product_version = str(version_info['product_version']['version'])
        logger.LogInfo(str(status_list))
        logger.LogInfo(str(version_list))
        logger.LogInfo(str(product_version))
        cmd = get_this_cmd()
        cmd.SetCollection('StatusList', status_list)
        cmd.SetCollection('VersionList', version_list)
        cmd.Set('ProductVersion', product_version)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('List Versions Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.SetCollection('StatusList', [])
    cmd.SetCollection('VersionList', [])
    cmd.Set('ProductVersion', '')
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
