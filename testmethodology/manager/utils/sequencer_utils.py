from StcIntPythonPL import *


# FIXME: As this class relies on the profile-based model of methodology, it
#        will be deprecated with the profile-based model
class SequenceInfo(object):
    # Constants (group names)
    STAK_PKG = "spirent.methodology."
    TEST_TOPO_GROUP = STAK_PKG + "TopologyTestGroupCommand"
    TEST_GROUP = STAK_PKG + "TestGroupCommand"
    TOPO_GROUP = STAK_PKG + "TopologyGroupCommand"
    ITER_GROUP = STAK_PKG + "IterationGroupCommand"
    OBJ_ITER_GROUP = STAK_PKG + "ObjectIteratorCommand"
    ITER_CONFIG = STAK_PKG + "IteratorConfigCommand"
    ITER_VALIDATE = STAK_PKG + "IteratorValidateCommand"
    TOPO_PROFILE_GROUP = STAK_PKG + "TopologyProfileGroupCommand"
    NETWORK_PROFILE_GROUP = STAK_PKG + "NetworkProfileGroupCommand"
    CREATE_ETH_NETWORK_INFO = STAK_PKG + "CreateEthernetNetworkInfoCommand"
    CREATE_IPV4_NETWORK_INFO = STAK_PKG + "CreateIpv4NetworkInfoCommand"
    CREATE_BGP_PROTOCOL_PROFILE = STAK_PKG + "routing.BgpProtocolProfileGroupCommand"
    CREATE_VLAN_NETWORK_INFO = STAK_PKG + "CreateVlanNetworkInfoCommand"
    CREATE_IPV4_TOS_TRAFFIC_PROFILE = "spirent.trafficcenter.CreateIPv4TosTrafficProfileCommand"
    CREATE_TRAFFIC_PROFILE = "spirent.trafficcenter.CreateTrafficProfileCommand"

    # Sequence Info commands, lists and maps
    test_topo_group_cmd = None
    topo_group_cmd = None
    test_group_cmd = None
    net_prof_group_cmd_list = None
    net_prof_group_cmd_map = None
    trf_cmd = None
    iter_group_cmd = None
    topo_info_name = None
    topo_info_desc = None

    def validate_and_load_profile_based_sequence(self, cmd_hnd_list):
        # validate_and_load_profile_based_sequence uses a set of
        # internal rules to check the contents of a command list. It returns
        # True if the sequence is a valid profile-based test methodology.
        # It returns False if any of the rules are violated.
        # When done, the SequenceInfo object is populated with
        # parsed results.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.validate_and_load_profile_based_sequence.SequenceInfo")
        if (None == cmd_hnd_list) or (0 == len(cmd_hnd_list)):
            plLogger.LogError("Invalid or empty command handle list!")
            return False
        hnd_reg = CHandleRegistry.Instance()

        plLogger.LogInfo(" command handles passed in: " + str(cmd_hnd_list))
        # Look for one and only one Topology Test Group
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogError("ERROR: Found invalid handle in command list in the sequencer!")
                continue
            else:
                plLogger.LogInfo(" -> test " + cmd.GetType() + "  " + cmd.Get("Name"))
                if cmd.IsTypeOf(self.TEST_TOPO_GROUP):
                    if self.test_topo_group_cmd is None:
                        self.test_topo_group_cmd = cmd
                    else:
                        plLogger.LogError("Multiple " + self.TEST_TOPO_GROUP +
                                          " commands detected!")
                        return False
        if self.test_topo_group_cmd is None:
            plLogger.LogInfo("Did not find a " + self.TEST_TOPO_GROUP + " command!")
            return False
        plLogger.LogInfo(" test_topo_group: " + self.test_topo_group_cmd.GetType() +
                         "  " + cmd.Get("Name"))

        # If we get here, we have discovered one and only one Test Topology Group
        # Verify that the group contains one and only one Test Group and one and only
        # one Topology Group in it
        cmd_list = self.test_topo_group_cmd.GetCollection("CommandList")
        plLogger.LogInfo(" command handles in the test_topo_group: " + str(cmd_list))
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogError("ERROR: Found invalid handle in command list " +
                                  "in the " + self.TEST_TOPO_GROUP + " command!")
                continue
            else:
                plLogger.LogInfo(" -> test " + cmd.GetType() + "  " + cmd.Get("Name"))
                if cmd.IsTypeOf(self.TOPO_PROFILE_GROUP):
                    if self.topo_group_cmd is None:
                        self.topo_group_cmd = cmd
                    else:
                        plLogger.LogError("Multiple " + self.TOPO_GROUP +
                                          " commands detected!")
                        return False
                elif cmd.IsTypeOf(self.TEST_GROUP):
                    if self.test_group_cmd is None:
                        self.test_group_cmd = cmd
                    else:
                        plLogger.LogError("Multiple " + self.TEST_GROUP +
                                          " commands detected!")
                        return False
        if self.test_group_cmd is None:
            plLogger.LogInfo("Did not find a " + self.TEST_GROUP + " command!")
            return False
        if self.topo_group_cmd is None:
            plLogger.LogInfo("Did not find a " + self.TOPO_GROUP + " command!")
            return False

        plLogger.LogInfo(" topo_group: " + self.topo_group_cmd.GetType() + "  " + cmd.Get("Name"))
        plLogger.LogInfo(" test_group: " + self.test_group_cmd.GetType() + "  " + cmd.Get("Name"))

        # If we get here we have found one and only one Topology Group command
        # The Topology Group should have one or more Network Profile groups in it.
        # It may also optionally contain a Traffic Profile Command.
        self.net_prof_group_cmd_list = []
        cmd_list = self.topo_group_cmd.GetCollection("CommandList")
        plLogger.LogInfo(" command handles in the topo_group: " + str(cmd_list))
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogError("ERROR: Found invalid handle in command list " +
                                  "in the " + self.TOPO_GROUP + " command!")
                continue
            else:
                plLogger.LogInfo(" -> test " + cmd.GetType() + "  " + cmd.Get("Name"))
                if cmd.IsTypeOf(self.NETWORK_PROFILE_GROUP):
                    # There can be more than one, so just append to the list
                    self.net_prof_group_cmd_list.append(cmd)
                elif cmd.IsTypeOf("spirent.trafficcenter.CreateTrafficProfileCommand"):
                    # If we find one TPC, we can only have one. Verify.
                    if self.trf_cmd is None:
                        self.trf_cmd = cmd
                    else:
                        plLogger.LogError("Multiple spirent.trafficcenter." +
                                          "CreateTrafficProfileCommand commands detected!")
                        return False
        if len(self.net_prof_group_cmd_list) < 1:
            plLogger.LogInfo("Did not find any " + self.NET_PROF_GROUP +
                             " commands in the " + self.TOPO_GROUP + " command!")
            return False

        # If we get here, we know that the Network Profile Group command list
        # has at least one entry in it. Each Network Profile Group command
        # should have at least one Network Info command in it
        # and may have optional Protocol and Network Profile commands
        for cmd in self.net_prof_group_cmd_list:
            plLogger.LogInfo(" net_prof_group: " + cmd.GetType() + "  " + cmd.Get("Name"))

        self.net_prof_group_cmd_map = {}
        for net_prof_group in self.net_prof_group_cmd_list:
            cmd_list = net_prof_group.GetCollection("CommandList")
            plLogger.LogInfo(" command handles in the net prof group command: " + str(cmd_list))
            group_key = str(net_prof_group.GetObjectHandle())
            plLogger.LogInfo(" group_key: " + group_key)
            self.net_prof_group_cmd_map[group_key + ",protocol_profile"] = []
            self.net_prof_group_cmd_map[group_key + ",network_info"] = []
            plLogger.LogInfo(" default map for key: " + str(self.net_prof_group_cmd_map))
            for cmd_hnd in cmd_list:
                cmd = hnd_reg.Find(cmd_hnd)
                if cmd is None:
                    plLogger.LogError("ERROR: Found invalid handle in command list " +
                                      "in the " + self.NET_PROFILE_GROUP + " command!")
                    continue
                else:
                    if cmd.IsTypeOf("spirent.methodology.CreateNetworkInfoCommand"):
                        self.net_prof_group_cmd_map[group_key + ",network_info"].append(cmd)
                        plLogger.LogInfo("Found " + cmd.Get("Name"))
                    elif cmd.IsTypeOf(
                            "spirent.methodology.ProtocolProfileGroupCommand"):
                        self.net_prof_group_cmd_map[group_key + ",protocol_profile"].append(cmd)
                        plLogger.LogInfo("Found " + cmd.Get("Name"))
                    elif cmd.IsTypeOf("spirent.methodology.CreateProtocolProfileCommand"):
                        self.net_prof_group_cmd_map[group_key + ",protocol_profile"].append(cmd)
                        plLogger.LogInfo("Found " + cmd.Get("Name"))

        plLogger.LogInfo("net_prof_group_cmd_map after: " + str(self.net_prof_group_cmd_map))

        for net_prof_group in self.net_prof_group_cmd_list:
            group_key = str(net_prof_group.GetObjectHandle())
            if len(self.net_prof_group_cmd_map[group_key + ",network_info"]) == 0:
                plLogger.LogInfo("Did not find any Network Info commands " +
                                 "in the " + self.NET_PROFILE_GROUP + " command!")
                return False

        # If we get here we peer into the Test Group command looking for
        # requirements there. For now, simply look for one and only one
        # iteration group command.
        # FIXME:
        # Need to handle more of these somehow later
        # This includes nested Iteration Groups
        cmd_list = self.test_group_cmd.GetCollection("CommandList")
        # iter_group = None
        plLogger.LogInfo(" command handles in the test_group: " + str(cmd_list))
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogError("ERROR: Found invalid handle in command list " +
                                  " in the " + TEST_GROUP + " command!")
                continue
            else:
                plLogger.LogInfo(" command with handle " + str(cmd_hnd) + " is "
                                 + cmd.Get("Name") + " type: " + cmd.GetType())
                if cmd.IsTypeOf(self.ITER_GROUP):
                    if self.iter_group_cmd is None:
                        self.iter_group_cmd = cmd
                    else:
                        plLogger.LogError("Multiple " + self.ITER_GROUP + " commands found!")
                        return False
        if self.iter_group_cmd is None:
            plLogger.LogInfo(" No iterate group command found")

        plLogger.LogDebug("end.validate_and_load_profile_based_sequence.SequenceInfo")
        return True


