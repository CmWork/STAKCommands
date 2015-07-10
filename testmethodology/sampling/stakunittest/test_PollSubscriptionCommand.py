from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


OBJ_KEY = 'spirent.methodology.sampling'


def test_ValidatePollingPeriod(stc):
    fail_message = ""
    got_failure = False
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        try:
            cmd.Set('PollingPeriod', 0)
            # Won't even get to execute -- system should prevent setting value
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'CStcInvalidArgument' in fail_message:
                got_failure = True
    if not got_failure:
        raise AssertionError('Setting Polling Period to 0 failed with ' +
                             'unexpected error "' + fail_message + '"')


def test_NoPersistObject(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    got_failure = False
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        try:
            cmd.Execute()
        except RuntimeError as e:
            # FIXME: Get correct error message from finalized command
            if 'not properly initialized' in str(e):
                got_failure = True
    if not got_failure:
        raise AssertionError('PollSubscriptionCommand did not fail as expected')


def test_MissingContent(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    got_failure = False
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        try:
            cmd.Execute()
        except RuntimeError as e:
            if 'missing subscription' in str(e):
                got_failure = True
    if not got_failure:
        raise AssertionError('PollSubscriptionCommand did not fail as expected')


# Retrieve all handles from a given parent STC Object
def get_child_handle_set(parent, child_type):
    result = set()
    for obj in parent.GetObjects(child_type):
        result.add(obj.GetObjectHandle())
    return result


# Basic test to verify that the polling works, does not exercise condition
def test_ResultRetrieval(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('port', project)
    ret_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 1)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()
        ret_list = cmd.GetCollection('ReturnList')
    assert 1 == len(ret_list)
    dev = hnd_reg.Find(ret_list[0])
    bgp = ctor.Create('BgpRouterConfig', dev)
    # Create the bgp result object (an IL message normally does this)
    bgp_res = ctor.Create('BgpRouterResults', bgp)
    bgp.AddObject(bgp_res, RelationType('ResultChild'))
    assert bgp_res is not None
    with AutoCommand('ApplyToILCommand') as cmd:
        cmd.Execute()
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [project.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'rxadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    dataset = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            dataset = obj
            break
    assert dataset
    # Set up subscriptions for persistent object
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    pers_obj['Subscription'] = []
    subs = {'ResultDatasetHandle': dataset.GetObjectHandle(),
            'ValueIdleTimeout': 10,
            'EnableCondition': False,
            'ResultParent': [project.GetObjectHandle()],
            'Data': []}
    pers_obj['Subscription'].append(subs)
    data = subs['Data']
    val_list = [10, 20, 25, 30, 35]
    utest_data = [(bgp_res.GetObjectHandle(), 'rxadvertisedroutecount',
                   val_list), ]
    pers_obj['UnitTest'] = utest_data
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        cmd.Set('PollingPeriod', 5)
        cmd.Execute()

    # At this point, check contents of data
    got_list = [x[2] for x in data]
    # At least got the middle entry
    assert 20 in got_list or 25 in got_list
    assert got_list[0] <= got_list[1]
    assert got_list[1] <= got_list[2]
    assert got_list[2] <= got_list[3]
    assert got_list[3] <= got_list[4]
    assert got_list[0] < got_list[-1]
    # Clean up after unit test
    CObjectRefStore.Release(OBJ_KEY)


def test_TerminalCondition(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('port', project)
    ret_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 1)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()
        ret_list = cmd.GetCollection('ReturnList')
    assert 1 == len(ret_list)
    dev = hnd_reg.Find(ret_list[0])
    bgp = ctor.Create('BgpRouterConfig', dev)
    # Create the bgp result object (an IL message normally does this)
    bgp_res = ctor.Create('BgpRouterResults', bgp)
    bgp.AddObject(bgp_res, RelationType('ResultChild'))
    assert bgp_res is not None
    with AutoCommand('ApplyToILCommand') as cmd:
        cmd.Execute()
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [project.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'rxadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    dataset = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            dataset = obj
            break
    assert dataset
    # Set up subscriptions for persistent object
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    pers_obj['Subscription'] = []
    subs = {'ResultDatasetHandle': dataset.GetObjectHandle(),
            'ValueIdleTimeout': 0,
            'EnableCondition': True,
            'Terminal': 35,
            'ResultParent': [project.GetObjectHandle()],
            'Data': []}
    pers_obj['Subscription'].append(subs)
    data = subs['Data']
    val_list = [10, 20, 25, 30, 35]
    utest_data = [(bgp_res.GetObjectHandle(), 'rxadvertisedroutecount',
                   val_list), ]
    pers_obj['UnitTest'] = utest_data
    elapsed = 0.0
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        cmd.Set('PollingPeriod', 25)
        cmd.Execute()
        elapsed = cmd.Get('ElapsedTime')

    # At this point, check contents of data
    got_list = [x[2] for x in data]
    # At least got the middle entry
    assert 20 in got_list or 25 in got_list
    assert len(got_list) >= 5
    assert 35 == got_list[-1]
    # Should not be the whole period, but more than 5 (elapsed in ms)
    elapsed /= 1000.0
    assert elapsed >= 4.5 and elapsed < 8.0
    # Clean up after unit test
    CObjectRefStore.Release(OBJ_KEY)


def test_IdleCondition(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('port', project)
    ret_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 1)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()
        ret_list = cmd.GetCollection('ReturnList')
    assert 1 == len(ret_list)
    dev = hnd_reg.Find(ret_list[0])
    bgp = ctor.Create('BgpRouterConfig', dev)
    # Create the bgp result object (an IL message normally does this)
    bgp_res = ctor.Create('BgpRouterResults', bgp)
    bgp.AddObject(bgp_res, RelationType('ResultChild'))
    assert bgp_res is not None
    with AutoCommand('ApplyToILCommand') as cmd:
        cmd.Execute()
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [project.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'rxadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    dataset = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            dataset = obj
            break
    assert dataset
    # Set up subscriptions for persistent object
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    pers_obj['Subscription'] = []
    subs = {'ResultDatasetHandle': dataset.GetObjectHandle(),
            'ValueIdleTimeout': 5,
            'EnableCondition': False,
            'ResultParent': [project.GetObjectHandle()],
            'Data': []}
    pers_obj['Subscription'].append(subs)
    data = subs['Data']
    # Sample data for sampling at 0s, 1s, 2s, 3s, and 4s...
    val_list = [10, 20, 25, 30, 35]
    utest_data = [(bgp_res.GetObjectHandle(), 'rxadvertisedroutecount',
                   val_list), ]
    pers_obj['UnitTest'] = utest_data
    elapsed = 0.0
    with AutoCommand('spirent.methodology.sampling.PollSubscriptionCommand') as cmd:
        cmd.Set('PollingPeriod', 25)
        cmd.Execute()
        elapsed = cmd.Get('ElapsedTime')

    # At this point, check contents of data
    got_list = [x[2] for x in data]
    # At least got the middle entry
    assert 20 in got_list or 25 in got_list
    assert len(got_list) >= 5
    assert 35 == got_list[-1]
    # Should not be the whole period, but more than 5 (elapsed in ms)
    elapsed /= 1000.0
    # The total elapsed time should be at least 9 seconds, which is the
    # sum of sampling seconds 0 through 4, plus 5 wait during idle.
    assert elapsed >= 9.0 and elapsed < 12.0
    # Clean up after unit test
    CObjectRefStore.Release(OBJ_KEY)
