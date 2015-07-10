from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(SrcTagName, TargetTagName, RelationName, RemoveRelation):
    plLogger = PLLogger.GetLogger('methodology')

    if RelationName:
        # Check that RelationName is a real relation type
        try:
            RelationType(RelationName)
        except RuntimeError as e:
            # Invalid name
            if 'does not exist' in str(e):
                err = "Relation name " + RelationName + \
                      " is not a valid relation type"
                plLogger.LogError(err)
                raise RuntimeError(err)
            else:
                raise e
    return ""


def run(SrcTagName, TargetTagName, RelationName, RemoveRelation):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run ConfigRelationCommand")

    # Before walking the tree, make sure the relation is a valid one
    try:
        RelationType(RelationName)
    except RuntimeError as e:
        # Invalid name
        if 'does not exist' in str(e):
            err = "Relation name " + RelationName + \
                  " is not a valid relation type"
            plLogger.LogError(err)
            raise RuntimeError(err)
        else:
            raise e

    src_objs = tag_utils.get_tagged_objects_from_string_names([SrcTagName])
    targ_objs = tag_utils.get_tagged_objects_from_string_names([TargetTagName])
    for src_obj in src_objs:
        for targ_obj in targ_objs:
            if RemoveRelation is False:
                # TODO: Have a try block to handle expected errors, like invlaid relations, or
                # single-target-only relations that have mutliple targets here?
                src_obj.AddObject(targ_obj, RelationType(RelationName))
            else:
                src_obj.RemoveObject(targ_obj, RelationType(RelationName))

    return True


def reset():
    return True
