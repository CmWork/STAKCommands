from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"


OBJ_KEY = 'spirent.methodology.Y1564_SvcCfgRamp'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StreamblockTagName):
    return ''


def user_out_tuple(descr, val_descr, value, unit=''):
    r = descr if val_descr is None or val_descr == '' else val_descr
    p = '{} is within the configured threshold of {}{}'.format(r, value, unit)
    f = '{} exceeded the configured threshold of {}{}'.format(r, value, unit)
    return (descr, p, f)


def run(StreamblockTagName):
    plLogger = PLLogger.GetLogger("Y1564ConfKpiQueries")
    if not CObjectRefStore.Exists(OBJ_KEY):
        plLogger.LogError('Y1564SvcCfgRampCommand was not called')
        raise RuntimeError('Y1564SvcCfgRampCommand was not called')
    cmd_dict = CObjectRefStore.Get(OBJ_KEY)
    start_bw = cmd_dict['start_bw']
    cir_bw = cmd_dict['cir_bw']
    eir_bw = cmd_dict['eir_bw']
    ovr_bw = cmd_dict['ovr_bw']
    step_bw = cmd_dict['step_bw']
    exp_pktloss = cmd_dict['exp_pktloss']
    exp_avgjitter = cmd_dict['exp_avgjitter']
    exp_maxjitter = cmd_dict['exp_maxjitter']
    exp_avglatency = cmd_dict['exp_avglatency']
    exp_maxlatency = cmd_dict['exp_maxlatency']
    exp_maxoop = cmd_dict['exp_maxoop']
    exp_maxlatepkt = cmd_dict['exp_maxlatepkt']

    obj_list = \
        tag_utils.get_tagged_objects_from_string_names([StreamblockTagName])
    if len(obj_list) > 1:
        raise RuntimeError('Tag pointed to more than one object')
    sb = obj_list[0]
    sb_name = sb.Get('Name')
    sb_hnd = str(sb.GetObjectHandle())
    src_if = sb.GetObject('NetworkEndpoint', RelationType('SrcBinding'))
    src_dev = src_if.GetParent()
    dst_if = sb.GetObject('NetworkEndpoint', RelationType('DstBinding'))
    dst_dev = dst_if.GetParent()
    # Use composite params
    cvlan = src_dev.Get('Vlan1')
    svlan = src_dev.Get('Vlan2')
    src = src_dev.Get('Ipv4Address')
    if src is None:
        src = src_dev.Get('Ipv6Address')
    dst = dst_dev.Get('Ipv4Address')
    if dst is None:
        dst = dst_dev.Get('Ipv6Address')
    if not sb.IsTypeOf('Streamblock'):
        raise RuntimeError('Tag did not point to a Streamblock')
    hnd_reg = CHandleRegistry.Instance()
    this_cmd = get_this_cmd()
    cmd_hnd_list = this_cmd.GetCollection('CommandList')
    # Remember to set it to lowercase
    exp_cmd_name_list = [PKG + '.verifymultipledbquerycommand',
                         PKG + '.verifydbquerycommand']
    exp_cmd_list = []
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd.GetType() in exp_cmd_name_list:
            exp_cmd_list.append(cmd)

    # FIXME: GregK said that we can just call local instances, instead of
    #        having it be children of a group command

    for cmd in exp_cmd_list:
        if cmd.IsTypeOf(PKG + '.VerifyMultipleDbQueryCommand'):
            # Tacked on for bandwidth check
            v = " AND Lp.Load <= " + str(cir_bw)
            q_list = []
            d_list = []
            p_list = []
            f_list = []
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "TxRes.FrameCount - RxRes.FrameCount AS 'Packet Loss', " + \
                "'" + str(exp_pktloss) + "' AS 'Expected Packet Loss' " + \
                "FROM TxEotStreamResults AS TxRes INNER JOIN " + \
                "RxEotStreamResults AS RxRes ON " + \
                "TxRes.ParentStreamBlock == RxRes.ParentStreamBlock " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "TxRes.ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + \
                sb_hnd + \
                " AND TxRes.FrameCount - RxRes.FrameCount > " + \
                str(exp_pktloss)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Frame Loss', '', exp_pktloss)
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "ROUND(AvgJitter*1e-3,3) AS 'RFC 4689 Avg FDV (ms)', " + \
                "'" + str(exp_avgjitter) + "' AS 'Expected RFC " + \
                "4689 Avg FDV' FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND AvgJitter*1e-3 > " + str(exp_avgjitter)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Average Frame Delay Variation',
                                     'Average FDV', exp_avgjitter, ' ms')
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "ROUND(MaxJitter*1e-3,3) AS 'Max FDV (ms)', " + \
                "'" + str(exp_maxjitter) + "' AS 'Expected Max FDV' " + \
                "FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND MaxJitter*1e-3 > " + str(exp_maxjitter)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Maximum Frame Delay Variation',
                                     'Maximum FDV', exp_maxjitter, ' ms')
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "ROUND(AvgLatency*1e-3,3) AS 'Avg FTD (ms)', " + \
                "'" + str(exp_avglatency) + "' AS 'Expected Avg FTD' " + \
                "FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND AvgLatency*1e-3 > " + str(exp_avglatency)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Average Frame Transfer Delay',
                                     'Average FTD', exp_avglatency, ' ms')
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "ROUND(MaxLatency*1e-3) AS 'Max FTD (ms)', " + \
                "'" + str(exp_maxlatency) + "' AS 'Expected Max FTD' " + \
                "FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND MaxLatency*1e-3 > " + str(exp_maxlatency)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Maximum Frame Transfer Delay',
                                     'Maximum FTD', exp_maxlatency, ' ms')
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "OutSeqFrameCount AS 'Out of Order Packet Count', " + \
                "'" + str(exp_maxoop) + "' AS 'Expected Max Out of " + \
                "Order Packet Count' FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND OutSeqFrameCount > " + str(exp_maxoop)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Out-of-order Packet Count', '',
                                     exp_maxoop)
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            q = "SELECT '" + sb_name + "' AS Streamblock, " + \
                "LateFrameCount AS 'Late Packet Count', " + \
                "'" + str(exp_maxlatepkt) + "' AS 'Expected Max Late " + \
                "Packet Count' FROM RxEotStreamResults " + \
                "INNER JOIN StreamBlock AS Sb ON " + \
                "ParentStreamBlock = Sb.Handle " + \
                "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                "Sb.Handle||','||Lp.Handle = " + \
                "(SELECT SourceHnd||','||TargetHnd " + \
                "FROM RelationTable WHERE " + \
                "Type='AffiliationStreamBlockLoadProfile') " + \
                "WHERE Sb.Handle == " + sb_hnd + \
                " AND LateFrameCount > " + str(exp_maxlatepkt)
            q_list.append(q + v)
            d, p, f = user_out_tuple('Late Packet Count', '',
                                     exp_maxlatepkt)
            d_list.append(d)
            p_list.append(p)
            f_list.append(f)
            cmd.SetCollection('SqlQueryList', q_list)
            cmd.SetCollection('DisplayNameList', d_list)
            cmd.SetCollection('PassedVerdictExplanationList', p_list)
            cmd.SetCollection('FailedVerdictExplanationList', f_list)
            cmd.Set('UseMultipleResultsDatabases', True)
        elif cmd.IsTypeOf(PKG + '.VerifyDbQueryCommand'):
            cmd.Set('ApplyVerdictToSummary', False)
            cmd.Set('OperationType', 'GREATER_THAN_OR_EQUAL')
            cmd.Set('RowCount', 0L)
            cmd.Set('UseMultipleResultsDatabases', True)
            cmd.Set('DisplayName', 'Y.1564 Configuration Test Summary Table')
            cmd.Set('PassedVerdictExplanation',
                    'Table of Load and related KPI values')
            query = "SELECT " + \
                    "CASE Lp.Load WHEN " + str(cir_bw) + \
                    " THEN 'Green (CIR)' WHEN " + str(cir_bw + eir_bw) + \
                    " THEN 'Yellow (CIR + EIR)' WHEN " + \
                    str(cir_bw + eir_bw + ovr_bw) + " THEN " + \
                    "'Red (CIR + EIR + Overshoot)' ELSE " + \
                    "'Step ' || CAST(ROUND(" + str(step_bw) + " * " + \
                    "(Lp.Load - " + str(start_bw) + ") / " + \
                    str(cir_bw - start_bw) + " + 1) AS INT) END " + \
                    "AS Iteration, " + \
                    "Sb.Name AS Service, " + \
                    "'" + src + "' AS Source, " + \
                    "'" + dst + "' AS Destination, " + \
                    str(svlan) + " AS 'S-Vlan', " + \
                    str(cvlan) + " AS 'C-Vlan', " + \
                    "Sb.FixedFrameLength  AS 'Frame Size (bytes)', " + \
                    "Lp.Load || CASE Lp.LoadUnit " + \
                    "WHEN 'PERCENT_LINE_RATE' THEN '%' " + \
                    "WHEN 'BITS_PER_SECOND' THEN 'bps' " + \
                    "WHEN 'KILOBITS_PER_SECOND' THEN 'Kbps' " + \
                    "WHEN 'MEGABITS_PER_SECOND' THEN 'Mbps' " + \
                    "WHEN 'FRAMES_PER_SECOND' THEN 'Fps' " + \
                    "ELSE '' END " + \
                    "AS 'IR', " + \
                    "TxRes.FrameCount-RxRes.FrameCount AS 'FL Count', " + \
                    "CAST(TxRes.FrameCount-RxRes.FrameCount AS FLOAT)/TxRes.FrameCount AS 'FLR', " + \
                    "ROUND(MinLatency*1e-3,3) AS 'Min FTD (ms)', " +\
                    "ROUND(AvgLatency*1e-3,3) AS 'Mean FTD (ms)', " + \
                    "ROUND(MaxLatency*1e-3,3) AS 'Max FTD (ms)', " + \
                    "ROUND(MinJitter*1e-3,3) AS 'Min FDV (ms)', " + \
                    "ROUND(AvgJitter*1e-3,3) AS 'Mean FDV (ms)', " + \
                    "ROUND(MaxJitter*1e-3,3) AS 'Max FDV (ms)', " + \
                    "OutSeqFrameCount AS 'Out of Sequence Frame Count', " + \
                    "LateFrameCount AS 'Late Frame Count' " + \
                    "FROM TxEotStreamResults AS TxRes INNER JOIN " + \
                    "RxEotStreamResults AS RxRes ON " + \
                    "TxRes.ParentStreamBlock == RxRes.ParentStreamBlock " + \
                    "INNER JOIN StreamBlock AS Sb ON " + \
                    "TxRes.ParentStreamBlock = Sb.Handle " + \
                    "INNER JOIN StreamBlockLoadProfile As Lp ON " + \
                    "Sb.Handle||','||Lp.Handle = " + \
                    "(SELECT SourceHnd||','||TargetHnd " + \
                    "FROM RelationTable WHERE " + \
                    "Type='AffiliationStreamBlockLoadProfile') " + \
                    "WHERE Sb.Handle == " + sb_hnd
            cmd.Set('SqlQuery', query)
    return True


def on_complete(failed_commands):
    return True


def reset():
    return True
