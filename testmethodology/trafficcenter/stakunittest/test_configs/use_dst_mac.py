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
               },
               {
                  "subnet": {
                     "device_count_per_port": 15,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "2.1.1.10",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "2.1.1.1",
                        "ipv4_port_step": "0.0.1.0",
                        "ipv4_step": "0.0.0.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "mac": "AB:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:11",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net3",
                     "id": "1235"
                  },
                  "ports": [{"id": "4002", "location": "//1.0.0.3/1/1"}]
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
                        "_type": "Profile::GatewayUseDestConfig"
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
               },
               {
                  "subnet": {
                     "device_count_per_port": 5,
                     "dhcp_enabled": false,
                     "gateway_config": {
                        "ip_config": {
                           "ipv4": "3.1.1.20",
                           "ipv4_port_step": "0.0.1.0",
                           "ipv4_step": "0.0.0.0",
                           "_type": "Profile::GatewayIpv4Config"
                        },
                        "_type": "Profile::GatewayArpConfig"
                     },
                     "ip_config": {
                        "ipv4": "3.1.1.100",
                        "ipv4_port_step": "0.0.1.2",
                        "ipv4_step": "0.0.1.1",
                        "prefix": 24,
                        "control_plane_priority": "routine",
                        "_type": "Profile::Ipv4Config"
                     },
                     "mac_config": {
                        "mac": "0B:BB:CC:DD:EE:FF",
                        "mac_port_step": "00:00:00:00:01:00",
                        "mac_step": "00:00:00:11:11:22",
                        "_type": "Profile::StaticMacConfig"
                     },
                     "name": "net4",
                     "id": "2346"
                  },
                  "ports": [{"id": "4003", "location": "//1.0.0.4/1/1"}]
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
