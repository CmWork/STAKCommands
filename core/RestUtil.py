import urllib2
import base64
import json


class RestUtil:
    ''' Utility class to create http resquests with Basic authetication
        scheme
        All methods raise Urllib2 exceotions URLError or HTTPError
    '''
    def _basic_auth_token(self, user, passwd):
        ''' Creates basic auth header
                user: username
                password: password
                returns the auth header
        '''
        userpasswd_bytes = (user + ':' + passwd).encode('utf-8')
        return base64.b64encode(userpasswd_bytes).decode('ascii')


    def __init__(self, user, password, auth='Basic'):
        ''' Initilizes the object with authentication parameters
            Only basic authetication supported right now
                user: username
                password: password
                auth: authentication scheme
        '''
        self._authHeader = ''
        if(auth == 'Basic'):
            self._authHeader = "Basic " + self._basic_auth_token(user, password)


    def get(self, path):
        ''' Issue the get request
                path: url path to get
                returns response as json or None if no response
        '''
        req = urllib2.Request(url=path, headers={'Authorization': self._authHeader})
        req.get_method = lambda: 'GET'

        resp = urllib2.urlopen(req)

        json_out = resp.read().decode('utf-8')
        return json.loads(json_out) if json_out else None


    def put(self, path, data):
        ''' Issue the put request
                path: url path for put
                data: json object to put
                returns response as json or None if no response
        '''
        json_in = json.dumps(data).encode('utf-8')

        req = urllib2.Request(url=path, data=json_in,
                              headers={'Content-Type': 'application/json',
                                       'Authorization': self._authHeader})
        req.get_method = lambda: 'PUT'
        resp = urllib2.urlopen(req)

        json_out = resp.read().decode('utf-8')
        return json.loads(json_out) if json_out else None


    def delete(self, path):
        ''' Issue the delete request
                path: url path for delete
        '''

        req = urllib2.Request(url=path, headers={'Authorization': self._authHeader})
        req.get_method = lambda: 'DELETE'

        urllib2.urlopen(req)