# FIXME: As this class relies on the profile-based model of methodology, it
#        will be deprecated with the profile-based model
class ProtocolProfileGroupCommandUtils(object):
    @staticmethod
    def validate_contained_cmds(proto_prof_group_cmd, allowRoutes=True, allowTopology=True):
        # Check the contents of the group.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.validate_contained_cmds.ProtocolProfileGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        cmd_list = proto_prof_group_cmd.GetCollection("CommandList")
        pkg = "spirent.methodology"
        Topologies = 0
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                                 " as unable to find in handle registry")
                continue

            p_type = CMeta.GetClassMeta(proto_prof_group_cmd)['name']

            if cmd.IsTypeOf(pkg + ".AddRoutesCommand"):
                if (allowRoutes is False):
                    return "ERROR: Unsupported AddRoutesCommand command under " + p_type + "."
            elif cmd.IsTypeOf(pkg + ".routing.AddBaseRoutingTopologyGroupCommand"):
                if (allowTopology is False):
                    return "ERROR: Unsupported AddBaseRoutingTopologyGroupCommand command " + \
                           "under " + p_type + "."
                else:
                    Topologies = Topologies + 1
                    if Topologies > 1:
                        p_type = CMeta.GetClassMeta(proto_prof_group_cmd)['name']
                        return "ERROR: Multiple topology commands under " + p_type + "."
            else:
                return "ERROR: Commands in the " + p_type + " must be of type " + \
                    pkg + ".AddRoutesCommand or " + \
                    pkg + ".routing.AddBaseRoutingTopologyGroupCommand."

        plLogger.LogDebug("end.validate_contained_cmds.ProtocolProfileGroupCommandUtils")
        return ""

    @staticmethod
    def config_contained_cmds(proto_prof_group_cmd, net_prof):
        # Configures the ProtocolProfileGroupCommand's contained
        # commands to pass the NetworkProfile handle
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.config_contained_cmds.ProtocolProfileGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        pkg = "spirent.methodology"
        plLogger.LogInfo("net_prof: " + str(net_prof))

        if net_prof is None:
            plLogger.LogError("ERROR: Invalid NetworkProfile object")
            return
        if proto_prof_group_cmd is None:
            plLogger.LogWarn("WARNING: Invalid " + pkg + ".ProtocolProfileGroupCommand object.")
            return

        cmd_hnd_list = proto_prof_group_cmd.GetCollection("CommandList")
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                                 " as unable to find in handle registry")
                continue
            if cmd.IsTypeOf(pkg + ".AddRoutesCommand") or \
               cmd.IsTypeOf(pkg + ".routing.AddBaseRoutingTopologyGroupCommand"):
                cmd.Set("NetworkProfile", net_prof.GetObjectHandle())
            else:
                # Skip the unhandled command
                # This needs to be updated when new types of commands are added
                # to create stuff in the NetworkProfile's NetworkInfo
                plLogger.LogInfo("Skipping direct configuration of a NetworkProfile " +
                                 "handle in " + cmd.Get("Name") + " input list. " +
                                 "Update sequencer_utils.ProtocolProfileGroupCommandUtils" +
                                 " if a handle needs to be propagated.")
                continue
            plLogger.LogInfo("Configure input NetworkProfile for: " + cmd.GetType() + " " +
                             str(cmd.GetObjectHandle()))
        plLogger.LogDebug("end.config_contained_cmds.ProtocolProfileGroupCommandUtils")
        return


