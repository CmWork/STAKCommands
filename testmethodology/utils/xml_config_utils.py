from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import re
import os
from xml.sax.saxutils import escape as sax_escape, \
    unescape as sax_unescape
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils
import spirent.methodology.utils.data_model_utils as dm_utils


ADDL_XML_ESC_CHARS = {"\"": "&quot;", "\'": "&apos;"}
ADDL_XML_UNESC_CHARS = {"&quot;": "\"", "&apos;": "\'"}


# Returns the first element specified by tag name
def get_element(root, xml_tag_name):
    ele_list = root.findall(".//" + xml_tag_name)
    if len(ele_list) > 0:
        return ele_list[0]
    return None


# Returns all Tag elements within the root. If tag_name is blank,
# return all Tag elements under the root element.
def find_tag_elements(root, tag_name=''):
    result = []
    tag_ele_list = root.findall('.//Tag')
    if tag_name == '':
        result = tag_ele_list
    else:
        for tag_ele in tag_ele_list:
            if tag_name == tag_ele.get('Name'):
                result.append(tag_ele)
    if len(result) == 0:
        return []
    return result


# Returns a tag name - id map
def build_tag_name_id_map(root, index_on_id=True):
    tag_list = root.findall(".//Tag")
    tag_dict = {}
    for tag in tag_list:
        if index_on_id:
            tag_dict[tag.get("id")] = tag.get("Name")
        else:
            tag_dict[tag.get("Name")] = tag.get("id")
    return tag_dict


# Returns all DefaultTag handles
def get_tag_handle_list(root, tag_type='DefaultTag'):
    relation_list = root.findall('.//Tags/Relation')
    hdl_list = []
    for rel in relation_list:
        if rel.get('type') == tag_type:
            hdl_list.append(int(rel.get('target')))
    return hdl_list


# Return all objects that are tagged with the given tag
# (integer) handle through the UserTag relation.  If
# element_tag is specified, only those elements with that
# string (xml) tag are returned.
# If a tag name is what's available, use find_tag_element
# and get the id first.
def find_tagged_elements(root, tag_hnd, element_tag=None):
    tagged_ele_list = []
    for child in root:
        if child.tag == "Relation":
            if child.get("type") == "UserTag" and \
               child.get("target") == str(tag_hnd):
                if element_tag is None:
                    tagged_ele_list.append(root)
                else:
                    if element_tag == root.tag:
                        tagged_ele_list.append(root)
        ret_list = find_tagged_elements(child, tag_hnd, element_tag)
        if len(ret_list) > 0:
            tagged_ele_list = tagged_ele_list + ret_list
    return tagged_ele_list


# Returns elements in the tree that are tagged
# with tags specified in the tag_name_list
def find_tagged_elements_by_tag_name(root, tag_name_list,
                                     ignore_tags_element=True,
                                     element_tag=None):
    if len(tag_name_list) == 0:
        # No tags specified
        return []
    tag_ele_list = []
    for tag in tag_name_list:
        ele_list = find_tag_elements(root, tag)
        if ele_list is not None and len(ele_list) > 0:
            tag_ele_list.append(ele_list[0])
    if len(tag_ele_list) < 1:
        # No tags found in template
        return []

    tag_hnd_list = []
    for tag_ele in tag_ele_list:
        tag_hnd_list.append(tag_ele.get("id"))
    tagged_ele_list = []
    ret_ele_list = set()
    for tag_hnd in tag_hnd_list:
        tagged_ele_list = find_tagged_elements(root, tag_hnd, element_tag)
        if len(tagged_ele_list) > 0:
            ret_ele_list.update(tagged_ele_list)
    # Turn this back into a list (so that it can be accessed by index)
    ret_list = []
    for ele in ret_ele_list:
        if (ignore_tags_element and ele.tag == "Tags"):
            continue
        ret_list.append(ele)
    return ret_list


# Get the parent of a given element
# (similar function doesn't exist in ElementTree)
def get_parent(root, element):
    parent = None
    if root is None:
        return None
    if element is None:
        return None
    if element.tag == "StcSystem":
        # No real "parent" here
        return None
    for child in root:
        # Is this the best way to do this?
        if etree.tostring(child) == etree.tostring(element):
            return root
        parent = get_parent(child, element)
        if parent is not None:
            return parent
    return parent


# Get the first (or only) child of root with a given tag_name
def get_child(root, tag_name):
    for child in root:
        if child.tag == tag_name:
            return child
    return None


# Get all the children of root with a given tag_name
def get_children(root, tag_name):
    child_list = []
    for child in root:
        if child.tag == tag_name:
            child_list.append(child)
    return child_list


# Returns a copy of the source element
def get_etree_copy(src_ele):
    # Use deepcopy or convert to a string and build
    # a new element to make a new copy
    # Import copy if using deepcopy
    # copy_ele = copy.deepcopy(src_ele)
    xml_copy = etree.tostring(src_ele)
    copy_ele = etree.fromstring(xml_copy)
    return copy_ele


