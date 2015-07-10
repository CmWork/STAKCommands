from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


OBJ_KEY = 'spirent.methodology.sampling'


def test_ValidatePollingError(stc):
    gotFailure = False
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 0)
            cmd.Execute()
        except RuntimeError as e:
            if 'must be at least' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('Setting PollingInterval to 0 did not fail as expected')


def test_ValidatePollingErrorString(stc):
    fail_message = ""
    got_failure = False
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 'string')
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'CStcInvalidArgument' in fail_message:
                got_failure = True
    if not got_failure:
        raise AssertionError('Setting PollingInterval to 0 failed with ' +
                             'unexpected error "' + fail_message + '"')


def test_ValidatePropertyError(stc):
    gotFailure = False
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 1)
            cmd.Set('PropertyList', "notadottedstring")
            cmd.Execute()
        except RuntimeError as e:
            if 'Properties within' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('SetupSubscriptionCommand did not fail as expected')


def test_ValidateEmptyPropertyError(stc):
    gotFailure = False
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 1)
            cmd.Set('PropertyList', '')
            cmd.Execute()
        except RuntimeError as e:
            if 'at least one' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('SetupSubscriptionCommand did not fail as expected')


def test_ValidatePropertyCommaError(stc):
    fail_message = ""
    got_failure = False
    projHnd = CStcSystem.Instance().GetObject("project").GetObjectHandle()
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 1)
            cmd.SetCollection('ResultParent', [projHnd])
            cmd.Set('PropertyList', "BfdRouterConfig.BfdRouterResults.TimeoutCount,"
                    " BfdRouterConfig.BfdRouterResults.RxCount")
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'Invalid property name' in fail_message:
                got_failure = True
    if not got_failure:
        raise AssertionError('SetupSubscriptionCommand failed with ' +
                             'unexpected error "' + fail_message + '"')


def test_ValidatePropertyCommaNoSpaceError(stc):
    fail_message = ""
    got_failure = False
    projHnd = CStcSystem.Instance().GetObject("project").GetObjectHandle()
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 1)
            cmd.SetCollection('ResultParent', [projHnd])
            cmd.Set('PropertyList', "BfdRouterConfig.BfdRouterResults.TimeoutCount,"
                    "BfdRouterConfig.BfdRouterResults.RxCount")
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'must be of the format' in fail_message:
                got_failure = True
    if not got_failure:
        raise AssertionError('SetupSubscriptionCommand failed with ' +
                             'unexpected error "' + fail_message + '"')


def test_ValidateTerminalError(stc):
    gotFailure = False
    plLogger = PLLogger.GetLogger('methodology')
    projHnd = CStcSystem.Instance().GetObject("project").GetObjectHandle()
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingInterval', 1)
            cmd.SetCollection('ResultParent', [projHnd])
            cmd.Set('PropertyList', "cfg1.res1.prop1 cfg1.res1.prop2")
            cmd.Set('EnableCondition', True)
            cmd.SetCollection('TerminalValueList', [1, 2, 3])
            cmd.Execute()
        except RuntimeError as e:
            plLogger.LogError("In test_ValidateTerminalError, e is:" + str(e))
            if 'same numbers' in str(e):
                gotFailure = True
    if not gotFailure:
        raise AssertionError('SetupSubscriptionCommand did not fail as expected')


