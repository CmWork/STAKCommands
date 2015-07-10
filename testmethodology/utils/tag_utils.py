from StcIntPythonPL import *


def get_tagged_endpoints_given_tag_ids(tag_list, relation_name='UserTag'):
    '''
    Given a list of tag object handles, this function looks for associated
    endpoints to the tagged objects and returns Scriptable object suitable for
    use with traffic endpoint bindings
    '''
    return_list = []
    hnd_reg = CHandleRegistry.Instance()
    relation = RelationType(relation_name, True)
    for tag in tag_list:
        # Check the tag in the tag_list is an int.  If it isn't (and this
        # function expects it to be one), skip it.
        try:
            int(tag)
        except ValueError:
            continue
        tag_obj = hnd_reg.Find(int(tag))
        if tag_obj is None:
            continue
        for obj in tag_obj.GetObjects('Scriptable', relation):
            if obj is None:
                continue
            if obj.IsTypeOf('Tags'):
                # Not a valid endpoint
                continue
            if obj.IsTypeOf('NetworkEndpoint'):
                return_list.append(obj)
                continue
            # At this point, we need to find the endpoint
            # The case where it is a route config, it has a child net block
            block = obj.GetObject('NetworkBlock')
            if block is not None:
                return_list.append(block)
                continue
            if obj.IsTypeOf('ProtocolConfig'):
                # Note: Only handling the very first uses if relation
                uses_list = obj.GetObjects('NetworkEndpoint',
                                           RelationType('UsesIf'))
                if uses_list is not None:
                    return_list += uses_list
                    continue
            if obj.IsTypeOf('EmulatedDevice'):
                tli_list = obj.GetObjects('NetworkEndpoint',
                                          RelationType('ToplevelIf'))
                if tli_list is not None:
                    return_list += tli_list
                    continue
            # All matches exhausted, couldn't figure it out
            plLogger = PLLogger.GetLogger('methodology')
            typename = CMeta.GetClassMeta(obj)['name']
            plLogger.LogWarn("ERROR: Unable to expand network endpoint " +
                             "for object of type " + typename)
    return return_list


# Returns all objects tagged by tags in the tag_list specific
# to how the tagged objects can act as endpoints.  This is different
# from a generic function to get all tagged objects.
# Tags that are invalid (don't exist) or do not tag anything
# are ignored.
def get_tagged_endpoints_given_tag_names(tag_list,
                                         relation_name='UserTag'):
    '''
    Given a list of tag names, this function looks for associated
    endpoints to the tagged objects and returns Scriptable object suitable for
    use with traffic endpoint bindings
    '''
    tag_obj_list = get_tag_objects_from_string_names(tag_list)
    return_list = []
    relation = RelationType(relation_name, True)
    for tag_obj in tag_obj_list:
        if tag_obj is None:
            continue
        for obj in tag_obj.GetObjects('Scriptable', relation):
            if obj is None:
                continue
            if obj.IsTypeOf('Tags'):
                # Not a valid endpoint
                continue
            if obj.IsTypeOf('NetworkEndpoint'):
                return_list.append(obj)
                continue
            # At this point, we need to find the endpoint
            # The case where it is a route config, it has a child net block
            block = obj.GetObject('NetworkBlock')
            if block is not None:
                return_list.append(block)
                continue
            if obj.IsTypeOf('ProtocolConfig'):
                # Note: Only handling the very first uses if relation
                uses_list = obj.GetObjects('NetworkEndpoint',
                                           RelationType('UsesIf'))
                if uses_list is not None:
                    return_list += uses_list
                    continue
            if obj.IsTypeOf('EmulatedDevice'):
                tli_list = obj.GetObjects('NetworkEndpoint',
                                          RelationType('ToplevelIf'))
                if tli_list is not None:
                    return_list += tli_list
                    continue
            # All matches exhausted, couldn't figure it out
            plLogger = PLLogger.GetLogger('methodology')
            typename = CMeta.GetClassMeta(obj)['name']
            plLogger.LogWarn("ERROR: Unable to expand network endpoint " +
                             "for object of type " + typename)
    return return_list


