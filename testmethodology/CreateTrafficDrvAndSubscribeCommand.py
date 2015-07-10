from StcIntPythonPL import *
import utils.methodology_utils as methodology_utils


def validate(TopologyProfile):
    return ""


def run(TopologyProfile):
    logger = PLLogger.GetLogger('methodology')
    logger.LogInfo(
        '**************** Running CreateTrafficDrvAndSubscribeCommand ***************')

    project = CStcSystem.Instance().GetObject('project')
    ctor = CScriptableCreator()
    hndReg = CHandleRegistry.Instance()

    drv = ctor.Create('DynamicResultView', project)
    if drv is None:
        logger.LogWarn('*** No DynamicResultView created')
    drv.Set("Name", "TestMeth - FrameLoss DRV")

    prq = ctor.Create('PresentationResultQuery', drv)
    if prq is None:
        logger.LogWarn('*** No PRQ created')

    # Get the topologyProfile
    # In case we do NOT want to use chaining to get TopologyProfile; use following line
    # topoProfile = project.GetObject("TopologyProfile")

    topoProfile = hndReg.Find(int(TopologyProfile))
    logger.LogInfo("TopologyProfile handle = " + str(TopologyProfile))
    if (topoProfile is None):
        return False

    # Use the ApplicationProfile to get the streamblocks from which we can get the ports
    portHdlList = []
    trfProfile = topoProfile.GetObject("TrafficProfile", RelationType("AssociatedTrafficProfile"))
    apProfileList = trfProfile.GetObjects("ApplicationProfile")
    for apProfile in apProfileList:
        streamBlockList = apProfile.GetObjects("StreamBlock", RelationType("GeneratedObject"))
        for sb in streamBlockList:
            if (sb is not None):
                port = sb.GetParent()
                if (port is not None and port not in portHdlList):
                    portHdlList.append(port.GetObjectHandle())

    # Hardcode the to be subscribed result attributes
#     FIX ME: 'StreamBlock.OutSeqFrameCount' need to have different "Counter Mode"
    resultPropList = ['StreamBlock.Name', 'StreamBlock.TxFrameCount', 'StreamBlock.RxFrameCount',
                      'StreamBlock.Frameloss', 'StreamBlock.DroppedFramePercent',
                      'StreamBlock.AvgLatency']
    prq.SetCollection('SelectProperties', resultPropList)
    prq.SetCollection('FromObjects', portHdlList)

    subCmd = ctor.CreateCommand('subscribeDynamicResultView')
    subCmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
    subCmd.Execute()

    methodology_utils.set_drv_handle(drv.GetObjectHandle())
    methodology_utils.set_subDrvCmd_handle(subCmd.GetObjectHandle())

    drv_deadStreams = ctor.Create('DynamicResultView', project)
    if drv_deadStreams is None:
        logger.LogWarn('*** No DynamicResultView (Dead Streams) created')
    drv_deadStreams.Set("Name", "TestMeth - DeadStreams DRV")

# See notes in "FIXME" below
# prq_deadStreams = ctor.Create('PresentationResultQuery', drv_deadStreams)
# if prq_deadStreams is None:
# logger.LogWarn('*** No PRQ (Dead Streams) created')

# Hardcode the to be subscribed result attributes
# resultPropList = ['StreamBlock.Name', 'StreamBlock.StreamId', 'StreamBlock.PortName',
# 'StreamBlock.ActualRxPortName',
# 'StreamBlock.TxFrameCount', "StreamBlock.RxSigFrameCount",
# "StreamBlock.TxBitRate", "StreamBlock.RxBitRate", "StreamBlock.IsExpected"]
# prq_deadStreams.SetCollection('SelectProperties', resultPropList)
# prq_deadStreams.SetCollection('FromObjects', portHdlList)


# FIXME:
# A single where clause testing tx, rx, and expect
# (AND'ing everything together) does not return any results
# This clause will work:
# prq_deadStreams.SetCollection("WhereConditions",
# ["StreamBlock.TxFrameCount > 0", "StreamBlock.RxSigFrameCount = 0 AND
# StreamBlock.IsExpected = 1"])
#
# For now though, Kahou says to leave off the TxFrameCount as the
# predefined DeadStream DRV also does not use it.
# prq_deadStreams.SetCollection("WhereConditions", ["StreamBlock.RxSigFrameCount = 0 AND
# StreamBlock.IsExpected = 1"])
#
#
# Additional Notes:
# Rahul says to use the existing DeadStreams template and
# load from it rather than creating a new DRV.
#
    cmd = ctor.CreateCommand("LoadFromTemplateCommand")
    cmd.Set("Config", drv_deadStreams.GetObjectHandle())
    cmd.Set("TemplateUri", "/Result Views/Stream Results/Dead Stream Results.xml")
    cmd.Execute()
    cmd.MarkDelete()

    prq_deadStreams = drv_deadStreams.GetObject("PresentationResultQuery")
    if (prq_deadStreams is not None):
        prq_deadStreams.SetCollection("FromObjects", portHdlList)
    else:
        logger.LogWarn(
            "CreateTrafficDrvAndSubscribeCommand: could not find a PresentationResultQuery"
            "for Dead Stream DRV")

    subDeadStreamsCmd = ctor.CreateCommand('subscribeDynamicResultView')
    subDeadStreamsCmd.Set('DynamicResultView', str(drv_deadStreams.GetObjectHandle()))
    subDeadStreamsCmd.Execute()

    methodology_utils.set_drv_deadStreams_handle(drv_deadStreams.GetObjectHandle())
    methodology_utils.set_subDeadStreamsDrvCmd_handle(subDeadStreamsCmd.GetObjectHandle())

    # Prepare the result file suffix (formatted time)
    methodology_utils.set_iteration_file_suffix()

    return True


def reset():
    return True
