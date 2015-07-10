from StcIntPythonPL import *
import traceback
import spirent.methodology.results.SqliteUtils as sql_utils
import spirent.methodology.results.ProviderDataGenerator as p
import spirent.methodology.results.ProviderUtils as pu
from spirent.methodology.results.ProviderConst import ProviderConst as pc


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(SqlQuery, OperationType, RowCount, MinRowCount,
             MaxRowCount, ApplyVerdictToSummary,
             UseMultipleResultsDatabases, ReportGroup, UseSummary, DisplayName,
             PassedVerdictExplanation, FailedVerdictExplanation):

    if not SqlQuery:
        return 'Empty SqlQuery property is not allowed.'
    return ''


def run(SqlQuery, OperationType, RowCount, MinRowCount,
        MaxRowCount, ApplyVerdictToSummary,
        UseMultipleResultsDatabases, ReportGroup, UseSummary, DisplayName,
        PassedVerdictExplanation, FailedVerdictExplanation):
    logger = PLLogger.GetLogger('methodology')
    try:
        if UseSummary and not UseMultipleResultsDatabases:
            db_list = [get_active_results_db()]
        else:
            db_list = pu.get_db_files(get_active_results_db(), UseMultipleResultsDatabases)
        row_data = sql_utils.get_all_data(db_list, SqlQuery)
        verdict_data = pu.get_comparision_verdict_with_text(OperationType,
                                                            len(row_data[pc.ROW]),
                                                            RowCount,
                                                            MinRowCount,
                                                            MaxRowCount,
                                                            'row count')
        result_data = p.get_table_db_query_data(SqlQuery,
                                                verdict_data[pc.VERDICT],
                                                verdict_data[pc.VERDICT_TEXT],
                                                ApplyVerdictToSummary,
                                                row_data[pc.COLUMN_DISPLAY_NAMES],
                                                row_data[pc.ROW],
                                                ReportGroup,
                                                DisplayName,
                                                PassedVerdictExplanation,
                                                FailedVerdictExplanation)
        p.submit_provider_data(result_data)
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


def get_active_results_db():
    # Seperated into its own proc for unit testing
    return pu.get_active_result_db_filename()


def reset():
    return True
