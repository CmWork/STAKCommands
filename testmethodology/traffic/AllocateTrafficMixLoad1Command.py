from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.weight_ops as weight


PKG = "spirent.methodology.traffic"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTrafficMix, TagName, Load, LoadUnit):
    return ''


def run(StmTrafficMix, TagName, Load, LoadUnit):
    plLogger = PLLogger.GetLogger("AllocateTrafficMixLoad1Command")
    obj_list = CCommandEx.ProcessInputHandleVec('StmTrafficMix', [StmTrafficMix])
    if TagName:
        obj_list = obj_list + tag_utils.get_tagged_objects_from_string_names([TagName])
    if len(obj_list) == 0:
        plLogger.LogError("Neither StmTrafficMix nor TagName specified " +
                          "a valid StmTrafficMix Object")
        return False
    obj_dict = {obj.GetObjectHandle(): obj for obj in obj_list}
    for traf_mix in obj_dict.values():
        tmi = traf_mix.Get('MixInfo')
        if tmi == '':
            plLogger.LogError("MixInfo is empty")
            return False
        mix_elem = etree.fromstring(tmi)
        val = mix_elem.get('WeightList')
        weight_list = [float(x) for x in val.split()]
        tmpl_list = traf_mix.GetObjects('StmTemplateConfig')
        if len(weight_list) != len(tmpl_list):
            plLogger.LogError("Size of weight list does not match " +
                              "number of templates")
            return False
        # Fractions are not supported only for these settings
        allow = (LoadUnit not in ['FRAMES_PER_SECOND', 'INTER_BURST_GAP'])
        load_list = weight.allocate_weighted_list(Load, weight_list,
                                                  allow_fraction=allow)
        for load, tmpl in zip(load_list, tmpl_list):
            allocate_weighted_load(load, tmpl, LoadUnit)
            config_generator(tmpl, LoadUnit)
        # After finishing, set the appropriate fields in the mix
        mix_elem.set('Load', str(Load))
        mix_elem.set('LoadUnit', LoadUnit)
        mix_elem.set('LoadDist', ' '.join([str(x) for x in load_list]))
        traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    return True


def reset():
    return True


# FIXME:
# Move this to traffic utils.  Also add call to this into expand traffic mix
def config_generator(template, LoadUnit):
    sb_list = template.GetObjects("StreamBlock",
                                  RelationType("GeneratedObject"))
    port_dict = {}
    for sb in sb_list:
        port = sb.GetParent()
        if port.IsTypeOf("Port"):
            port_dict[port.GetObjectHandle()] = port
    for port in port_dict.values():
        gen = port.GetObject("Generator")
        if not gen:
            continue
        gen_conf = gen.GetObject("GeneratorConfig")
        if not gen_conf:
            continue
        if LoadUnit == 'INTER_BURST_GAP' or \
           LoadUnit == 'INTER_BURST_GAP_IN_MILLISECONDS' or \
           LoadUnit == 'INTER_BURST_GAP_IN_NANOSECONDS':
            gen_conf.Set("SchedulingMode", "PRIORITY_BASED")
        else:
            gen_conf.Set("SchedulingMode", "RATE_BASED")


def allocate_weighted_load(load, template, load_unit):
    sb_list = template.GetObjects('StreamBlock',
                                  RelationType('GeneratedObject'))
    for sb in sb_list:
        load_prof = sb.GetObject('StreamBlockLoadProfile',
                                 RelationType('AffiliationStreamBlockLoadProfile'))
        load_prof.Set('LoadUnit', load_unit)
        if load == 0.0:
            sb.Set('Active', False)
            load_prof.Set('Load', 0.01)
        else:
            sb.Set('Active', True)
            load_prof.Set('Load', load)
