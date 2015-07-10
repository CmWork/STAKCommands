from StcIntPythonPL import *
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"


OBJ_KEY = PKG + '.Y1564_Microburst'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate():
    return ''


def run():
    logger = PLLogger.GetLogger('Y.1564MicroburstResults')
    if not CObjectRefStore.Exists(OBJ_KEY):
        err = 'Y1564MicroburstConfigCommand was not called'
        logger.LogError(err)
        raise RuntimeError(err)
    cmd_dict = CObjectRefStore.Get(OBJ_KEY)
    if cmd_dict is None:
        err = 'Failed to retrieve persistent storage'
        logger.LogError(err)
        raise RuntimeError(err)
    # this_cmd = get_this_cmd()
    # Stolen from AppendToEotCommand
    db_file = get_db_filename()
    db_conn = sqlite3.connect(db_file)
    db_curs = db_conn.cursor()
    ds_id = get_dataset_id(db_curs)
    logger.LogInfo('Writing Burst table')
    write_burst_table(db_curs, ds_id, cmd_dict)
    logger.LogInfo('Writing Chart table')
    write_burst_chart(db_curs, ds_id, cmd_dict)
    db_conn.commit()
    extract_unique_info(db_curs, ds_id, cmd_dict)
    db_conn.close()
    # Propagate the queries and parameters to the appropriate tagged commands
    process_tagged_commands(cmd_dict)
    return True


def reset():
    return True


def process_tagged_commands(cmd_dict):
    cmd_list = \
        tag_utils.get_tagged_objects_from_string_names(['Y1564Command'])
    for cmd in cmd_list:
        if cmd.IsTypeOf(PKG + '.VerifyDbQueryCommand'):
            create_summary_queries(cmd, cmd_dict)
        elif cmd.IsTypeOf(PKG + '.VerifyMultipleDbQueryCommand'):
            create_kpi_queries(cmd, cmd_dict)
        elif cmd.IsTypeOf(PKG + '.ExportDbChartCommand'):
            create_chart_queries(cmd, cmd_dict)


# EOT DB Custom Tables
def write_burst_table(curs, ds_id, cmd_dict):
    '''
    Given each burst configuration and delta list list, populate a table
    Columns:
        DataSetId, Name, Stream_#, StreamBlock Handle,
        Source Addr, Dest Addr, CoS Values, DSCP Values, Unique Addresses
    '''
    delta_list = cmd_dict['delta_list']
    burst_cfg = cmd_dict['burst_cfg']
    be_hdl_list = cmd_dict['be_hdl_list']
    table_sql = "CREATE TABLE Y1564Burst ('DataSetId' INTEGER, " + \
                "'Name' STRING, 'StreamNum' INTEGER, " + \
                "'StreamBlock' INTEGER, " +\
                "'SourceAddr' STRING, 'DestAddr' STRING, " + \
                "'Rate' FLOAT, " +\
                "'CoSValues' STRING, " +\
                "'DSCPValues' STRING, " +\
                "'UniqAddr' STRING)"
    create_table(curs, table_sql)
    values = []
    for sb_delta, burst, be_hdl in zip(delta_list, burst_cfg, be_hdl_list):
        vlan_id = burst['VlanId'].strip() if 'VlanId' in burst else ''
        values.append((ds_id, 'Best Effort Stream', None, be_hdl,
                       burst['SourceAddr'], burst['DestAddr'],
                       cmd_dict['nom_rate'], None, None, None))
        for idx, (hdl, rate, uniq) in enumerate(zip(sb_delta['handle'],
                                                    sb_delta['rate'],
                                                    sb_delta['uniq'])):
            if vlan_id:
                cos_list = ', '.join(burst['ServiceCosList'].split(';'))
                dscp_list = None
            else:
                cos_list = None
                dscp_list = ', '.join(burst['ServiceDscpList'].split(';'))
            values.append((ds_id, burst['MicroburstName'], idx + 1,
                           hdl,
                           burst['SourceAddr'], burst['DestAddr'], rate,
                           cos_list, dscp_list, uniq))
    sql_cmd = "INSERT INTO Y1564Burst VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    curs.executemany(sql_cmd, values)
    return len(values)