# Get the maximum object ID in use in the XML file
# (note this is the integer object handle)
def get_max_object_id(root, max_id):
    for child in root:
        if child.tag == "Relation":
            continue
        max_id = get_max_object_id(child, max_id)
        if "id" in child.attrib:
            # An element that is part of the STC
            # generated XML
            if int(child.get("id")) > max_id:
                max_id = int(child.get("id"))
    return max_id


# This function removes all modifiers from the template XML
def strip_modifiers(template_xml):
    root = etree.fromstring(template_xml)

    strip_modifiers_recursive(root)
    return etree.tostring(root)


# Recursive function that actually removes the modifier objects
def strip_modifiers_recursive(root):
    child_list = list(root)
    for child in child_list:
        if child.tag == "StmModifier" or \
           child.tag == "StmPropertyModifier":
            root.remove(child)
        else:
            strip_modifiers_recursive(child)
    return


# Escape <, >, &, ', and " in XML
def escape_xml(xml_str):
    return sax_escape(xml_str, ADDL_XML_ESC_CHARS)


# Unescape &gt;, &lt;, &amp;, &quot;, and &apos; in XML
def unescape_xml(xml_str):
    return sax_unescape(xml_str, ADDL_XML_UNESC_CHARS)


# Parses a list of strings of the form classname.property=val
def parse_property_value_list(prop_val_list):
    attr_dict = {}
    attr_dict["obj_list"] = []
    for item in prop_val_list:
        parsed_pattern = re.findall("(.*?)\.(.*?)=(.*)", item)

        # FIXME:
        # Check for three things
        # Use Barry's functions to test obj, param, and val

        obj = parsed_pattern[0][0]
        param = parsed_pattern[0][1]
        val = parsed_pattern[0][2]

        # Check the class name (obj)
        res, classname = dm_utils.validate_classname(obj)
        if res is False:
            return None, "Invalid classname: " + classname + \
                " specified in property value list."
        else:
            obj = classname

        # Check the property and value
        param_val = (param, val)
        msg, tuple_list = dm_utils.validate_property_tuple(obj,
                                                           [param_val])
        if msg != "":
            return None, msg
        else:
            param = tuple_list[0][0]
            val = tuple_list[0][1]

        attr_dict[obj + "." + param] = val
        if obj not in attr_dict["obj_list"]:
            attr_dict["obj_list"].append(obj)
            attr_dict[obj] = []
        if param not in attr_dict[obj]:
            attr_dict[obj].append(param)
    return attr_dict, ""


# Parses a list of PropertyList and ValueList into
# a dictionary and validates classes, properties, and values
def parse_prop_and_val_list(PropertyList, ValueList):
    plLogger = PLLogger.GetLogger("methodology")
    attr_dict = {}
    attr_dict["obj_list"] = []
    # Check the length of the PropertyList and ValueList
    # They MUST be the same length.
    if len(PropertyList) != len(ValueList):
        msg = "PropertyList and ValueList must have " + \
              "the same number of elements."
        plLogger.LogError(msg)
        return None, msg

    for prop_id, val in zip(PropertyList, ValueList):
        # Break down the property name
        split_name = prop_id.split(".")
        if len(split_name) < 2:
            msg = "Format of PropertyList item " + str(prop_id) + \
                  " is invalid.  Item should be in the form " + \
                  "Object.Property."
            plLogger.LogError(msg)
            return None, msg
        classname = ".".join(split_name[0:-1])
        prop_name = split_name[-1]
        plLogger.LogDebug("checking class: " + classname + " for prop " +
                          prop_name + " with value " + str(val))

        # Check the class name
        res, classname = dm_utils.validate_classname(classname)
        if res is False:
            return None, "Invalid classname: " + classname + \
                " specified in PropertyList."

        # Check the property and value
        prop_val = (prop_name, val)
        msg, tuple_list = dm_utils.validate_property_tuple(classname,
                                                           [prop_val])
        if msg != "":
            plLogger.LogError(msg)
            return None, msg
        else:
            prop_name = tuple_list[0][0]
            val = tuple_list[0][1]

        attr_dict[classname + "." + prop_name] = val
        if classname not in attr_dict["obj_list"]:
            attr_dict["obj_list"].append(classname)
            attr_dict[classname] = []
        if prop_name not in attr_dict[classname]:
            attr_dict[classname].append(prop_name)
    return attr_dict, ""


# Creates a relation element under parent targeting target
def create_relation_element(parent, rel_type, target_id):
    plLogger = PLLogger.GetLogger('methodology')
    if parent is None:
        plLogger.LogError("parent is None")
        return
    rel_ele = etree.Element("Relation")
    rel_ele.set("target", str(target_id))
    rel_ele.set("type", rel_type)
    parent.append(rel_ele)


# Given an STC class_name, returns the properties that are handles
def get_handle_props(class_name):
    hnd_prop_list = []
    if not CMeta.ClassExists(class_name):
        return []
    prop_list = CMeta.GetProperties(class_name)
    for prop in prop_list:
        prop_meta = CMeta.GetPropertyMeta(class_name, prop)
        if prop_meta["type"] == "handle":
            hnd_prop_list.append(prop)
    return hnd_prop_list


