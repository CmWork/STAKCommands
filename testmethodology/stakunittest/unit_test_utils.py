from StcIntPythonPL import *
import time as tm


def wait_for_object_state(parent_handle_list, object_class_name,
                          property_name, state_value,
                          poll_interval, max_wait_time):
    plLogger = PLLogger.GetLogger('methodology')
    ctm = CTaskManager.Instance()

    # Process input objects
    validObjList = CCommandEx.ProcessInputHandleVec(object_class_name, parent_handle_list)

    if (len(validObjList) > 0):
        for obj in validObjList:
            plLogger.LogInfo(" -> obj: " + obj.Get("Name"))
    else:
        plLogger.LogError("ERROR: No valid input objects to wait for")
        return False

    #    cmd = hndReg.Find(__commandHandle__)
    plLogger.LogInfo(" Checking " + property_name + " for " + state_value +
                     " on " + str(len(validObjList)) + " " + object_class_name + " objects...")
    isPass = True
    objWaitList = []

    startTime = tm.clock()
    while True:
        currTime = tm.clock()
        plLogger.LogInfo(" Current Time: " + str(currTime))
        for obj in validObjList:
            if obj.Get(property_name) != state_value:
                plLogger.LogInfo(" adding " + obj.Get("Name") + " as it has state " +
                                 str(obj.Get(property_name)))
                objWaitList.append(obj)
        plLogger.LogInfo(" objWaitList has " + str(len(objWaitList)) + " items...")
        if len(objWaitList) == 0:
            break
        else:
            objWaitList = []
        if (tm.clock() > (startTime + max_wait_time)):
            plLogger.LogInfo("ERROR: WaitForPropertyValueCommand not all objects are in " +
                             state_value + " state")
            isPass = False
            break

        # Differentiate between the poll_interval and the "sampling" interval
        i = 0
        while (i < poll_interval):
            #            if cmd.Get('ProgressCancelled'):
            #                plLogger.LogInfo("WaitForPropertyValueCommand cancelled")
            #                break
            ctm.CtmYield(1000)
            i = i + 1

    return isPass