# FIXME: As this class relies on the profile-based model of methodology, it
#        will be deprecated with the profile-based model
class ProfileGroupCommandUtils(object):
    @staticmethod
    def config_contained_cmds(group_cmd, obj_type, param_name, param_ref):
        # Configures an input parameter with a parameter ref (output) for
        # any number of a given object type in the command list.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.config_contained_cmds.ProfileGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        pkg = "spirent.methodology."

        if param_ref is None:
            plLogger.LogError("ERROR: Invalid parameter reference")
            return
        if param_name is None or param_name == "":
            plLogger.LogError("ERROR: Invalid parameter name")
            return
        if obj_type is None:
            plLogger.LogError("ERROR: Invalid object type")
            return
        if group_cmd is None:
            plLogger.LogError("ERROR: Invalid group command")
            return

        cmd_hnd_list = group_cmd.GetCollection("CommandList")
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                                 " as unable to find in handle registry")
                continue
            if cmd.IsTypeOf(pkg + obj_type) or cmd.IsTypeOf(pkg + "routing." + obj_type):
                plLogger.LogInfo("Configuring " + obj_type + "." + param_name)
                cmd.Set(param_name, param_ref)
                continue
        plLogger.LogDebug("end.config_contained_cmds.ProfileGroupCommandUtils")
        return


