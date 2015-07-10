from StcIntPythonPL import *
import utils.tag_utils as tag_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def get_list_type(obj_list):
    ts = set()
    for obj in obj_list:
        ts.add(obj.GetType())
    if not ts:
        return None
    elif len(ts) > 1:
        return ''
    return ts.pop()


def validate(LinkType, SrcObjTag, SrcIfTag,
             DstObjTag, DstIfTag, LinkPattern, LinkTag):
    if len(LinkType) == 0:
        return 'Link Type must not be empty'
    return ''


def run(LinkType, SrcObjTag, SrcIfTag,
        DstObjTag, DstIfTag, LinkPattern, LinkTag):
    logger = PLLogger.GetLogger('methodology')

    # Check object tags are not empty
    if not SrcObjTag:
        raise RuntimeError('Source Object Tag is empty')
    if not DstObjTag:
        raise RuntimeError('Destination Object Tag is empty')

    ctor = CScriptableCreator()
    src_obj_list = tag_utils.get_tagged_objects_from_string_names([SrcObjTag])
    src_type = get_list_type(src_obj_list)
    if src_type is None:
        raise RuntimeError('No objects tagged by tag "{}"'.format(SrcObjTag))
    elif not src_type:
        raise RuntimeError('Tag "{}" points to various object types'
                           .format(SrcObjTag))
    dst_obj_list = tag_utils.get_tagged_objects_from_string_names([DstObjTag])
    dst_type = get_list_type(dst_obj_list)
    if dst_type is None:
        raise RuntimeError('No objects tagged by tag "{}"'.format(DstObjTag))
    elif not dst_type:
        raise RuntimeError('Tag "{}" points to various object types'
                           .format(DstObjTag))
    # Only check the multiples if it's not backbone
    if LinkPattern != 'BACKBONE':
        if len(src_obj_list) < len(dst_obj_list):
            raise RuntimeError('Not enough destination objects for '
                               '{} Link Pattern'.format(LinkPattern))
        if (len(src_obj_list) % len(dst_obj_list)) != 0:
            raise RuntimeError('Source and Destination lists must match or be '
                               'even multiples '
                               'in {} Link Pattern'.format(LinkPattern))
    if dst_type != 'Port':
        src_if_list = \
            tag_utils.get_tagged_objects_from_string_names([SrcIfTag]) \
            if SrcIfTag else []
        dst_if_list = \
            tag_utils.get_tagged_objects_from_string_names([DstIfTag]) \
            if DstIfTag else []
        if src_if_list and len(src_if_list) != len(src_obj_list):
            raise RuntimeError("Source Object and Interface list "
                               "sizes don't match")
        if dst_if_list and len(dst_if_list) != len(dst_obj_list):
            raise RuntimeError("Destination Object and Interface list "
                               "sizes don't match")
    # Make lists for each endpoint
    if 'src_if_list' not in locals() or not src_if_list:
        src_if_list = [None] * len(src_obj_list)
    if 'dst_if_list' not in locals() or not dst_if_list:
        dst_if_list = [None] * len(dst_obj_list)
    src_tup_list = zip(src_obj_list, src_if_list)
    dst_tup_list = zip(dst_obj_list, dst_if_list)
    pair_list = []
    logger.LogDebug('Src: ' +
                    ', '.join(['{} ({})'.format(o.Get('Name'),
                                                o.GetObjectHandle())
                               for o in src_obj_list]))
    logger.LogDebug('Dst: ' +
                    ', '.join(['{} ({})'.format(o.Get('Name'),
                                                o.GetObjectHandle())
                               for o in dst_obj_list]))
    if LinkPattern == 'BACKBONE':
        pair_list = [(x, y) for x in src_tup_list for y in dst_tup_list]
    else:
        multi = len(src_obj_list) / len(dst_obj_list)
        mult_dst_tup_list = []
        if LinkPattern == 'PAIR':
            mult_dst_tup_list = [y for y in dst_tup_list for _ in range(multi)]
        else:
            mult_dst_tup_list = dst_tup_list * multi
        pair_list = [(x, y) for x, y in zip(src_tup_list, mult_dst_tup_list)]
    link_list = []
    failure = ''
    for pair in pair_list:
        (src_obj, src_if), (dst_obj, dst_if) = pair
        # Command doesn't support reset, so each command needs instantiated
        cmd = ctor.CreateCommand('LinkCreateCommand')
        cmd.Set('LinkType', LinkType)
        cmd.Set('SrcDev', src_obj.GetObjectHandle())
        if (src_if):
            cmd.Set('SrcIf', src_if.GetObjectHandle())
        cmd.Set('DstDev', dst_obj.GetObjectHandle())
        if (dst_if):
            cmd.Set('DstIf', dst_if.GetObjectHandle())
        cmd.Execute()
        if 'COMPLETED' != cmd.Get('State'):
            failure = cmd.Get('Status')
            break
        link_list.append(cmd.Get('Link'))
        cmd.MarkDelete()
    this_cmd = get_this_cmd()
    this_cmd.SetCollection('LinkList', link_list)
    if LinkTag:
        hnd_reg = CHandleRegistry.Instance()
        for hdl in link_list:
            obj = hnd_reg.Find(hdl)
            if obj is not None:
                tag_utils.add_tag_to_object(obj, LinkTag)
    if failure:
        failure = 'Source: {}, Destination: {}, Error: {} '.format(SrcObjTag,
                                                                   DstObjTag,
                                                                   failure)
        this_cmd.Set('Status', failure)
        raise RuntimeError(failure)
    return True


def reset():
    return True
