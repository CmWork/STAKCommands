from StcIntPythonPL import *
import pytest
import json
from ..utils.CommandUtils import exec_command
from spirent.core.utils.scriptable import AutoCommand


@pytest.fixture(scope="module")
def results_to_ignore(stc):
    project = CStcSystem.Instance().GetObject('project')
    result_datasets = project.GetObjects("ResultDataSet")
    return [rd.GetObjectHandle() for rd in result_datasets]


@pytest.fixture(scope="module")
def cleanup_all(stc, request, results_to_ignore):
    def cleanup():
        with AutoCommand("ResetConfigCommand") as reset_cmd:
            reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
            reset_cmd.Execute()
    request.addfinalizer(cleanup)


@pytest.fixture(scope="module")
def port(stc, request, results_to_ignore):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', project)

    def cleanup():
        port.MarkDelete()

    request.addfinalizer(cleanup)
    return port


@pytest.fixture(scope="module")
def health(stc, port, results_to_ignore):
    health_config = {
        'health': {
            'traffic': [
                {'name': 'DeadFlow'},
                {'name': 'DroppedFrameCount',
                 'threshold': '0',
                 'condition': 'GREATER_THAN'}
                ],
            'system': []
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
    cmd = exec_command(
        'SubscribeHealthCommand',
        {'HealthConfig': json.dumps(health_config)}
        )
    trf_drvs = cmd.GetCollection('TrafficDrvs')
    trf_filters = cmd.GetCollection('TrafficFilter')
    return {
        'trf_drvs': trf_drvs,
        'trf_filters': trf_filters
        }


@pytest.fixture(scope="module")
def stream_stats(health, stc, port, results_to_ignore):
    params = {
        'TrafficFilter': health['trf_filters'][0],
        'TargetPort': port.GetObjectHandle(),
        'CallbackInfo':
        '{"url":"http://localhost:5000","context":""}'
    }
    cmd = exec_command('DrillDownHealthCommand', params)
    stream_drv = cmd.Get('HealthDetailDrv')
    return {'stream_drv': stream_drv}


@pytest.fixture(scope="module")
def port_stats(stc, port, results_to_ignore):
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
    params = {'Config': json.dumps(config)}
    exec_command('SubscribePortCounterCommand', params)


def test_exec(stc,
              results_to_ignore,
              health,
              stream_stats,
              port_stats,
              cleanup_all):
    hnd_reg = CHandleRegistry.Instance()
    trf_drv_hnds = health['trf_drvs']
    assert len(trf_drv_hnds) == 1
    trf_drv_hnd = trf_drv_hnds[0]
    trf_drv = hnd_reg.Find(trf_drv_hnd)
    assert trf_drv.Get('ResultState') == 'SUBSCRIBED'
    stream_drv_hnd = stream_stats['stream_drv']
    stream_drv = hnd_reg.Find(stream_drv_hnd)
    assert stream_drv.Get('ResultState') == 'SUBSCRIBED'

    with AutoCommand(
        'spirent.methodology.trafficcenter.UnsubscribeAllStatsCommand'
    ) as cmd:
        cmd.Execute()
    trf_drv = hnd_reg.Find(trf_drv_hnd)
    assert (trf_drv is None or
            trf_drv.Get('ResultState') == 'NONE')
    stream_drv = hnd_reg.Find(stream_drv_hnd)
    assert (stream_drv is None or
            stream_drv.Get('ResultState') == 'NONE')

    # verify all result dataset
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")
    result_datasets = project.GetObjects("ResultDataSet")
    for result_dataset in result_datasets:
        if result_dataset.GetObjectHandle() in results_to_ignore:
            assert result_dataset.Get('ResultState') == 'NONE'