# FIXME: As this class relies on the profile-based model of methodology, it
#        will be deprecated with the profile-based model
class NetworkProfileGroupCommandUtils(object):
    @classmethod
    def validate_contained_interfaces(self, cmd_list):
        # Check the NetworkInfo commands in the group.
        # Contained NetworkInfoCommands should be in right order.
        # This function is designed to be called from the STAK Command's
        # validate function and will return the string error description if
        # there is an error.  It will return an empty string if there is no
        # error.

        ETH_CMD = "CreateEthernetNetworkInfoCommand"
        VLAN_CMD = "CreateVlanNetworkInfoCommand"
        IPV4_CMD = "CreateIpv4NetworkInfoCommand"
        IPV6_CMD = "CreateIpv6NetworkInfoCommand"
        DUAL_CMD = "CreateDualStackNetworkInfoCommand"

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.validate_contained_interfaces.NetworkProfileGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        pkg = "spirent.methodology."

        stackIndex = {ETH_CMD: 1, VLAN_CMD: 2, IPV4_CMD: 3, IPV6_CMD: 4, DUAL_CMD: 5}
        curIdx = 0
        prvIdx = 0
        stackTracker = []

        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                continue

            fullName = CMeta.GetClassMeta(cmd)['name'].split('.')
            cmdName = fullName[-1]
            plLogger.LogInfo("cmd : " + cmdName)

            if cmd.IsTypeOf(pkg + "CreateNetworkInfoCommand"):
                if not cmd.IsTypeOf(pkg + ETH_CMD) and \
                   not cmd.IsTypeOf(pkg + VLAN_CMD) and \
                   not cmd.IsTypeOf(pkg + IPV4_CMD) and \
                   not cmd.IsTypeOf(pkg + IPV6_CMD) and \
                   not cmd.IsTypeOf(pkg + DUAL_CMD):

                    return "ERROR: " + pkg + "CreateNetworkInfoCommand must be of type " + \
                        pkg + ETH_CMD + " or " + \
                        pkg + VLAN_CMD + " or " + \
                        pkg + IPV4_CMD + " or " + \
                        pkg + IPV6_CMD + " or " + \
                        pkg + DUAL_CMD + "."

                # check if stack is in proper order
                curIdx = stackIndex[cmdName]
                plLogger.LogInfo("stackIndex cur/prv : " + str(curIdx) + ", " + str(prvIdx))
                if curIdx < prvIdx:
                    return "ERROR: " + pkg + "CreateNetworkInfoCommand not in correct order."
                else:
                    # only allow following -- Ipv4, Ipv6, DualStack
                    if curIdx is not stackIndex[VLAN_CMD] and curIdx in stackTracker:
                        return "ERROR: " + pkg + cmdName + " is inserted in more than once."
                    elif cmdName == DUAL_CMD and \
                        (stackIndex[IPV4_CMD] in stackTracker or
                            stackIndex[IPV6_CMD] in stackTracker):
                        return "ERROR: adding " + pkg + DUAL_CMD + \
                            " on top of Ipv4 or Ipv6 interface."
                    elif cmdName == IPV6_CMD and stackIndex[IPV4_CMD] in stackTracker:
                        return "ERROR: adding " + pkg + IPV6_CMD + " on top of Ipv4 interface."
                    else:
                        stackTracker.append(curIdx)
                        prvIdx = curIdx

        plLogger.LogDebug("end.validate_contained_interfaces.NetworkProfileGroupCommandUtils")
        return ""

    @staticmethod
    def validate_port_exists(port_list, port_group_hnd):
        # Checks to see that between the port_list and the port_group_tag,
        # an actual port exists somewhere.
        # This function is designed to be called from the STAK Command's
        # validate function and will return the string error description if
        # there is an error.  It will return an empty string if there is no
        # error.
        hnd_reg = CHandleRegistry.Instance()
        port_group_tag = None
        if port_group_hnd != "":
            port_group_tag = hnd_reg.Find(port_group_hnd)
        if len(port_list) == 0:
            if port_group_tag is None:
                return "ERROR: Ports should be specified by selecting ports " + \
                    "in the PortList or selecting a PortGroupTag representing " + \
                    "a set of ports."
            else:
                tagged_port_list = port_group_tag.GetObjects("Port",
                                                             RelationType("UserTag", 1))
                if len(tagged_port_list) < 1:
                    return "ERROR: PortGroupTag " + port_group_tag.Get("Name") + \
                        " has no tagged ports.  Tag some ports with this tag."
        return ""

    @staticmethod
    def get_ports(port_list, tag_hnd_list):
        # Returns port objects specified in the port group or the port list
        # (but not both).  The port group takes precedence over the port list.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.get_ports.NetworkProfileGroupCommandUtils")

        # Note that the invalid STC handle is 0
        if tag_hnd_list is not None and len(tag_hnd_list) > 0:
            tag_list = CCommandEx.ProcessInputHandleVec("Tag", tag_hnd_list)
            if len(tag_list) < 1:
                # Use port_list
                return CCommandEx.ProcessInputHandleVec("Port", port_list)

            if len(tag_list) > 1:
                plLogger.LogWarn("WARNING: Multiple tags in the specified " +
                                 "port_group_hnd.  Only the first tag " +
                                 tag_list[0].Get("Name") +
                                 " will be used.")
            tag = tag_list[0]
            return tag.GetObjects("Port", RelationType("UserTag", 1))

        # Process the port_list
        plLogger.LogDebug("end.get_ports.NetworkProfileGroupCommandUtils")
        return CCommandEx.ProcessInputHandleVec("Port", port_list)

    @staticmethod
    def validate_contained_cmds(net_prof_group_cmd):
        # Check the contents of the group.  Should only contain
        # commands that inherit from CreateNetworkInfoCommand,
        # ProtocolProfileGroupCommand, and CreateProtocolProfileCommand.
        # If more command types are necessary, add them here.
        # This function is designed to be called from the STAK Command's
        # validate function and will return the string error description if
        # there is an error.  It will return an empty string if there is no
        # error.  If needed to be used for generic validation, True == "",
        # False == "some string"

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.validate_contained_cmds.NetworkProfileGroupCommandUtils")

        pkg = "spirent.methodology"
        foundCreateNetworkInfoCommand = False
        isXNetworkProfileGroupCmd = False
        if net_prof_group_cmd.IsTypeOf(pkg + ".Ipv4NetworkProfileGroupCommand") or \
           net_prof_group_cmd.IsTypeOf(pkg + ".Ipv6NetworkProfileGroupCommand") or \
           net_prof_group_cmd.IsTypeOf(pkg + ".DualStackNetworkProfileGroupCommand"):
            isXNetworkProfileGroupCmd = True
        plLogger.LogInfo("isXNetworkProfileGroupCmd: " + str(isXNetworkProfileGroupCmd))

        hnd_reg = CHandleRegistry.Instance()
        cmd_list = net_prof_group_cmd.GetCollection("CommandList")
        proto_set = set()
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                                 " as unable to find in handle registry")
                continue

            c_type = CMeta.GetClassMeta(cmd)['name']
            p_type = CMeta.GetClassMeta(net_prof_group_cmd)['name']
            plLogger.LogInfo("c_type: " + str(c_type) + ",  p_type: " + str(p_type))

            if not cmd.IsTypeOf(pkg + ".CreateNetworkInfoCommand") and \
               not cmd.IsTypeOf(pkg + ".ProtocolProfileGroupCommand") and \
               not cmd.IsTypeOf(pkg + ".CreateProtocolProfileCommand"):
                return "ERROR: Commands in the " + \
                    p_type + " must be of type " + \
                    pkg + ".CreateNetworkInfoCommand, " + \
                    pkg + ".ProtocolProfileGroupCommand or " + \
                    pkg + ".CreateProtocolProfileCommand."
            if cmd.IsTypeOf(pkg + ".CreateProtocolProfileCommand") or \
               cmd.IsTypeOf(pkg + ".ProtocolProfileGroupCommand"):
                if cmd.GetType() not in proto_set:
                    proto_set.add(cmd.GetType())
                else:
                    return "ERROR: Duplicate command of type " + \
                        c_type + " added within " + p_type
            if cmd.IsTypeOf(pkg + ".CreateProtocolProfileCommand") and \
               foundCreateNetworkInfoCommand is False and \
               isXNetworkProfileGroupCmd is False:
                return "ERROR: CreateNetworkInfoCommand must precede " + \
                    "CreateProtocolProfileCommand."
            if cmd.IsTypeOf(pkg + ".CreateNetworkInfoCommand"):
                foundCreateNetworkInfoCommand = True
                if isXNetworkProfileGroupCmd is True:
                    return "ERROR: " + c_type + " added within " + p_type

        plLogger.LogDebug("end.validate_contained_cmds.NetworkProfileGroupCommandUtils")
        return NetworkProfileGroupCommandUtils.validate_contained_interfaces(cmd_list)

    @staticmethod
    def config_contained_cmds(net_prof_group_cmd, net_prof):
        # Configures the NetworkProfileGroupCommand's (or derived command's) contained
        # commands to pass the NetworkProfile handle
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.config_contained_cmds.NetworkProfileGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        pkg = "spirent.methodology"

        plLogger.LogInfo("net_prof: " + str(net_prof))

        if net_prof is None:
            plLogger.LogError("ERROR: Invalid NetworkProfile object")
            return
        if net_prof_group_cmd is None:
            plLogger.LogWarn("WARNING: Invalid " + pkg + ".NetworkProfileGroupCommand " +
                             "object.  Nothing will be configured.")
            return

        cmd_hnd_list = net_prof_group_cmd.GetCollection("CommandList")
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                                 " as unable to find in handle registry")
                continue
            if cmd.IsTypeOf(pkg + ".CreateNetworkInfoCommand") or \
               cmd.IsTypeOf(pkg + ".ProtocolProfileGroupCommand") or \
               cmd.IsTypeOf(pkg + ".CreateProtocolProfileCommand"):
                cmd.Set("NetworkProfile", net_prof.GetObjectHandle())
            else:
                # Skip the unhandled command
                # This needs to be updated when new types of commands are added
                # to create stuff in the NetworkProfile's NetworkInfo
                plLogger.LogInfo("Skipping direct configuration of a NetworkProfile handle in " +
                                 cmd.Get("Name") + " input list.  Update " +
                                 "sequencer_utils.config_net_prof_group_cmd_children " +
                                 "if a handle needs to be propagated.")
                continue
            plLogger.LogInfo("Configure input NetworkProfile for: " + cmd.GetType() + " " +
                             str(cmd.GetObjectHandle()))

        plLogger.LogDebug("end.config_contained_cmds.NetworkProfileGroupCommandUtils")
        return


