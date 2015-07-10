from StcIntPythonPL import *
import pytest
from ..utils.CommandUtils import exec_command


@pytest.fixture(scope="module")
def health():
    return {'name': 'DroppedFrameCount',
            'threshold': '0',
            'condition': 'GREATER_THAN'}


@pytest.fixture(scope="module")
def port(stc, request):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', project)

    def cleanup():
        port.MarkDelete()

    request.addfinalizer(cleanup)
    return port


@pytest.fixture(scope="module")
def resultFilter(stc, request, health):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    result_filter = ctor.Create("CounterResultFilter", project)
    filter_property = ctor.Create("CounterFilterProperty", result_filter)
    filter_property.Set("FilterDisplayName", health["name"])
    filter_property.Set("PropertyOperand", health["name"])
    filter_property.Set("ValueOperand", health["threshold"])
    filter_property.Set("ComparisonOperator", health["condition"])
    return result_filter


@pytest.fixture(scope="module")
def stak(stc, request, port, resultFilter):

    def cleanup():
        stc_sys = CStcSystem.Instance()
        project = stc_sys.GetObject('project')
        drvs = project.GetObjects('DynamicResultView')
        subscribeCommands = stc_sys.GetObjects('SubscribePropertyChangeCommand')
        for drv in drvs:
            drv.MarkDelete()
        for cmd in subscribeCommands:
            cmd.MarkDelete()

    cleanup()
    params = {'TrafficFilter': resultFilter.GetObjectHandle(),
              'TargetPort': port.GetObjectHandle(),
              'CallbackInfo':
              '{"url":"http://localhost:5000","context":""}'
              }
    request.addfinalizer(cleanup)
    from .. import DrillDownHealthCommand
    return {'command': DrillDownHealthCommand,
            'params': params, }


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak):
    cmd = exec_command('DrillDownHealthCommand', stak['params'])
    drvHnd = cmd.Get('HealthDetailDrv')
    hnd_reg = CHandleRegistry.Instance()
    drv = hnd_reg.Find(drvHnd)
    assert drv.Get('ResultState') == 'SUBSCRIBED'
