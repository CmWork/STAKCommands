from StcIntPythonPL import *
import os
import sys
import pytest


def clear():
    project = CStcSystem.Instance().GetObject('project')
    for drv in project.GetObjects('DynamicResultView'):
        drv.MarkDelete()


@pytest.fixture
def sub(request):
    # we don't want module scope for this fixture
    # Need to be in build output folder
    sys.path.append(
        os.path.join(os.getcwd(),
                     'STAKCommands',
                     'spirent',
                     'methodology', 'trafficcenter')
        )
    clear()

    def fin():
        clear()
    request.addfinalizer(fin)
    import ResultSubscriber
    ResultSubscriber.registered = {}
    return ResultSubscriber


def test_loadConfig(stc, sub):
    # test good case
    drv = sub.loadConfig('DroppedCountBasic')
    assert drv

    # test drv def not exists
    drv = None
    drv = sub.loadConfig('foo')
    assert not drv


def test_loadSystemConfig(stc, sub):
    drv = sub.loadSystemConfig('FloodedFlow')
    assert drv

    drv = None
    drv = sub.loadSystemConfig('foo')
    assert not drv


def test_subscribe(stc, sub):
    # Test clean case
    drv = sub.subscribe('DroppedCountBasic')
    assert drv
    assert drv.Get('ResultState') == 'SUBSCRIBED'

    # Test already registered
    sub.registered['DroppedCountBasic'] = drv.GetObjectHandle()
    drv2 = sub.subscribe('DroppedCountBasic')
    assert drv2.GetObjectHandle() == drv.GetObjectHandle()

    # test system drv
    drv = None
    drv = sub.subscribe('FloodedFlow')
    assert drv
    assert drv.Get('ResultState') == 'SUBSCRIBED'


def test_unsubscribe(stc, sub):
    sub.subscribe('DroppedCountBasic')
    assert sub.unsubscribe('DroppedCountBasic')
