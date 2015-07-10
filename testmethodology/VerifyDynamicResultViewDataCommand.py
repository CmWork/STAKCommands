from StcIntPythonPL import *
import spirent.methodology.results.drv_utils as drv_utils
import traceback
import spirent.methodology.results.ProviderUtils as pu
from spirent.methodology.results.ProviderConst import ProviderConst as pc
import spirent.methodology.results.ProviderDataGenerator as p


vdrvc_object = None


def validate(ApplyVerdictToSummary, DynamicResultViewName, OperationType,
             ResultCount, MinResultCount, MaxResultCount, ReportGroup, DisplayName,
             PassedVerdictExplanation, FailedVerdictExplanation):
    """Validate drv is available. """
    global vdrvc_object
    vdrvc_object = None
    project = CStcSystem.Instance().GetObject("project")
    drvs = project.GetObjects("DynamicResultView")
    for drv in drvs:
        if drv.Get("Name").lower() == DynamicResultViewName.lower():
            vdrvc_object = drv
            break

    if vdrvc_object is None:
        return 'Unable to find Dynamic result view from name:' + DynamicResultViewName
    return ''


def run(ApplyVerdictToSummary, DynamicResultViewName, OperationType,
        ResultCount, MinResultCount, MaxResultCount, ReportGroup, DisplayName,
        PassedVerdictExplanation, FailedVerdictExplanation):
    logger = PLLogger.GetLogger('methodology')
    global vdrvc_object
    try:
        drv = vdrvc_object
        # subscribe or refresh
        if drv_utils.subscribe(drv) is False:
            drv_utils.refresh(drv)

        # get verdict and text
        verdict_data = pu.get_comparision_verdict_with_text(OperationType,
                                                            drv.Get('ResultCount'),
                                                            ResultCount,
                                                            0,
                                                            0,
                                                            'result count')

        # generate drill down data
        prq = drv.GetObject('PresentationResultQuery')
        col_names = prq.GetCollection('SelectProperties')
        col_display_names = drv_utils.get_column_display_names(drv, col_names)

        active_groupby = drv_utils.get_active_groupby(drv)
        active_view_data = drv_utils.get_drilldown_data(drv,
                                                        active_groupby,
                                                        col_names,
                                                        col_display_names,
                                                        False)

        group_order_list = drv_utils.get_export_groupby_ordered(col_names, False)
        viewdata = []
        for groupbyKey in reversed(group_order_list):
            if active_groupby == groupbyKey:
                viewdata.append(active_view_data)
            else:
                viewdata.append(drv_utils.get_drilldown_data(drv,
                                                             groupbyKey,
                                                             col_names,
                                                             col_display_names,
                                                             True))

        drilldown_data = drv_utils.get_formatted_drilldown_data(viewdata)
        provider_data = p.get_table_drv_drilldown_data(DynamicResultViewName,
                                                       verdict_data[pc.VERDICT],
                                                       verdict_data[pc.VERDICT_TEXT],
                                                       ApplyVerdictToSummary,
                                                       drilldown_data,
                                                       ReportGroup,
                                                       DisplayName,
                                                       PassedVerdictExplanation,
                                                       FailedVerdictExplanation)
        p.submit_provider_data(provider_data)
        # revert drv config changes
        drv_utils.set_groupby(drv, active_groupby)
        drv_utils.refresh(drv)

    except Exception, e:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error(DisplayName,
                                         str(e),
                                         stack_trace)
        return False
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error(DisplayName,
                                         pc.UNKNOWN_EXCEPTION_MESSAGE,
                                         stack_trace)

        return False
    return True


def reset():
    global vdrvc_object
    vdrvc_object = None
    return True
