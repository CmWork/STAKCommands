from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
from AclPerformanceData import AclPerformanceData


PKG = 'spirent.methodology'
TTPKG = PKG + '.traffictest'


def SetRotation(tagname, tagged_object_list, params):
    rots = tag_utils.get_tagged_objects_from_string_names('IterRotate')
    if len(rots) == 0:
        return 'Missing IterRotate tagged object.'
    for rot in rots:
        rot.Set('MaxVal', float(len(tagged_object_list) - 1))
        rot.Set('StepVal', float(params))
        rot.Set('MinVal', float(params))
    return ''


def SetRulesFilename(tagname, tagged_object_list, params):
    cmds = tag_utils.get_tagged_objects_from_string_names('RulesFileName')
    if len(cmds) == 0:
        return 'Missing "RulesFileName" tagged command.'
    for cmd in cmds:
        if cmd.IsTypeOf(TTPKG + '.LoadAclTrafficRulesCommand'):
            cmd.Set('RulesFileName', params)
        else:
            return 'Only LoadAclTrafficRulesCommand is supported for RulesFileName.'
    return ''


def SetExpPacketLoss(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_pktloss(int(params))
    return ''


def SetExpMaxLatePacket(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_maxlatepkt(int(params))
    return ''


def SetExpMaxOutOfSeq(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_maxoop(int(params))
    return ''


def SetExpMaxLatency(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_maxlatency(float(params))
    return ''


def SetExpAvgLatency(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_avglatency(float(params))
    return ''


def SetExpMaxJitter(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_maxjitter(float(params))
    return ''


def SetExpAvgJitter(tagname, tagged_object_list, params):
    apd = AclPerformanceData()
    apd.set_exp_avgjitter(float(params))
    return ''


def get_query(is_passthru):
    s = 'Tag.Name = "Good.ttStreamBlock" AND Rx.FrameCount < Tx.FrameCount' \
        if is_passthru else \
        'Tag.Name = "Bad.ttStreamBlock" AND Rx.FrameCount > 0'
    return '''
 SELECT
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN r.OffsetReference LIKE '%dstMac' THEN r.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN r.OffsetReference LIKE '%srcMac' THEN r.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN r.OffsetReference LIKE '%destAddr' THEN r.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN r.OffsetReference LIKE '%sourceAddr' THEN r.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN r.OffsetReference LIKE '%destPort' THEN r.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN r.OffsetReference LIKE '%sourcePort' THEN r.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb JOIN RangeModifier AS r ON Sb.Handle = r.ParentHnd
 WHERE r.ParentHnd in  (SELECT DISTINCT Rm.ParentHnd FROM Tag
 JOIN RelationTable AS Rt ON Tag.Handle = Rt.TargetHnd
 JOIN TxEotStreamResults AS Tx ON Tx.ParentStreamBlock = Rt.SourceHnd
 JOIN RxEotStreamResults AS Rx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Rt.SourceHnd
 WHERE Tx.FrameCount > 0 AND ____where____)
 GROUP BY r.ParentHnd
 '''.replace('____where____', s)


def SetQueries(tagname, tagged_object_list, params):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("AclPerf_ResultsScript.run()")

    apd = AclPerformanceData()
    exp_pktloss = apd.get_exp_pktloss()
    exp_avgjitter = apd.get_exp_avgjitter()
    exp_maxjitter = apd.get_exp_maxjitter()
    exp_avglatency = apd.get_exp_avglatency()
    exp_maxlatency = apd.get_exp_maxlatency()
    exp_maxoop = apd.get_exp_maxoop()
    exp_maxlatepkt = apd.get_exp_maxlatepkt()

    for cmd in tagged_object_list:
        if cmd.IsTypeOf(PKG + '.VerifyDbQueryCommand'):
            is_passthru = tagname.find('Block') == -1
            display_name = 'Verifying Pass Through Traffic Processing' \
                if is_passthru else 'Verifying Blocking Traffic Processing'
            pass_verdict = 'The DUT properly processed all pass through traffic.' \
                if is_passthru else 'The DUT properly processed all blocking traffic.'
            fail_verdict = 'The DUT failed to process some pass through traffic.' \
                if is_passthru else 'The DUT failed to process some blocking traffic.'

            cmd.Set('SqlQuery', get_query(is_passthru))
            cmd.Set('DisplayName', display_name)
            cmd.Set('PassedVerdictExplanation', pass_verdict)
            cmd.Set('FailedVerdictExplanation', fail_verdict)
            cmd.Set('ApplyVerdictToSummary', True)
            cmd.Set('OperationType', 'EQUAL')
            cmd.Set('RowCount', 0L)

        elif cmd.IsTypeOf(PKG + '.VerifyMultipleDbQueryCommand'):
            q_list = []
            display_name_list = []
            pass_list = []
            fail_list = []

            display_name_list.append("RFC4689 Mean Frame Delay Variation (FDV) Results")
            pass_list.append("RFC4689 Mean FDV is within the configured threshold of " +
                             str(exp_avgjitter) + " us.")
            fail_list.append("RFC4689 Mean FDV exceeded the configured threshold of " +
                             str(exp_avgjitter) + " us.")
            q = '''
SELECT
 ROUND(AvgJitter,3) AS 'Mean FDV (us)', '%1' AS 'Mean FDV Threshold (us)',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE ROUND(AvgJitter,3) > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_avgjitter))
            q_list.append(q)

            display_name_list.append("Max Frame Delay Variation (FDV) Results")
            pass_list.append("Max FDV is within the configured threshold of " +
                             str(exp_maxjitter) + " us.")
            fail_list.append("Max FDV exceeded the configured threshold of " +
                             str(exp_maxjitter) + " us.")
            q = '''
SELECT
 ROUND(MaxJitter,3) AS 'Max FDV (us)', '%1' AS 'Max FDV Threshold (us)',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE ROUND(MaxJitter,3) > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_maxjitter))
            q_list.append(q)

            display_name_list.append("Mean Frame Transfer Delay (FTD) Results")
            pass_list.append("Mean FTD is within the configured threshold of " +
                             str(exp_avglatency) + " us.")
            fail_list.append("Mean FTD exceeded the configured threshold of " +
                             str(exp_avglatency) + " us.")
            q = '''
SELECT
 ROUND(AvgLatency,3) AS 'Mean FTD (us)', '%1' AS 'Mean FTD Threshold (us)',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE ROUND(AvgLatency,3) > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_avglatency))
            q_list.append(q)

            display_name_list.append("Max Frame Transfer Delay (FTD) Results")
            pass_list.append("Max FTD is within the configured threshold of " +
                             str(exp_maxlatency) + " us.")
            fail_list.append("Max FTD exceeded the configured threshold of " +
                             str(exp_maxlatency) + " us.")
            q = '''
SELECT
 ROUND(MaxLatency,3) AS 'Max FTD (us)', '%1' AS 'Max FTD Threshold (us)',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE ROUND(MaxLatency,3) > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_maxlatency))
            q_list.append(q)

            display_name_list.append("Frame Loss (FL) Results")
            pass_list.append("Frame Loss Count is within the configured threshold of " +
                             str(exp_pktloss) + ".")
            fail_list.append("Frame Loss Count exceeded the configured threshold of " +
                             str(exp_pktloss) + ".")
            q = '''
SELECT
 Tx.FrameCount - Rx.FrameCount As 'FL Count', '%1' AS 'FL Count Threshold',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE Tx.FrameCount - Rx.FrameCount > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_pktloss))
            q_list.append(q)

            display_name_list.append("Out of Order Frame Results")
            pass_list.append("Out of Order Frame Count is within the configured threshold of " +
                             str(exp_maxoop) + ".")
            fail_list.append("Out of Order Frame Count exceeded the configured threshold of " +
                             str(exp_maxoop) + ".")
            q = '''
SELECT
 OutSeqFrameCount AS 'Out of Order Frame Count', '%1' AS 'Out of Order Frame Count Threshold',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE OutSeqFrameCount > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_maxoop))
            q_list.append(q)

            display_name_list.append("Late Frame Results")
            pass_list.append("Late Frame Count is within the configured threshold of " +
                             str(exp_maxlatepkt) + ".")
            fail_list.append("Late Frame Count exceeded the configured threshold of " +
                             str(exp_maxlatepkt) + ".")
            q = '''
SELECT
 LateFrameCount AS 'Late Frame Count', '%1' AS 'Late Frame Count Threshold',
 Sb.FixedFrameLength AS 'Frame Size (bytes)',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%dstMac' THEN Rm.Data ELSE NULL END) AS 'DST MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%srcMac' THEN Rm.Data ELSE NULL END) AS 'SRC MAC',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destAddr' THEN Rm.Data ELSE NULL END) AS 'DST IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourceAddr' THEN Rm.Data ELSE NULL END) AS 'SRC IP',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%destPort' THEN Rm.Data ELSE NULL END) AS 'DST PORT',
 MAX(CASE WHEN Rm.OffsetReference LIKE '%sourcePort' THEN Rm.Data ELSE NULL END) AS 'SRC PORT'
FROM StreamBlock AS Sb
 JOIN RxEotStreamResults AS Rx ON Rx.ParentStreamBlock = Sb.Handle
 JOIN TxEotStreamResults AS Tx ON Tx.StreamId = Rx.Comp32
 JOIN RangeModifier AS Rm ON Rm.ParentHnd = Sb.Handle
 JOIN RelationTable AS Rt ON Rt.SourceHnd = Rm.ParentHnd
 WHERE LateFrameCount > %1
 GROUP BY Rm.ParentHnd
'''.replace('%1', str(exp_maxlatepkt))
            q_list.append(q)

            cmd.SetCollection('DisplayNameList', display_name_list)
            cmd.SetCollection('PassedVerdictExplanationList', pass_list)
            cmd.SetCollection('FailedVerdictExplanationList', fail_list)
            cmd.SetCollection('SqlQueryList', q_list)
            # cmd.Set('UseMultipleResultsDatabases', False)
        else:
            return 'Unexpected command "' + cmd.GetType() + '" was tagged for SQL query setup.'
    return ''