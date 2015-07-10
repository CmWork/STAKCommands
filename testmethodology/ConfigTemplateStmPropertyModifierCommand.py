from StcIntPythonPL import *
import json
import xml.etree.ElementTree as etree
import spirent.methodology.utils.xml_config_utils as xml_utils
import spirent.methodology.utils.data_model_utils as dm_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.template_processing_functions as proc_func


PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def gen_range_modifier_json(classname, prop_name, start, step,
                            repeat=None, recycle=None,
                            target_step=None, reset=None):
    pv_dict = {}
    pv_dict["start"] = start
    pv_dict["step"] = step
    if repeat is not None:
        pv_dict["repeat"] = repeat
    if recycle is not None:
        pv_dict["recycle"] = recycle
    if target_step is not None:
        pv_dict["targetObjectStep"] = target_step
    if reset is not None:
        pv_dict["resetOnNewTargetObject"] = reset

    mod_dict = {}
    mod_dict["objectName"] = classname
    mod_dict["propertyName"] = prop_name
    mod_dict["modifierType"] = "RANGE"
    mod_dict["propertyValueDict"] = pv_dict
    return json.dumps(mod_dict)


def match_modifier_to_obj_and_prop_names(mod_ele, obj_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("match_modifier_to_obj_and_prop_names: " +
                      str(mod_ele) +
                      "  " + str(obj_name) + "  " + str(prop_name))
    if mod_ele is None:
        return "Invalid ElementTree element", None
    mod_info = mod_ele.get("ModifierInfo")
    if mod_info is None:
        return "Missing ModifierInfo attribute", None
    res = json_utils.validate_json(
        mod_info, proc_func.get_range_modifier_json_schema())
    if res != "":
        t_err_str = "Failed to validate ModifierInfo JSON against " + \
            "its schema: " + res
        return t_err_str, None
    err_str, mod_dict = json_utils.load_json(mod_info)
    if err_str != "":
        t_err_str = "Failed to load ModifierInfo JSON: " + \
            err_str
        return t_err_str, None
    plLogger.LogInfo("mod_dict: " + str(mod_dict))
    if obj_name != "":
        mod_obj_name = mod_dict.get("objectName")
        plLogger.LogInfo("mod_obj_name: " + str(mod_obj_name))
        if mod_obj_name == obj_name:
            if prop_name != "":
                mod_prop_name = mod_dict.get("propertyName")
                plLogger.LogInfo("mod_prop_name: " + str(mod_prop_name))
                if mod_prop_name == prop_name:
                    return "", mod_ele
            else:
                # Assume it is what it is as it is tagged
                return "", mod_ele
    elif prop_name != "":
        mod_prop_name = mod_dict.get("propertyName")
        if mod_prop_name == prop_name:
            return "", mod_ele
    else:
        # Assume it is what it is as it is tagged
        return "", mod_ele
    # Didn't match
    return "", None


def find_matching_modifiers(mod_list, obj_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo(" find an StmPropertyModifier to modify...")
    match_list = []
    for mod_ele in mod_list:
        err_str, res = match_modifier_to_obj_and_prop_names(
            mod_ele, obj_name, prop_name)
        if err_str != "":
            return err_str, None
        else:
            if res is not None:
                match_list.append(res)
    return "", match_list


def check_obj_and_prop_names(input_obj_name, input_prop_name):
    obj_name = ""
    # Check the object name
    if input_obj_name != "":
        res, obj_name = dm_utils.validate_classname(input_obj_name)
        if res is False:
            err_str = "Invalid object with ObjectName: " + input_obj_name
            return err_str, input_obj_name, input_prop_name

    # Check the property name with start value
    if obj_name != "":
        if input_prop_name != "":
            prop_list = [prop.lower() for prop in CMeta.GetProperties(obj_name)]
            if input_prop_name.lower() not in prop_list:
                err_str = "Object class " + input_obj_name + \
                    " does not have a property called " + \
                    input_prop_name + "."
                return err_str, input_obj_name, input_prop_name

    # input_prop_name may not exist.  If it does, let validation elsewhere
    # check that it is valid (it will be pulled out of the modifier)
    return "", input_obj_name, input_prop_name


def validate(StmTemplateConfig, TagName, TargetObjectTagName,
             ObjectName, PropertyName, ModifierType,
             StartList, StepList, RepeatList, RecycleList,
             TargetObjectStepList, ResetOnNewTargetObject):
    return ""


def run(StmTemplateConfig, TagName, TargetObjectTagName,
        ObjectName, PropertyName, ModifierType,
        StartList, StepList, RepeatList, RecycleList,
        TargetObjectStepList, ResetOnNewTargetObject):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("ConfigTemplateStmPropertyModifierCommand.start")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    this_cmd = get_this_cmd()

    template = hnd_reg.Find(StmTemplateConfig)
    if template is None:
        err_str = "Invalid or missing StmTemplateConfig"
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False
    if not template.IsTypeOf("StmTemplateConfig"):
        err_str = "Input StmTemplateConfig is not an StmTemplateConfig"
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Check the ModifierType
    if ModifierType != "RANGE":
        err_str = "Unspported ModifierType: " + ModifierType
        this_cmd.Set("Status", err_str)
        return False

    # Validate the ObjectName and PropertyName
    # Note that neither are required if an existing modifier can
    # be modified.  However, both are required if a new modifier
    # is being added.
    err_str, obj_name, prop_name = check_obj_and_prop_names(
        ObjectName, PropertyName)

    plLogger.LogDebug("checked ObjectName: " + str(obj_name))
    plLogger.LogDebug("checked PropertyName: " + str(prop_name))

    # Find the Tag with TagName in the StmTemplateConfig
    mod_ele_list = []
    if TagName != "":
        root = etree.fromstring(template.Get("TemplateXml"))
        tagged_ele_list = xml_utils.find_tagged_elements_by_tag_name(
            root, [TagName], ignore_tags_element=True)

        if len(tagged_ele_list):
            err_str, res_list = find_matching_modifiers(
                tagged_ele_list, obj_name, prop_name)
            if err_str != "":
                this_cmd.Set("Status", err_str)
                return False
            if len(res_list):
                mod_ele_list = res_list

    # If an existing StmPropertyModifier is being modified,
    # nothing is required.  Whatever exists will be updated; whatever
    # doesn't exist will be added.
    # If there is no existing StmPropertyModifier, PropertyName,
    # ObjectName, start, and step are required.
    start_list = []
    step_list = []
    repeat_list = []
    recycle_list = []
    target_step_list = []
    if len(mod_ele_list) == 0:
        plLogger.LogInfo("Add a new StmPropertyModifier on " +
                         ObjectName + "'s " + PropertyName + ".")
        if obj_name == "":
            err_str = "ObjectName is required to add a new " + \
                "StmPropertyModifier with tag name " + TagName + "."
            this_cmd.Set("Status", err_str)
            return False
        if prop_name == "":
            err_str = "PropertyName is required to add a new " + \
                "StmPropertyModifier on " + ObjectName + " with tag name " + \
                TagName + "."
            this_cmd.Set("Status", err_str)

        # StartList
        if StartList is None or StartList == "" or StartList == []:
            err_str = "StartList is required to add a new " + \
                "StmPropertyModifier on " + ObjectName + " property " + \
                PropertyName + " with tag name " + TagName + "."
            this_cmd.Set("Status", err_str)
        else:
            # Check start_list values for validity
            for value in StartList:
                res = dm_utils.validate_obj_prop_val(obj_name,
                                                     prop_name, value)
                if res != "":
                    this_cmd.Set("Status", res)
                    return False
            start_list = StartList

        # StepList
        if StepList is None or StepList == "" or StepList == []:
            err_str = "StepList is required to add a new " + \
                "StmPropertyModifier on " + ObjectName + " property " + \
                PropertyName + " with tag name " + TagName + "."
            this_cmd.Set("Status", err_str)
        else:
            # Check step_list values for validity
            for value in step_list:
                res = dm_utils.validate_obj_prop_val(obj_name,
                                                     prop_name, value)
                if res != "":
                    this_cmd.Set("Status", res)
                    return False
            step_list = StepList

        # RepeatList
        if RepeatList is None or RepeatList == "" or RepeatList == []:
            repeat_list = None
        else:
            repeat_list = RepeatList

        # RecycleList
        if RecycleList is None or RecycleList == "" or RecycleList == []:
            recycle_list = None
        else:
            recycle_list = RecycleList

        # TargetObjectStepList
        if TargetObjectStepList is None or TargetObjectStepList == "" \
           or TargetObjectStepList == []:
            target_step_list = None
        else:
            # Check target_step_list values for validity
            for value in target_step_list:
                res = dm_utils.validate_obj_prop_val(obj_name,
                                                     prop_name, value)
                if res != "":
                    this_cmd.Set("Status", res)
                    return False
            target_step_list = TargetObjectStepList

        # Build the new modifier info
        mod_info = gen_range_modifier_json(
            obj_name, prop_name, start_list, step_list,
            repeat=repeat_list, recycle=recycle_list,
            target_step=target_step_list,
            reset=ResetOnNewTargetObject)

        # Create a new StmPropertyModifier under the elements tagged by
        # TargetObjectTagName
        # Call AddTemplateObjectCommand
        add_cmd = ctor.CreateCommand(PKG + ".AddTemplateObjectCommand")
        add_cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        add_cmd.Set("ParentTagName", TargetObjectTagName)
        add_cmd.Set("TagName", TagName)
        add_cmd.Set("ClassName", "StmPropertyModifier")
        add_cmd.SetCollection("PropertyList", ["ModifierInfo", "TagName"])
        add_cmd.SetCollection("ValueList", [mod_info, TargetObjectTagName])
        add_cmd.Execute()
        add_cmd.MarkDelete()
    else:
        # Get the ObjectName/PropertyName from the existing info
        for mod_ele in mod_ele_list:
            mod_info = mod_ele.get("ModifierInfo")
            err_str, mod_dict = json_utils.load_json(mod_info)
            if err_str != "":
                t_err_str = "Failed to read ModifierInfo out of the " + \
                    "StmTemplateModifier that is being modified: " + \
                    err_str
                this_cmd.Set("Status", t_err_str)
                return False

            plLogger.LogDebug("ModifierInfo json: " + json.dumps(mod_dict))
            if prop_name == "":
                prop_name = mod_dict["propertyName"]
            if obj_name == "":
                obj_name = mod_dict["objectName"]
            plLogger.LogInfo("Found an StmPropertyModifier tagged with " +
                             TagName + " that is modifying " + str(obj_name) +
                             "'s " + str(prop_name) + " to modify.")
            pv_dict = mod_dict["propertyValueDict"]

            # StartList
            if StartList is not None and StartList != "" and StartList != []:
                start_list = StartList
                for value in start_list:
                    res = dm_utils.validate_obj_prop_val(obj_name,
                                                         prop_name, value)
                    if res != "":
                        this_cmd.Set("Status", res)
                        return False
                pv_dict["start"] = start_list

            # StepList
            if StepList is not None and StepList != "" and StepList != []:
                step_list = StepList
                for value in step_list:
                    res = dm_utils.validate_obj_prop_val(obj_name,
                                                         prop_name, value)
                    if res != "":
                        this_cmd.Set("Status", res)
                        return False
                pv_dict["step"] = step_list

            # RepeatList
            if RepeatList is not None and RepeatList != "" \
               and RepeatList != []:
                pv_dict["repeat"] = RepeatList

            # RecycleList
            if RecycleList is not None and RecycleList != "" \
               and RecycleList != []:
                pv_dict["recycle"] = RecycleList

            # TargetObjectStepList
            if TargetObjectStepList is not None and TargetObjectStepList != "" \
               and TargetObjectStepList != []:
                target_step_list = TargetObjectStepList
                for value in target_step_list:
                    res = dm_utils.validate_obj_prop_val(obj_name,
                                                         prop_name, value)
                    if res != "":
                        this_cmd.Set("Status", res)
                        return False
                pv_dict["targetObjectStepList"] = target_step_list

            # Call ModifyTemplatePropertyCommand
            plLogger.LogInfo("call the modify template property command")
            mod_cmd = ctor.CreateCommand(PKG + ".ModifyTemplatePropertyCommand")
            mod_cmd.Set("StmTemplateConfig", template.GetObjectHandle())
            mod_cmd.SetCollection("TagNameList", [TagName])
            mod_cmd.SetCollection("PropertyList",
                                  ["StmPropertyModifier.ModifierInfo"])
            mod_cmd.SetCollection("ValueList", [json.dumps(mod_dict)])
            mod_cmd.Execute()
            mod_cmd.MarkDelete()

    plLogger.LogDebug("ConfigTemplateStmPropertyModifierCommand.end")
    return True


def reset():
    return True
