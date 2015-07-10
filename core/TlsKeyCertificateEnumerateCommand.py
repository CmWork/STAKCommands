from StcIntPythonPL import *
from spirent.core.utils.CommonUtilities import GetFileListFromDir
import traceback
from TlsConstants import *

global logger
logger = PLLogger.GetLogger('spirent.core')


def run(Port):
    try:
        thisCmd = CHandleRegistry.Instance().Find(__commandHandle__)
        portObj = CHandleRegistry.Instance().Find(Port)
        if portObj and not portObj.Get('online'):
            return False

        fileList = GetFileListFromDir([Port], KEY_ROOT, True)
        logger.LogDebug(str(fileList))

        privateList = []
        certificateList = []
        caCertificateList = []
        currentList = privateList
        foundReqDir = False
        # The files get returned in the following format.
        #    /dir1:
        #    file1
        #    file2
        #    /dir2:
        #    file3
        #    file4
        # A list of filenames is returned for a single directory.
        for file in fileList:
            isDir = False
            if file == '':
                continue
            if file.endswith(PRIVATE_KEY_LOC + ':'):
                foundReqDir = True
                isDir = True
                currentList = privateList
            elif file.endswith(CERTIFICATE_LOC + ':'):
                foundReqDir = True
                isDir = True
                currentList = certificateList
            elif file.endswith(CA_CERTIFICATE_LOC + ':'):
                foundReqDir = True
                isDir = True
                currentList = caCertificateList
            elif file.endswith(':'):  # Ignore other dirs
                isDir = True
                foundReqDir = False
            if foundReqDir and not isDir:
                currentList.append(file)

        logger.LogDebug('Private keys ' + str(privateList))

        logger.LogDebug('Cerificates ' + str(certificateList))

        logger.LogDebug('CA Certificates ' + str(caCertificateList))

        physPort = portObj.GetObject('physicalport', RelationType.ReverseDir('PhysicalLogical'))
        physPg = physPort.GetObject('physicalportgroup', RelationType.ReverseDir('ParentChild'))
        physTm = physPg.GetObject('physicaltestmodule', RelationType.ReverseDir('ParentChild'))

        if privateList:
            thisCmd.SetCollection('PrivateKeyFiles', privateList)
            physTm.SetCollection('TlsPrivateKeyFiles', privateList)
        if certificateList:
            thisCmd.SetCollection('CertificateFiles', certificateList)
            physTm.SetCollection('TlsCertificateFiles', certificateList)
        if caCertificateList:
            thisCmd.SetCollection('CaCertificateFiles', caCertificateList)
            physTm.SetCollection('TlsCaCertificateFiles', caCertificateList)

        return True

    except:
        stack_trace = traceback.format_exc()
        logger.LogError('Exception caught:' + stack_trace)
        return False


def validate(Port):
    return ''


def reset():
    return True
