import pytest
from StcIntPythonPL import *
from spirent.core.GetUserErrorLogsCommand import *
from spirent.core.utils.scriptable import AutoCommand


def test_validate():
    assert validate(True, True) == ''


def test_run(stc):

    # Log collection needs to be enabled.
    logs = []
    with AutoCommand('spirent.core.GetUserErrorLogsCommand') as get_logs_cmd:
        get_logs_cmd.Execute()
        logs = get_logs_cmd.GetCollection('LogList')
    assert len(logs) == 0

    with AutoCommand('spirent.core.EnableUserLogsCommand') as enable_cmd:
        enable_cmd.Execute()

    # Generate a info log which we filter out.
    with AutoCommand('ApplyToIl') as apply_cmd:
        apply_cmd.Execute()

    # Generate an error.
    with pytest.raises(RuntimeError):
        with AutoCommand('LoadFromDatabaseCommand') as load_cmd:
            load_cmd.Set('DatabaseConnectionString', 'xxx.db')
            load_cmd.Execute()

    logs = []
    with AutoCommand('spirent.core.GetUserErrorLogsCommand') as get_logs_cmd:
        get_logs_cmd.Execute()
        logs = get_logs_cmd.GetCollection('LogList')
    assert len(logs) == 1
    assert logs[0].find('Please check that equipment is online') != 0

    # Logs should clear by default.
    logs = []
    with AutoCommand('spirent.core.GetUserErrorLogsCommand') as get_logs_cmd:
        get_logs_cmd.Execute()
        logs = get_logs_cmd.GetCollection('LogList')
    assert len(logs) == 0

    # Disable
    with AutoCommand('spirent.core.EnableUserLogsCommand') as enable_cmd:
        enable_cmd.Set('Enable', False)
        enable_cmd.Execute()

    # Generate another warning.
    logs = []
    with AutoCommand('spirent.core.GetUserErrorLogsCommand') as get_logs_cmd:
        get_logs_cmd.Execute()
        logs = get_logs_cmd.GetCollection('LogList')
    assert len(logs) == 0

    with AutoCommand('spirent.core.EnableUserLogsCommand') as enable_cmd:
        enable_cmd.Execute()

    # No warnings by default.
    logs = []
    with AutoCommand('spirent.core.GetUserErrorLogsCommand') as get_logs_cmd:
        get_logs_cmd.Execute()
        logs = get_logs_cmd.GetCollection('LogList')
    assert len(logs) == 0


def test_reset():
    assert reset()
