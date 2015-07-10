from StcIntPythonPL import *
import pytest
from ..utils.CommandUtils import exec_command
import json
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.utils import tag_utils


test_config = '''{
   "topology_nodes": [
         {
            "id": "83749364",
            "name": "West",
            "subnet_configs": [
               {
                  "subnet": {
                     "device_count_per_port": 1,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "1.1.1.10",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "1.1.1.1",
                        "ipv4_port_step": "0.0.1.0",
                        "ipv4_step": "0.0.0.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "_type": "Profile::UniqueMacConfig"
                     },
                     "name": "net1",
                     "id": "1234"
                  },
                  "ports": [{"id": "4000", "location": "//1.1.1.1/1/1"}]
               },
               {
                  "subnet": {
                     "device_count_per_port": 1,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "1.1.1.10",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "1.1.1.1",
                        "ipv4_port_step": "0.0.1.0",
                        "ipv4_step": "0.0.0.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "_type": "Profile::UniqueMacConfig"
                     },
                     "name": "net1",
                     "id": "3456"
                  },
                  "ports": [{"id": "4002", "location": "//1.1.1.2/1/1"}]
               }
            ]
         },
         {
            "id": "374343123",
            "name": "East",
            "ports": [{"id": "4001",
                  "location": "//1.0.0.2/1/1"}],
            "subnet_configs": [
               {
                  "subnet": {
                     "device_count_per_port": 2,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "1.1.1.20",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "1.1.1.100",
                        "ipv4_port_step": "0.0.1.2",
                        "ipv4_step": "0.0.1.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "_type": "Profile::UniqueMacConfig"
                     },
                     "name": "net2",
                     "id": "2345"
                  },
                  "ports": [{"id": "4001", "location": "//1.1.1.1/1/2"}]
               },
               {
                  "subnet": {
                     "device_count_per_port": 1,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "1.1.1.20",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "1.1.1.100",
                        "ipv4_port_step": "0.0.1.2",
                        "ipv4_step": "0.0.1.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "mac": "00:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:22",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net2",
                     "id": "4567"
                  },
                  "ports": [{"id": "4003", "location": "//1.1.1.2/1/2"}]
               }
            ]
         }
   ],
   "duration": 100,
   "endpoint_infos": [
      {
         "src": "East",
         "dst": "West",
         "traffic": {
             "id": "1357",
             "load": 10,
             "traffic_flows": [
                {
                   "weight": 100,
                   "fixed_frame_length": 64,
                   "max_frame_length": 111,
                   "min_frame_length": 99,
                   "step_frame_length": 100,
                   "frame_length_mode": 1,
                   "id": "5001",
                   "frame_config": "<frame><config>\
<pdus>\
<pdu name=\\"eth1\\" pdu=\\"ethernet:EthernetII\\" />\
<pdu name=\\"ip_1\\" pdu=\\"ipv4:IPv4\\" />\
<pdu name=\\"custom_1\\" pdu=\\"custom:Custom\\">\
<pattern>0000</pattern>\
</pdu>\
</pdus>\
</config></frame>"
                }
             ]
          }
      },
      {
         "src": "West",
         "dst": "East",
         "traffic": {
             "id": "2468",
             "load": 20,
             "traffic_flows": [
                {
                   "weight": 100,
                   "fixed_frame_length": 128,
                   "max_frame_length": 222,
                   "min_frame_length": 88,
                   "step_frame_length": 200,
                   "frame_length_mode": 2,
                   "id": "5002"
                }
             ]
          }
      }
   ]
    }'''


detect_source_mac_called = False
detect_source_mac_called_with = []


def get_network_profiles(data):
    topo_nodes = data["topology_nodes"]
    nps = []
    for node in topo_nodes:
        node_nps = [np_config["subnet"] for np_config in node["subnet_configs"]]
        nps += node_nps
    return nps


def get_traffic_profiles(data):
    ep_infos = data["endpoint_infos"]
    return [ep_info["traffic"] for ep_info in ep_infos]


@pytest.fixture(scope='module')
def mock_hardware_util():
    from ..utils import hardware_util
    assert hardware_util.VIRTUAL_PART_NUMS == [
        'SPT-QEMU', 'SPT-ANYWHERE', 'SPT-VIRTUAL'
        ]

    def mock_is_virtual(ip):
        if ip == '1.1.1.1':
            return True
        else:
            return False
    hardware_util.is_virtual = mock_is_virtual
    return hardware_util


@pytest.fixture(scope='module')
def mock_mac_util():
    global detect_source_mac_called
    global detect_source_mac_called_with
    from ..utils import mac_util

    def mock_detect_source_mac(port_list):
        global detect_source_mac_called
        global detect_source_mac_called_with
        detect_source_mac_called = True
        detect_source_mac_called_with = port_list
    mac_util.detect_source_mac = mock_detect_source_mac
    return mac_util


