from StcIntPythonPL import *
import os
import sys
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), "STAKCommands", "spirent", "methodology"))
import manager.EstimateTxmlProfileObjectExpansionCommand as \
    EstTxmlObjExpCmd
from manager.utils.estimation_utils import SequencerEstimator


def test_parse_exposed_properties(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    # Build a sample XML string
    txml_str = "<testParams>" + \
        "<paramGroups>" + \
        "<paramGroup id=\"2580\" name=\"createipv4networkinfocommand\">" + \
        "<params>" + \
        "<param name=\"ipv4addr\">" + \
        "<attribute name=\"stcPropertyId\" " + \
        "value=\"prop1.Ipv4Address\"/>" + \
        "<attribute name=\"defaultValue\" value=\"1.1.1.1\"/>" + \
        "<attribute name=\"type\" value=\"ip\"/>" + \
        "<attribute name=\"units\" value=\"ounces\"/>" + \
        "<attribute name=\"minInclusive\" value=\"0\"/>" + \
        "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
        "</param>" + \
        "<param name=\"ipv4addrstep\">" + \
        "<attribute name=\"stcPropertyId\" " + \
        "value=\"prop2.Ipv4AddressStep\"/>" + \
        "<attribute name=\"defaultValue\" value=\"0.0.0.1\"/>" + \
        "<attribute name=\"type\" value=\"ip\"/>" + \
        "<attribute name=\"units\" value=\"ounces\"/>" + \
        "<attribute name=\"minInclusive\" value=\"0\"/>" + \
        "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
        "</param>" + \
        "<param name=\"ipv4addrportstep\">" + \
        "<attribute name=\"stcPropertyId\" " + \
        "value=\"prop3.Ipv4AddressPortStep\"/>" + \
        "<attribute name=\"defaultValue\" value=\"0.0.1.0\"/>" + \
        "<attribute name=\"type\" value=\"ip\"/>" + \
        "<attribute name=\"units\" value=\"ounces\"/>" + \
        "<attribute name=\"minInclusive\" value=\"0\"/>" + \
        "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
        "</param>" + \
        "</params>" + \
        "</paramGroup>" + \
        "</paramGroups>" + \
        "</testParams>"
    root = etree.fromstring(txml_str)
    txml_summ = EstTxmlObjExpCmd.TxmlSummary(None, None, None)
    EstTxmlObjExpCmd.parse_exposed_properties(root, txml_summ)
    assert txml_summ.prop_id_list == ["prop1.Ipv4Address",
                                      "prop2.Ipv4AddressStep",
                                      "prop3.Ipv4AddressPortStep"]


def test_parse_param_tag(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    # Build a sample XML string
    txml_str = "<param name=\"ipv4addr\">" + \
        "<attribute name=\"stcPropertyId\" " + \
        "value=\"prop1.Ipv4Address\"/>" + \
        "<attribute name=\"defaultValue\" value=\"1.1.1.1\"/>" + \
        "<attribute name=\"type\" value=\"ip\"/>" + \
        "<attribute name=\"units\" value=\"ounces\"/>" + \
        "<attribute name=\"minInclusive\" value=\"0\"/>" + \
        "<attribute name=\"maxInclusive\" value=\"unbounded\"/>" + \
        "</param>"
    root = etree.fromstring(txml_str)
    txml_summ = EstTxmlObjExpCmd.TxmlSummary(None, None, None)
    EstTxmlObjExpCmd.parse_param_tag(root, txml_summ)
    assert txml_summ.prop_id_list == ["prop1.Ipv4Address"]


def test_parse_test_resources(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    tag1 = "tag.name.2046"
    tag2 = "tag.name.2047"
    csp1 = "//10.28.225.100/1/1"
    csp2 = "//10.28.225.172/1/1"

    # Build a sample XML string
    txml_str = "<testResources>" + \
        "<resourceGroups>" + \
        "<resourceGroup displayName=\"Chassis Info\" id=\"chassisInfo\">" + \
        "<portGroups>" + \
        "<portGroup id=\"" + tag1 + "\" name=\"EastPortGroup\">" + \
        "<port name=\"port.location.2388\">" + \
        "<attribute name=\"location\" value=\"" + csp1 + "\"/>" + \
        "<attribute name=\"workload\" value=\"performance\"/>" + \
        "</port>" + \
        "</portGroup>" + \
        "<portGroup id=\"" + tag2 + "\" name=\"WestPortGroup\">" + \
        "<port name=\"port.location.2468\">" + \
        "<attribute name=\"location\" value=\"" + csp2 + "\"/>" + \
        "<attribute name=\"workload\" value=\"performance\"/>" + \
        "</port>" + \
        "</portGroup>" + \
        "</portGroups>" + \
        "<workloads>" + \
        "<workload name=\"Performance\">" + \
        "<attribute name=\"minPerPortMemory\" value=\"24\"/>" + \
        "<attribute name=\"unitsMemory\" value=\"GB\"/>" + \
        "<attribute name=\"minPerPortStorage\" value=\"512\"/>" + \
        "<attribute name=\"unitsStorage\" value=\"MB\"/>" + \
        "<attribute name=\"minPerPortVCPU\" value=\"4\"/>" + \
        "<attribute name=\"unitsVCPU\" value=\"SpiMips\"/>" + \
        "<attribute name=\"portPortSpeeds\" value=\"10,40,100\"/>" + \
        "<attribute name=\"unitsPortSpeed\" value=\"Gpbs\"/>" + \
        "</workload>" + \
        "</workloads>" + \
        "</resourceGroup>" + \
        "</resourceGroups>" + \
        "</testResources>"
    root = etree.fromstring(txml_str)
    txml_summ = EstTxmlObjExpCmd.TxmlSummary(None, None, None)
    EstTxmlObjExpCmd.parse_test_resources(root, txml_summ)

    # Check the data structure
    assert len(txml_summ.port_group_dict.keys()) == 2
    assert tag1 in txml_summ.port_group_dict.keys()
    assert tag2 in txml_summ.port_group_dict.keys()
    assert len(txml_summ.port_group_dict[tag1]["port_list"]) == 1
    assert txml_summ.port_group_dict[tag1]["port_list"][0] == csp1
    assert len(txml_summ.port_group_dict[tag2]["port_list"]) == 1
    assert txml_summ.port_group_dict[tag2]["port_list"][0] == csp2


def d_test_parse_network_info(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    # Build a sample XML string
    txml_str = "<networkProfile name=\"East1\" " + \
        "description=\"desc\" " + \
        "portGroupId=\"1632\" " + \
        "id=\"NetProfGroupCmd.1\">" + \
        "<attribute name=\"deviceCount\" value=\"20\" />" + \
        "<interface type=\"Ipv4\">" + \
        "<attribute name=\"gateway\" value=\"1.1.1.1\"/>" + \
        "<attribute name=\"ipAddress\" value=\"1.1.1.10\" " + \
        "id=\"CreateIpv4NetworkProfile1.StartingIp\" /> " + \
        "<attribute name=\"ipAddressStep\" value=\"0.0.0.1\" " + \
        "id=\"CreateIpv4NetworkProfile1.StepIp\" /> " + \
        "<attribute name=\"ipAddressPortStep\" value=\"0.1.0.0\" " + \
        "id=\"CreateIpv4NetworkProfile1.PortStepIp\" />" + \
        "<attribute name=\"prefix\" value=\"24\"/>" + \
        "</interface>" + \
        "<interface type=\"Vlan\">" + \
        "<attribute name=\"id\" value=\"100\"/>" + \
        "</interface>" + \
        "<interface type=\"EthII\">" + \
        "<attribute name=\"macAddress\" value=\"00:01:24:56:1B:43\"/>" + \
        "</interface>" + \
        "<protocol name=\"BGP\">" + \
        "<attribute name=\"asNumber\" value=\"123\"/>" + \
        "<attribute name=\"dutIpv4Addr\" value=\"1.1.1.1\"/>" + \
        "<attribute name=\"dutIpv6Addr\" value=\"2000::1\"/>" + \
        "<attribute name=\"eiBgp\" value=\"123\"/>" + \
        "<attribute name=\"peerAs\" value=\"234\"/>" + \
        "<attribute name=\"ipVersion\" value=\"4\"/>" + \
        "</protocol>" + \
        "</networkProfile>"
    root = etree.fromstring(txml_str)
    net_prof_summ = EstTxmlObjExpCmd.parse_network_info(root)

    # Check the data structure
    assert net_prof_summ.name == "East1"
    assert net_prof_summ.id == "NetProfGroupCmd.1"
    assert net_prof_summ.device_count == 20
    assert net_prof_summ.port_group_id == "1632"
    assert net_prof_summ.net_if_stack == ["Ipv4", "Vlan", "EthII"]

sequencer_xml = "<?xml version=\"1.0\" encoding=\"windows-1252\"?>" + \
                "<StcSystem id=\"1\" serializationBase=\"true\" " + \
                "InSimulationMode=\"FALSE\" " + \
                "UseSmbMessaging=\"FALSE\" " + \
                "ApplicationName=\"TestCenter\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"StcSystem 1\"> " + \
                "<Sequencer id=\"8\" " + \
                "CommandList=\"4254\" " + \
                "BreakpointList=\"\" " + \
                "DisabledCommandList=\"\" " + \
                "CleanupCommand=\"4228\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Sequencer\"> " + \
                "<Relation type=\"SequencerFinalizeType\" target=\"4228\"/> " + \
                "<spirent.methodology.manager.MethodologyGroupCommand id=\"4254\" " + \
                "InputJson=\"\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "CommandList=\"4200 4201\" " + \
                "ExecutionMode=\"BACKGROUND\" " + \
                "GroupCategory=\"REGULAR_COMMAND\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Methodology Manager: Dispatch Input Command 3\"> " + \
                "<spirent.methodology.DeleteProfileAndGeneratedObjectsCommand id=\"4200\" " + \
                "DeleteProfiles=\"TRUE\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "ErrorOnFailure=\"TRUE\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Custom Builder Commands: Delete Profile and associated Generated Objects Command 1\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4255\"/> " + \
                "</spirent.methodology.DeleteProfileAndGeneratedObjectsCommand> " + \
                "<spirent.methodology.TopologyTestGroupCommand id=\"4201\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "CommandList=\"4202 4215\" " + \
                "ExecutionMode=\"BACKGROUND\" " + \
                "GroupCategory=\"REGULAR_COMMAND\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Test Methodology: Topology Test Group Command 1\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4281\"/> " + \
                "<spirent.methodology.TrafficForwardingTestGroupCommand id=\"4215\" " + \
                "TopologyProfile=\"0\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "CommandList=\"4216\" " + \
                "ExecutionMode=\"BACKGROUND\" " + \
                "GroupCategory=\"REGULAR_COMMAND\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Test Group Commands: Traffic Forwarding Test 1\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4280\"/> " + \
                "<spirent.methodology.TrafficProfileIterationGroupCommand id=\"4216\" " + \
                "ObjectList=\"\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "CommandList=\"4217\" " + \
                "ExecutionMode=\"BACKGROUND\" " + \
                "GroupCategory=\"REGULAR_COMMAND\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Iteration Framework: Traffic Profile Iteration Group Command 4\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4279\"/> " + \
                "<SequencerWhileCommand id=\"4217\" " + \
                "ExpressionCommand=\"4218\" " + \
                "Condition=\"PASSED\" " + \
                "CommandList=\"4249 4219 4220 4221 4222 4223 4224 4225 4226\" " + \
                "ExecutionMode=\"BACKGROUND\" " + \
                "GroupCategory=\"REGULAR_COMMAND\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"While\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4278\"/> " + \
                "<spirent.methodology.ObjectIteratorCommand id=\"4218\" " + \
                "IterMode=\"STEP\" " + \
                "StepVal=\"10\" " + \
                "ValueType=\"LIST\" " + \
                "ValueList=\"20 25 30 45 50 55 60\" " + \
                "BreakOnFail=\"FALSE\" " + \
                "MinVal=\"0\" " + \
                "MaxVal=\"100\" " + \
                "PrevIterVerdict=\"TRUE\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "ErrorOnFailure=\"FALSE\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Iterators: Object Iterator Command\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4268\"/> " + \
                "</spirent.methodology.ObjectIteratorCommand> " + \
                "<WaitCommand id=\"4222\" " + \
                "WaitTime=\"10\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Wait 4\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4272\"/> " + \
                "</WaitCommand> " + \
                "<spirent.methodology.NetworkProfileDeviceCountConfigCommand id=\"4249\" " + \
                "PercentageList=\"50 25\" " + \
                "ObjectList=\"\" " + \
                "CurrVal=\"\" " + \
                "Iteration=\"0\" " + \
                "CommandName=\"\" " + \
                "PackageName=\"spirent\" " + \
                "ErrorOnFailure=\"TRUE\" " + \
                "AutoDestroy=\"FALSE\" " + \
                "ExecuteSynchronous=\"FALSE\" " + \
                "ProgressEnable=\"TRUE\" " + \
                "ProgressIsSafeCancel=\"TRUE\" " + \
                "Active=\"TRUE\" " + \
                "LocalActive=\"TRUE\" " + \
                "Name=\"Configurators: Iterator Config Device Counts Command 4\"> " + \
                "<Relation type=\"SequenceableProperties\" target=\"4277\"/> " + \
                "</spirent.methodology.NetworkProfileDeviceCountConfigCommand> " + \
                "</SequencerWhileCommand> " + \
                "</spirent.methodology.TrafficProfileIterationGroupCommand> " + \
                "</spirent.methodology.TrafficForwardingTestGroupCommand> " + \
                "</spirent.methodology.TopologyTestGroupCommand> " + \
                "</spirent.methodology.manager.MethodologyGroupCommand> " + \
                "</Sequencer> " + \
                "</StcSystem>"


def notatest_gen_json(stc):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    pg_tag1 = "tag.name.12"
    pg_port1 = "//10.14.16.20/2/1"
    pg_port2 = "//10.14.16.20/2/2"

    pg_tag2 = "tag.name.13"
    pg_port3 = "//10.14.16.27/1/1"
    pg_port4 = "//10.14.16.27/1/2"

    # Build a couple of NetworkProfileSummary data structures
    net_prof_summ1 = EstTxmlObjExpCmd.NetworkProfileSummary()
    net_prof_summ1.name = "North"
    net_prof_summ1.id = "NetProfGroupCmd.1"
    net_prof_summ1.device_count = 222
    net_prof_summ1.port_group_id = pg_tag1
    net_prof_summ1.net_if_stack = ["eth", "ipv4"]
    net_prof_summ1.has_bgp = True

    net_prof_summ2 = EstTxmlObjExpCmd.NetworkProfileSummary()
    net_prof_summ2.name = "South"
    net_prof_summ2.id = "NetProfGroupCmd.2"
    net_prof_summ2.device_count = 333
    net_prof_summ2.port_group_id = pg_tag2
    net_prof_summ2.net_if_stack = ["Ipv4", "Vlan", "EthII"]

    # net_prof_summ1.print_contents()
    # net_prof_summ2.print_contents()

    # Build the TxmlSummary data structure
    txml_summ = EstTxmlObjExpCmd.TxmlSummary(None, None, None)
    txml_summ.net_prof_summ_list = [net_prof_summ1, net_prof_summ2]
    txml_summ.port_group_dict[pg_tag1] = {}
    txml_summ.port_group_dict[pg_tag1]["port_list"] = [pg_port1, pg_port2]
    txml_summ.port_group_dict[pg_tag2] = {}
    txml_summ.port_group_dict[pg_tag2]["port_list"] = [pg_port3, pg_port4]

    txml_summ.print_contents()

    deviceCountUtils = SequencerEstimator(str=sequencer_xml)

    # Generate the JSON output
    json_str = EstTxmlObjExpCmd.gen_json(txml_summ, deviceCountUtils)

    exp_json = "{\"portProfiles\": " + \
        "[{\"deviceCount\": 142, \"profileId\": \"NetProfGroupCmd.1\", " + \
        "\"portLocations\": [\"//10.14.16.20/2/1\", \"//10.14.16.20/2/2\"], " + \
        "\"BGP.maxBgpSessionCount\": 222, \"portCount\": 2}, " + \
        "{\"deviceCount\": 71, \"profileId\": \"NetProfGroupCmd.2\", " + \
        "\"portLocations\": [\"//10.14.16.27/1/1\", \"//10.14.16.27/1/2\"], " + \
        "\"portCount\": 2}]}"

    plLogger.LogInfo("json_str: " + str(json_str))
    plLogger.LogInfo("exp_json: " + str(exp_json))
    assert json_str == exp_json
