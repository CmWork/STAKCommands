from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"
OBJ_KEY = 'spirent.methodology.DiffServ_CfgRamp'

# String input used for queries
q_devSelect = "DevInfo.SRC AS 'SRC', DevInfo.DST AS 'DST'"

q_devInfo = "(SELECT DstInfo.Address AS DST, SrcInfo.Address AS SRC, " + \
    "SrcInfo.SourceHnd AS SbHnd, SrcInfo.ParentHnd AS ParentHnd " + \
    "FROM (SELECT * FROM IPv4If AS Ip JOIN (SELECT * FROM RelationTable " + \
    "WHERE Type = 'DstBinding') As Dst ON Ip.Handle = Dst.TargetHnd) AS DstInfo " + \
    "JOIN (SELECT * FROM Ipv4If AS Ip JOIN (SELECT * FROM RelationTable " + \
    "WHERE Type = 'SrcBinding') As Src ON Ip.Handle = Src.TargetHnd) " + \
    "AS SrcInfo ON SrcInfo.SourceHnd = DstInfo.SourceHnd) AS DevInfo"


def do_db_query(cmd, sb_handle_list):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("do_query(), sb_handle_list: " + str(sb_handle_list))

    num_str = len(sb_handle_list)
    cnt = 0
    for hnd in sb_handle_list:
        if cnt == 0:
            q_stream = " AND ("
        q_stream = q_stream + "Sb.Handle == " + str(hnd)
        cnt = cnt + 1
        if cnt < num_str:
            q_stream = q_stream + " OR "
        elif cnt == num_str:
            q_stream = q_stream + ")"

    query = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
        ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
        "Lp.Load || CASE Lp.LoadUnit " + \
        "WHEN 'PERCENT_LINE_RATE' THEN '%' " + \
        "WHEN 'BITS_PER_SECOND' THEN 'bps' " + \
        "WHEN 'KILOBITS_PER_SECOND' THEN 'Kbps' " + \
        "WHEN 'MEGABITS_PER_SECOND' THEN 'Mbps' " + \
        "WHEN 'FRAMES_PER_SECOND' THEN 'Fps' " + \
        "ELSE '' END AS 'CIR', " + \
        "TxRes.FrameCount-RxRes.FrameCount AS 'FL Count', " + \
        "ROUND(MaxLatency*1e-3,3) AS 'Max FTD (ms)', " + \
        "ROUND(MaxJitter*1e-3,3) AS 'Max FDV (ms)', " + \
        "OutSeqFrameCount AS 'Out of Order Frame Count', " + \
        "LateFrameCount AS 'Late Frame Count', " + \
        "DuplicateFrameCount AS 'Duplicated Frame Count' " + \
        "FROM " + str(q_devInfo) + \
        " JOIN RxEotStreamResults as RxRes JOIN TxEotStreamResults as TxRes ON " + \
        "TxRes.ParentStreamBlock = RxRes.ParentStreamBlock JOIN Streamblock AS Sb " + \
        "ON TxRes.ParentStreamBlock = Sb.Handle " + str(q_stream) + \
        " JOIN RelationTable as Rt ON " + \
        "Rt.type = 'AffiliationStreamBlockLoadProfile' AND Sb.Handle = Rt.SourceHnd " + \
        "JOIN StreamBlockLoadProfile as Lp ON Lp.Handle = Rt.TargetHnd " + \
        "WHERE DevInfo.SbHnd = Sb.Handle"

    cmd.Set('SqlQuery', query)
    cmd.Set('DisplayName', 'L3 QoS DiffServ Summary Results')
    cmd.Set('PassedVerdictExplanation', 'L3 QoS DiffServ Summary Results')
    cmd.Set('FailedVerdictExplanation', 'ERROR found in L3 QoS DiffServ Results.')
    cmd.Set('UseMultipleResultsDatabases', True)
    cmd.Set('ApplyVerdictToSummary', False)
    cmd.Set('OperationType', 'GREATER_THAN_OR_EQUAL')
    cmd.Set('RowCount', 0L)
    plLogger.LogDebug("    VerifyDbQueryCommand - " + str(query))
    return ''