def test_VerifyFreshInvokePort(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    ctor = CScriptableCreator()

    proj = CStcSystem.Instance().GetObject("project")
    port = ctor.Create('Port', proj)
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        cmd.Set('PollingInterval', 1)
        cmd.SetCollection('ResultParent', [port.GetObjectHandle()])
        cmd.Set('ValueIdleTimeout', 100)
        cmd.Set('PropertyList', "BfdRouterConfig.BfdRouterResults.TimeoutCount"
                                " BfdRouterConfig.BfdRouterResults.RxCount")
        cmd.Execute()

    assert CObjectRefStore.Exists(OBJ_KEY)
    persObj = CObjectRefStore.Get(OBJ_KEY)
    assert 'Subscription' in persObj
    subList = persObj['Subscription']
    # Exactly 2 entry found
    assert 2 == len(subList)
    # Check fields
    assert 100 == subList[0]['ValueIdleTimeout']
    assert False == subList[0]['EnableCondition']
    assert (subList[0]['Terminal'] is None) or (len(subList[0]['Terminal']) == 0)
    CObjectRefStore.Release(OBJ_KEY)


def test_VerifyFreshInvoke(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)

    projHnd = CStcSystem.Instance().GetObject("project").GetObjectHandle()
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        cmd.Set('PollingInterval', 1)
        cmd.SetCollection('ResultParent', [projHnd])
        cmd.Set('ValueIdleTimeout', 100)
        cmd.Set('PropertyList', "BfdRouterConfig.BfdRouterResults.TimeoutCount"
                                " BfdRouterConfig.BfdRouterResults.RxCount")
        cmd.Execute()

    assert CObjectRefStore.Exists(OBJ_KEY)
    persObj = CObjectRefStore.Get(OBJ_KEY)
    assert 'Subscription' in persObj
    subList = persObj['Subscription']
    # Exactly 2 entry found
    assert 2 == len(subList)
    # Check fields
    assert 100 == subList[0]['ValueIdleTimeout']
    assert False == subList[0]['EnableCondition']
    assert (subList[0]['Terminal'] is None) or (len(subList[0]['Terminal']) == 0)

    assert subList[0]["ConfigType"] == "BfdRouterConfig"
    assert subList[0]["ResultType"] == "BfdRouterResults"
    assert subList[0]["ViewAttributeList"] == "TimeoutCount"
    assert subList[1]["ConfigType"] == "BfdRouterConfig"
    assert subList[1]["ResultType"] == "BfdRouterResults"
    assert subList[1]["ViewAttributeList"] == "RxCount"

    CObjectRefStore.Release(OBJ_KEY)


def test_VerifySecondInvoke(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)

    projHnd = CStcSystem.Instance().GetObject("project").GetObjectHandle()
    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        cmd.Set('PollingInterval', 1)
        cmd.SetCollection('ResultParent', [projHnd])
        cmd.Set('ValueIdleTimeout', 100)
        cmd.Set('PropertyList', "BfdRouterConfig.BfdRouterResults.TimeoutCount"
                                " BfdRouterConfig.BfdRouterResults.RxCount")
        cmd.Execute()

    assert CObjectRefStore.Exists(OBJ_KEY)
    persObj = CObjectRefStore.Get(OBJ_KEY)
    assert 'Subscription' in persObj
    subList = persObj['Subscription']
    # Exactly 2 entry found
    assert 2 == len(subList)
    # Check fields
    assert 100 == subList[0]['ValueIdleTimeout']
    assert False == subList[0]['EnableCondition']
    assert (subList[0]['Terminal'] is None) or (len(subList[0]['Terminal']) == 0)

    with AutoCommand('spirent.methodology.sampling.SetupSubscriptionCommand') as cmd:
        cmd.Set('PollingInterval', 1)
        cmd.SetCollection('ResultParent', [projHnd])
        cmd.Set('ValueIdleTimeout', 101)
        cmd.Set('PropertyList', "BgpRouterConfig.BgpRouterResults.TxAdvertisedRouteCount"
                                " BgpRouterConfig.BgpRouterResults.RxAdvertisedRouteCount")
        cmd.Execute()
    assert 'Subscription' in persObj

    # Exactly 4 entry found
    assert 4 == len(subList)
    # Check fields
    assert 100 == subList[0]['ValueIdleTimeout']
    assert 100 == subList[1]['ValueIdleTimeout']
    assert 101 == subList[2]['ValueIdleTimeout']
    assert 101 == subList[3]['ValueIdleTimeout']

    assert subList[0]["ConfigType"] == "BfdRouterConfig"
    assert subList[0]["ResultType"] == "BfdRouterResults"
    assert subList[0]["ViewAttributeList"] == "TimeoutCount"
    assert subList[1]["ConfigType"] == "BfdRouterConfig"
    assert subList[1]["ResultType"] == "BfdRouterResults"
    assert subList[1]["ViewAttributeList"] == "RxCount"
    assert subList[2]["ConfigType"] == "BgpRouterConfig"
    assert subList[2]["ResultType"] == "BgpRouterResults"
    assert subList[2]["ViewAttributeList"] == "TxAdvertisedRouteCount"
    assert subList[3]["ConfigType"] == "BgpRouterConfig"
    assert subList[3]["ResultType"] == "BgpRouterResults"
    assert subList[3]["ViewAttributeList"] == "RxAdvertisedRouteCount"

    # Clean up
    CObjectRefStore.Release(OBJ_KEY)
