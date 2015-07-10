from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import utils.xml_config_utils as xml_utils
import utils.template_processing_functions as proc_func
import utils.tag_utils as tag_utils
import utils.data_model_utils as dm_utils
import utils.json_utils as json_utils
import time


PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfigList, CopiesPerParent,
             SrcTagList, TargetTagList):
    return ""


# FIXME: Write a unit test
# Applies the StmModifiers to the generated objects
def apply_modifiers_to_gen_objs(template, time_data):
    template_key = str(template.GetObjectHandle())
    time_data["templates"][template_key]["apply_mods_start"] = time.clock()

    # Recreate the element tree.
    root = etree.fromstring(template.Get("TemplateXml"))
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("ExpandTemplateCommand.apply_modifiers_to_gen_objs.begin")

    # Apply the modifiers to the created objects
    modifier_ele_list = root.findall(".//" + "StmPropertyModifier")
    for modifier_ele in modifier_ele_list:
        # Modifier must contain a type and a tag name
        modifier_info = modifier_ele.get("ModifierInfo")
        plLogger.LogDebug("modifier_info: " + str(modifier_info))

        res = json_utils.validate_json(
            modifier_info, proc_func.get_range_modifier_json_schema())
        if res != "":
            t_err_str = "Failed to validate ModifierInfo JSON against " + \
                "its schema: " + res
            return t_err_str
        err_str, mod_dict = json_utils.load_json(modifier_info)
        if err_str != "":
            t_err_str = "Failed to load ModifierInfo JSON: " + err_str
            return t_err_str
        md_type = mod_dict.get("modifierType")
        plLogger.LogDebug("md_type: " + str(md_type))

        # Call the correct processing function given the type
        if md_type == "RANGE":
            proc_func.apply_range_modifier(template, modifier_ele)

    plLogger.LogDebug("ExpandTemplateCommand.apply_modifiers_to_gen_objs.end")
    time_data["templates"][template_key]["apply_mods_end"] = time.clock()
    time_data["templates"][template_key]["mod_count"] = len(modifier_ele_list)
    return ""


# Updates the elements in the template to set serializationBase
# parameter or unset it based on if the src_tag_list is set.
# SrcTagList (in the command) takes precedence over serializationBase.
# All templates must have something serializable to load.
# Returns a list of element tree elements (the src_obj_list).
def update_template_using_src_tag_list(root, src_tag_list):
    plLogger = PLLogger.GetLogger("methodology")
    src_obj_list = xml_utils.find_tagged_elements_by_tag_name(root,
                                                              src_tag_list)
    if len(src_tag_list) > 0 and len(src_obj_list) < 1:
        plLogger.LogError("Invalid tag names found in SrcTagList " +
                          str(src_tag_list) + ".")
        return []
    if len(src_obj_list) < 1:
        plLogger.LogDebug("No elements tagged in SrcTagList, " +
                          "relying on serializationBase.")
        serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
        if len(serial_ele_list) > 0:
            plLogger.LogDebug("Finding elements marked with the " +
                              "serializationBase parameter.")
            src_obj_list = serial_ele_list
    else:
        # Reset the serializationBase parameters and rebuild
        # the src_obj_list.
        serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
        for ele in serial_ele_list:
            if "serializationBase" in ele.attrib.keys():
                ele.attrib.pop("serializationBase")
        for ele in src_obj_list:
            ele.attrib["serializationBase"] = "true"

    # Tags element must be marked with serializationBase to load
    # Only check if there is anything in the src_obj_list.  If the
    # src_obj_list is empty, let the calling function throw an error.
    # This is to avoid the case where Tags is the only thing marked
    # for load in the template (will work but rather useless).
    if len(src_obj_list) > 0:
        tags_ele = root.find(".//Tags")
        if tags_ele is not None:
            tags_ele.attrib["serializationBase"] = "true"
            if tags_ele not in src_obj_list:
                src_obj_list.append(tags_ele)
    return src_obj_list


def check_load_src_to_target(src_ele_list, target_type):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("check_load_src.start")

    # Handle EmulatedDevice blocks separately first.
    # If there are any EmulatedDevice objects, the
    # target_ele may be a Port.  If it is, set it
    # to project.
    if target_type.lower() == "port":
        for src_ele in src_ele_list:
            if src_ele.tag == "EmulatedDevice":
                target_type = "Project"
    plLogger.LogDebug("target object type: " + str(target_type))

    for src_ele in src_ele_list:
        src_type = src_ele.tag
        plLogger.LogDebug(" process source object type: " + src_type)
        if src_type == "Tags" or src_type == "Tag":
            continue
        res = dm_utils.is_valid_parent(target_type, src_type)
        if not res:
            return target_type + " is not a valid parent for " + \
                src_type + "."
    plLogger.LogDebug("check_load_src.end")
    return ""


