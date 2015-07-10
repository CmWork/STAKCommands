from StcIntPythonPL import *
import traceback
import spirent.methodology.results.SqliteUtils as sql_utils
import spirent.methodology.results.ProviderDataGenerator as p
import spirent.methodology.results.ProviderUtils as pu
from spirent.methodology.results.ProviderConst import ProviderConst as pc


def validate(SqlQueryList, ApplyVerdictToSummary, UseMultipleResultsDatabases,
             ReportGroup, DisplayNameList, PassedVerdictExplanationList,
             FailedVerdictExplanationList, UseSummary):

    if not SqlQueryList:
        return 'Empty SqlQueryList property is not allowed.'
    for query in SqlQueryList:
        if not query:
            return 'Empty query is not allowed.'
    return ''


def run(SqlQueryList, ApplyVerdictToSummary, UseMultipleResultsDatabases,
        ReportGroup, DisplayNameList, PassedVerdictExplanationList,
        FailedVerdictExplanationList, UseSummary):
    logger = PLLogger.GetLogger('methodology')
    count = 0
    try:
        # define operator and expected values
        operation = 'EQUAL'
        expected_row_count = 0
        if UseSummary and not UseMultipleResultsDatabases:
            db_list = [get_active_results_db()]
        else:
            db_list = pu.get_db_files(get_active_results_db(), UseMultipleResultsDatabases)
        for query in SqlQueryList:
            display_name = ""
            pass_text = ""
            fail_text = ""
            if len(DisplayNameList) > count:
                display_name = DisplayNameList[count]
            if len(PassedVerdictExplanationList) > count:
                pass_text = PassedVerdictExplanationList[count]
            if len(FailedVerdictExplanationList) > count:
                fail_text = FailedVerdictExplanationList[count]
            count += 1
            row_data = sql_utils.get_all_data(db_list, query)
            verdict_data = pu.get_comparision_verdict_with_text(operation,
                                                                len(row_data[pc.ROW]),
                                                                expected_row_count,
                                                                0,
                                                                0,
                                                                'row count')
            result_data = p.get_table_db_query_data(query,
                                                    verdict_data[pc.VERDICT],
                                                    verdict_data[pc.VERDICT_TEXT],
                                                    ApplyVerdictToSummary,
                                                    row_data[pc.COLUMN_DISPLAY_NAMES],
                                                    row_data[pc.ROW],
                                                    ReportGroup,
                                                    display_name,
                                                    pass_text,
                                                    fail_text)
            p.submit_provider_data(result_data)
    except Exception, e:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error('VerifyMultipleDbQueryCommand',
                                         str(e),
                                         stack_trace)
        return False
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        p.submit_command_execution_error('VerifyMultipleDbQueryCommand',
                                         pc.UNKNOWN_EXCEPTION_MESSAGE,
                                         stack_trace)

        return False
    return True


def get_active_results_db():
    # Seperated into its own proc for unit testing
    return pu.get_active_result_db_filename()


def reset():
    return True