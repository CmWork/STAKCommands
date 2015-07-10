import traceback

from StcIntPythonPL import PLLogger, CStcSystem, CUserLogResult, CHandleRegistry

CMD_NAME = 'spirent.core.GetUserErrorLogsCommand'


def validate(IncludeWarnings, Clear):
    return ''


def run(IncludeWarnings, Clear):
    log = _get_logger()

    try:
        # Flush any current messages to the cache.
        CUserLogResult.Instance().FlushCache()

        log_result = CStcSystem.Instance().GetObject('UserLogResult')
        if not log_result.Get('LogCacheEnabled'):
            log.LogWarn('Log collection must be enabled first via the EnableUserLogs command.')
            return False

        cmd = _get_this_cmd()
        if cmd:
            logs = _filter(log_result.GetCollection('LogCache'), IncludeWarnings)
            cmd.SetCollection('LogList', logs)

        if Clear:
            log_result.SetCollection('LogCache', [])
    except RuntimeError as e:
        log.LogError('error: ' + str(e))
        return False
    except Exception:
        log.LogError('error: unhandled exception:\n' +
                     traceback.format_exc())
        return False

    return True


def _filter(logs, include_warnings):

    def should_include(log):
        if log.startswith('category==user.event'):
            return True
        if log.find('level==1') != -1:
            return True
        if include_warnings and log.find('level==2') != -1:
            return True
        return False
    return [_strip_meta(log) for log in logs if should_include(log)]


def _strip_meta(log):
    token = 'level=='
    idx = log.find(token) + len(token) + 2
    return log[idx:]


def reset():
    return True


def _get_logger():
    return PLLogger.GetLogger(CMD_NAME)


def _get_this_cmd():
    try:
        thisCommand = CHandleRegistry.Instance().Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand