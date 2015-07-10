import json


class MethodologyBase(object):

    @staticmethod
    def get_data_dict_name():
        return 'data'

    @property
    def run_time_json(self):
        return json.dumps(self.run_time_data, separators=(',', ':'), sort_keys=False)

    def load_from_string(self, string_data):
        if string_data:
            data = json.loads(string_data)
            self.load_from_dict(data)
        else:
            raise Exception('Load from string failed for empty string.')