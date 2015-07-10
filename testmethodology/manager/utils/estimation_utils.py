from StcIntPythonPL import *
import ast
import itertools
import json
import os
import re
import sys
import xml.etree.ElementTree as etree
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
import spirent.methodology.utils.xml_config_utils as xml_utils
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from spirent.methodology.utils.iteration_framework_utils \
    import parse_iterate_mode_input


# Constants (taken in global context just for removing self.)
# Table of PHY types and default speeds, if differing from SPEED_1G
PHY_TABLE = {
    'ETHERNET_COPPER': {'class': 'EthernetCopper'},
    'ETHERNET_FIBER': {'class': 'EthernetFiber'},
    'ETHERNET_10_GIG_FIBER': {'class': 'Ethernet10GigFiber'},
    'POS': {'class': 'PosPhy', 'default': 'OC192'},
    'ETHERNET_10_GIG_COPPER': {'class': 'Ethernet10GigCopper'},
    'ATM': {'class': 'AtmPhy', 'default': 'OC192'},
    'FC': {'class': 'FcPhy', 'default': 'SPEED_2G'},
    'ETHERNET_40_GIG_FIBER': {'class': 'Ethernet40GigFiber'},
    'ETHERNET_100_GIG_FIBER': {'class': 'Ethernet100GigFiber'}
}
# Usually part of the Phy.LineSpeed, but for SONET-based interfaces, it is
# located in the SonetConfig (1:1 to Phy) object
RATE_TABLE = {
    'ETHERNET': ['SPEED_10M', 'SPEED_100M', 'SPEED_1G',
                 'SPEED_10G', 'SPEED_40G', 'SPEED_100G'],
    'SONET': ['OC3', 'OC12', 'OC48', 'OC192'],
    'FC': ['SPEED_2G', 'SPEED_4G', 'SPEED_8G', 'SPEED_10G']
}
RATE_BPS = {
    'SPEED_10M': 10000000.0,
    'SPEED_100M': 100000000.0,
    'SPEED_1G': 1000000000.0,
    'SPEED_10G': 10000000000.0,
    'SPEED_40G': 40000000000.0,
    'SPEED_100G': 100000000000.0,
    'OC3': 155520000.0,
    'OC12': 622080000.0,
    'OC48': 2488000000.0,
    'OC192': 9952000000.0,
    'SPEED_2G': 2000000000.0,
    'SPEED_4G': 4000000000.0,
    'SPEED_8G': 8000000000.0
}


class PhyValidator(object):
    '''
    Code to take care of phy and line rate calculations, given parameters from
    the TXML file
    '''

    @staticmethod
    def validate_type_and_speed(phy_type, line_speed):
        logger = PLLogger.GetLogger('methodology')
        if phy_type not in PHY_TABLE:
            logger.LogWarn('Unknown phy_type {}, assuming ETHERNET_COPPER'.
                           format(phy_type))
            phy_type = 'ETHERNET_COPPER'
        default = PHY_TABLE[phy_type].get('default', 'SPEED_1G')
        rate_type = {
            'POS': 'SONET',
            'ATM': 'SONET',
            'FC': 'FC'
        }.get(phy_type, 'ETHERNET')
        if line_speed not in RATE_TABLE[rate_type]:
            logger.LogWarn('Invalid line speed for {}, using default {}'.
                           format(phy_type, default))
            line_speed = default
        return {'class': PHY_TABLE[phy_type].get('class',
                                                 'EthernetCopper'),
                'rate_bps': RATE_BPS[line_speed]}

    @staticmethod
    def convert_to_fps(value, unit, frame_size, phy_type, line_speed):
        logger = PLLogger.GetLogger('methodology')
        val_data = PhyValidator.validate_type_and_speed(phy_type, line_speed)
        if unit is None or unit == 'FRAMES_PER_SECOND':
            return value
        bps = val_data['rate_bps']
        if unit in ['INTER_BURST_GAP', 'INTER_BURST_GAP_IN_MILLISECONDS',
                    'INTER_BURST_GAP_IN_NANOSECONDS']:
            logger.LogWarn("{} mode unsupported, using frames per second".
                           format(unit))
        elif unit == 'PERCENT_LINE_RATE':
            # Assumes 12 byte gap
            return int(round((bps * value) /
                             (100 * 8 * (frame_size + 12 + 8))))
        elif unit == 'BITS_PER_SECOND':
            return int(round(float(value) /
                             (8 * (frame_size + 12 + 8))))
        elif unit == 'KILOBITS_PER_SECOND':
            return int(round(float(value) * 1000.0 /
                             (8 * (frame_size + 12 + 8))))
        elif unit == 'MEGABITS_PER_SECOND':
            return int(round(float(value) * 1000000.0 /
                             (8 * (frame_size + 12 + 8))))
        else:
            logger.LogWarn("Unknown load unit {}, using frames per second".
                           format(unit))
        return value


