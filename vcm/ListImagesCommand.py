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
        msg = 'list images failed validation' + msg
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
        image_info = vcmlib.listimages(Server, Port, credentials)
        id_list = []
        name_list = []
        info = image_info['images']
        for image_dict in info:
            id_list.append(str(image_dict['id']))
            name_list.append(str(image_dict['name']))
        logger.LogInfo(str(id_list))
        logger.LogInfo(str(name_list))
        cmd = get_this_cmd()
        cmd.SetCollection('ImageIdList', id_list)
        cmd.SetCollection('ImageNameList', name_list)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('List Images Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.SetCollection('ImageIdList', [])
    cmd.SetCollection('ImageNameList', [])
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
