from StcIntPythonPL import *
import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ResultEnum import EnumDataFormat, \
    EnumExecStatus, EnumVerdict, EnumDataClass
from spirent.methodology.results.ProviderConst import ProviderConst, ChartConst
import spirent.methodology.results.ProviderUtils as pu
import spirent.methodology.results.SqliteUtils as sql_utils


def CreateCharts(tagname, tagged_object_list, params):
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('AclPerformanceChartScript.CreateCharts()')
    create_line_rate_chart()
    create_tolerance_chart()
    return ''


def create_line_rate_chart():
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('AclPerformanceChartScript.create_line_rate_chart()')
    db_list = get_dbs(True, False)

    # The frame size and the frame rates are what we want, the third value is 0 because
    # find_msdata uses that value to identify which tuple is the most significant (N/A here).
    q_theo_max = '''SELECT  Sb.FixedFrameLength, Round( Theo.FrameRate , 0), 0
                    FROM TheoreticalMaxLineRate AS Theo
                    JOIN StreamBlock AS Sb ON Theo.FrameSize = Sb.FixedFrameLength
                    WHERE Theo.MbpsLineRate =
                        ( CASE WHEN (SELECT DISTINCT Ec.LineSpeed FROM EthernetCopper AS Ec
                        JOIN TxEotStreamResults AS tx ON Tx.ParentHnd = Ec.ParentHnd
                        WHERE Tx.FrameCount > 0) = 'SPEED_100M' THEN 100 ELSE  1000 END)
                    LIMIT 1
                    '''
    q_real_max = '''SELECT Sb.FixedFrameLength, SUM(Sb.FpsLoad), 0 FROM StreamBlock AS Sb
                    JOIN TxEotStreamResults AS Tx ON Tx.ParentStreamBlock = Sb.Handle
                    WHERE Tx.FrameCount > 0
                    '''

    theo_max = get_data_from_query(db_list, q_theo_max)
    real_max = get_data_from_query(db_list, q_real_max)

    q_xcat = str("SELECT DISTINCT Sb.FixedFrameLength " +
                 "FROM RxEotStreamResults As RxStr " +
                 "JOIN StreamBlock AS Sb " +
                 "ON RxStr.ParentStreamBlock == Sb.Handle")
    xcat_data = get_data_from_query(db_list, q_xcat)

    template_line_rate['series'][0]['data'] = find_msdata(theo_max)
    template_line_rate['series'][1]['data'] = find_msdata(real_max)
    template_line_rate['xAxis']['categories'] = find_distinct_cats(xcat_data)

    result_data = init_chart_data_dict("GROUP_1", template_line_rate)
    pdg.submit_provider_data(result_data)
    return ""


