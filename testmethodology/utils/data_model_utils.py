from StcIntPythonPL import *
import collections
import tag_utils as tag_utils
from collections import defaultdict, OrderedDict


# Returns whether or not the property is an enumeration
def is_property_enum(class_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    try:
        meta = CMeta.GetPropertyMeta(class_name, prop_name)
        if meta and (len(meta["enumerationRefName"]) > 0):
            return True
    except:
        plLogger.LogError("Could not get meta information for " +
                          str(class_name) + "  " + str(prop_name))
    return False


def is_property_collection(class_name, prop_name):
    plLogger = PLLogger.GetLogger("methodology")
    try:
        meta = CMeta.GetPropertyMeta(class_name, prop_name)
        if meta and meta["isCollection"]:
            return True
    except:
        plLogger.LogError("Could not get meta information for " +
                          str(class_name) + "  " + str(prop_name))
    return False


def get_enum_str(class_name, prop_name, num_value):
    return CMeta.GetEnumerationString(class_name, prop_name, num_value)


def get_enum_val(class_name, prop_name, string_value):
    return CMeta.GetEnumerationValue(class_name, prop_name, string_value)


def validate_classname(class_name):
    # Check the meta data before trying to create new XML!
    if not CMeta.ClassExists(class_name):
        return False, class_name
    cl_meta = CMeta.GetClassMeta(class_name)
    # Fix the name capitalization
    if cl_meta['name'] != class_name:
        class_name = cl_meta['name']
    return True, class_name


def validate_property_tuple(class_name, prop_tuple_list):
    new_tuple_list = []
    prop_list = CMeta.GetProperties(class_name)
    lower_list = [obj.lower() for obj in prop_list]
    for prop, value in prop_tuple_list:
        if prop.lower() not in lower_list:
            return "Property " + prop + " not found in class " + class_name, \
                   prop_tuple_list
        if prop not in prop_list:
            for tp in prop_list:
                if tp.lower() == prop.lower():
                    prop = tp
                    break
        # Validate enumeration value
        if is_property_enum(class_name, prop):
            if is_property_collection(class_name, prop):
                tmp_value = stcsave_string_to_list(value)
            else:
                tmp_value = [value]
            for val in tmp_value:
                try:
                    CMeta.GetEnumerationValue(class_name, prop, val)
                except RuntimeError:
                    # Handle a collection of enums
                    return "Invalid value " + val + " given for " + \
                           "property " + prop + " on class " + \
                           class_name, prop_tuple_list
        else:
            ok = True
            err = ""
            if is_property_collection(class_name, prop):
                # Try to adjust the value if it's a string
                tmp_value = stcsave_string_to_list(value)
                ok, err = CMeta.IsPropertyValueValid(class_name, prop,
                                                     tmp_value)
            else:
                ok, err = CMeta.IsPropertyValueValid(class_name, prop, value)
            if not ok:
                return "Value " + value + " is not valid for " + \
                       "property " + prop + " on class " + class_name + \
                       ": " + err, prop_tuple_list
        new_tuple_list.append((prop, value))
    return "", new_tuple_list


def validate_obj_prop_val(obj_name, prop_name, value):
    # Check the object exists
    res, obj_name = validate_classname(obj_name)
    if res is False:
        return "Object with name: " + obj_name + " does not exist!"

    # Check the property exists on the given object
    prop_list = [prop.lower() for prop in CMeta.GetProperties(obj_name)]
    if prop_name.lower() not in prop_list:
        return "Property: " + prop_name + " does not exist on object: " + \
            obj_name + "."

    # Check the prop_name with the value
    prop_val = (prop_name, value)
    msg, tuple_list = validate_property_tuple(obj_name, [prop_val])
    if msg != "":
        return "Invalid value: " + value + \
            " specified for " + obj_name + "'s " + prop_name + ": " + msg
    return ""


def get_class_hierarchy(class_name, terminator='Scriptable'):
    result = []
    res, class_name = validate_classname(class_name)
    if res:
        result = [class_name]
        while class_name != terminator and class_name != 'Null':
            base = CMeta.GetClassMeta(class_name)['baseClass']
            class_name = base.split('.')[-1]
            result.append(class_name)
    return result


def get_valid_relations(src_class, dst_class):
    src_list = get_class_hierarchy(src_class)
    dst_list = get_class_hierarchy(dst_class)
    result = []
    # Failure, throw?
    if len(src_list) != 0 and len(dst_list) != 0:
        # Walk down the relations
        for s_class in src_list:
            for rel in CMeta.GetRelations(s_class, 'forward'):
                rm_list = CMeta.GetRelationMeta(s_class, rel, 'forward')
                if len(rm_list) == 0:
                    continue
                for rm in rm_list:
                    dest = CMeta.GetClassMeta(rm['class2'])['name']
                    if dest in dst_list:
                        result.append(rel)
    return result


def validate_class_relation(src_class, dst_class, relation, ignore_case=False):
    relations = get_valid_relations(src_class, dst_class)
    if not ignore_case:
        return relation in relations
    else:
        return relation.lower() in [obj.lower() for obj in relations]


# Returns True if all objects in the list are of the same
# class_name.  If class_name is given, determines if all objects
# are of that type.
def is_obj_list_all_same_type(obj_list, class_name=None):
    if len(obj_list) == 0:
        return None
    for obj in obj_list:
        if class_name is None:
            class_name = obj.GetType()
        if not obj.IsTypeOf(class_name):
            return False
    return True


# Recursively search an object's ancestors
# for an ancestor of a given type.
def get_ancestor(obj, ancestor_type):
    if obj is None:
        return None
    if obj.IsTypeOf(ancestor_type):
        return obj
    return get_ancestor(obj.GetParent(), ancestor_type)


# Process the input handles and tag names for objects
# of a given class name.
def process_inputs_for_objects(hnd_list, tag_name_list, obj_class):
    obj_dict = {}

    # Process tag objects
    if len(tag_name_list) > 0:
        tagged_obj_list = tag_utils.get_tagged_objects_from_string_names(
            tag_name_list,
            remove_duplicates=True,
            class_name=obj_class)
        obj_dict = {obj.GetObjectHandle(): obj for obj in tagged_obj_list}

    # Process handles
    obj_list = CCommandEx.ProcessInputHandleVec(obj_class,
                                                hnd_list)
    for obj in obj_list:
        if obj is None:
            continue
        obj_dict[obj.GetObjectHandle()] = obj
    return obj_dict.values()


def set_tagged_object_names(tag_name, name_prefix, start_index=1):
    '''
    Given a tag name, set the Name property of each object given the name
    prefix and number. For example: Prefix 'Router', yields names 'Router 1',
    'Router 2', 'Router 3'.
    '''
    obj_list = tag_utils.get_tagged_objects_from_string_names([tag_name])
    for idx, obj in enumerate(obj_list, start=start_index):
        obj.Set('Name', '{}{}'.format(name_prefix, idx))


"""
def clean_up_property_chains(parent_obj):
    plLogger = PLLogger.GetLogger("clean_up_property_chains")
    plLogger.LogInfo("start")
    prop_chain_list = parent_obj.GetObjects("PropertyChainingConfig")
    for prop_chain in prop_chain_list:
        target_obj = prop_chain.GetObject("Scriptable",
                                          RelationType("PropertyChain"))
        # Dangling PropertyChainingConfig
        if target_obj is None:
            prop_chain.MarkDelete()
"""


# FIXME:
# Need to clean up "invalid" property chains, particularly if the
# property chain is being added in a loop (ie nested iterations).
# Not sure what an "invalid" property chain is yet but once it is
# known what they are, can address that here.
# Note that "dangling" property chains (ie target cmd is deleted) are
# automatically cleaned up.
def add_property_chain(source_prop, source_cmd,
                       target_prop, target_cmd):
    ctor = CScriptableCreator()
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("data_model_utils.add_property_chain.start")
    plLogger.LogDebug(" add prop chain between src: " +
                      source_cmd.Get("Name") + "  " +
                      str(source_cmd.GetObjectHandle()) +
                      " and dst: " +
                      target_cmd.Get("Name") + "  " +
                      str(target_cmd.GetObjectHandle()))
    prop_chain_list = source_cmd.GetObjects("PropertyChainingConfig")
    for prop_chain in prop_chain_list:
        target_objs = prop_chain.GetObjects("Scriptable",
                                            RelationType("PropertyChain"))
        for target_obj in target_objs:
            plLogger.LogInfo(" - prop_chain: " + prop_chain.Get("Name") +
                             "  " + str(prop_chain.GetObjectHandle()) +
                             " targeting " + target_obj.Get("Name") +
                             " " + str(target_obj.GetObjectHandle()))
    cmd = ctor.CreateCommand("AddPropertyChainingCommand")
    cmd.SetCollection("SourcePropertyIdList", [source_prop])
    cmd.SetCollection("SourceCommandList", [source_cmd.GetObjectHandle()])
    cmd.SetCollection("TargetPropertyIdList", [target_prop])
    cmd.SetCollection("TargetCommandList", [target_cmd.GetObjectHandle()])
    cmd.Execute()
    cmd.MarkDelete()
    plLogger.LogDebug("data_model_utils.add_property_chain.end")


def print_device_interfaces(dev):
    plLogger = PLLogger.GetLogger('methodology')
    currIf = get_bottom_level_if(dev)

    intStr = currIf.GetType() + " -> "
    while currIf is not None:
        childIfs = currIf.GetObjects("NetworkInterface", RelationType("StackedOnEndpoint", 1))
        for intf in childIfs:
            intStr = intStr + intf.GetType() + " "
        currIf = None
        if childIfs is not None and len(childIfs) > 0:
            currIf = childIfs[0]
            intStr = intStr + " -> "
    plLogger.LogInfo(intStr)


# Returns the "BottomLevelIf" (outermost interface, usually Ethernet II)
def get_bottom_level_if(dev):
    # Start from the TLI (any TLI) and walk down the stack
    tliList = dev.GetObjects("NetworkInterface", RelationType("TopLevelIf"))
    if (len(tliList) < 1):
        plLogger = PLLogger.GetLogger('methodology')
        plLogger.LogError("ERROR: Could not find a TopLevelIf for " + str(dev.Get("Name")))
        return ""

    # Use the first TopLevelIf to find the BottomIf
    currIf = tliList[0]
    bottomIf = tliList[0]
    while (currIf is not None):
        bottomIf = currIf
        currIf = currIf.GetObject("NetworkInterface", RelationType("StackedOnEndpoint"))
    return bottomIf


# Add tag list
def add_tag_list(parent, handle_list):
    hnd_reg = CHandleRegistry.Instance()
    pos = 0
    for handle in handle_list:
        tag = hnd_reg.Find(int(handle))
        # Ignore invalid handles
        if tag is None:
            continue
        if not tag.IsTypeOf('Tag'):
            plLogger = PLLogger.GetLogger('methodology')
            plLogger.LogInfo("Invalid handle " + str(handle) + " of type " +
                             tag.GetType())
            continue
        tag_elem = Element('Tag')
        tag_elem.set('name', tag.Get('Name'))
        tag_elem.set('handle', str(handle))
        # Push them to the front
        parent.insert(pos, tag_elem)
        pos += 1


# Just a boolean to check whether element has at least one tag
def is_element_tagged(element):
    first_tag = element.find('Tag')
    return first_tag is not None


# Returns all tags contained within an element
def get_element_tags(element):
    tag_list = element.findall('Tag')
    handle_list = []
    for tag in tag_list:
        handle_list.append(int(tag.get('handle')))
    return handle_list


def add_tag_to_objects(object_list, tag_handle_list, relation='UserTag'):
    hnd_reg = CHandleRegistry.Instance()
    # Skip processing if nothing is passed in
    if not object_list or not tag_handle_list:
        return
    tag_list = []
    for tag_hnd in tag_handle_list:
        tag_obj = hnd_reg.Find(int(tag_hnd))
        if tag_obj is None or not tag_obj.IsTypeOf('Tag'):
            continue
        tag_list.append(tag_obj)

    # For each object (not handle)
    rel_type = RelationType(relation)
    for obj in object_list:
        if obj is None:
            continue
        for tag in tag_list:
            obj.AddObject(tag, rel_type)


def is_valid_parent(parent_type, child_type):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("is_valid_parent")
    plLogger.LogDebug(" parent_type: " + parent_type +
                      "  child_type: " + child_type)
    # Save all base classes of the parent
    curr_class = parent_type
    parent_bases = []
    while curr_class:
        if curr_class not in parent_bases:
            parent_bases.append(curr_class.lower())
        class_meta = CMeta.GetClassMeta(curr_class)
        curr_class = class_meta["parentClassId"]
    # Need to check back to the base class
    curr_class = child_type
    has_valid_parent = False
    while True:
        rel_meta_list = CMeta.GetRelationMeta(curr_class,
                                              "ParentChild",
                                              "BACKWARD")
        for rel_meta in rel_meta_list:
            plLogger.LogDebug("rel_meta: " + str(rel_meta))
            if rel_meta["class1"].lower() in parent_bases:
                has_valid_parent = True
                break
        if has_valid_parent:
            break

        class_meta = CMeta.GetClassMeta(curr_class)
        curr_class = class_meta["parentClassId"]
        if curr_class == "":
            break
    return has_valid_parent


def stcsave_list_to_string(input_list):
    '''
    This function is a port of the exact code in CollectionProperty.h, which
    has a bug where braces are never escaped. This yields an error when
    loading back strings with braces. See CR 2291433831
    '''
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("stcsave_list_to_string with {}".format(input_list))
    return ' '.join(['{{{}}}'.format(i) if ' ' in str(i) or not str(i)
                     else str(i) for i in input_list])


def stcsave_string_to_list(input_str):
    '''
    See documentation for function above. If the BLL code is fixed, please
    update here as well
    '''
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("stcsave_string_to_list with {}".format(input_str))
    # Already a list?
    if isinstance(input_str, collections.Sequence) and \
       not isinstance(input_str, str):
        return input_str
    result = []
    rem = str(input_str)
    while rem:
        rem = rem.lstrip(' ')
        if rem[0] == '{':
            idx = rem.find('}')
            if idx == -1:
                result.append(rem)
                break
            else:
                result.append(rem[1:idx])
                rem = rem[idx + 1:]
        else:
            idx = rem.find(' ')
            if idx == -1:
                result.append(rem)
                break
            else:
                result.append(rem[:idx])
                rem = rem[idx + 1:]
    return result


def remove_dup_scriptable(obj_list):
    obj_dict = defaultdict(list)
    obj_dict = OrderedDict([(x.GetObjectHandle(), x) for x in obj_list if x is not None])
    return obj_dict.values()


# Sorts obj_list by handle and removes duplicates
def sort_obj_list_by_handle(obj_list):
    obj_dict = defaultdict(list)
    # Put obj_list in a dict with the object handle as the key
    obj_dict = {x.GetObjectHandle(): x for x in obj_list if x is not None}
    # Sort dict by handle and put into list
    sorted_list = [obj_dict[handle] for handle in sorted(obj_dict)]

    return sorted_list


def rsearch(parent, classname_list, relation_list, found_list):
    '''
    Recursively search via specified relations all descendants for objects that match one of the
    types found in the classname_list, and return all matching descendants in the found_list.  If
    classname_list is empty, all classes match.
    '''
    if not classname_list:
        found_list.append(parent)
    else:
        for classname in classname_list:
            if parent.IsTypeOf(classname):
                found_list.append(parent)

    child_list = []
    for relation in relation_list:
        child_list += parent.GetObjects("Scriptable", RelationType(relation))
    remove_dup_scriptable(child_list)
    child_list = sort_obj_list_by_handle(child_list)

    for child in child_list:
        rsearch(child, classname_list, relation_list, found_list)


def get_class_objects(ObjectHandleList, ObjectTagNameList, ClassNameList):
    plLogger = PLLogger.GetLogger("methodology")

    # Get list of objects from ObjectHandleList and ObjectTagNameList
    obj_list = []
    obj_list = get_obj_list_from_handles_and_tags(ObjectHandleList, ObjectTagNameList)
    if len(obj_list) == 0:
        err = "Neither ObjectHandleList nor ObjectTagNameList " \
              "specified a valid STC objects."
        plLogger.LogError(err)
        return {}

    target_obj_list = []
    for obj in obj_list:
        # If Mix Object, get children TemplateConfigs, get GeneratedObjects and
        # call rsearch function
        if obj.IsTypeOf('StmTemplateMix'):
            for tcfg in obj.GetObjects('StmTemplateConfig'):
                for gen_obj in tcfg.GetObjects("Scriptable",
                                               RelationType("GeneratedObject")):
                    rsearch(gen_obj, ClassNameList, ['ParentChild'], target_obj_list)
        # If TemplateConfig, get GeneratedObjects and call rsearch function
        elif obj.IsTypeOf('StmTemplateConfig'):
            for gen_obj in obj.GetObjects("Scriptable",
                                          RelationType("GeneratedObject")):
                rsearch(gen_obj, ClassNameList, ['ParentChild'], target_obj_list)
        # If not a mix object or template config, call rsearch function to search its
        # children
        else:
            rsearch(obj, ClassNameList, ['ParentChild'], target_obj_list)

    target_obj_list = sort_obj_list_by_handle(target_obj_list)
    if len(target_obj_list) == 0:
        err = "No objects of given class found in ObjectHandleList or ObjectTagNameList"
        plLogger.LogError(err)

    return target_obj_list


def get_obj_list_from_handles_and_tags(ObjectHandleList, ObjectTagNameList):
    plLogger = PLLogger.GetLogger("methodology")
    obj_list = []
    hnd_reg = CHandleRegistry.Instance()

    # Get objects from handle list
    for hnd in ObjectHandleList:
        obj = hnd_reg.Find(int(hnd))
        if not obj:
            err_str = "Invalid object with handle " + str(int(hnd))
            plLogger.LogError(err_str)
            return {}
        obj_list.append(obj)

    # Get objects from tag list
    tagged_things = tag_utils.get_tagged_objects_from_string_names(
        ObjectTagNameList)
    obj_list = obj_list + tagged_things

    # Sort by handle and remove duplicates
    obj_list = sort_obj_list_by_handle(obj_list)

    return obj_list