# Builds a map of the object IDs to the elements in the element tree
def build_id_map(root, id_map):
    if root is None:
        return id_map

    # Object ID is none for those elements that don't have an id attribute
    # (Skip these...do not add a new id attribute)
    obj_id = root.get("id")
    if obj_id is not None:
        id_map[root.get("id")] = root
        if "in_order_id_list" not in id_map.keys():
            id_map["in_order_id_list"] = []
        id_map["in_order_id_list"].append(obj_id)
    for child in root:
        build_id_map(child, id_map)
    return


# ADD UNIT TESTS FOR STUFF BELOW:


# Loads XML from a source file
def load_xml_from_file(file_path):
    plLogger = PLLogger.GetLogger('methodology')
    xml_str = None
    if not os.path.isabs(file_path):
        full_path = mm_utils.find_template_across_common_paths(file_path)
        if full_path != '':
            file_path = full_path
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            xml_str = f.read()
    else:
        plLogger.LogError("ERROR: Failed to find file " +
                          file_path)
        return None
    return xml_str


def add_prefix_to_tags(prefix, xml_value):
    root = etree.fromstring(xml_value)
    default_list = get_tag_handle_list(root)
    tag_list = find_tag_elements(root)
    if tag_list is not None:
        for tag in tag_list:
            tag_id = int(tag.get('id'))
            if tag_id in default_list:
                continue
            name = tag.get('Name')
            if name is not None:
                tag.set('Name', prefix + str(name))
    for ele in root.findall('.//StmPropertyModifier'):
        ele.set('TagName', prefix + ele.get('TagName'))
    return etree.tostring(root)


# Builds a map of elements, tags, and IDs for merging XML files
def renormalize_xml_obj_ids(root, start_id=1):
    # plLogger = PLLogger.GetLogger("renormalize_xml_obj_ids")
    id_map = {}
    build_id_map(root, id_map)

    # Build a new_id_map
    # Technically ID 1 and 2 are "reserved" for StcSystem and Project
    # However, we'll start from 1 anyway here (so if the template doesn't
    # have StcSystem or Project, it will still start from id 1 if it is
    # renormalized)

    curr_id = start_id
    new_id_map = {}
    for key in id_map["in_order_id_list"]:
        new_id_map[str(key)] = str(curr_id)
        curr_id = curr_id + 1

    renormalize_ids_recursive(root, id_map, new_id_map)
    return


# Fix the object ids, the relation targets, and any handle properties
# to use the new IDs
def renormalize_ids_recursive(root, id_map, new_id_map):
    if root.tag == "Relation":
        old_id = root.get("target")
        # Skip any bad IDs since we don't build a map of relation targets
        if old_id in id_map.keys():
            root.set("target", new_id_map[old_id])
    else:
        if root.get("id") is not None:
            root.set("id", str(new_id_map[root.get("id")]))

        # Fix any properties
        hnd_prop_list = get_handle_props(root.tag)
        for prop in hnd_prop_list:
            # Handle scalars or collections correctly
            hnd_list_str = root.get(prop)
            if hnd_list_str is not None:
                # Fix each of the handles
                hnd_list = hnd_list_str.split()
                new_hnd_list = []
                for old_id in hnd_list:
                    if old_id in id_map.keys():
                        new_id = new_id_map[old_id]
                        new_hnd_list.append(new_id)
                if len(new_hnd_list):
                    new_hnd_list_str = " ".join(new_hnd_list)
                else:
                    # Invalid Stc Handle
                    new_hnd_list_str = "0"
                root.set(prop, new_hnd_list_str)
        for child in root:
            renormalize_ids_recursive(child, id_map, new_id_map)
    return


# Removes all invalid handles
# These can be objects that have handle properties that refer to
# objects that no longer exist or Relation elements
# that target objects that no longer exist
def remove_invalid_stc_handles(root):
    id_map = {}
    build_id_map(root, id_map)

    plLogger = PLLogger.GetLogger("remove_invalid_stc_handles")
    plLogger.LogDebug("removing invalid handles...")
    plLogger.LogDebug("root: " + str(root))
    plLogger.LogDebug("id_map: " + str(id_map))
    rm_ele_list = remove_invalid_stc_handles_recursive(root, id_map)
    for ele in rm_ele_list:
        parent = get_parent(root, ele)
        parent.remove(ele)
    return


# Recurses over the XML and removes invalid relations
# and other invalid object IDs defined in handle properties
def remove_invalid_stc_handles_recursive(root, id_map):
    if root.tag == "Relation":
        if root.get("target") not in id_map.keys():
            plLogger = PLLogger.GetLogger("remove_invalid_stc_handles_recur")
            plLogger.LogDebug("could not find " + str(root.get("target")) +
                              " in keys: " + str(id_map.keys()))
            return [root]
    else:
        # FIXME: Handle invalid object handles
        # Check each property in root
        hnd_prop_list = get_handle_props(root.tag)
        for prop in hnd_prop_list:
            pass
    # Recurse
    rm_ele_list = []
    for child in root:
        rm_ele_list = rm_ele_list + remove_invalid_stc_handles_recursive(child, id_map)
    return rm_ele_list
