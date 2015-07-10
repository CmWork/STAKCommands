from StcIntPythonPL import *
import json
import xml.etree.ElementTree as etree
from utils.txml_utils import MetaManager as meta_mgr
from utils.estimation_utils import SequencerEstimator
import os

# FIXME:
# Move this somewhere else
TIE_PORT_PROFILES = "portProfiles"
TIE_PROFILE_ID = "profileId"
TIE_PORT_COUNT = "portCount"
TIE_PORT_LOCATIONS = "portLocations"
TIE_DEV_COUNT = "deviceCount"

# G/A
TIE_GEN_STREAM_COUNT = "generator.streams.count"
TIE_ANA_STREAM_COUNT = "analyzer.anaStreams"

# Access
# (?) - does not use RCM files

# Routing
TIE_BGP_SESS_COUNT = "BGP.maxBgpSessionCount"

# Datacenter
TIE_OPENFLOW_MAX_BLOCK_COUNT = "OPENFLOW.maxOpenflowBlockCount"


# FIXME:
# Move this someplace else too?
class TxmlSummary(object):
    def __init__(self, test_methodology, test_instance, path):

        # Basic information in the TXML
        self.test_methodology = test_methodology
        self.test_instance = test_instance
        self.path = path

        # List of the exposed property IDs
        self.prop_id_list = []

        # Port Group Dictionary indexed on the group_id
        self.port_group_dict = {}

        # List of NetworkProfileSummary objects
        self.net_prof_summ_list = []

        # # Map of NetworkProfile objects to port locations
        # self.port_net_profile_map = {}

    def print_contents(self):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("test_methodology: " + str(self.test_methodology))
        plLogger.LogDebug("test_instance: " + str(self.test_instance))
        plLogger.LogDebug("path: " + str(self.path))
        plLogger.LogDebug("prop_id_list: " + str(self.prop_id_list))
        plLogger.LogDebug("port_group_dict: " + str(self.port_group_dict))
        plLogger.LogDebug("net_prof_summ_list:")
        for net_prof_summ in self.net_prof_summ_list:
            net_prof_summ.print_contents()


# FIXME:
# Move this someplace else too?
# Network Profile internals:
# Device Count
# Protocols/Routes
# Network Stack?
# What else?
class NetworkProfileSummary(object):
    def __init__(self):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("init")

        # Basic information
        self.name = ""
        self.id = ""
        self.device_count = 0
        self.port_group_id = None
        self.net_if_stack = []

        # Protocols
        self.has_bgp = False
        self.has_dhcpv4 = False
        plLogger.LogDebug("done")

    def print_contents(self):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("name: " + str(self.name))
        plLogger.LogDebug("id: " + str(self.id))
        plLogger.LogDebug("device_count: " + str(self.device_count))
        plLogger.LogDebug("port_group_id: " + str(self.port_group_id))
        plLogger.LogDebug("net_if_stack: " + str(self.net_if_stack))
        plLogger.LogDebug("has_bgp: " + str(self.has_bgp))
        plLogger.LogDebug("has_dhcpv4: " + str(self.has_dhcpv4))


def validate(StmMethodology, StmTestCase, InputJson):
    return ''


def parse_exposed_properties(root, txml_summ):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_exposed_properties.EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return
    if root is None:
        plLogger.LogError("ERROR: Invalid root Element passed in!")
        return

    # Clear out the prop_id_list and rebuild
    txml_summ.prop_id_list[:] = []
    for param_tag in root.findall(".//" + meta_mgr.EP_PARAM):
        parse_param_tag(param_tag, txml_summ)
    plLogger.LogDebug("prop_id_list: " + str(txml_summ.prop_id_list))
    plLogger.LogDebug("end.parse_exposed_properties.EstimateTxmlProfileObjectExpansionCommand")


def parse_param_tag(param_tag, txml_summ):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_param_tag.EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return
    if param_tag is None:
        plLogger.LogError("ERROR: Invalid param_tag Element passed in!")
        return
    prop_id = None
    for attr_tag in param_tag.findall(meta_mgr.EP_ATTR):
        name = attr_tag.get(meta_mgr.EP_NAME)
        if name == meta_mgr.EP_PROP_ID:
            prop_id = attr_tag.get(meta_mgr.EP_VALUE)
            plLogger.LogDebug(" STC Property ID: " + prop_id)
            txml_summ.prop_id_list.append(prop_id)
            return

    plLogger.LogDebug("end.parse_param_tag.EstimateTxmlProfileObjectExpansionCommand")


