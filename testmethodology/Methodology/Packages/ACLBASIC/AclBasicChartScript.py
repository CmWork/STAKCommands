from StcIntPythonPL import *
import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ResultEnum import EnumDataFormat, \
    EnumExecStatus, EnumVerdict, EnumDataClass
from spirent.methodology.results.ProviderConst import ProviderConst, ChartConst
import spirent.methodology.results.ProviderUtils as pu
import spirent.methodology.results.SqliteUtils as sql_utils


def CreateChart(tagname, tagged_object_list, params):
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('AclBasicChartScript.CreateCharts()')
    create_error_chart()
    return ''


def create_error_chart():
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('AclBasicChartScript.create_error_chart()')

    # We want to use the summary (the latter summary with ACL enabled)...
    db_list = [pu.get_active_result_db_filename()]

    queries = [('Out Of Seq', 'SELECT SUM (OutSeqFrameCount) FROM RxEotStreamResults'),
               ('Sequence Errors', 'SELECT SUM (DroppedFrameCount + ReorderedFrameCount + '
                'FcsErrorFrameCount + PrbsBitErrorCount + DuplicateFrameCount + '
                'LateFrameCount) FROM RxEotStreamResults'),
               ('CRC Errors', 'SELECT SUM(GeneratorCrcErrorFrameCount) FROM GeneratorPortResults'),
               ('Checksum Errors', 'SELECT SUM(GeneratorL3ChecksumErrorCount + '
                'GeneratorL4ChecksumErrorCount) FROM GeneratorPortResults'),
               ('Data Error', 'SELECT SUM(PrbsBitErrorCount) FROM AnalyzerPortResults')
               ]
    total_error_count = 0
    errors = []
    captions = []
    for caption, query in queries:
        error_count = get_data_from_query(db_list, query)[0]
        errors.append(error_count)
        captions.append(caption)
        total_error_count += error_count

    if total_error_count == 0:
        errors.append(1)
        captions.append('No Errors')

    template_error_pie['series'][0]['data'] = zip(captions, errors)
    template_error_pie['xAxis']['categories'] = captions

    result_data = init_chart_data_dict("SUMMARY", template_error_pie)
    pdg.submit_provider_data(result_data)
    return ""


def get_data_from_query(db_file_list, query):
    result_data = sql_utils.get_all_data(db_file_list, query)
    rows = result_data[ProviderConst.ROW]
    row_data = []
    for row in rows:
        row_data.append(row[0])
    return row_data


def init_chart_data_dict(ReportGroup, template):
    info = {
        ProviderConst.REPORT_GROUP: ReportGroup
    }
    status = {
        ProviderConst.VERDICT: EnumVerdict.none,
        ProviderConst.VERDICT_TEXT: '',
        ProviderConst.EXEC_STATUS: EnumExecStatus.completed,
        ProviderConst.APPLY_VERDICT: 'false'
    }
    data = {
        ChartConst.BASE_NAME: template,
        ChartConst.TITLE: '',
        ChartConst.X_CAT: '',
        ChartConst.X_LAB: '',
        ChartConst.Y_CAT: '',
        ChartConst.Y_LAB: '',
        ChartConst.SERIES: '',
        ChartConst.MOD_LIST: ''
    }
    provider_data = {
        ProviderConst.DATA_FORMAT: EnumDataFormat.chart,
        ProviderConst.CLASS: EnumDataClass.methodology_chart,
        ProviderConst.INFO: info,
        ProviderConst.STATUS: status,
        ProviderConst.DATA: data
    }
    return provider_data


template_error_pie = {
    "title": {
        "text": "Access Control List Basic Functionality Error Chart",
        "x": -20
    },
    "xAxis": {
        "title": {
            "text": "x-axis legend"
        },
        "categories": []
    },
    "yAxis": {
        "title": {
            "text": "y-axis legend"
        }
    },
    "series": [
        {
            "type": "pie",
            "size": 200,
            "colors": ["#ff0000", "#882200", "#bb4444", "#882288", "#662222", "#00cc00"],
            "name": "Errors",
            "dataLabels": {
                "enabled": False
            },
            "showInLegend": True,
            "data": [
                5,
                5,
                5,
                5,
                5
            ]
        }
    ]
}
