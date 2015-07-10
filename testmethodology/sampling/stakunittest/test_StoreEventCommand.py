from StcIntPythonPL import *
import time
from spirent.core.utils.scriptable import AutoCommand


KEY = 'spirent.methodology.sampling'


def test_ValidateError(stc):
    gotFailure = False
    with AutoCommand('spirent.methodology.sampling.StoreEventCommand') as cmd:
        try:
            cmd.Execute()
        except RuntimeError as e:
            if 'not be blank' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('StoreEventCommand did not fail as expected')


def test_NoPersistObject(stc):
    if CObjectRefStore.Exists(KEY):
        CObjectRefStore.Release(KEY)
    gotFailure = False
    with AutoCommand('spirent.methodology.sampling.StoreEventCommand') as cmd:
        try:
            cmd.Set('EventName', 'DeviceStart')
            cmd.Set('ErrorOnFailure', True)
            cmd.Execute()
        except RuntimeError as e:
            if 'not properly initialized' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('StoreEventCommand did not fail as expected')


def test_VerifyInvoke(stc):
    if CObjectRefStore.Exists(KEY):
        CObjectRefStore.Release(KEY)
    now = int(time.time())
    persObj = {}
    CObjectRefStore.Put(KEY, persObj)
    with AutoCommand('spirent.methodology.sampling.StoreEventCommand') as cmd:
        cmd.Set('EventName', 'DeviceStart')
        cmd.Execute()
    assert 'Event' in persObj
    evList = persObj['Event']
    # Only 1 entry found
    assert 1 == len(evList)
    # Check fields
    assert 'DeviceStart' == evList[0][0]
    assert 0 == evList[0][1]
    assert now <= evList[0][2]
    # Clean up
    CObjectRefStore.Release(KEY)


def test_VerifyMultiInvoke(stc):
    if CObjectRefStore.Exists(KEY):
        CObjectRefStore.Release(KEY)
    persObj = {}
    CObjectRefStore.Put(KEY, persObj)
    with AutoCommand('spirent.methodology.sampling.StoreEventCommand') as cmd:
        cmd.Set('EventName', 'DeviceStart')
        cmd.Execute()
        assert cmd.Reset()
        cmd.Set('EventName', 'DeviceStop')
        cmd.Execute()
        assert cmd.Reset()
        cmd.Set('EventName', 'DeviceStart')
        cmd.Execute()
    assert 'Event' in persObj
    evList = persObj['Event']
    # 3 entries
    assert 3 == len(evList)
    assert 'DeviceStart' == evList[0][0]
    assert 0 == evList[0][1]
    assert 'DeviceStop' == evList[1][0]
    assert 0 == evList[1][1]
    # The second DeviceStart should have 2nd tuple element as 1
    assert 'DeviceStart' == evList[2][0]
    assert 1 == evList[2][1]
    # Clean up
    CObjectRefStore.Release(KEY)
