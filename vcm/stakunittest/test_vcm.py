from StcIntPythonPL import (CScriptableCreator)
from mock import MagicMock
import urllib2
import httplib
import json
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'vcm'))
import vcmlib
import ListVirtualMachinesCommand
import ListImagesCommand
import ListNetworksCommand
import ListSizesCommand
import VirtualMachineCreateCommand
import VirtualMachineInfoCommand
import VirtualMachineRebootCommand
import VirtualMachineDestroyCommand
import ListVersionsCommand
import ListLogsCommand
import GetLogCommand

class Response:
    """mock urllib2 urlopen response"""
    def __init__(self, result, code):
        self.result = result
        self.code = str(code)

    def getcode(self):
        """returns http code string"""
        return self.code

    def read(self):
        """returns json string"""
        return self.result

    def close(self):
        """returns nothing"""
        pass


def do_test(command_name, command, arguments, result, expected):
    """returns nothing"""
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(command_name)
    assert(cmd)
    command.get_this_cmd = MagicMock(return_value=cmd)
    saveurlopen = urllib2.urlopen
    urllib2.urlopen = MagicMock(return_value=result)
    command.run(**arguments)
    urllib2.urlopen = saveurlopen
    for element in expected:
        if element['collection']:
            assert element['val'] in cmd.GetCollection(element['key'])
        elif element['key'] == 'plaintext':
            assert element['val'] == result.read()
        elif type(element['val']) is bool:
            assert element['val'] == cmd.Get(element['key'])
        else:
            assert element['val'] in cmd.Get(element['key'])

    assert(cmd.Reset())
    for element in expected:
        if element['collection']:
            assert element['val'] not in cmd.GetCollection(element['key'])
        elif element['key'] == 'plaintext':
            pass
        elif type(element['val']) is bool:
            assert element['val'] is not cmd.Get(element['key'])
        else:
            assert element['val'] not in cmd.Get(element['key'])


