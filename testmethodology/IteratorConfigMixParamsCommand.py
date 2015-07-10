from StcIntPythonPL import *
import json
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils

PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateMix, TagData, ObjectList,
             IgnoreEmptyTags, TagList, CurrVal, Iteration):
    return ""


def run(StmTemplateMix, TagData, ObjectList,
        IgnoreEmptyTags, TagList, CurrVal, Iteration):
    '''
        StmTemplateMix: Handle of StmTemplateMix Object
        TagData: JSON String of Tags Needed in Sequence
        ObjectList: (from Base Class)
        IgnoreEmptyTags: (from Base Class)
        TagList: (from Base Class)
        CurrVal: Current Row Index (from Base Class)
        Iteration: (from Base Class)
    '''
    hnd_reg = CHandleRegistry.Instance()
    plLogger = PLLogger.GetLogger("Methodology")

    # Check Mandatory Arguments
    if (StmTemplateMix is None) or (StmTemplateMix == ""):
        plLogger.LogError("StmTemplateMix is a mandatory argument for " +
                          "IteratorConfigMixParamsCommand.")
        return False
    if (TagData is None) or (TagData == ""):
        plLogger.LogError("TagData is a mandatory argument for " +
                          "IteratorConfigMixParamsCommand.")
        return False

    err_str, tag_data = json_utils.load_json(TagData)
    if err_str != "":
        plLogger.LogError(err_str)
        return False

    # MixInfo in StmTemplateMix contains JSON String of Input Table
    mix_obj = hnd_reg.Find(StmTemplateMix)
    if mix_obj is None:
        plLogger.LogError("No objects with handle, " +
                          str(StmTemplateMix) +
                          ", found.")
        return False
    elif not mix_obj.IsTypeOf("StmTemplateMix"):
        plLogger.LogError(str(StmTemplateMix) +
                          " does not refer to a StmTemplateMix object.")
        return False

    # Fetch the json string from the MIX object...
    mix_info_json = mix_obj.Get("MixInfo")

    # Validate the json against its schema...
    res = json_utils.validate_json(mix_info_json, get_this_cmd().Get('MixJsonSchema'))
    if res != '':
        plLogger.LogError(res)
        return False

    # Load the json information...
    err_str, mix_info = json_utils.load_json(mix_info_json)
    if err_str != "":
        plLogger.LogError(err_str)
        return False
    components = mix_info["components"]

    # Get row by matching index (CurrVal) with TableData
    row = components[int(CurrVal)]
    # DEBUG PRINT
    plLogger.LogDebug("component " + str(CurrVal) + ":")
    for property in row:
        plLogger.LogDebug("   " + str(property) + " = " + str(row[property]))

    # Setup CreateTemplateConfigCommand
    temp_conf_tag_name = tag_data["templateConfigurator"]
    tagged_obj_list = tag_utils.get_tagged_objects_from_string_names([temp_conf_tag_name])
    if len(tagged_obj_list) == 0:
        plLogger.LogError("No objects tagged with " +
                          str(temp_conf_tag_name) +
                          " tag name.")
        return False

    create_temp_cfg_cmd = tagged_obj_list[0]
    create_temp_cfg_cmd.Set("StmTemplateMix", StmTemplateMix)
    create_temp_cfg_cmd.Set("InputJson", json.dumps(row))
    create_temp_cfg_cmd.Set("AutoExpandTemplate", False)

    return True


def reset():
    return True
