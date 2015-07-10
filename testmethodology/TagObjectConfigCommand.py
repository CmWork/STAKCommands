from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(TagNameList, ObjectList, CurrVal, Iteration,
             TagList, IgnoreEmptyTags):
    return ''


def run(TagNameList, ObjectList, CurrVal, Iteration,
        TagList, IgnoreEmptyTags):
    if CurrVal != '':
        hdl_list = [int(s) for s in CurrVal.split(',')]
    else:
        hdl_list = []
    if len(TagNameList) < len(hdl_list):
        raise RuntimeError('Not enough tag names specified, expected at ' +
                           'least' + str(len(hdl_list)) + ' elements')
    hnd_reg = CHandleRegistry.Instance()
    # Before processing, remove any objects from tags
    for tag in TagNameList:
        tag_obj = tag_utils.get_tag_object(tag)
        # Clear anything the tag points to
        exist_list = tag_utils.get_tagged_objects([tag_obj])
        for rem_obj in exist_list:
            rem_obj.RemoveObject(tag_obj, RelationType('UserTag'))
    for tag, hdl in zip(TagNameList, hdl_list):
        tag_obj = tag_utils.get_tag_object(tag)
        obj = hnd_reg.Find(hdl)
        # Is this an error if we are getting an invalid handle?
        if obj is None:
            continue
        # Add the object to the tag (not using util, since it operates on str)
        obj.AddObject(tag_obj, RelationType('UserTag'))
    return True


def reset():
    return True
