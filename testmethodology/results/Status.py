from spirent.methodology.results.MethodologyBase import MethodologyBase
from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumExecStatus
    )


class Status(MethodologyBase):
    def __init__(self,
                 verdict=EnumVerdict.none,
                 verdict_text='Not Defined',
                 execution_status=EnumExecStatus.none):
        self._verdict = verdict
        self._verdict_text = verdict_text
        self._exec_status = execution_status
        self._verdict_provider_name = None
        self._apply_verdict_to_summary = None

    @staticmethod
    def get_stc_property_name():
        return 'Status'

    @staticmethod
    def get_dict_name():
        return 'status'

    @staticmethod
    def get_verdict_dict_name():
        return 'verdict'

    @staticmethod
    def get_verdict_text_dict_name():
        return 'verdictExplanation'

    @staticmethod
    def get_exec_status_dict_name():
        return 'execStatus'

    @staticmethod
    def get_verdict_provider_dict_name():
        return 'verdictProviderName'

    @staticmethod
    def get_apply_verdict_dict_name():
        return 'promoteVerdict'

    @property
    def stc_property_name(self):
        return self.get_stc_property_name()

    @property
    def dict_name(self):
        return self.get_dict_name()

    @property
    def verdict(self):
        return self._verdict

    @verdict.setter
    def verdict(self, verdict):
        self._verdict = verdict

    @property
    def verdict_text(self):
        return self._verdict_text

    @verdict_text.setter
    def verdict_text(self, verdict_text):
        self._verdict_text = verdict_text

    @property
    def exec_status(self):
        return self._exec_status

    @exec_status.setter
    def exec_status(self, status):
        self._exec_status = status

    @property
    def verdict_provider_name(self):
        return self._verdict_provider_name

    @verdict_provider_name.setter
    def verdict_provider_name(self, name):
        self._verdict_provider_name = name

    @property
    def apply_verdict_to_summary(self):
        return self._apply_verdict_to_summary

    @apply_verdict_to_summary.setter
    def apply_verdict_to_summary(self, verdict):
        self._apply_verdict_to_summary = verdict

    @property
    def run_time_data(self):
        status = {}
        status[self.get_verdict_dict_name()] = self._verdict
        status[self.get_verdict_text_dict_name()] = self._verdict_text
        status[self.get_exec_status_dict_name()] = self._exec_status
        if self._verdict_provider_name is not None:
            status[self.get_verdict_provider_dict_name()] = self._verdict_provider_name
        if self._apply_verdict_to_summary is not None:
            status[self.get_apply_verdict_dict_name()] = self._apply_verdict_to_summary
        return status

    def load_from_dict(self, data):
        self._verdict = data[self.get_verdict_dict_name()]
        self._verdict_text = data[self.get_verdict_text_dict_name()]
        self._exec_status = data[self.get_exec_status_dict_name()]
        if self.get_verdict_provider_dict_name() in data:
            self._verdict_provider_name = data[self.get_verdict_provider_dict_name()]
        if self.get_apply_verdict_dict_name() in data:
            self._apply_verdict_to_summary = data[self.get_apply_verdict_dict_name()]


class ActiveIterationStatus(Status):

    @staticmethod
    def get_stc_property_name():
        return 'ActiveIterationStatus'

    @property
    def stc_property_name(self):
        return self.get_stc_property_name()