def write_burst_chart(curs, ds_id, cmd_dict):
    '''
    Using tshark, extract pertinent data for analysis of results. Note that
    the spirent tshark (wireshark) must be installed and in the path for this
    to produce an actual chart
    Columns:
        DataSetId, Index, Timestamp, StreamId, SeqNum
    '''
    logger = PLLogger.GetLogger('Y.1564MicroburstResults')
    table_sql = "CREATE TABLE Y1564BurstChart ('DataSetId' INTEGER, " + \
                "'Index' INTEGER, 'Timestamp' DOUBLE, " + \
                "'StreamId' INTEGER, 'SeqNum' INTEGER)"
    create_table(curs, table_sql)
    values = []
    # First, check to make sure that tshark is installed and is the spirent
    # version
    spirent = False
    try:
        result = subprocess.check_output('tshark -v', stderr=subprocess.PIPE)
        if re.search(r'[Ss]pirent', result):
            spirent = True
    except:
        err_msg = str(sys.exc_info()[1])
        if 'No such file' not in err_msg and 'cannot find' not in err_msg:
            raise
    if not spirent:
        logger.LogWarn('Did not find correct version of tshark, ' +
                       'chart data will not be populated')
        return 0
    stc_sys = CStcSystem.Instance()
    # For windows commands, the path needs to be normalized so that
    # backslashes are used, this does nothing for Linux
    data_path = os.path.normpath(stc_sys.GetApplicationSessionDataPath())
    capture_path = os.path.join(data_path, 'microburst_data.pcap')
    if not os.path.exists(capture_path):
        logger.LogWarn('No capture file was found, '
                       'chart data will not be populated')
        return 0
    if ' ' in capture_path:
        capture_path = '"' + capture_path + '"'
    parse_cmd = 'tshark -r {} -T fields'.format(capture_path)
    for field in ['frame.number', 'frame.time_relative',
                  'stcsig.streamid', 'stcsig.seqnum']:
        parse_cmd += ' -e {}'.format(field)
    logger.LogInfo('Issuing command: {}'.format(parse_cmd))
    tshark = subprocess.Popen(parse_cmd, bufsize=-1,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
    out_text, err_text = tshark.communicate()
    if tshark.returncode != 0:
        err_msg = 'Tshark command failed with error: {}'.format(err_text)
        logger.LogError(err_msg)
        raise RuntimeError(err_msg)
    # Skip the last line, as it is blank
    values = []
    for line in out_text.split('\n')[:-1]:
        # Do numerical conversions and split on whitespace
        num_list = tuple([ds_id] + [float(n) if '.' in n else int(n)
                                    for n in re.split(r'\s+', line)])
        values.append(num_list)
    sql_cmd = "INSERT INTO Y1564BurstChart VALUES (?, ?, ?, ?, ?)"
    if len(values) > 0:
        curs.executemany(sql_cmd, values)
    return len(values)


def extract_unique_info(curs, ds_id, cmd_dict):
    query = "SELECT " + \
            "Timestamp*1e3, UniqAddr, SeqNum FROM Y1564BurstChart " + \
            "INNER JOIN TxEotStreamResults AS TxR " + \
            "ON TxR.StreamId=Y1564BurstChart.StreamId " + \
            "INNER JOIN Y1564Burst ON TxR.ParentStreamBlock=StreamBlock " + \
            "ORDER BY Timestamp"
    curs.execute(query)
    prev_ts = None
    prev_uniq = None
    cmd_dict['zone_table'] = []
    max = float(cmd_dict['max_unique'])
    for ts, uniq, seq in curs.fetchall():
        if seq == 0:
            # Normalize unique to maximum
            if prev_uniq is not None:
                prev_uniq = int(round(255 * prev_uniq / max))
            cmd_dict['zone_table'].append((prev_ts, prev_uniq))
        else:
            prev_ts, prev_uniq = ts, uniq
    # Add the last zone
    if prev_uniq is not None:
        prev_uniq = int(round(255 * prev_uniq / max))
        cmd_dict['zone_table'].append((prev_ts, prev_uniq))


def get_rate_unit_suff(rate_unit):
    return {
        'PERCENT_LINE_RATE': '%',
        'BITS_PER_SECOND': 'bps',
        'KILO_BITS_PER_SECOND': 'Kbps',
        'MEGABITS_PER_SECOND': 'Mbps',
        'FRAMES_PER_SECOND': 'fps'
    }.get(rate_unit, '%')


def create_summary_queries(cmd, cmd_dict):
    cmd.Set('ApplyVerdictToSummary', False)
    cmd.Set('OperationType', 'GREATER_THAN_OR_EQUAL')
    cmd.Set('RowCount', 0L)
    cmd.Set('DisplayName', 'Y.1564 Microburst Summary Table')
    cmd.Set('PassedVerdictExplanation',
            'Table of Microburst Deltas and related KPI values')
    cmd.Set('UseMultipleResultsDatabases', False)
    rate_unit = get_rate_unit_suff(cmd_dict['bur_rate_unit'])
    query = "SELECT " + \
            "Y1564Burst.Name AS 'Microburst Name', " + \
            "Y1564Burst.StreamNum AS 'Stream', " + \
            "UniqAddr AS 'Unique Addresses', " + \
            "ROUND(Y1564Burst.Rate,3) || '" + rate_unit + "' AS 'Load', " + \
            "CoSValues AS 'CoS Values', " + \
            "DSCPValues AS 'DSCP Values', " + \
            "RxRes.SigFrameCount AS 'Rx Frame Count', " + \
            "RxRes.PrbsErrorFrameCount AS 'PRBS Error Count', " + \
            "RxRes.InOrderFrameCount AS 'In-Order Frame Count', " + \
            "RxRes.OutSeqFrameCount AS 'Out-of-Order Frame Count', " + \
            "RxRes.ReorderedFrameCount AS 'Reordered Frame Count', " + \
            "TxRes.FrameCount - RxRes.FrameCount AS 'Frame Loss', " + \
            "ROUND(RxRes.MaxLatency*1e-3) AS 'Max FTD (ms)', " + \
            "ROUND(RxRes.MaxJitter*1e-3) AS 'Max FDV (ms)' " + \
            "FROM TxEotStreamResults AS TxRes " + \
            "INNER JOIN RxEotStreamResults AS RxRes " + \
            "ON TxRes.ParentStreamBlock=RxRes.ParentStreamBlock " + \
            "INNER JOIN Y1564Burst ON TxRes.ParentStreamBlock=StreamBlock " + \
            "INNER JOIN RelationTable AS Rt " + \
            "ON SourceHnd=TxRes.ParentStreamBlock " + \
            "INNER JOIN Tag ON TargetHnd=Tag.Handle " + \
            "WHERE Type='UserTag' AND Tag.Name='ttMicroburst' " + \
            "ORDER BY TxRes.ParentStreamBlock"
    cmd.Set('SqlQuery', query)


def user_out_tuple(descr, val_descr, value, unit=''):
    r = descr if val_descr is None or val_descr == '' else val_descr
    p = '{} is within the configured threshold of {}{}'.format(r, value, unit)
    f = '{} exceeded the configured threshold of {}{}'.format(r, value, unit)
    return (descr, p, f)


def create_kpi_queries(cmd, cmd_dict):
    '''
    Iterate over all configured bursts, and create KPI queries for each one
    '''
    cmd.Set('UseMultipleResultsDatabases', False)
    delta_list = cmd_dict['delta_list']
    burst_cfg = cmd_dict['burst_cfg']
    select_start = \
        "SELECT Y1564Burst.Name AS 'Microburst Name', " + \
        "Y1564Burst.StreamNum AS 'Stream', "
    from_clause = \
        "FROM RxEotStreamResults AS RxRes " + \
        "INNER JOIN Y1564Burst ON RxRes.ParentStreamBlock=StreamBlock " + \
        "INNER JOIN RelationTable AS Rt " + \
        "ON SourceHnd=RxRes.ParentStreamBlock " + \
        "INNER JOIN Tag ON TargetHnd=Tag.Handle "
    tx_from_clause = \
        "INNER JOIN TxEotStreamResults AS TxRes " + \
        "ON TxRes.ParentStreamBlock=RxRes.ParentStreamBlock "
    where_clause = \
        "WHERE Type='UserTag' AND Tag.Name='ttMicroburst' " + \
        "AND RxRes.ParentStreamBlock in ({}) "
    order_clause = \
        "ORDER BY RxRes.ParentStreamBlock"
    # Set up the query list
    q_list = []
    d_list = []
    p_list = []
    f_list = []
    for sb_delta, burst in zip(delta_list, burst_cfg):
        # Create a string of comma-separated stream block handles
        hdl_select = ','.join([str(x) for x in sb_delta['handle']])
        # Each KPI set needs to add separate queries in the list
        q = select_start + \
            "RxRes.SigFrameCount AS 'Rx Frame Count', " + \
            "'> 0' AS 'Expected' " + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.SigFrameCount=0 " + \
            order_clause
        q_list.append(q)
        d_list.append('{} Rx Frame Count'.format(burst['MicroburstName']))
        p_list.append('Rx Frame Count received as expected')
        f_list.append('No Rx Frames')
        q = select_start + \
            "RxRes.PrbsErrorFrameCount AS 'PRBS Error Count', " + \
            "{} AS 'Threshold' ".format(burst['PrbsLimit']) + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.PrbsErrorFrameCount>{} ".format(burst['PrbsLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} PRBS Error Frame Count'.format(burst['MicroburstName']),
                           'PRBS Error Count', burst['PrbsLimit'])
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
        q = select_start + \
            "TxRes.FrameCount-RxRes.FrameCount AS 'Frame Loss', " + \
            "{} AS 'Threshold' ".format(burst['FrameLossLimit']) + \
            from_clause + tx_from_clause + \
            where_clause.format(hdl_select) + \
            "AND TxRes.FrameCount-RxRes.FrameCount>{} ".format(burst['FrameLossLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} Frame Loss'.format(burst['MicroburstName']),
                           'Frame Loss', burst['FrameLossLimit'])
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
        q = select_start + \
            "ROUND(RxRes.MaxLatency*1e-3,3) AS 'Max FTD (ms)', " + \
            "{} AS 'Threshold' ".format(burst['LatencyLimit']) + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.MaxLatency*1e-3>{} ".format(burst['LatencyLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} Max Frame Transfer Delay'.format(burst['MicroburstName']),
                           'Max FTD', burst['LatencyLimit'], ' ms')
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
        q = select_start + \
            "ROUND(RxRes.MaxJitter*1e-3,3) AS 'Max FDV (ms)', " + \
            "{} AS 'Threshold' ".format(burst['JitterLimit']) + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.MaxJitter*1e-3>{} ".format(burst['JitterLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} Max Frame Delay Variation'.format(burst['MicroburstName']),
                           'Max FDV', burst['JitterLimit'], ' ms')
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
        q = select_start + \
            "RxRes.InOrderFrameCount AS 'In-Order Frame Count', " + \
            "'> 0' AS 'Expected' " + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.InOrderFrameCount=0 " + \
            order_clause
        q_list.append(q)
        d_list.append('{} In-Order Frame Count'.format(burst['MicroburstName']))
        p_list.append('In-Order Frame Count received as expected')
        f_list.append('No In-Order Frames')
        q = select_start + \
            "RxRes.OutSeqFrameCount AS 'Out-of-Order Frame Count', " + \
            "{} AS 'Threshold' ".format(burst['OosFrameLimit']) + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.OutSeqFrameCount>{} ".format(burst['OosFrameLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} Out-of-Order Frame Count'.format(burst['MicroburstName']),
                           'Out-of-Order Count', burst['OosFrameLimit'])
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
        q = select_start + \
            "RxRes.ReorderedFrameCount AS 'Reordered Frame Count', " + \
            "{} AS 'Threshold' ".format(burst['ReorderFrameLimit']) + \
            from_clause + where_clause.format(hdl_select) + \
            "AND RxRes.ReorderedFrameCount>{} ".format(burst['ReorderFrameLimit']) + \
            order_clause
        q_list.append(q)
        d, p, f = \
            user_out_tuple('{} Reordered Frame Count'.format(burst['MicroburstName']),
                           'Reordered Count', burst['ReorderFrameLimit'])
        d_list.append(d)
        p_list.append(p)
        f_list.append(f)
    cmd.SetCollection('SqlQueryList', q_list)
    cmd.SetCollection('DisplayNameList', d_list)
    cmd.SetCollection('PassedVerdictExplanationList', p_list)
    cmd.SetCollection('FailedVerdictExplanationList', f_list)


