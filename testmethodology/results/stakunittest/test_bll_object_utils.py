from StcIntPythonPL import *
import spirent.methodology.results.ResultBllObjectInterface as result_obj
import spirent.methodology.results.IteratorUtils as iterator_utils
from spirent.methodology.manager.utils.methodology_manager_utils import (
    MethodologyManagerUtils as meth_man_utils
    )


def test_create_stm_get_stm(stc, resource_cleanup):
    mm = meth_man_utils.get_meth_manager()
    assert mm is not None
    assert result_obj.get_stm_test_result() is None
    stm_result = mm.GetObject('StmTestResult')
    assert stm_result is None
    stm_result = result_obj.create_stm_test_result_under_mm()
    assert stm_result is not None
    stm_mm = mm.GetObject('StmTestResult')
    assert stm_result.GetObjectHandle() == stm_mm.GetObjectHandle()
    stm3 = result_obj.get_stm_test_result()
    assert stm3 is not None
    assert stm_result.GetObjectHandle() == stm3.GetObjectHandle()
    # check leaf iterator is none
    assert iterator_utils.get_leaf_iterator() is None
    # check StmTestResult is active result
    stm4 = iterator_utils.get_active_result_object()
    assert stm4 is not None
    assert stm_result.GetObjectHandle() == stm4.GetObjectHandle()


def test_iterato_utils_create_get(stc, resource_cleanup):
    # check there are no result objects to start with
    assert result_obj.get_stm_test_result() is None
    # create iterator result which should create StmTestResult as well
    iterator_result_1 = iterator_utils.create_iterator_result()
    assert iterator_result_1 is not None
    stm_result = result_obj.get_stm_test_result()
    assert stm_result is not None
    parent_1 = iterator_result_1.GetParent()
    assert parent_1 is not None
    assert stm_result.GetObjectHandle() == parent_1.GetObjectHandle()
    # check leaf iterator
    iterator_result_3 = iterator_utils.get_leaf_iterator()
    assert iterator_result_3 is not None
    assert iterator_result_3.GetObjectHandle() == iterator_result_1.GetObjectHandle()
    # create one more iterator
    child_1 = iterator_utils.create_iterator_result()
    assert child_1 is not None
    # check parent is previous iterator
    parent_2 = child_1.GetParent()
    assert parent_2 is not None
    assert parent_2.GetObjectHandle() == iterator_result_3.GetObjectHandle()
    # new child should be leaf now
    child_3 = iterator_utils.get_leaf_iterator()
    assert child_3 is not None
    assert child_3.GetObjectHandle() == child_1.GetObjectHandle()
    # active result is same as well
    active_1 = iterator_utils.get_active_result_object()
    assert active_1 is not None
    assert child_3.GetObjectHandle() == active_1.GetObjectHandle()
    # reset results
    result_obj.reset()
    stm_2 = iterator_utils.get_active_result_object()
    assert stm_2 is not None
    assert stm_result.GetObjectHandle() == stm_2.GetObjectHandle()
    # check there are no iterator results
    assert iterator_utils.get_leaf_iterator() is None
    assert stm_2.GetObject('StmIteratorResult') is None