@pytest.fixture(scope='module')
def cleanup_all(stc, request):
    def cleanup():
        with AutoCommand("ResetConfigCommand") as reset_cmd:
            reset_cmd.Set("Config",
                          CStcSystem.Instance().GetObjectHandle())
            reset_cmd.Execute()
    request.addfinalizer(cleanup)
    cleanup()


@pytest.fixture(scope='module')
def ports(stc, request, cleanup_all):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    port1 = ctor.Create('Port', project)
    port1.Set('Location', '//1.1.1.1/1/1')
    port2 = ctor.Create('Port', project)
    port2.Set('Location', '//1.1.1.1/1/2')
    port3 = ctor.Create('Port', project)
    port3.Set('Location', '//1.1.1.2/1/1')
    port4 = ctor.Create('Port', project)
    port4.Set('Location', '//1.1.1.2/1/2')

    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    port2.AddObject(east_tag, RelationType("UserTag"))
    port4.AddObject(east_tag, RelationType("UserTag"))

    east_subnet1_tag = ctor.Create("Tag", tags)
    east_subnet1_tag.Set("Name", "East_net2_2345")
    east_subnet2_tag = ctor.Create("Tag", tags)
    east_subnet2_tag.Set("Name", "East_net2_4567")
    port2.AddObject(east_subnet1_tag, RelationType("UserTag"))
    port4.AddObject(east_subnet2_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    port1.AddObject(west_tag, RelationType("UserTag"))
    port3.AddObject(west_tag, RelationType("UserTag"))

    west_subnet1_tag = ctor.Create("Tag", tags)
    west_subnet1_tag.Set("Name", "West_net1_1234")
    west_subnet2_tag = ctor.Create("Tag", tags)
    west_subnet2_tag.Set("Name", "West_net1_3456")
    port1.AddObject(west_subnet1_tag, RelationType("UserTag"))
    port3.AddObject(west_subnet2_tag, RelationType("UserTag"))

    def cleanup():
        port1.MarkDelete()
        port2.MarkDelete()
        port3.MarkDelete()
        port4.MarkDelete()

    request.addfinalizer(cleanup)
    return [port1, port2, port3, port4]


@pytest.fixture(scope='module')
def stak(stc, request, ports, mock_hardware_util, mock_mac_util):
    data = json.loads(test_config)
    topology_config = data["topology_nodes"]
    params = {'TopologyConfig': json.dumps(topology_config)}
    from .. import AdjustMacCommand
    return {'command': AdjustMacCommand,
            'params': params}


def test_validate(stc, stak):
    assert stak['command'].validate(**stak['params']) == ''


def test_reset(stc, stak):
    assert stak['command'].reset()


def test_exec(stc, stak, cleanup_all, ports):
    data = json.loads(test_config)
    topology_config = data['topology_nodes']
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data['endpoint_infos']
    exec_command('CreateTemplatesCommand', {
        'TopologyConfig': json.dumps(topology_config),
        'NetworkProfileConfig': json.dumps(network_profiles),
        'TrafficProfileConfig': json.dumps(traffic_profiles),
        'EndpointConfig': json.dumps(endpoint_infos)
        })
    exec_command('AdjustMacCommand', stak['params'])
    assert detect_source_mac_called is True
    assert detect_source_mac_called_with == [ports[0].GetObjectHandle()]

    # subnet 1234 (west, unique, virtual, dev count == 1)
    # should not be randomized
    ethii_ifs1 = tag_utils.get_tagged_objects_from_string_names(
        ['net1_1234_ttEthIIIf']
        )
    assert len(ethii_ifs1) == 1
    for eif in ethii_ifs1:
        assert eif.GetObject('Rfc4814EthIIIfDecorator') is None

    # subnet 3456 (west, unique, hw) should be randomized
    ethii_ifs2 = tag_utils.get_tagged_objects_from_string_names(
        ['net1_3456_ttEthIIIf']
        )
    assert len(ethii_ifs2) == 1
    for eif in ethii_ifs2:
        assert eif.GetObject('Rfc4814EthIIIfDecorator') is not None

    # subnet 2345 (east, unique, virtual, dev count == 2)
    # should be randomized
    ethii_ifs3 = tag_utils.get_tagged_objects_from_string_names(
        ['net2_2345_ttEthIIIf']
        )
    assert len(ethii_ifs3) == 1
    for eif in ethii_ifs3:
        assert eif.GetObject('Rfc4814EthIIIfDecorator') is not None

    # subnet 4567 (east, static, hw) should not be randomized
    ethii_ifs4 = tag_utils.get_tagged_objects_from_string_names(
        ['net2_4567_ttEthIIIf']
        )
    assert len(ethii_ifs4) == 1
    for eif in ethii_ifs4:
        assert eif.GetObject('Rfc4814EthIIIfDecorator') is None
