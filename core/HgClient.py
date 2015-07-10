from RestUtil import RestUtil
from urllib import urlencode

# HGAPI 1.0 API Paths (No need to change these!)
PUT_TOPOLOGY = '/topology'
DELETE_TOPOLOGY = '/topology'
LIST_TOPOLOGY = '/topology'
AUGMENT_ATTRIBUTES = '/augment/attributes'
GET_NETWORK = '/network'


class HgClient:
    ''' Class to communicate with hyperglance server using Rest API.
        Follows the Hyperglance REST Api documentation
    '''
    def __init__(self, serverUrl, dataSource, apiVersion, apiKey):
        ''' Initializes the obj based on url, api version and api key
            serverUrl: Hg root server url
            dataSource: data source to use for topology
            apiVesion: Hyperglance Api version to use
            apiKey: api key used for authentication
            Exception if no compatible version founds
        '''
        self._dataSource = dataSource
        self._apiVer = apiVersion
        self._apiRoot = serverUrl + '/hgapi'
        self._restUtil = RestUtil(dataSource, apiKey)
        self._url = self._findHgApiUrl(serverUrl)


    def _findHgApiUrl(self, serverUrl):
        ''' Checks server API version and prepares url
                serverUrl: Hg root server url
                Returns the url wiht compatible version
                Exception if no compatible version found
        '''
        version_info = self._restUtil.get(self._apiRoot)
        all_versions = version_info['versions']
        compatible_versions = [v for v in all_versions if v['id'] == self._apiVer]
        if not compatible_versions:
            err = 'HGS Server does not support necessary version: ' + self._apiVer
            raise RuntimeError(err)

        version = compatible_versions[0]
        path = version['path']
        if path.endswith('/'):
            path = path[:-1]
        url = path if path.startswith('http') else serverUrl + path
        return url


    def addTopology(self, topologyJson):
        ''' Sends topology to the server
                topologyJson: topology json object to send
                Returns response json object
                Raises URL/HTTP exception on errors
        '''
        response = self._restUtil.put(self._url + PUT_TOPOLOGY, topologyJson)
        return response


    def getTopology(self):
        ''' Gets all the topologyies contributed by this data source
                Returns topologies response json object
                Raises URL/HTTP exception on errors
        '''
        response = self._restUtil.get(self._url + LIST_TOPOLOGY)
        return response


    def deleteTopology(self, topologyName):
        ''' Deleates a topology
                topologyName: name of the topology to delete
                Raises URL/HTTP exception on errors
        '''
        self._restUtil.delete(self._url + DELETE_TOPOLOGY + '?' +
                              urlencode({'name': topologyName}))


    def updateAttributes(self, attributeJson):
        ''' Updates the entities attributes only
                attributeJson: attributes json object
                Raises URL/HTTP exception on errors
        '''
        self._restUtil.put(self._url + AUGMENT_ATTRIBUTES, attributeJson)


    def getNetwork(self, dataSource=None):
        ''' Gets the whole network of topologies
                dataSource: data source name to get the topologies,
                            set None to get topologies from all datasource
                Returns the whole network json object
                Raises URL/HTTP exception on errors
        '''
        response = self._restUtil.get(self._url + GET_NETWORK +
                                      ('?' + urlencode({'datasource': dataSource}))
                                      if dataSource else '')
        return response


    # def updateTopology(self, nodeKey, attrsJsonArray)
    #    augmentAttrs =
