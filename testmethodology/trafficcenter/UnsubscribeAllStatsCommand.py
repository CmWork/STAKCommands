from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


def validate():
    return ''


def run():
    # unsubscribe result datasets for
    # stream streamthresold and port result
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")
    result_datasets = project.GetObjects("ResultDataSet")
    for result_dataset in result_datasets:
        if result_dataset.Get('ResultState') == 'NONE':
            continue
        with AutoCommand("ResultDataSetUnsubscribeCommand") as cmd:
            cmd.Set("ResultDataSet", result_dataset.GetObjectHandle())
            cmd.Execute()
        result_dataset.MarkDelete()
    # unsubscribe DRVs
    for drv in project.GetObjects('DynamicResultView'):
        if drv.Get('ResultState') == 'NONE':
            continue
        with AutoCommand('UnsubscribeDynamicResultView') as cmd:
            cmd.Set('DynamicResultView', drv.GetObjectHandle())
            cmd.Execute()
        drv.MarkDelete()
    return True


def reset():
    return True