# STC XML Manipulation utilities
def get_stc_collection(elem, attr):
    '''
    This code takes the property from an ElementTree element, and gets the
    value of the named attribute for the element.
    Note that this also emulates the existing bug in the manner in which
    save/load fails with strings containing braces gives problems.
    '''
    # Optimization, if no braces, just split on whitespace
    cur_str = elem.get(attr)
    if '{' not in cur_str:
        return cur_str.split()
    # Otherwise, if the string starts on a left brace, look for next occuring
    # right brace, and use that as the string. Note that this incurs a bug in
    # the case where the actual string contains a brace (and space)
    out_list = []
    while len(cur_str) > 0:
        if cur_str[0] == '{':
            idx = cur_str.find('}', 1)
            out_list.append(cur_str[1:idx])
            if idx == -1:
                cur_str = ''
            else:
                cur_str = cur_str[idx + 1:].lstrip()
        else:
            tmp = cur_str.split(None, 1)
            if len(tmp) == 0:
                break
            else:
                out_list.append(tmp[0])
                cur_str = tmp[1] if len(tmp) > 1 else ''
    return out_list


STAK_PKG = 'spirent.methodology.'
TRAF_PKG = STAK_PKG + 'traffic.'
LOAD_TMPL_CMD = STAK_PKG + 'LoadTemplateCommand'
GEN_START_CMD = "GeneratorStartCommand"
OBJ_ITER_CMD = STAK_PKG + 'ObjectIteratorCommand'
CFG_FRAMESIZE_CMD = STAK_PKG + 'IteratorConfigFrameSizeCommand'
CFG_TRAFLOAD_CMD = STAK_PKG + 'IteratorConfigTrafficLoadCommand'
CREATE_TRAF_MIX_CMD = TRAF_PKG + 'CreateTrafficMix1Command'
SET_TRAF_ENDPT_CMD = TRAF_PKG + 'SetTrafficEndpointTagsCommand'
FRAME_LEN_DIST = 'FrameLengthDistribution'
FRAME_LEN_DIST_SLOT = 'FrameLengthDistributionSlot'


