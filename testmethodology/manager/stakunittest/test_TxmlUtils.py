from StcIntPythonPL import *
import os
import sys
import hashlib
import xml.etree.ElementTree as ET
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import manager.utils.txml_utils as txml_utils
from manager.utils.sequencer_utils import SequenceInfo as SequenceInfo
from unit_test_utils import UnitTestUtils
from methodologymanagerUtestConst import MethodologyManagerUtestConst as mmuc
from manager.utils.methodologymanagerConst import MethodologyManagerConst as mmc

STAK_PKG = "spirent.methodology."
STAK_TRF_PKG = "spirent.trafficcenter."

ETH_CMD = "CreateEthernetNetworkInfoCommand"
IPV4_CMD = "CreateIpv4NetworkInfoCommand"
BGP_CMD = "routing.BgpProtocolProfileGroupCommand"
VLAN_CMD = "CreateVlanNetworkInfoCommand"
MAC_ADDR = "MacAddr"
MAC_ADDR_STEP = "MacAddrStep"
MAC_ADDR_PORT_STEP = "MacAddrPortStep"
IPV4_ADDR = "Ipv4Addr"
IPV4_ADDR_STEP = "Ipv4AddrStep"
IPV4_ADDR_PORT_STEP = "Ipv4AddrPortStep"


def populate_mini_sequence_and_expose_properties(arp_cmd_name,
                                                 arp_cmd,
                                                 stak_cmd_name,
                                                 stak_cmd):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
    insert_cmd.SetCollection("CommandList", [arp_cmd.GetObjectHandle(),
                                             stak_cmd.GetObjectHandle()])
    insert_cmd.Execute()

    # Exposed Config/Exposed Properties
    exposedConfig = ctor.Create("ExposedConfig", project)
    prop1 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop1, arp_cmd, arp_cmd_name, "ArpNdOption")
    prop2 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop2, arp_cmd, arp_cmd_name, "ForceArp")
    prop3 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop3, arp_cmd, arp_cmd_name, "WaitForArpToFinish")
    prop4 = ctor.Create("ExposedProperty", exposedConfig)
    UnitTestUtils.bind(prop4, stak_cmd, STAK_PKG + stak_cmd_name, "DeviceCount")

    plLogger.LogInfo("end")
    return exposedConfig.GetObjects("ExposedProperty")


