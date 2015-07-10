"""VDS STAK Library"""

import urllib2
import json
import time

VER = 'V1'


class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""

    def __init__(self, url, method, data=None, headers=None,
                 origin_req_host=None, unverifiable=False):
        self._method = method
        if data is None:
            data = json.dumps({})
        if headers is None:
            headers = {}
        urllib2.Request.__init__(self, url, data, headers,
                                 origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


def do_retry(url):
    """poll the retry url, returns far side dict"""
    while True:
        response = None
        try:
            response = urllib2.urlopen(url)
            if response is not None and hasattr(response, 'getcode'):
                if response.getcode() == 202:  # not complete
                    time.sleep(2)
                    continue
                if response.getcode() == 204:  # no data
                    return ''
            try:
                return json.loads(response.read())
            except (ValueError, TypeError, StopIteration) as ex:
                raise
        except (urllib2.HTTPError, urllib2.URLError) as ex:
            if hasattr(ex, 'code'):
                if str(ex.code) == 202:  # not complete
                    continue
        finally:
            if response is not None and hasattr(response, 'close'):
                response.close()
        raise


def do_vds_command(request, do_json=True, data=None):
    """issue urllib2 request, returns far side dict"""
    response = None
    try:
        response = urllib2.urlopen(request, data)
        if response is not None and hasattr(response, 'getcode'):
            if response.getcode() == 202:  # not complete
                # JSONDecodeError or KeyError here forwarded below
                info = json.loads(response.read())
                url = info['task-url']
                return do_retry(url)
            if response.getcode() == 204:  # no data from DELETE
                return ''
        try:
            if do_json:
                return json.loads(response.read())
            return response.read()
        except (ValueError, TypeError,
                StopIteration, AttributeError) as ex:
            raise
    except (urllib2.HTTPError, urllib2.URLError) as ex:
        try:
            if not hasattr(ex, 'read'):
                msg = ex.message
                raise
            msg = ex.read()
            msg = json.loads(msg)
            if 'detail' in msg:
                msg = msg['detail']  # json validation error
            else:
                if 'message' in msg:
                    msg = msg['message']  # vds error
                else:
                    msg = str(ex)
            # VDS level exception with useful diagnostics
            ex.message = msg
            raise
        except (ValueError, TypeError, StopIteration, KeyError):
            # JSONDecodeError inherits from ValueError
            # Django server error
            # ex.read() returned a useless web page, not a json string
            if len(ex.message) == 0:
                ex.message = 'Exception, no details available'
            raise ex
    finally:
        if response is not None and hasattr(response, 'close'):
            response.close()
    raise


def build_headers(credentials = {}):
    """Build dict of headers to send for VDS commands"""
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json',
        'X-SPIRENT-VDS-API-VERSION': VER,
    }
    headers['X-SPIRENT-VDS-PROVIDER'] = credentials.get('provider', None)
    headers['X-SPIRENT-VDS-PROVIDER-SERVER'] = credentials.get('provider_server', None)
    headers['X-SPIRENT-VDS-PROVIDER-USER'] = credentials.get('provider_user', None)
    headers['X-SPIRENT-VDS-PROVIDER-PASSWORD'] = credentials.get('provider_password', None)
    headers['X-SPIRENT-VDS-PROVIDER-TENANT'] = credentials.get('provider_tenant', None)

    return headers


def listvirtualmachines(server, port, credentials):
    """Get VM list returns list of dicts with vmIds, vmNames"""
    url = 'http://{0}:{1}/api/virtualmachines/'.format(
        server, port)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def listimages(server, port, credentials):
    """Get Image list returns list of dicts with imageIds, imageNames"""
    url = 'http://{0}:{1}/api/images/'.format(server, port)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def listnetworks(server, port, credentials):
    """Get Network list returns list of dicts with networkIds, networkNames"""
    url = 'http://{0}:{1}/api/networks/'.format(server, port)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def listsizes(server, port, credentials):
    """Get Size list returns list of dicts with Ids, Names Ram, Disk, VCPUs"""
    url = 'http://{0}:{1}/api/sizes/'.format(server, port)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def virtualmachineinfo(server, port, credentials, virtual_machine_id):
    """Get VM info returns dict with virtualmachine_found,
    list virtualmachine_ips with ip_address, network_name"""
    # Missing virtual_machine_id will result in a bad address so throw exception
    if not virtual_machine_id:
        raise Exception('Virtual Machine Info requires virtual machine id')
    url = 'http://{0}:{1}/api/virtualmachines/{2}/'.format(
        server, port, virtual_machine_id)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def virtualmachinedestroy(server, port, credentials, virtual_machine_id):
    """Destroy VM returns virtualmachinePresent"""
    # Missing virtual_machine_id will result in a bad address so throw exception
    if not virtual_machine_id:
        raise Exception('Virtual Machine Destroy requires virtual machine id')
    url = 'http://{0}:{1}/api/virtualmachines/{2}/'.format(
        server, port, virtual_machine_id)
    headers = build_headers(credentials)
    request = RequestWithMethod(url, 'DELETE', None, headers)
    return do_vds_command(request)


