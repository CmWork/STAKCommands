from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


PKG = 'spirent.methodology'


def init_create_hierarchy(parent, child_tuple):
    '''
        Create a hierarchy based upon the child_tuple with the parent as the root node.
        Each child_tuple has the following schema:
            (child-command-name, tag-designator, [grandchildren-tuples])
        This function is re-entrant by each generation child command.
        Each individual grandchild-tuple is passed one at a time in each nested call.
    '''
    ctor = CScriptableCreator()
    childname = child_tuple[0]
    grandchildren_tuples = child_tuple[2]

    # Create the child off the parent's command list...
    child = ctor.Create(childname, parent)
    cmd_list = parent.GetCollection('CommandList')
    cmd_list.append(child.GetObjectHandle())
    parent.SetCollection('CommandList', cmd_list)

    # If the child is a While command, then set it's expression to an object iterator...
    if childname == 'SequencerWhileCommand':
        objIterCmd = ctor.Create(PKG + '.ObjectIteratorCommand', child)
        child.Set('ExpressionCommand', objIterCmd.GetObjectHandle())

    # process each grandchild one at a time...
    for grandchild_tuple in grandchildren_tuples:
        init_create_hierarchy(child, grandchild_tuple)


def run_validate_hierarchy(parent, children_tuples):
    '''
        Validates that the hierarchy described by the children_tuples is correctly
            established under the parent command.
        This function is re-entrant by each generation child command.
        This function differs from init_create_hierarchy in that it takes a list of
            child_tuples rather than a single child_tuple. This was useful in simplifying
            the implementation.
        All of the grandchildren tuples are passed (as a list) with each nested call.
    '''
    if len(children_tuples) == 0:
        return ''
    hnd_reg = CHandleRegistry.Instance()
    cmd_list = parent.GetCollection('CommandList')
    if len(cmd_list) != len(children_tuples):
        return str(parent.GetType()) + "'s command list is incorrect"

    for cmd_hnd, child_tuple in zip(cmd_list, children_tuples):
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            return str(parent.GetType()) + ' has an invalid child command'
        if cmd.GetType().lower() != child_tuple[0].lower():
            return str(cmd.GetType()) + ' does not match expected command of ' + \
                str(child_tuple[0].lower()) + ' in command list of ' + str(parent.GetType())
        msg = run_validate_hierarchy(cmd, child_tuple[2])
        if msg != '':
            return msg
    return ''


def on_complete_remove_tags(tag_name_list):
    '''
        Marks all tags in the tag_name_list for delete.
        All relationships will drop away when the tag objects are deleted.
        It isn't clear when the tag will delete. Unit testing may not see
        the tag delete right away.
    '''
    for tag in tag_utils.get_tag_objects_from_string_names(tag_name_list):
        tag.MarkDelete()


def run_tag_hierarchy(parent, children_tuples, tag_dict=None):
    '''
        Create and add tags to those commands in the hierarchy for which there
        are tag-designators in the hierarchy definition.
        tag_dict is updated and returned as a result.
    '''
    # Initialization of parameters, a mutable with a default value will retain
    # its value in subsequent calls
    if tag_dict is None:
        tag_dict = {}
    if len(children_tuples) == 0:
        return tag_dict
    hnd_reg = CHandleRegistry.Instance()
    cmd_list = parent.GetCollection('CommandList')
    for cmd_hnd, child_tuple in zip(cmd_list, children_tuples):
        seq_cmd = hnd_reg.Find(cmd_hnd)
        if child_tuple[1] != '':
            cmd = seq_cmd
            if cmd.IsTypeOf('SequencerWhileCommand'):
                cmd_hnd = cmd.Get('ExpressionCommand')
                cmd = hnd_reg.Find(cmd_hnd)
            tag_name = str(cmd.GetType()) + '.' + str(cmd_hnd)
            tag_dict[child_tuple[1]] = tag_name
            tag_utils.add_tag_to_object(cmd, tag_name)
        # Process all grandchildren, accumulating the tags into tag_dict...
        run_tag_hierarchy(seq_cmd, child_tuple[2], tag_dict)
    # pass back the tag_dict as it looks right now...
    return tag_dict
