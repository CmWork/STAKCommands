from StcIntPythonPL import *
import csv
import random
import os
import xml.etree.ElementTree as etree
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils


PKG = "spirent.methodology"


OBJ_KEY = PKG + '.Y1564_Microburst'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(LeftTagName, RightTagName, EnableLearning,
             MicroburstMaxRate, MicroburstRateUnit, FrameSize, MaxDeltaCount,
             DeltaWidth, MaxUniqueAddrCount, MaxImg,
             NominalRate, NominalRateUnit,
             EnableRandomSeed, RandomSeedValue,
             BestEffortTagName, MicroburstTagName, MixTagName,
             MicroburstFileName):
    if MaxDeltaCount < 5:
        return 'Maximum Delta Count must be greater than 5'
    if MaxImg < 50:
        return 'Maximum Inter-Multiburst Gap must be greater than 50 frames'
    if MaxUniqueAddrCount < 1:
        return 'Maximum Unique Address Count must be at least 1'
    if not MicroburstFileName:
        return 'Microburst configuration file name must be specified'
    return ''


def run(LeftTagName, RightTagName, EnableLearning,
        MicroburstMaxRate, MicroburstRateUnit, FrameSize, MaxDeltaCount,
        DeltaWidth, MaxUniqueAddrCount, MaxImg,
        NominalRate, NominalRateUnit,
        EnableRandomSeed, RandomSeedValue,
        BestEffortTagName, MicroburstTagName, MixTagName,
        MicroburstFileName):
    plLogger = PLLogger.GetLogger('Y.1564MicroburstSetup')
    plLogger.LogInfo('Initialize random number generator')
    this_cmd = get_this_cmd()
    # Initialize the random number generator
    if EnableRandomSeed:
        random.seed(RandomSeedValue)
    else:
        random.seed()
    # Rather than call the usual Traffic Mix and Template commands, we fake it
    # here to add the raw streamblocks based on the source port
    plLogger.LogInfo('Create dummy traffic mix')
    traf_mix = create_traffic_mix(MixTagName)
    if not traf_mix:
        raise RuntimeError('Failed to create Traffic Mix object')
    plLogger.LogInfo('Create dummy traffic template')
    tmpl_cfg = create_traffic_template(traf_mix)
    if not tmpl_cfg:
        raise RuntimeError('Failed to create Traffic Template Config object')
    this_cmd.Set('Status', 'Configure generator')
    # Initialize the persistent object
    cmd_dict = {
        'left_tag': LeftTagName,
        'right_tag': RightTagName,
        'stream_tag': MicroburstTagName,
        'max_img': MaxImg,
        'max_unique': MaxUniqueAddrCount,
        'last_unique': 1,
        'nom_rate': NominalRate,
        'nom_rate_unit': NominalRateUnit,
        'bur_max_rate': MicroburstMaxRate,
        'bur_rate_unit': MicroburstRateUnit,
        'frame_size': FrameSize,
        'delta_width': DeltaWidth,
        'gen_list': configure_generator(LeftTagName),
        'img_frame_list': [],
        'be_hdl_list': [],
        'delta_list': [],
        'uniq_map': {}}
    if len(cmd_dict['gen_list']) == 0:
        plLogger.LogError('Failed to retrieve a list of generators')
        return False
    this_cmd.Set('Status', 'Load Microburst configuration')
    plLogger.LogInfo('Read Microburst configuration')
    burst_cfg = read_microburst_cfg(MicroburstFileName)
    # Each burst configuration is stored as a dictionary in a list
    cmd_dict['burst_cfg'] = burst_cfg[:]
    total_delta = 0
    total_be_frame = 0
    plLogger.LogInfo('Configure ' + str(len(burst_cfg)) + ' bursts')
    for burst in cmd_dict['burst_cfg']:
        status = 'Create best effort stream for ' + burst['MicroburstName']
        this_cmd.Set('Status', status)
        plLogger.LogInfo(status)
        # create best effort stream
        be_stream, sched = create_manual_stream(cmd_dict, burst)
        if be_stream:
            tmpl_cfg.AddObject(be_stream, RelationType('GeneratedObject'))
            cmd_dict['be_hdl_list'].append(be_stream.GetObjectHandle())
        if sched:
            tmpl_cfg.AddObject(sched, RelationType('GeneratedObject'))
        if BestEffortTagName:
            tag_utils.add_tag_to_object(be_stream, BestEffortTagName)
        delta_count = random.randint(5, int(MaxDeltaCount))
        status = 'Creating ' + str(delta_count) + ' delta streams for ' + \
            burst['MicroburstName']
        this_cmd.Set('Status', status)
        plLogger.LogInfo(status)
        sb_hdl_list = []
        sb_rate_list = []
        sb_uniq_list = []
        for delta_idx in range(delta_count):
            status = 'Creating delta stream ' + str(delta_idx + 1) + \
                     ' of ' + str(delta_count) + \
                     ' for ' + burst['MicroburstName']
            this_cmd.Set('Status', status)
            plLogger.LogInfo(status)
            # Create delta stream
            del_stream, sched = create_manual_stream(cmd_dict, burst,
                                                     delta_idx)
            total_delta = total_delta + 1
            if del_stream:
                tmpl_cfg.AddObject(del_stream, RelationType('GeneratedObject'))
                sb_hdl_list.append(del_stream.GetObjectHandle())
                sb_rate_list.append(sched.Get('InterFrameGap'))
                sb_uniq_list.append(cmd_dict['last_unique'])
            if sched:
                tmpl_cfg.AddObject(sched, RelationType('GeneratedObject'))
            if MicroburstTagName:
                tag_utils.add_tag_to_object(del_stream, MicroburstTagName)
        # After all deltas per burst, store them
        cmd_dict['delta_list'].append({'handle': sb_hdl_list,
                                       'rate': sb_rate_list,
                                       'uniq': sb_uniq_list})
    # For each handle, map the unique count
    for hdl, uniq in zip(sum([i['handle'] for i in cmd_dict['delta_list']], []),
                         sum([i['uniq'] for i in cmd_dict['delta_list']], [])):
        cmd_dict['uniq_map'][hdl] = uniq
    total_be_frame = sum(cmd_dict['img_frame_list'])
    dur = float(DeltaWidth * total_delta + total_be_frame)

    plLogger.LogInfo('Setting generator duration to ' + str(dur))
    # Set generator's burst duration
    configure_generator(LeftTagName, dur)
    process_tagged_commands()

    # Overwrite if it already exists
    plLogger.LogInfo('Writing persistent object')
    CObjectRefStore.Put(OBJ_KEY, cmd_dict, True)

    if EnableLearning:
        this_cmd.Set('Status', 'Performing Learning...')
        with AutoCommand('ArpNdStartOnAllStreamBlocksCommand') as learning:
            port_list = \
                tag_utils.get_tagged_objects_from_string_names([tag_name])
            learning.SetCollection('PortList',
                                   [x.GetObjectHandle() for x in port_list])
            learning.Execute()
            # Note that whether it passes or fails, this command passes
    return True


