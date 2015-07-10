from StcIntPythonPL import *
import spirent.methodology.utils.xml_config_utils as xml_utils
import xml.etree.ElementTree as etree


PKG = "spirent.methodology"


# FIXME: write a unit test
def find_tagged_filtered_elements(root, tag_list,
                                  ignore_tags_obj=True):
    ele_list = xml_utils.find_tagged_elements_by_tag_name(root,
                                                          tag_list)
    if ele_list is None:
        return []
    if ignore_tags_obj:
        # Remove the Tags element as it has a UserTag relation
        # to each of the Tag objects that will cause it to
        # appear to be tagged
        filtered_ele_list = []
        for ele in ele_list:
            if ele.tag != "Tags":
                filtered_ele_list.append(ele)
        return filtered_ele_list
    return ele_list


# FIXME: write a unit test
# Updates the target ids with the new ones
# given in the id_map (map is of old to new ids)
def update_relation_targets(root, id_map):
    rel_ele_list = root.findall(".//Relation")
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("rel_ele_list contains: " + str(rel_ele_list))
    for rel_ele in rel_ele_list:
        if rel_ele.get("type") == "UserTag" and \
           rel_ele.get("target") in id_map.keys():
            plLogger.LogInfo(" setting new tag target...")
            rel_ele.set("target",
                        str(id_map[rel_ele.get("target")]))


# FIXME: write a unit test
# Updates the StmPropertyModifier object's TagName
# with the new names given in the name_map
# (map of old names to new names)
def update_property_modifier_tag_names(root, name_map):
    plLogger = PLLogger.GetLogger('methodology')
    mod_ele_list = root.findall(".//StmPropertyModifier")
    plLogger.LogInfo("mod_ele_list contains: " + str(mod_ele_list))
    for mod_ele in mod_ele_list:
        if mod_ele.get("TagName") in name_map.keys():
            mod_ele.set("TagName",
                        name_map[mod_ele.get("TagName")])


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfig, SrcTagList, TargetTagList,
             TagPrefix, TemplateXml, TemplateXmlFileName,
             EnableLoadFromFileName):
    # plLogger = PLLogger.GetLogger('methodology')
    return ""


