from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


def reset():
    return True


def validate(BllCommandTagName, PropertyName, TagList, OverwriteProperty):
    plLogger = PLLogger.GetLogger('testmethodology')
    plLogger.LogInfo(' Validate ModifyHandleListCommand')

    if not BllCommandTagName:
        return "ERROR: Must provide a command name"
    if not PropertyName:
        return "ERROR: Must provide a PropertyName"
    if not TagList:
        return "ERROR: Must provide a tag list"

    taggedCmdList = tag_utils.get_tagged_objects_from_string_names([BllCommandTagName])
    if not taggedCmdList:
        return "ERROR: Nothing is tagged with BllCommandTagName"

    for taggedCmd in taggedCmdList:
        try:
            prop_meta = CMeta.GetPropertyMeta(taggedCmd.GetType(), PropertyName)
        except RuntimeError:
            return "ERROR: %s is not a valid property of a tagged object." % (PropertyName)
        if not prop_meta:
            return "ERROR: %s is not a valid property of a tagged object." % (PropertyName)
        if not prop_meta["isCollection"]:
            return "ERROR: %s is not a collection property." % (PropertyName)

    return ''


def run(BllCommandTagName, PropertyName, TagList, OverwriteProperty):
    plLogger = PLLogger.GetLogger('testmethodology')
    plLogger.LogInfo(' Run ModifyHandleListCommand')

    taggedCmdList = tag_utils.get_tagged_objects_from_string_names([BllCommandTagName])
    # How much re-validation is appropriate?
    if not taggedCmdList:
        plLogger.LogError('ERROR: Nothing is tagged with BllCommandTagName')
        return False

    for taggedCmd in taggedCmdList:
        # Get the current contents on the command's property
        prop_meta = CMeta.GetPropertyMeta(taggedCmd.GetType(), PropertyName)
        # Best practices assert versus LogError versus return False versus exception versus ... ?
        assert prop_meta["isCollection"]

        if OverwriteProperty:
            propList = []
        else:
            propList = taggedCmd.GetCollection(PropertyName)

        for tagName in TagList[:]:
            toAdd = tag_utils.get_tagged_objects_from_string_names([tagName], True, True)
            # Deal wth potentially empty tags
            if not toAdd:
                plLogger.LogError('ERROR: tagName %s is not tagging any objects' % (tagName))
                return False
            else:
                # Expand tags to objects
                for one in toAdd:
                    propList.append(one.GetObjectHandle())

        taggedCmd.SetCollection(PropertyName, propList)

    return True
