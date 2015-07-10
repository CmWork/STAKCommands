from StcIntPythonPL import *
import time as tm
import operator


def _get_this_cmd():
    '''
    Get this Command instance from the HandleRegistry for setting output
    properties, status, progress, etc.
    '''
    hnd_reg = CHandleRegistry.Instance()
    try:
        this_cmd = hnd_reg.Find(__commandHandle__)
    except NameError:
        return None
    return this_cmd


# This command will wait for a given property value on objects
# given by ObjectClassName under the ParentList.
def validate(ParentList, ObjectClassName, PropertyName,
             PropertyValue, PropertyValueType, OperationType,
             PollInterval, MaxWaitTime):

    if (len(ParentList) < 1):
        return "ParentList should at least have one parent handle in it"
    if (ObjectClassName == ""):
        return "ObjectClassName should be a valid object class name"
    else:
        if (CMeta.ClassExists(ObjectClassName) is False):
            return "ObjectClassName not found"
    if (PropertyName == ""):
        return "Property should be the property being waited for, not null"
    else:
        propertiesList = CMeta.GetProperties(ObjectClassName)
        if (PropertyName not in propertiesList):
            return "Property name " + PropertyName + " not found"
    if (PropertyValue == ""):
        return "State should be the state the command will wait for, not null"
    if (PropertyValueType == ""):
        return "Property value type should not be null"
    else:
        if (_verifyPropertyType(ObjectClassName, PropertyName, PropertyValue,
                                PropertyValueType) is False):
            return "Property Value Type does not match the type of the property"
    if (_verifyPropertyValueTypeAndOperatorMatch(
            PropertyValueType, OperationType) is False):
        return "Property Value Type and Operation Type Mismatch"
    if (PollInterval < 1):
        return "PollInterval should be at least 1 second"
    return ""


def _verifyPropertyType(ObjectClassName, PropertyName,
                        PropertyValue, PropertyValueType):

    propertyMetaDict = CMeta.GetPropertyMeta(ObjectClassName, PropertyName)
    propType = propertyMetaDict['type']
    if propType == 'u32' or propType == 'u64':
        actualPropertyValueType = 'NUMBER'
    elif propType == 'bool':
        actualPropertyValueType = 'BOOL'
    elif propType == 'string':
        actualPropertyValueType = 'STRING'
    elif propType == 'u8' or propType == 'u16':
        actualPropertyValueType = 'ENUM'
    else:
        return False
    return PropertyValueType == actualPropertyValueType


def _verifyPropertyValueTypeAndOperatorMatch(PropertyValueType, OperationType):
    if PropertyValueType == 'NUMBER':
        return True
    else:
        # For Bool, String and enum types, only operations
        # eq and neq are valid
        return OperationType == 'EQUALS' or OperationType == 'NOT_EQUALS'


