from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumExecStatus,
    EnumDataFormat,
    EnumDataClass
    )
from spirent.methodology.results.ProviderConst import ProviderConst
from spirent.methodology.results.ResultInterface import ResultInterface


def submit_provider_data(data):
    ResultInterface.add_provider_result(data)


def submit_provider_data_to_root(data):
    ResultInterface.add_provider_result_to_root(data)


def submit_command_execution_error(command_name,
                                   error_summary,
                                   error_details,
                                   report_group=ProviderConst.HIGHEST_PRIORITY_REPORT_GROUP):
    info = {}
    info[ProviderConst.REPORT_GROUP] = report_group
    status = {}
    status[ProviderConst.VERDICT] = EnumVerdict.failed
    status[ProviderConst.VERDICT_TEXT] = ProviderConst.CMD_EXEC_ERROR_PREFIX + command_name
    status[ProviderConst.EXEC_STATUS] = EnumExecStatus.error
    # for now apply execution failure to test.
    status[ProviderConst.APPLY_VERDICT] = True
    # data
    data = {}
    data[ProviderConst.NOTE_LABEL] = str(error_summary)
    data[ProviderConst.NOTE_TEXT] = error_details
    provider_data = {}
    provider_data[ProviderConst.CLASS] = EnumDataClass.error_summary_details
    provider_data[ProviderConst.DATA_FORMAT] = EnumDataFormat.note
    provider_data[ProviderConst.INFO] = info
    provider_data[ProviderConst.STATUS] = status
    provider_data[ProviderConst.DATA] = data
    submit_provider_data(provider_data)


def submit_sequencer_execution_error(seq_status):
    info = {}
    info[ProviderConst.REPORT_GROUP] = ProviderConst.HIGHEST_PRIORITY_REPORT_GROUP
    status = {}
    status[ProviderConst.VERDICT] = EnumVerdict.failed
    status[ProviderConst.VERDICT_TEXT] = ProviderConst.TEST_EXECUTION_ERROR
    status[ProviderConst.EXEC_STATUS] = EnumExecStatus.error
    # for now apply execution failure to test.
    status[ProviderConst.APPLY_VERDICT] = True
    # data
    data = {}
    data[ProviderConst.NOTE_LABEL] = ProviderConst.TEST_EXECUTION_ERROR
    data[ProviderConst.NOTE_TEXT] = seq_status
    provider_data = {}
    provider_data[ProviderConst.CLASS] = EnumDataClass.error_summary_details
    provider_data[ProviderConst.DATA_FORMAT] = EnumDataFormat.note
    provider_data[ProviderConst.INFO] = info
    provider_data[ProviderConst.STATUS] = status
    provider_data[ProviderConst.DATA] = data
    submit_provider_data_to_root(provider_data)


def get_table_db_query_data_advanced(verdict,
                                     verdict_text,
                                     exec_status,
                                     apply_verdict_to_summary,
                                     query,
                                     column_display_names,
                                     result_rows,
                                     report_group,
                                     cmd_display_name):
    """
    This function is intended for internal use.
    Create simple helper function if existing funtion does not
    meet user requirement.
    """
    info = {}
    info[ProviderConst.SQL_QUERY] = query
    info[ProviderConst.REPORT_GROUP] = report_group
    info[ProviderConst.DISPLAY_NAME] = cmd_display_name
    status = {}
    status[ProviderConst.VERDICT] = verdict
    status[ProviderConst.VERDICT_TEXT] = verdict_text
    status[ProviderConst.EXEC_STATUS] = exec_status
    status[ProviderConst.APPLY_VERDICT] = apply_verdict_to_summary
    # data
    data = {}
    data[ProviderConst.COLUMN_DISPLAY_NAMES] = column_display_names
    data[ProviderConst.ROW] = result_rows
    provider_data = {}
    provider_data[ProviderConst.CLASS] = EnumDataClass.table_db_query
    provider_data[ProviderConst.DATA_FORMAT] = EnumDataFormat.table
    provider_data[ProviderConst.INFO] = info
    provider_data[ProviderConst.STATUS] = status
    provider_data[ProviderConst.DATA] = data
    return provider_data


