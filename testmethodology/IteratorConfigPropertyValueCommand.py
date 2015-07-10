from StcIntPythonPL import *
import ast
from utils.iteration_framework_utils import update_results_with_current_value
import spirent.methodology.utils.data_model_utils as dm_utils
import spirent.methodology.utils.tag_utils as tag_utils


def validate(ObjectList, TagList, IgnoreEmptyTags, CurrVal,
             Iteration, ClassName, PropertyName):
    return ""


def run(ObjectList, TagList, IgnoreEmptyTags, CurrVal,
        Iteration, ClassName, PropertyName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("IteratorConfigPropertyValueCommand.run")

    # Validate ClassName
    valid_class, ret_name = dm_utils.validate_classname(ClassName)
    if not valid_class:
        plLogger.LogError("Invalid ClassName: " + str(ClassName))
        return False

    # Validate PropertyName
    prop_list = [p.lower() for p in CMeta.GetProperties(ClassName)]
    if PropertyName.lower() not in prop_list:
        plLogger.LogError("Invalid PropertyName: " + str(PropertyName) +
                          " given for class: " + str(ClassName))
        return False

    if not IgnoreEmptyTags:
        if tag_utils.is_any_empty_tags_given_string_names(TagList, ClassName):
            plLogger.LogError("No tagged objects for TagList: " +
                              str(TagList))
            return False

    # Find the objects
    obj_list = dm_utils.process_inputs_for_objects(ObjectList, TagList,
                                                   ClassName)
    if len(obj_list) == 0:
        plLogger.LogInfo("No objects of type " + ClassName +
                         " to configure.")
        return True

    plLogger.LogDebug("obj_list contains: " + str(len(obj_list)))

    # Set the new value
    prop_meta = CMeta.GetPropertyMeta(ClassName, PropertyName)
    for obj in obj_list:
        plLogger.LogDebug("setting obj " + obj.Get("Name") + "'s " +
                          PropertyName + " to " + CurrVal)
        if prop_meta["isCollection"]:
            plLogger.LogDebug(PropertyName + " is a collection")
            try:
                val_list = ast.literal_eval(CurrVal)
                if isinstance(val_list, list):
                    obj.SetCollection(PropertyName,
                                      [str(val) for val in val_list])
                else:
                    obj.SetCollection(PropertyName, [str(val_list)])
            except ValueError:
                plLogger.LogError("Was not able to to set collection " +
                                  "property: " + PropertyName + " of " +
                                  ClassName + " to " + CurrVal)
                return False
        else:
            # Scalar
            obj.Set(PropertyName, CurrVal)

    # Update the results
    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)
    res_name = ClassName + "." + PropertyName
    update_results_with_current_value(res_name, CurrVal, Iteration, this_cmd)
    return True


def reset():

    return True