def populate_profile_test_and_expose_properties(min_num_ports,
                                                max_num_ports,
                                                port_speed_list):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    exposedConfig = project.GetObject("ExposedConfig")
    if exposedConfig is None:
        exposedConfig = ctor.Create("ExposedConfig", project)

    # Add some ports
    east_port = ctor.Create("Port", project)
    west_port = ctor.Create("Port", project)

    # Add some port group tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)

    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "EastPortGroup")

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "WestPortGroup")

    east_port.AddObject(east_tag, RelationType("UserTag"))
    west_port.AddObject(west_tag, RelationType("UserTag"))

    # Build the BLL objects
    plLogger.LogInfo("set up sequence...")
    pkg = STAK_PKG

    # Test Topology Group
    plLogger.LogInfo("Topo-Test group first...")
    test_topo_group_cmd = ctor.Create(pkg + "TopologyTestGroupCommand", sequencer)
    test_topo_group_cmd.Set("Name", "TestTopologyGroup")

    insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
    insert_cmd.SetCollection("CommandList", [test_topo_group_cmd.GetObjectHandle()])
    insert_cmd.Execute()

    # Topology profile group command
    plLogger.LogInfo("Topo group next...")
    topo_group_cmd = ctor.Create(pkg + "TopologyProfileGroupCommand", test_topo_group_cmd)
    topo_group_cmd.Set("Name", "TopologyGroup")

    # First network profile group command
    plLogger.LogInfo("1st network profile...")
    net_prof_group_cmd1 = ctor.Create(pkg + "NetworkProfileGroupCommand", topo_group_cmd)
    net_prof_group_cmd1.Set("Name", "EastNetworkProfileGroup")
    net_prof_group_cmd1.Set("DeviceCount", "2")
    net_prof_group_cmd1.Set("PortGroupTag", east_tag.GetObjectHandle())

    # Create the stack for the first network profile
    plLogger.LogInfo("1st network profile stak...")
    create_eth_net1 = ctor.Create(pkg + ETH_CMD,
                                  net_prof_group_cmd1)
    create_ipv4_net1 = ctor.Create(pkg + IPV4_CMD,
                                   net_prof_group_cmd1)
    create_bgp_proto1 = ctor.Create(pkg + BGP_CMD,
                                    net_prof_group_cmd1)
    net_prof_group_cmd1.SetCollection("CommandList",
                                      [create_ipv4_net1.GetObjectHandle(),
                                       create_eth_net1.GetObjectHandle(),
                                       create_bgp_proto1.GetObjectHandle()])

    # Exposed properties for the first network profile
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_eth_net1, pkg + ETH_CMD, MAC_ADDR)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_eth_net1, pkg + ETH_CMD, MAC_ADDR_STEP)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_ipv4_net1, pkg + IPV4_CMD, IPV4_ADDR)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_ipv4_net1, pkg + IPV4_CMD, IPV4_ADDR_STEP)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_bgp_proto1, pkg + BGP_CMD, "AsNum")
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_bgp_proto1, pkg + BGP_CMD, "AsNumStep")

    # Now setup the second network profile
    plLogger.LogInfo("2nd network profile...")
    net_prof_group_cmd2 = ctor.Create(pkg + "NetworkProfileGroupCommand", topo_group_cmd)
    net_prof_group_cmd2.Set("Name", "WestNetworkProfileGroup")
    net_prof_group_cmd2.Set("DeviceCount", "2")
    net_prof_group_cmd2.Set("PortGroupTag", west_tag.GetObjectHandle())

    # And now the stack for the profile
    plLogger.LogInfo("2nd network profile stack...")
    create_eth_net2 = ctor.Create(pkg + ETH_CMD,
                                  net_prof_group_cmd2)
    create_vlan_net2 = ctor.Create(pkg + VLAN_CMD,
                                   net_prof_group_cmd2)
    create_ipv4_net2 = ctor.Create(pkg + IPV4_CMD,
                                   net_prof_group_cmd2)
    net_prof_group_cmd2.SetCollection("CommandList",
                                      [create_ipv4_net2.GetObjectHandle(),
                                       create_vlan_net2.GetObjectHandle(),
                                       create_eth_net2.GetObjectHandle()])
    topo_group_cmd.SetCollection("CommandList", [net_prof_group_cmd1.GetObjectHandle(),
                                                 net_prof_group_cmd2.GetObjectHandle()])

    # Exposed properties for the second network profile
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_eth_net2, pkg + ETH_CMD, MAC_ADDR)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_eth_net2, pkg + ETH_CMD, MAC_ADDR_STEP)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_eth_net2, pkg + ETH_CMD, MAC_ADDR_PORT_STEP)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_vlan_net2, pkg + VLAN_CMD, "VlanId")
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_vlan_net2, pkg + VLAN_CMD, "VlanIdStep")
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_ipv4_net2, pkg + IPV4_CMD, IPV4_ADDR)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_ipv4_net2, pkg + IPV4_CMD, IPV4_ADDR_STEP)
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       create_ipv4_net2, pkg + IPV4_CMD, IPV4_ADDR_PORT_STEP)

    # Now create the test group
    plLogger.LogInfo("Test group...")
    test_group_cmd = ctor.Create(pkg + "TestGroupCommand", test_topo_group_cmd)
    test_group_cmd.Set("Name", "TestGroup")

    test_topo_group_cmd.SetCollection("CommandList", [topo_group_cmd.GetObjectHandle(),
                                                      test_group_cmd.GetObjectHandle()])

    # Due to the objects being internally "sorted" by their object ID and
    # then written out to file in that order, the paramGroups here also need
    # to be sorted by their originating object's object ID (good thing there's
    # only two commands).

    # FIXME:
    # Need to redo this to use templates and get rid of all of the profile
    # stuff.  Also need to allow direct configuration of the testCaseName
    # or need to default it to "original" if it isn't set (maybe).
    testInfo = "<testInfo description=\"UnitTest Description1\" " + \
               "displayName=\"UnitTest Meth1\" " + \
               "methodologyKey=\"UNITTESTA\" " + \
               "testCaseDescription=\"\" " + \
               "testCaseKey=\"\" " + \
               "testCaseName=\"\" version=\"1.0\">" + \
               "<labels>" + \
               "<label>UnitTest</label>" + \
               "<label>Arp</label>" + \
               "<label>Ipv4</label>" + \
               "</labels>" + \
               "<features><feature id=\"Feature1\"/><feature id=\"Feature2\"/></features>" +\
               "</testInfo>"

    testResources = "<testResources>" + \
                    "<resourceGroups>" + \
                    "<resourceGroup name=\"Port Limits\">" + \
                    "<attribute name=\"minNumPorts\" value=\"" + min_num_ports + "\"/>" + \
                    "<attribute name=\"maxNumPorts\" value=\"" + max_num_ports + "\"/>" + \
                    "<attribute name=\"portSpeedList\" value=\"" + port_speed_list + "\"/>" + \
                    "</resourceGroup>" + \
                    "<resourceGroup displayName=\"Chassis Info\" id=\"chassisInfo\">" + \
                    "<portGroups/>" + \
                    "</resourceGroup>" + \
                    "</resourceGroups>" + \
                    "</testResources>"

    editableParams = "<editableParams>" + \
                     "<paramGroups name=\"exposedProperties\">" + \
                     "<paramGroup id=\"" + str(create_eth_net1.GetObjectHandle()) + "\" " + \
                     "name=\"createethernetnetworkinfocommand\">" + \
                     "<params>" + \
                     "<param name=\"macaddr\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createethernetnetworkinfocommand." + \
                     "macaddr." + str(create_eth_net1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"00:01:94:00:00:01\"/>" + \
                     "<attribute name=\"type\" value=\"mac\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"macaddrstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createethernetnetworkinfocommand." + \
                     "macaddrstep." + str(create_eth_net1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"00:00:00:00:00:01\"/>" + \
                     "<attribute name=\"type\" value=\"mac\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "<paramGroup id=\"" + str(create_ipv4_net1.GetObjectHandle()) + "\" " + \
                     "name=\"createipv4networkinfocommand\">" + \
                     "<params>" + \
                     "<param name=\"ipv4addr\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createipv4networkinfocommand." + \
                     "ipv4addr." + str(create_ipv4_net1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"192.85.1.3\"/>" + \
                     "<attribute name=\"type\" value=\"ip\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"ipv4addrstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createipv4networkinfocommand." + \
                     "ipv4addrstep." + str(create_ipv4_net1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"0.0.0.1\"/>" + \
                     "<attribute name=\"type\" value=\"ip\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "<paramGroup id=\"" + str(create_bgp_proto1.GetObjectHandle()) + "\" " + \
                     "name=\"routing.bgpprotocolprofilegroupcommand\">" + \
                     "<params>" + \
                     "<param name=\"routing.bgpprotocolprofilegroupcommand.asnum\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.routing.bgpprotocolprofilegroupcommand." + \
                     "asnum." + str(create_bgp_proto1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"1\"/>" + \
                     "<attribute name=\"type\" value=\"integer\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"routing.bgpprotocolprofilegroupcommand.asnumstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.routing.bgpprotocolprofilegroupcommand." + \
                     "asnumstep." + str(create_bgp_proto1.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"0\"/>" + \
                     "<attribute name=\"type\" value=\"integer\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "<paramGroup id=\"" + str(create_eth_net2.GetObjectHandle()) + "\" " + \
                     "name=\"createethernetnetworkinfocommand\">" + \
                     "<params>" + \
                     "<param name=\"macaddr\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createethernetnetworkinfocommand." + \
                     "macaddr." + str(create_eth_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"00:01:94:00:00:01\"/>" + \
                     "<attribute name=\"type\" value=\"mac\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"macaddrstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createethernetnetworkinfocommand." + \
                     "macaddrstep." + str(create_eth_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"00:00:00:00:00:01\"/>" + \
                     "<attribute name=\"type\" value=\"mac\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"macaddrportstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createethernetnetworkinfocommand." + \
                     "macaddrportstep." + str(create_eth_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"00:00:00:00:01:00\"/>" + \
                     "<attribute name=\"type\" value=\"mac\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "<paramGroup id=\"" + str(create_vlan_net2.GetObjectHandle()) + "\" " + \
                     "name=\"createvlannetworkinfocommand\">" + \
                     "<params>" + \
                     "<param name=\"vlanid\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createvlannetworkinfocommand." + \
                     "vlanid." + str(create_vlan_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"100\"/>" + \
                     "<attribute name=\"type\" value=\"integer\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"vlanidstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createvlannetworkinfocommand." + \
                     "vlanidstep." + str(create_vlan_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"0\"/>" + \
                     "<attribute name=\"type\" value=\"integer\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "<paramGroup id=\"" + str(create_ipv4_net2.GetObjectHandle()) + "\" " + \
                     "name=\"createipv4networkinfocommand\">" + \
                     "<params>" + \
                     "<param name=\"ipv4addr\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createipv4networkinfocommand." + \
                     "ipv4addr." + str(create_ipv4_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"192.85.1.3\"/>" + \
                     "<attribute name=\"type\" value=\"ip\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"ipv4addrstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createipv4networkinfocommand." + \
                     "ipv4addrstep." + str(create_ipv4_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"0.0.0.1\"/>" + \
                     "<attribute name=\"type\" value=\"ip\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "<param name=\"ipv4addrportstep\">" + \
                     "<attribute name=\"stcPropertyId\" " + \
                     "value=\"spirent.methodology.createipv4networkinfocommand." + \
                     "ipv4addrportstep." + str(create_ipv4_net2.GetObjectHandle()) + "\"/>" + \
                     "<attribute name=\"defaultValue\" value=\"0.0.1.0\"/>" + \
                     "<attribute name=\"type\" value=\"ip\"/>" + \
                     "<attribute name=\"units\" value=\"ounces\"/>" + \
                     "<attribute name=\"minInclusive\" value=\"0\"/>" + \
                     "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
                     "</param>" + \
                     "</params>" + \
                     "</paramGroup>" + \
                     "</paramGroups>" + \
                     "<paramGroups name=\"taggedProperties\">" + \
                     "<paramGroup name=\"LoadTemplateGroupCommand.1234\">" + \
                     "<params><param id=\"1234\" tag=\"Bgp\">" + \
                     "<attribute name=\"BgpRouterConfig.AsNum\" value=\"564\"/>" + \
                     "<attribute name=\"BgpRouterConfig.PeerAs\" value=\"111\"/>" + \
                     "</param><param id=\"5678\" tag=\"OuterVlan\">" + \
                     "<attribute name=\"VlanIfnIf.VlanId\" value=\"100\"/>" + \
                     "</param></params></paramGroup>" + \
                     "<paramGroup name=\"LoadTemplateGroupCommand.5678\">" + \
                     "<params><param id=\"9012\" tag=\"Bgp\">" + \
                     "<attribute name=\"BgpRouterConfig.AsNum\" value=\"444\"/>" + \
                     "<attribute name=\"BgpRouterConfig.PeerAs\" value=\"333\"/>" + \
                     "</param><param id=\"3456\" tag=\"InnerVlan\">" + \
                     "<attribute name=\"VlanIfnIf.VlanId\" value=\"101\"/>" + \
                     "</param></params></paramGroup></paramGroups>" + \
                     "</editableParams>"

    topologyInfo = "<topologyInfo description=\"Reserved for future use\" name=\"Reserved\"/>"

    trafficInfo = "<trafficInfo description=\"Optional Description\" name=\"Test Traffic\"/>"

    gold_meta = "<?xml version=\"1.0\" ?>" + \
                "<test>" + \
                testInfo + \
                testResources + \
                editableParams + \
                topologyInfo + \
                trafficInfo + \
                "</test>"

    plLogger.LogInfo("end")
    return exposedConfig.GetObjects("ExposedProperty"), gold_meta


def populate_sequence_and_expose_traffic_properties():
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")
    exposedConfig = ctor.Create("ExposedConfig", project)

    # Add some ports
    east_port = ctor.Create("Port", project)
    west_port = ctor.Create("Port", project)

    # Add some port group tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)

    east_tag = ctor.Create("Tag", tags)
    east_tag.Set("Name", "EastPortGroup")

    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "WestPortGroup")

    east_port.AddObject(east_tag, RelationType("UserTag"))
    west_port.AddObject(west_tag, RelationType("UserTag"))

    # Test Topology Group
    plLogger.LogInfo("Topo-Test group first...")
    test_topo_group_cmd = ctor.Create(STAK_PKG + "TopologyTestGroupCommand", sequencer)
    test_topo_group_cmd.Set("Name", "TestTopologyGroup")

    insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
    insert_cmd.SetCollection("CommandList", [test_topo_group_cmd.GetObjectHandle()])
    insert_cmd.Execute()

    # Topology profile group command
    plLogger.LogInfo("Topo group next...")
    topo_group_cmd = ctor.Create(STAK_PKG + "TopologyProfileGroupCommand", test_topo_group_cmd)
    topo_group_cmd.Set("Name", "TopologyGroup")

    # network profile group command
    plLogger.LogInfo("network profile...")
    net_prof_group_cmd = ctor.Create(STAK_PKG + "NetworkProfileGroupCommand", topo_group_cmd)
    net_prof_group_cmd.Set("Name", "NetworkProfileGroup")
    net_prof_group_cmd.Set("DeviceCount", "2")
    net_prof_group_cmd.Set("PortGroupTag", str(west_tag.GetObjectHandle()))

    # Create the stack for the first network profile
    create_ipv4_net = ctor.Create(STAK_PKG + "CreateIpv4NetworkInfoCommand", net_prof_group_cmd)
    net_prof_group_cmd.SetCollection("CommandList", [create_ipv4_net.GetObjectHandle()])

    # Traffic profile
    plLogger.LogInfo("traffic profile...")
    trf_prof_cmd = ctor.Create(STAK_TRF_PKG + "CreateTrafficProfileCommand", topo_group_cmd)

    topo_group_cmd.SetCollection("CommandList", [net_prof_group_cmd.GetObjectHandle(),
                                                 trf_prof_cmd.GetObjectHandle()])

    # Exposed Config/Exposed Properties
    UnitTestUtils.bind(ctor.Create("ExposedProperty", exposedConfig),
                       trf_prof_cmd, STAK_TRF_PKG + "CreateTrafficProfileCommand", "Load")

    # Now create the test group
    plLogger.LogInfo("Test group...")
    test_group_cmd = ctor.Create(STAK_PKG + "TestGroupCommand", test_topo_group_cmd)
    test_group_cmd.Set("Name", "TestGroup")

    test_topo_group_cmd.SetCollection("CommandList", [topo_group_cmd.GetObjectHandle(),
                                                      test_group_cmd.GetObjectHandle()])

    gold_meta = "<UnitTest>" + \
                "<trafficInfo description=\"My description\" name=\"Just a name\">" + \
                "<traffic>" + \
                "<attribute name=\"Load\" value=\"10\" />" + \
                "<attribute name=\"LoadUnit\" value=\"PERCENT_LINE_RATE\" />" + \
                "<attribute name=\"TrafficPattern\" value=\"PAIR\" />" + \
                "<attribute name=\"ProfileName\" value=\"TrafficProfile\" />" + \
                "<attribute name=\"EndpointDescriptors\" value=\"\" />" + \
                "<attribute name=\"ResultDescriptors\" value=\"DroppedCountBasic\" />" + \
                "</traffic>" + \
                "</trafficInfo>" + \
                "</UnitTest>"

    plLogger.LogInfo("end")
    return exposedConfig.GetObjects("ExposedProperty"), gold_meta


def test_adjust_type(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    BOGUS_TYPE = "nothing"
    INT_LIST = ["u8", "u16", "u32", "u64", "s8", "s16", "s32", "s64"]
    for int_type in INT_LIST:
        assert "integer" == txml_utils.MetaManager.adjust_type(int_type)
    assert BOGUS_TYPE == txml_utils.MetaManager.adjust_type(BOGUS_TYPE)
    plLogger.LogInfo("end")


# FIXME
# Use template commands instead of profile commands
def disabled_test_sort_exposed_properties(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    exp_conf = ctor.Create("ExposedConfig", project)

    # Non-command object
    port = ctor.Create("Port", project)
    port.Set("Location", "//10.14.16.27/2/1")
    port_id = txml_utils.get_unique_property_id(port, "Location")
    exp_port = ctor.Create("ExposedProperty", exp_conf)
    exp_port.Set("EPNameId", port_id)
    exp_port.Set("EPClassId", "Port")
    exp_port.Set("EPPropertyId", "Port.Location")
    exp_port.AddObject(port, RelationType("ScriptableExposedProperty"))

    # Command objects
    ipv4_cmd_name = "spirent.methodology.Ipv4NetworkProfileGroupCommand"
    ipv4_netprof1 = ctor.Create(ipv4_cmd_name, sequencer)
    ipv4_addr_id1 = txml_utils.get_unique_property_id(ipv4_netprof1, IPV4_ADDR)
    exp_ipv4_addr1 = ctor.Create("ExposedProperty", exp_conf)
    exp_ipv4_addr1.Set("EPNameId", ipv4_addr_id1)
    exp_ipv4_addr1.Set("EPClassId", ipv4_cmd_name)
    exp_ipv4_addr1.Set("EPPropertyId", ipv4_cmd_name + ".Ipv4Addr")
    exp_ipv4_addr1.AddObject(ipv4_netprof1, RelationType("ScriptableExposedProperty"))

    vlan_id_id = txml_utils.get_unique_property_id(ipv4_netprof1, "VlanId")
    exp_vlan_id = ctor.Create("ExposedProperty", exp_conf)
    exp_vlan_id.Set("EPNameId", vlan_id_id)
    exp_vlan_id.Set("EPClassId", ipv4_cmd_name)
    exp_vlan_id.Set("EPPropertyId", ipv4_cmd_name + ".VlanId")
    exp_vlan_id.AddObject(ipv4_netprof1, RelationType("ScriptableExposedProperty"))

    ipv4_netprof2 = ctor.Create(ipv4_cmd_name, sequencer)
    ipv4_addr_id2 = txml_utils.get_unique_property_id(ipv4_netprof2, IPV4_ADDR)
    exp_ipv4_addr2 = ctor.Create("ExposedProperty", exp_conf)
    exp_ipv4_addr2.Set("EPNameId", ipv4_addr_id2)
    exp_ipv4_addr2.Set("EPClassId", ipv4_cmd_name)
    exp_ipv4_addr2.Set("EPPropertyId", ipv4_cmd_name + ".Ipv4Addr")
    exp_ipv4_addr2.AddObject(ipv4_netprof2, RelationType("ScriptableExposedProperty"))

    ipv6_cmd_name = "spirent.methodology.Ipv6NetworkProfileGroupCommand"
    ipv6_netprof = ctor.Create(ipv6_cmd_name, sequencer)
    ipv6_addr_id = txml_utils.get_unique_property_id(ipv6_netprof, "Ipv6Addr")
    exp_ipv6_addr = ctor.Create("ExposedProperty", exp_conf)
    exp_ipv6_addr.Set("EPNameId", ipv6_addr_id)
    exp_ipv6_addr.Set("EPClassId", ipv6_cmd_name)
    exp_ipv6_addr.Set("EPPropertyId", ipv6_cmd_name + ".Ipv6Addr")
    exp_ipv6_addr.AddObject(ipv6_netprof, RelationType("ScriptableExposedProperty"))

    sorted_props = txml_utils.MetaManager.sort_exposed_properties([exp_port,
                                                                   exp_ipv4_addr1,
                                                                   exp_vlan_id,
                                                                   exp_ipv4_addr2,
                                                                   exp_ipv6_addr])
    plLogger.LogInfo("sorted_props: " + str(sorted_props))
    assert len(sorted_props.keys()) == 3
    assert ipv4_netprof1.GetObjectHandle() in sorted_props.keys()
    assert ipv4_netprof2.GetObjectHandle() in sorted_props.keys()
    assert ipv6_netprof.GetObjectHandle() in sorted_props.keys()
    assert port.GetObjectHandle() not in sorted_props.keys()

    assert len(sorted_props[ipv4_netprof1.GetObjectHandle()]) == 2
    assert len(sorted_props[ipv4_netprof2.GetObjectHandle()]) == 1
    assert len(sorted_props[ipv6_netprof.GetObjectHandle()]) == 1

    assert exp_ipv4_addr1 in sorted_props[ipv4_netprof1.GetObjectHandle()]
    assert exp_vlan_id in sorted_props[ipv4_netprof1.GetObjectHandle()]
    assert exp_ipv4_addr2 in sorted_props[ipv4_netprof2.GetObjectHandle()]
    assert exp_ipv6_addr in sorted_props[ipv6_netprof.GetObjectHandle()]
    plLogger.LogInfo("end")


# FIXME:
# Profile-based tests no longer supported.
# This unit test should be removed.
def disabled_test_generate_txml_file(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    min_num_ports = "2"
    max_num_ports = "10"
    port_speed_list = "100,40"
    exp_prop_list, gold_meta = populate_profile_test_and_expose_properties(min_num_ports,
                                                                           max_num_ports,
                                                                           port_speed_list)

    # Build the SequenceInfo
    plLogger.LogInfo("Validate and load the sequence...")
    si = SequenceInfo()
    assert si.validate_and_load_profile_based_sequence(sequencer.GetCollection("CommandList"))

    test_label_list = ["UnitTest", "Arp", "Ipv4"]
    feature_id_list = ["Feature1", "Feature2"]
    file_name = mmc.MM_META_FILE_NAME
    meth_name = "UnitTest Meth1"
    meth_descript = "UnitTest Description1"
    meth_key = "UNITTESTA"
    port_tag_list = {}
    assert txml_utils.MetaManager.generate_txml_file(
        exp_prop_list, meth_name, meth_descript,
        meth_key, port_tag_list,
        test_label_list, feature_id_list,
        si,
        min_num_ports, max_num_ports,
        port_speed_list,
        get_tagged_xml(),
        file_name)

    f = open(file_name, 'r')
    actual = ""
    for line in f:
        actual = actual + line.strip(' \t\n\r')

    plLogger.LogInfo("actual TXML: \n" + actual)
    plLogger.LogInfo("gold_meta TXML: \n" + gold_meta)

    actual_cs = hashlib.md5(actual).hexdigest()
    expect_cs = hashlib.md5(gold_meta).hexdigest()
    # Clean up
    f.close()
    os.remove(file_name)

    assert actual_cs == expect_cs
    plLogger.LogInfo("end")


def test_generate_test_info(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    feature_id_list = ["Feature1", "Feature2"]
    M = txml_utils.MetaManager
    meta = ET.Element("UnitTest")
    meth_name = "UnitTest test_generate_test_info"
    meth_descript = "UnitTest test_generate_test_info lengthy description"
    meth_key = "UT_GEN_TI"
    tc_name = "UnitTest test case name"
    tc_descript = "UnitTest test case lengthy description"
    tc_key = meth_key + "-12"
    test_label_list = ["UnitTest", "Arp", "Ipv4"]
    version = "2.2"
    M.generate_test_info(meta, meth_name, meth_descript, meth_key,
                         tc_name, tc_descript, tc_key,
                         test_label_list, feature_id_list, version)

    result = ET.tostring(meta)
    plLogger.LogInfo("result:\n" + result)
    gold_meta = "<UnitTest>" + \
                "<testInfo description=\"" + meth_descript + "\" " + \
                "displayName=\"" + meth_name + "\" " + \
                "methodologyKey=\"" + meth_key + "\" " + \
                "testCaseDescription=\"" + tc_descript + "\" " + \
                "testCaseKey=\"" + tc_key + "\" " + \
                "testCaseName=\"" + tc_name + "\" " + \
                "version=\"" + version + "\">" + \
                "<labels><label>UnitTest</label>" + \
                "<label>Arp</label>" + \
                "<label>Ipv4</label></labels>" + \
                "<features><feature id=\"Feature1\" /><feature id=\"Feature2\" /></features>" +\
                "</testInfo></UnitTest>"
    plLogger.LogInfo("gold_meta: " + gold_meta)
    plLogger.LogInfo("result: " + result)

    assert result == gold_meta
    # Try it without the labels
    test_label_list = []
    meta = ET.Element("UnitTest")
    M.generate_test_info(meta, meth_name, meth_descript, meth_key,
                         tc_name, tc_descript, tc_key,
                         test_label_list, feature_id_list, version)
    result = ET.tostring(meta)
    plLogger.LogInfo("result:\n" + result)

    gold_meta = "<UnitTest>" + \
                "<testInfo description=\"" + meth_descript + "\" " + \
                "displayName=\"" + meth_name + "\" " + \
                "methodologyKey=\"" + meth_key + "\" " + \
                "testCaseDescription=\"" + tc_descript + "\" " + \
                "testCaseKey=\"" + tc_key + "\" " + \
                "testCaseName=\"" + tc_name + "\" " + \
                "version=\"" + version + "\">" + \
                "<labels />" + \
                "<features><feature id=\"Feature1\" /><feature id=\"Feature2\" /></features>" +\
                "</testInfo></UnitTest>"
    assert result == gold_meta
    plLogger.LogInfo("end")


def test_generate_test_resources(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    PORT1_LOCATION = "//10.14.16.20/2/1"
    PORT2_LOCATION = "//10.14.16.20/2/2"
    PORT3_LOCATION = "//10.14.16.21/2/1"
    PORT4_LOCATION = "//10.14.16.21/2/2"
    PORT5_LOCATION = "//10.14.16.22/2/1"
    PORT6_LOCATION = "//10.14.16.22/2/2"
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    # Untagged ports
    port1 = ctor.Create("Port", project)
    port1.Set("Location", PORT1_LOCATION)
    port1_id = txml_utils.get_unique_property_id(port1, "Location")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", PORT2_LOCATION)
    port2_id = txml_utils.get_unique_property_id(port2, "Location")

    # Tagged ports (EastPortGroup)
    tags = ctor.Create("Tags", project)
    east_port1 = ctor.Create("Port", project)
    east_port1.Set("Location", PORT3_LOCATION)
    east_port1_id = txml_utils.get_unique_property_id(east_port1, "Location")
    east_port2 = ctor.Create("Port", project)
    east_port2.Set("Location", PORT4_LOCATION)
    east_port2_id = txml_utils.get_unique_property_id(east_port2, "Location")
    east_tag = ctor.Create("Tag", tags)
    east_tag_id = txml_utils.get_unique_property_id(east_tag, "Name")
    east_tag.Set("Name", "EastPortGroup")
    east_port1.AddObject(east_tag, RelationType("UserTag"))
    east_port2.AddObject(east_tag, RelationType("UserTag"))

    # Tagged ports (WestPortGroup)
    west_port1 = ctor.Create("Port", project)
    west_port1.Set("Location", PORT5_LOCATION)
    west_port1_id = txml_utils.get_unique_property_id(west_port1, "Location")
    west_port2 = ctor.Create("Port", project)
    west_port2.Set("Location", PORT6_LOCATION)
    west_port2_id = txml_utils.get_unique_property_id(west_port2, "Location")
    west_tag = ctor.Create("Tag", tags)
    west_tag.Set("Name", "WestPortGroup")
    west_port1.AddObject(west_tag, RelationType("UserTag"))
    west_port2.AddObject(west_tag, RelationType("UserTag"))
    west_tag_id = txml_utils.get_unique_property_id(west_tag, "Name")

    # Port limits
    min_num_ports = "2"
    max_num_ports = "4"
    port_speed_list = "1, 40"

    M = txml_utils.MetaManager
    meta = ET.Element("UnitTest")
    M.generate_test_resources([east_tag, west_tag],
                              min_num_ports,
                              max_num_ports,
                              port_speed_list,
                              meta)
    plLogger.LogInfo("meta: " + ET.tostring(meta))

    exp_xml = "<UnitTest><testResources><resourceGroups>" + \
              "<resourceGroup name=\"Port Limits\">" + \
              "<attribute name=\"minNumPorts\" value=\"" + min_num_ports + "\" />" + \
              "<attribute name=\"maxNumPorts\" value=\"" + max_num_ports + "\" />" + \
              "<attribute name=\"portSpeedList\" value=\"" + port_speed_list + "\" />" + \
              "</resourceGroup>" + \
              "<resourceGroup displayName=\"Chassis Info\" id=\"chassisInfo\">" + \
              "<portGroups><portGroup id=\"" + east_tag_id + "\" name=\"EastPortGroup\">" + \
              "<port name=\"" + east_port1_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT3_LOCATION + "\" />" + \
              "</port>" + \
              "<port name=\"" + east_port2_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT4_LOCATION + "\" />" + \
              "</port></portGroup>" + \
              "<portGroup id=\"" + west_tag_id + "\" name=\"WestPortGroup\">" + \
              "<port name=\"" + west_port1_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT5_LOCATION + "\" />" + \
              "</port>" + \
              "<port name=\"" + west_port2_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT6_LOCATION + "\" />" + \
              "</port></portGroup>" + \
              "<portGroup id=\"untagged\" name=\"untagged\">" + \
              "<port name=\"" + port1_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT1_LOCATION + "\" />" + \
              "</port>" + \
              "<port name=\"" + port2_id + "\">" + \
              "<attribute name=\"location\" value=\"" + PORT2_LOCATION + "\" />" + \
              "</port></portGroup></portGroups>" + \
              "</resourceGroup></resourceGroups></testResources></UnitTest>"
    plLogger.LogInfo("exp_xml: " + exp_xml)

    assert ET.tostring(meta) == exp_xml
    plLogger.LogInfo("end")


# FIXME:
# Use template commands instead of profile commands
def disabled_test_generate_editable_params_with_bogus_tagged_params(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    ctor = CScriptableCreator()
    arp_cmd_name = "ArpNdStartCommand"
    arp_cmd = ctor.CreateCommand(arp_cmd_name)
    stak_cmd_name = "Ipv4NetworkProfileGroupCommand"
    stak_cmd = ctor.CreateCommand(STAK_PKG + "Ipv4NetworkProfileGroup")

    exp_prop_list = populate_mini_sequence_and_expose_properties(arp_cmd_name,
                                                                 arp_cmd,
                                                                 stak_cmd_name,
                                                                 stak_cmd)
    M = txml_utils.MetaManager
    meta = ET.Element("UnitTest")
    M.generate_editable_params(exp_prop_list, "this is a bogus input", meta)
    result = ET.tostring(meta)
    plLogger.LogInfo("result:\n" + result)
    gold_meta = "<UnitTest>" + \
                "<editableParams>" + \
                "<paramGroups name=\"exposedProperties\">" + \
                "<paramGroup id=\"" + str(arp_cmd.GetObjectHandle()) + "\" " + \
                "name=\"arpndstartcommand\">" + \
                "<params>" + \
                "<param name=\"arpndoption\">" + \
                "<attribute name=\"stcPropertyId\" value=\"arpndstartcommand.arpndoption." + \
                str(arp_cmd.GetObjectHandle()) + "\" />" + \
                "<attribute name=\"defaultValue\" value=\"TX_ONLY\" />" + \
                "<attribute name=\"type\" value=\"integer\" />" + \
                "<attribute name=\"units\" value=\"ounces\" />" + \
                "<attribute name=\"minInclusive\" value=\"0\" />" + \
                "<attribute name=\"maxInclusive\" value=\"unbounded\" />" + \
                "</param>" + \
                "<param name=\"forcearp\">" + \
                "<attribute name=\"stcPropertyId\" value=\"arpndstartcommand.forcearp." + \
                str(arp_cmd.GetObjectHandle()) + "\" />" + \
                "<attribute name=\"defaultValue\" value=\"true\" />" + \
                "<attribute name=\"type\" value=\"bool\" />" + \
                "<attribute name=\"units\" value=\"ounces\" />" + \
                "<attribute name=\"minInclusive\" value=\"0\" />" + \
                "<attribute name=\"maxInclusive\" value=\"unbounded\" />" + \
                "</param>" + \
                "<param name=\"waitforarptofinish\">" + \
                "<attribute name=\"stcPropertyId\" " + \
                "value=\"arpndstartcommand.waitforarptofinish." + \
                str(arp_cmd.GetObjectHandle()) + "\" />" + \
                "<attribute name=\"defaultValue\" value=\"true\" />" + \
                "<attribute name=\"type\" value=\"bool\" />" + \
                "<attribute name=\"units\" value=\"ounces\" />" + \
                "<attribute name=\"minInclusive\" value=\"0\" />" + \
                "<attribute name=\"maxInclusive\" value=\"unbounded\" />" + \
                "</param></params></paramGroup>" + \
                "<paramGroup id=\"" + str(stak_cmd.GetObjectHandle()) + "\" " + \
                "name=\"ipv4networkprofilegroupcommand\">" + \
                "<params>" + \
                "<param name=\"devicecount\">" + \
                "<attribute name=\"stcPropertyId\" " + \
                "value=\"spirent.methodology." + \
                "ipv4networkprofilegroupcommand.devicecount." + \
                str(stak_cmd.GetObjectHandle()) + "\" />" + \
                "<attribute name=\"defaultValue\" value=\"1\" />" + \
                "<attribute name=\"type\" value=\"integer\" />" + \
                "<attribute name=\"units\" value=\"ounces\" />" + \
                "<attribute name=\"minInclusive\" value=\"0\" />" + \
                "<attribute name=\"maxInclusive\" value=\"unbounded\" />" + \
                "</param></params></paramGroup></paramGroups>" + \
                "<paramGroups name=\"taggedProperties\" />" + \
                "</editableParams>" + \
                "</UnitTest>"
    plLogger.LogInfo("gold:\n" + gold_meta)
    assert result == gold_meta
    plLogger.LogInfo("end")


def test_generate_topology_info(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")

    gold_meta = "<UnitTest>" + \
                "<topologyInfo description=\"Reserved for future use\" name=\"Reserved\" />" + \
                "</UnitTest>"

    # Call the MetaManager
    plLogger.LogInfo("Generate the TXML...")
    meta = ET.Element("UnitTest")
    txml_utils.MetaManager.generate_topology_info(meta)
    plLogger.LogInfo("Actual:\n" + ET.tostring(meta))

    plLogger.LogInfo("gold_meta:\n" + gold_meta)
    assert ET.tostring(meta) == gold_meta
    plLogger.LogInfo("end")


def disabled_test_generate_traffic_info(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    stc_sys = CStcSystem.Instance()

    exp_prop_list, gold_meta = populate_sequence_and_expose_traffic_properties()

    sequencer = stc_sys.GetObject("Sequencer")
    if sequencer is None:
        plLogger.LogError("sequencer cannot be found")

    # Build the SequenceInfo
    plLogger.LogInfo("Validate and load the sequence...")
    si = SequenceInfo()
    assert si.validate_and_load_profile_based_sequence(sequencer.GetCollection("CommandList"))

    M = txml_utils.MetaManager
    meta = ET.Element("UnitTest")
    M.generate_traffic_info(si, "Just a name", "My description", meta)
    result = ET.tostring(meta)

    plLogger.LogInfo("result:\n" + result)
    plLogger.LogInfo("gold:\n" + gold_meta)

    assert result == gold_meta
    plLogger.LogInfo("end")


def test_extract_methodology_name_from_file(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    # Cleanup from the last run... Just in case....
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)
    # Create a TXML file
    f = open(mmuc.MM_UTEST_FILE_NAME, "w")
    f.write(mmuc.MM_UTEST_HEADER + mmuc.MM_UTEST_FOOTER)
    f.close()

    test_name = txml_utils.extract_methodology_name_from_file(
        mmuc.MM_UTEST_FILE_NAME)
    # Clean up
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)

    assert test_name == mmuc.MM_UTEST_DISPLAY_NAME
    plLogger.LogInfo("end")


def test_extract_test_case_name_from_file(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    # Cleanup from the last run... Just in case....
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)
    # Create a TXML file
    f = open(mmuc.MM_UTEST_FILE_NAME, "w")
    f.write(mmuc.MM_UTEST_HEADER + mmuc.MM_UTEST_FOOTER)
    f.close()

    test_case = txml_utils.extract_test_case_name_from_file(mmuc.MM_UTEST_FILE_NAME)
    # Clean up
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)

    assert test_case == mmuc.MM_UTEST_INSTANCE
    plLogger.LogInfo("end")


def test_extract_test_labels_from_file(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("begin")
    # Cleanup from the last run... Just in case....
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)
    # Create a TXML file
    f = open(mmuc.MM_UTEST_FILE_NAME, "w")
    f.write(mmuc.MM_UTEST_HEADER + mmuc.MM_UTEST_FOOTER)
    f.close()

    label_list = txml_utils.extract_test_labels_from_file(mmuc.MM_UTEST_FILE_NAME)
    # Clean up
    UnitTestUtils.delete_test(mmuc.MM_UTEST_FILE_NAME)

    assert len(label_list) == 2
    assert mmuc.MM_UTEST_LABEL1 in label_list
    assert mmuc.MM_UTEST_LABEL2 in label_list
    plLogger.LogInfo("end")


def get_tagged_xml():
    tagged_xml = "<paramGroups>\
    <paramGroup name=\"LoadTemplateGroupCommand.1234\">\
    <params>\
    <param tag=\"Bgp\" id=\"1234\">\
    <attribute name=\"BgpRouterConfig.AsNum\" value=\"564\"/>\
    <attribute name=\"BgpRouterConfig.PeerAs\" value=\"111\"/>\
    </param>\
    <param tag=\"OuterVlan\" id=\"5678\">\
    <attribute name=\"VlanIfnIf.VlanId\" value=\"100\"/>\
    </param>\
    </params>\
    </paramGroup>\
    <paramGroup name=\"LoadTemplateGroupCommand.5678\">\
    <params>\
    <param tag=\"Bgp\" id=\"9012\">\
    <attribute name=\"BgpRouterConfig.AsNum\" value=\"444\"/>\
    <attribute name=\"BgpRouterConfig.PeerAs\" value=\"333\"/>\
    </param>\
    <param tag=\"InnerVlan\" id=\"3456\">\
    <attribute name=\"VlanIfnIf.VlanId\" value=\"101\"/>\
    </param>\
    </params>\
    </paramGroup>\
    </paramGroups>"
    return tagged_xml