def get_table_db_query_data(query,
                            verdict,
                            verdict_explanation,
                            apply_verdict_to_summary,
                            column_display_names,
                            result_rows,
                            report_group,
                            cmd_display_name="",
                            pass_text="",
                            fail_text=""):
    """
    Simple function to generate provider data for db query type.
    query: <string> sql query run by command to generate verdict.
    verdict: <bool> verdict (It will be changed to right enum value.)
    verdict_explanation: <string> 140 character info about verdict
    apply_verdict_to_summary: <bool> should verdict apply to test verdict.
    column_names: <list> name of columns for table style results.
    result_rows: <list of list>
    return: dict data as expected by result framework.
    """
    updated_verdict = EnumVerdict.passed
    updated_verdict_text = verdict_explanation
    if pass_text:
        updated_verdict_text = pass_text
    if verdict is False:
        updated_verdict = EnumVerdict.failed
        if fail_text:
            updated_verdict_text = fail_text

    exec_status = EnumExecStatus.completed
    return get_table_db_query_data_advanced(updated_verdict, updated_verdict_text,
                                            exec_status, apply_verdict_to_summary, query,
                                            column_display_names, result_rows, report_group,
                                            cmd_display_name)


def get_table_drv_drilldown_data_advanced(verdict,
                                          verdict_text,
                                          exec_status,
                                          apply_verdict_to_summary,
                                          drv_name,
                                          drilldowndata,
                                          report_group,
                                          cmd_display_name):
    """
    This function is intended for internal use.
    Create simple helper function if existing funtion does not
    meet user requirement.
    """
    status = {}
    status[ProviderConst.VERDICT] = verdict
    status[ProviderConst.VERDICT_TEXT] = verdict_text
    status[ProviderConst.EXEC_STATUS] = exec_status
    status[ProviderConst.APPLY_VERDICT] = apply_verdict_to_summary
    provider_data = drilldowndata
    provider_data[ProviderConst.INFO][ProviderConst.REPORT_GROUP] = report_group
    provider_data[ProviderConst.INFO][ProviderConst.RESULT_VIEW_NAME] = drv_name
    provider_data[ProviderConst.INFO][ProviderConst.DISPLAY_NAME] = cmd_display_name
    provider_data[ProviderConst.STATUS] = status
    provider_data[ProviderConst.CLASS] = EnumDataClass.table_drv_drilldown
    return provider_data


def get_table_drv_drilldown_data(drv_name,
                                 verdict,
                                 verdict_explanation,
                                 apply_verdict_to_summary,
                                 drilldowndata,
                                 report_group,
                                 cmd_display_name="",
                                 pass_text="",
                                 fail_text=""):
    """
    Simple function to generate provider data for drv drilldown.
    drv_name: STC drv object name property.
    verdict: <bool> verdict (It will be changed to right enum value.)
    verdict_explanation: <string> 140 character info about verdict
    apply_verdict_to_summary: <bool> should verdict apply to test verdict.
    drilldowndata: drill down result data
    return: dict data as expected by result framework.
    """
    updated_verdict = EnumVerdict.passed
    updated_verdict_text = verdict_explanation
    if pass_text:
        updated_verdict_text = pass_text
    if verdict is False:
        updated_verdict = EnumVerdict.failed
        if fail_text:
            updated_verdict_text = fail_text

    exec_status = EnumExecStatus.completed
    return get_table_drv_drilldown_data_advanced(updated_verdict,
                                                 updated_verdict_text, exec_status,
                                                 apply_verdict_to_summary, drv_name,
                                                 drilldowndata,
                                                 report_group,
                                                 cmd_display_name)


def get_table_drv_complete_verdict_data(drv_name,
                                        drilldowndata,
                                        report_group,
                                        cmd_display_name=""):
    """
    Simple function to generate provider data for drv drilldown.
    drv_name: STC drv object name property.
    drilldowndata: drill down result data
    return
    """
    return get_table_drv_drilldown_data_advanced(EnumVerdict.none,
                                                 "",
                                                 EnumExecStatus.completed,
                                                 False,
                                                 drv_name,
                                                 drilldowndata,
                                                 report_group,
                                                 cmd_display_name)
