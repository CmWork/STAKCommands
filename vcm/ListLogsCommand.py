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
        msg = 'list logs failed validation' + msg
        logger.LogError(msg)
        return msg
    return ''


def run(Server, Port):
    """command run method returns True/False"""
    logger = PLLogger.GetLogger('spirent.vds')
    try:
        log_info = vcmlib.listlogs(Server, Port)
        log_files = log_info['log_files']
        url_list = []
        log_file_size_list = []
        log_file_name_list = []
        for log_file in log_files:
            url_list.append(str(log_file['url']))
            log_file_size_list.append(str(log_file['log_file_size']))
            log_file_name_list.append(str(log_file['log_file_name']))
        logger.LogInfo(str(url_list))
        logger.LogInfo(str(log_file_size_list))
        logger.LogInfo(str(log_file_name_list))
        cmd = get_this_cmd()
        cmd.SetCollection('UrlList', url_list)
        cmd.SetCollection('LogSizeList', log_file_size_list)
        cmd.SetCollection('LogNameList', log_file_name_list)
    except Exception as ex:
        if len(ex.message):
            msg = str(ex.message)
        else:
            msg = str(ex)
        stack_trace = traceback.format_exc()
        logger.LogError('List Logs Exception Caught: ' +
                        msg + ' ' + stack_trace)
        return False
    return True


def reset():
    """command reset method returns True/False"""
    cmd = get_this_cmd()
    cmd.SetCollection('UrlList', [])
    cmd.SetCollection('LogSizeList', [])
    cmd.SetCollection('LogNameList', [])
    return True


def get_this_cmd():
    """returns command handle"""
    hnd_reg = CHandleRegistry.Instance()
    try:
        cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return cmd
