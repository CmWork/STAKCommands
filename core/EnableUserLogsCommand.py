from StcIntPythonPL import CStcSystem


def validate(Enable, Limit):
    return ''


def run(Enable, Limit):
    log_result = CStcSystem.Instance().GetObject('UserLogResult')
    log_result.Set('LogCacheEnabled', Enable)
    log_result.Set('LogCacheMaxSize', Limit)
    return True


def reset():
    return True