def test_listvms(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1'
                }
    result = { 'virtualmachines': [ { 'id': 'id1', 'name': 'name1' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'VmIdList', 'val': 'id1', 'collection': True },
                { 'key': 'VmNameList', 'val': 'name1', 'collection': True } ]
    res = Response(result, 200)
    command = ListVirtualMachinesCommand
    command_name = 'spirent.vcm.ListVirtualMachinesCommand'
    do_test(command_name, command, arguments, res, expected)


def test_listimages(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1'
                }
    result = { 'images': [ { 'id': 'id1', 'name': 'name1' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'ImageIdList', 'val': 'id1', 'collection': True },
                { 'key': 'ImageNameList', 'val': 'name1', 'collection': True } ]
    res = Response(result, 200)
    command = ListImagesCommand
    command_name = 'spirent.vcm.ListImagesCommand'
    do_test(command_name, command, arguments, res, expected)


def test_listnetworks(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1'
                }
    result = { 'networks': [ { 'id': 'id1', 'label': 'name1' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'NetworkIdList', 'val': 'id1', 'collection': True },
                { 'key': 'NetworkNameList', 'val': 'name1', 'collection': True } ]
    res = Response(result, 200)
    command = ListNetworksCommand
    command_name = 'spirent.vcm.ListNetworksCommand'
    do_test(command_name, command, arguments, res, expected)

def test_listsizes(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1'
                }
    result = { 'sizes': [ { 'id': 'id1', 'name': 'name1',
                           'ram': '1234', 'disk': '12345',
                           'vcpus': '4' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'SizeIdList', 'val': 'id1', 'collection': True },
                { 'key': 'SizeNameList', 'val': 'name1', 'collection': True },
                { 'key': 'RamList', 'val': '1234', 'collection': True },
                { 'key': 'DiskList', 'val': '12345', 'collection': True },
                { 'key': 'VcpusList', 'val': '4', 'collection': True } ]
    res = Response(result, 200)
    command = ListSizesCommand
    command_name = 'spirent.vcm.ListSizesCommand'
    do_test(command_name, command, arguments, res,  expected)


def test_create(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1',
                 'VirtualMachineName': 'virtualmachinename1',
                 'SizeName': 'sizename1',
                 'ImageName': 'imagename1',
                 'LicenseServer': '10.14.16.26',
                 'NtpServer': '10.109.134.17',
                 'PortSpeed': '1G',
                 'Driver': 'sockets',
                 'IpAddr': '10.10.10.10',
                 'Netmask': '255.255.255.0',
                 'Gateway': '10.10.10.1',
                 'Telnet': 'on',
                 'NetworkList': [ 'net1'],
                 'BootTimeoutSeconds': 120,
                 'BootCheckSeconds': 5,
                 'HostName': '10.100.239.31',
                 'DatacenterName': 'TestEnvironment',
                 'DatastoreName': 'VMware iSCSI',
                 'ResourcePoolName': 'dev_net_1',
                 'Count': 1
                }

    result = { 'virtualmachine_running': [True], 'id': ['id1'], 'url': ['url1'] }
    result = json.dumps(result)
    expected = [ { 'key': 'VirtualMachineRunning', 'val': True, 'collection': True },
                { 'key': 'VirtualMachineId', 'val': 'id1', 'collection': True },
                { 'key': 'Url', 'val': 'url1', 'collection': True } ]
    res = Response(result, 200)
    command = VirtualMachineCreateCommand
    command_name = \
        'spirent.vcm.VirtualMachineCreateCommand'
    do_test(command_name, command, arguments, res, expected)


def test_vm_info(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1',
                 'VirtualMachineId': 'vm1',
                }
    result = { 'virtualmachine_found': True, 'virtualmachine_ips':
              [ { 'ip_address': '10.10.10.10', 'network_name': 'net1' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'VirtualMachineFound', 'val': True, 'collection': False },
                { 'key': 'AddrList', 'val': '10.10.10.10', 'collection': True },
                { 'key': 'NetworkList', 'val': 'net1', 'collection': True } ]
    res = Response(result, 200)
    command = VirtualMachineInfoCommand
    command_name = 'spirent.vcm.VirtualMachineInfoCommand'
    do_test(command_name, command, arguments, res, expected)


def test_vm_reboot(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1',
                 'VirtualMachineId': 'vm1',
                 'BootTimeoutSeconds': 120,
                 'BootCheckSeconds': 5
                }
    result = { 'virtualmachine_running': True }
    result = json.dumps(result)
    expected = [ { 'key': 'VirtualMachineRunning', 'val': True, 'collection': False } ]
    res = Response(result, 200)
    command = VirtualMachineRebootCommand
    command_name = 'spirent.vcm.VirtualMachineRebootCommand'
    do_test(command_name, command, arguments, res, expected)


def test_vm_destroy(stc):
    """returns nothing"""
    arguments = {'Server': 'server1',
                 'Port': 1234,
                 'Provider': 'Simulator',
                 'ProviderServer': 'Simulator',
                 'ProviderUser': 'user1',
                 'ProviderPassword': 'password1',
                 'ProviderTenant': 'tenant1',
                 'VirtualMachineId': 'vm1'
                }
    result = { 'virtualmachine_present': False }
    result = json.dumps(result)
    expected = [ { 'key': 'VirtualMachinePresent', 'val': False, 'collection': False } ]
    res = Response(result, 200)
    command = VirtualMachineDestroyCommand
    command_name = 'spirent.vcm.VirtualMachineDestroyCommand'
    do_test(command_name, command, arguments, res, expected)


def test_list_versions(stc):
    """returns nothing"""
    arguments = { 'Server': 'server1', 'Port': 1234 }
    result = { 'api_versions': [ { 'status': 'CURRENT', 'version': 'v1' },
                                { 'status': 'EXPERIMENTAL', 'version': 'v1.1' } ],
              'product_version': { 'version': '4.50.62' } }
    result = json.dumps(result)
    expected = [ { 'key': 'StatusList', 'val': 'CURRENT', 'collection': True },
                { 'key': 'VersionList', 'val': 'v1', 'collection': True },
                { 'key': 'ProductVersion', 'val': '4.50.62', 'collection': False } ]
    res = Response(result, 200)
    command = ListVersionsCommand
    command_name = 'spirent.vcm.ListVersionsCommand'
    do_test(command_name, command, arguments, res, expected)


def test_list_logs(stc):
    """returns nothing"""
    arguments = { 'Server': 'server1', 'Port': 1234 }
    result = { 'log_files': [ { 'url': 'http://foo', 'log_file_size': '100',
                               'log_file_name': 'vcm.log' } ] }
    result = json.dumps(result)
    expected = [ { 'key': 'UrlList', 'val': 'http://foo', 'collection': True },
                { 'key': 'LogSizeList', 'val': '100', 'collection': True },
                { 'key': 'LogNameList', 'val': 'vcm.log', 'collection': True } ]
    res = Response(result, 200)
    command = ListLogsCommand
    command_name = 'spirent.vcm.ListLogsCommand'
    do_test(command_name, command, arguments, res, expected)


def test_get_log(stc):
    """returns nothing"""
    arguments = { 'Server': 'server1', 'Port': 1234,
                 'LogFileName': 'vcm.log', 'SavePath': '/tmp' }
    text = 'This is test log file text'
    result = text
    expected = [ { 'key': 'plaintext', 'val': text, 'collection': False } ]
    res = Response(result, 200)
    command = GetLogCommand
    command_name = 'spirent.vcm.GetLogCommand'
    do_test(command_name, command, arguments, res, expected)

def test_json_exception(stc):
    """returns nothing"""
    result = 'bad json'
    res = Response(result, 200)
    saveurlopen = urllib2.urlopen
    urllib2.urlopen = MagicMock(return_value=res)
    try:
        vcmlib.listversions('server1', 1234)
        urllib2.urlopen = saveurlopen
        assert(0), 'expected a ValueError exception'
    except ValueError as ex:
        urllib2.urlopen = saveurlopen

def test_url_exception(stc):
    """returns nothing"""
    # not mocked to generate URLError 
    try:
        vcmlib.listversions('badserver', 1234)
        assert(0), 'expected an urllib2.URLError exception'
    except urllib2.URLError as ex:
        pass

def test_http_exception(stc):
    """returns nothing"""
    # not mocked to generate InvalidURL
    try:
        vcmlib.listversions('badserver', 'bad port')
        assert(0), 'expected an httplib.InvalidURL exception'
    except httplib.InvalidURL as ex:
        pass
