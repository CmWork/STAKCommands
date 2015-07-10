from StcIntPythonPL import *
import json
import spirent.methodology.utils.weight_ops as weight_ops
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateMix, TagName, DeviceCount, PortGroupTagList):
    # plLogger = PLLogger.GetLogger("ExpandTrafficMixCommand")
    # this_cmd = get_this_cmd()
    return ""


# FIXME: handle lists of StmTemplateMix objects?
def run(StmTemplateMix, TagName, DeviceCount, PortGroupTagList):
    # MixInfo JSON:
    # {
    #     "deviceCount": 100,
    #     "components": [
    #         {
    #             "weight": 10.0,
    #             "devicesPerBlock": 0,
    #             "baseTemplateFile": "IPv4_NoVlan.xml",
    #             "appliedValue": 0
    #         }
    #     ]
    # }
    plLogger = PLLogger.GetLogger("methodology")
    ctor = CScriptableCreator()
    obj_list = []
    this_cmd = get_this_cmd()
    if StmTemplateMix:
        obj_list = CCommandEx.ProcessInputHandleVec("StmTemplateMix",
                                                    [StmTemplateMix])
    if TagName:
        obj_list = obj_list + \
            tag_utils.get_tagged_objects_from_string_names(
                [TagName])
    if len(obj_list) == 0:
        err_str = "Neither StmTemplateMix nor TagName specified a " + \
            "valid StmTemplateMix object."
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    if DeviceCount < 1:
        err_str = "DeviceCount must be at least 1."
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Process obj_list to remove duplicates by using
    # a dictionary indexed on object handle.
    obj_dict = {obj.GetObjectHandle(): obj for obj in obj_list}
    for mix in obj_dict.values():
        str_mix_info = mix.Get("MixInfo")
        if str_mix_info == "":
            err_str = "MixInfo is empty"
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        '''
        # Validate the MixInfo
        # mi_schema = CreateProtoMixCmd_get_mix_info_schema()
        # err_str, res = json_utils.validate_json(str_mix_info, mi_schema)
        # if err_str != "":
            # plLogger.LogError(err_str)
            # this_cmd.Set("Status", err_str)
            # return False
        '''

        plLogger.LogDebug("string mix_info: " + str_mix_info)
        err_str, mix_info = json_utils.load_json(str_mix_info)
        if err_str != "":
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False
        plLogger.LogDebug("mix_info: " + str(mix_info))

        if "components" not in mix_info.keys():
            err_str = "components is missing in MixInfo for " + \
                "StmProtocolMix: " + mix.Get("Name")
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        component_list = mix_info["components"]
        if len(component_list) == 0:
            err_str = "Could not find any objects in components in " + \
                "the MixInfo in " + mix.Get("Name")
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        template_list = mix.GetObjects("StmTemplateConfig")
        if len(component_list) != len(template_list):
            err_str = "Number of component elements in the " + \
                "MixInfo for " + mix.Get("Name") + \
                ": " + str(len(component_list)) + ", " + \
                "does not match number of StmTemplateConfig objects " + \
                ": " + str(len(template_list)) + "."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Check the DeviceCount
        if DeviceCount < len(component_list):
            err_str = "Invalid DeviceCount " + str(DeviceCount) + \
                " specified.  DeviceCount must be at " + \
                " least " + str(len(component_list))
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Process the weight parameter
        static_list = []
        percent_list = []
        use_percent_list = []

        for component in component_list:
            if "weight" not in component.keys():
                err_str = "Missing required weight parameter in " + \
                    "Component in StmProtocolMix: " + mix.Get("Name")
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False
            weight = component["weight"]
            is_percent, act_val, err_str = weight_ops.parse_weight_string(weight)
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
        # configured total device count...
        if total_static_count > DeviceCount:
            err_str = "Sum total of the static counts (" + \
                str(int(total_static_count)) + ") exceeds the total " + \
                "configured DeviceCount (" + str(DeviceCount) + ")."
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

        # Error if there is no DeviceCount left to divide amongst
        # the weighted components (NetworkCount == 0 probably not allowed)
        if total_percent > 0 and total_static_count == DeviceCount:
            err_str = "Not enough total DeviceCount to distribute devices " + \
                "to all components of the mix.  The required total static " + \
                "device count will use up all of the DeviceCount leaving " + \
                "nothing to distribute on the percent-based weighted " + \
                "components."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Calculate how much of the DeviceCount is left for the
        # weighted components...
        total_percent_count = DeviceCount - total_static_count

        # Check that each percent-based weighted component can get
        # at least 1 device
        if total_percent_count < sum(use_percent_list):
            err_str = "Not enough total DeviceCount to distribute devices " + \
                "to all components of the mix.  Once the static counts " + \
                "are handled (if any), there aren't enough devices left (" + \
                str(total_percent_count) + ") such that each " + \
                "percent-based mix component will get at least one device."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

        # Calculate the percent weighted counts from the percents...
        weighted_counts = weight_ops.allocate_weighted_list(
            total_percent_count, percent_list, allow_fraction=False)

        # Apply the counts across each component
        # Assume apply in creation order to map components to templates
        i = 0
        final_device_count = 0
        plLogger.LogInfo("weighted_counts: " + str(weighted_counts))
        plLogger.LogInfo("static_list: " + str(static_list))
        for component, template in zip(component_list, template_list):
            act_value = 0.0
            if use_percent_list[i]:
                act_value = weighted_counts[i]
            else:
                act_value = static_list[i]

            # Note what we chose to apply and then apply it...
            component["appliedValue"] = act_value
            final_device_count += act_value
            i = i + 1

            if "devicesPerBlock" not in component.keys():
                err_str = "Missing required devicesPerBlock parameter in " + \
                    "Component in StmProtocolMix: " + mix.Get("Name")
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False

            dev_per_block = component["devicesPerBlock"]
            plLogger.LogDebug("Template: " + template.Get("Name"))
            plLogger.LogDebug("dev_count: " + str(act_value))
            plLogger.LogDebug("devicesPerBlock: " + str(dev_per_block))

            last_block_count = 0
            if dev_per_block == 0 or dev_per_block > act_value:
                # All devices into one block
                block_dev_count = act_value
                copies_per_parent = 1
            else:
                # (Greedily) Fill device block with number of devices
                # specified by devicesPerBlock.  Last block will have
                # remainder of devices that does not fill a complete block.
                block_dev_count = dev_per_block
                copies_per_parent = int(act_value // dev_per_block)
                last_block_count = int(act_value % dev_per_block)

            if last_block_count > 0:
                copies_per_parent += 1

            plLogger.LogDebug("block_dev_count: " + str(block_dev_count))
            plLogger.LogDebug("copies_per_parent: " + str(copies_per_parent))
            plLogger.LogDebug("last_block_count: " + str(last_block_count))

            # Call ExpandTemplateConfigCommand
            cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
            cmd.SetCollection("StmTemplateConfigList", [template.GetObjectHandle()])
            cmd.Set("CopiesPerParent", copies_per_parent)
            cmd.SetCollection("TargetTagList", PortGroupTagList)
            cmd.Execute()
            cmd.MarkDelete()

            emul_dev_list = template.GetObjects("emulateddevice", RelationType("GeneratedObject"))
            for emul_dev in emul_dev_list:
                # Last Block has remainder AND last emulateddevice in list
                if (last_block_count > 0) and \
                   (emul_dev.GetObjectHandle() == emul_dev_list[-1].GetObjectHandle()):
                    emul_dev.Set("DeviceCount", last_block_count)
                else:
                    emul_dev.Set("DeviceCount", block_dev_count)

    mix_info["deviceCount"] = final_device_count

    # Write the MixInfo back to the StmProtocolMix
    plLogger.LogDebug("dumping back into MixInfo: " +
                      json.dumps(mix_info))
    mix.Set("MixInfo", json.dumps(mix_info))

    return True


def reset():
    return True
