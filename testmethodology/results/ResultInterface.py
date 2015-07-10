import spirent.methodology.results.ResultInterfaceUtils as utils


class ResultInterface():
    @staticmethod
    def create_test():
        """
        Call this function when new test is loaded.
        Result object and status get initialized.
        """
        utils.create_test()

    @staticmethod
    def start_test():
        """
        Call this function when test exeuction starts.
        Execution status get updated.
        Framework will take care of missing create test call.
        """
        utils.start_test()

    @staticmethod
    def end_test():
        """
        Call this function test execution is complete.
        Verdict will be summarized.
        test report will be generated.
        """
        utils.end_test()

    @staticmethod
    def stop_test():
        """
        Call this function when test is stopped.
        Manually or on error exit.
        test report will be generated.
        """
        utils.stop_test()

    @staticmethod
    def set_iterator_current_value(iterator_handle,
                                   iterator_param,
                                   current_value,
                                   iterator_id):
        """
        call this function when iterator start loop with new value.
        Framework will intialize/update results for iterator.
        iterator_handle : stc handle of iterator command to identify iterator.
        iterator_param  : stc property updated by iterator. e.g. Framesize
        current_value   : current value that will be set for property
        iteration_id    : iteration count.
        """
        utils.set_iterator_current_value(iterator_handle,
                                         iterator_param,
                                         current_value,
                                         iterator_id)

    @staticmethod
    def complete_iteration():
        """
        Call this function at the end of each iteration.
        Verdict will be summarized.
        Iteration result file will be created if innermost iterator.
        """
        utils.complete_iteration()

    @staticmethod
    def end_iterator():
        """
        Call this function on completion of iterating all values.
        Iterator result summary will be created.
        Iterator stc result object will be deleted.
        """
        utils.end_iterator()

    @staticmethod
    def add_provider_result(dict_data):
        """
        Call this function to add result data to active iteration/test.
        """
        utils.add_provider_result(dict_data)

    @staticmethod
    def add_provider_result_to_root(dict_data):
        """
        Call this function to add result data to overall test.
        result that directly apply to overall test.
        e.g. Test stopped on execution error.
        """
        utils.add_provider_result_to_root(dict_data)

    @staticmethod
    def get_last_iteration_info_status(iterator_handle):
        """
        call this function to get last iteration info/status for
        provided iterator handle.
        iterator_handle : stc handle of iterator command to identify iterator.
        return value info/status as dict data.
        return None in all error cases.
        """
        return utils.get_last_iteration_info_status(iterator_handle)

    @staticmethod
    def add_data_to_test_info(dict_data):
        """
        Call this function to add data to info section of test report.
        """
        utils.add_data_to_test_info(dict_data)
