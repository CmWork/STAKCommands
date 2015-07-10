from StcIntPythonPL import *
import collections
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.xml_config_utils as xml_utils
import spirent.methodology.utils.data_model_utils as dm_utils


PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateMix, InputJson, AutoExpandTemplate,
             CopiesPerParent, SrcTagList, TargetTagList):
    return ""


def get_prop_val_lists(src_dict, prefix=None):
    '''
    Return the property value lists as expected. The output is usable directly
    in an STC XML save file, meaning the string value is properly formatted
    for a collection property as used in XML (including the errors we have
    with braces)
    '''
    if prefix is None:
        prefix = ''
    else:
        prefix = prefix + '.'
    prop_list = [prefix + k for k in src_dict.keys()]
    val_list = [v if not isinstance(v, collections.Sequence) or
                isinstance(v, str)
                else dm_utils.stcsave_list_to_string(v)
                for v in src_dict.values()]
    return prop_list, val_list


def run_merge(template, tag_prefix, merge_data):
    plLogger = PLLogger.GetLogger('methodology')
    merge_src_tag = merge_data["mergeSourceTag"]
    merge_src_file = merge_data["mergeSourceTemplateFile"]
    merge_target_tag = merge_data["mergeTargetTag"]
    merge_tag_prefix = tag_prefix
    if "mergeTagPrefix" in merge_data.keys():
        merge_tag_prefix = tag_prefix + merge_data["mergeTagPrefix"]

    plLogger.LogDebug("merging from " + merge_src_tag +
                      " in " + merge_src_file + " to " +
                      merge_target_tag + " using " +
                      "merge prefix: " + merge_tag_prefix +
                      " with tag prefix: " + tag_prefix)

    ret_val = False
    # Call the MergeTemplateCommand to merge the templates
    with AutoCommand(PKG + ".MergeTemplateCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        cmd.SetCollection("SrcTagList", [merge_src_tag])
        cmd.SetCollection("TargetTagList", [tag_prefix + merge_target_tag])
        cmd.Set("TagPrefix", merge_tag_prefix)
        cmd.Set("TemplateXmlFileName", merge_src_file)
        cmd.Set("EnableLoadFromFileName", True)
        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
        if not ret_val:
            return False

    # Modify the stuff in the PropertyValueList
    for prop_set in merge_data.get('propertyValueList', []):
        ret_val = run_modify(template, tag_prefix, prop_set, 'run_merge')
        if not ret_val:
            return False

    # Modify the stuff in the StmPropertyModifierList
    for prop_set in merge_data.get('stmPropertyModifierList', []):
        ret_val = run_config_prop_modifier(template, tag_prefix, prop_set)
        if not ret_val:
            return False
    return True


def run_objectlist(template, tag_prefix, obj_data):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("process obj_data: " + str(obj_data))
    class_name = obj_data["className"]
    parent_tag_name = obj_data["parentTagName"]
    tag_name = obj_data["tagName"]
    prop_val_dict = obj_data.get("propertyValueList", {})
    prop_list, val_list = get_prop_val_lists(prop_val_dict)

    ret_val = False
    # Call AddTemplateObjectCommand to modify the template
    with AutoCommand(PKG + ".AddTemplateObjectCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        cmd.Set("ParentTagName", tag_prefix + parent_tag_name)
        cmd.Set("TagName", tag_prefix + tag_name)
        cmd.Set("ClassName", class_name)
        cmd.SetCollection("PropertyList", prop_list)
        cmd.SetCollection("ValueList", val_list)
        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
    return ret_val


def run_modify(template, tag_prefix, mod_data, where='run'):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("process mod_data from {}: {}".format(where, mod_data))
    class_name = mod_data['className']
    tag_name = mod_data['tagName']
    prop_val_dict = mod_data.get('propertyValueList', {})
    prop_list, val_list = get_prop_val_lists(prop_val_dict, class_name)

    ret_val = False
    # Call ModifyTemplatePropertyCommand to modify the template
    with AutoCommand(PKG + ".ModifyTemplatePropertyCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        cmd.SetCollection("PropertyList", prop_list)
        cmd.SetCollection("ValueList", val_list)
        cmd.SetCollection("TagNameList", [tag_prefix + tag_name])
        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
    return ret_val


def run_config_prop_modifier(template, tag_prefix, mod_data):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("process config mod_data: " + str(mod_data))
    class_name = mod_data["className"]
    tag_name = mod_data.get("tagName", "")
    parent_tag_name = mod_data.get("parentTagName", "")
    property_name = mod_data.get("propertyName", "")

    prop_val_dict = mod_data["propertyValueList"]
    start = prop_val_dict["Start"]
    step = prop_val_dict["Step"]
    repeat = prop_val_dict.get("Repeat", [0])
    recycle = prop_val_dict.get("Recycle", [0])
    modifier_type = prop_val_dict.get("ModifierType", "RANGE")
    target_step = prop_val_dict.get("TargetObjectStep", None)
    reset = prop_val_dict.get("ResetOnNewTargetObject", True)

    if isinstance(start, basestring):
        start = [start]
    if isinstance(step, basestring):
        step = [step]
    if isinstance(repeat, int):
        repeat = [repeat]
    if isinstance(recycle, int):
        recycle = [recycle]
    if target_step is not None and isinstance(target_step, basestring):
        target_step = [target_step]

    ret_val = False
    with AutoCommand(PKG + ".ConfigTemplateStmPropertyModifierCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        if tag_name != "":
            cmd.Set("TagName", tag_prefix + tag_name)
        if parent_tag_name != "":
            cmd.Set("TargetObjectTagName", tag_prefix + parent_tag_name)
        cmd.Set("ObjectName", class_name)
        if property_name != "":
            cmd.Set("PropertyName", property_name)
        cmd.Set("ModifierType", modifier_type)
        cmd.SetCollection("StartList", start)
        cmd.SetCollection("StepList", step)
        cmd.SetCollection("RepeatList", repeat)
        cmd.SetCollection("RecycleList", recycle)
        if target_step is not None:
            cmd.SetCollection("TargetObjectStepList", target_step)
        cmd.Set("ResetOnNewTargetObject", reset)

        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
    return ret_val


def run_config_pdu(template, tag_prefix, mod_data):
    plLogger = PLLogger.GetLogger('methodology')
    ele_tag_name = mod_data["templateElementTagName"]
    offset_ref = mod_data["offsetReference"]
    val = mod_data["value"]
    plLogger.LogDebug("Config PDU value, streamblock tag: " +
                      ele_tag_name + " with offset ref: " +
                      offset_ref + " to new value: " + str(val))

    ret_val = False
    with AutoCommand(PKG + ".ConfigTemplatePdusCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        cmd.SetCollection("TemplateElementTagNameList", [tag_prefix + ele_tag_name])
        cmd.SetCollection("PduPropertyList", [offset_ref])
        cmd.SetCollection("PduValueList", [val])
        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
    return ret_val


def run_config_relation(template, tag_prefix, rel_mod):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("process relation: " + str(rel_mod))
    rel_type = rel_mod["relationType"]
    src_tag = rel_mod["sourceTag"]
    target_tag = rel_mod["targetTag"]
    remove_rel = False
    if "removeRelation" in rel_mod.keys():
        remove_rel = rel_mod["removeRelation"]

    ret_val = False
    with AutoCommand(PKG + ".ConfigTemplateRelationCommand") as cmd:
        cmd.Set("StmTemplateConfig", template.GetObjectHandle())
        cmd.Set("SrcTagName", tag_prefix + src_tag)
        cmd.Set("TargetTagName", tag_prefix + target_tag)
        cmd.Set("RelationName", rel_type)
        cmd.Set("RemoveRelation", remove_rel)
        cmd.Execute()
        ret_val = cmd.Get("PassFailState") == "PASSED"
    return ret_val


def run_expand(template, target_tag_list, src_tag_list, copies_per_parent):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("Expand the StmTemplateConfig " + template.Get("Name"))
    result = 'FAILED'
    with AutoCommand(PKG + ".ExpandTemplateCommand") as cmd:
        cmd.SetCollection("StmTemplateConfigList",
                          [template.GetObjectHandle()])
        cmd.SetCollection("TargetTagList", target_tag_list)
        cmd.SetCollection("SrcTagList", src_tag_list)
        cmd.Set("CopiesPerParent", copies_per_parent)
        cmd.Execute()
        result = cmd.Get('PassFailState')
    return result == "PASSED"


def run(StmTemplateMix, InputJson, AutoExpandTemplate,
        CopiesPerParent, SrcTagList, TargetTagList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("CreateTemplateConfigCommand.run")

    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    this_cmd = get_this_cmd()
    project = CStcSystem.Instance().GetObject("Project")

    if InputJson == "":
        err_str = "InputJson is an empty string."
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Validate the InputJson against the schema
    res = json_utils.validate_json(InputJson,
                                   this_cmd.Get("InputJsonSchema"))
    if res != "":
        err_str = "InputJson is invalid or does not conform to the " + \
            "schema: " + res
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    if StmTemplateMix != "" and StmTemplateMix != 0:
        mix = hnd_reg.Find(StmTemplateMix)
        if mix is None:
            err_str = "StmTemplateMix with given handle: " + \
                str(StmTemplateMix) + " is invalid."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False
        elif not mix.IsTypeOf("StmTemplateMix"):
            err_str = "Object with given handle: " + \
                str(StmTemplateMix) + " is a " + \
                mix.GetType() + ".  If StmTemplateMix is " + \
                "specified, object must be an StmTemplateMix."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False
        parent = mix
    else:
        parent = project

    template = ctor.Create("StmTemplateConfig", parent)
    this_cmd.Set("StmTemplateConfig", template.GetObjectHandle())

    # Breakdown the json
    err_str, conf_data = json_utils.load_json(InputJson)
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    plLogger.LogDebug("conf_data: " + str(conf_data))

    # Do the load first
    if "baseTemplateFile" not in conf_data.keys():
        plLogger.LogError("InputJson is missing a baseTemplateFile.")
        return False
    xml_file = conf_data["baseTemplateFile"]

    xml_val = xml_utils.load_xml_from_file(xml_file)
    if xml_val is None:
        err_str = "Was unable to load template XML from " + xml_file
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Update the prefixes
    tag_prefix = ""
    if ("tagPrefix" in conf_data.keys() and conf_data["tagPrefix"] != ""):
        tag_prefix = conf_data["tagPrefix"]
    plLogger.LogDebug("using tag_prefix: " + tag_prefix)

    xml_val = xml_utils.add_prefix_to_tags(tag_prefix, xml_val)
    template.Set("TemplateXml", xml_val)
    plLogger.LogDebug("conf_data: " + str(conf_data))

    # Iterate over the objects in the array and apply the appropriate
    # template modification.  Order is determined by the list order.
    for mod_data in conf_data.get("modifyList", []):
        plLogger.LogDebug("mod_data: " + str(mod_data))
        plLogger.LogDebug("mod_data.keys(): " + str(mod_data.keys()))
        err_str = ""
        res = True

        # Merge stuff in mergeList
        for merge_data in mod_data.get("mergeList", []):
            res = run_merge(template, tag_prefix, merge_data)
            err_str = "Failed to merge XML into the StmTemplateConfig " + \
                "given JSON specified as: " + str(merge_data)

        # Process objects in the addObjectList
        for obj_data in mod_data.get("addObjectList", []):
            res = run_objectlist(template, tag_prefix, obj_data)
            err_str = "Failed to add object into the StmTemplateConfig " + \
                "given JSON specified as: " + str(obj_data)

        # Modify the stuff in the PropertyValueList
        for prop_set in mod_data.get('propertyValueList', []):
            res = run_modify(template, tag_prefix, prop_set)
            err_str = "Failed to modify properties in the " + \
                "StmTemplateConfig given JSON specified as: " + \
                str(prop_set)

        # Modify the stuff in the StmPropertyModifierList
        for prop_set in mod_data.get("stmPropertyModifierList", []):
            res = run_config_prop_modifier(template, tag_prefix, prop_set)
            err_str = "Failed to add or configure " + \
                "StmPropertyModifier objects in the StmTemplateConfig " + \
                "given JSON specified as: " + str(prop_set)

        # Modify PDUs
        for pdu_mod in mod_data.get("pduModifierList", []):
            res = run_config_pdu(template, tag_prefix, pdu_mod)
            err_str = "Failed to modify PDU data in a streamblock's " + \
                "FrameConfig in the StmTemplateConfig given JSON " + \
                "specified as: " + str(pdu_mod)

        # Modify the stuff in the RelationList
        for rel_mod in mod_data.get("relationList", []):
            res = run_config_relation(template, tag_prefix, rel_mod)
            err_str = "Failed to add or remove a relation in the " + \
                "StmTemplateConfig given JSON specified as " + str(rel_mod)

        if not res:
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

    # Handle Expand if necessary
    if AutoExpandTemplate:
        res = run_expand(template, TargetTagList,
                         SrcTagList, CopiesPerParent)
        if not res:
            err_str = "Failed to expand the StmTemplateConfig."
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

    this_cmd.Set("Status", "")
    return True


def reset():
    return True
