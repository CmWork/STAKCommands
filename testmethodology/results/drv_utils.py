from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.results.ProviderConst import ProviderConst as pc
from spirent.methodology.results.ResultEnum import (
    EnumDataFormat,
    EnumDataClass
    )

drv_drilldown_ordered_properties = ['Project.Name',
                                    'Port.Name',
                                    'StreamBlock.Name',
                                    pc.NO_GROUP_BY,
                                    pc.DISABLED_AUTO_GROUP]


def subscribe(drv):
    if drv.Get('resultstate') == 'SUBSCRIBED':
        return False

    with AutoCommand('SubscribeDynamicResultViewCommand') as cmd:
        cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
        cmd.Execute()
    return True


def refresh(drv):
    if drv.Get('resultstate') != 'SUBSCRIBED':
        return subscribe(drv)

    with AutoCommand('UpdateDynamicResultView') as cmd:
        cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
        cmd.Execute()
    return True


def get_results_from_drv(drv, max_result_per_row):
    """ Return a list of list
    Get all first level resultviewdata objects and return.
    """
    results = []
    prq = drv.GetObject('PresentationResultQuery')
    rds = prq.GetObjects('resultviewdata', RelationType('ParentChild'))
    for rd in rds:
        result_data = rd.GetCollection('ResultData')
        # remove extra drv keys not subscribed by user.
        if len(result_data) > max_result_per_row:
            del result_data[max_result_per_row:]
        results.append(result_data)
    return results


def get_export_groupby_ordered(columnNames, addAutoGroupDisabled):
    """Return groupby order as per Drv RSA
    todo - find a way to do this using bll command to support all drv results.
    """
    groupbyKeys = []
    for groupby in drv_drilldown_ordered_properties:
        if groupby in columnNames:
            groupbyKeys.append(groupby)
    if addAutoGroupDisabled is True:
        groupbyKeys.append(pc.DISABLED_AUTO_GROUP)
    return groupbyKeys


def get_active_groupby(drv):
    prq = drv.GetObject('PresentationResultQuery')
    if prq.Get('DisableAutoGrouping') is True:
        return pc.DISABLED_AUTO_GROUP
    grpByNames = prq.GetCollection('GroupByProperties')
    if not grpByNames:
        return pc.NO_GROUP_BY
    for grpKey in drv_drilldown_ordered_properties:
        if grpKey in grpByNames:
            return grpKey
    return pc.NO_GROUP_BY


def set_groupby(drv, groupbyKey):
    prq = drv.GetObject('PresentationResultQuery')
    if groupbyKey == pc.DISABLED_AUTO_GROUP:
        prq.SetCollection('GroupByProperties', [])
        prq.Set('DisableAutoGrouping', str(True))
    else:
        prq.Set('DisableAutoGrouping', str(False))
        if groupbyKey == pc.NO_GROUP_BY:
            prq.SetCollection('GroupByProperties', [])
        else:
            prq.SetCollection('GroupByProperties', [groupbyKey])


def get_column_display_names(drv, columnNames=[]):
    displayNames = []
    if not columnNames:
        prq = drv.GetObject('PresentationResultQuery')
        columnNames = prq.GetCollection('SelectProperties')

    with AutoCommand('GetDrvPropertyDisplayNameCommand') as cmd:
        cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
        cmd.SetCollection('PropertyNameList', columnNames)
        cmd.Execute()
        displayNames = cmd.GetCollection('DisplayNameList')

    return displayNames


def get_drilldown_data(drv, groupbyKey, columnNames, columnDisplayNames, doRefresh=True):
    """Return drv result as dictionary.
    todo- Drv does not support group by changes and query same results.
    Add support in Drv framework so no need to refresh results for each groupby key.
    """
    if doRefresh:
        set_groupby(drv, groupbyKey)
        refresh(drv)
    data = {}
    # data[pc.RESULT_COUNT] = drv.Get('ResultCount')
    data[pc.SUMMARIZATION_OBJECT] = groupbyKey
    # skip column names until needed.
    # data[pc.COLUMN_NAMES] = columnNames
    data[pc.COLUMN_DISPLAY_NAMES] = columnDisplayNames
    tempdata = get_results_from_drv(drv, len(columnDisplayNames))
    data[pc.ROW] = tempdata
    return data


def get_formatted_drilldown_data(data_objects):
    """Return output data dictionary as per drill down schema.
    """
    currentdata = None
    for drilldowndata in data_objects:
        # format data first
        data = {}
        data[pc.CLASS] = EnumDataClass.drill_down_results
        data[pc.DATA_FORMAT] = EnumDataFormat.table
        data[pc.INFO] = {}
        data[pc.INFO][pc.SUMMARIZATION_OBJECT] = drilldowndata[pc.SUMMARIZATION_OBJECT]
        data[pc.DATA] = {}
        data[pc.DATA][pc.COLUMN_DISPLAY_NAMES] = drilldowndata[pc.COLUMN_DISPLAY_NAMES]
        data[pc.DATA][pc.ROW] = drilldowndata[pc.ROW]
        if currentdata is not None:
            links = []
            linkdata = {}
            linkdata[pc.TAG] = currentdata[pc.INFO][pc.SUMMARIZATION_OBJECT]
            linkdata[pc.LINK_DATA] = currentdata
            links.append(linkdata)
            data[pc.DATA][pc.LINKS] = links
        currentdata = data

    return currentdata
