from StcIntPythonPL import *
import spirent.methodology.results.drv_utils as drv_utils
import traceback
import spirent.methodology.results.ProviderDataGenerator as p


edrvd_object_list = []


def validate(ApplyVerdictToSummary, ExportDisabledAutoGroupData,
             DynamicResultViewNameList, ReportGroup, DisplayNameList):
    """ Validate that all input Drvs are available.
    todo- Add a way to take template view names from user and subscribe.
    """
    global edrvd_object_list
    if not DynamicResultViewNameList:
        return 'No dynamic result view provided.'

    del edrvd_object_list[:]
    project = CStcSystem.Instance().GetObject("project")
    drvs = project.GetObjects("DynamicResultView")
    availableDrvList = []
    unavailableDrvList = []
    for drv in drvs:
        drvName = drv.Get("Name").lower()
        if drvName in (userdrv.lower() for userdrv in DynamicResultViewNameList):
            edrvd_object_list.append(drv)
            availableDrvList.append(drvName)

    for drvName in DynamicResultViewNameList:
        if drvName.lower() not in availableDrvList:
            unavailableDrvList.append(drvName)
    if unavailableDrvList:
        return 'Unable to find dynamic result views from name:' + ",".join(unavailableDrvList)
    return ''


def run(ApplyVerdictToSummary, ExportDisabledAutoGroupData,
        DynamicResultViewNameList, ReportGroup, DisplayNameList):
    global edrvd_object_list
    logger = PLLogger.GetLogger('methodology')
    count = 0
    try:
        for drv in edrvd_object_list:
            display_name = ""
            if len(DisplayNameList) > count:
                display_name = DisplayNameList[count]
                count += 1
            active_groupby = drv_utils.get_active_groupby(drv)
            prq = drv.GetObject('PresentationResultQuery')
            col_names = prq.GetCollection('SelectProperties')
            col_display_names = drv_utils.get_column_display_names(drv, col_names)
            group_order_list = drv_utils.get_export_groupby_ordered(col_names,
                                                                    ExportDisabledAutoGroupData)
            viewdata = []
            for groupbyKey in reversed(group_order_list):
                viewdata.append(drv_utils.get_drilldown_data(drv,
                                                             groupbyKey,
                                                             col_names,
                                                             col_display_names,
                                                             True))
            # format and submit
            drilldown_data = drv_utils.get_formatted_drilldown_data(viewdata)
            provider_data = p.get_table_drv_complete_verdict_data(drv.Get("Name"),
                                                                  drilldown_data,
                                                                  ReportGroup,
                                                                  display_name)
            p.submit_provider_data(provider_data)
            # revert drv config changes
            drv_utils.set_groupby(drv, active_groupby)
            drv_utils.refresh(drv)

    except Exception, e:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error('ExportDynamicResultViewDataCommand',
                                         str(e),
                                         stack_trace)
        return False
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error('ExportDynamicResultViewDataCommand',
                                         pc.UNKNOWN_EXCEPTION_MESSAGE,
                                         stack_trace)

        return False
    return True


def reset():
    global edrvd_object_list
    del edrvd_object_list[:]
    return True