def create_tolerance_chart():
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('AclPerformanceChartScript.create_tolerance_chart()')

    from AclPerformanceData import AclPerformanceData
    exp_maxjitter = AclPerformanceData().get_exp_maxjitter()
    exp_maxlatency = AclPerformanceData().get_exp_maxlatency()

    db_list = get_dbs(True, False)

    q_minjitter = form_query_during_blocking_traffic('MIN(MinJitter)')
    q_avgjitter = form_query_during_blocking_traffic('AVG(AvgJitter)')
    q_maxjitter = form_query_during_blocking_traffic('MAX(MaxJitter)')
    q_minlatency = form_query_during_blocking_traffic('MIN(MinLatency)')
    q_avglatency = form_query_during_blocking_traffic('AVG(AvgLatency)')
    q_maxlatency = form_query_during_blocking_traffic('MAX(MaxLatency)')
    q_blocking = form_query_during_blocking_traffic('COUNT(*)', 'Tag.Name="Bad.ttStreamBlock"')

    min_jitter_data = get_data_from_query(db_list, q_minjitter)
    avg_jitter_data = get_data_from_query(db_list, q_avgjitter)
    max_jitter_data = get_data_from_query(db_list, q_maxjitter)
    min_latency_data = get_data_from_query(db_list, q_minlatency)
    avg_latency_data = get_data_from_query(db_list, q_avglatency)
    max_latency_data = get_data_from_query(db_list, q_maxlatency)
    nonconformant_data = get_data_from_query(db_list, q_blocking)

    q_xcat = str('''SELECT DISTINCT Sb.FixedFrameLength FROM RxEotStreamResults As RxStr
                 JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle
                 ''')
    xcat_data = find_distinct_cats(get_data_from_query(db_list, q_xcat))
    count = len(xcat_data)

    template_tolerances['series'][0]['data'] = find_msdata(nonconformant_data)
    template_tolerances['series'][1]['data'] = find_msdata(min_jitter_data)
    template_tolerances['series'][2]['data'] = find_msdata(avg_jitter_data)
    template_tolerances['series'][3]['data'] = find_msdata(max_jitter_data)
    template_tolerances['series'][4]['data'] = find_msdata(min_latency_data)
    template_tolerances['series'][5]['data'] = find_msdata(avg_latency_data)
    template_tolerances['series'][6]['data'] = find_msdata(max_latency_data)
    template_tolerances['series'][7]['data'] = line(count, exp_maxjitter)
    template_tolerances['series'][8]['data'] = line(count, exp_maxlatency)
    template_tolerances['xAxis']['categories'] = xcat_data

    result_data = init_chart_data_dict("GROUP_1", template_tolerances)
    pdg.submit_provider_data(result_data)
    return ""


def line(count, data):
    return [data for i in range(0, count)]


# This function will take multiple rows in the result set of the same frame size and perform
# the calculation action on them, resulting in a single row for each framesize. Order is
# assumed the same as that incoming.
def find_msdata(data):
    s = []
    r = []
    d = {}
    z = {}
    for framesize, value, significance in data:
        k = str(framesize)
        if k not in d or z[k] < significance:
            d[k] = value
            z[k] = significance
    for framesize, value, significance in data:
        k = str(framesize)
        if k not in s:
            s.append(k)
            r.append(d[k])
    return r


def find_distinct_cats(xcat):
    cats = []
    for cat in xcat:
        if cat not in cats:
            cats.append(cat)
    return cats


def get_data_from_query(db_file_list, query):
    result_data = sql_utils.get_all_data(db_file_list, query)
    rows = result_data[ProviderConst.ROW]
    row_data = []
    for row in rows:
        row_data.append(row[0] if len(row) == 1 else (row[0], row[1], row[2]))
    return row_data


def get_dbs(UseMultipleResultsDatabases, UseSummary):
    if UseSummary and not UseMultipleResultsDatabases:
        return [get_active_results_db()]
    return pu.get_db_files(get_active_results_db(), UseMultipleResultsDatabases)


def get_active_results_db():
    # In its own function to allow for easier unit testing using MagicMock
    return pu.get_active_result_db_filename()


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


def form_query_during_blocking_traffic(field, where=''):
    if where != '':
        where = ' AND ' + where
    return '''
    SELECT
    (
    SELECT Sb.FixedFrameLength
    FROM Tag JOIN RelationTable AS Rt ON Tag.Handle = Rt.TargetHnd
    JOIN TxEotStreamResults AS Tx ON Tx.ParentStreamBlock = Rt.SourceHnd
    JOIN RxEotStreamResults AS Rx ON Tx.StreamId = Rx.Comp32
    JOIN StreamBlock AS Sb ON Tx.ParentStreamBlock = Sb.Handle
    WHERE Tx.FrameCount > 0
    ),
    (
    SELECT ___field___
    FROM Tag JOIN RelationTable AS Rt ON Tag.Handle = Rt.TargetHnd
    JOIN TxEotStreamResults AS Tx ON Tx.ParentStreamBlock = Rt.SourceHnd
    JOIN RxEotStreamResults AS Rx ON Tx.StreamId = Rx.Comp32
    JOIN StreamBlock AS Sb ON Tx.ParentStreamBlock = Sb.Handle
    WHERE Tx.FrameCount > 0      ___where___
    ),
    (
    SELECT COUNT(*)
    FROM Tag JOIN RelationTable AS Rt ON Tag.Handle = Rt.TargetHnd
    JOIN TxEotStreamResults AS Tx ON Tx.ParentStreamBlock = Rt.SourceHnd
    JOIN RxEotStreamResults AS Rx ON Tx.StreamId = Rx.Comp32
    JOIN StreamBlock AS Sb ON Tx.ParentStreamBlock = Sb.Handle
    WHERE Tx.FrameCount > 0
    AND Tag.Name = 'Bad.ttStreamBlock'
    )
    '''.replace('___field___', field).replace('___where___', where)


