import spirent.methodology.results.IteratorUtils as iterator_utils
from spirent.methodology.results.Iterator import Iterator
from spirent.methodology.results.TestResult import TestResult
import spirent.methodology.results.LogUtils as logger
import spirent.methodology.results.ResultBllObjectInterface as result_obj
from spirent.methodology.results.ProviderConst import ProviderConst as pc
import spirent.methodology.results.ResultUtils as result_utils


def create_test():
    logger.info('Create methodology test.')
    test_result = TestResult()
    test_result.create_test()
    logger.debug('Create test completed.')


def start_test():
    logger.info('Start test')
    test_result = TestResult()
    test_result.start_test()
    logger.debug('Start test completed')


def start_test_if_required(test_obj=None):
    if test_obj is None:
        test_obj = TestResult()
    if not test_obj.is_test_started():
        logger.warning('Test is not created and/or started.')
        test_obj.start_test()


def end_all_iterators(force_stop):
    itr_result_obj = iterator_utils.get_leaf_iterator()
    while itr_result_obj is not None:
        logger.error('End iterator call is missing.')
        end_iterator(force_stop)
        itr_result_obj = iterator_utils.get_leaf_iterator()


def end_inner_iterator_if_required(active_iterator_handle):
    itr_result_obj = iterator_utils.get_leaf_iterator()
    root_result = iterator_utils.get_stm_test_result_throw()

    if itr_result_obj is None or \
            itr_result_obj.GetObjectHandle() == root_result.GetObjectHandle() or \
            itr_result_obj.Get(Iterator.get_stc_property_Iterator()) == active_iterator_handle:
        logger.debug('Either new iterator or leaf iterator.')
        return
    # find if new iterator or existing iterator with missing child end iterator
    while itr_result_obj is not None and \
            itr_result_obj.GetObjectHandle() != root_result.GetObjectHandle() and \
            itr_result_obj.Get(Iterator.get_stc_property_Iterator()) != active_iterator_handle:

        itr_result_obj = itr_result_obj.GetParent()
        logger.debug_result_object_info(itr_result_obj)
    if itr_result_obj.GetObjectHandle() == root_result.GetObjectHandle() or \
            itr_result_obj.Get(Iterator.get_stc_property_Iterator()) != active_iterator_handle:
        logger.debug('No existing iterator found with same handle')
        return
    # call end iterator for missing
    leaf_iterator = iterator_utils.get_leaf_iterator()
    while leaf_iterator.Get(Iterator.get_stc_property_Iterator()) != active_iterator_handle:
        logger.error('Missing end iterator for child iterator')
        end_iterator()
        leaf_iterator = iterator_utils.get_leaf_iterator()


def end_test(force_stop=False):
    logger.info('end test. Force stop:' + str(force_stop))
    # end all iterators if required.
    start_test_if_required()
    end_all_iterators(force_stop)
    test_result = TestResult()
    test_result.end_test(force_stop)
    logger.debug('end test completed.')


def stop_test():
    logger.debug('stop_test')
    start_test_if_required()
    test_obj = TestResult()
    if not test_obj.is_test_completed():
        logger.warning('Test did not complete.')
        end_test(True)


def set_iterator_current_value(iterator_handle,
                               iterator_param,
                               value,
                               iteration_id):
    log_string = 'Set iterator values. Iterator handle:' + str(iterator_handle) + ', param:' +\
        str(iterator_param) + ', value:' + str(value) + ', iteration_id:' + str(iteration_id)
    logger.info(log_string)
    start_test_if_required()
    end_inner_iterator_if_required(iterator_handle)
    iterator = Iterator(iterator_handle, None, iterator_param)
    iterator.start_next_iteration(value, iteration_id)
    logger.debug('Set iterator values completed.')


def complete_iteration():
    logger.info('Complete iteration.')
    itr_result_obj = iterator_utils.get_leaf_iterator()
    if itr_result_obj is None:
        logger.error('There is no iterator running to complete iteration.')
        return
    logger.debug_result_object_info(itr_result_obj)
    iterator = Iterator(0, itr_result_obj)
    iterator.complete_active_iteration()
    logger.debug('Complete iteration completed.')


def end_iterator(force_stop=False):
    logger.info('End iteration.')
    itr_result_obj = iterator_utils.get_leaf_iterator()
    if itr_result_obj is None:
        logger.error('There is no iterator running to end iterator.')
        return
    iterator = Iterator(0, itr_result_obj)
    data = iterator.complete(force_stop)
    parentIterator = iterator_utils.get_leaf_iterator_no_throw()
    if parentIterator is None:
        logger.info('Adding iteration result to Test.')
        data[pc.STATUS][pc.APPLY_VERDICT] = True
        test_result = TestResult()
        test_result.add_provider_data(data)
    else:
        logger.info('Adding iteration result to parent iterator.')
        logger.debug_result_object_info(itr_result_obj)
        parent_itr = Iterator(0, parentIterator)
        parent_itr.add_child_iterator_data(data)
    logger.debug('End iteration completed')


def add_provider_result(dict_data):
    """Add provider result to active result object.
    It is leaf iterator result object in case of iterative test.
    Do not throw error if result object does not exist.
    Try to create one and continue.
    """
    logger.info('Add provider result.')
    # make sure test in created and running. If not do that first.
    start_test_if_required()
    result = iterator_utils.get_active_result_object()
    logger.debug_result_object_info(result)
    dict_data = result_utils.insert_report_group_if_not_defined(dict_data)
    result_obj.add_provider_data(result, dict_data)


def add_provider_result_to_root(dict_data):
    """Add provider result to test object.
    Try to create one and continue if test does not exist.
    """
    logger.info('Add provider result to root.')
    # make sure test in created and running. If not do that first.
    start_test_if_required()
    test_result = TestResult()
    dict_data = result_utils.insert_report_group_if_not_defined(dict_data)
    test_result.add_provider_data(dict_data)


def get_last_iteration_info_status(iterator_handle):
    logger.info('Get last iteration info for iterator:' + str(iterator_handle))
    result = iterator_utils.get_iterator_result_no_leaf_check(iterator_handle)
    if result is None:
        return None
    iterator = Iterator(iterator_handle, result)
    return iterator.get_last_iteration_data()


def add_data_to_test_info(dict_data):
    logger.info('Adding data to test report info')
    start_test_if_required()
    test_result = TestResult()
    test_result.add_info_data(dict_data)