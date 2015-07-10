from StcIntPythonPL import *
import pytest
import json
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

    def cleanup():
        result_filter.MarkDelete()

    request.addfinalizer(cleanup)
    return result_filter


@pytest.fixture(scope="module")
def sub(stc, request):
    import ResultSubscriber

    def cleanup():
        project = CStcSystem.Instance().GetObject('project')
        for drv in project.GetObjects('DynamicResultView'):
            drv.MarkDelete()
        ResultSubscriber.registered = {}
    request.addfinalizer(cleanup)
    return ResultSubscriber


@pytest.fixture(scope="module")
def stak(stc, request, port, resultFilter, sub):

    def cleanup():
        stc_sys = CStcSystem.Instance()
        project = stc_sys.GetObject('project')
        drvs = project.GetObjects('DynamicResultView')
        for drv in drvs:
            drv.MarkDelete()

    cleanup()
    request.addfinalizer(cleanup)
    drv = sub.subscribe('DeadFlow')
    params = {'TrafficFilters': [resultFilter.GetObjectHandle()],
              'Ports': [port.GetObjectHandle()],
              'Drvs': [drv.GetObjectHandle()],
              'DrvPorts': [port.GetObjectHandle()]}
    import CollectResultCommand
    return {'command': CollectResultCommand,
            'params': params}


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak):
    cmd = exec_command('CollectResultCommand', stak['params'])
    result = json.loads(cmd.Get("Result"))
    assert len(result["health_drilldowns"]) == 2
    assert len(result["health_drilldowns"][0]["columns"]) > 0