def create_chart_queries(cmd, cmd_dict):
    rate_unit = get_rate_unit_suff(cmd_dict['bur_rate_unit'])
    rate_unit_suff = ' ' + rate_unit if rate_unit != '%' else rate_unit
    cmd.Set('Title', 'Y.1564 Microburst Test')
    cmd.Set('XAxisTitle', 'Time (ms)')
    cmd.Set('YAxisTitle', 'Rate ({})'.format(rate_unit))
    cmd.Set('SeriesDataType', 'PAIR')
    cmd.Set('UseMultipleResultsDatabases', False)
    cmd.Set('UseSummary', False)
    cmd.Set('ReportGroup', 'GROUP_1')
    zones = []
    for ts_limit, norm_density in cmd_dict['zone_table']:
        if norm_density is not None:
            g = 255 - norm_density
            norm_density = '#{:02X}{:02X}00'.format(norm_density, g)
        zones.append({'value': ts_limit, 'fillColor': norm_density})
    # Zone coloring requires HighCharts 4.1.0 or higher
    modifier = [{
        'yAxis': [{'title': {'text': 'Rate ({})'.format(rate_unit)}}],
        'subtitle': {
            'text': 'Rate area color goes from green (low density) to red (max density)'},
        'series': [{'zones': zones,
                    'tooltip': {'valueSuffix': rate_unit_suff}}]
    }]
    cmd.Set('CustomModifier', json.dumps(modifier))
    q_list = []
    q = "SELECT Timestamp * 1000.0, Rate FROM Y1564BurstChart " + \
        "INNER JOIN TxEotStreamResults AS TxR " + \
        "ON TxR.StreamId=Y1564BurstChart.StreamId " + \
        "INNER JOIN Y1564Burst ON TxR.ParentStreamBlock=StreamBlock"
    q_list.append(q)
    q = "SELECT Timestamp * 1000.0, SeqNum FROM Y1564BurstChart " + \
        "INNER JOIN TxEotStreamResults AS TxR " + \
        "ON TxR.StreamId=Y1564BurstChart.StreamId " + \
        "INNER JOIN Y1564Burst ON TxR.ParentStreamBlock=StreamBlock"
    q_list.append(q)
    cmd.SetCollection('Series', q_list)


