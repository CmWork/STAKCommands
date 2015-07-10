from StcIntPythonPL import *
import json
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.weight_ops as weight_ops


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTrafficMix, TrafficMixTagName, Load, LoadUnit):
    return ''


def run(StmTrafficMix, TrafficMixTagName, Load, LoadUnit):
    plLogger = PLLogger.GetLogger('AllocateTrafficMixLoad2Command')
    obj_list = []
    this_cmd = get_this_cmd()
    if StmTrafficMix:
        obj_list = CCommandEx.ProcessInputHandleVec('StmTrafficMix', [StmTrafficMix])
    if TrafficMixTagName:
        obj_list = obj_list + tag_utils.get_tagged_objects_from_string_names([TrafficMixTagName])
    if len(obj_list) == 0:
        err_str = "Neither StmTrafficMix nor TrafficMixTagName " + \
            "specified a valid StmTrafficMix Object"
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    obj_dict = {obj.GetObjectHandle(): obj for obj in obj_list}
    for mix in obj_dict.values():
        mix_info_s = mix.Get('MixInfo')

        # Validate the input MixInfo against its schema
        res = json_utils.validate_json(mix_info_s,
                                       this_cmd.Get('MixInfoJsonSchema'))
        if res != '':
            plLogger.LogError(res)
            this_cmd.Set("Status", res)
            return False

        err_str, mix_info = json_utils.load_json(mix_info_s)
        if err_str != "":
            plLoger.LogError(err_str)

        component_list = mix_info['components']

        # Record what we will use MIX wide...
        mix_info['load'] = Load
        mix_info['loadUnits'] = LoadUnit

        # Aggregate the individual streamblock information...
        static_list = []
        percent_list = []
        use_percent_list = []

        for component in component_list:
            weight = component["weight"]
            is_percent, act_val, err_str = \
                weight_ops.parse_weight_string(weight)
            if err_str != "":
                err_str = "Total static loads exceed the mix load."
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False

            if is_percent:
                static_list.append(0)
                percent_list.append(act_val)
            else:
                static_list.append(act_val)
                percent_list.append(0)
            use_percent_list.append(is_percent)

        total_static_load = sum(static_list)
        total_percent = sum(percent_list)

        # Don't allow the aggregate of static loads to exceed the MIX wide load...
        if total_static_load > Load:
            err_str = 'Total static load ({}) exceeds the ' \
                'configured mix load ({}).'.format(total_static_load, Load)
            plLogger.LogError(err_str)
            this_cmd.Set('Status', err_str)
            return False

        # Don't allow an invalid aggregate of streamblock weights...
        if total_percent > 100:
            err_str = "Total weights ({}) exceed 100%.".format(total_percent)
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Warn if there is no MIX wide load left to divide amongst the
        # weighted streamblocks...
        if total_percent > 0 and total_static_load == Load:
            err_str = 'No mix load available for weight distribution'
            plLogger.LogWarn(err_str)
            this_cmd.Set("Status", err_str)

        # Fractions are not supported only for these settings
        allow = (LoadUnit not in ['FRAMES_PER_SECOND', 'INTER_BURST_GAP'])

        # Calculate how much of the load is left for the weighted streamblocks...
        total_weighted_load = Load - total_static_load

        # Calculate the weighted loads from the weights...
        weighted_loads = weight_ops.allocate_weighted_list(total_weighted_load,
                                                           percent_list,
                                                           allow_fraction=allow)

        # Get all of the StmTemplateConfig objects for this MIX...
        templates = mix.GetObjects('StmTemplateConfig')

        # Apply the loads across each streamblock according to their individual preferences...
        # Yes, we are ASSUMING creation order to map components to templates...
        for component, template, weight_load in zip(component_list, templates, weighted_loads):
            is_percent, act_val, err_str = \
                weight_ops.parse_weight_string(component['weight'])
            if not is_percent:
                applied_load = act_val
            else:
                applied_load = weight_load

            # Note what we chose to apply and then apply it...
            component['appliedValue'] = applied_load
            allocate_weighted_load(applied_load, template, LoadUnit)
            config_generator(template, LoadUnit)

        # Update the MIX with our changes...
        mix.Set('MixInfo', json.dumps(mix_info))
    return True


def reset():
    return True


# FIXME:
# Move this to traffic utils.  Also add call to this into expand traffic mix
def config_generator(template, LoadUnit):
    sb_list = template.GetObjects('StreamBlock',
                                  RelationType('GeneratedObject'))
    port_dict = {}
    for sb in sb_list:
        port = sb.GetParent()
        if port.IsTypeOf('Port'):
            port_dict[port.GetObjectHandle()] = port
    for port in port_dict.values():
        gen = port.GetObject('Generator')
        if not gen:
            continue
        gen_conf = gen.GetObject('GeneratorConfig')
        if not gen_conf:
            continue
        if LoadUnit == 'INTER_BURST_GAP' or \
           LoadUnit == 'INTER_BURST_GAP_IN_MILLISECONDS' or \
           LoadUnit == 'INTER_BURST_GAP_IN_NANOSECONDS':
            gen_conf.Set('SchedulingMode', 'PRIORITY_BASED')
        else:
            gen_conf.Set('SchedulingMode', 'RATE_BASED')


def adjust_load_and_load_unit(load, load_unit):
    print load, load_unit
    if load >= 1.0:
        return load, load_unit

    new_load_unit = load_unit
    multiplier = 1000.0
    if load_unit == 'MEGABITS_PER_SECOND':
        new_load_unit = 'KILOBITS_PER_SECOND'
    elif load_unit == 'KILOBITS_PER_SECOND':
        new_load_unit = 'BITS_PER_SECOND'
    else:
        multiplier = 1.0

    return load*multiplier, new_load_unit


def allocate_weighted_load(load, template, load_unit):
    sb_list = template.GetObjects('StreamBlock',
                                  RelationType('GeneratedObject'))

    load, load_unit = adjust_load_and_load_unit(load, load_unit)
    for sb in sb_list:
        load_prof = sb.GetObject('StreamBlockLoadProfile',
                                 RelationType('AffiliationStreamBlockLoadProfile'))
        load_prof.Set('LoadUnit', load_unit)
        if load == 0.0:
            sb.Set('Active', False)
            load_prof.Set('Load', 0.01)
        else:
            sb.Set('Active', True)
            load_prof.Set('Load', float(load))