def reset():
    return True


# Utilities


def find_config_path(file_name):
    stc_sys = CStcSystem.Instance()
    if os.path.isabs(file_name):
        if os.path.isfile(file_name):
            return file_name
        else:
            return None
    path_list = []
    methodology = None
    test_case = meth_man_utils.get_active_test_case()
    if test_case:
        methodology = test_case.GetParent()
        path_list.append(test_case.Get('Path'))
    if methodology:
        path_list.append(methodology.Get('Path'))
    path_list.append(stc_sys.GetApplicationCommonDataPath())
    for path in path_list:
        path = os.path.normpath(path)
        abs_path = os.path.join(path, file_name)
        if os.path.isfile(abs_path):
            return abs_path
    return None


def create_traffic_mix(tag_name):
    proj = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    # Using default values from traffic mix, assume only a single mix/template
    mix_info = {'Load': '10.0',
                'LoadUnit': 'PERCENT_LINE_RATE',
                'WeightList': '100'}
    mix_elem = etree.Element('MixInfo', mix_info)
    traf_mix = ctor.Create('StmTrafficMix', proj)
    if traf_mix is None:
        return traf_mix
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    if tag_name:
        tag_utils.add_tag_to_object(traf_mix, tag_name)
    return traf_mix


def create_traffic_template(parent_mix):
    ctor = CScriptableCreator()
    tmpl_cfg = ctor.Create('StmTemplateConfig', parent_mix)
    # No further processing, leaving the XML as empty for this purpose
    return tmpl_cfg


def get_frame_list_from_percents(total, perc_list):
    size_list = [int(total * perc / 100.0) for perc in perc_list]
    if sum(size_list) < total:
        remainder = total - sum(size_list)
        # Distribute remainder by "growing" the smallest
        while remainder > 0:
            min_idx = size_list.index(min(size_list))
            size_list[min_idx] += 1
            remainder -= 1
    return size_list


