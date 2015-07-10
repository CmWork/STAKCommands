from StcIntPythonPL import *
import json
import math
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.weight_ops as weight_ops
import spirent.methodology.utils.json_utils as json_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def get_all_network_blocks(parent, net_block_list):
    if parent.IsTypeOf("NetworkBlock"):
        net_block_list.append(parent)
    for child in parent.GetObjects("Scriptable"):
        get_all_network_blocks(child, net_block_list)


def update_generated_objects(template, route_count):
    gen_obj_list = template.GetObjects("Scriptable",
                                       RelationType("GeneratedObject"))
    if len(gen_obj_list) < 1:
        return ""

    # Assuming that we only expanded one copy per parent, we
    # can figure out the different pieces of the component so that
    # each target object gets the correct route_count
    dev_dict = {}
    for gen_obj in gen_obj_list:
        gen_type = gen_obj.GetType().lower()
        proto = gen_obj.GetParent()
        # Special case: Wizard objects should be ignored, assumption is that
        # generated object ends with "params"
        if proto and proto.IsTypeOf('Project') and \
           (gen_type.endswith('params') or gen_type.endswith('param')):
            continue
        if not proto or not proto.IsTypeOf("ProtocolConfig"):
            return "Could not find a parent ProtocolConfig for " + \
                gen_obj.Get("Name")
        dev = proto.GetParent()
        if not dev or not dev.IsTypeOf("EmulatedDevice"):
            return "Could not find a parent EmulatedDevice for " + \
                proto.Get("Name")
        # Prevent adding wizard-generated objects
        # We need to do it twice for now until we consolidate the BGP-based
        # one with the routing core based one
        param = gen_obj.GetObject('Scriptable',
                                  RelationType('WizardGenerated', True))
        if param is not None:
            continue
        param = gen_obj.GetObject('Scriptable',
                                  RelationType('WizardGeneratedObject', True))
        if param is not None:
            continue
        # We only add the key if there is something to update counts on
        if not dev.GetObjectHandle() in dev_dict.keys():
            dev_dict[dev.GetObjectHandle()] = []
        dev_dict[dev.GetObjectHandle()].append(gen_obj)

    # Distribute the route_count per target object
    # (based on number of target objects...so not all target
    # objects will necessarily get the same count)
    for key in dev_dict.keys():
        # Find all of the network blocks
        net_block_list = []
        for gen_obj in dev_dict[key]:
            get_all_network_blocks(gen_obj, net_block_list)

        if len(net_block_list) < 1:
            return "Could not find any NetworkBlocks to update route counts on."
        # Number of routes we can safely assign every block
        per_block_count = math.floor(route_count / len(net_block_list))

        if per_block_count < 1:
            return "Could not distribute at least one route to each block " + \
                "defined in StmTemplateConfig " + \
                template.Get("Name") + " (" + \
                str(template.GetObjectHandle()) + ")."

        # Number of "extra" routes that will be distributed on a
        # first-come first-serve basis (based on NetworkBlock load/creation)
        remainder = route_count - (per_block_count * len(net_block_list))

        for net_block in net_block_list:
            act_net_count = per_block_count
            if remainder:
                act_net_count = act_net_count + 1
                remainder = remainder - 1
            net_block.Set("NetworkCount", act_net_count)
    return ""


def validate(RouteMixList, RouteMixTagList, RouteCount):
    return ''


