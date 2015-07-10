from StcIntPythonPL import *
import time
import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom
import collections
from methodologymanagerConst import MethodologyManagerConst as mmc


class MetaManager(object):

    MM_NAME = "name"
    MM_ID = "id"
    MM_ATTR = "attribute"
    MM_VALUE = "value"
    MM_COMMAND_NAME = "command"
    MM_DEFAULT = "defaultValue"
    MM_DESC = "description"
    MM_TYPE = "type"

    MM_TEST = "test"

    TEST_INFO = "testInfo"
    TI_DISPLAY_NAME = "displayName"
    TI_KEY = "methodologyKey"
    TI_DESCRIPTION = MM_DESC
    TI_TEST_CASE_NAME = "testCaseName"
    TI_TEST_CASE_DESCRIPTION = "testCaseDescription"
    TI_TEST_CASE_KEY = "testCaseKey"
    TI_VERSION = "version"
    TI_LABELS = "labels"
    TI_LABEL = "label"
    TI_FEATURES = "features"
    TI_FEATURE = "feature"
    TI_ID = MM_ID
    TEST_INSTANCE_ORIGINAL = "original"

    TEST_RESOURCES = "testResources"
    TR_RESOURCE_GROUPS = "resourceGroups"
    TR_RESOURCE_GROUP = "resourceGroup"
    TR_PORT_GROUPS = "portGroups"
    TR_PORT_GROUP = "portGroup"
    TR_PORTS = "ports"
    TR_PORT = "port"
    TR_NAME = MM_NAME
    TR_DISPLAY_NAME = "displayName"
    TR_ID = MM_ID
    TR_LOCATION = "location"
    TR_ATTR = MM_ATTR
    TR_VALUE = MM_VALUE
    TR_MINPORTS = "minNumPorts"
    TR_MAXPORTS = "maxNumPorts"
    TR_PSPEEDLIST = "portSpeedList"

    W_WIZARD = "wizard"
    W_PAGE = "page"
    W_GROUP = "group"
    W_DATA = "data"
    W_PROPERTY = "property"
    W_GUI_ONLY = "ignoreOnBackEnd"
    W_ID = "id"
    W_VALUE = "value"

    P_PROC_FUNCS = "processingFunctions"
    P_PROC_FUNC = "processingFunction"
    P_PROC_DICT = "processingDictionary"
    P_ID = "id"
    P_SCRIPT_FILE = "scriptFile"
    P_ENTRY_FUNC = "entryFunction"
    P_INPUT_DICT = "inputDict"
    P_INPUT = "input"
    P_OUTPUT = "output"
    P_SRC_ID = "srcId"
    P_SCRIPT_VAR_NAME = "scriptVarName"
    P_EP_KEY = "epKey"
    P_DEFAULT = "default"

    EDITABLE_PARAMS = "editableParams"
    EP_PARAM_GROUPS = "paramGroups"
    EP_PARAM_GROUP = "paramGroup"
    EP_PARAMS = "params"
    EP_PARAM = "param"
    EP_EXPOSED = "exposedProperties"
    EP_TAGGED = "taggedProperties"
    EP_NAME = MM_NAME
    EP_ID = MM_ID
    EP_TAG = "tag"
    EP_ATTR = MM_ATTR
    EP_VALUE = MM_VALUE
    EP_PROP_ID = "stcPropertyId"
    EP_DEFAULT = MM_DEFAULT
    EP_TYPE = "type"
    EP_UNITS = "units"
    EP_MIN_INCL = "minInclusive"
    EP_MAX_INCL = "maxInclusive"
    EP_MIN_OCCURS = "minOccurences"
    EP_MAX_OCCURS = "maxOccurences"

    TRAFFIC_INFO = "trafficInfo"
    TRF_NAME = MM_NAME
    TRF_VALUE = MM_VALUE
    TRF_ID = MM_ID
    TRF_DESCRIPTION = MM_DESC
    TRF_TRAFFIC = "traffic"
    TRF_APP_INFO = "appinfo"
    TRF_ATTR = MM_ATTR
    TRF_END_POINTS = "endpoints"
    TRF_UP_LINK_END_POINT = "uplinkEndpoint"
    TRF_DOWN_LINK_END_POINT = "downlinkEndpoint"
    TRF_COMMAND_NAME = "CommandName"
    TRF_PACKAGE_NAME = "PackageName"
    # hardcode trafficInfo name and trafficInfo description here, eventually
    # user inputs will be passed in for them
    TRF_INFO_NAME = "Test Traffic"
    TRF_INFO_DESCP = "Optional Description"

    META_FILE_NAME = mmc.MM_META_FILE_NAME

    # Profile-Based Info
    TOPOLOGY_INFO = "topologyInfo"
    TPI_NET_PROFILE = "networkProfile"
    TPI_NAME = MM_NAME
    TPI_VALUE = MM_VALUE
    TPI_ID = MM_ID
    TPI_DESC = MM_DESC
    TPI_ATTR = MM_ATTR
    TPI_INTERFACE = "interface"
    TPI_PROTOCOL = "protocol"
    TPI_TYPE = MM_TYPE
    TPI_PORT_GROUP_ID = "portGroupId"
    TPI_PORT_GROUP_TAG = "portGroupTag"
    TPI_DEVICE_COUNT = "deviceCount"
    TPI_INTERFACE = "interface"

    INTERFACE = "interface"
    PROTOCOL = "protocol"

    @staticmethod
    def adjust_type(type_val):
        int_list = ["u8", "u16", "u32", "u64", "s8", "s16", "s32", "s64"]
        if type_val in int_list:
            return "integer"
        else:
            return type_val

    @staticmethod
    def sort_exposed_properties(exposed_properties):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.sort_exposed_properties.MetaManager")
        plLogger.LogDebug("exposed_properties: " + str(exposed_properties))
        # OrderedDict preserves insertion order
        sorted_exp_props = collections.OrderedDict()
        for ep in exposed_properties:
            # Skip the non-commands
            target_obj = ep.GetObject(
                "Scriptable", RelationType("ScriptableExposedProperty"))
            if target_obj is None:
                plLogger.LogDebug("Skipping because no target_obj")
                continue
            if target_obj.IsTypeOf("Command") is False:
                plLogger.LogDebug("Skipping non-command")
                continue
            if target_obj.GetObjectHandle() not in sorted_exp_props.keys():
                plLogger.LogDebug("Initializing sorted_exp_props" +
                                  str(target_obj.GetObjectHandle()) + "]")
                sorted_exp_props[target_obj.GetObjectHandle()] = []
                # sorted_exp_props[ep.Get("EPClassHandle")] = []
            sorted_exp_props[target_obj.GetObjectHandle()].append(ep)
        plLogger.LogDebug("sorted_exp_props: " + str(sorted_exp_props))
        plLogger.LogDebug("end.sort_exposed_properties.MetaManager")
        return sorted_exp_props

    @staticmethod
    def generate_txml_file(exp_props,
                           meth_name,
                           meth_descript,
                           meth_key,
                           port_tag_list,
                           label_list,
                           feature_id_list,
                           seq_info,
                           minNumPorts,
                           maxNumPorts,
                           portSpeedList,
                           taggedParams,
                           pathAndFileName,
                           sequencer_file_path,
                           tc_name="original",
                           tc_key="",
                           tc_descript=""):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_txml_file.MetaManager")
        meta = ET.Element(MetaManager.MM_TEST)
        MetaManager.generate_test_info(meta,
                                       meth_name, meth_descript, meth_key,
                                       tc_name, tc_descript, tc_key,
                                       label_list, feature_id_list)
        MetaManager.generate_test_resources(port_tag_list,
                                            minNumPorts,
                                            maxNumPorts,
                                            portSpeedList,
                                            meta)
        MetaManager.generate_editable_params(exp_props, taggedParams, meta)

        # FIXME:
        # Remove this
        MetaManager.generate_topology_info(meta)
        # hardcode trafficInfo name and trafficInfo description here, eventually
        # user inputs will be passed in for them
        MetaManager.generate_traffic_info(seq_info, MetaManager.TRF_INFO_NAME,
                                          MetaManager.TRF_INFO_DESCP, meta)

        tree = ET.ElementTree(meta)
        if not tree:
            plLogger.LogError("Error converting meta to tree")
        tree.write(pathAndFileName)

        plLogger.LogError("Writing to file " + pathAndFileName)

        # make pretty print
        xml_obj = xml.dom.minidom.parse(pathAndFileName)
        xml_str = xml_obj.toprettyxml()

        f = open(pathAndFileName, "w")
        f.write(xml_str)
        f.close()

        plLogger.LogError("Wrote to file " + pathAndFileName)
        plLogger.LogDebug("end.generate_txml_file.MetaManager")
        return True

    @staticmethod
    def generate_test_info(root,
                           meth_name, meth_descript, meth_key,
                           tc_name, tc_descript, tc_key,
                           label_list, feature_id_list, version="1.0"):
        # Populate the testInfo section of the TXML string
        # This includes the labels subelement.
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_test_info.MetaManager")
        if root is None:
            plLogger.LogError("Invalid root")
            return
        if meth_name is None:
            plLogger.LogError("Invalid meth_name")
            return
        if label_list is None:
            plLogger.LogError("Invalid label_list")
            return
        test_info = ET.SubElement(root, MetaManager.TEST_INFO)
        test_info.set(MetaManager.TI_DISPLAY_NAME, meth_name)
        test_info.set(MetaManager.TI_DESCRIPTION, meth_descript)
        test_info.set(MetaManager.TI_KEY, meth_key)
        test_info.set(MetaManager.TI_TEST_CASE_NAME, tc_name)
        test_info.set(MetaManager.TI_TEST_CASE_DESCRIPTION, tc_descript)
        test_info.set(MetaManager.TI_TEST_CASE_KEY, tc_key)
        test_info.set(MetaManager.TI_VERSION, version)
        labels = ET.SubElement(test_info, MetaManager.TI_LABELS)
        for string_label in label_list:
            label = ET.SubElement(labels, MetaManager.TI_LABEL)
            label.text = str(string_label)
        features = ET.SubElement(test_info, MetaManager.TI_FEATURES)
        for feature_id in feature_id_list:
            feature = ET.SubElement(features, MetaManager.TI_FEATURE)
            feature.set(MetaManager.TI_ID, str(feature_id))
        plLogger.LogDebug("end.generate_test_info.MetaManager")

    @staticmethod
    def generate_test_resources(port_tag_list,
                                minNumPorts,
                                maxNumPorts,
                                portSpeedList,
                                root):
        # Populate the testResources section of the TXML string
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_test_resources.MetaManager")
        if port_tag_list is None:
            plLogger.LogError("Invalid port_tag_list")
            return
        if root is None:
            plLogger.LogError("Invalid root")
            return

        # Create the testResources tag
        test_res = ET.SubElement(root, MetaManager.TEST_RESOURCES)
        # Create a subtag for resourceGroups
        res_groups = ET.SubElement(test_res, MetaManager.TR_RESOURCE_GROUPS)
        # Create a subtag for a resource group to handle port limits
        port_limits = ET.SubElement(res_groups, MetaManager.TR_RESOURCE_GROUP)
        port_limits.set(MetaManager.TR_NAME, "Port Limits")
        # Within the resourceGroup, create tags for the limit attribs
        min_attr = ET.SubElement(port_limits, MetaManager.TR_ATTR)
        min_attr.set(MetaManager.TR_NAME, MetaManager.TR_MINPORTS)
        min_attr.set(MetaManager.TR_VALUE, str(minNumPorts))

        max_attr = ET.SubElement(port_limits, MetaManager.TR_ATTR)
        max_attr.set(MetaManager.TR_NAME, MetaManager.TR_MAXPORTS)
        max_attr.set(MetaManager.TR_VALUE, str(maxNumPorts))

        speed_list_attr = ET.SubElement(port_limits, MetaManager.TR_ATTR)
        speed_list_attr.set(MetaManager.TR_NAME, MetaManager.TR_PSPEEDLIST)
        speed_list_attr.set(MetaManager.TR_VALUE, str(portSpeedList))
        # Now pop up a level and create a subtag
        # for one resourceGroup to handle chassis information
        res_group = ET.SubElement(res_groups, MetaManager.TR_RESOURCE_GROUP)
        res_group.set(MetaManager.TR_DISPLAY_NAME, "Chassis Info")
        res_group.set(MetaManager.TR_ID, "chassisInfo")
        # Within the resourceGroup, create portGroups
        port_groups = ET.SubElement(res_group, MetaManager.TR_PORT_GROUPS)

        # Use tagged ports (different from the tags provided in
        # the testInfo section, above) to create port groups.
        # Create one port group per tag
        for tag in port_tag_list:
            tagged_ports = tag.GetObjects("Port", RelationType("UserTag", 1))
            if len(tagged_ports) > 0:
                # If there are tagged ports, create the portGroup subtag
                port_group = ET.SubElement(
                    port_groups, MetaManager.TR_PORT_GROUP)
                port_group.set(MetaManager.TR_NAME, tag.Get("Name"))
                port_group.set(
                    MetaManager.TR_ID, get_unique_property_id(tag, "Name"))
                for tagged_port in tagged_ports:
                    # Create a port subtag for each port
                    port = ET.SubElement(port_group, MetaManager.TR_PORT)
                    port.set(
                        MetaManager.TR_NAME, get_unique_property_id(tagged_port, "Location"))
                    loc_attr = ET.SubElement(port, MetaManager.TR_ATTR)
                    loc_attr.set(MetaManager.TR_NAME, MetaManager.TR_LOCATION)
                    loc_attr.set(
                        MetaManager.TR_VALUE, tagged_port.Get("Location"))
        # Process ports that haven't been tagged, if any
        stc_sys = CStcSystem.Instance()
        project = stc_sys.GetObject("Project")
        port_list = project.GetObjects("Port")
        untagged_ports = []
        for port in port_list:
            port_tags = port.GetObjects("Tag", RelationType("UserTag"))
            if len(port_tags) != 0:
                continue
            else:
                untagged_ports.append(port)
        if untagged_ports:
            # We have ports to process, add a port group to hold them
            port_group = ET.SubElement(port_groups, MetaManager.TR_PORT_GROUP)
            port_group.set(MetaManager.TR_NAME, "untagged")
            port_group.set(MetaManager.TR_ID, "untagged")
            # Create the ports subtag
            for untagged_port in untagged_ports:
                port = ET.SubElement(port_group, MetaManager.TR_PORT)
                port.set(
                    MetaManager.TR_NAME, get_unique_property_id(untagged_port, "Location"))
                loc_attr = ET.SubElement(port, MetaManager.TR_ATTR)
                loc_attr.set(MetaManager.TR_NAME, MetaManager.TR_LOCATION)
                loc_attr.set(
                    MetaManager.TR_VALUE, untagged_port.Get("Location"))
        plLogger.LogDebug("end.generate_test_resources.MetaManager")

    @staticmethod
    def generate_editable_params(exp_props, taggedParams, root):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_editable_params.MetaManager")
        if root is None:
            plLogger.LogError("Invalid root")
            return

        # Create the editableParams tag
        editableParams = ET.SubElement(root, MetaManager.EDITABLE_PARAMS)

        # First, handle exposed properties, if any.
        if exp_props is None:
            plLogger.LogDebug("No exposedProperties. Skipping.")
        else:
            # Create the paramGroups subtag
            paramGroups = ET.SubElement(editableParams, MetaManager.EP_PARAM_GROUPS)
            # Mark as containing exposed parameters
            paramGroups.set(MetaManager.EP_NAME, MetaManager.EP_EXPOSED)

            # Now process the commands that have exposed properties
            sorted_eps = MetaManager.sort_exposed_properties(exp_props)

            if sorted_eps is None:
                plLogger.LogError("No sorted_eps")
                return
            if sorted_eps.keys() is None:
                plLogger.LogError("No sorted_eps keys")
                return

            # Each object in the sorted list corresponds to a command.
            # For now, create one paramGroup per command.
            for obj_id in sorted_eps.keys():
                plLogger.LogDebug("Found one obj_id in sorted_eps.keys()")
                # Create a new paramGroup
                paramGroup = ET.SubElement(paramGroups, MetaManager.EP_PARAM_GROUP)
                # Give the paramGroup a name and ID
                # For the name, sometimes the EPClassId comes in of form
                # spirent.methodology.command, so need to split
                # Eventually, this will be replaced with user input
                class_id = sorted_eps[obj_id][0].Get("EPClassId")
                ci_name_list = class_id.split('spirent.methodology.')
                if len(ci_name_list) == 2:
                    # Just get the second part
                    pg_name = ci_name_list[1]
                else:
                    # Just use the original
                    pg_name = class_id

                paramGroup.set(MetaManager.EP_NAME, pg_name)
                paramGroup.set(MetaManager.EP_ID, str(obj_id))

                # Now create a params tag and loop through the exposed properties
                # associated with the command
                params = ET.SubElement(paramGroup, MetaManager.EP_PARAMS)
                for ep in sorted_eps[obj_id]:
                    param = ET.SubElement(params, MetaManager.EP_PARAM)
                    # Give the param a name
                    # Sometimes the EPPropertyId comes in of form
                    # spirent.methodology.command.property, so need to split
                    # Eventually, this will be replaced with user input
                    prop_id = ep.Get("EPPropertyId")
                    split_prop_id = prop_id.split('spirent.methodology.')
                    if len(split_prop_id) == 2:
                        # Process the second part
                        command_prop = split_prop_id[1]
                        split_command_prop = command_prop.split('.')
                        if len(split_command_prop) == 2:
                            # Use the second part. It's the property name
                            param_name = split_command_prop[1]
                        else:
                            # Just use the unsplit command_prop
                            param_name = command_prop
                    else:
                        # Sometimes this part will be of the form command.prop,
                        # so some split magic is also required here.
                        split_command_prop = prop_id.split('.')
                        if len(split_command_prop) == 2:
                            # Use the second part. It's the property name
                            param_name = split_command_prop[1]
                        else:
                            # Just use the unsplit command_prop
                            param_name = prop_id

                    param.set(MetaManager.EP_NAME, param_name)

                    # StcPropertyId is the EPNameId
                    # Note that this value is the key that the MethodologyGroupCommand
                    # uses to associate parameters with the commands in the sequencer.
                    # Both TXML generation and MethodologyGroupCommand must use this
                    # value.
                    stcPropertyId = ep.Get("EPNameId")
                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_PROP_ID)
                    attribute.set(MetaManager.EP_VALUE, stcPropertyId)

                    # defaultValue
                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_DEFAULT)
                    attribute.set(MetaManager.EP_VALUE, ep.Get("EPDefaultValue"))

                    # type
                    ep_prop_id = ep.Get("EPPropertyId")
                    idx = ep_prop_id.index(MetaManager.MM_COMMAND_NAME) + \
                        len(MetaManager.MM_COMMAND_NAME)
                    class_name = ep_prop_id[:idx]
                    property_id = ep_prop_id[idx + 1:]

                    prop_meta = CMeta.GetPropertyMeta(class_name, property_id)

                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_TYPE)
                    attribute.set(
                        MetaManager.EP_VALUE, MetaManager.adjust_type(prop_meta["type"]))

                    # units
                    # Don't know where to get them from, so hard-code for now
                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_UNITS)
                    attribute.set(MetaManager.EP_VALUE, "ounces")

                    # minInclusive and maxInclusive
                    # Since we don't have stak interface to get the numeric
                    # validate tag in the data model we hardcode them for now
                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_MIN_INCL)
                    attribute.set(MetaManager.EP_VALUE, "0")

                    attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                    attribute.set(MetaManager.EP_NAME, MetaManager.EP_MAX_INCL)
                    attribute.set(MetaManager.EP_VALUE, "unbounded")

                    # MinOccurences and MaxOccurrences
                    if prop_meta["isCollection"] == "true":
                        attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                        attribute.set(
                            MetaManager.EP_NAME, MetaManager.EP_MIN_OCCURS)
                        attribute.set(MetaManager.EP_VALUE, prop_meta["minOccurs"])
                        attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                        attribute.set(
                            MetaManager.EP_NAME, MetaManager.EP_MAX_OCCURS)
                        attribute.set(MetaManager.EP_VALUE, prop_meta["maxOccurs"])
        # Next, process any tagged params

        # Always create the paramGroups subtag
        paramGroups = ET.SubElement(editableParams, MetaManager.EP_PARAM_GROUPS)
        # Mark as containing tagged parameters
        paramGroups.set(MetaManager.EP_NAME, MetaManager.EP_TAGGED)

        # Fill in groups and params only if passed in.
        plLogger.LogDebug("Start processing tagged parameters: " + str(taggedParams))
        if taggedParams:
            try:
                root = ET.fromstring(taggedParams)
                if root is None:
                    plLogger.LogWarn("No tagged params to process")
                else:
                    pg_list = root.findall(".//" + MetaManager.EP_PARAM_GROUP)
                    for pg in pg_list:
                        plLogger.LogDebug("pg: " + str(pg))
                        paramGroup = ET.SubElement(paramGroups, MetaManager.EP_PARAM_GROUP)
                        if pg.get(MetaManager.EP_NAME):
                            paramGroup.set(MetaManager.EP_NAME, pg.get(MetaManager.EP_NAME))
                        params = ET.SubElement(paramGroup, MetaManager.EP_PARAMS)
                        p_list = pg.findall(".//" + MetaManager.EP_PARAM)
                        for p in p_list:
                            param = ET.SubElement(params, MetaManager.EP_PARAM)
                            if p.get(MetaManager.EP_ID):
                                param.set(MetaManager.EP_ID, p.get(MetaManager.EP_ID))
                            if p.get(MetaManager.EP_NAME):
                                param.set(MetaManager.EP_NAME, p.get(MetaManager.EP_NAME))
                            if p.get(MetaManager.EP_TAG):
                                param.set(MetaManager.EP_TAG, p.get(MetaManager.EP_TAG))
                            a_list = p.findall(".//" + MetaManager.EP_ATTR)
                            for a in a_list:
                                attribute = ET.SubElement(param, MetaManager.EP_ATTR)
                                if a.get(MetaManager.EP_NAME) and a.get(MetaManager.EP_VALUE):
                                    attribute.set(MetaManager.EP_NAME,
                                                  a.get(MetaManager.EP_NAME))
                                    attribute.set(MetaManager.EP_VALUE,
                                                  a.get(MetaManager.EP_VALUE))
            except ET.ParseError:
                plLogger.LogError("Error parsing tagged params:\n" + ET.tostring(editableParams))
                # Keep going
                pass

        plLogger.LogDebug("Editable params: \n" + ET.tostring(editableParams))
        plLogger.LogDebug("end.generate_editable_params.MetaManager")

    # FIXME:
    # This can be removed
    @staticmethod
    def generate_topology_info(root):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_topology_info.MetaManager")

        # Check inputs
        if root is None:
            plLogger.LogError("Invalid root")
            return
        # Insert the <topologyInfo> tag. For now, that is all we will do.
        # We'll name the section in the TXML so that we will show it
        # as reserved for future use.
        topo_info = ET.SubElement(root, MetaManager.TOPOLOGY_INFO)
        topo_info.set(MetaManager.TPI_NAME, "Reserved")
        topo_info.set(MetaManager.TPI_DESC, "Reserved for future use")

        plLogger.LogDebug("end.generate_topology_info.MetaManager")

    # FIXME:
    # This can be removed
    @staticmethod
    def generate_traffic_info(seq_info, infoName, infoDescp, root):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogDebug("begin.generate_traffic_info.MetaManager")

        if root is None:
            plLogger.LogError("Invalid root")
            return

        # Create the trafficInfo tag
        trafficInfo = ET.SubElement(root, MetaManager.TRAFFIC_INFO)
        trafficInfo.set(MetaManager.TRF_NAME, infoName)
        trafficInfo.set(MetaManager.TRF_DESCRIPTION, infoDescp)

        if seq_info is None:
            plLogger.LogError("Invalid seq_info")
            return
        if seq_info.trf_cmd is None:
            plLogger.LogDebug("Invalid trf_cmd")
            return

        plLogger.LogDebug("Processing a traffic command...")
        # Create the traffic subtag
        traffic = ET.SubElement(trafficInfo, MetaManager.TRF_TRAFFIC)

        add_traffic_props_as_attributes(seq_info.trf_cmd, traffic)
        plLogger.LogDebug("end.generate_traffic_info.MetaManager")

    # FIXME:
    # This can be removed
    @staticmethod
    def generate_result_info(seq_info, root):
        pass