def diffServResultsReport(tagname, b, params):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom diffServResultsReport script...")
    plLogger.LogDebug("    tagname : " + str(tagname))

    exp_pktloss = 0
    exp_maxjitter = 200
    exp_maxlatency = 1000
    exp_maxoop = 0
    exp_maxlatepkt = 0
    exp_maxduppkt = 0
    service_dict = {}
    sb_handle_list = []
    if not CObjectRefStore.Exists(OBJ_KEY):
        plLogger.LogWarn('DiffServCfgRampCommand was not called. ' +
                         'Using default threshold values.')
    else:
        tmp_dict = CObjectRefStore.Get(OBJ_KEY)
        plLogger.LogDebug("  tmp_dict: " + str(tmp_dict))
        dict_keys = tmp_dict.keys()
        plLogger.LogDebug("  dict_keys: " + str(dict_keys))

        # convert keys to handles
        sb_list = tag_utils.get_tagged_objects_from_string_names(dict_keys)
        sb_handle_list = []
        for sb in sb_list:
            sb_handle_list.append(sb.GetObjectHandle())
        plLogger.LogDebug("  sb_handle_list: " + str(sb_handle_list))
        i = 0
        for dk in dict_keys:
            service_dict[sb_handle_list[i]] = tmp_dict[dk]
            i = i + 1
    plLogger.LogDebug("  service_dict: " + str(service_dict))

    res_cmd_list = tag_utils.get_tagged_objects_from_string_names(tagname)
    # plLogger.LogDebug("res_cmd_list: " + str(res_cmd_list))

    for cmd in res_cmd_list:
        if cmd.IsTypeOf(PKG + '.VerifyDbQueryCommand'):
            plLogger.LogDebug("cmd.IsTypeOf: VerifyDbQueryCommand")
            do_db_query(cmd, sb_handle_list)

        if cmd.IsTypeOf(PKG + '.VerifyMultipleDbQueryCommand'):
            plLogger.LogDebug("cmd.IsTypeOf: VerifyMultipleDbQueryCommand")
            q_list = []
            display_name_list = []
            pass_list = []
            fail_list = []

            q_loss = ''
            q_jitter = ''
            q_latency = ''
            q_oop = ''
            q_late = ''
            q_dup = ''
            i = 0
            for hnd, value in service_dict.items():
                plLogger.LogDebug("service_dict key/handle: " + str(hnd))
                exp_pktloss = value['exp_pktloss']
                exp_maxjitter = value['exp_maxjitter']
                exp_maxlatency = value['exp_maxlatency']
                exp_maxoop = value['exp_maxoop']
                exp_maxlatepkt = value['exp_maxlatepkt']
                exp_maxduppkt = value['exp_maxduppkt']

                if i == 0:
                    q_tmp = " WHERE "
                else:
                    q_tmp = " OR "

                # q_loss
                q_loss = q_loss + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND TxRes.FrameCount - RxRes.FrameCount > " + \
                    str(exp_pktloss) + ")"

                # q_jitter
                q_jitter = q_jitter + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND ROUND(AvgJitter*1e-3,3) > " + str(exp_maxjitter) + ")"

                # q_latency
                q_latency = q_latency + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND ROUND(AvgLatency*1e-3,3) > " + str(exp_maxlatency) + ")"

                # q_oop
                q_oop = q_oop + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND OutSeqFrameCount > " + str(exp_maxoop) + ")"

                # q_late
                q_late = q_late + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND LateFrameCount > " + str(exp_maxlatepkt) + ")"

                # q_dup
                q_dup = q_dup + q_tmp + "(Sb.Handle = " + str(hnd) + \
                    " AND DuplicateFrameCount > " + str(exp_maxduppkt) + ")"

                i = i + 1

            display_name_list.append("Max Frame Transfer Delay (FTD) Results")
            pass_list.append("Max FTD is within the configured threshold of " +
                             str(exp_maxlatency) + " ms.")
            fail_list.append("Max FTD exceeded the configured threshold of " +
                             str(exp_maxlatency) + " ms.")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "ROUND(MaxLatency*1e-3,3) AS 'Max FTD (ms)' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults As RxStr " + \
                "JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_latency)
            q_list.append(q)

            display_name_list.append("Max Frame Delay Variation (FDV) Results")
            pass_list.append("Max FDV is within the configured threshold of " +
                             str(exp_maxjitter) + " ms.")
            fail_list.append("Max FDV exceeded the configured threshold of " +
                             str(exp_maxjitter) + " ms.")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "ROUND(MaxJitter*1e-3,3) AS 'Max FDV (ms)' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults As RxStr " + \
                "JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_jitter)
            q_list.append(q)

            display_name_list.append("Frame Loss (FL) Results")
            pass_list.append("Frame Loss Count is within the configured threshold of " +
                             str(exp_pktloss) + ".")
            fail_list.append("Frame Loss Count exceeded the configured threshold of " +
                             str(exp_pktloss) + ".")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "TxRes.FrameCount - RxRes.FrameCount As 'FL Count' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults AS RxRes " + \
                "JOIN TxEotStreamResults AS TxRes JOIN Streamblock AS Sb " + \
                "ON RxRes.ParentStreamBlock = TxRes.ParentStreamblock AND " + \
                "TxRes.ParentStreamblock = Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_loss)
            q_list.append(q)

            display_name_list.append("Out of Order Frame Results")
            pass_list.append("Out of Order Frame Count is within the configured threshold of " +
                             str(exp_maxoop) + ".")
            fail_list.append("Out of Order Frame Count exceeded the configured threshold of " +
                             str(exp_maxoop) + ".")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "OutSeqFrameCount AS 'Out of Order Frame Count' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults As RxStr " + \
                "JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_oop)
            q_list.append(q)

            display_name_list.append("Late Frame Results")
            pass_list.append("Late Frame Count is within the configured threshold of " +
                             str(exp_maxlatepkt) + ".")
            fail_list.append("Late Frame Count exceeded the configured threshold of " +
                             str(exp_maxlatepkt) + ".")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "LateFrameCount AS 'Late Frame Count' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults As RxStr " + \
                "JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_late)
            q_list.append(q)

            display_name_list.append("Duplicated Frame Results")
            pass_list.append("Duplicated Frame Count is within the configured threshold of " +
                             str(exp_maxduppkt) + ".")
            fail_list.append("Duplicated Frame Count exceeded the configured threshold of " +
                             str(exp_maxduppkt) + ".")
            q = "SELECT Sb.Name AS 'Streamblock', " + str(q_devSelect) + \
                ", Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
                "DuplicateFrameCount AS 'Duplicated Frame Count' " + \
                "FROM " + str(q_devInfo) + " JOIN RxEotStreamResults As RxStr " + \
                "JOIN StreamBlock AS Sb ON RxStr.ParentStreamBlock == Sb.Handle " + \
                "AND DevInfo.SbHnd = Sb.Handle " + str(q_dup)
            q_list.append(q)

            cmd.SetCollection('DisplayNameList', display_name_list)
            cmd.SetCollection('PassedVerdictExplanationList', pass_list)
            cmd.SetCollection('FailedVerdictExplanationList', fail_list)
            cmd.SetCollection('SqlQueryList', q_list)
            cmd.Set('UseMultipleResultsDatabases', True)
            plLogger.LogDebug("    VerifyMultipleDbQueryCommand - " + str(q_list))

    return ""

    