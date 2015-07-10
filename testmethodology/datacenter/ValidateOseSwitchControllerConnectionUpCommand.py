from __future__ import print_function
from StcIntPythonPL import *
import os.path
import traceback

logger = PLLogger.GetLogger('methodology')


def GetDrvValue(drvName, drvColumnIndex):
    try:
        ctor = CScriptableCreator()
        project = CStcSystem.Instance().GetObject('project')

        drv = None
        rdList = project.GetObjects('dynamicresultview')
        for rd in rdList:
            if rd.Get('Name') == drvName:
                drv = rd

        if drv is None:
            raise Exception('Invalid Dynamic result view name. Name:' + drvName)

        if drv.Get('resultstate') != 'SUBSCRIBED':
            cmd = ctor.CreateCommand('SubscribeDynamicResultViewCommand')
            cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
            cmd.Execute()
            cmd.MarkDelete()
        else:
            cmd = ctor.CreateCommand('UpdateDynamicResultViewCommand')
            cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
            cmd.Execute()
            cmd.MarkDelete()

        actualList = []

        if drv.Get('ResultCount') == 0:
            raise Exception('Unexpeted Drv stream result count.')

        rdList = drv.GetObject('PresentationResultQuery').GetObjects('resultviewdata')
        for rd in rdList:
            dataList = rd.GetCollection('ResultData')
            actualList.append(dataList[drvColumnIndex])
        logger.LogInfo('Conn drop list: '+str(actualList))
        return actualList

    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        return []


def validate(Iteration, OseDevice):
    logger.LogInfo(" Validate ValidateOseSwitchControllerConnectionUpCommand")
    handleReg = CHandleRegistry.Instance()
    device = handleReg.Find(OseDevice)
    if device is None or device.GetObject('OseSwitchConfig') is None:
        return 'Invalid Ose device'
    return ""


def reset():
    return True


def run(Iteration, OseDevice):
    logger.LogInfo(" Run ValidateOseSwitchControllerConnectionUpCommand")
    try:
        handleReg = CHandleRegistry.Instance()
        device = handleReg.Find(OseDevice)

        thisCmd = handleReg.Find(__commandHandle__)
        # Get controller switch connection loss counter from the DRV, 0 is the index
        countList = GetDrvValue('ose-traffic', 0)
        droppedConnCount = sum([int(val) for val in countList])

        oseObj = device.GetObject('OseSwitchConfig')
        traffObj = oseObj.GetObject('OseTrafficConfig')

        stcSys = CStcSystem.Instance()
        # Temp solution to write output to a file and read it to show in the UI
        resultFilename = os.path.join(stcSys.GetLogOutputPath(), 'OsePacketInResults.csv')
        logger.LogInfo(resultFilename)
        with open(resultFilename, 'w+' if Iteration == 1 else 'a+') as resultFile:
            cmulRate = int(device.Get('DeviceCount')) * int(traffObj.Get('TrafficFramesPerSecond'))
            logger.LogInfo(str(cmulRate))
            print(Iteration, device.Get('DeviceCount'), traffObj.Get('TrafficFrameSize'),
                  cmulRate, 'Failure' if droppedConnCount > 0 else 'Success',
                  sep=',', end='\n', file=resultFile)
            resultFile.flush()

        logger.LogInfo('Num conn dropped ' + str(droppedConnCount))
        thisCmd.Set('Verdict', droppedConnCount > 0)
    except:
        stack_trace = traceback.format_exc()
        logger.LogError('Exception caught ' + stack_trace)
        return False
    return True