# FIXME: As this class relies on the profile-based model of methodology, it
#        will be deprecated with the profile-based model
class TopologyTestGroupCommandUtils(object):
    @staticmethod
    def get_topo_group_cmd(topo_test_group_cmd):
        # Returns the command of type TopologyProfileGroupCommand
        # or None if not found

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.get_topo_group_cmd.TopologyTestGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        if topo_test_group_cmd is None:
            return None
        pkg = "spirent.methodology"
        if not topo_test_group_cmd.IsTypeOf(pkg + ".TopologyTestGroupCommand"):
            plLogger.LogWarn("WARNING: " + topo_test_group_cmd + " is not type " +
                             "of TopologyTestGroupCommand")
            return None
        cmd_hnd_list = topo_test_group_cmd.GetCollection("CommandList")
        topo_cmd = None
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            plLogger.LogInfo(" cmd is " + cmd.GetType())
            if cmd is None:
                plLogger.LogWarn("WARNING: Invalid command found.  Skipping it.")
                continue
            if cmd.IsTypeOf(pkg + ".TopologyProfileGroupCommand"):
                topo_cmd = cmd
                break
        plLogger.LogDebug("end.get_topo_group_cmd.TopologyTestGroupCommandUtils")
        return topo_cmd

    @staticmethod
    def get_test_group_cmd(topo_test_group_cmd):
        # Returns the command of type TestGroupCommand or None if not found

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.get_test_group_cmd.TopologyTestGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        if topo_test_group_cmd is None:
            return None
        pkg = "spirent.methodology"
        if not topo_test_group_cmd.IsTypeOf(pkg + ".TopologyTestGroupCommand"):
            plLogger.LogWarn("WARNING: " + topo_test_group_cmd + " is not type " +
                             "of TopologyTestGroupCommand")
            return None
        cmd_hnd_list = topo_test_group_cmd.GetCollection("CommandList")
        test_cmd = None
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Invalid command found.  Skipping it.")
                continue
            if cmd.IsTypeOf(pkg + ".TestGroupCommand"):
                test_cmd = cmd
                break
        plLogger.LogDebug("end.get_test_group_cmd.TopologyTestGroupCommandUtils")
        return test_cmd

    @staticmethod
    def validate_contained_cmds(topo_test_group_cmd):
        # This function is designed to be called from the STAK Command's
        # validate function and will return the string error description if
        # there is an error.  It will return an empty string if there is no
        # error.

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.validate_contained_cmds.TopologyTestGroupCommandUtils")
        pkg = "spirent.methodology"
        if topo_test_group_cmd is None:
            return "ERROR: Could not find a command of type " + pkg + \
                ".TopologyTestGroupCommand."
        if not topo_test_group_cmd.IsTypeOf(pkg + ".TopologyTestGroupCommand"):
            return "ERROR: Could not find a command of type " + \
                pkg + ".TopologyTestGroupCommand."

        topo_group_cmd = TopologyTestGroupCommandUtils.get_topo_group_cmd(topo_test_group_cmd)
        test_group_cmd = TopologyTestGroupCommandUtils.get_test_group_cmd(topo_test_group_cmd)
        if topo_group_cmd is None:
            return "ERROR: Expected a " + pkg + ".TopologyProfileGroupCommand in the " + \
                pkg + ".TopologyTestGroupCommand.  Could not find one."
        if test_group_cmd is None:
            return "ERROR: Expected a " + pkg + ".TestGroupCommand in the " + \
                pkg + ".TopologyTestGroupCommand.  Could not find one."
        plLogger.LogDebug("end.validate_contained_cmds.TopologyTestGroupCommandUtils")
        return ""

    @staticmethod
    def build_property_chains(topo_cmd, test_cmd):
        # Builds the property chain to pass the TopologyProfile object from the
        # TopologyProfileGroupCommand to the TestGroupCommand

        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.build_property_chains.TopologyTestGroupCommandUtils")
        if (topo_cmd is None) or (test_cmd is None):
            plLogger.LogError("ERROR: Input topo_cmd " + topo_cmd + " or test_cmd " +
                              test_cmd + " was None")
            return
        ctor = CScriptableCreator()
        pkg = "spirent.methodology"

        # Build the property chain to pass TopologyProfile
        chain_cmd = ctor.CreateCommand("AddPropertyChaining")
        chain_cmd.SetCollection("SourcePropertyIdList",
                                [pkg + ".TopologyProfileGroupCommand.TopologyProfile"])
        chain_cmd.SetCollection("SourceCommandList", [topo_cmd.GetObjectHandle()])
        chain_cmd.SetCollection("TargetPropertyIdList",
                                [pkg + ".TestGroupCommand.TopologyProfile"])
        chain_cmd.SetCollection("TargetCommandList", [test_cmd.GetObjectHandle()])
        chain_cmd.Execute()
        chain_cmd.MarkDelete()
        plLogger.LogDebug("end.build_property_chains.TopologyTestGroupCommandUtils")
        return


