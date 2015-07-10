import json
from StcIntPythonPL import *
from spirent.methodology.results.MethodologyBase import MethodologyBase


class ResultBase(MethodologyBase):
    def __init__(self, info=None, status=None, result_object=None):
        self._stc_result_object = result_object
        self._info = info
        self._status = status

    def set_result_objact(self, obj):
        if obj is None:
            raise Exception('None is not a valid result object type.')
        self._stc_result_object = obj

    def commit_info_status(self):
        self.set_stc_object_from_object(self._info)
        self.set_stc_object_from_object(self._status)

    def set_stc_object_from_object(self, source):
        self.set_stc_object(source.stc_property_name, source.run_time_json)

    def set_stc_object(self, stc_prop_name, dataString):
        self._stc_result_object.Set(stc_prop_name, dataString)

    def append_stc_object_collection(self, property_name, data):
        existing_data = self.get_from_stc_collection_property(property_name)
        existing_data.append(data)
        self._stc_result_object.SetCollection(property_name, existing_data)

    def load_from_stc_object(self, source):
        source.load_from_string(self._stc_result_object.Get(source.stc_property_name))

    def get_from_stc_collection_property(self, property_name):
        return self._stc_result_object.GetCollection(property_name)

    def get_from_stc_collection_property_as_dict(self, property_name):
        stringCollection = self._stc_result_object.GetCollection(property_name)
        data = []
        for string_data in stringCollection:
            if string_data:
                data.append(json.loads(string_data))
        return data

    def get_from_stc_as_dict(self, property_name):
        stcString = self._stc_result_object.Get(property_name)
        if stcString is None or not stcString:
            return {}
        else:
            return json.loads(self._stc_result_object.Get(property_name))