def expand_template_configs(template_list, copies_per_parent,
                            src_tag_list, target_obj_list,
                            time_data):
    plLogger = PLLogger.GetLogger("methodology")
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    ctm = CTaskManager.Instance()

    time_data["expand_template_configs_start"] = time.clock()
    time_data["templates"] = {}

    # Process the templates and expand each one
    for template in template_list:
        template_xml = template.Get("TemplateXml")
        if template_xml == "":
            err_str = "Nothing in the TemplateXml for template " + \
                template.Get("Name") + " with handle " + \
                str(template.GetObjectHandle())
            return err_str
        template_key = str(template.GetObjectHandle())
        time_data["templates"][template_key] = {}

        time_tmpl_data = {}
        time_tmpl_data["start"] = time.clock()
        time_tmpl_data["targets"] = {}

        # Pre-process the modifiers and strip them out of the template
        # that will be copied to the target objects
        # Note that the ElementTree representation still has the
        # StmModifiers
        template_xml = xml_utils.strip_modifiers(template_xml)

        # Create an Element tree
        root = etree.fromstring(template_xml)

        # Process the SrcTagList
        # These string names are from the template file
        # If the SrcTagList is empty, look for elements with the
        # serializationBase parameter and use those elements.
        # If there are none of those, throw an error.
        src_obj_list = update_template_using_src_tag_list(root, src_tag_list)
        exclude_tags = \
            sum([1 for x in src_obj_list if x.tag not in ['Tags', 'Tag']])
        if exclude_tags < 1:
            plLogger.LogWarn("Found no elements given a SrcTagList: " +
                             str("SrcTagList") + " and no elements " +
                             "marked with serializationBase=\"true\" " +
                             "in the XML.  " +
                             "Nothing will be expanded.  " +
                             "Please specify the SrcTagList " +
                             "or mark source elements in the template " +
                             "with serializationBase=\"true\"." +
                             "SrcTagList will take precedence.")
            time_data["expand_template_configs_end"] = time.clock()
            return ""
        plLogger.LogDebug("src_obj_list: " + str(src_obj_list))

        # Build the XML input for the LoadFromXmlCommand
        xml_config_string = etree.tostring(root)

        plLogger.LogDebug("xml_config_string: " + str(xml_config_string))

        # Call a LoadXmlCommand for each target
        for target in target_obj_list:
            plLogger.LogDebug(" process target: {} ({}={})"
                              .format(target.Get('Name'), target.GetType(),
                                      target.GetObjectHandle()))
            target_key = str(target.GetObjectHandle())
            time_tmpl_data["targets"][target_key] = {}

            time_target_data = {}
            time_target_data["start"] = time.clock()
            time_target_data["sources"] = {}

            if target.IsTypeOf("Tags") or target.IsTypeOf("Tag"):
                # Skip Tags and Tag
                continue

            res = check_load_src_to_target(src_obj_list, target.GetType())
            if res != "":
                return res

            parent_config = None
            for src in src_obj_list:
                if src.tag == "Tags" or src.tag == "Tag":
                    # Skip Tags and Tag
                    continue
                if src.tag == "EmulatedDevice":
                    # For EmulatedDevices, the parent is actually project
                    # even though the target will be specified as a port.
                    parent_config = project
                else:
                    parent_config = target

            if parent_config is None:
                err = 'Failed to find valid parent config for target {}' \
                    .format(target.Get('Name'))
                return err

            time_src_data = {}
            time_src_data["start"] = time.clock()

            # Load the XML
            cmd = ctor.CreateCommand("LoadFromXml")
            cmd.Set("FileName", "")
            cmd.Set("ParentConfig", parent_config.GetObjectHandle())
            cmd.Set("InputConfigString", xml_config_string)
            cmd.Execute()

            time_src_data["load_from_xml"] = cmd.Get("ElapsedTime")

            # Yield - LoadFromXmlCommand may take a while
            # and doesn't yield while running.
            ctm.CtmYield()
            config = cmd.GetCollection("Config")

            # Enable for debugging (prints all object handles
            # created by load)
            # plLogger.LogDebug("Config: " + str(config))
            cmd.MarkDelete()

            # If parent_config is a project,
            # depending on the type of obj, we'll do some
            # relationship rewiring.  For sources that are
            # EmulatedDevice, we'll add the AffiliationPort relation.
            if parent_config.IsTypeOf("Project"):
                plLogger.LogDebug("parent_config is project")

                yield_ctr = 0
                for hnd in config:
                    obj = hnd_reg.Find(hnd)
                    if obj is None:
                        continue
                    if obj.IsTypeOf("EmulatedDevice"):
                        # Automatically configure the AffiliationPort
                        # relation
                        # Note that target IS a port
                        plLogger.LogDebug("Add the AffiliationPort " +
                                          "relation... dev: " +
                                          str(obj.GetObjectHandle()) +
                                          "  to port: " +
                                          str(target.GetObjectHandle()))
                        port = obj.GetObject(
                            "Port", RelationType("AffiliationPort"))
                        if port is not None:
                            err_str = "Adding the AffiliationPort " + \
                                "relation between device: " + \
                                str(obj.GetObjectHandle()) + \
                                " and port: " + \
                                str(target.GetObjectHandle()) + \
                                " will fail as device already has " + \
                                "AffiliationPort: " + \
                                str(port.GetObjectHandle())
                            plLogger.LogError(err_str)
                        obj.AddObject(
                            target, RelationType("AffiliationPort"))
                        if yield_ctr > 10:
                            yield_ctr = 0
                            ctm.CtmYield()
                        yield_ctr = yield_ctr + 1

            # Add the GeneratedObject relation
            plLogger.LogDebug("Adding the GeneratedObject relation...")
            yield_ctr = 0
            for handle in config:
                # Don't use ProcessInputHandleVec here!
                # (it does not yield)
                obj = hnd_reg.Find(handle)
                if obj is None:
                    plLogger.LogWarn("Object with Handle: " + str(hnd) +
                                     " is invalid.  Skipping configuring " +
                                     " relations on it.")
                    continue
                if obj.IsTypeOf("Tags"):
                    # Skip the Tags object (not valid)
                    continue

                # Print for debugging only if the copies_per_parent
                # is not too large
                if copies_per_parent < 100:
                    plLogger.LogDebug(" config obj: " +
                                      str(obj.Get("Name")))
                template.AddObject(obj, RelationType("GeneratedObject"))

                # Yield every so often
                if yield_ctr > 50:
                    yield_ctr = 0
                    ctm.CtmYield()
                yield_ctr = yield_ctr + 1

            # Update the number of copies using CopiesPerParent
            # All relations set up already should be maintained.
            time_src_data["copy"] = {}

            for hnd in config:
                obj = hnd_reg.Find(hnd)
                if obj is None:
                    plLogger.LogWarn("Object with Handle: " + str(hnd) +
                                     " is invalid.  Skipping copy" +
                                     " expansion.")
                    continue
                if obj.IsTypeOf("Tags") or obj.IsTypeOf("Tag"):
                    # Skip the Tags object (not valid to copy)
                    continue

                copy_time = 0
                copy_count = copies_per_parent - 1
                if copy_count > 0:
                    cmd = ctor.CreateCommand("CopyCommand")
                    cmd.SetCollection("SrcList", [hnd])
                    cmd.Set("DstList",
                            obj.GetParent().GetObjectHandle())
                    cmd.Set("RepeatCount", copy_count)
                    cmd.Execute()
                    plLogger.LogInfo("CopyCommand ElapsedTime: " +
                                     str(cmd.Get("ElapsedTime")))
                    copy_time = cmd.Get("ElapsedTime")
                    copy_hnd_list = cmd.GetCollection("ReturnList")
                    for copy_hnd in copy_hnd_list:
                        copy = hnd_reg.Find(copy_hnd)
                        if not copy:
                            continue
                        source_template = copy.GetObject(
                            "StmTemplateConfig",
                            RelationType("GeneratedObject", 1))
                        if source_template is None:
                            # Add the missing relation - apparently
                            # the CopyCommand doesn't always copy this
                            # relation.
                            template.AddObject(copy,
                                               RelationType("GeneratedObject"))
                    cmd.MarkDelete()

                time_src_data["copy"][str(hnd)] = copy_time
                time_src_data["end"] = time.clock()

                time_target_data["sources"][src.get("Name")] = time_src_data

            time_target_data["end"] = time.clock()
            time_tmpl_data["targets"][target_key] = time_target_data
        time_tmpl_data["end"] = time.clock()

        # Apply the StmModifiers
        plLogger.LogDebug("Calling apply_modifiers_to_gen_objs...")
        err_str = apply_modifiers_to_gen_objs(template, time_data)
        if err_str != "":
            t_err_str = "Failed to apply StmPropertyModifiers to generated " + \
                "objects: " + err_str
            plLogger.LogError(t_err_str)
            return err_str

        time_data["templates"][template_key] = time_tmpl_data
        time_data["templates"][template_key]["end"] = time.clock()

    time_data["expand_template_configs_end"] = time.clock()
    return ""


