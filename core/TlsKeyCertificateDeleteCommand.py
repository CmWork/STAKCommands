from StcIntPythonPL import *
import traceback
from spirent.core.utils.scriptable import AutoCommand
from TlsConstants import MAP_FILE_TO_TYPE_LOC

global logger
logger = PLLogger.GetLogger('spirent.core')


class TlsKeyCertificateDeleteCommandHelper:
    def __init__(self):
        self._portGroupSet = set()
        self._isUnitTest = False

    def SetPortGroupHandles(self, portList):
        for port in portList:
            if port.Get('online') or self._isUnitTest:
                physPort = port.GetObject('PhysicalPort', RelationType.ReverseDir("PhysicalLogical"))
                if physPort is None:
                    logger.LogError('Invalid handle for the physical port')
                else:
                    self._portGroupSet.add(physPort.GetParent().GetObjectHandle())
                    logger.LogDebug('_portGroupSet:' + str(len(self._portGroupSet)))

    def GetPortGroupSet(self):
        return self._portGroupSet


def run(PortList, FileNameList, FileType):
    try:
        logger.LogDebug('Instantiating TlsKeyCertificateDeleteCommandHelper')
        tlsCmdHelper = TlsKeyCertificateDeleteCommandHelper()
        tlsCmdHelper.SetPortGroupHandles(CCommandEx.ProcessInputHandleVec('Port', PortList))
        if not tlsCmdHelper.GetPortGroupSet():
            return False

        with AutoCommand('DeleteFileCommand') as deleteFileCmd:
            for portGroupHnd in tlsCmdHelper.GetPortGroupSet():
                portGroup = CHandleRegistry.Instance().Find(portGroupHnd)
                if portGroup.IsTypeOf('PhysicalPortGroup'):
                    physTm = portGroup.GetObject('physicaltestmodule', RelationType.ReverseDir('ParentChild'))
                    if FileType in 'PRIVATE_KEY':
                        checkPrivateList = physTm.GetCollection('TlsPrivateKeyFiles')
                        for aFile in FileNameList:
                            if aFile in checkPrivateList:
                                checkPrivateList.remove(aFile)
                        physTm.SetCollection('TlsPrivateKeyFiles', checkPrivateList)
                    elif FileType in 'CERTIFICATE':
                        checkCertList = physTm.GetCollection('TlsCertificateFiles')
                        for aFile in FileNameList:
                            if aFile in checkCertList:
                                checkCertList.remove(aFile)
                        physTm.SetCollection('TlsCertificateFiles', checkCertList)
                    else:
                        checkCaCertList = physTm.GetCollection('TlsCaCertificateFiles')
                        for aFile in FileNameList:
                            if aFile in checkCaCertList:
                                checkCaCertList.remove(aFile)
                        physTm.SetCollection('TlsCaCertificateFiles', checkCaCertList)

            for file in FileNameList:
                logger.LogInfo(file)
                deleteFileCmd.Reset()
                deleteFileCmd.SetCollection('EquipmentList', list(tlsCmdHelper.GetPortGroupSet()))
                deleteFileCmd.Set('FileName', (MAP_FILE_TO_TYPE_LOC[FileType] + '/' + file))
                deleteFileCmd.Execute()

        logger.LogInfo('Files successfully Deleted')
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