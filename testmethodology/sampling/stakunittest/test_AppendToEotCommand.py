from StcIntPythonPL import *
import sqlite3
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.sampling.AppendToEotCommand import get_db_filename


OBJ_KEY = 'spirent.methodology.sampling'


def test_ValidateError(stc):
    failed = False
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        try:
            cmd.Set('EventTableName', '')
            cmd.Execute()
        except RuntimeError as e:
            if 'must be set' in str(e):
                failed = True
        if not failed:
            raise AssertionError('AppendToEotCommand did not fail on blank event table name')
        cmd.Reset()
        try:
            cmd.Set('EventTableName', 'Methodology_SamplingEvent')
            cmd.Set('DataTableName', '')
            cmd.Execute()
        except RuntimeError as e:
            if 'must be set' in str(e):
                failed = True
        if not failed:
            raise AssertionError('AppendToEotCommand did not fail on blank data table name')


def test_NoStoredData(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    failed = False
    # Object should not exist
    with AutoCommand('SaveResultsCommand') as cmd:
        cmd.Set('SaveDetailedResults', True)
        cmd.Set('ResultFileName', 'AppendUnitTest.db')
        cmd.Execute()
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        try:
            cmd.Execute()
        except RuntimeError as e:
            if 'not properly initialized' in str(e):
                failed = True
        if not failed:
            raise AssertionError('AppendToEotCommand did not fail as ' +
                                 'expected on missing persistent data')


def test_ErrorNoSave(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    failed = False
    fail_message = ""
    pers_obj = {}

    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        try:
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'No results have been saved' in fail_message:
                failed = True
        if not failed:
            raise AssertionError('AppendToEotCommand failed with ' +
                                 'unexpected error: "' + fail_message + '"')
    # Confirm the command cleaned up
    assert not CObjectRefStore.Exists(OBJ_KEY)


def test_CreateEventTable(stc):
    if CObjectRefStore.Exists(OBJ_KEY):
        CObjectRefStore.Release(OBJ_KEY)
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    # Pre-canned event table data
    pers_obj['Event'] = [('DeviceStart', 0, 1111), ('DeviceStop', 0, 2222),
                         ('DeviceStart', 1, 3333)]
    with AutoCommand('SaveResultsCommand') as cmd:
        cmd.Set('SaveDetailedResults', True)
        cmd.Set('ResultFileName', 'AppendUnitTest.db')
        cmd.Execute()
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists(OBJ_KEY)
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()
    db_curs.execute('''SELECT * FROM Methodology_SamplingEvent''')
    evList = db_curs.fetchall()
    # 3 entries
    assert 3 == len(evList)
    assert 'DeviceStart' == evList[0][1]
    assert 0 == evList[0][2]
    assert 'DeviceStop' == evList[1][1]
    assert 0 == evList[1][2]
    # The second DeviceStart should have 2nd tuple element as 1
    assert 'DeviceStart' == evList[2][1]
    assert 1 == evList[2][2]
    db_conn.close()


def get_child_handle_set(parent, child_type):
    result = set()
    for obj in parent.GetObjects(child_type):
        result.add(obj.GetObjectHandle())
    return result


def test_CreateDataTable(stc):
    hnd_reg = CHandleRegistry.Instance()
    project = CStcSystem.Instance().GetObject('project')
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    view_attr_list = 'rxadvertisedroutecount txadvertisedroutecount'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [project.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList', view_attr_list)
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    found = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            found = obj
            break
    assert found
    ds_hdl = found.GetObjectHandle()
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    sub = {'ResultDatasetHandle': ds_hdl, 'Data': []}
    dataList = sub['Data']
    dataList.append((1234, 11111, 15, 25))
    dataList.append((1234, 22222, 30, 15))
    dataList.append((1234, 33333, 40, 50))
    sub["ConfigType"] = cfg_class
    sub["ResultType"] = res_class
    sub["ViewAttributeList"] = view_attr_list
    pers_obj['Subscription'] = [sub]
    with AutoCommand('SaveResultsCommand') as cmd:
        cmd.Set('SaveDetailedResults', True)
        cmd.Set('ResultFileName', 'AppendUnitTest.db')
        cmd.Execute()
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists(OBJ_KEY)
    # Validate dataset is removed
    ds_obj = hnd_reg.Find(ds_hdl)
    assert ds_obj is None or ds_obj.IsDeleted()
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()
    # Verify field names
    db_curs.execute('''PRAGMA table_info(Methodology_SamplingData)''')
    infoList = db_curs.fetchall()
    # 5 columns
    assert 5 == len(infoList)
    assert 'DataSetId' == infoList[0][1]
    assert 'SubscriptionHandle' == infoList[1][1]
    assert 'Timestamp' == infoList[2][1]
    assert 'BgpRouterResults_RxAdvertisedRouteCount' == infoList[3][1]
    assert 'BgpRouterResults_TxAdvertisedRouteCount' == infoList[4][1]

    db_curs.execute('''SELECT * FROM Methodology_SamplingData''')
    evList = db_curs.fetchall()
    # 3 entries
    assert 3 == len(evList)
    # Check timestamps
    assert 11111 == evList[0][2]
    assert 22222 == evList[1][2]
    assert 33333 == evList[2][2]
    # Check values
    assert (15, 25) == evList[0][3:5]
    assert (30, 15) == evList[1][3:5]
    assert (40, 50) == evList[2][3:5]
    db_conn.close()


def test_write_data_table_abst_base_class(stc):
    hnd_reg = CHandleRegistry.Instance()
    project = CStcSystem.Instance().GetObject("Project")
    cur_set = get_child_handle_set(project, "ResultDataSet")

    plLogger = PLLogger.GetLogger("test_write_data_table_abst_base_class")
    cfg_class = "project"
    res_class = "ospfv2statesummary"
    view_attr_list = "RouterUpCount RouterDownCount"
    with AutoCommand("ResultsSubscribeCommand") as cmd:
        cmd.Set("Parent", project.GetObjectHandle())
        cmd.SetCollection("ResultParent", [project.GetObjectHandle()])
        cmd.Set("ConfigType", cfg_class)
        cmd.Set("ResultType", res_class)
        cmd.Set("ViewAttributeList", view_attr_list)
        cmd.Set("Interval", 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, "ResultDataSet")
    created_set = new_set - cur_set
    found = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject("ResultQuery")
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get("ConfigClassId"), query.Get("ResultClassId"))
        plLogger.LogInfo("query_pair: " + str(query_pair))
        if res_pair == query_pair:
            found = obj
            break
    assert found
    ds_hdl = found.GetObjectHandle()
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    sub = {"ResultDatasetHandle": ds_hdl, "Data": []}
    dataList = sub["Data"]
    dataList.append((1234, 11111, 15, 25))
    dataList.append((1234, 22222, 30, 15))
    dataList.append((1234, 33333, 40, 50))
    sub["ConfigType"] = cfg_class
    sub["ResultType"] = res_class
    sub["ViewAttributeList"] = view_attr_list
    pers_obj["Subscription"] = [sub]
    with AutoCommand("SaveResultsCommand") as cmd:
        cmd.Set("SaveDetailedResults", True)
        cmd.Set("ResultFileName", "AppendUnitTest.db")
        cmd.Execute()
    with AutoCommand("spirent.methodology.sampling.AppendToEotCommand") as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists(OBJ_KEY)

    # Validate dataset is removed
    ds_obj = hnd_reg.Find(ds_hdl)
    assert ds_obj is None or ds_obj.IsDeleted()
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()

    # Verify field names
    db_curs.execute("""PRAGMA table_info(Methodology_SamplingData)""")
    infoList = db_curs.fetchall()

    # 5 columns
    assert 5 == len(infoList)
    plLogger.LogInfo("infoList: " + str(infoList))
    assert "DataSetId" == infoList[0][1]
    assert "SubscriptionHandle" == infoList[1][1]
    assert "Timestamp" == infoList[2][1]
    assert "Ospfv2StateSummary_RouterUpCount" == infoList[3][1]
    assert "Ospfv2StateSummary_RouterDownCount" == infoList[4][1]

    db_curs.execute("""SELECT * FROM Methodology_SamplingData""")
    evList = db_curs.fetchall()
    plLogger.LogInfo("evList: " + str(evList))

    # 3 entries
    assert 3 == len(evList)

    # Check timestamps
    assert 11111 == evList[0][2]
    assert 22222 == evList[1][2]
    assert 33333 == evList[2][2]

    # Check values
    assert (15, 25) == evList[0][3:5]
    assert (30, 15) == evList[1][3:5]
    assert (40, 50) == evList[2][3:5]
    db_conn.close()


def test_MultiSubscription(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    project = CStcSystem.Instance().GetObject('project')
    port1 = ctor.Create('port', project)
    port2 = ctor.Create('port', project)

    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [port1.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'rxadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    ds1 = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            ds1 = obj
            break
    assert ds1
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [port2.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'txadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    ds2 = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            ds2 = obj
            break
    assert ds2
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    sub1 = {'ResultDatasetHandle': ds1.GetObjectHandle(), 'Data': []}
    # Each subscription only has one value
    dataList = sub1['Data']
    dataList.append((1234, 11111, 15))
    dataList.append((1234, 22222, 30))
    sub1["ConfigType"] = "BgpRouterConfig"
    sub1["ResultType"] = "BgpRouterResults"
    sub1["ViewAttributeList"] = "RxAdvertisedRouteCount"
    sub2 = {'ResultDatasetHandle': ds2.GetObjectHandle(), 'Data': []}
    dataList = sub2['Data']
    dataList.append((4321, 11151, 30))
    dataList.append((4321, 22252, 15))
    sub2["ConfigType"] = "BgpRouterConfig"
    sub2["ResultType"] = "BgpRouterResults"
    sub2["ViewAttributeList"] = "TxAdvertisedRouteCount"
    pers_obj['Subscription'] = [sub1, sub2]
    with AutoCommand('SaveResultsCommand') as cmd:
        cmd.Set('SaveDetailedResults', True)
        cmd.Set('ResultFileName', 'AppendUnitTest.db')
        cmd.Execute()
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists(OBJ_KEY)
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()
    # Verify field names
    db_curs.execute('''PRAGMA table_info(Methodology_SamplingData)''')
    infoList = db_curs.fetchall()
    # 5 columns
    assert 5 == len(infoList)
    assert 'DataSetId' == infoList[0][1]
    assert 'SubscriptionHandle' == infoList[1][1]
    assert 'Timestamp' == infoList[2][1]
    assert 'BgpRouterResults_RxAdvertisedRouteCount' == infoList[3][1]
    assert 'BgpRouterResults_TxAdvertisedRouteCount' == infoList[4][1]

    db_curs.execute('''SELECT * FROM Methodology_SamplingData''')
    evList = db_curs.fetchall()
    # 4 entries
    assert 4 == len(evList)
    # Check timestamps
    assert 11111 == evList[0][2]
    assert 22222 == evList[1][2]
    assert 11151 == evList[2][2]
    assert 22252 == evList[3][2]
    # Check values
    assert (15, None) == evList[0][3:5]
    assert (30, None) == evList[1][3:5]
    assert (None, 30) == evList[2][3:5]
    assert (None, 15) == evList[3][3:5]
    db_conn.close()


def test_MultiResultType(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    project = CStcSystem.Instance().GetObject('project')
    port1 = ctor.Create('port', project)
    port2 = ctor.Create('port', project)

    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bgprouterconfig'
    res_class = 'bgprouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [port1.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList',
                'rxadvertisedroutecount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    ds1 = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            ds1 = obj
            break
    assert ds1
    cur_set = get_child_handle_set(project, 'ResultDataSet')
    cfg_class = 'bfdrouterconfig'
    res_class = 'bfdrouterresults'
    with AutoCommand('ResultsSubscribeCommand') as cmd:
        cmd.Set('Parent', project.GetObjectHandle())
        cmd.SetCollection('ResultParent', [port2.GetObjectHandle()])
        cmd.Set('ConfigType', cfg_class)
        cmd.Set('ResultType', res_class)
        cmd.Set('ViewAttributeList', 'txcount')
        cmd.Set('Interval', 1)
        cmd.Execute()
    new_set = get_child_handle_set(project, 'ResultDataSet')
    created_set = new_set - cur_set
    ds2 = None
    for hnd in created_set:
        obj = hnd_reg.Find(hnd)
        query = obj.GetObject('ResultQuery')
        res_pair = (cfg_class, res_class)
        query_pair = (query.Get('ConfigClassId'), query.Get('ResultClassId'))
        if res_pair == query_pair:
            ds2 = obj
            break
    assert ds2
    pers_obj = {}
    CObjectRefStore.Put(OBJ_KEY, pers_obj)
    sub1 = {'ResultDatasetHandle': ds1.GetObjectHandle(), 'Data': []}
    # Each subscription only has one value
    dataList = sub1['Data']
    dataList.append((1234, 11111, 15))
    dataList.append((1234, 22222, 30))
    sub1["ConfigType"] = "BgpRouterConfig"
    sub1["ResultType"] = "BgpRouterResults"
    sub1["ViewAttributeList"] = "RxAdvertisedRouteCount"
    sub2 = {'ResultDatasetHandle': ds2.GetObjectHandle(), 'Data': []}
    dataList = sub2['Data']
    dataList.append((4321, 11151, 30))
    dataList.append((4321, 22252, 15))
    sub2["ConfigType"] = "BfdRouterConfig"
    sub2["ResultType"] = "BfdRouterResults"
    sub2["ViewAttributeList"] = "TxCount"
    pers_obj['Subscription'] = [sub1, sub2]
    with AutoCommand('SaveResultsCommand') as cmd:
        cmd.Set('SaveDetailedResults', True)
        cmd.Set('ResultFileName', 'AppendUnitTest.db')
        cmd.Execute()
    with AutoCommand('spirent.methodology.sampling.AppendToEotCommand') as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists(OBJ_KEY)
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()
    # Verify field names
    db_curs.execute('''PRAGMA table_info(Methodology_SamplingData)''')
    infoList = db_curs.fetchall()
    # 5 columns
    assert 5 == len(infoList)
    assert 'DataSetId' == infoList[0][1]
    assert 'SubscriptionHandle' == infoList[1][1]
    assert 'Timestamp' == infoList[2][1]
    assert 'BgpRouterResults_RxAdvertisedRouteCount' == infoList[3][1]
    assert 'BfdRouterResults_TxCount' == infoList[4][1]

    db_curs.execute('''SELECT * FROM Methodology_SamplingData''')
    evList = db_curs.fetchall()
    # 4 entries
    assert 4 == len(evList)
    # Check timestamps
    assert 11111 == evList[0][2]
    assert 22222 == evList[1][2]
    assert 11151 == evList[2][2]
    assert 22252 == evList[3][2]
    # Check values
    assert (15, None) == evList[0][3:5]
    assert (30, None) == evList[1][3:5]
    assert (None, 30) == evList[2][3:5]
    assert (None, 15) == evList[3][3:5]
    db_conn.close()