def convert_vlan_priority(value):
    return '{:03b}'.format(value)


def convert_service(name):
    return {'AF11': (40, 1, 2),
            'AF12': (48, 1, 4),
            'AF13': (56, 1, 6),
            'AF21': (72, 2, 2),
            'AF22': (80, 2, 4),
            'AF23': (88, 2, 6),
            'AF31': (104, 3, 2),
            'AF32': (112, 3, 4),
            'AF33': (120, 3, 6),
            'AF41': (136, 4, 2),
            'AF42': (136, 4, 4),
            'AF43': (136, 4, 6),
            'CS1': (32, 1, 0),
            'CS2': (64, 2, 0),
            'CS3': (96, 3, 0),
            'CS4': (128, 4, 0),
            'CS5': (160, 5, 0),
            'CS6': (192, 6, 0),
            'CS7': (224, 7, 0),
            '00': (0, 0, 0),
            'EF': (184, 5, 6)}.get(name, (0, 0, 0))


# Methodology functions


def configure_generator(tag_name, duration=100.0):
    '''
        The generators under the tagged ports will be configured as required
        by the tests
    '''
    port_list = tag_utils.get_tagged_objects_from_string_names([tag_name])
    gen_list = []
    for port in port_list:
        gen = port.GetObject('Generator')
        assert gen
        gen_cfg = gen.GetObject('GeneratorConfig')
        assert gen_cfg
        gen_cfg.Set('SchedulingMode', 'MANUAL_BASED')
        gen_cfg.Set('DurationMode', 'BURSTS')
        gen_cfg.Set('Duration', duration)
        gen_list.append(gen)
    return gen_list


def read_microburst_cfg(file_name):
    '''
        The command will read a csv file with the following format:
        First line is a header with field names, remaining lines are the data
        Expected field names:
        MicroburstName, VlanId, SourceAddr, DestAddr, Gateway, ServiceCosList,
        ServiceDscpList, ServiceRatioList, PrbsLimit, FrameLossLimit,
        LatencyLimit, JitterLimit, OosFrameLimit, ReorderFrameLimit
        Note on format: If an entry has a comma, the string has double quotes
        around it -- double quotes are doubled to escape it from the
        DictReader.
    '''
    path = find_config_path(file_name)
    if not Path:
        raise RuntimeError('Invalid file: ' + file_name)
    values = []
    with open(path, 'r') as fd:
        reader = csv.DictReader(fd)
        for entry in reader:
            values.append(entry)
    return values


