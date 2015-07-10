from StcIntPythonPL import *
import spirent.methodology.results.drv_utils as drv_utils
from spirent.methodology.results.ProviderConst import ProviderConst as pc
import spirent.methodology.results.ProviderDataGenerator as p
from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumExecStatus,
    EnumDataFormat,
    EnumDataClass
    )
import spirent.methodology.results.LogUtils as logger
import json


def test_get_export_groupby_ordered():
    testKeys = ['Port.Name', 'Project.Name', 'abc']
    expectedKeys = ['Project.Name', 'Port.Name']
    actualKeys = drv_utils.get_export_groupby_ordered(testKeys, False)
    assert actualKeys == expectedKeys
    actualKeys = drv_utils.get_export_groupby_ordered(actualKeys, True)
    expectedKeys.append(pc.DISABLED_AUTO_GROUP)
    assert actualKeys == expectedKeys


def test_get_active_groupby(stc, resource_cleanup):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    drv = ctor.Create("DynamicResultView", project)
    prq = ctor.Create("PresentationResultQuery", drv)
    prq.Set('DisableAutoGrouping', str(True))
    assert pc.DISABLED_AUTO_GROUP == drv_utils.get_active_groupby(drv)
    prq.Set('DisableAutoGrouping', str(False))
    prq.SetCollection('GroupByProperties', [])
    assert pc.NO_GROUP_BY == drv_utils.get_active_groupby(drv)
    prq.SetCollection('GroupByProperties', ['Project.Name', 'Port.Name'])
    assert 'Project.Name' == drv_utils.get_active_groupby(drv)


def test_set_active_groupby(stc, resource_cleanup):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    drv = ctor.Create("DynamicResultView", project)
    prq = ctor.Create("PresentationResultQuery", drv)
    prq.SetCollection('GroupByProperties', ['Project.Name'])
    drv_utils.set_groupby(drv, pc.DISABLED_AUTO_GROUP)
    assert prq.Get('DisableAutoGrouping') is True
    assert prq.GetCollection('GroupByProperties') == []
    prq.Set('DisableAutoGrouping', str(True))
    prq.SetCollection('GroupByProperties', ['Project.Name'])
    drv_utils.set_groupby(drv, 'Port.Name')
    assert prq.Get('DisableAutoGrouping') is False
    assert prq.GetCollection('GroupByProperties') == ['Port.Name']
    drv_utils.set_groupby(drv, pc.NO_GROUP_BY)
    assert prq.Get('DisableAutoGrouping') is False
    assert prq.GetCollection('GroupByProperties') == []


def test_get_results_from_drv(stc, resource_cleanup):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    drv = ctor.Create("DynamicResultView", project)
    prq = ctor.Create("PresentationResultQuery", drv)
    results = drv_utils.get_results_from_drv(drv, 3)
    assert len(results) == 0
    ctor.Create("ResultViewData", prq)
    ctor.Create("ResultViewData", prq)
    ctor.Create("ResultViewData", prq)
    results = drv_utils.get_results_from_drv(drv, 3)
    assert len(results) == 3


def test_get_formatted_drilldown_data_and_more():
    verdict = True
    verdictText = 'Not available'
    displayName = "My display name"
    pass_text = "my pass text"
    applyVerdictToSum = False
    viewName = 'MyTestDrv'
    displays = ['First', 'Second']
    report_group = pc.HIGHEST_PRIORITY_REPORT_GROUP
    drilldowndataObjects = []
    drilldowndata = {}
    drilldowndata[pc.SUMMARIZATION_OBJECT] = 'Port.Name'
    drilldowndata[pc.COLUMN_DISPLAY_NAMES] = displays
    resultviewdata1 = [1, 2]
    resultviewdata2 = [3, 4]
    resultviewdataList = [resultviewdata1, resultviewdata2]
    drilldowndata[pc.ROW] = resultviewdataList
    drilldowndataObjects.append(drilldowndata)

    drilldowndata = {}
    drilldowndata[pc.SUMMARIZATION_OBJECT] = 'Project.Name'
    drilldowndata[pc.COLUMN_DISPLAY_NAMES] = displays
    resultviewdata = [4, 6]
    resultviewdataList = [resultviewdata]
    drilldowndata[pc.ROW] = resultviewdataList
    drilldowndataObjects.append(drilldowndata)

    formatted_data = drv_utils.get_formatted_drilldown_data(drilldowndataObjects)

    provider_data = p.get_table_drv_drilldown_data(viewName,
                                                   verdict,
                                                   verdictText,
                                                   applyVerdictToSum,
                                                   formatted_data,
                                                   report_group,
                                                   displayName,
                                                   pass_text,
                                                   "")
    assert provider_data is not None
    info = provider_data[pc.INFO]
    status = provider_data[pc.STATUS]
    data = provider_data[pc.DATA]
    logger.info(json.dumps(provider_data, separators=(',', ':'), sort_keys=False))
    assert provider_data[pc.CLASS] == EnumDataClass.table_drv_drilldown
    assert provider_data[pc.DATA_FORMAT] == EnumDataFormat.table
    # verify info
    assert info[pc.RESULT_VIEW_NAME] == viewName
    assert info[pc.SUMMARIZATION_OBJECT] == 'Project.Name'
    assert info[pc.REPORT_GROUP] == pc.HIGHEST_PRIORITY_REPORT_GROUP
    assert info[pc.DISPLAY_NAME] == displayName
    # verify status
    assert status[pc.VERDICT] == EnumVerdict.passed
    assert status[pc.VERDICT_TEXT] == pass_text
    assert status[pc.EXEC_STATUS] == EnumExecStatus.completed
    assert status[pc.APPLY_VERDICT] == applyVerdictToSum

    assert len(data[pc.COLUMN_DISPLAY_NAMES]) == 2
    assert data[pc.COLUMN_DISPLAY_NAMES][0] == displays[0]
    assert data[pc.COLUMN_DISPLAY_NAMES][1] == displays[1]
    rows = data[pc.ROW]
    assert len(rows) == 1
    assert len(rows[0]) == 2
    assert rows[0][0] == 4
    assert rows[0][1] == 6
    assert (pc.LINKS in data) is True
    # verify drilldown results
    data = data[pc.LINKS]
    assert len(data) == 1
    data = data[0]
    data[pc.TAG] = 'Port.Name'
    assert (pc.LINK_DATA in data) is True
    data = data[pc.LINK_DATA]
    assert data[pc.CLASS] == EnumDataClass.drill_down_results
    assert data[pc.DATA_FORMAT] == EnumDataFormat.table
    assert data[pc.INFO][pc.SUMMARIZATION_OBJECT] == 'Port.Name'
    data = data[pc.DATA]
    assert len(data[pc.COLUMN_DISPLAY_NAMES]) == 2
    assert data[pc.COLUMN_DISPLAY_NAMES][0] == displays[0]
    assert data[pc.COLUMN_DISPLAY_NAMES][1] == displays[1]
    rows = data[pc.ROW]
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert rows[0][0] == 1
    assert rows[0][1] == 2
    assert rows[1][0] == 3
    assert rows[1][1] == 4
    assert (pc.LINKS in data) is False