def run(ParentList, ObjectClassName, PropertyName,
        PropertyValue, PropertyValueType, OperationType,
        PollInterval, MaxWaitTime):
    plLogger = PLLogger.GetLogger('methodology')
    hnd_reg = CHandleRegistry.Instance()
    ctm = CTaskManager.Instance()
    cmd = _get_this_cmd()

    # max_obj_log determines how many objects we log information on
    # before we stop logging.  This is necessary to ensure we do not saturate
    # the log file when testing with large quantities of objects. If you need
    # to see more objects listed, then change this value.
    max_obj_log = 50

    # Process input objects
    obj_list = []
    valid_obj_list = []
    for parent_hnd in ParentList:
        plLogger.LogInfo("parent handle: " + str(parent_hnd))
        scriptable_obj = hnd_reg.Find(parent_hnd)
        if scriptable_obj is None:
            plLogger.LogWarn("Object with handle " + str(parent_hnd) +
                             " is invalid, skipping it.")
            continue
        obj_list.append(scriptable_obj)
        # The Object Picker will return a Port object if all of the
        # devices affiliated to it are selected.  This will fail in
        # process_input_objects as that function only looks at ParentChild
        # relations.  To fix this, the affiliated devices must also be added
        # to the obj_list so that process_input_objects and look at those too.
        if (scriptable_obj.IsTypeOf("Port")):
            devList = \
                scriptable_obj.GetObjects("EmulatedDevice",
                                          RelationType("AffiliationPort", 1))
            obj_list = obj_list + devList
    obj_hnd_list = []
    for obj in obj_list:
        obj_hnd_list.append(obj.GetObjectHandle())
    if (len(obj_hnd_list) > 0):
        valid_obj_list = CCommandEx.ProcessInputHandleVec(ObjectClassName,
                                                          obj_hnd_list)

    logItemCount = 0
    if (len(valid_obj_list) > 0):
        for obj in valid_obj_list:
            logItemCount += 1
            if logItemCount < max_obj_log:
                plLogger.LogInfo(" -> obj: " + str(obj.Get("Name")))
            elif logItemCount == max_obj_log:
                plLogger.LogInfo(" -> additional objects also...")
                break
    else:
        err_str = "No valid input objects to wait for"
        plLogger.LogError(err_str)
        cmd.Set("Status", err_str)
        return False

    plLogger.LogInfo(" Checking " + PropertyName + " " +
                     str(OperationType) + " " + str(PropertyValue) +
                     " on " + str(len(valid_obj_list)) + " " +
                     ObjectClassName + " objects...")

    oper_dict = {'EQUALS': operator.eq,
                 'NOT_EQUALS': operator.ne,
                 'GREATER_THAN': operator.gt,
                 'LESS_THAN': operator.lt,
                 'GREATER_THAN_OR_EQUALS': operator.ge,
                 'LESS_THAN_OR_EQUALS': operator.le}

    is_pass = True
    obj_wait_list = []
    start_time = tm.time()

    log_item_count = 0
    while True:
        curr_time = tm.time()
        for obj in valid_obj_list:
            obj_val = obj.Get(PropertyName)
            log_item_count += 1
            if log_item_count < max_obj_log:
                plLogger.LogInfo("Property Type = " + obj.GetType() +
                                 ", Value = " + str(obj_val))
            elif log_item_count == max_obj_log:
                plLogger.LogInfo("and more property types and values also...")
            if (PropertyValueType == 'NUMBER'):
                if (oper_dict[OperationType](long(obj_val),
                                             long(PropertyValue))) is False:
                    obj_wait_list.append(obj)
            if (PropertyValueType == 'STRING'):
                if (oper_dict[OperationType](str(obj_val),
                                             str(PropertyValue))) is False:
                    obj_wait_list.append(obj)
            if (PropertyValueType == 'ENUM'):
                if (oper_dict[OperationType](str(obj_val),
                                             str(PropertyValue))) is False:
                    obj_wait_list.append(obj)
            if (PropertyValueType == 'BOOL'):
                if (oper_dict[OperationType](str(obj_val),
                                             str(PropertyValue))) is False:
                    obj_wait_list.append(obj)
        if len(obj_wait_list) == 0:
            break
        else:
            obj_wait_list = []

        curr_time = tm.time()
        plLogger.LogInfo("Current Time: " + str(curr_time))

        if (curr_time > (start_time + MaxWaitTime)):
            err_str = "WaitForpropertyValueCommand not all objects meet " + \
                PropertyName + " " + str(OperationType) + " " + \
                str(PropertyValue)
            plLogger.LogError(err_str)
            cmd.Set("Status", err_str)
            is_pass = False
            break

        # Differentiate between the PollInterval and the "sampling" interval
        i = 0
        while (i < PollInterval):
            ctm.CtmYield(1000)

            if cmd is not None:
                if cmd.Get('ProgressCancelled'):
                    err_str = "WaitForPropertyValueCommand canceled"
                    plLogger.LogInfo(err_str)
                    cmd.Set("Status", err_str)
                    break
            CTaskManager.Instance().CtmYield(1000)
            i = i + 1
        plLogger.LogInfo("Continuing wait")
    return is_pass


def reset():
    return True