def create_manual_stream(cmd_dict, burst, delta_idx=None):
    plLogger = PLLogger.GetLogger('Y.1564MicroburstSetup')
    ctor = CScriptableCreator()
    # Only dealing with the first generator
    gen = cmd_dict['gen_list'][0]
    port = gen.GetParent()
    frame_size = cmd_dict['frame_size']
    # Burst parameters
    if delta_idx is not None:
        # Burst delta
        svc_name = burst['MicroburstName'] + ' Stream ' + str(delta_idx + 1)
        frame_count = cmd_dict['delta_width']
        rand_rate = random.uniform(1,
                                   (cmd_dict['bur_max_rate'] -
                                    cmd_dict['nom_rate']))
        delta_rate = cmd_dict['nom_rate'] + rand_rate
        ifg = delta_rate
        ibg = cmd_dict['nom_rate']
        ieg = delta_rate
        rate_unit = cmd_dict['bur_rate_unit']
    else:
        # Best effort calculations
        svc_name = 'Best Effort Stream'
        frame_count = random.randint(50, cmd_dict['max_img'])
        rate_unit = cmd_dict['nom_rate_unit']
        ifg = cmd_dict['nom_rate']
        ibg = cmd_dict['nom_rate']
        ieg = cmd_dict['nom_rate']
        # Default frame size, 128
        frame_size = 128
        cmd_dict['img_frame_list'].append(frame_count)

    # Set up manual schedule
    gen_cfg = gen.GetObject('GeneratorConfig')
    sched = gen_cfg.GetObject('ManualSchedule')
    if not sched:
        sched = ctor.Create('ManualSchedule', gen_cfg)
    if not sched:
        raise RuntimeError('Failed to create Manual Schedule for port ' +
                           gen.GetParent().Get('Name'))
    plLogger.LogInfo('Creating manual schedule entry')
    sched_entry = ctor.Create('ManualScheduleEntry', sched)
    sched_entry.Set('BurstCount', 1)
    sched_entry.Set('BurstSize', float(frame_count))
    sched_entry.Set('InterFrameGap', ifg)
    sched_entry.Set('InterFrameGapUnit', rate_unit)
    sched_entry.Set('InterBurstGap', ibg)
    sched_entry.Set('InterBurstGapUnit', cmd_dict['nom_rate_unit'])
    sched_entry.Set('InterEntryGap', ieg)
    sched_entry.Set('InterEntryGapUnit', rate_unit)

    plLogger.LogInfo('Creating stream block')
    # Create Stream
    sb = ctor.Create('StreamBlock', port)
    sb.Set('Name', svc_name)
    sb.Set('FixedFrameLength', frame_size)
    sb.Set('TrafficPattern', 'PAIR')
    lp = sb.GetObject('StreamBlockLoadProfile',
                      RelationType('AffiliationStreamBlockLoadProfile'))
    lp.Set('Load', ifg)
    lp.Set('LoadUnit', rate_unit)

    # Populate the raw stream block using PDU scriptable objects
    # This portion of the code should probably be refactored for future use

    # Clear existing objects
    sb.Set('FrameConfig', '')

    vlan_id = ''
    if 'VlanId' in burst and delta_idx is not None:
        vlan_id = burst['VlanId'].strip()
    src_mac = '06:01:00:10:00:01'
    dst_mac = '08:01:00:10:00:01'
    if delta_idx is not None:
        src_mac = '00:{:02x}:00:10:00:01'.format(delta_idx)
    # Ethernet
    pdu_eth = ctor.Create('ethernet:EthernetII', sb)
    pdu_eth.Set('srcMac', src_mac)
    pdu_eth.Set('dstMac', dst_mac)

    # VLAN not used for best effort stuff
    if vlan_id:
        pri = burst['ServiceCosList'].split(';')[0]
        pdu_vlan_cont = ctor.Create('vlans', pdu_eth)
        pdu_vlan = ctor.Create('Vlan', pdu_vlan_cont)
        pdu_vlan.Set('id', vlan_id)
        pdu_vlan.Set('pri', convert_vlan_priority(pri))
        pdu_vlan.Set('type', '8100')

    has_v4 = ('.' in burst['SourceAddr'] and '.' in burst['DestAddr'])
    has_v6 = (':' in burst['SourceAddr'] and ':' in burst['DestAddr'])

    # FIXME: This validation should be done when we read in the csv file
    if not has_v4 and not has_v6:
        raise RuntimeError('Invalid source (' + burst['SourceAddr'] + ') ' +
                           'and destination (' + burst['DestAddr'] + ') ' +
                           'addresses')

    if has_v4:
        pdu_ip = ctor.Create('ipv4:IPv4', sb)
        pdu_ip.Set('sourceAddr', burst['SourceAddr'])
        pdu_ip.Set('destAddr', burst['DestAddr'])
        pdu_ip.Set('gateway', burst['Gateway'])
    else:
        pdu_ip = ctor.Create('ipv6:IPv6', sb)
        pdu_ip.Set('sourceAddr', burst['SourceAddr'])
        pdu_ip.Set('destAddr', burst['DestAddr'])
        pdu_ip.Set('gateway', burst['Gateway'])

    # DSCP or VLAN priorities are set
    if not vlan_id:
        if delta_idx is not None:
            qos = burst['ServiceDscpList'].split(';')[0]
        else:
            qos = '00'
        dscp = convert_service(qos)
        if has_v4:
            pdu_tosdiff = ctor.Create('tosDiffserv', pdu_ip)
            pdu_diff = ctor.Create('diffserv', pdu_tosdiff)
            pdu_diff.Set('dscpHigh', str(dscp[1]))
            pdu_diff.Set('dscplow', str(dscp[2]))
        else:
            pdu_ip.Set('trafficClass', dscp[0])

    # Modifier section, only applicable to delta streams
    if delta_idx is not None:
        perc_list = [float(x) for x in burst['ServiceRatioList'].split(';')]
        size_list = get_frame_list_from_percents(frame_count, perc_list)
        if vlan_id:
            # Make a list of Vlan Priorities
            for pri, num in zip(burst['ServiceCosList'].split(';'), size_list):
                pri_list += [convert_lan_priority(int(pri))] * num
            random.shuffle(pri_list)
            cos_mod = ctor.Create('TableModifier', sb)
            cos_mod.SetCollection('Data', pri_list)
            cos_mod.Set('OffsetReference',
                        '{}.vlans.vlan.pri'.format(pdu_eth.Get('Name')))
            cos_mod.Set('Name', 'CoS Modifier')
        else:
            # Make a list of diffserv Priorities
            dscp_list = []
            for svc, num in zip(burst['ServiceDscpList'].split(';'),
                                size_list):
                # Only grab the byte element, convert to hex bytes
                svc_val = '{:02x}'.format(convert_service(svc)[0])
                dscp_list += [svc_val] * num
            random.shuffle(dscp_list)
            dscp_mod = ctor.Create('TableModifier', sb)
            dscp_mod.SetCollection('Data', dscp_list)
            if has_v4:
                dscp_mod.Set('OffsetReference',
                             '{}.tosDiffserv.diffServ'.format(pdu_ip.Get('Name')))
            else:
                dscp_mod.Set('OffsetReference',
                             '{}.trafficClass'.format(pdu_ip.Get('Name')))
            dscp_mod.Set('Name', 'DSCP Modifier')
        unique_count = random.randint(1, cmd_dict['max_unique'])
        cmd_dict['last_unique'] = unique_count
        # Ether Modifiers
        ethsrc_mod = ctor.Create('RangeModifier', sb)
        ethsrc_mod.Set('ModifierMode', 'SHUFFLE')
        ethsrc_mod.Set('Mask', '00:00:00:FF:FF:FF')
        ethsrc_mod.Set('StepValue', '00:00:00:00:00:01')
        ethsrc_mod.Set('RecycleCount', unique_count)
        ethsrc_mod.Set('Data', src_mac)
        ethsrc_mod.Set('Offset', 3)
        ethsrc_mod.Set('OffsetReference',
                       '{}.srcMac'.format(pdu_eth.Get('Name')))
        ethdst_mod = ctor.Create('RangeModifier', sb)
        ethdst_mod.Set('ModifierMode', 'SHUFFLE')
        ethdst_mod.Set('Mask', '00:00:00:FF:FF:FF')
        ethdst_mod.Set('StepValue', '00:00:00:00:00:01')
        ethdst_mod.Set('RecycleCount', unique_count)
        ethdst_mod.Set('Data', dst_mac)
        ethdst_mod.Set('Offset', 3)
        ethdst_mod.Set('OffsetReference',
                       '{}.dstMac'.format(pdu_eth.Get('Name')))
        # IP modifiers
        ipsrc_mod = ctor.Create('RangeModifier', sb)
        ipsrc_mod.Set('ModifierMode', 'SHUFFLE')
        ipsrc_mod.Set('Data', burst['SourceAddr'])
        ipsrc_mod.Set('RecycleCount', unique_count)
        ipsrc_mod.Set('Name', 'Source IP Modifier')
        ipdst_mod = ctor.Create('RangeModifier', sb)
        ipdst_mod.Set('ModifierMode', 'SHUFFLE')
        ipdst_mod.Set('Data', burst['DestAddr'])
        ipdst_mod.Set('RecycleCount', unique_count)
        ipdst_mod.Set('Name', 'Dest IP Modifier')
        ipsrc_mod.Set('OffsetReference',
                      '{}.sourceAddr'.format(pdu_ip.Get('Name')))
        ipdst_mod.Set('OffsetReference',
                      '{}.destAddr'.format(pdu_ip.Get('Name')))
        if has_v4:
            ipsrc_mod.Set('Mask', '255.255.255.255')
            ipsrc_mod.Set('StepValue', '0.0.0.1')
            ipdst_mod.Set('Mask', '255.255.255.255')
            ipdst_mod.Set('StepValue', '0.0.0.1')
        else:
            ipsrc_mod.Set('Mask', '::FFFF:FFFF')
            ipsrc_mod.Set('StepValue', '::1')
            ipdst_mod.Set('Mask', '::FFFF:FFFF')
            ipdst_mod.Set('StepValue', '::1')
    amsesb = RelationType('AffiliationManualScheduleEntryStreamBlock')
    sched_entry.AddObject(sb, amsesb)
    return sb, sched_entry


def process_tagged_commands():
    stc_sys = CStcSystem.Instance()
    cmd_list = \
        tag_utils.get_tagged_objects_from_string_names(['Y1564Command'])
    for cmd in cmd_list:
        # For now, just pre-set the capture wrapper to set the capture path
        if cmd.IsTypeOf('CaptureDataSaveCommand'):
            path = os.path.normpath(stc_sys.GetApplicationSessionDataPath())
            cmd.Set('FileNamePath', path)
            cmd.Set('FileName', 'microburst_data.pcap')
            cmd.Set('FileNameFormat', 'PCAP')
            cmd.Set('AppendSuffixToFileName', False)
    return