def virtualmachinecreate(server, port, credentials, virtual_machine_name,
                         size_name, image_name, lserver=None, ntpserver=None,
                         portspeed=None, driver=None, ipaddr=None, netmask=None,
                         gateway=None, telnet=None, network_list=None, 
                         boottimeoutseconds=None, bootcheckseconds=None,
                         host_name=None, datacenter_name=None, datastore_name=None,
                         resource_pool_name=None, count=None):
    """Create VM, returns dict with
       virtualmachine_running, virtualMachine_id"""
    url = 'http://{0}:{1}/api/virtualmachines/'.format(
        server, port)
    headers = build_headers(credentials)
    user_data = []
    if lserver:
        ud_dict = {'name': 'lserver',
                   'value': lserver}
        user_data.append(ud_dict)
    if ntpserver:
        ud_dict = {'name': 'ntp',
                   'value': ntpserver}
        user_data.append(ud_dict)
    if portspeed:
        ud_dict = {'name': 'speed',
                   'value': portspeed}
        user_data.append(ud_dict)
    if driver:
        ud_dict = {'name': 'driver',
                   'value': driver}
        user_data.append(ud_dict)
    if ipaddr:
        ud_dict = {'name': 'ipaddress',
                   'value': ipaddr}
        user_data.append(ud_dict)
    if netmask:
        ud_dict = {'name': 'netmask',
                   'value': netmask}
        user_data.append(ud_dict)
    if gateway:
        ud_dict = {'name': 'gwaddress',
                   'value': gateway}
        user_data.append(ud_dict)
    if telnet:
        ud_dict = {'name': 'telnetd',
                   'value': telnet}
        user_data.append(ud_dict)

    data = {
        'name': virtual_machine_name,
        'size_name': size_name,
        'image_name': image_name,
        'user_data': user_data
    }
    if network_list:
        data['network_names'] = network_list
    if boottimeoutseconds:
        data['boot_timeout_s'] = int(boottimeoutseconds)
    if bootcheckseconds:
        data['boot_check_s'] = int(bootcheckseconds)
    if host_name:
        data['host_name'] = host_name
    if datacenter_name:
        data['datacenter_name'] = datacenter_name
    if datastore_name:
        data['datastore_name'] = datastore_name
    if resource_pool_name:
        data['resource_pool_name'] = resource_pool_name
    if count:
        data['count'] = int(count)
    request = RequestWithMethod(url, 'POST', json.dumps(data), headers)
    return do_vds_command(request)


def virtualmachinereboot(server, port, credentials, virtual_machine_id,
                         boottimeoutseconds=None, bootcheckseconds=None):
    """Reboot VM returns virtualmachineRunning"""
    # Missing virtual_machine_id will result in a bad address so throw exception
    if not virtual_machine_id:
        raise Exception('Virtual Machine Reboot requires virtual machine id')
    url = 'http://{0}:{1}/api/virtualmachines/{2}/reboot/'.format(
        server, port, virtual_machine_id)
    headers = build_headers(credentials)
    data = {}
    if boottimeoutseconds:
        data['boot_timeout_s'] = int(boottimeoutseconds)
    if bootcheckseconds:
        data['boot_check_s'] = int(bootcheckseconds)
    request = RequestWithMethod(url, 'POST', json.dumps(data), headers)
    return do_vds_command(request)


def listversions(server, port):
    """Retrieve the version of the VDS, returns dict"""
    url = 'http://{0}:{1}/api/versions/'.format(server, port)
    headers = {
        'Accept': 'application/json',
        'content-type': 'application/json'
    }
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def listlogs(server, port):
    """Retrieve the log info from the VDS, returns dict"""
    url = 'http://{0}:{1}/api/logfiles/'.format(server, port)
    headers = build_headers()
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request)


def getlog(server, port, logfilename):
    """Retrieve the logfile from the VDS"""
    # Missing logfilename will result in a bad address so throw exception
    if not logfilename:
        raise Exception('Get log requires logfilename')
    url = 'http://{0}:{1}/api/logfiles/{2}/'.format(server, port,
                                                    logfilename)
    headers = {
        'Accept': 'application/octet-stream',
        'X-SPIRENT-VDS-API-VERSION': VER
    }
    request = RequestWithMethod(url, 'GET', None, headers)
    return do_vds_command(request, False)
