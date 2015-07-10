from StcIntPythonPL import *
import json
from spirent.methodology.manager.utils.methodology_manager_utils import (
    MethodologyManagerUtils as meth_man_utils
    )
import spirent.methodology.results.LogUtils as logger
from spirent.methodology.results.Info import Info
from spirent.methodology.results.Status import Status


def get_stc_json_collection_name():
    return 'JsonResults'


def create_stm_test_result_under_mm():
    logger.debug('Create StmTestResult object')
    result_parent = meth_man_utils.get_meth_manager()
    ctor = CScriptableCreator()
    test_result = ctor.Create("StmTestResult", result_parent)
    return test_result


def reset_stm_test_result(test_result):
    """ reset root result data and delete all children
    STmTestResult is root result object.
    """
    logger.debug('Reset StmTestResult object')
    iteration_result = test_result.GetObject('StmIteratorResult')
    if iteration_result is not None:
        iteration_result.MarkDelete()
    test_result.Set(Info.get_stc_property_name(), "")
    test_result.Set(Status.get_stc_property_name(), "")
    test_result.SetCollection(get_stc_json_collection_name(), [])


def reset():
    """Create StmTestResult object if does not exist.
    reset object if exist.
    StmTestResult object should be created under active test.
    If active test does not exist then under methodology manager.
    """
    logger.debug('Reset result objects.')
    result_parent = meth_man_utils.get_meth_manager()
    active_test = meth_man_utils.get_active_test_case()
    if active_test is not None:
        logger.debug('Active test is result parent.')
        result_parent = active_test
    test_result = result_parent.GetObject('StmTestResult')
    if test_result is None:
        ctor = CScriptableCreator()
        test_result = ctor.Create("StmTestResult", result_parent)
    else:
        reset_stm_test_result(test_result)
    logger.debug('Reset result objects done.')
    return test_result


def partial_reset_stm_test_result(test_result):
    """
    Reset everything except info and status for StmTestResult.
    """
    iteration_result = test_result.GetObject('StmIteratorResult')
    if iteration_result is not None:
        iteration_result.MarkDelete()
    test_result.SetCollection(get_stc_json_collection_name(), [])


def get_stm_test_result():
    """
    Return StmTestResult object if exist else return None.
    """
    logger.debug('get_stm_test_result started.')
    result_parent = meth_man_utils.get_meth_manager()
    active_test = meth_man_utils.get_active_test_case()
    if active_test is not None:
        result_parent = active_test
    test_result = result_parent.GetObject('StmTestResult')
    logger.debug('get_stm_test_result completed.')
    return test_result


def update_result_filename(filename):
    stc_sys = CStcSystem.Instance()
    trs = stc_sys.GetObject('Project').GetObject('TestResultSetting')
    if trs is not None:
        trs.Set('CurrentJsonResultFileName', filename)


def add_provider_data(result_obj, dict_data):
    existing_data = result_obj.GetCollection(get_stc_json_collection_name())
    existing_data.append(json.dumps(dict_data, separators=(',', ':'), sort_keys=False))
    result_obj.SetCollection(get_stc_json_collection_name(), existing_data)


def get_stc_version():
    return CStcSystem.Instance().Get('Version')