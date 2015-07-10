from StcIntPythonPL import *

import json
import os
import traceback
# from jsonschema import validate as json_validate
import re

import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ResultEnum import EnumDataFormat, \
    EnumExecStatus, EnumVerdict, EnumDataClass
from spirent.methodology.results.ProviderConst import ProviderConst, ChartConst
import spirent.methodology.results.ProviderUtils as pu
import spirent.methodology.results.SqliteUtils as sql_utils
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mmutils
import spirent.methodology.utils.json_utils as json_utils


# Regular expression -- note that the braces are retained to be processed
SQL_RE = re.compile(r'({{.*?}})')


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(ChartTemplateJsonFileName, Title,
             XAxisTitle, XAxisCategories,
             YAxisTitle, YAxisCategories,
             Series, SeriesDataType, CustomModifier,
             UseMultipleResultsDatabases, UseSummary, ReportGroup):
    global SQL_RE

    logger = PLLogger.GetLogger('ExportDbChartCommand')
    logger.LogInfo(' ExportDbChartCommand validate')

    # Validate ChartTemplateJsonFileName
    file_name, found = find_template_file(ChartTemplateJsonFileName)
    if not found:
        return "Invalid Chart Template: %s" % ChartTemplateJsonFileName

    if Series is None or Series == []:
        return "Invalid Series specified: %s" % Series

    # Validate property types
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "xAxis": {"type": "string"},
            "x_categories": {"type": "array",
                             "items": {"allOf": [{"type": "string"}]}},
            "yAxis": {"type": "string"},
            "y_categories": {"type": "array",
                             "items": {"allOf": [{"type": "string"}]}},
            "series_data": {"type": "array", "minItems": 1,
                            "items": {"allOf": [{"type": "string"}]}},
            "series_data_type": {"enum": ["SINGLE", "PAIR"]}
        },
    }
    json_dict = {
        "title": Title,
        "xAxis": XAxisTitle,
        "x_categories": XAxisCategories,
        "yAxis": YAxisTitle,
        "y_categories": YAxisCategories,
        "series_data": Series,
        "series_data_type": SeriesDataType
    }

    try:
        res = json_utils.validate_json(
            json.dumps(json_dict), json.dumps(schema))
        if res != "":
            logger.LogInfo(res)
            return res
        # Before validating, "innoculate" the SQL-embedded junk by putting
        # quotes around them
        if CustomModifier != "":
            mod_safe = SQL_RE.sub(r'"\1"', CustomModifier)
            json.loads(mod_safe)
    except ValueError as ve:
        return ("Value Error: " + str(ve))
    except TypeError as te:
        return ("Type Error: " + str(te))
    except Exception as e:
        return ("Error: " + str(e))

    # Validate Series given as pair values if SeriesDataType is set to PAIR
    if SeriesDataType == "PAIR":
        for s in Series:
            if not is_sql_query(s):
                if len(s.split(',')) != 2:
                    return ("Series data must be pair values")

    return ""


def run(ChartTemplateJsonFileName, Title,
        XAxisTitle, XAxisCategories,
        YAxisTitle, YAxisCategories,
        Series, SeriesDataType, CustomModifier,
        UseMultipleResultsDatabases, UseSummary, ReportGroup):
    logger = PLLogger.GetLogger('ExportDbChartCommand')
    try:
        db_list = get_dbs(UseMultipleResultsDatabases, UseSummary)
        result_data = init_chart_data_dict(ReportGroup)

        series_data = get_series_data(db_list)
        add_series_data_list(result_data, series_data)

        # If any sql queries were passed in, grab results from db
        sql_result_file_list = []
        sql_result_file_list.append(db_list[0])
        get_sql_data(result_data, sql_result_file_list)

        pdg.submit_provider_data(result_data)
    # Catch most of them here
    except Exception as e:
        trace = traceback.format_exc()
        logger.LogError(trace)
        pdg.submit_command_execution_error('ExportDbChartCommand',
                                           str(e), trace)
        return False
    except:
        trace = traceback.format_exc()
        logger.LogError(trace)
        pdg.submit_command_execution_error('ExportDbChartCommand',
                                           ProviderConst.UNKNOWN_EXCEPTION_MESSAGE,
                                           trace)
        return False
    return True


def reset():
    return True


def get_dbs(UseMultipleResultsDatabases, UseSummary):
    if UseSummary and not UseMultipleResultsDatabases:
        return [get_active_results_db()]
    return pu.get_db_files(get_active_results_db(), UseMultipleResultsDatabases)


def init_chart_data_dict(ReportGroup):
    this_cmd = get_this_cmd()

    info = {
        ProviderConst.REPORT_GROUP: ReportGroup
    }
    status = {
        ProviderConst.VERDICT: EnumVerdict.none,
        ProviderConst.VERDICT_TEXT: '',
        ProviderConst.EXEC_STATUS: EnumExecStatus.completed,
        ProviderConst.APPLY_VERDICT: 'false'
    }
    title = {
        ChartConst.TEXT: this_cmd.Get('Title')
    }

    # Load the base template from the file
    base_template = load_base_template()

    mod_list = retrieve_modifier_objects()
    if mod_list is None:
        mod_list = ""

    xcat = this_cmd.GetCollection('XAxisCategories')

    x_label = {
        ChartConst.TEXT: this_cmd.Get('XAxisTitle')
    }
    ycat = this_cmd.GetCollection('YAxisCategories')
    y_label = {
        ChartConst.TEXT: this_cmd.Get('YAxisTitle')
    }
    # Remove any category modifications if it's empty (prevents graphing)
    if len(xcat) == 0:
        xcat = None
    if len(ycat) == 0:
        ycat = None
    data = {
        ChartConst.BASE_NAME: base_template,
        ChartConst.TITLE: title,
        ChartConst.X_CAT: xcat,
        ChartConst.X_LAB: x_label,
        ChartConst.Y_CAT: ycat,
        ChartConst.Y_LAB: y_label,
        ChartConst.SERIES: [],
        ChartConst.MOD_LIST: mod_list
    }
    provider_data = {
        ProviderConst.DATA_FORMAT: EnumDataFormat.chart,
        ProviderConst.CLASS: EnumDataClass.methodology_chart,
        ProviderConst.INFO: info,
        ProviderConst.STATUS: status,
        ProviderConst.DATA: data
    }
    return provider_data


