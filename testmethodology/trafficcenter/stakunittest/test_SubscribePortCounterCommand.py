from StcIntPythonPL import *
import pytest
from ..utils.CommandUtils import exec_command
import json
from spirent.core.utils.scriptable import AutoCommand


@pytest.fixture(scope="module")
def stak(stc, request):
    config = {
        'counters': {
            'tx': ['totalframecount'],
            'rx': ['totalframecount']
        },
        'callback_info': {
            'url': "http://localhost:5000",
            "context": ""
        }
    }

    def cleanup():
        with AutoCommand("ResetConfigCommand") as reset_cmd:
            reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
            reset_cmd.Execute()

    cleanup()
    params = {'Config': json.dumps(config)}
    request.addfinalizer(cleanup)
    from .. import SubscribePortCounterCommand
    return {'command': SubscribePortCounterCommand,
            'params': params, }


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak):
    cmd = exec_command('SubscribePortCounterCommand', stak['params'])
    assert cmd is not None
