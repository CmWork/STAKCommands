import json
from spirent.methodology.results.Info import (
    IteratorInfo,
    ActiveIterationInfo
    )
from spirent.methodology.results.Status import (
    Status,
    ActiveIterationStatus,
    )
from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumExecStatus,
    EnumDataFormat,
    EnumDataClass
    )
import spirent.methodology.results.IteratorUtils as iterator_utils
from spirent.methodology.results.ResultBase import ResultBase
import spirent.methodology.results.LogUtils as logger
from spirent.methodology.results.Iteration import Iteration
import spirent.methodology.results.ResultBllObjectInterface as result_obj
import spirent.methodology.results.ResultUtils as result_utils


class Iterator(ResultBase):
    def __init__(self, iterator_handle, iterator_result_object=None, iterator_param=None):
        super(Iterator, self).__init__(None, None, iterator_result_object)
        self._iterator_handle = iterator_handle
        self._completed_iteration_data = None
        self._active_iteration_info = None
        self._active_iteration_status = None
        self._active_child_iterator_data = None
        self._iterator_param = iterator_param
        self.set_iterator_result()

    @staticmethod
    def get_stc_property_Iterator():
        return 'Iterator'

    @property
    def stc_property_Iterator(self):
        return self.get_stc_property_Iterator()

    @property
    def stc_property_completed_data(self):
        return 'CompletedIterationData'

    @property
    def stc_property_child_iterator_data(self):
        return 'ActiveChildIteratorData'

    def set_iterator_result(self):
        logger.debug('Set iterator result object.')
        if self._stc_result_object is None:
            self._stc_result_object = iterator_utils.get_iterator(self._iterator_handle)
            if self._stc_result_object is None:
                self.create_new_iterator()
        logger.debug('Set iterator results object completed.')

    def create_new_iterator(self):
        logger.info('Create new iterator.')
        self._stc_result_object = iterator_utils.create_iterator_result()
        self.set_stc_object(self.stc_property_Iterator, str(self._iterator_handle))
        self._info = IteratorInfo(self._iterator_param)
        self._status = Status(EnumExecStatus.created)
        self.commit_info_status()
        logger.debug('Create new iterator completed.')
        logger.log_result_info_status(self._stc_result_object)

    def start_next_iteration(self, value, iteration_id):
        logger.info('start next iteration.')
        # make sure no active iteration running.
        if self.is_iteration_running():
            logger.warning('Complete iteration call missing for previous iteration.')
            self.complete_active_iteration()
        self._active_iteration_info = ActiveIterationInfo(value,
                                                          iteration_id,
                                                          self._iterator_param)
        self._active_iteration_info._start_time = result_utils.get_current_time_string()
        self._active_iteration_status = ActiveIterationStatus(EnumExecStatus.running)
        self.commit_active_info_status()
        logger.debug('start next iteration completed.')
        logger.log_result_info_status(self._stc_result_object)

    def complete_active_iteration(self, force_stop=False):
        logger.info('completea active iteration.')
        if not self.is_iteration_running():
            logger.error('No active iteration found to complete.')
            return
        logger.log_result_info_status(self._stc_result_object)
        self._active_iteration_info = ActiveIterationInfo()
        self.load_from_stc_object(self._active_iteration_info)
        self._active_iteration_status = ActiveIterationStatus()
        self.load_from_stc_object(self._active_iteration_status)
        if force_stop is True:
            self._active_iteration_status.exec_status = EnumExecStatus.stopped
        else:
            self._active_iteration_status.exec_status = EnumExecStatus.completed
        self._active_iteration_info._end_time = result_utils.get_current_time_string()
        result = self.generate_iteration_verdict()
        if result:
            self._active_iteration_status.verdict = result['verdict']
            self._active_iteration_info.result_file = result['resultFile']
            self._active_iteration_info.set_data_class(self._active_iteration_info,
                                                       EnumDataClass.iteration_result)
            self._active_iteration_info.set_data_format(self._active_iteration_info,
                                                        EnumDataFormat.none)
        else:
            self._active_iteration_status.verdict = EnumVerdict.none
            self._active_iteration_info.set_data_class(self._active_iteration_info,
                                                       EnumDataClass.iteration_result)
            self._active_iteration_info.set_data_format(self._active_iteration_info,
                                                        EnumDataFormat.none)
        self.save_active_iteration_data()
        self.reset_active_iteration_data()
        logger.info('completea active iteration completed.')

    def save_active_iteration_data(self):
        """Convert from Active iteration data to Iteration data
        """
        logger.info('Save active iteration data.')
        child_data = self.get_from_stc_as_dict(self.stc_property_child_iterator_data)
        if child_data:
            self._active_iteration_info.set_data_format(self._active_iteration_info,
                                                        EnumDataFormat.group)
            result = self._active_iteration_info.run_time_data
            result[self.get_data_dict_name()] = result_utils.wrap_data_as_single_group(child_data)
        else:
            result = self._active_iteration_info.run_time_data
        result[Status.get_dict_name()] = self._active_iteration_status.run_time_data
        self.append_stc_object_collection(
            self.stc_property_completed_data,
            json.dumps(result, separators=(',', ':'), sort_keys=False))
        logger.debug('Save active iteration data completed.')

    def generate_iteration_verdict(self):
        logger.info('Generate iteration verdict.')
        jsonResults = self.get_from_stc_collection_property_as_dict('JsonResults')
        if jsonResults and len(jsonResults) >= 0:
            return self.generate_iteration_result_file(jsonResults)
        else:
            return {}

    def generate_iteration_result_file(self, results):
        logger.info('Generate Iteration result file.')
        iteration = Iteration(self._active_iteration_info.run_time_data,
                              self._stc_result_object,
                              results,
                              self._active_iteration_status.run_time_data,)
        return iteration.generate_report()

    def complete(self, force_stop):
        logger.info('Complete - End iterator.')
        if self.is_iteration_running():
            logger.warning('Complete iteration call missing before end iterator.')
            self.complete_active_iteration(force_stop)
        self.load_all_iterator_data()
        if force_stop is True:
            self._status.exec_status = EnumExecStatus.stopped
        else:
            self._status.exec_status = EnumExecStatus.completed
        self._status.verdict = EnumVerdict.none
        self._info.set_data_format(self._info, EnumDataFormat.group)
        self._info.set_data_class(self._info, EnumDataClass.iterator_result)
        iteratorData = self._info.run_time_data
        iteratorData[self._status.dict_name] = self._status.run_time_data
        allData = self.get_from_stc_collection_property_as_dict(self.stc_property_completed_data)
        iteratorData[self.get_data_dict_name()] = result_utils.wrap_data_as_single_group(allData)
        self._stc_result_object.MarkDelete()
        logger.debug('Complete - End iterator completed.')
        return iteratorData

    def load_all_iterator_data(self):
        self._info = IteratorInfo()
        self.load_from_stc_object(self._info)
        self._status = Status()
        self.load_from_stc_object(self._status)

    def add_child_iterator_data(self, data):
        logger.info('Add child iterator data.')
        json_data = json.dumps(data, separators=(',', ':'), sort_keys=False)
        self.set_stc_object(self.stc_property_child_iterator_data, json_data)
        logger.debug('Add child iterator data completed.')

    def commit_active_info_status(self):
        self.set_stc_object_from_object(self._active_iteration_info)
        self.set_stc_object_from_object(self._active_iteration_status)

    def reset_active_iteration_data(self):
        self.set_stc_object(self._active_iteration_info.stc_property_name, "")
        self.set_stc_object(self._active_iteration_status.stc_property_name, "")
        self.set_stc_object(self.stc_property_child_iterator_data, "")
        self._stc_result_object.SetCollection(result_obj.get_stc_json_collection_name(), [])

    def is_iteration_running(self):
        # complete iteration reset active iteration data. check that to find status.
        status_data = self.get_from_stc_as_dict(ActiveIterationStatus.get_stc_property_name())
        if status_data:
            return True
        return False

    def get_last_iteration_data(self):
        logger.debug('Get last iteration data.')
        idata = self.get_from_stc_collection_property_as_dict(self.stc_property_completed_data)
        if not idata:
            return None
        return idata[-1]

    