# The following functions should be moved to an appropriate utility package
def get_db_filename(db_idx=-1):
    project = CStcSystem.Instance().GetObject('project')
    result_setting = project.GetObject('testresultsetting')
    if result_setting is None:
        # Should never happen, it's a 1:1
        raise RuntimeError('Unable to find Test Result Setting Object')
    result_dir = os.path.dirname(result_setting.Get('CurrentResultFileName'))
    if result_dir is None or result_dir == '':
        raise RuntimeError('No results have been saved. Unable to find directory.')
    all_db_set = set(glob.glob(os.path.join(result_dir, '*.db')))
    ts_db_list = glob.glob(os.path.join(result_dir, '*_????-??-??_??-??-??.db'))
    trim_set = set()
    for fn in ts_db_list:
        trim_set.add(fn[0:-23] + '.db')
    sort_list = list(all_db_set - trim_set)
    # sort dbs by modified time
    sort_list.sort(key=lambda fn: os.path.getmtime(fn))
    if (db_idx < 0 and -db_idx > len(sort_list)) or db_idx >= len(sort_list):
        raise RuntimeError('No results have been saved. No files in directory.')
    return sort_list[db_idx]


def get_dataset_id(cursor):
    cursor.execute('''SELECT MAX(Id) FROM DataSet''')
    return cursor.fetchone()[0]


def create_table(cursor, sql_command):
    sql_list = sql_command.split()
    # Verify the command at least has the first 2 words correct
    if sql_list[0].upper() != 'CREATE' and sql_list[1].upper() != 'TABLE':
        raise RuntimeError('Invalid TABLE CREATE SQL command')
    table_name = sql_list[2]
    # Check for existence first
    query = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' and " + \
        "name='{0}'"
    cursor.execute(query.format(table_name))
    # If it exists already, no need to create the table (or we could validate)
    if cursor.fetchone()[0] != 0:
        return
    cursor.execute(sql_command)