def get_active_results_db():
    # In its own function to allow for easier unit testing using MagicMock
    return pu.get_active_result_db_filename()


def get_sql_data(provider_data, result_file_list):
    this_cmd = get_this_cmd()
    data = provider_data[ProviderConst.DATA]
    sql_param_dict = {ChartConst.TITLE: this_cmd.Get('Title'),
                      ChartConst.X_CAT: this_cmd.GetCollection('XAxisCategories'),
                      ChartConst.X_LAB: this_cmd.Get('XAxisTitle'),
                      ChartConst.Y_CAT: this_cmd.GetCollection('YAxisCategories'),
                      ChartConst.Y_LAB: this_cmd.Get('YAxisTitle'),
                      ChartConst.MOD_LIST: this_cmd.Get('CustomModifier')}
    for key, value in sql_param_dict.iteritems():
        if type(value) is str:
            if has_embedded_sql(value):
                data['{0}'.format(key)] = expand_embedded_sql(value,
                                                              result_file_list)
            elif is_sql_query(value):
                result_data = sql_utils.get_all_data(result_file_list, value)
                row_data = result_data[ProviderConst.ROW]
                data['{0}'.format(key)] = {ChartConst.TEXT: str(row_data[0][0])}
        else:
            result_list = []
            for v in value:
                if has_embedded_sql(v):
                    v = expand_embedded_sql(v, result_file_list)
                    result_list.append(v)
                elif is_sql_query(v):
                    row_data = []
                    result_data = sql_utils.get_all_data(result_file_list, v)
                    for row in result_data[ProviderConst.ROW]:
                        row_data.append(str(row[0]))
                    result_list.extend(row_data)
                else:
                    result_list.append(v)
            if (key == ChartConst.X_CAT or key == ChartConst.Y_CAT) and \
               len(result_list) == 0:
                result_list = None
            data['{0}'.format(key)] = result_list


def has_embedded_sql(param):
    global SQL_RE
    return SQL_RE.search(param)


def expand_embedded_sql(value, result_file_list):
    global SQL_RE
    if not has_embedded_sql(value):
        return value
    result = ""
    for expr in SQL_RE.split(value):
        if SQL_RE.match(expr):
            # Remove leading braces
            sql = expr.strip('{}')
            result_data = sql_utils.get_all_data(result_file_list, sql)
            row_data = []
            for row in result_data[ProviderConst.ROW]:
                if len(row) == 1:
                    row_data.extend(row)
                else:
                    row_data.append(row)
            if len(row_data) == 1:
                if type(row_data[0]) != type(list()):
                    result += json.dumps(row_data[0])
                elif len(row_data[0]) == 1:
                    result += json.dumps(row_data[0][0])
                else:
                    result += json.dumps(row_data[0])
            else:
                result += json.dumps(row_data)
        else:
            result += expr
    return result


def is_sql_query(param):
    if "select" in param.lower() and "from" in param.lower():
        return True
    else:
        return False


def get_series_data(result_file_list):
    this_cmd = get_this_cmd()
    series = this_cmd.GetCollection('Series')
    series_data_type = this_cmd.Get('SeriesDataType')
    new_series = []
    for s in series:
        if is_sql_query(s):
            new_series.append(sql_utils.get_all_chart_data(s,
                                                           series_data_type,
                                                           result_file_list))
        else:
            if series_data_type == "SINGLE":
                new_series.append([int(i) for i in s.split(',')])
            else:
                pair_list = []
                split_pairs = re.findall('\[(.*?)\]', s)
                for pair in split_pairs:
                    pair_list.append([int(i) for i in pair.split(',')])
                new_series.append(pair_list)
    return new_series


def add_series_data_list(provider_data, series_data_list):
    data = provider_data[ProviderConst.DATA]
    series = data[ChartConst.SERIES]
    for series_data in series_data_list:
        one_series = {ChartConst.DATA: series_data}
        series.append(one_series)


def find_template_file(file_path):
    if not os.path.isabs(file_path):
        abs_file_name = mmutils.find_template_across_common_paths(file_path)
        if abs_file_name != '':
            file_path = abs_file_name
    if os.path.isfile(file_path):
        return file_path, True
    else:
        return file_path, False


def load_base_template():
    this_cmd = get_this_cmd()
    file_path = this_cmd.Get('ChartTemplateJsonFileName')
    file_path, found = find_template_file(file_path)
    # Throw and let the outer try catch it
    if not found:
        raise IOError("[Errno 2] No such file: '" + file_path + "'")
    obj = None
    with open(file_path, 'r') as fd:
        # This can throw, and will be caught by the outer try
        obj = json.load(fd)
    if obj is None:
        raise ValueError('Failed to read a valid JSON entity from '
                         + file_path)
    return obj


def retrieve_modifier_objects():
    global SQL_RE
    this_cmd = get_this_cmd()
    obj = None
    mod_string = this_cmd.Get('CustomModifier')
    if mod_string != "":
        mod_safe = SQL_RE.sub(r'"\1"', mod_string)
        obj = None
        obj = json.loads(mod_safe)
        if obj is None:
            raise ValueError('Failed to read a valid JSON entity from ' +
                             mod_string)
    return obj
