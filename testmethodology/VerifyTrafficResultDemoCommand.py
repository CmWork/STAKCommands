from StcIntPythonPL import *
import traceback
from spirent.core.utils.scriptable import AutoCommand


def validate(PropertyName, PropertyValue, MinPropertyValue,
             MaxPropertyValue, OperationType, PollInterval, MaxWaitTime):
    return ''


def get_drv_prop_name(PropertyName):
    if PropertyName == 'DROPPED_FRAME_COUNT':
        return 'Streamblock.DroppedFrameCount'
    elif PropertyName == 'MIN_LATENCY':
        return 'Streamblock.MinLatency'
    elif PropertyName == 'MAX_LATENCY':
        return 'Streamblock.MaxLatency'
    else:
        raise Exception("Unsupported property {0}".format(PropertyName))


def create_filter(PropertyName, PropertyValue, MinPropertyValue,
                  MaxPropertyValue, OperationType):
    resultProp = get_drv_prop_name(PropertyName)
    operator = ' > '
    if OperationType == 'LESS_THAN':
        operator = ' >= '
    elif OperationType == 'LESS_THAN_OR_EQUAL':
        operator = ' > '
    elif OperationType == 'GREATER_THAN':
        operator = ' <= '
    elif OperationType == 'GREATER_THAN_OR_EQUAL':
        operator = ' < '
    elif OperationType == 'EQUAL':
        operator = ' <> '
    elif OperationType == 'NOT_EQUAL':
        operator = ' == '
    elif OperationType == 'BETWEEN':
        filterStr = resultProp + ' > ' + str(MaxPropertyValue) + ' AND '
        filterStr = filterStr + resultProp + ' < ' + str(MinPropertyValue)
        return filterStr
    else:
        raise Exception("Unsupported operator {0}".format(OperationType))

    return resultProp + operator + str(PropertyValue)


def create_drv(whereCond):
    project = CStcSystem.Instance().GetObject('project')
    ctor = CScriptableCreator()
    drv = ctor.Create('DynamicResultView', project)
    prq = ctor.Create('PresentationResultQuery', drv)
    prq.SetCollection('SelectProperties', ['Project.Name',
                                           'StreamBlock.Name',
                                           'Port.Name',
                                           'StreamBlock.ActualRxPortName',
                                           'StreamBlock.TxFrameCount',
                                           'StreamBlock.RxSigFrameCount',
                                           'StreamBlock.DroppedFrameCount',
                                           'StreamBlock.MinLatency',
                                           'StreamBlock.MaxLatency'])
    prq.SetCollection('FromObjects', [project.GetObjectHandle()])
    prq.Set('DisableAutoGrouping', 'True')
    prq.SetCollection('WhereConditions', [whereCond])
    return drv


def unsubscribe_drv(drv):
    with AutoCommand('UnsubscribeDynamicResultViewCommand') as cmd:
        cmd.Set('DynamicResultView', str(drv.GetObjectHandle()))
        cmd.Execute()
        drv.MarkDelete()


def run_validate(drv):
    with AutoCommand('spirent.core.results.ValidateAndExportDynamicResultCommand') as cmd:
        cmd.Set('DynamicResultView', drv.Get('Name'))
        cmd.Set('ExpectedResultCount', '0')
        cmd.Execute()
        # jsonResults = test_result.GetCollection('JsonResults')
        # jsonResults.append(data)
        # test_result.SetCollection('JsonResults', jsonResults)


def run(PropertyName, PropertyValue, MinPropertyValue,
        MaxPropertyValue, OperationType, PollInterval, MaxWaitTime):
    logger = PLLogger.GetLogger('methodology')
    try:
        whereString = create_filter(PropertyName, PropertyValue, MinPropertyValue,
                                    MaxPropertyValue, OperationType)
        drv = create_drv(whereString)
        run_validate(drv)
        unsubscribe_drv(drv)
        return True
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        return False


def reset():
    return True
