from StcIntPythonPL import *
import time


OBJ_KEY = 'spirent.methodology.sampling'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(PollingPeriod):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("Validate PollSubscriptionCommand")

    if PollingPeriod < 1:
        err = "PollingPeriod must be at least 1 second"
        plLogger.LogError(err)
        raise RuntimeError(err)

    return ''


def run(PollingPeriod):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("Run PollSubscriptionCommand")

    if not CObjectRefStore.Exists(OBJ_KEY):
        err = "Persistent storage not properly initialized.  Add a SetupSubscriptionCommand."
        plLogger.LogError(err)
        raise RuntimeError(err)

    sampDict = CObjectRefStore.Get(OBJ_KEY)
    utest = None
    if 'Subscription' not in sampDict:
        err = "Persistent storage is missing subscription.  Fix the SetupSubscriptionCommand."
        plLogger.LogError(err)
        raise RuntimeError(err)
    # Everything in python is by reference, so we can modify subList
    subList = sampDict['Subscription']
    if 'UnitTest' in sampDict:
        utest = sampDict['UnitTest']

    get_this_cmd().Set("ProgressIsCancellable", True)

    # Set up next poll time
    start = int(time.time())

    # Initialize the per-(subscription,resultHndl) tracking dictionaries
    prevValueDict = {}
    lastChangeDict = {}
    stabReachedDict = {}

    # TODO: Magic to go from sub['ResultDatasetHandle'] to ResultsSubscribeCommand.Interval
    # pollInterval = min(pollInterval, magic.ResultsSubscribeCommand.Interval)
    pollInterval = 1

    # Grabbing data from unit test
    if utest is not None:
        hnd_reg = CHandleRegistry.Instance()
        ut_tuple_list = utest
        ut_objhdl_list = [hnd_reg.Find(x[0]) for x in ut_tuple_list]
        ut_objprop_list = [x[1] for x in ut_tuple_list]
        ut_iter_list = [x[2].__iter__() for x in ut_tuple_list]
    # Loop through subscriptions until done
    while True:
        now = int(time.time())

        foundReasonToContinue = False

        # Log every result
        for sub in subList:
            hnd_reg = CHandleRegistry.Instance()
            ourDatasetObj = hnd_reg.Find(sub['ResultDatasetHandle'])
            ourQueryObj = ourDatasetObj.GetObject('ResultQuery')
            resObjList = CCommandEx.ProcessInputHandleVec(ourQueryObj.Get('ResultClassId'),
                                                          sub['ResultParent'])
            for resObj in resObjList:
                foundResultHnd = resObj.GetObjectHandle()
                ourDatasetHnd = ourDatasetObj.GetObjectHandle()
                foundDataSet = resObj.GetObject("ResultDataset", RelationType("ResultChild", 1))
                if foundDataSet is not None and foundDataSet.GetObjectHandle() != ourDatasetHnd:
                    continue

                firstResultDotProperty = ourQueryObj.GetCollection('PropertyIdArray')[0]
                resultValue = resObj.Get(firstResultDotProperty.split('.')[1])

                sub['Data'].append((foundResultHnd, now, resultValue))

                thisGuy = (ourDatasetHnd, foundResultHnd)

                # Fill the dictionaries regarding idleness (if subscription cares about it)
                if sub['ValueIdleTimeout'] != 0:
                    # First time, do initialization of thisGuy
                    if thisGuy not in stabReachedDict:
                        # From here assume if thisGuy in the stabReachedDict, then he's in the rest
                        stabReachedDict[thisGuy] = False
                        lastChangeDict[thisGuy] = now
                        prevValueDict[thisGuy] = None
                        foundReasonToContinue = True
                    # We've been here before, but we sadly haven't yet gone stable
                    elif stabReachedDict[thisGuy] is False:
                        # Check for a change in value
                        if resultValue != prevValueDict[thisGuy]:
                            prevValueDict[thisGuy] = resultValue
                            lastChangeDict[thisGuy] = now
                        # See if we have reached stability
                        if (now - lastChangeDict[thisGuy] >= sub['ValueIdleTimeout']):
                            stabReachedDict[thisGuy] = True
                        else:
                            foundReasonToContinue = True

                # Check regarding condition (if subscription cares about it)
                if sub['EnableCondition'] is True and resultValue < sub['Terminal']:
                    foundReasonToContinue = True

        # Check if overall polling time has passed
        if now + pollInterval > start + PollingPeriod:
            break

        # Or stop if no subscriptions wish us to continue
        if foundReasonToContinue is False:
            break

        # Or stop if user asked
        if get_this_cmd().Get("ProgressCancelled") is True:
            break

        # Sleep
        CTaskManager.Instance().CtmYield(pollInterval * 1000)

        # Unit test kludge to fake the setting of data
        if utest is not None:
            for obj, prop, val_iter in zip(ut_objhdl_list, ut_objprop_list,
                                           ut_iter_list):
                value = next(val_iter, None)
                if value is not None and obj is not None:
                    obj.Set(prop, str(value))

    plLogger.LogInfo("Finished PollSubscriptionCommand")
    return True


def reset():
    return True
