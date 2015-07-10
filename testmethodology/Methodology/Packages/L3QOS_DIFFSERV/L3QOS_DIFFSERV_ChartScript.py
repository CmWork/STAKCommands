from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ResultEnum import EnumDataFormat, \
    EnumExecStatus, EnumVerdict, EnumDataClass
from spirent.methodology.results.ProviderConst import ProviderConst, ChartConst
import spirent.methodology.results.ProviderUtils as pu
import spirent.methodology.results.SqliteUtils as sql_utils
import spirent.methodology.results.LogUtils as logger
import os
import sqlite3

OBJ_KEY = 'spirent.methodology.DiffServ_CfgRamp'

color_collection = ['black', 'red', 'blue', 'orange', 'green', 'yellow', 'grey', 'pink']
series_keys = ['type', 'color', 'name', 'data']

# packet_template is customized by the author based on what
# type of chart is needed for specific methodology's report
packet_template = {
    "title": {
        "text": "L3QOS DIFFSERV Results",
        "x": -20
    },
    "xAxis": {
        "categories": "xcat",
        "title": {
            "text": "Iteration"
        }
    },
    "yAxis": {
        "categories": None,
        "title": {
            "text": "Packet Count",
            "style": {
                "color": '#90ed7d'
            }
        }
    },
    "tooltip": {
        "valueSuffix": " (packets)"
    },
    "series": [
    ]
}


# time_template is customized by the author based on what
# type of chart is needed for specific methodology's report
time_template = {
    "title": {
        "text": "L3QOS DIFFSERV Results",
        "x": -20
    },
    "xAxis": {
        "categories": "xcat",
        "title": {
            "text": "Iteration"
        }
    },
    "yAxis": {
        "categories": None,
        "title": {
            "text": "Rate",
            "style": {
                "color": '#90ed7d'
            }
        }
    },
    "tooltip": {
        "valueSuffix": " (ms)"
    },
    "series": [
    ]
}


def CreateChart(tagname, b, params):
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug("Running custom CreateChart script...")
    plLogger.LogDebug("    tagname : " + str(tagname))
    db_list = get_dbs(True, False)

    sb_info = get_active_streamblock_info(db_list)
    logger.debug("   number of selected streams: " + str(len(sb_info)))
    q_stream = get_streamblock_query()

    q_maxjitter = str("SELECT ROUND(MaxJitter*1e-3,3) FROM RxEotStreamResults As RxStr " +
                      "JOIN StreamBlock AS Sb " +
                      "ON RxStr.ParentStreamBlock == Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")
    q_maxlatency = str("SELECT ROUND(MaxLatency*1e-3,3) FROM RxEotStreamResults As RxStr " +
                       "JOIN StreamBlock AS Sb " +
                       "ON RxStr.ParentStreamBlock == Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")
    q_pktloss = str("SELECT TxRes.FrameCount - RxRes.FrameCount " +
                    "As 'Packet Loss' From RxEotStreamResults As RxRes " +
                    "JOIN TxEotStreamResults As TxRes " +
                    "JOIN Streamblock As Sb " +
                    "ON RxRes.ParentStreamBlock = TxRes.ParentStreamblock " +
                    "AND TxRes.ParentStreamblock = Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")
    q_ooopkt = str("SELECT OutSeqFrameCount FROM RxEotStreamResults As RxStr " +
                   "JOIN StreamBlock AS Sb " +
                   "ON RxStr.ParentStreamBlock == Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")
    q_latepkt = str("SELECT LateFrameCount FROM RxEotStreamResults As RxStr " +
                    "JOIN StreamBlock AS Sb " +
                    "ON RxStr.ParentStreamBlock == Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")
    q_duppkt = str("SELECT DuplicateFrameCount FROM RxEotStreamResults As RxStr " +
                   "JOIN StreamBlock AS Sb " +
                   "ON RxStr.ParentStreamBlock == Sb.Handle") + \
        str(q_stream) + str("  WHERE IsExpectedPort = 1")

    max_jitter_data = get_data_from_query(db_list, q_maxjitter)
    max_latency_data = get_data_from_query(db_list, q_maxlatency)
    pktloss_data = get_data_from_query(db_list, q_pktloss)
    ooopkt_data = get_data_from_query(db_list, q_ooopkt)
    latepkt_data = get_data_from_query(db_list, q_latepkt)
    duppkt_data = get_data_from_query(db_list, q_duppkt)

    xcat_data = [x+1 for x in range(len(db_list))]

    # jitter
    get_per_stream_time_from_db(sb_info, max_jitter_data, "Jitter (ms)", xcat_data)
    result_jitter = init_chart_data_dict("GROUP_1", time_template)
    pdg.submit_provider_data(result_jitter)
    # latency
    get_per_stream_time_from_db(sb_info, max_latency_data, "Latency (ms)", xcat_data)
    result_latency = init_chart_data_dict("GROUP_1", time_template)
    pdg.submit_provider_data(result_latency)
    # packet loss
    get_per_stream_packet_from_db(sb_info, pktloss_data, "Packet Loss", xcat_data)
    result_loss = init_chart_data_dict("GROUP_1", packet_template)
    pdg.submit_provider_data(result_loss)
    # ooo packet
    get_per_stream_packet_from_db(sb_info, ooopkt_data, "Out of Order Packet", xcat_data)
    result_ooo = init_chart_data_dict("GROUP_1", packet_template)
    pdg.submit_provider_data(result_ooo)
    # late packet
    get_per_stream_packet_from_db(sb_info, latepkt_data, "Late Packet", xcat_data)
    result_late = init_chart_data_dict("GROUP_1", packet_template)
    pdg.submit_provider_data(result_late)
    # duplicated packet
    get_per_stream_packet_from_db(sb_info, duppkt_data, "Duplicated Packet", xcat_data)
    result_dup = init_chart_data_dict("GROUP_1", packet_template)
    pdg.submit_provider_data(result_dup)

    return ""


