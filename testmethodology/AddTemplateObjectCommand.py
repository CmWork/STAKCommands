from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import utils.data_model_utils as dm_utils
import utils.xml_config_utils as xml_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfig, ParentTagName, TagName, ClassName,
             PropertyList, ValueList):
    return ""


DM_XML = "DataModelXml"


def run(StmTemplateConfig, ParentTagName, TagName, ClassName,
        PropertyList, ValueList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("run")

    class_name = ClassName

    if len(PropertyList) != len(ValueList):
        return "PropertyList and ValueList must have " + \
            "the same number of elements."

    valid, class_name = dm_utils.validate_classname(class_name)
    if not valid:
        plLogger.LogError("Invalid Class Name " + class_name)
        return False

    prop_val_list = zip(PropertyList, ValueList)

    err_msg, prop_val_list = dm_utils.validate_property_tuple(class_name,
                                                              prop_val_list)
    if err_msg != "":
        plLogger.LogError(err_msg)
        return False

    hnd_reg = CHandleRegistry.Instance()
    template = hnd_reg.Find(StmTemplateConfig)
    if not template.IsTypeOf("StmTemplateConfig"):
        plLogger.LogError("Input StmTemplateConfig is not an " +
                          "StmTemplateConfig")
        return False

    xml_str = template.Get("TemplateXml")
    root = etree.fromstring(xml_str)
    dm_xml_ele_list = root.findall(".//" + DM_XML)
    if len(dm_xml_ele_list) < 1:
        plLogger.LogError("Invalid XML, could not find a " +
                          DM_XML + " element")
        return False
    dm_xml_ele = dm_xml_ele_list[0]
    max_used_id = 0
    for child in dm_xml_ele:
        max_used_id = xml_utils.get_max_object_id(child, max_used_id)

    # Next available id:
    next_id = max_used_id + 1

    # FIXME:
    # Need to guarantee that StcSystem and Project elements exist
    stc_sys_ele = dm_xml_ele.find(".//" + "StcSystem")
    project_ele = dm_xml_ele.find(".//" + "Project")
    tags_ele = dm_xml_ele.find(".//" + "Tags")

    if stc_sys_ele is None or project_ele is None:
        plLogger.LogError("StcSystem or Project elements missing from XML")
        return False

    if tags_ele is None:
        tags_ele = etree.Element("Tags")
        tags_ele.set("id", str(next_id))
        next_id = next_id + 1
        project_ele.append(tags_ele)

    tag_ele = etree.Element("Tag")
    tag_ele.set("id", str(next_id))
    tag_ele.set("Name", TagName)
    tag_ele.set("Active", "TRUE")
    tag_ele.set("LocalActive", "TRUE")
    xml_utils.create_relation_element(tags_ele, "UserTag", str(next_id))
    next_id = next_id + 1
    tags_ele.append(tag_ele)

    # Find a tag with the given name
    # If multiple tags, we'll use the first one that is not a <Tags> element
    parent_tag_id = 0
    for child in tags_ele:
        if child.tag == "Tag":
            if child.get("Name") == ParentTagName:
                parent_tag_id = child.get("id")
    if parent_tag_id == 0:
        plLogger.LogError("Failed to find a Tag with name " + ParentTagName)
        return False

    plLogger.LogInfo("parent tag id: " + str(parent_tag_id))

    # Find the tagged parent to attach the new node onto
    parent_ele_list = xml_utils.find_tagged_elements(stc_sys_ele, parent_tag_id)
    if len(parent_ele_list) == 0:
        plLogger.LogError("Could not find corresponding element with " +
                          "id " + str(parent_tag_id))
        return False

    parent_ele = None
    for ele in parent_ele_list:
        if ele.tag != "Tags":
            parent_ele = ele
            break

    new_ele = etree.Element(class_name)
    new_ele.set("id", str(next_id))
    next_id = next_id + 1
    if TagName is not "":
        # Tag the object
        xml_utils.create_relation_element(new_ele, "UserTag",
                                          tag_ele.get("id"))
    for prop, val in prop_val_list:
        new_ele.set(prop, val)
    parent_ele.append(new_ele)

    plLogger.LogInfo("new xml: " + etree.tostring(root))
    template.Set("TemplateXml", etree.tostring(root))

    return True


def reset():
    return True
