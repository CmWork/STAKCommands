from StcIntPythonPL import *


def get_result_framework_logger():
    logger = PLLogger.GetLogger('methodology')
    return logger


def debug(message):
    logger = get_result_framework_logger()
    logger.LogDebug(message)


def info(message):
    logger = get_result_framework_logger()
    logger.LogInfo(message)


def warning(message):
    logger = get_result_framework_logger()
    logger.LogWarn(message)


def error(message):
    logger = get_result_framework_logger()
    logger.LogError(message)


def debug_result_object_info(result_object):
    debug('Result Handle:' + str(result_object.GetObjectHandle()))
    debug('Result object Name:' + result_object.Get('name'))


def log_result_info_status(result_object):
    debug_result_object_info(result_object)
    debug('Result info:' + result_object.Get('Info'))
    debug('Result status:' + result_object.Get('Status'))


def log_active_iteration_info_status(result_object):
    debug_result_object_info(result_object)
    debug('Active Iteration info:' + result_object.Get('ActiveIterationInfo'))
    debug('Active Iteration status:' + result_object.Get('ActiveIterationStatus'))