# FIXME:
# This can be removed
def add_traffic_props_as_attributes(cmd, tag):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.add_traffic_props_as_attributes.txml_utils")
    if not cmd:
        plLogger.LogError("No command passed in")
        return
    prop_list = CMeta.GetProperties(cmd.GetType())
    if not prop_list:
        plLogger.LogError("No property found")
        return
    plLogger.LogDebug("Properties: " + str(prop_list))
    for prop in prop_list:
        prop_meta = CMeta.GetPropertyMeta(cmd.GetType(), prop)
        if prop_meta:
            category = prop_meta.get("category")
            plLogger.LogDebug("category: " + category)
            if "input" == category:
                if ((prop == MetaManager.TRF_COMMAND_NAME) or
                        (prop == MetaManager.TRF_PACKAGE_NAME)):
                    continue
                # Set the name
                attribute_tag = ET.SubElement(tag, MetaManager.TRF_ATTR)
                attribute_tag.set(MetaManager.TRF_NAME, prop)

                # Set the value
                plLogger.LogDebug(
                    " property: " + prop + "  : " + str(prop_meta))
                attribute_tag.set(
                    MetaManager.TRF_VALUE, str(prop_meta.get("default")))
        else:
            plLogger.LogWarn("No meta data for command. Skipping.")
    plLogger.LogDebug("end.add_traffic_props_as_attributes.txml_utils")


