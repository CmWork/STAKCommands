from StcIntPythonPL import *
import pytest
from ..utils.CommandUtils import exec_command
import json
from spirent.core.utils.scriptable import AutoCommand


@pytest.fixture(scope="module")
def stak(stc, request):
    health_config = {
        'health': {
            'traffic': [
                {'name': 'DeadFlow'},
                {'name': 'DroppedFrameCount',
                 'threshold': '0',
                 'condition': 'GREATER_THAN'}
                ],
            'system': [
                {'name': 'PhysicalLinkFailure'}
                ]
            },
        'callback_info': {
            'traffic': {
                "url": "http://localhost:5000",
                "context": ""
                },
            'system': {
                "url": "http://localhost:5000",
                "context": ""
                },
            'drv': {
                "url": "http://localhost:5000",
                "context": ""
                }
            }
        }

    def cleanup():
        with AutoCommand("ResetConfigCommand") as reset_cmd:
            reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
            reset_cmd.Execute()

    cleanup()
    params = {'HealthConfig': json.dumps(health_config)}
    request.addfinalizer(cleanup)
    from .. import SubscribeHealthCommand
    return {'command': SubscribeHealthCommand,
            'params': params, }


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak):
    cmd = exec_command('SubscribeHealthCommand', stak['params'])
    assert cmd.GetCollection('TrafficDrvNames') == ['DeadFlow']
    assert cmd.GetCollection('TrafficThresholdNames') == ['DroppedFrameCount']
    assert len(cmd.GetCollection('TrafficDrvs')) == 1
    assert len(cmd.GetCollection('TrafficFilter')) == 1
