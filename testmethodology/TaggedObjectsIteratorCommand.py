from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


OBJ_KEY_HEAD = 'spirent.methodology.obj_iterator.'


def get_this_obj_key():
    return OBJ_KEY_HEAD + str(__commandHandle__)


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(TagNameList, ObjectOrder,
             BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    return ''


def run(TagNameList, ObjectOrder,
        BreakOnFail, MinVal, MaxVal, PrevIterVerdict):
    # plLogger = PLLogger.GetLogger('IterateOverTaggedObjects')
    this_cmd = get_this_cmd()
    key = get_this_obj_key()
    # If a validator fails, then set the results
    if BreakOnFail and PrevIterVerdict is False:
        this_cmd.Set('PassFailState', 'Failed')
        this_cmd.Set('ResetState', True)
        return False
    # Verify that the set up parameters match what's being iterated
    if CObjectRefStore.Exists(key):
        cmd_dict = CObjectRefStore.Get(key)
        # If they don't match, ditch what we have, start over
        if cmd_dict['ObjectOrder'] != ObjectOrder or \
           cmd_dict['TagNameList'] != TagNameList:
            CObjectRefStore.Release(key)
    if this_cmd.Get('ResetState') or not CObjectRefStore.Exists(key):
        this_cmd.Set('ResetState', False)
        this_cmd.Set('Iteration', 0)
        this_cmd.Set('CurrVal', '')
        cmd_dict = {'ObjectOrder': ObjectOrder,
                    'TagNameList': TagNameList}
        # Assumption, if not SCALAR, it's TUPLE
        if ObjectOrder == 'SCALAR':
            obj_list = tag_utils.get_tagged_objects_from_string_names(TagNameList)
            hnd_list = [obj.GetObjectHandle() for obj in obj_list]
        else:
            # This expression gets too ugly the way it's set up, so will be
            # explicit for this nested list of lists
            hnd_list_list = []
            for tag in TagNameList:
                obj_list = tag_utils.get_tagged_objects_from_string_names(tag)
                hnd_list = [obj.GetObjectHandle() for obj in obj_list]
                hnd_list_list.append(hnd_list)
            if len(hnd_list_list) < 2:
                raise ValueError('Expected multiple lists, but only got one')
            hnd_list = zip(*hnd_list_list)
        cmd_dict['HandleList'] = hnd_list
        CObjectRefStore.Put(key, cmd_dict)
    # At this point, it should exist
    cmd_dict = CObjectRefStore.Get(key)
    iter_num = this_cmd.Get('Iteration')
    # Done if we reach last index
    if iter_num >= len(cmd_dict['HandleList']):
        this_cmd.Set('Iteration', iter_num)
        this_cmd.Set('PassFailState', 'FAILED')
        this_cmd.Set('ResetState', True)
        if CObjectRefStore.Exists(key):
            CObjectRefStore.Release(key)
        return False
    if ObjectOrder == 'SCALAR':
        curr_val = str(cmd_dict['HandleList'][iter_num])
    else:
        curr_val = ','.join([str(x) for x in cmd_dict['HandleList'][iter_num]])
    this_cmd.Set('CurrVal', curr_val)
    iter_num = iter_num + 1
    this_cmd.Set('Iteration', iter_num)
    return True


def reset():
    ''' Called when command sequencer starts up, or steps from idle '''
    seq = CStcSystem.Instance().GetObject('Sequencer')
    seq_parent = False
    this_cmd = get_this_cmd()
    walk = this_cmd
    while walk:
        if walk.GetObjectHandle() == seq.GetObjectHandle():
            seq_parent = True
        walk = walk.GetParent()
    # Only reset if command lives under sequencer, and Reset() is called when
    # idle
    if seq_parent and seq.Get('State') == 'IDLE':
        if CObjectRefStore.Exists(key):
            CObjectRefStore.Release(key)
    return True