def extract_methodology_key_from_file(meta_file):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.extract_methodology_key_from_file.txml_utils")
    test_name = ""

    plLogger.LogDebug("Parse XML from file")
    plLogger.LogDebug("File name is " + meta_file)
    tree = ET.parse(meta_file)
    plLogger.LogDebug("get root from parsed XML")
    root = tree.getroot()
    if root is None:
        plLogger.LogError("Failed to find an XML root node in " + meta_file)
        return ""
    plLogger.LogDebug("root from parsed XML is not empty")
    for child in root:
        if child.tag == MetaManager.TEST_INFO:
            test_name = child.get(MetaManager.TI_KEY)

    if test_name is None:
        plLogger.LogWarn("WARNING: Could not find the test " +
                         "name in the TXML file.")
    else:
        plLogger.LogDebug("test_name: " + test_name)
    plLogger.LogDebug("end.extract_methodology_key_from_file.txml_utils")
    return test_name


def extract_methodology_name_from_file(meta_file):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.extract_methodology_name_from_file.txml_utils")
    test_name = ""

    plLogger.LogDebug("Parse XML from file")
    plLogger.LogDebug("File name is " + meta_file)
    tree = ET.parse(meta_file)
    plLogger.LogDebug("get root from parsed XML")
    root = tree.getroot()
    if root is None:
        plLogger.LogError("Failed to find an XML root node in " + meta_file)
        return ""
    plLogger.LogDebug("root from parsed XML is not empty")
    for child in root:
        if child.tag == MetaManager.TEST_INFO:
            test_name = child.get(MetaManager.TI_DISPLAY_NAME)

    if test_name is None:
        plLogger.LogWarn("WARNING: Could not find the test name in the TXML file.")
    else:
        plLogger.LogDebug("test_name: " + test_name)
    plLogger.LogDebug("end.extract_methodology_name_from_file.txml_utils")
    return test_name