def get_tagged_objects(tag_list, remove_duplicates=True,
                       ignore_tags_obj=True,
                       class_name=None):
    '''
    Returns the objects tagged by tags in the tag_list.
    remove_duplicates will remove duplicate objects and
    ignore_tags_obj will ignore the Tags object.
    class_name, if not None, will be used to filter the
    tagged objects.
    '''
    tagged_obj_list = []
    handle_set = set()
    s_list = []
    for tag in tag_list:
        s_list = tag.GetObjects("Scriptable",
                                RelationType("UserTag", 1))
        for s_obj in s_list:
            if ignore_tags_obj and s_obj.IsTypeOf("Tags"):
                continue
            if remove_duplicates:
                hnd = s_obj.GetObjectHandle()
                if hnd not in handle_set:
                    handle_set.add(hnd)
                    tagged_obj_list.append(s_obj)
            else:
                tagged_obj_list.append(s_obj)
    # Apply object filtering
    if class_name is not None:
        filtered_objs = []
        for tagged_obj in tagged_obj_list:
            if tagged_obj.IsTypeOf(class_name):
                filtered_objs.append(tagged_obj)
        tagged_obj_list = filtered_objs

    return tagged_obj_list


def get_tag_objects_from_string_names(string_tag_list, remove_duplicates=True):
    '''
    Returns all Tag objects given the names listed in
    the string_tag_list.
    '''
    project = CStcSystem.Instance().GetObject("Project")
    ret_tag_list = []

    tags = project.GetObject("Tags")
    assert tags
    tag_list = tags.GetObjects("Tag")
    # Store found tags in a map so we can preserve order of
    # tag objects found.
    tag_map = {}
    for tag in tag_list:
        tag_name = tag.Get("Name")
        if tag_name in string_tag_list:
            if tag_name not in tag_map:
                tag_map[tag_name] = tag

    if type(string_tag_list) is list:
        if remove_duplicates:
            get_tag = lambda tag_map, string_tag: tag_map.pop(string_tag, None)
        else:
            get_tag = lambda tag_map, string_tag: tag_map.get(string_tag)

        for string_tag in string_tag_list:
            tag = get_tag(tag_map, string_tag)
            if tag:
                ret_tag_list.append(tag)
    else:
        if string_tag_list in tag_map:
            ret_tag_list.append(tag_map[string_tag_list])

    return ret_tag_list


def get_tagged_objects_from_string_names(string_tag_list,
                                         remove_duplicates=True,
                                         ignore_tags_obj=True,
                                         class_name=None):
    '''
    Returns the objects tagged by the tags given by
    name in the string_tag_list
    '''
    tag_list = get_tag_objects_from_string_names(string_tag_list, remove_duplicates)
    return get_tagged_objects(tag_list, remove_duplicates,
                              ignore_tags_obj, class_name)


def get_tag_object(tag_name, relation_name='UserTag'):
    '''
    Given a string, retrieve or create a tag and return an
    instance of Tag object corresponding to the input
    '''
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    tags = project.GetObject('Tags')
    assert tags
    # Get a map of names and objects
    exist_tag_map = {obj.Get('Name'): obj for obj in tags.GetObjects('Tag')}
    if tag_name == '':
        raise ValueError('Tag names must not be blank')
    tag = None
    if tag_name in exist_tag_map:
        tag = exist_tag_map[tag_name]
    else:
        tag = ctor.Create('Tag', tags)
        tag.Set('Name', tag_name)
    # Ensure tag is of the right 'type' (via relation)
    if tag.GetObject('Tags', RelationType(relation_name, True)) is None:
        tags.AddObject(tag, RelationType(relation_name))
    return tag


def is_any_empty_tags_given_string_names(tag_name_list, obj_name):
    tag_list = get_tag_objects_from_string_names(tag_name_list)
    return is_any_empty_tags(tag_list, obj_name)


def is_any_empty_tags(tag_list, obj_name):
    if len(tag_list) > 0:
        for tag in tag_list:
            tagged_obj_list = get_tagged_objects(
                [tag],
                remove_duplicates=True,
                class_name=obj_name)
            if len(tagged_obj_list) < 1:
                return True
    return False


def get_tag_object_list(tag_list, relation_name='UserTag'):
    '''
    Given a list of strings, retrieve or create tags and return an
    list of instances of Tag objects corresponding to the input
    '''
    return [get_tag_object(name, relation_name) for name in tag_list]


# Given an object instance and a tag name, tag the object
def add_tag_to_object(obj, tag_name, relation_name='UserTag'):
    '''
    Given an object instance and tag name, tag the object with the named tag.
    If the tag object does not exist, create it and tag it.
    '''
    tag = get_tag_object(tag_name, relation_name)
    obj.AddObject(tag, RelationType(relation_name))
    return tag
