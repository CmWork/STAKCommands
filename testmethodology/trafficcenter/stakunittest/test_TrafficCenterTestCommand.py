from StcIntPythonPL import *
import sys
import os
import json
# from mock import MagicMock
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology', 'trafficcenter'))
import TrafficCenterTestCommand
from spirent.core.utils.scriptable import AutoCommand


PKG = "spirent.methodology.trafficcenter"


def test_basic(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    test_config = '''{
   "traffic_pattern": 0,
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
                        "mac": "AA:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:11",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net1",
                     "id": "1234"
                  },
                  "ports": [{"id": "4000", "location": "//10.109.124.231/1/1"}]
               }
            ]
         },
         {
            "id": "374343123",
            "name": "East",
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
                  "ports": [{"id": "4001", "location": "//10.109.125.148/1/1"}]
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
                   "id": "5001"
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

    # ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()
    seq = stcSys.GetObject("Sequencer")
    hndReg = CHandleRegistry.Instance()

    # FIXME:
    # This should be handled by the TrafficCenterTestCommand
    # Create two ports
    # project = stcSys.GetObject("project")
    # east_port = ctor.Create("Port", project)
    # east_port.Set("Location", "//10.109.124.231/1/1")
    # west_port = ctor.Create("Port", project)
    # west_port.Set("Location", "//10.109.125.148/1/1")
    # hnd_list = [east_port.GetObjectHandle(),
    #            west_port.GetObjectHandle()]

    # Mock functions in TrafficCenterTestCommand that
    # can't participate in unit tests
    # TrafficCenterTestCommand.getVirtualPorts = MagicMock(
    #    return_value=hnd_list)
    # TrafficCenterTestCommand.attachPorts = MagicMock(
    #    return_value=True)

    # Mock will not work with Execute(), need to call run() directly
    #    with AutoCommand(PKG + ".TrafficCenterTestCommand") as tc_cmd:
    #        tc_cmd.Set("TestConfig", test_config)
    #        tc_cmd.Execute()
    TrafficCenterTestCommand.run(test_config)

    # Check the port groups were created
    # port_list = project.GetObjects("Port")
    # assert len(port_list) == 2
    # west_port = port_list[0]
    # east_port = port_list[1]
    # assert east_port is not None
    # assert west_port is not None

    # west_tag = west_port.GetObject("Tag", RelationType("UserTag"))
    # assert west_tag is not None
    # assert west_tag.Get("Name") == "West"
    # east_tag = east_port.GetObject("Tag", RelationType("UserTag"))
    # assert east_tag is not None
    # assert east_tag.Get("Name") == "East"

    # Check the command sequence
    assert seq.Get("ErrorHandler") == "STOP_ON_ERROR"
    cmd_list = seq.GetCollection("CommandList")
    assert len(cmd_list) == 9

    obj = hndReg.Find(cmd_list[0])
    assert obj.IsTypeOf(PKG + ".ReservePortsCommand")

    obj = hndReg.Find(cmd_list[1])
    assert obj.IsTypeOf(PKG + ".CreateTemplatesCommand")

    obj = hndReg.Find(cmd_list[2])
    assert obj.IsTypeOf(PKG + ".AdjustMacCommand")

    obj = hndReg.Find(cmd_list[3])
    assert obj.IsTypeOf(PKG + ".BindDhcpSubnetCommand")

    obj = hndReg.Find(cmd_list[4])
    assert obj.IsTypeOf(PKG + ".ArpSubnetCommand")

    obj = hndReg.Find(cmd_list[5])
    assert obj.IsTypeOf(PKG + ".SetTrafficDurationCommand")

    obj = hndReg.Find(cmd_list[6])
    assert obj.IsTypeOf("GeneratorStartCommand")

    obj = hndReg.Find(cmd_list[7])
    assert obj.IsTypeOf("GeneratorWaitForStopCommand")

    obj = hndReg.Find(cmd_list[8])
    assert obj.IsTypeOf("WaitCommand")

    # obj = hndReg.Find(cmd_list[9])
    # assert obj.IsTypeOf(PKG + ".ReleaseDhcpSubnetCommand")
    # move to UI
    # group_cmd = stcSys.GetObject("SequencerGroupCommand")
    # group_cmd_list = group_cmd.GetCollection("CommandList")
    # assert len(group_cmd_list) == 1
    #
    # obj = hndReg.Find(group_cmd_list[0])
    # assert obj.IsTypeOf(PKG + ".ReleasePortsCommand")


def test_traffic_pattern(stc):
    with AutoCommand("ResetConfigCommand") as reset_cmd:
        reset_cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        reset_cmd.Execute()

    test_config = '''{
   "traffic_pattern": 2,
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
                        "mac": "AA:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:11",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net1",
                     "id": "1234"
                  },
                  "ports": [{"id": "4000", "location": "//10.109.124.231/1/1"}]
               }
            ]
         },
         {
            "id": "374343123",
            "name": "East",
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
                  "ports": [{"id": "4000", "location": "//10.109.124.233/1/1"}]
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
                   "id": "5001"
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

    # ctor = CScriptableCreator()
    stcSys = CStcSystem.Instance()
    seq = stcSys.GetObject("Sequencer")
    hndReg = CHandleRegistry.Instance()

    TrafficCenterTestCommand.run(test_config)

    cmd_list = seq.GetCollection("CommandList")
    assert len(cmd_list) == 9

    # Check that the generated CreateTemplateCommand's traffic profile information
    # has the traffic pattern configured.

    obj = hndReg.Find(cmd_list[1])
    assert obj.IsTypeOf(PKG + ".CreateTemplatesCommand")

    traffic_profiles = obj.Get("TrafficProfileConfig")
    tp = json.loads(traffic_profiles)
    assert len(tp) == 2

    assert tp[0]["traffic_pattern"] == 2
    assert tp[1]["traffic_pattern"] == 2
