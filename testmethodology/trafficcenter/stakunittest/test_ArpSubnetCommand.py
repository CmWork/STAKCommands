from StcIntPythonPL import *
import json
from spirent.core.utils.scriptable import AutoCommand
import pytest


PKG = "spirent.methodology.trafficcenter"
arped_sbs = []


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


@pytest.fixture
def reset_conf(stc, request):
    def run():
        with AutoCommand("ResetConfigCommand") as reset_cmd:
            reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
            reset_cmd.Execute()
    request.addfinalizer(run)
    run()


def mock_arp(sbs_to_arp):
    global arped_sbs
    arped_sbs = sbs_to_arp


def test_arp(stc, reset_conf):
    from .. import ArpSubnetCommand
    global arped_sbs
    ArpSubnetCommand.run_arp = mock_arp

    ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()

    test_config = '''{
   "topology_nodes": [
         {
            "id": "83749364",
            "name": "West",
            "subnet_configs": [
               {
                  "subnet": {
                     "device_count_per_port": 20,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "_type": "Profile::GatewayUseDestConfig"
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
                        "mac": "AA:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:11",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net1",
                     "id": "1234"
                  },
                  "ports": [{"id": "4000", "location": "//1.0.0.1/1/1"}]
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
                     "device_count_per_port": 30,
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
                     "id": "2345"
                  },
                  "ports": [{"id": "4001", "location": "//1.0.0.2/1/1"}]
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

    # Create two ports
    project = stcSys.GetObject("project")
    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//1.0.0.2/1/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//1.0.0.1/1/1")

    # Create port groups
    tags = project.GetObject("Tags")
    assert tags is not None
    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "East")
    tags.AddObject(east_tag, RelationType("UserTag"))
    east_port.AddObject(east_tag, RelationType("UserTag"))

    east_subnet_tag = ctor.Create("Tag", tags)
    east_subnet_tag.Set("Name", "East_net2_2345")
    tags.AddObject(east_subnet_tag, RelationType("UserTag"))
    east_port.AddObject(east_subnet_tag, RelationType("UserTag"))

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "West")
    tags.AddObject(west_tag, RelationType("UserTag"))
    west_port.AddObject(west_tag, RelationType("UserTag"))

    west_subnet_tag = ctor.Create("Tag", tags)
    west_subnet_tag.Set("Name", "West_net1_1234")
    tags.AddObject(west_subnet_tag, RelationType("UserTag"))
    west_port.AddObject(west_subnet_tag, RelationType("UserTag"))

    data = json.loads(test_config)
    topo_conf = data["topology_nodes"]
    network_profiles = get_network_profiles(data)
    traffic_profiles = get_traffic_profiles(data)
    endpoint_infos = data["endpoint_infos"]

    with AutoCommand(PKG + ".CreateTemplatesCommand") as profile_cmd:
        profile_cmd.Set("TopologyConfig", json.dumps(topo_conf))
        profile_cmd.Set("NetworkProfileConfig",
                        json.dumps(network_profiles))
        profile_cmd.Set("TrafficProfileConfig",
                        json.dumps(traffic_profiles))
        profile_cmd.Set("EndpointConfig", json.dumps(endpoint_infos))
        profile_cmd.Execute()

    assert ArpSubnetCommand.validate(json.dumps(topo_conf)) == ''
    assert ArpSubnetCommand.reset()
    ArpSubnetCommand.run(json.dumps(topo_conf))

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 2
    ap_list_1 = trf_mix_list[0].GetObjects("StmTemplateConfig")
    assert len(ap_list_1) == 1
    sb = ap_list_1[0].GetObject("StreamBlock", RelationType("GeneratedObject"))

    assert len(arped_sbs) == 1
    assert arped_sbs[0] == sb.GetObjectHandle()