def run(StmTemplateConfig, SrcTagList, TargetTagList,
        TagPrefix, TemplateXml, TemplateXmlFileName,
        EnableLoadFromFileName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run MergeTemplateCommand")

    hnd_reg = CHandleRegistry.Instance()
    temp_conf = hnd_reg.Find(StmTemplateConfig)

    if temp_conf is None:
        plLogger.LogError("ERROR: Failed to find a valid StmTemplateConfig")
        return False

    # Get the template XML (target XML) and renormalize the IDs
    template = temp_conf.Get("TemplateXml")
    target_root = etree.fromstring(template)

    # FIXME:
    # RENORMALIZE must ALSO remove invalid relations and potentially invalid
    # property values (for type handle).  Otherwise, renumbering the objects
    # may end up relating things that shouldn't be related.
    # Example:
    # <Relation type="DefaultSelection" target="15"/>
    #  Object with ID 15 doesn't exist if the XML was stripped incorrectly
    #  but it will probably exist when the objects are renumbered.

    xml_utils.renormalize_xml_obj_ids(target_root)

    # Get the new current object ID (1 + maximum object ID)
    curr_id = xml_utils.get_max_object_id(target_root, 0) + 1

    # Find the target elements
    target_ele_list = find_tagged_filtered_elements(target_root,
                                                    TargetTagList)
    if len(target_ele_list) < 1:
        plLogger.LogError("Found no target elements in the " +
                          "StmTemplateConfig in to which the " +
                          "new XML should be merged into.")
        return False

    # Get the source XML
    merge_xml = None
    if not EnableLoadFromFileName:
        merge_xml = TemplateXml
        if merge_xml == "":
            plLogger.LogError("No valid XML Template String defined.")
            return False
    elif TemplateXmlFileName != "":
        merge_xml = xml_utils.load_xml_from_file(TemplateXmlFileName)
        if merge_xml is None:
            plLogger.LogError("No valid XML Template File defined.")
            return False

    source_root = etree.fromstring(merge_xml)

    # Find the source elements
    src_ele_list = find_tagged_filtered_elements(source_root,
                                                 SrcTagList)
    if len(src_ele_list) < 1:
        plLogger.LogError("Found no source elements in the input XML " +
                          "from which XML should be copied into the " +
                          "StmTemplateConfig from.")
        return False

    # FIXME:
    # Source elements should not contain other source elements
    # Need to prevent this from happening

    # Find the Tags object in the target XML
    target_tags_ele = target_root.find(".//Tags")
    if target_tags_ele is None:
        plLogger.LogError("ERROR: Target XML has no Tags element!")
        return False

    # Merge Tag objects from the XML source if necessary
    copy_src_tag_list = []
    for src_ele in src_ele_list:
        tag_ele_list = src_ele.findall(".//Relation")
        for tag_ele in tag_ele_list:
            if tag_ele.get("type") == "UserTag":
                copy_src_tag_list.append(tag_ele.get("target"))
    copy_src_tag_list = set(copy_src_tag_list)
    plLogger.LogDebug("copy_src_tag_list: " + str(copy_src_tag_list))

    # Find the tags in the source XML and extract the ones of interest
    copy_src_tag_ele_list = []
    src_tag_ele_list = source_root.findall(".//Tag")
    for src_tag_ele in src_tag_ele_list:
        if src_tag_ele.get("id") in copy_src_tag_list:
            copy_src_tag_ele_list.append(src_tag_ele)
    plLogger.LogDebug("copy_src_tag_ele_list: " + str(copy_src_tag_ele_list))
    # Store the mappings between the old ID, new ID, old and new name
    # These will be used later to update relations and
    # StmPropertyModifier objects
    new_src_tag_id_map = {}
    new_src_tag_name_map = {}
    for src_tag_ele in copy_src_tag_ele_list:
        src_tag_ele_copy = xml_utils.get_etree_copy(src_tag_ele)

        # Update the tag's Name if the TagPrefix is defined
        old_name = src_tag_ele_copy.get("Name")
        if TagPrefix != "":
            new_name = TagPrefix + old_name
        else:
            new_name = old_name
        src_tag_ele_copy.set("Name", new_name)

        # Update the ID
        old_id = src_tag_ele_copy.get("id")
        src_tag_ele_copy.set("id", str(curr_id))

        # Store both for use later
        new_src_tag_id_map[old_id] = curr_id
        new_src_tag_name_map[old_name] = new_name

        target_tags_ele.append(src_tag_ele_copy)
        xml_utils.create_relation_element(target_tags_ele,
                                          "UserTag", str(curr_id))

        curr_id = curr_id + 1
    plLogger.LogDebug("new_src_tag_id_map: " + str(new_src_tag_id_map))
    plLogger.LogDebug("new_src_tag_name_map: " + str(new_src_tag_name_map))

    # Merge the sources into the target(s)
    for target_ele in target_ele_list:
        for src_ele in src_ele_list:
            plLogger.LogInfo("merging " + str(src_ele) +
                             " into " + str(target_ele))
            # Renumber the object IDs
            src_ele_copy = xml_utils.get_etree_copy(src_ele)
            xml_utils.renormalize_xml_obj_ids(src_ele_copy, start_id=curr_id)

            # Update the tag IDs (should have been lost
            # unless src_ele is Tags...which is not allowed).
            update_relation_targets(src_ele_copy, new_src_tag_id_map)

            # Update the StmPropertyModifiers
            update_property_modifier_tag_names(src_ele_copy,
                                               new_src_tag_name_map)

            plLogger.LogInfo(" src_ele_copy: " + etree.tostring(src_ele_copy))
            target_ele.append(src_ele_copy)

            # Increment the current max ID
            curr_id = curr_id + 1

    # Clean up the invalid handles
    xml_utils.remove_invalid_stc_handles(target_root)
    xml_value = etree.tostring(target_root)
    plLogger.LogInfo("FINAL xml_value: " + etree.tostring(target_root))
    temp_conf.Set("TemplateXml", xml_value)

    return True


def reset():
    return True
