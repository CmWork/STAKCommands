from StcIntPythonPL import *
import pytest
from ..utils.CommandUtils import exec_command


@pytest.fixture(scope="module")
def stak(stc, request):
    params = {'Duration': 10}

    from .. import SetTrafficDurationCommand
    return {'command': SetTrafficDurationCommand,
            'params': params, }


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak):
    params = {'Duration': 100}

    cmd = exec_command("SetTrafficDurationCommand", params)
    duration = cmd.Get("Duration")
    assert duration == 100