class SequencerEstimator(object):
    '''
    Base class for manipulating sequencer XML file stored as ElementTree
    elements. Arguments must be specified by keyword. Valid keywords (in order
    of precedence):
    filename - specifies file name
    str - specifies string to load from
    '''
    # Initializer
    def __init__(self, *args, **kwargs):
        self.log = PLLogger.GetLogger('methodology')
        self.port_dict = {}
        self.port_loc_set = set()
        if len(args) > 0:
            raise ValueError('Arguments must be specified with keywords')
        if 'filename' in kwargs:
            try:
                tree = etree.parse(kwargs['filename'])
                if tree is not None:
                    self.root = tree.getroot()
            except:
                exc_info = sys.exc_info()
                err = 'Could not load sequencer file {}: {} {}'
                self.log.LogError(err.format(kwargs['filename'],
                                             exc_info[0], exc_info[1]))
                raise
        elif 'str' in kwargs:
            try:
                self.root = etree.fromstring(kwargs['str'])
            except:
                err = 'Could not load sequencer from string: {} {}'
                self.log.LogError(err.format(exc_info[0], exc_info[1]))
        elif 'root' in kwargs:
            self.root = kwargs['root']

    def set_port_dict(self, port_dict):
        self.port_dict = port_dict
        # The values turn into lists of lists of locations
        self.port_loc_set = \
            set(itertools.chain(*self.port_dict.values()))

    def find_all_elements(self, xml_tag, under=None):
        '''
        Shortcut utility just to find all nodes in the sequencer with xml tag
        If under is not specified, assumes root
        '''
        if under is None:
            under = self.root
        return under.findall('.//' + xml_tag) if under is not None else []

    def traffic_enabled(self):
        '''
        Simple check to verify that traffic is used
        '''
        start_list = self.find_all_elements(GEN_START_CMD)
        return start_list is not None and len(start_list) > 0

    def find_iterator_from_config(self, config_cmd_tag):
        '''
        Given a tag name for a configurator, find a list of all object
        iterator commands which correspond to it
        '''
        if self.root is None:
            return []
        iter_cmd_list = []
        for cfg_cmd in self.find_all_elements(config_cmd_tag):
            parent = xml_utils.get_parent(self.root, cfg_cmd)
            # This doesn't cover all types of iterator commands
            child_iter = xml_utils.get_children(parent, OBJ_ITER_CMD)
            iter_cmd_list += child_iter
        return iter_cmd_list

    def get_iter_value_list(self, obj_iter_cmd):
        '''
        Retrieves the value list from the object iterator command
        '''
        value_type = obj_iter_cmd.get('ValueType')  # List or range

        if value_type == 'LIST':
            str_list = get_stc_collection(obj_iter_cmd, 'ValueList')
            # Some of these could be type(<tuple>) strings
            val_list = [ast.literal_eval(x) if '(' not in x else x for x in str_list]
            return val_list
        elif value_type == 'RANGE':
            minVal = int(obj_iter_cmd.get('MinVal'))
            maxVal = int(obj_iter_cmd.get('MaxVal'))
            stepVal = int(obj_iter_cmd.get('StepVal'))
            # Python range operator goes to maxVal - 1
            return range(minVal, maxVal + 1, stepVal)

    # Frame Length Specific
    def get_imix_max_frame_length(self, name):
        element = None
        for elem in self.find_all_elements(FRAME_LEN_DIST):
            if elem.get('Name') == name:
                element = elem
                break
        if element is None:
            return 0
        frame_len_list = \
            [int(slot.get('MaxFrameLength')) for slot in
                self.find_all_elements(FRAME_LEN_DIST_SLOT, element)]
        return max(frame_len_list)

    # Specific statistic retrieval
    def estimate_device_count(self):
        portDeviceCountDict = {}
        for loc in self.port_loc_set:
            portDeviceCountDict[loc] = 0
        for load_tmpl_elem in self.find_all_elements(LOAD_TMPL_CMD):
            copiesPerParent = int(load_tmpl_elem.get('CopiesPerParent'))
            tagNames = get_stc_collection(load_tmpl_elem, 'TargetTagList')
            for targetTag in tagNames:
                if targetTag == '':
                    continue
                if targetTag in self.port_dict:
                    location_list = self.port_dict[targetTag]
                    for loc in location_list:
                        if loc not in portDeviceCountDict:
                            portDeviceCountDict[loc] = 0
                        portDeviceCountDict[loc] += copiesPerParent
        return portDeviceCountDict

    def estimate_frame_size(self):
        portFrameSizeDict = {}
        for loc in self.port_loc_set:
            portFrameSizeDict[loc] = 0
        if not self.traffic_enabled():
            return portFrameSizeDict
        for trafficStartCmd in self.find_all_elements(GEN_START_CMD):
            objectIteratorCommands = \
                self.find_iterator_from_config(CFG_FRAMESIZE_CMD)
            for objectIteratorCommand in objectIteratorCommands:
                val_list = self.get_iter_value_list(objectIteratorCommand)
                new_list = []
                for val in val_list:
                    if isinstance(val, int):
                        new_list.append(val)
                        continue
                    match = parse_iterate_mode_input(val)
                    val = 0
                    sizeType = match['type']
                    if sizeType == 'fixed':
                        val = int(match["start"])
                    elif sizeType == "incr":
                        val = int(match["end"])
                    elif sizeType == "rand":
                        val = int(match["end"])
                    elif sizeType == "imix":
                        # Find max frame length from FrameLengthDistribution
                        val = self.get_imix_max_frame_length(match["name"])
                    new_list.append(val)
                value = max(new_list)
                for loc in self.port_loc_set:
                    if loc in portFrameSizeDict and value > portFrameSizeDict[loc]:
                        portFrameSizeDict[loc] = value
        self.log.LogDebug("estimate_frame_size returning " +
                          str(portFrameSizeDict))
        return portFrameSizeDict

    def estimate_load(self, frame_estimate={}, hw_dict={}):
        portTrafficLoadDict = {}
        loadUnit = None
        for loc in self.port_loc_set:
            portTrafficLoadDict[loc] = 0
        if not self.traffic_enabled():
            return portTrafficLoadDict
        ele_list = self.find_all_elements(CFG_TRAFLOAD_CMD)
        if len(ele_list) > 0:
            loadUnit = ele_list[0].get("LoadUnit")
        objectIteratorCommands = \
            self.find_iterator_from_config(CFG_TRAFLOAD_CMD)
        for objectIteratorCommand in objectIteratorCommands:
            val_list = self.get_iter_value_list(objectIteratorCommand)
            new_list = []
            for val in val_list:
                if isinstance(val, int):
                    new_list.append(val)
                    continue
                match = parse_iterate_mode_input(val)
                val = 0
                if match['type'] != 'fixed':
                    self.log.LogError("ERROR: Only the fixed " +
                                      "load size is currently supported")
                    return None
                try:
                    val = ast.literal_eval(match["start"])
                except SyntaxError:
                    self.log.LogError("ERROR: " + LoadUnit +
                                      " requires numeric values")
                    return None
                new_list.append(val)
            value = max(new_list)
            for loc in self.port_loc_set:
                if loc not in portTrafficLoadDict or \
                   value <= portTrafficLoadDict[loc]:
                    continue
                phy_type = 'ETHERNET_COPPER'
                line_speed = 'SPEED_1G'
                frame_size = 128
                if loc in hw_dict:
                    phy_type = hw_dict[loc]['phy']
                    line_speed = hw_dict[loc]['speed']
                if loc in frame_estimate:
                    frame_size = frame_estimate[loc]
                portTrafficLoadDict[loc] = \
                    PhyValidator.convert_to_fps(value, loadUnit,
                                                frame_size,
                                                phy_type, line_speed)
        return portTrafficLoadDict

    def count_template_tagged_objects(self, tag_name, obj_count_dict):
        for load_tmpl_elem in self.find_all_elements(LOAD_TMPL_CMD):
            copiesPerParent = int(load_tmpl_elem.get('CopiesPerParent'))
            tag_list = get_stc_collection(load_tmpl_elem, 'TargetTagList')
            load_from_file = \
                load_tmpl_elem.get('EnableLoadFromFileName') == 'TRUE'
            tagged_port_list = []
            for tag in tag_list:
                if tag == '' or tag not in self.port_dict:
                    continue
                for port in self.port_dict[tag]:
                    if port not in obj_count_dict:
                        obj_count_dict[port] = 0
                        tagged_port_list.append(port)
            template_xml = load_tmpl_elem.get('TemplateXml') \
                if not load_from_file else \
                xml_utils.load_xml_from_file(load_tmpl_elem.get('TemplateXmlFileName'))
            tag_prefix = load_tmpl_elem.get('TagPrefix')
            if tag_prefix != '':
                template_xml = xml_utils.add_prefix_to_tags(tag_prefix,
                                                            template_xml)
            root = etree.fromstring(template_xml)
            tagged_ele_list = \
                xml_utils.find_tagged_elements_by_tag_name(root, [tag_name])
            tagged_objs = []
            for tagged_obj in tagged_ele_list:
                if tagged_obj.tag != "Tags":
                    tagged_objs.append(tagged_obj)
            tagged_ele_cnt = len(tagged_objs)
            for port in tagged_port_list:
                obj_count_dict[port] += (copiesPerParent * tagged_ele_cnt)
            if tagged_ele_cnt == 0:
                self.log.LogDebug("Could not find any element tagged with " +
                                  tag_name + " in the template XML from cmd " +
                                  etree.tostring(load_tmpl_elem))

    def estimate_stream_count(self):
        portStreamCountDict = {}
        for loc in self.port_loc_set:
            portStreamCountDict[loc] = 0
        if not self.traffic_enabled():
            return portStreamCountDict
        setTrafficEndpointTagsCommands = []
        for traf_mix in self.find_all_elements(CREATE_TRAF_MIX_CMD):
            setTrafficEndpointTagsCommands += \
                self.find_all_elements(SET_TRAF_ENDPT_CMD, traf_mix)
        for setTrafficEndpointTagsCommand in setTrafficEndpointTagsCommands:
            if setTrafficEndpointTagsCommand is None:
                self.log.LogDebug("estimate_stream_count returning None")
                return None

            srcTagList = get_stc_collection(setTrafficEndpointTagsCommand,
                                            "SrcEndpointNameList")
            dstTagList = get_stc_collection(setTrafficEndpointTagsCommand,
                                            "DstEndpointNameList")

            self.log.LogDebug("estimate_stream_count srcTagList = " + str(srcTagList))
            self.log.LogDebug("estimate_stream_count dstTagList = " + str(dstTagList))

            srcPortCntDict = {}
            dstPortCntDict = {}
            for srcTag in srcTagList:
                self.count_template_tagged_objects(srcTag, srcPortCntDict)
            for dstTag in dstTagList:
                self.count_template_tagged_objects(dstTag, dstPortCntDict)
            self.log.LogDebug("estimate_stream_count srcPortCntDict = " +
                              str(srcPortCntDict))
            self.log.LogDebug("estimate_stream_count dstPortCntDict = " +
                              str(dstPortCntDict))

            srcEndpointCnt = 0
            dstEndpointCnt = 0
            for port, objectCnt in dstPortCntDict.iteritems():
                dstEndpointCnt = dstEndpointCnt + objectCnt

            for port, objectCnt in srcPortCntDict.iteritems():
                srcEndpointCnt = srcEndpointCnt + objectCnt
                streamCnt = objectCnt * dstEndpointCnt
                if port in portStreamCountDict:
                    portStreamCountDict[port] = portStreamCountDict[port] + streamCnt
                else:
                    portStreamCountDict[port] = streamCnt

            for port, objectCnt in dstPortCntDict.iteritems():
                streamCnt = objectCnt * srcEndpointCnt
                if port in portStreamCountDict:
                    portStreamCountDict[port] = portStreamCountDict[port] + streamCnt
                else:
                    portStreamCountDict[port] = streamCnt
        for loc in self.port_loc_set:
            if loc not in portStreamCountDict:
                portStreamCountDict[loc] = 0
        self.log.LogDebug("estimate_stream_count returning " + str(portStreamCountDict))
        return portStreamCountDict