def extract_test_case_name_from_file(meta_file):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.extract_test_case_name_from_file.txml_utils")
    test_case = ""

    plLogger.LogDebug("meta_file: " + str(meta_file))
    try:
        tree = ET.parse(meta_file)
    except ET.ParseError:
        plLogger.LogError("Error parsing meta file: " + str(meta_file))
        return test_case
    root = tree.getroot()
    for child in root:
        if child.tag == MetaManager.TEST_INFO:
            test_case = child.get(MetaManager.TI_TEST_CASE_NAME)
            break
    # Note that None is returned if the attribute doesn't exist in the tag
    if test_case is None:
        test_case = ""

    if test_case is None:
        plLogger.LogWarn(
            "WARNING: Could not find the test case name in the TXML file.")
    plLogger.LogDebug("test_case: " + str(test_case))
    plLogger.LogDebug("end.extract_test_case_name_from_file.txml_utils")
    return test_case


def extract_test_case_key_from_file(meta_file):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.extract_test_case_key_from_file.txml_utils")
    test_case = ""

    plLogger.LogDebug("meta_file: " + str(meta_file))
    try:
        tree = ET.parse(meta_file)
    except ET.ParseError:
        plLogger.LogError("Error parsing meta file: " + str(meta_file))
        return test_case
    root = tree.getroot()
    for child in root:
        if child.tag == MetaManager.TEST_INFO:
            test_case = child.get(MetaManager.TI_TEST_CASE_KEY)
            break
    # Note that None is returned if the attribute doesn't exist in the tag
    if test_case is None:
        test_case = ""

    if test_case is None:
        plLogger.LogWarn(
            "WARNING: Could not find the test case key in the TXML file.")
    plLogger.LogDebug("test_case: " + str(test_case))
    plLogger.LogDebug("end.extract_test_case_name_from_file.txml_utils")
    return test_case