template_line_rate = {
    "title": {
        "text": "ACL Performance Frame Rate Results",
        "x": -20
    },
    "xAxis": {
        "categories": "xcat_rate",
        "labels": {
            "rotation": -45
        },
        "title": {
            "text": "Frame Size (bytes)"
        }
    },
    "yAxis": [
        {
            "categories": None,
            "title": {
                "text": "Frame Rate (fps)",
                "style": {
                    "color": '#434348'
                }
            }
        }
    ],
    "tooltip": {
        "valueSuffix": " (fps)"
    },
    "series": [
        {
            "type": "column",
            "name": "Theoretical Max Frame Rate",
            "data": "theo_max",
            "color": "green"
        },
        {
            "type": "column",
            "name": "Measured Max Frame Rate",
            "data": "real_max",
            "color": "orange"
        }
    ]
}


template_tolerances = {
    "title": {
        "text": "ACL Performance Traffic Results",
        "x": -20
    },
    "xAxis": {
        "categories": "xcat_tol",
        "labels": {
            "rotation": -45
        },
        "title": {
            "text": "Frame Size (bytes)"
        }
    },
    "yAxis": [
        {
            "categories": None,
            "min": 0,
            "tickInterval": 1,
            "title": {
                "text": "Blocking Flows",
                "style": {
                    "color": '#0000ff'
                }
            }
        },
        {  # yAxis-1
            "categories": None,
            "title": {
                "text": "Latency (us)",
                "style": {
                    "color": '#ff0000'
                }
            },
            "opposite": True
        },
        {  # yAxis-2
            "categories": None,
            "title": {
                "text": "Jitter (us)",
                "style": {
                    "color": '#00ff00'
                }
            },
            "opposite": True
        }
    ],
    "series": [
        {
            "type": "column",
            "name": "Blocking Flows",
            "data": "",
            "color": '#009999',
            "tooltip": {
                "valueSuffix": " flows"
            }
        },
        {
            "type": "column",
            "yAxis": 2,
            "name": "Min Jitter",
            "data": "",
            "color": '#006600',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "column",
            "yAxis": 2,
            "name": "RFC4689 Avg Jitter",
            "data": "",
            "color": '#009900',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "column",
            "yAxis": 2,
            "name": "Max Jitter",
            "data": "",
            "color": '#00ee00',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "column",
            "yAxis": 1,
            "name": "Min Latency",
            "data": "",
            "color": '#660000',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "column",
            "yAxis": 1,
            "name": "Avg Latency",
            "data": "",
            "color": '#990000',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "column",
            "yAxis": 1,
            "name": "Max latency",
            "data": "",
            "color": '#ee0000',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "line",
            "yAxis": 2,
            "name": "Jitter Limit",
            "data": "",
            "dashStyle": 'Dot',
            "color": '#00ee00',
            "tooltip": {
                "valueSuffix": " us"
            }
        },
        {
            "type": "line",
            "yAxis": 1,
            "name": "Latency Limit",
            "data": "",
            "dashStyle": 'Dot',
            "color": '#ee0000',
            "tooltip": {
                "valueSuffix": " us"
            }
        }
    ]
}
