from StcIntPythonPL import *
from spirent.methodology.results.Info import IterationInfo
from spirent.methodology.results.Status import Status
from spirent.methodology.results.ResultBase import ResultBase
import spirent.methodology.results.ResultUtils as result_utils
import spirent.methodology.results.IteratorUtils as iterator_utils
from spirent.methodology.results.ResultEnum import (
    EnumDataFormat,
    EnumDataClass
)


class Iteration(ResultBase):
    def __init__(self, info=None, result_obj=None, results=None, status=None):
        iteration_info = IterationInfo()
        iteration_info.load_from_dict(info)
        iteration_status = Status()
        iteration_status.load_from_dict(status)
        super(Iteration, self).__init__(iteration_info, iteration_status, result_obj)
        self._data = results

    def generate_report(self):
        result_utils.summarize_status(self)
        parent_itr_info = iterator_utils.get_parent_active_info(self._stc_result_object)
        self._info.set_data_format(self._info, EnumDataFormat.group)
        self._info.set_data_class(self._info, EnumDataClass.iteration_report)
        report = self._info.run_time_data
        if parent_itr_info and len(parent_itr_info) > 0:
            report[self._info.dict_name]['parent_iteration_info'] = parent_itr_info
        report[self._status.dict_name] = self._status.run_time_data
        report[ResultBase.get_data_dict_name()] = \
            result_utils.group_data_using_report_group(self._data)

        report_name = self.get_report_file_name(parent_itr_info)
        # add report name to info
        report[self._info.dict_name]['resultFile'] = report_name
        result_utils.generate_report_file(report_name, report)
        # return status
        status = {}
        status[Status.get_verdict_dict_name()] = self._status.verdict
        status[Status.get_verdict_text_dict_name()] = self._status._verdict_text
        status[IterationInfo.get_result_file_dict_name()] = report_name
        return status

    def get_report_file_name(self, parent_info):
        report_name = 'Iteration'
        if parent_info and len(parent_info) > 0:
            for info in reversed(parent_info):
                report_name = report_name + '-' + info[IterationInfo.get_param_dict_name()]
                report_name = report_name + '-' + str(info[IterationInfo.get_value_dict_name()])
        report_name = report_name + '-' + self._info._param + '-' + str(self._info._value)
        report_name = report_name + '-' + IterationInfo.get_id_dict_name()
        report_name = report_name + '-' + str(self._info._id) + '.json'
        return str(report_name)
        