def run(StmTemplateConfigList, CopiesPerParent,
        SrcTagList, TargetTagList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run ExpandTemplateCommand")

    time_data = {}
    time_data["cmd_start"] = time.clock()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    this_cmd = get_this_cmd()

    template_list = []
    obj_list = CCommandEx.ProcessInputHandleVec("StmTemplateConfig",
                                                StmTemplateConfigList)
    for obj in obj_list:
        if obj is not None and obj not in template_list:
            template_list.append(obj)

    if not len(template_list):
        err_str = "Could not find any valid StmTemplateConfig objects."
        this_cmd.Set("Status", err_str)
        plLogger.LogError(err_str)
        return False
    time_data["template_list_len"] = len(template_list)

    # Process the TargetTagList
    # Since it is string names, convert to a list of bll objects
    # An empty TargetTagList indicates the target is project
    target_obj_list = []
    if len(TargetTagList) == 0:
        plLogger.LogDebug("TargetTagList is empty so project will be " +
                          "used as the attachment target.")
        target_obj_list = [project]
    else:
        # This is only used for checking if each tag actually tags anything
        for target_tag in TargetTagList:
            obj_list = tag_utils.get_tagged_objects_from_string_names(
                target_tag)
            if len(obj_list) < 1:
                err_str = "TargetTagList contains invalid tags " + \
                    "or tags that don't tag anything."
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False
        target_obj_list = tag_utils.get_tagged_objects_from_string_names(
            TargetTagList)
    if len(target_obj_list) < 1:
        err_str = "TargetTagList contains invalid tags " + \
            "or tags that don't tag anything."
        this_cmd.Set("Status", err_str)
        return False

    plLogger.LogDebug("target_obj_list: ")
    for obj in target_obj_list:
        plLogger.LogDebug("  target: " + obj.Get("Name"))

    if len(template_list) > 0:
        plLogger.LogDebug("call expand_template_configs")
        res = expand_template_configs(template_list,
                                      CopiesPerParent,
                                      SrcTagList,
                                      target_obj_list,
                                      time_data)
        if res != "":
            err_str = "Failed to expand template(s): " + res
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

    # Remove duplicate tags from the copies
    cmd = ctor.CreateCommand("RemoveDuplicateTagsCommand")
    cmd.Execute()
    time_data["rem_dup_tags_cmd"] = cmd.Get("ElapsedTime")
    cmd.MarkDelete()

    time_data["cmd_end"] = time.clock()
    print_time_data(time_data)

    return True


def print_time_data(time_data):
    total = time_data["cmd_end"] - time_data["cmd_start"]
    exp_tmpl_cfg = time_data["expand_template_configs_end"] - \
        time_data["expand_template_configs_start"]
    rem_dup_tags = float(time_data["rem_dup_tags_cmd"]) / 1000.0
    num_tmpls = time_data["template_list_len"]

    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo(PKG + ".ExpandTemplateCommand Timing Data")
    plLogger.LogInfo(" Template Count: " + str(num_tmpls))
    plLogger.LogInfo(" Total Time: " + str(total) + " s")
    plLogger.LogInfo(" expand_template_configs: " + str(exp_tmpl_cfg) + " s")
    plLogger.LogInfo(" remove duplicate tags: " + str(rem_dup_tags) + " s")
    total_xml_load = 0
    total_copy_cmd = 0

    for key in time_data["templates"].keys():
        template = time_data["templates"][key]
        if not template:
            continue
        t_total = template["end"] - template["start"]
        mod_total = 0
        if "apply_mods_end" in template.keys():
            mod_total = template["apply_mods_end"] - \
                template["apply_mods_start"]
        plLogger.LogInfo(" -- Template (" + str(key) + ")")
        plLogger.LogInfo("  Time: " + str(t_total))
        plLogger.LogInfo("  StmPropertyModifier total: " + str(mod_total))

        for target_key in template["targets"].keys():
            target = template["targets"][target_key]
            tgt_total = target["end"] - target["start"]
            plLogger.LogInfo("   -> target " + str(target_key))
            plLogger.LogInfo("     Time: " + str(tgt_total))
            for source_key in target["sources"].keys():
                source = target["sources"][source_key]
                src_total = source["end"] - source["start"]
                load = float(source["load_from_xml"]) / 1000.0
                plLogger.LogInfo("     load: " + str(load))
                total_xml_load = total_xml_load + load
                copy_total = 0
                for copy_key in source["copy"].keys():
                    copy = source["copy"][copy_key] / 1000.0
                    plLogger.LogInfo("    copy: " + str(copy_key) +
                                     "  " + str(copy))
                    copy_total = copy_total + copy
                total_copy_cmd = total_copy_cmd + copy_total
                plLogger.LogInfo("      -> source " + str(source_key))
                plLogger.LogInfo("        Time:  " + str(src_total))
                plLogger.LogInfo("        LoadFromXml: " + str(load))
                plLogger.LogInfo("        Copy: " + str(copy_total))
        plLogger.LogInfo("  Total LoadFromXml: " + str(total_xml_load))
        plLogger.LogInfo("  Total CopyCommand: " + str(total_copy_cmd))


def reset():
    return True
