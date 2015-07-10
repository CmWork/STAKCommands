from spirent.methodology.results.MethodologyBase import MethodologyBase
from spirent.methodology.results.ResultEnum import (
    EnumDataFormat,
    EnumDataClass
)
from spirent.methodology.results.ResultConst import ResultConst as rc


class Info(MethodologyBase):

    @staticmethod
    def get_dict_name():
        return 'info'

    @staticmethod
    def get_stc_property_name():
        return 'Info'

    @staticmethod
    def get_param_dict_name():
        return 'param'

    @staticmethod
    def get_value_dict_name():
        return 'value'

    @staticmethod
    def get_id_dict_name():
        return 'id'

    @staticmethod
    def get_result_file_dict_name():
        return 'resultFile'

    @property
    def dict_name(self):
        return self.get_dict_name()

    @property
    def stc_property_name(self):
        return self.get_stc_property_name()

    @staticmethod
    def get_data_format_dict_name():
        return 'dataFormat'

    @staticmethod
    def get_data_class_dict_name():
        return 'class'

    @staticmethod
    def set_data_format(self, value):
        self._data_format = value

    @staticmethod
    def set_data_class(self, value):
        self._data_class = value


class TestInfo(Info):
    def __init__(self, test_name='Not Defined'):
        self._test_name = test_name
        self._data_format = EnumDataFormat.group
        self._data_class = EnumDataClass.test_report
        self._test_variables = {}
        self._start_time = ""
        self._end_time = ""

    @property
    def run_time_data(self):
        info = {}
        info[self.get_data_class_dict_name()] = self._data_class
        info[self.get_data_format_dict_name()] = self._data_format
        infodata = {}
        infodata['name'] = self._test_name
        infodata['startTime'] = self._start_time
        infodata['endTime'] = self._end_time
        infodata['testVariables'] = self._test_variables
        info[self.get_dict_name()] = infodata
        return info

    def load_from_dict(self, dict_data):
        self._data_class = dict_data[self.get_data_class_dict_name()]
        self._data_format = dict_data[self.get_data_format_dict_name()]
        self._test_name = dict_data[self.get_dict_name()]['name']
        self._start_time = dict_data[self.get_dict_name()]['startTime']
        self._end_time = dict_data[self.get_dict_name()]['endTime']
        self._test_variables = dict_data[self.get_dict_name()]['testVariables']

    def add_test_variables(self, dict_data):
        self._test_variables = dict(self._test_variables.items() + dict_data.items())

    def get_final_info_data(self):
        all = self.run_time_data
        all[self.get_dict_name()] = dict(all[self.get_dict_name()].items() +
                                         all[self.get_dict_name()]['testVariables'].items())
        del all[self.get_dict_name()]['testVariables']
        return all


class IteratorInfo(Info):
    def __init__(self, iterator_key='Not Defined'):
        self._key = iterator_key
        self._data_format = None
        self._data_class = None

    @property
    def run_time_data(self):
        info = {}
        if self._data_class is not None:
            info[self.get_data_class_dict_name()] = self._data_class
        if self._data_format is not None:
            info[self.get_data_format_dict_name()] = self._data_format
        infodata = {}
        infodata[self.get_param_dict_name()] = self._key
        infodata['reportGroup'] = rc.ITERATOR_REPORT_GROUP
        info[self.get_dict_name()] = infodata
        return info

    def load_from_dict(self, dict_data):
        self._key = dict_data[self.get_dict_name()][self.get_param_dict_name()]
        if self.get_data_class_dict_name() in dict_data:
            self._data_class = dict_data[self.get_data_class_dict_name()]
        if self.get_data_format_dict_name() in dict_data:
            self._data_format = dict_data[self.get_data_format_dict_name()]


class IterationInfo(Info):
    def __init__(self, iteration_value=None, iteration_id=None, param=None):
        self._value = iteration_value
        self._id = iteration_id
        self._result_file = None
        self._param = param
        self._data_format = None
        self._data_class = None
        self._start_time = ""
        self._end_time = ""

    @property
    def result_file(self):
        return self._result_file

    @result_file.setter
    def result_file(self, filename):
        self._result_file = filename

    def load_from_dict(self, dict_data):
        infodata = dict_data[self.get_dict_name()]
        self._value = infodata[self.get_value_dict_name()]
        self._id = infodata[self.get_id_dict_name()]
        self._start_time = infodata['startTime']
        self._end_time = infodata['endTime']
        self._param = infodata[self.get_param_dict_name()]
        if self.get_result_file_dict_name() in infodata:
            self._result_file = infodata[self.get_result_file_dict_name()]
        if self.get_data_format_dict_name() in dict_data:
            self._data_format = dict_data[self.get_data_format_dict_name()]
        if self.get_data_class_dict_name() in dict_data:
            self._data_class = dict_data[self.get_data_class_dict_name()()]

    @property
    def run_time_data(self):
        info = {}
        if self._data_format is not None:
            info[self.get_data_format_dict_name()] = self._data_format
        if self._data_class is not None:
            info[self.get_data_class_dict_name()] = self._data_class
        infodata = {}
        infodata[self.get_value_dict_name()] = self._value
        infodata[self.get_id_dict_name()] = self._id
        infodata[self.get_param_dict_name()] = self._param
        infodata['startTime'] = self._start_time
        infodata['endTime'] = self._end_time
        if self._result_file is not None:
            infodata[self.get_result_file_dict_name()] = self._result_file
        info[self.get_dict_name()] = infodata
        return info


class ActiveIterationInfo(IterationInfo):

    @staticmethod
    def get_stc_property_name():
        return 'ActiveIterationInfo'

    @property
    def stc_property_name(self):
        return self.get_stc_property_name()