def extract_test_labels_from_file(meta_file):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.extract_test_labels_from_file.txml_utils")
    label_list = []
    tree = ET.parse(meta_file)
    root = tree.getroot()
    plLogger.LogDebug("root tag is " + root.tag)
    for child in root:
        plLogger.LogDebug("child tag is " + child.tag)
        if child.tag == MetaManager.TEST_INFO:
            for subchild in child:
                plLogger.LogDebug("subchild tag is " + subchild.tag)
                if subchild.tag == MetaManager.TI_LABELS:
                    for subsubchild in subchild:
                        plLogger.LogDebug(
                            "subsubchild tag is " + subsubchild.tag)
                        if subsubchild.tag == MetaManager.TI_LABEL:
                            if subsubchild.text is not None:
                                plLogger.LogDebug(
                                    "appending " + str(subsubchild.text))
                                label_list.append(subsubchild.text)
    plLogger.LogDebug(" returning: " + str(label_list))
    plLogger.LogDebug("end.extract_test_labels_from_file.txml_utils")
    return label_list


def get_timestamp_ymd_hms():
    ts = time.time()
    nice_ts = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    return nice_ts


def get_unique_property_id(obj, prop):
    return (obj.GetType() + "." + prop + "." + str(obj.GetObjectHandle())).lower()


def add_props_as_attributes(cmd, tag):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.add_props_as_attributes.txml_utils")
    if not cmd:
        plLogger.LogError("No command passed in")
        return
    prop_list = CMeta.GetProperties(cmd.GetType())
    if not prop_list:
        plLogger.LogError("No command properties found")
        return
    plLogger.LogDebug("Properties: " + str(prop_list))
    for prop in prop_list:
        prop_meta = CMeta.GetPropertyMeta(cmd.GetType(), prop)
        if prop_meta:
            category = prop_meta.get("category")
            if "input" == category:
                # Set the name
                attribute_tag = ET.SubElement(tag, MetaManager.TPI_ATTR)
                attribute_tag.set(MetaManager.TPI_NAME, prop)

                # Set the value
                attribute_tag.set(
                    MetaManager.TPI_VALUE, str(prop_meta.get("default")))

                # Set the id
                attribute_tag.set(
                    MetaManager.TPI_ID, get_unique_property_id(cmd, prop))
        else:
            plLogger.LogWarn("No meta data for command [Name = " + cmd.GetName() +
                             " Handle = " + str(cmd.GetObjectHandle()) + "]" + ". Skipping.")
    plLogger.LogDebug("end.add_props_as_attributes.txml_utils")
