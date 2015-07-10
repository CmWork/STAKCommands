from StcIntPythonPL import *
from HgClient import HgClient
import traceback
from urllib2 import URLError, HTTPError
import json


def getLogger():
    logger = PLLogger.GetLogger('spirent.core.HyperglanceCommand')
    return logger


def validate(CmdType, NodeIdentifier, CmdParam):
    if not CmdType:
        return 'No command specified'
    if not NodeIdentifier and not CmdParam and \
            CmdType not in ['CHECK_CONNECTION', 'GET_TOPOLOGY']:
        return 'Empty command parameters'
    return ''


def run(CmdType, NodeIdentifier, CmdParam):
    if '__commandHandle__' in globals():
        thisCmd = CHandleRegistry.Instance().Find(__commandHandle__)
    try:
        serverUrl = 'https://127.0.0.1'
        dataSource = 'Spirent-Testcenter'
        apiKey = '135e9b26-282e-4d7e-82e7-6fa07c116e26'
        apiVersion = '1.0'
        response = None
        hgClient = HgClient(serverUrl, dataSource, apiVersion, apiKey)
        if CmdType == 'ADD_TOPOLOGY':
            responseJson = hgClient.addTopology(json.loads(CmdParam))
            response = json.dumps(responseJson)
        elif CmdType == 'UPDATE_TOPOLOGY':
            responseJson = hgClient.addTopology(json.loads(CmdParam))
            response = json.dumps(response)
        elif CmdType == 'GET_TOPOLOGY':
            responseJson = hgClient.getTopology()
            response = json.dumps(responseJson)
        elif CmdType == 'DELETE_TOPOLOGY':
            response = str(hgClient.deleteTopology(NodeIdentifier))
        elif CmdType == 'UPDATE_ATTRIBUTES':
            response = str(hgClient.updateAttributes(json.loads(CmdParam)))
        elif CmdType == 'GET_NETWORK':
            responseJson = hgClient.getNetwork()
            response = json.dumps(responseJson)

        elif CmdType == 'CHECK_CONNECTION':
            # HgClient constructor does connection testing
            response = 'True'
        else:
            raise RuntimeError('Unknown Hyperglance command')

        if thisCmd is not None:
            thisCmd.Set('Status', 'Hyperglance Command'
                        ' completed')
            thisCmd.Set('Response', response)

        getLogger().LogDebug('Hyperglance response: ' + str(response))

        return True
    except HTTPError as e:
        # For connection check return true on HTTP 404 error
        if e.code == 404 and cmdType == 'CHECK_CONNECTION':
            thisCmd.Set('Response', 'False')
            return True
        getLogger().LogError('HTTP Error: Code ' + str(e.code) +
                             ' :' + str(e.reason))
        return False
    except URLError as e:
        # For connection check return true on URL error
        if CmdType == 'CHECK_CONNECTION':
            thisCmd.Set('Response', 'False')
            return True
        getLogger().LogError('URL Error:' + str(e.reason))
        return False
    except RuntimeError as e:
        getLogger().LogError('Runtime Error: ' + str(e))
        return False
    except Exception:
        getLogger().LogError('Error: unhandled exception:\n' +
                             traceback.format_exc())
        return False


def reset():
    return True