class StcTag(object):
    '''
    Wrapper class used to create exposed property instances from an
    ElementTree element object holding an exposed property object
    '''
    def __init__(self, prop_elem):
        self.name = prop_elem.get('Name')
        self.handle = int(prop_elem.get('id'))

    @staticmethod
    def get_tag_list(root):
        ep_list = root.findall('.//Tag')
        return [StcTag(ep) for ep in ep_list]


class ExposedProperty(object):
    '''
    Wrapper class used to create exposed property instances from an
    ElementTree element object holding an exposed property object
    '''
    def __init__(self, prop_elem):
        self.name = prop_elem.get('EPNameId')
        self.prop_name = prop_elem.get('EPPropertyName')
        self.class_id = prop_elem.get('EPClassId')
        self.prop_id = prop_elem.get('EPPropertyId')
        self.default = prop_elem.get('EPDefaultValue')
        self.target_list = []
        rel_list = prop_elem.findall('Relation')
        for rel in rel_list:
            if rel.get('type') == 'ScriptableExposedProperty':
                    self.target_list.append(int(rel.get('target')))

    @staticmethod
    def get_prop_list(root):
        ep_list = root.findall('.//ExposedProperty')
        return [ExposedProperty(ep) for ep in ep_list]


class EstimationUtils(object):
    '''
    Utility class to estimate test parameters
    '''
    # Base class initializer
    def __init__(self, *args, **kwargs):
        '''
        Initialize the class given the STM test case object. Arguments can
        either be anonymous (meaning it's the test case STC object) or you
        need to specify seq_root=<element>, txml_root=<element>
        '''
        self.log = PLLogger.GetLogger('methodology')
        self.port_hw_info = {}
        self.port_loc_set = set()
        self.port_tag_location_dict = {}
        # For unit test only -- short-circuit the usual check and just use the
        # passed in tuple as is
        if 'seq_root' in kwargs and 'txml_root' in kwargs:
            self.seq_root = kwargs['seq_root']
            self.txml_root = kwargs['txml_root']
            self.populate_port_dict()
            return
        if 'test_case' in kwargs:
            test_case = kwargs[test_case]
        elif len(args) > 0:
            test_case = args[0]
        if type(test_case) == int:
            hnd_reg = CHandleRegistry.Instance()
            test_case = hnd_reg.Find(test_case)
        if test_case is None or not test_case.IsTypeOf('StmTestCase'):
            raise ValueError('Invalid test case object')
        base_path = test_case.Get('Path')
        txml_path = os.path.join(base_path, mgr_const.MM_META_FILE_NAME)
        seq_path = os.path.join(base_path, mgr_const.MM_SEQUENCER_FILE_NAME)
        tree = etree.parse(txml_path)
        if tree is not None:
            self.txml_root = tree.getroot()
        else:
            raise RuntimeError('Failed to parse ' + txml_path)
        tree = etree.parse(seq_path)
        if tree is not None:
            self.seq_root = tree.getroot()
        else:
            raise RuntimeError('Failed to parse ' + seq_path)
        self.populate_port_dict()

    def populate_port_dict(self):
        # Before we can start finding the objects, we need a map to link
        # the exposed property to the actual tag names
        ep_list = ExposedProperty.get_prop_list(self.seq_root)
        tag_list = StcTag.get_tag_list(self.seq_root)
        hdl_to_tag_name = {tag.handle: tag.name for tag in tag_list}
        ep_to_name = {}
        for ep in ep_list:
            # Only look for tag/name exposed properties
            if ep.class_id != 'tag' or ep.prop_id != 'scriptable.name':
                continue
            for target in ep.target_list:
                if target in hdl_to_tag_name:
                    ep_to_name[ep.name] = hdl_to_tag_name[target]
        port_grps_list = self.txml_root.findall('.//portGroup')
        if port_grps_list is None:
            return
        for port_grp in port_grps_list:
            # The TXML contains the exposed property's ID
            tag_ep_id = port_grp.get('id')
            # Skip if the exposed tag ID is not in the name
            if tag_ep_id not in ep_to_name:
                continue
            tag_name = ep_to_name[tag_ep_id]
            # Given the ID, find the tag from the sequencer
            port_list = port_grp.findall(".//" + "port")
            for port in port_list:
                phy_type = 'ETHERNET_COPPER'
                line_speed = 'SPEED_1G'
                for child in port:
                    # Uses <attribute name="location" value="..." />
                    # where name can be location, phy_type or line_speed
                    if child.get('name') == 'location':
                        loc = child.get('value')
                        if tag_name not in self.port_tag_location_dict:
                            self.port_tag_location_dict[tag_name] = []
                        self.port_tag_location_dict[tag_name].append(loc)
                        self.port_loc_set.add(loc)
                    if child.get('name') == 'phy_type':
                        phy_type = child.get('value')
                    if child.get('name') == 'line_speed':
                        line_speed = child.get('value')
                # After all children are processed, we set up phy
                self.port_hw_info[loc] = {
                    'phy': phy_type,
                    'speed': line_speed
                }

    def find_tag_from_location(self, location):
        for tag, loc_list in self.port_tag_location_dict.iteritems():
            if location in loc_list:
                return tag
        return None

    @staticmethod
    def get_new_name(old_name):
        match = re.match(r'(.*?)\s+([0-9]+)', old_name)
        if match is None:
            return old_name + ' 1'
        else:
            return match.group(1) + ' ' + str(int(match.group(2)) + 1)

    def get_estimates(self):
        seq_est = SequencerEstimator(root=self.seq_root)
        seq_est.set_port_dict(self.port_tag_location_dict)
        deviceCountEstimate = seq_est.estimate_device_count()
        frameSizeEstimate = seq_est.estimate_frame_size()
        trafficLoadEstimate = seq_est.estimate_load(frameSizeEstimate,
                                                    self.port_hw_info)
        streamCountEstimate = seq_est.estimate_stream_count()

        estimateDict = {}
        for loc in self.port_loc_set:
            # Need to find profile ID
            profile = self.find_tag_from_location(loc)
            if profile in estimateDict:
                ent = estimateDict[profile]
                # If it matches, just tack it on to the location
                if ent['deviceCount'] == int(deviceCountEstimate[loc]) and \
                   ent['avgPacketSize'] == int(frameSizeEstimate[loc]) and \
                   ent['avgFramesPerSecond'] == int(trafficLoadEstimate[loc]) and \
                   ent['streamCount'] == int(streamCountEstimate[loc]):
                    ent['portLocations'].append(loc)
                    continue
                else:
                    profile = self.get_new_name(profile)
            # Set the load accordingly
            estimateDict[profile] = {
                'profileId': profile,
                'portLocations': [loc],
                'deviceCount': int(deviceCountEstimate[loc]),
                'avgPacketSize': int(frameSizeEstimate[loc]),
                'avgFramesPerSecond': int(trafficLoadEstimate[loc]),
                'streamCount': int(streamCountEstimate[loc])
            }
        return estimateDict

    def make_json_string(self, estimationDict):
        # {
        #     {"portProfiles":
        #     [
        #       {"profileId":"test", "portLocations": ["//10.109.120.246/1/1",
        #                                              "//10.109.120.174/1/1",
        #                                              "//10.14.16.27/2/1"],
        #        "deviceCount": 100, "avgFramesPerSecond": 1000,
        #        "streamCount": 1000, "avgPacketSize": 1000}
        #     ]
        #     }
        # }

        self.log.LogDebug("begin.make_json_string.EstimationUtils")

        out_dict = {'portProfiles': []}
        for port, estimate in estimationDict.iteritems():
            out_dict['portProfiles'].append(estimate)
        return json.dumps(out_dict)

    def get_estimates_json(self):
        estimateDict = self.get_estimates()
        return self.make_json_string(estimateDict)
