import json
from StcIntPythonPL import *
import spirent.methodology.results.ResultBllObjectInterface as result_obj
from spirent.methodology.results.ResultBase import ResultBase
from spirent.methodology.results.Info import TestInfo
from spirent.methodology.results.Status import Status
from spirent.methodology.results.ResultEnum import EnumExecStatus
from spirent.methodology.results.ResultEnum import EnumVerdict
import spirent.methodology.results.LogUtils as logger
from spirent.methodology.results.ResultConst import ResultConst
import spirent.methodology.results.ResultUtils as result_utils
from spirent.methodology.manager.utils.methodology_manager_utils import (
    MethodologyManagerUtils as meth_man_utils
    )


class TestResult(ResultBase):
    def __init__(self):
        super(TestResult, self).__init__(None,
                                         None,
                                         result_obj.get_stm_test_result())

    def create_test(self):
        """
        Prepare data model result object and set info, status.
        """
        logger.info('TestResult, create test started.')

        active_test = meth_man_utils.get_active_test_case()
        if active_test is not None:
            test_case_name = active_test.Get('Name')
            active_meth = active_test.GetParent()
            if active_meth is not None:
                test_case_name = active_meth.Get('Name') + ' - ' + test_case_name
            logger.info('TestResult, using test case name "' + test_case_name + '"')
            self._info = TestInfo(test_case_name)
        else:
            self._info = TestInfo()

        self.set_result_objact(result_obj.reset())
        self._status = Status(EnumExecStatus.created)
        self.commit_info_status()
        logger.info('TestResult, create test completed.')

    def start_test(self):
        """
        create_test must get called before start_test.
        For now, take care of all error conditions.
        call create_test if result object does not exist.
        """
        if self._stc_result_object is None:
            logger.error('Start test called without create_test.')
            self.create_test()
        else:
            result_obj.partial_reset_stm_test_result(self._stc_result_object)
        self.load_info_status_data()
        self._status.exec_status = EnumExecStatus.running
        self._info._start_time = result_utils.get_current_time_string()
        self.commit_info_status()

    def end_test(self, force_stop=False):
        self.load_all_test_data()
        if force_stop is True:
            self._status.exec_status = EnumExecStatus.stopped
        else:
            self._status.exec_status = EnumExecStatus.completed
        self._info.verdict = EnumVerdict.none
        self._info._end_time = result_utils.get_current_time_string()
        self.generate_report()
        self.commit_info_status()

    def load_info_status_data(self):
        self._info = TestInfo()
        self.load_from_stc_object(self._info)
        self._status = Status(EnumExecStatus.none)
        self.load_from_stc_object(self._status)

    def load_all_test_data(self):
        self.load_info_status_data()
        self._data = self.get_from_stc_collection_property_as_dict(
            result_obj.get_stc_json_collection_name())

    def add_provider_data(self, data):
        dataString = json.dumps(data, separators=(',', ':'), sort_keys=False)
        self.append_stc_object_collection(result_obj.get_stc_json_collection_name(), dataString)

    def generate_report(self):
        result_utils.summarize_status(self)
        report = self._info.get_final_info_data()
        report[self._info.dict_name]['version'] = result_obj.get_stc_version()
        report[self._status.dict_name] = self._status.run_time_data
        report[self.get_data_dict_name()] = result_utils.group_data_using_report_group(self._data)

        filename = result_utils.generate_report_file(ResultConst.TEST_RESULT_FILE_NAME,
                                                     report)
        result_obj.update_result_filename(filename)

    def is_test_started(self):
        if self._stc_result_object is None:
            return False
        self.load_info_status_data()
        if self._status.exec_status == EnumExecStatus.none or \
                self._status.exec_status == EnumExecStatus.created:
            return False
        return True

    def is_test_completed(self):
        if self._stc_result_object is None:
            return True
        self.load_info_status_data()
        if self._status.exec_status == EnumExecStatus.completed or \
                self._status.exec_status == EnumExecStatus.stopped or \
                self._status.exec_status == EnumExecStatus.error:
            return True
        return False

    def add_info_data(self, dict_data):
        self.load_info_status_data()
        self._info.add_test_variables(dict_data)
        self.commit_info_status()