def get_data_from_query(db_file_list, query):
    result_data = sql_utils.get_all_data(db_file_list, query)
    rows = result_data[ProviderConst.ROW]
    row_data = []
    for row in rows:
        row_data.append(row[0])
    logger.debug('    row_data in get_data_from_query: ' + str(row_data))
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


def get_streamblock_handle_list():
    logger.debug('get_streamblock_handle_list : ')

    sb_handle_list = []
    if not CObjectRefStore.Exists(OBJ_KEY):
        logger.warn('DiffServCfgRampCommand was not called. ' +
                    'Using default threshold values.')
    else:
        tmp_dict = CObjectRefStore.Get(OBJ_KEY)
        logger.debug("  tmp_dict: " + str(tmp_dict))
        dict_keys = tmp_dict.keys()
        logger.debug("  dict_keys: " + str(dict_keys))

        # convert keys to handles
        sb_list = tag_utils.get_tagged_objects_from_string_names(dict_keys)
        for sb in sb_list:
            sb_handle_list.append(sb.GetObjectHandle())
        logger.debug("  sb_handle_list: " + str(sb_handle_list))

    return sb_handle_list


def get_streamblock_query():
    logger.debug('get_streamblock_query : ')

    sb_handle_list = get_streamblock_handle_list()
    num_str = len(sb_handle_list)
    cnt = 0
    for hnd in sb_handle_list:
        if cnt == 0:
            q_stream = " AND ("
        q_stream = q_stream + "sb.Handle == " + str(hnd)
        cnt = cnt + 1
        if cnt < num_str:
            q_stream = q_stream + " OR "
        elif cnt == num_str:
            q_stream = q_stream + ")"

    return q_stream


def get_active_streamblock_info(db_file_list):
    logger.debug('get_active_streamblock_info : ')

    q_stream = get_streamblock_query()
    query = str("SELECT Name FROM StreamBlock AS Sb " +
                "WHERE sb.Active == 1") + str(q_stream)
    logger.debug("  query: " + str(query))

    prv_num = 0
    num = 0
    for db_file in db_file_list:
        if not os.path.isfile(db_file):
            raise Exception('Unable to find db file:' + db_file)
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        for q in query.split(";"):
            if len(q) > 0:
                cur.execute(q)
        rows = cur.fetchall()
        conn.close()
        num = len(rows)

        if prv_num != 0 and num != prv_num:
            logger.error('Inconsistent numbers of streams in DBs')
        prv_num = num
    return rows


def get_per_stream_packet_from_db(sb_info, db_info_list, title, xcat):
    logger.debug("ndb_info_list PACKET: " + str(db_info_list))
    num_stream = len(sb_info)
    packet_template['title']['text'] = title
    packet_template['yAxis']['title']['text'] = "Packet Count"
    packet_template['xAxis']['categories'] = xcat

    packet_template['series'][:] = []
    i = 0
    for sb in sb_info:
        # series_info has to match series_keys
        series_info = ['spline', color_collection[i], sb_info[i], db_info_list[i::num_stream]]
        packet_template['series'].append(dict(zip(series_keys, series_info)))
        i = i + 1

    return ""


def get_per_stream_time_from_db(sb_info, db_info_list, title, xcat):
    logger.debug("ndb_info_list TIME: " + str(db_info_list))
    num_stream = len(sb_info)
    time_template['title']['text'] = title
    time_template['yAxis']['title']['text'] = "ms"
    time_template['xAxis']['categories'] = xcat

    time_template['series'][:] = []
    i = 0
    for sb in sb_info:
        # series_info has to match series_keys
        series_info = ['spline', color_collection[i], sb_info[i], db_info_list[i::num_stream]]
        time_template['series'].append(dict(zip(series_keys, series_info)))
        i = i + 1

    return ""