def run(RouteMixList, RouteMixTagList, RouteCount):
    plLogger = PLLogger.GetLogger("methodology")
    obj_list = []
    this_cmd = get_this_cmd()
    if RouteMixList:
        obj_list = CCommandEx.ProcessInputHandleVec("StmTemplateMix",
                                                    RouteMixList)
    if RouteMixTagList:
        obj_list = obj_list + \
            tag_utils.get_tagged_objects_from_string_names(
                RouteMixTagList)
    if len(obj_list) == 0:
        err_str = "Neither RouteMixList nor RouteMixTagList specified a " + \
            "valid StmTemplateMix object."
        this_cmd.Set("Status", err_str)
        plLogger.LogError(err_str)
        return False

    if RouteCount < 1:
        err_str = "RouteCount must be at least 1."
        this_cmd.Set("Status", err_str)
        plLogger.LogError(err_str)
        return False

    obj_dict = {obj.GetObjectHandle(): obj for obj in obj_list}
    for mix in obj_dict.values():
        # Get all of the StmTemplateConfig objects for this mix...
        templates = mix.GetObjects("StmTemplateConfig")

        # Get the MixInfo
        str_mix_info = mix.Get("MixInfo")

        # Validate the input MixInfo against its schema
        # res = json_utils.validate_json(str_mix_info,
        #                                get_this_cmd().Get("MixInfoJsonSchema"))
        # if res != "":
        #     this_cmd.Set("Status", res)
        #     plLogger.LogError(res)
        #     return False

        plLogger.LogInfo("string mix_info: " + str(str_mix_info))
        err_str, mix_info = json_utils.load_json(str_mix_info)
        if err_str != "":
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        plLogger.LogInfo("mix_info: " + str(mix_info))
        component_list = mix_info["components"]
        plLogger.LogInfo("number of components: " + str(len(component_list)))

        # Check the MixInfo component_list length against the
        # number of templates
        if len(templates) != len(component_list):
            err_str = "There are " + str(len(templates)) + " under the " + \
                "StmTemplateMix " + mix.Get("Name") + " (" + \
                str(mix.GetObjectHandle()) + ") but " + \
                str(len(component_list)) + \
                " components in the MixInfo.  " + \
                "These MUST match."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Record what we will use over the whole mix
        mix_info["routeCount"] = RouteCount

        # Process the weight parameter
        static_list = []
        percent_list = []
        use_percent_list = []

        for component in component_list:
            weight = component["weight"]
            is_percent, act_val, err_str = weight_ops.parse_weight_string(
                weight)
            if err_str != "":
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

        total_static_count = sum(static_list)
        total_percent = sum(percent_list)

        plLogger.LogDebug("total_static_count: " + str(total_static_count))
        plLogger.LogDebug("total_percent: " + str(total_percent))

        # Don't allow the aggregate of static counts to exceed the
        # configured total route count...
        if total_static_count > RouteCount:
            err_str = "Sum total of the static counts (" + \
                str(int(total_static_count)) + ") exceeds the total " + \
                "configured RouteCount (" + str(RouteCount) + ")."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Don't allow the total percent to exceed 100%
        if total_percent > 100:
            err_str = "Sum total of the weights defined as percentages (" + \
                str(total_percent) + "%) exceeds 100%."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Error if there is no RouteCount left to divide amongst
        # the weighted components (NetworkCount == 0 probably not allowed)
        if total_percent > 0 and total_static_count == RouteCount:
            err_str = "Not enough total RouteCount to distribute routes " + \
                "to all components of the mix.  The required total static " + \
                "route count will use up all of the RouteCount leaving " + \
                "nothing to distribute on the percent-based weighted " + \
                "components."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Calculate how much of the RouteCount is left for the
        # weighted components...
        total_percent_count = RouteCount - total_static_count

        # Check that each percent-based weighted component can get
        # at least 1 route
        if total_percent_count < sum(use_percent_list):
            err_str = "Not enough total RouteCount to distribute routes " + \
                "to all components of the mix.  Once the static counts " + \
                "are handled (if any), there aren't enough routes left (" + \
                str(total_percent_count) + ") such that each " + \
                "percent-based mix component will get at least one route."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Calculate the percent weighted counts from the percents...
        weighted_counts = weight_ops.allocate_weighted_list(
            total_percent_count, percent_list, allow_fraction=False)

        # Apply the counts across each component
        # Assume apply in creation order to map components to templates
        i = 0
        plLogger.LogInfo("weighted_counts: " + str(weighted_counts))
        plLogger.LogInfo("static_list: " + str(static_list))
        for component, template in zip(component_list, templates):
            act_value = 0.0
            if use_percent_list[i]:
                act_value = weighted_counts[i]
            else:
                act_value = static_list[i]

            # Note what we chose to apply and then apply it...
            component["appliedValue"] = act_value

            # Update the NetworkBlocks
            err_str = update_generated_objects(template, act_value)
            if err_str != "":
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False
            i = i + 1

        # Update the mix with our changes...
        mix.Set("MixInfo", json.dumps(mix_info))
    return True


def reset():
    return True