def parse_test_resources(root, txml_summ):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_test_resources.EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return
    if root is None:
        plLogger.LogError("ERROR: Invalid root Element passed in!")
        return

    # Clear out the port_group_dict
    txml_summ.port_group_dict.clear()
    for port_group in root.findall(".//" + meta_mgr.TR_PORT_GROUP):
        parse_test_resource_port_group(port_group, txml_summ)
    plLogger.LogDebug("txml_summ.port_group_dict: " + str(txml_summ.port_group_dict))
    plLogger.LogDebug("end.parse_test_resources.EstimateTxmlProfileObjectExpansionCommand")


def parse_test_resource_port_group(root, txml_summ):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_test_resource_port_group.\
                        EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return
    if root is None:
        plLogger.LogError("ERROR: Invalid root Element passed in!")
        return

    group_id = root.get(meta_mgr.TR_ID)
    name = root.get("name")
    txml_summ.port_group_dict[group_id] = {}
    txml_summ.port_group_dict[group_id]["name"] = name
    txml_summ.port_group_dict[group_id]["port_list"] = []
    for port in root.findall(".//" + meta_mgr.TR_PORT):
        # port_name = port.get(meta_mgr.TR_NAME)
        attr_name = ""
        attr_val = ""
        for attr in port.findall(meta_mgr.TR_ATTR):
            attr_name = attr.get(meta_mgr.TR_NAME)
            # plLogger.LogDebug("attr_name: " + attr_name)
            # plLogger.LogDebug("attr_val: " + attr_val)
            if attr_name == meta_mgr.TR_LOCATION:
                attr_val = attr.get(meta_mgr.TR_VALUE)
                txml_summ.port_group_dict[group_id]["port_list"].append(attr_val)

    plLogger.LogDebug("end.parse_test_resource_port_group.\
                        EstimateTxmlProfileObjectExpansionCommand")


def parse_topology_info(root, txml_summ):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_topology_info.EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return
    if root is None:
        plLogger.LogError("ERROR: Invalid root Element passed in!")
        return

    txml_summ.net_prof_summ_list[:] = []
    for child in root:
        if child.tag == meta_mgr.TPI_NET_PROFILE:
            net_prof_summ = parse_network_info(child)
            net_prof_summ.print_contents()
            txml_summ.net_prof_summ_list.append(net_prof_summ)

    plLogger.LogDebug("end.parse_topology_info.EstimateTxmlProfileObjectExpansionCommand")
    return


def parse_network_info(root):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.parse_network_info.EstimateTxmlProfileObjectExpansionCommand")

    if root is None:
        plLogger.LogError("ERROR: Invalid root Element passed in!")
        return

    net_prof_summ = NetworkProfileSummary()
    net_prof_summ.name = root.get(meta_mgr.TPI_NAME)

    plLogger.LogDebug("name: " + net_prof_summ.name)

    net_prof_summ.id = root.get(meta_mgr.TPI_ID)
    net_prof_summ.port_group_id = root.get(meta_mgr.TPI_PORT_GROUP_ID)

    plLogger.LogDebug(" NetworkProfile: " + net_prof_summ.name +
                      "  devCount: " + str(net_prof_summ.device_count) +
                      "  portGroup: " + str(net_prof_summ.port_group_id))
    for child in root:
        plLogger.LogDebug("child.tag: " + str(child.tag))
        if child.tag == meta_mgr.TPI_ATTR:
            plLogger.LogDebug(" <attribute> name: " + str(child.get("name")))
            plLogger.LogDebug(" <attribute> value: " + str(child.get("value")))
            attr_name = child.get(meta_mgr.TPI_NAME)
            if attr_name == meta_mgr.TPI_DEVICE_COUNT:
                net_prof_summ.device_count = int(child.get(meta_mgr.TPI_VALUE))
        if child.tag == meta_mgr.INTERFACE:
            net_prof_summ.net_if_stack.append(child.get(meta_mgr.TPI_TYPE))

        elif child.tag == meta_mgr.PROTOCOL:
            proto = child.get(meta_mgr.TPI_NAME)
            if proto == "BGP":
                net_prof_summ.has_bgp = True

    plLogger.LogDebug("end.parse_network_info.EstimateTxmlProfileObjectExpansionCommand")
    return net_prof_summ


