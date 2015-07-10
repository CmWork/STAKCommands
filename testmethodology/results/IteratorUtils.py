from StcIntPythonPL import *
import json
import spirent.methodology.results.ResultBllObjectInterface as result_obj
import spirent.methodology.results.LogUtils as logger
from spirent.methodology.results.Info import ActiveIterationInfo


def get_stm_test_result_throw():
    stm_tr = result_obj.get_stm_test_result()
    if stm_tr is None:
        """
        Log error for now and create result object.
        """
        # raise Exception("Unable to find StmTestResult object")
        logger.error('Unable to find StmTestResult object, creating one.')
        stm_tr = result_obj.create_stm_test_result_under_mm()
    return stm_tr


def get_leaf_iterator_recursive(parent_obj):
    child_obj = parent_obj.GetObject('StmIteratorResult')
    if child_obj is not None:
        return get_leaf_iterator_recursive(child_obj)
    else:
        return parent_obj


def get_leaf_iterator_no_throw():
    stm_tr = get_stm_test_result_throw()
    leaf_iterator = get_leaf_iterator_recursive(stm_tr)
    if leaf_iterator.GetObjectHandle() == stm_tr.GetObjectHandle():
        return None
    else:
        return leaf_iterator


def get_iterator(iterator_handle):
    """Get leaf iterator result object and compare handle. If not same return None
    """
    logger.debug('Get leaf iterator for with handle:' + str(iterator_handle))
    leaf_iterator = get_leaf_iterator_no_throw()
    if leaf_iterator is None:
        return None
    if leaf_iterator.Get('Iterator') != iterator_handle:
        return None
    else:
        return leaf_iterator


def get_iterator_result_no_leaf_check(iterator_handle):
    """Find result with provided handle.
        Return none if not found.
    """
    stm_result = result_obj.get_stm_test_result()
    if stm_result is None:
        return None
    child_obj = stm_result.GetObject('StmIteratorResult')
    while child_obj is not None:
        if child_obj.Get('Iterator') == iterator_handle:
            return child_obj
        child_obj = child_obj.GetObject('StmIteratorResult')
    return None


def create_iterator_result():
    """Create iterator result object under leaf result object
    """
    stm_tr = get_stm_test_result_throw()
    leaf_iterator = get_leaf_iterator_recursive(stm_tr)
    ctor = CScriptableCreator()
    ir = ctor.Create("StmIteratorResult", leaf_iterator)
    return ir


def get_leaf_iterator():
    """Get leaf iterator and throw in all error cases
    """
    leaf_iterator = get_leaf_iterator_no_throw()
    if leaf_iterator is None:
        # return none for now. try to handle error condition if it can be.
        # raise Exception("Unable to find StmTestResult object")
        return None
    else:
        return leaf_iterator


def get_active_result_object():
    """Leaf iterator is active result object.
        return StmTestRessult object if none exist.
    """
    logger.debug('Get active result object')
    result = get_leaf_iterator_no_throw()
    if result is None:
        logger.debug('Get active result object, No iterator result so return StmTestResult')
        return get_stm_test_result_throw()
    return result


def get_parent_active_info(iterator_result):
    stm_tr = get_stm_test_result_throw()
    parent = iterator_result.GetParent()
    data = []
    while parent.GetObjectHandle() != stm_tr.GetObjectHandle():
        string_data = parent.Get(ActiveIterationInfo.get_stc_property_name())
        if string_data:
            active_info = json.loads(string_data)
            active_info = active_info[ActiveIterationInfo.get_dict_name()]
            if 'startTime' in active_info:
                del active_info['startTime']
            if 'endTime' in active_info:
                del active_info['endTime']
            data.append(active_info)
        parent = parent.GetParent()
    return data