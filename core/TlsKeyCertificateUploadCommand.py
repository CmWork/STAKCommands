from StcIntPythonPL import *
import traceback
import os
from spirent.core.utils.CommonUtilities import *
from collections import defaultdict
from spirent.core.utils.scriptable import AutoCommand
from TlsConstants import MAP_FILE_TO_TYPE_LOC

global logger
logger = PLLogger.GetLogger('spirent.core')


class TlsKeyCertificateUploadCommandHelper:
    def __init__(self):
        self._portGroupHndToPortHndSetDict = defaultdict(set)
        self._isUnitTest = False

    def SetPortGroupHndToPortHndSetDict(self, portList):
        for port in portList:
            if port.Get('online') or self._isUnitTest:
                physPort = port.GetObject('PhysicalPort', RelationType.ReverseDir('PhysicalLogical'))
                if physPort is None:
                    logger.LogError('Invalid handle for the physical port')
                else:
                    self._portGroupHndToPortHndSetDict[physPort.GetParent().GetObjectHandle()].add(port.GetObjectHandle())
                    logger.LogDebug('_portGroupHndToPortHndSetDict:' + str(len(self._portGroupHndToPortHndSetDict)))

    def GetPortGroupHndToPortHndSetDictKeys(self):
        return self._portGroupHndToPortHndSetDict.keys()

    def GetPortHandles(self, portGroup):
        return self._portGroupHndToPortHndSetDict[portGroup]


def run(PortList, FileNameList, FileType):
    try:
        logger.LogDebug('Instantiating TlsKeyCertificateUploadCommandHelper')
        tlsCmdHelper = TlsKeyCertificateUploadCommandHelper()
        tlsCmdHelper.SetPortGroupHndToPortHndSetDict(CCommandEx.ProcessInputHandleVec('Port', PortList))

        if not tlsCmdHelper.GetPortGroupHndToPortHndSetDictKeys():
            return False

        with AutoCommand('DownloadFileCommand') as downloadFileCmd:
            fileList = []
            for origFileName in FileNameList:
                file = CFileManager.GetServerSideInputFilePath(origFileName)
                fileList.append(file)

            requiredSize = sum([os.path.getsize(aFile) for aFile in fileList])
            retValDict = defaultdict(list)
            # CheckDiskSpaceAvailability
            # args:
            # PortGroupHandleList : list of port group handles, ILPathName : IL path to check space,
            # RequiredSize: size(bytes) required
            # returns:
            # A dictionary containing two keys, Success and Failure
            # Success: The value for this key is a list of port group handles for which
            #          space is available for the download
            # Failure: The value for this key is a list of port group handles for which
            #          there isn't enough space on the card for download to be successful
            retValDict = CheckDiskSpaceAvailability(tlsCmdHelper.GetPortGroupHndToPortHndSetDictKeys(), MAP_FILE_TO_TYPE_LOC['PRIVATE_KEY'], requiredSize)
            thisCmd = CHandleRegistry.Instance().Find(__commandHandle__)

            if 'Failure' in retValDict:
                logger.LogDebug('Inside Failure')
                fail = retValDict.get('Failure')
                if fail:
                    failurePortList = []
                    for portGroup in fail:
                        failurePortList.extend(tlsCmdHelper.GetPortHandles(portGroup))
                    # The command contains a list of port handles for which the download failed.
                    # Within a given input list of ports it is possible that some ports may not
                    # have space available for download to succeed. The 'FailurePortList'
                    # communicates this info to the user.
                    # The command status is returned as True
                    thisCmd.SetCollection('FailurePortList', failurePortList)
                    portNameList = []
                    for portHandle in failurePortList:
                        portObject = CHandleRegistry.Instance().Find(portHandle)
                        portNameList.append(portObject.Get('Name'))
                    logger.LogInfo('File transfer failed on the following ports')
                    logger.LogInfo(str(portNameList))
            if 'Success' in retValDict:
                success = retValDict.get('Success')
                for portGroupHnd in success:
                    portGroup = CHandleRegistry.Instance().Find(portGroupHnd)
                    if portGroup.IsTypeOf('PhysicalPortGroup'):
                        physTm = portGroup.GetObject('physicaltestmodule', RelationType.ReverseDir('ParentChild'))
                        if FileType == 'PRIVATE_KEY':
                            checkPrivateList = physTm.GetCollection('TlsPrivateKeyFiles')
                            for aFile in fileList:
                                filePathList = aFile.split("\\")
                                actualFile = filePathList[-1]
                                if actualFile not in checkPrivateList:
                                    checkPrivateList.append(actualFile)
                            physTm.SetCollection('TlsPrivateKeyFiles', checkPrivateList)
                        elif FileType == 'CERTIFICATE':
                            checkCertList = physTm.GetCollection('TlsCertificateFiles')
                            for aFile in fileList:
                                filePathList = aFile.split("\\")
                                actualFile = filePathList[-1]
                                if actualFile not in checkCertList:
                                    checkCertList.append(actualFile)
                            physTm.SetCollection('TlsCertificateFiles', checkCertList)
                        else:
                            checkCaCertList = physTm.GetCollection('TlsCaCertificateFiles')
                            for aFile in fileList:
                                filePathList = aFile.split("\\")
                                actualFile = filePathList[-1]
                                if actualFile not in checkCaCertList:
                                    checkCaCertList.append(actualFile)
                            physTm.SetCollection('TlsCaCertificateFiles', checkCaCertList)
                if success:
                    for aFile in fileList:
                        downloadFileCmd.Reset()
                        downloadFileCmd.Set('DstDir', MAP_FILE_TO_TYPE_LOC[FileType])
                        downloadFileCmd.SetCollection('EquipmentList', success)
                        downloadFileCmd.Set('FileName', aFile)
                        downloadFileCmd.Execute()

        logger.LogInfo('Files successfully transferred')
        return True
    except:
        stack_trace = traceback.format_exc()
        logger.LogError('Exception caught:' + stack_trace)
        return False


def validate(PortList, FileNameList, FileType):
    if not PortList:
        return 'Port list cannot be empty'
    elif not FileNameList:
        return 'File name list cannot be empty'
    else:
        if FileType not in MAP_FILE_TO_TYPE_LOC.keys():
            return 'Invalid file type'
    return ''


def reset():
    return True
