import json


def uni2str(data):
    if type(data) == unicode:
        return str(data)
    if type(data) == list:
        return [uni2str(item) for item in data]
    if type(data) == dict:
        ret = {}
        for key, value in data.iteritems():
            new_key = uni2str(key)
            new_val = uni2str(value)
            ret[new_key] = new_val
        return ret
    return data


def loads(json_str):
    data = json.loads(json_str)
    return uni2str(data)


def dumps(data):
    return json.dumps(data)
