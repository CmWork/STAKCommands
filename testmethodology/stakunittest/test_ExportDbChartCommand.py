from StcIntPythonPL import *
from mock import MagicMock
from spirent.core.utils.scriptable import AutoCommand
import json
import os
import sys
import traceback

sys.path.append(os.path.join(os.getcwd(),
                'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.ExportDbChartCommand as export_to_json
from results.ResultInterface import ResultInterface
from results.ProviderConst import ProviderConst, ChartConst
from results.ResultEnum import EnumDataFormat, EnumExecStatus, EnumDataClass
from manager.utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


PKG = 'spirent.methodology'
COMMAND_NAME = 'ExportDbChartCommand'
COMMAND = export_to_json
TEST_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
               'stakunittest/test_sqlite_util_data.db'
TEST_MULTIPLE_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
                        'stakunittest/test_util_multi_data.db'
TEST_MULTIPLE_DB_ITR_FILE = 'test_util_multi_data_2015-01-21_16-25-42.db'


def test_validation(stc, tmpdir):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    ChartTemplateJsonFileName = template_file
    Title = "Test Chart"
    XAxisTitle = "Time"
    XAxisCategories = ["1t", "2t", "3t"]
    YAxisTitle = "Routes"
    YAxisCategories = ["a", "b", "c"]
    Series = ["Select TotalFrameCount from AnalyzerPortResults"]
    SeriesDataType = "PAIR"
    CustomModifier = "{\"yAxis\": {\"title\": {\"text\": \"Modified Label\"}}}"
    UseMultipleResultsDatabases = "FALSE"
    UseSummary = "FALSE"
    ReportGroup = "LEVEL_1"
    assert export_to_json.validate(ChartTemplateJsonFileName, Title,
                                   XAxisTitle, XAxisCategories,
                                   YAxisTitle, YAxisCategories,
                                   Series, SeriesDataType, CustomModifier,
                                   UseMultipleResultsDatabases, UseSummary, ReportGroup) == ""

    assert "Invalid Chart Template" in \
        export_to_json.validate("", Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)
    assert "1 is not of type u'string'" in \
        export_to_json.validate(ChartTemplateJsonFileName, 1,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "Invalid Chart Template: """ in \
        export_to_json.validate("", Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "[1, 2] is not of type u'string'" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                [1, 2], XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "1 is not of type u'array'" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, 1,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "1 is not of type u'string'" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                1, YAxisCategories,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "1 is not of type u'array'" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, 1,
                                Series, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "1 is not of type u'array'" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                1, SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "Invalid Series specified: []" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                [], SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "'TEST' is not one of [u'SINGLE', u'PAIR']" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, "TEST", CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "Type Error: expected string or buffer" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                Series, SeriesDataType, [1],
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)

    assert "Series data must be pair values" in \
        export_to_json.validate(ChartTemplateJsonFileName, Title,
                                XAxisTitle, XAxisCategories,
                                YAxisTitle, YAxisCategories,
                                ["[1, 2, 3]"], SeriesDataType, CustomModifier,
                                UseMultipleResultsDatabases, UseSummary, ReportGroup)


# tmpdir fixture creates a temporary directory for test invocation. The
# directory is removed after test completes
# Thanks Cliff for the link:
# http://pytest.org/latest/tmpdir.html
def test_load_base_template(stc, tmpdir):
    global PKG, COMMAND, COMMAND_NAME
    # Testcase: Check for blank filename (no such file)
    fail_message = ''
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('ChartTemplateJsonFileName', '')
        try:
            COMMAND.load_base_template()
        except:
            exc_info = sys.exc_info()
            fail_list = traceback.format_exception_only(exc_info[0],
                                                        exc_info[1])
            if len(fail_list) == 1:
                fail_message = fail_list[0]
            else:
                fail_message = '\n'.join(fail_list)
    if 'No such file' not in fail_message:
        raise AssertionError('Command failed with unexpected error: "' +
                             fail_message + '"')

    # Testcase: Check for empty file (in this case, bad format)
    fail_message = ''
    blank_file = os.path.join(str(tmpdir), 'blank.xml')
    with open(blank_file, 'w') as fd:
        fd.write('')
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('ChartTemplateJsonFileName', blank_file)
        try:
            COMMAND.load_base_template()
        except:
            exc_info = sys.exc_info()
            fail_list = traceback.format_exception_only(exc_info[0],
                                                        exc_info[1])
            if len(fail_list) == 1:
                fail_message = fail_list[0]
            else:
                fail_message = '\n'.join(fail_list)
    if 'No JSON object' not in fail_message:
        raise AssertionError('Command failed with unexpected error: "' +
                             fail_message + '"')

    # Testcase: Check for JSON errors
    fail_message = ''
    bad_file = os.path.join(str(tmpdir), 'bad.xml')
    with open(bad_file, 'w') as fd:
        # A dictionary that isn't closed
        fd.write('{"Key": "value"')
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('ChartTemplateJsonFileName', bad_file)
        try:
            COMMAND.load_base_template()
        except:
            exc_info = sys.exc_info()
            fail_list = traceback.format_exception_only(exc_info[0],
                                                        exc_info[1])
            if len(fail_list) == 1:
                fail_message = fail_list[0]
            else:
                fail_message = '\n'.join(fail_list)
    if 'ValueError' not in fail_message:
        raise AssertionError('Command failed with unexpected error: "' +
                             fail_message + '"')


def test_init_chart_data_dict(stc, tmpdir):
    global PKG, COMMAND, COMMAND_NAME

    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Testcase: Verify example dictionary initialization
    result = {}
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        result = COMMAND.init_chart_data_dict("")
    # Check elements contained
    assert ProviderConst.INFO in result
    assert ProviderConst.STATUS in result
    assert ProviderConst.DATA in result
    assert result[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart
    assert result[ProviderConst.CLASS] == EnumDataClass.methodology_chart
    status = result[ProviderConst.STATUS]
    assert status[ProviderConst.EXEC_STATUS] == EnumExecStatus.completed
    data = result[ProviderConst.DATA]
    title = data[ChartConst.TITLE]
    assert title[ChartConst.TEXT] == 'My Chart'
    x_label = data[ChartConst.X_LAB]
    assert x_label[ChartConst.TEXT] == 'My X Axis'
    y_label = data[ChartConst.Y_LAB]
    assert y_label[ChartConst.TEXT] == 'My Y Axis'


def test_add_series_data_list(stc, tmpdir):
    global PKG, COMMAND, COMMAND_NAME

    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Testcase: Verify addition of series
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        provider_data = COMMAND.init_chart_data_dict("")
        list_of_lists = [[1, 2, 3, 4, 5], [(3, 0), (2, -10), (0, 0)]]
        COMMAND.add_series_data_list(provider_data, list_of_lists)
    data = provider_data[ProviderConst.DATA]
    series = data[ChartConst.SERIES]
    assert len(series) == 2
    assert series[0]['data'] == [1, 2, 3, 4, 5]
    assert series[1]['data'] == [(3, 0), (2, -10), (0, 0)]


def test_retrieve_modifier_objects(stc):
    global PKG, COMMAND, COMMAND_NAME

    # Testcase: Verify no errors for an empty modifier list
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        result = COMMAND.retrieve_modifier_objects()
    assert result is None

    # Testcase: Verify passing modifier expression
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('CustomModifier', "{\"xAxis\": {\"plotLines\": "
                "[{\"color\": \"#123456\", \"label\": {\"text\": \"AAA\"}, "
                "\"width\": 10}, {\"color\": \"#00FF00\"} ] } }")
        result = COMMAND.retrieve_modifier_objects()
    assert 'xAxis' in result
    x_axis = result['xAxis']
    assert 'plotLines' in x_axis
    assert len(x_axis['plotLines']) == 2

    # Testcase: Improperly formed JSON string
    fail_message = ''
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        COMMAND.get_this_cmd = MagicMock(return_value=cmd)
        cmd.Set('CustomModifier', "{\"xAxis\": {\"plotLines\" "
                "[{\"color\": \"#123456\", \"label\": {\"text\": \"AAA\"},"
                "\"width\": 10}, {\"color\": \"#00FF00\"} ] } }")
        try:
            result = COMMAND.retrieve_modifier_objects()
        except:
            exc_info = sys.exc_info()
            fail_list = traceback.format_exception_only(exc_info[0],
                                                        exc_info[1])
            if len(fail_list) == 1:
                fail_message = fail_list[0]
            else:
                fail_message = '\n'.join(fail_list)
    if 'ValueError' not in fail_message:
        raise AssertionError('Command failed with unexpected error: "' +
                             fail_message + '"')


def test_command_execute_default(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        export_to_json.run("", "", "", "", "", "", "",
                           "", "", "", "", "GROUP_1")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        info = obj[ProviderConst.INFO]
        assert ProviderConst.REPORT_GROUP in info
        assert info[ProviderConst.REPORT_GROUP] == "GROUP_1"
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "{u'text': u'My Chart'}" == str(data[ChartConst.TITLE])
    assert "{u'text': u'My X Axis'}" == str(data[ChartConst.X_LAB])
    assert "None" == str(data[ChartConst.X_CAT])
    assert "{u'text': u'My Y Axis'}" == str(data[ChartConst.Y_LAB])
    assert "None" == str(data[ChartConst.Y_CAT])
    assert "[""]" == str(data[ChartConst.SERIES])
    assert "" == \
        str(data[ChartConst.MOD_LIST])


def test_command_execute_empty(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.Set("Title", "")
        cmd.Set("XAxisTitle", "")
        cmd.SetCollection("XAxisCategories", [""])
        cmd.Set("YAxisTitle", "")
        cmd.SetCollection("YAxisCategories", [""])
        cmd.Set("SeriesDataType", "SINGLE")
        export_to_json.run("", "", "", "", "", "", "",
                           "", "", "", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "{u'text': u''}" == str(data[ChartConst.TITLE])
    assert "{u'text': u''}" == str(data[ChartConst.X_LAB])
    assert "[u'']" == str(data[ChartConst.X_CAT])
    assert "{u'text': u''}" == str(data[ChartConst.Y_LAB])
    assert "[u'']" == str(data[ChartConst.Y_CAT])


def test_command_execute(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.Set("Title", "My Graph")
        cmd.Set("XAxisTitle", "Time")
        cmd.SetCollection("XAxisCategories", ["1t", "2s", "3s", "4s"])
        cmd.Set("YAxisTitle", "Routes Count")
        cmd.SetCollection("YAxisCategories", ["a", "b", "c"])
        cmd.SetCollection("Series",
                          ["1, 2", "3, 4"])
        cmd.Set("SeriesDataType", "SINGLE")
        cmd.Set("CustomModifier",
                "{\"yAxis\": {\"title\": {\"text\": \"Modified Label\"}}}")
        export_to_json.run("", "", "", "", "", "", "",
                           "", "", "", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "{u'text': u'My Graph'}" == str(data[ChartConst.TITLE])
    assert "{u'text': u'Time'}" == str(data[ChartConst.X_LAB])
    assert "[u'1t', u'2s', u'3s', u'4s']" == str(data[ChartConst.X_CAT])
    assert "{u'text': u'Routes Count'}" == str(data[ChartConst.Y_LAB])
    assert "[u'a', u'b', u'c']" == str(data[ChartConst.Y_CAT])
    assert "[{u'data': [1, 2]}, {u'data': [3, 4]}]" \
        == str(data[ChartConst.SERIES])
    assert "{u'yAxis': {u'title': {u'text': u'Modified Label'}}}" == \
        str(data[ChartConst.MOD_LIST])


def test_command_execute_get_dbs(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_MULTIPLE_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_MULTIPLE_DB_FILE)

    db_list = []

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        db_list = export_to_json.get_dbs(False, True)
        assert len(db_list) == 1
        assert db_list[0].endswith(TEST_MULTIPLE_DB_FILE)
        db_list = export_to_json.get_dbs(False, False)
        assert len(db_list) == 1
        assert db_list[0].endswith(TEST_MULTIPLE_DB_ITR_FILE)
        db_list = export_to_json.get_dbs(True, False)
        assert len(db_list) > 1
        db_list = export_to_json.get_dbs(True, True)
        assert len(db_list) > 1


def test_command_execute_with_sql(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.Set("Title", "Select MIN(Id) From AnalyzerPortResults")
        cmd.Set("XAxisTitle", "Select MIN(Id) From AnalyzerPortResults")
        cmd.SetCollection("XAxisCategories",
                          ["Select Id From AnalyzerPortResults", "3", "4"])
        cmd.Set("YAxisTitle", "Select MIN(Id) From AnalyzerPortResults")
        cmd.SetCollection("YAxisCategories", ["Select Id From AnalyzerPortResults"])
        cmd.SetCollection("Series",
                          ["3",
                           "Select TotalFrameCount from AnalyzerPortResults", "1, 2"])
        cmd.Set("SeriesDataType", "SINGLE")
        cmd.Set("CustomModifier",
                "{\"yAxis\": {\"title\": {\"text\": \"Modified Label\"}}}")
        export_to_json.run("", "", "", "", "", "",
                           ["Select TotalFrameCount from AnalyzerPortResults"],
                           "", "", "", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "{u'text': u'1'}" == str(data[ChartConst.TITLE])
    assert "{u'text': u'1'}" == str(data[ChartConst.X_LAB])
    assert "[u'1', u'2', u'3', u'4']" == str(data[ChartConst.X_CAT])
    assert "{u'text': u'1'}" == str(data[ChartConst.Y_LAB])
    assert "[u'1', u'2']" == str(data[ChartConst.Y_CAT])
    assert "[{u'data': [3]}, {u'data': [1151261, 1239945]}, {u'data': [1, 2]}]" \
        == str(data[ChartConst.SERIES])
    assert "{u'yAxis': {u'title': {u'text': u'Modified Label'}}}" == \
        str(data[ChartConst.MOD_LIST])


def test_command_execute_pair(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.SetCollection("Series",
                          ["[1, 2], [3, 4]", "[5, 6], [7, 8]"])
        cmd.Set("SeriesDataType", "PAIR")
        export_to_json.run("", "", "", "", "", "",
                           "", "", "", "", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "[{u'data': [[1, 2], [3, 4]]}, {u'data': [[5, 6], [7, 8]]}]" \
        == str(data[ChartConst.SERIES])


def test_command_execute_with_sql_pair(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.SetCollection("Series",
                          ["Select TotalFrameCount, Id from AnalyzerPortResults",
                           "Select Id, TotalFrameCount From AnalyzerPortResults"])
        cmd.Set("SeriesDataType", "PAIR")
        export_to_json.run("", "", "", "", "", "",
                           [""], "",
                           "", "", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "[{u'data': [[1151261, 1], [1239945, 2]]}, {u'data': [[1, 1151261], [2, 1239945]]}]" \
        == str(data[ChartConst.SERIES])


def test_command_execute_with_sql_modlist(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.SetCollection("Series",
                          ["Select TotalFrameCount from AnalyzerPortResults", "1, 2"])
        cmd.Set("SeriesDataType", "SINGLE")
        cmd.Set("CustomModifier", "{\"yAxis\": {\"title\": {\"text\": "
                "{{SELECT MIN(Id) FROM AnalyzerPortResults}}}}, \"xAxis\": "
                "{\"categories\": {{SELECT Id FROM AnalyzerPortResults}}}, "
                "\"series\": {\"data\": {{SELECT TotalFrameCount, "
                "TotalOctetCount FROM AnalyzerPortResults}}}}")
        export_to_json.run(cmd.Get('ChartTemplateJsonFileName'),
                           cmd.Get('Title'), cmd.Get('XAxisTitle'),
                           cmd.GetCollection('XAxisCategories'),
                           cmd.Get('YAxisTitle'),
                           cmd.GetCollection('YAxisCategories'),
                           cmd.GetCollection('Series'),
                           cmd.Get('SeriesDataType'),
                           cmd.Get('CustomModifier'),
                           cmd.Get('UseMultipleResultsDatabases'),
                           cmd.Get('UseSummary'),
                           "LEVEL_2")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    x_cat = data[ChartConst.X_CAT]
    y_cat = data[ChartConst.Y_CAT]
    mod_list = data[ChartConst.MOD_LIST]
    assert mod_list == "{\"yAxis\": {\"title\": {\"text\": 1}}, \"xAxis\": " \
                       "{\"categories\": [1, 2]}, \"series\": " \
                       "{\"data\": [[1151261, 147361408], [1239945, 158712960]]}}"
    assert x_cat is None
    assert y_cat is None


def test_command_execute_invalid_sql(stc, tmpdir):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()
    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.Set("SeriesDataType", "SINGLE")

        cmd.SetCollection("XAxisCategories", ["SELECT test FROM test"])
        assert not export_to_json.run("", "", "", "", "", "", "",
                                      "", "", "", "", "")

        cmd.SetCollection("XAxisCategories", [])
        cmd.SetCollection("YAxisCategories", ["SELECT test FROM test"])
        assert not export_to_json.run("", "", "", "", "", "", "",
                                      "", "", "", "", "")

        cmd.SetCollection("YAxisCategories", [])
        cmd.SetCollection("Series",
                          ["SELECT test FROM test"])
        assert not export_to_json.run("", "", "", "", "", "", "",
                                      "", "", "", "", "")

        cmd.SetCollection("Series", [])
        cmd.Set("CustomModifier",
                "SELECT test FROM test")
        assert not export_to_json.run("", "", "", "", "", "", "",
                                      "", "", "", "", "")


def test_command_execute_with_sql_multiple_dbs(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_MULTIPLE_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_MULTIPLE_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.SetCollection("Series",
                          ["3",
                           "Select TotalFrameCount from AnalyzerPortResults", "1, 2"])
        cmd.Set("SeriesDataType", "SINGLE")
        cmd.Set("UseMultipleResultsDatabases", "TRUE")
        cmd.Set("UseSummary", "TRUE")
        export_to_json.run("", "", "", "", "", "",
                           ["Select TotalFrameCount from AnalyzerPortResults"],
                           "", "", "TRUE", "TRUE", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "[{u'data': [3]}, {u'data': [298838, 287903, 294329, 289852]}, {u'data': [1, 2]}]" \
        == str(data[ChartConst.SERIES])


def test_command_execute_with_sql_pair_multiple_dbs(stc, tmpdir, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_MULTIPLE_DB_FILE

    # FIXME: Do the various checks to ensure the db file's result are properly
    # loaded into the JSON string
    result_file = os.path.join(os.getcwd(), TEST_MULTIPLE_DB_FILE)
    template_file = os.path.join(str(tmpdir), 'template.xml')
    create_template_file(template_file)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        export_to_json.get_this_cmd = MagicMock(return_value=cmd)
        export_to_json.get_active_results_db = MagicMock(return_value=result_file)
        cmd.Set('ChartTemplateJsonFileName', template_file)
        cmd.SetCollection("Series",
                          ["Select TotalFrameCount, Id from AnalyzerPortResults Where Id = 1"])
        cmd.Set("SeriesDataType", "PAIR")
        cmd.Set("UseMultipleResultsDatabases", "TRUE")
        export_to_json.run("", "", "", "", "", "",
                           [""],
                           "", "", "TRUE", "", "")
    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = None
    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        assert ProviderConst.DATA_FORMAT in obj
        if obj[ProviderConst.DATA_FORMAT] == EnumDataFormat.chart:
            selected = obj
            break
    assert selected is not None
    data = selected[ProviderConst.DATA]
    assert "[{u'data': [[298838, 1], [294329, 1]]}]" \
        == str(data[ChartConst.SERIES])


def create_template_file(file_name, content=None):
    if content is None:
        content = get_sample_template()
    with open(file_name, 'w') as fd:
        fd.write(content)


def get_sample_template():
    return """
{
    "title": {
        "text": "BGP Route Reflector Convergence",
            "x": -20
    },
        "xAxis": {
            "categories": [
                "1t",
            "2s",
            "3s",
            "4s",
            "5s",
            "6s",
            "7s",
            "8s",
            "9s",
            "10s",
            "11s",
            "12s"
                ],
            "plotLines": [
            {
                "label": {
                    "text": "Start"
                },
                "color": "#FF0000",
                "value": 2
            },
            {
                "label": {
                    "text": "End"
                },
                "color": "#FF0000",
                "width": 2,
                "value": 10
            }
            ]
        },
        "yAxis": {
            "title": {
                "text": "Routes Converged"
            }
        },
        "tooltip": {
            "valueSuffix": " routes"
        },
        "series": [
        {
            "data": [
                200,
            200,
            200,
            155,
            144,
            135,
            120.6,
            100.5,
            75.4,
            65.1,
            0,
            0
                ]
        },
        {
            "data": [
                0,
            0,
            64.1,
            78,
            105,
            115,
            118,
            120,
            135,
            140,
            200,
            200
                ]
        }
    ]
}
"""