def gen_json(txml_summ, deviceCountUtils=None):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.gen_json.EstimateTxmlProfileObjectExpansionCommand")

    if txml_summ is None:
        plLogger.LogError("ERROR: Invalid TxmlSummary object!")
        return

    json_dict = {}
    json_dict[TIE_PORT_PROFILES] = []
    net_prof_dict = {}
    plLogger.LogDebug(" done init")

    net_prof_count = 0
    for net_prof_summ in txml_summ.net_prof_summ_list:
        plLogger.LogDebug(" process net_prof_summ...")

        net_prof_dict[TIE_PROFILE_ID] = str(net_prof_summ.id)
        plLogger.LogDebug("net_prof_summ.id is: " + str(net_prof_dict[TIE_PROFILE_ID]))
        port_list = txml_summ.port_group_dict[net_prof_summ.port_group_id]["port_list"]
        net_prof_dict[TIE_PORT_COUNT] = len(port_list)
        net_prof_dict[TIE_PORT_LOCATIONS] = []
        for port_loc in port_list:
            net_prof_dict[TIE_PORT_LOCATIONS].append(port_loc)
        if deviceCountUtils is not None:
            net_prof_dict[TIE_DEV_COUNT] = deviceCountUtils.estimate_device_count(net_prof_count)
            net_prof_count = net_prof_count + 1
        else:
            net_prof_dict[TIE_DEV_COUNT] = net_prof_summ.device_count
        if net_prof_summ.has_bgp:
            net_prof_dict[TIE_BGP_SESS_COUNT] = net_prof_summ.device_count

        json_dict[TIE_PORT_PROFILES].append(net_prof_dict)
        net_prof_dict = {}

    plLogger.LogDebug("JSON: " + json.dumps(json_dict))
    plLogger.LogDebug("end.gen_json.EstimateTxmlProfileObjectExpansionCommand")
    return json.dumps(json_dict)


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def run(StmMethodology, StmTestCase, InputJson):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.EstimateTxmlProfileObjectExpansionCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = get_this_cmd()

    test_meth = hnd_reg.Find(StmMethodology)
    if test_meth is None:
        plLogger.LogError("ERROR: Was unable to find StmMethodology with handle " +
                          str(StmMethodology) + " in the list of installed tests.")
        return False
    test_name = test_meth.Get('TestMethodologyName')
    plLogger.LogDebug("Found Methodology for " + test_name)

    sequencerXmlFilePath = os.path.join(test_meth.Get("Path"), "sequencer.xml")

    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None:
        plLogger.LogError("ERROR: Was unable to find StmTestCase with handle " +
                          str(StmTestCase) + " in the list of installed test cases.")
        return False
    test_case_name = test_case.Get('TestCaseName')
    plLogger.LogDebug("Found StmTestCase for " + test_case_name)

    # StmTestCase contains the path to the TXML
    txml_path = test_case.Get("Path")

    plLogger.LogDebug("txml_path is " + str(txml_path))

    # Read the TXML and find the different sections.
    # In particular, the testParams section will provide the set of parameters
    # (and their IDs) that the user can modify.  The topologyInfo and related
    # sections will provide the rest of the defaults.
    # The InputJson (input) will provide the new values for the parameters in
    # the testParams that the user has modified.
    tree = etree.parse(txml_path)
    root = tree.getroot()

    txml_summ = TxmlSummary(test_meth, test_case, txml_path)

    for child in root:
        plLogger.LogDebug(" tag: " + child.tag)
        if child.tag == meta_mgr.EDITABLE_PARAMS:
            plLogger.LogDebug("Found the <" +
                              meta_mgr.EDITABLE_PARAMS + "> tag")
            parse_exposed_properties(child, txml_summ)
        elif child.tag == meta_mgr.TEST_RESOURCES:
            plLogger.LogDebug("Found the <" +
                              meta_mgr.TEST_RESOURCES + "> tag")
            parse_test_resources(child, txml_summ)
        elif child.tag == meta_mgr.TOPOLOGY_INFO:
            plLogger.LogDebug("Found the <" +
                              meta_mgr.TOPOLOGY_INFO + "> tag")
            parse_topology_info(child, txml_summ)
            # FIXME: This entire command relies on the profile schema, and
            # this change is only to prevent unit test failures
            deviceCountUtils = SequencerEstimator(filename=sequencerXmlFilePath)
            if deviceCountUtils.initializeElements() is False:
                deviceCountUtils = None
            json_str = gen_json(txml_summ, deviceCountUtils)
            plLogger.LogDebug("json_str: " + json_str)
            this_cmd.Set("OutputJson", json_str)
        # elif child.tag == meta_mgr.TRAFFIC_INFO:
        #     plLogger.LogDebug("Found the <trafficInfo> tag")
    plLogger.LogDebug("end.run.EstimateTxmlProfileObjectExpansionCommand")
    return True


def reset():
    return True