class MethodologyGroupCommandUtils(object):
    @staticmethod
    def set_sequenceable_properties(cmd_hnd_list, enable):
        # This function is not recursive and it simply turns the
        # cmd_hnd_list into a list of command objects.
        # The reason we need it at all is because it is usually easier
        # to think in terms of a command's (or sequencer's)
        # CommandList rather than the command children.  However, it
        # is easier to recurse on the command objects rather than
        # handles due to the fact that the recursion will be done using
        # the parent-child relationship rather than the CommandList
        # property.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.set_sequenceable_properties.MethodologyGroupCommandUtils")
        hnd_reg = CHandleRegistry.Instance()
        cmd_list = []
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("Skipping command with invalid handle")
                continue
            cmd_list.append(cmd)

        # Call the recursive function
        MethodologyGroupCommandUtils.set_sequenceable_properties_recursive(
            cmd_list, enable)
        plLogger.LogDebug("end.set_sequenceable_properties.MethodologyGroupCommandUtils")

    @staticmethod
    def set_sequenceable_properties_recursive(cmd_list, enable):
        mm_pkg = "spirent.methodology.manager"
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.set_sequenceable_properties_recursive.\
                            MethodologyGroupCommandUtils")

        for cmd in cmd_list:
            if cmd is None:
                continue

            plLogger.LogInfo("cmd: " + cmd.GetType())

            # Maybe it's better to do this using a command's children
            # It gets tricky using CommandList as some child commands may not
            # be in a group command's CommandList.  For example,
            # the SequencerWhileCommand's
            # ExpressionCommand is a child of the SequencerWhileCommand but
            # it is NOT contained in the CommandList
            #
            # if cmd.IsTypeOf("SequencerGroupCommand") or \
            #    cmd.IsTypeOf("stak.StakGroupCommand"):
            #     # Recurse into the SequencerGroupCommand's CommandList
            #     set_sequenceable_properties_recursive(
            #         cmd.GetCollection("CommandList"), enable)
            children = cmd.GetObjects("Command")
            if len(children) > 0:
                MethodologyGroupCommandUtils.set_sequenceable_properties_recursive(
                    children, enable)

            # Except for the MethodologyGroupCommand, all other commands should have
            # their SequenceableProperties set to the value of the enable parameter.
            if not cmd.IsTypeOf(mm_pkg + ".MethodologyGroupCommand"):
                plLogger.LogInfo(" -> call bind_seq_props with: " + str(enable))
                MethodologyGroupCommandUtils.bind_sequenceable_properties(cmd, enable)
        plLogger.LogDebug("end.set_sequenceable_properties_recursive.MethodologyGroupCommandUtils")
        return

    @staticmethod
    def bind_sequenceable_properties(cmd, enable):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.bind_sequenceable_properties.MethodologyGroupCommandUtils")
        ctor = CScriptableCreator()
        stc_sys = CStcSystem.Instance()
        sequencer = stc_sys.GetObject("Sequencer")
        if cmd is None:
            plLogger.LogWarn("WARNING: bind_sequenceable_properties called for" +
                             " null cmd.")
            return
        sp = cmd.GetObject("SequenceableCommandProperties",
                           RelationType("SequenceableProperties"))
        if sp is None:
            plLogger.LogInfo(" sp is null...create a new one on: " + cmd.GetType())

            # Create a new one
            sp = ctor.Create("SequenceableCommandProperties", sequencer)
            cmd.AddObject(sp, RelationType("SequenceableProperties"))
            plLogger.LogInfo(" created a new sp...")
            temp = cmd.GetObject("SequenceableCommandProperties",
                                 RelationType("SequenceableProperties"))
            if temp is not None:
                plLogger.LogInfo("temp: " + temp.Get("Name"))
            else:
                temp = cmd.GetObject("SequenceableCommandProperties",
                                     RelationType("SequenceableProperties", 1))
                plLogger.LogInfo("temp (rev): " + temp.Get("Name"))

        plLogger.LogInfo("sp: " + sp.Get("Name"))
        sp.Set("AllowDelete", enable)
        sp.Set("AllowMove", enable)
        sp.Set("AllowUngroup", enable)
        sp.Set("AllowDisable", enable)
        sp.Set("ShowEditor", enable)
        plLogger.LogDebug("end.bind_sequenceable_properties.MethodologyGroupCommandUtils")

    @staticmethod
    def insert_top_level_group_command():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.insert_top_level_group_command.MethodologyGroupCommandUtils")
        ctor = CScriptableCreator()
        mm_pkg = "spirent.methodology.manager"
        stc_sys = CStcSystem.Instance()
        sequencer = stc_sys.GetObject("Sequencer")
        hnd_reg = CHandleRegistry.Instance()
        cmd_hnd_list = sequencer.GetCollection("CommandList")

        # Create the group command
        tlgc = ctor.Create(mm_pkg + ".MethodologyGroupCommand", sequencer)
        sequencer.SetCollection("CommandList", [tlgc.GetObjectHandle()])
        tlgc.SetCollection("CommandList", cmd_hnd_list)

        # Change the parent to the MethodologyGroupCommand
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.Warn("Skipping invalid command")
            cmd.AddObject(tlgc, RelationType("ParentChild", 1))
        plLogger.LogDebug("end.insert_top_level_group_command.MethodologyGroupCommandUtils")
        return

    @staticmethod
    def remove_top_level_group_command():
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.remove_top_level_group_command.MethodologyGroupCommandUtils")
        stc_sys = CStcSystem.Instance()
        sequencer = stc_sys.GetObject("sequencer")
        hnd_reg = CHandleRegistry.Instance()
        ctor = CScriptableCreator()
        mm_pkg = "spirent.methodology.manager"
        cmd_hnd_list = sequencer.GetCollection("CommandList")

        tlgc = MethodologyGroupCommandUtils.find_top_level_group_command()
        if tlgc is None:
            plLogger.LogWarn("WARNING: Could not find the " + mm_pkg +
                             ".MethodologyGroupCommand.  Did not remove anything.")
            return
        cmd_hnd_list = tlgc.GetCollection("CommandList")
        tlgc.SetCollection("CommandList", [])
        insert_cmd = ctor.CreateCommand("SequencerInsertCommand")
        insert_cmd.SetCollection("CommandList", cmd_hnd_list)
        insert_cmd.Set("InsertAfter", tlgc.GetObjectHandle())
        insert_cmd.Execute()

        remove_cmd = ctor.CreateCommand("SequencerRemoveCommand")
        remove_cmd.SetCollection("CommandList", [tlgc.GetObjectHandle()])
        remove_cmd.Execute()
        remove_cmd.MarkDelete()

        # Change the parent to the Sequencer
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.Warn("Skipping invalid command")
            cmd.AddObject(sequencer, RelationType("ParentChild", 1))
        plLogger.LogDebug("end.remove_top_level_group_command.MethodologyGroupCommandUtils")
        return

    @staticmethod
    def find_top_level_group_command():
        # FIXME (eventually):
        # For now, assume that the MethodologyGroupCommand is at the top
        # level (direct child) of the sequencer.  The user could have
        # inserted more commands above and below this group.
        # If the user puts the MethodologyGroupCommand into a group, we
        # may need to look recursively into the sequence.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.find_top_level_group_command.MethodologyGroupCommandUtils")
        stc_sys = CStcSystem.Instance()
        sequencer = stc_sys.GetObject("sequencer")
        hnd_reg = CHandleRegistry.Instance()
        cmd_hnd_list = sequencer.GetCollection("CommandList")
        mm_pkg = "spirent.methodology.manager"
        for cmd_hnd in cmd_hnd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                plLogger.LogWarn("WARNING: Skipping invalid command handle.")
                continue
            if cmd.IsTypeOf(mm_pkg + ".MethodologyGroupCommand"):
                return cmd
        plLogger.LogDebug("end.find_top_level_group_command.MethodologyGroupCommandUtils")
        return None
