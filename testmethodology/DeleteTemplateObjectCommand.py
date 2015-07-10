from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import utils.data_model_utils as dm_utils
import utils.xml_config_utils as xml_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfig, TagName, ClassName):
    # FIXME:
    # Determine that ClassName is a real STC class

    return ""


def run(StmTemplateConfig, TagName, ClassName):
    plLogger = PLLogger.GetLogger('methodology')

    hnd_reg = CHandleRegistry.Instance()
    template = hnd_reg.Find(StmTemplateConfig)
    if not template.IsTypeOf("StmTemplateConfig"):
        plLogger.LogError("ERROR: Input StmTemplateConfig is not an " +
                          "StmTemplateConfig")
        return False
    valid, ClassName = dm_utils.validate_classname(ClassName)
    if not valid:
        plLogger.LogError("Invalid Class Name " + class_name)
        return False
    xml_str = template.Get("TemplateXml")
    root = etree.fromstring(xml_str)

    # Find the tag IDs
    tag_ele = xml_utils.find_tag_elements(root, TagName)
    if tag_ele is None:
        plLogger.LogError("ERROR: Could not find a " + TagName +
                          " in the template XML")
        return False
    tag_id = tag_ele[0].get("id")

    tagged_ele_list = xml_utils.find_tagged_elements(root, tag_id)
    if len(tagged_ele_list) == 0:
        plLogger.LogWarn("Could not find a element tagged with " +
                         SourceTag + " in the template XML")
        return False
    for tagged_ele in tagged_ele_list:
        # Remove the tagged element and all of its children
        if tagged_ele.tag == ClassName:
            parent = xml_utils.get_parent(root, tagged_ele)
            if parent is not None:
                parent.remove(tagged_ele)

    template.Set("TemplateXml", etree.tostring(root))

    return True


def reset():
    return True
