"""This file provides utility functions to manipulate the meta files used for
a Spirent TestCenter methodology. Functionality covered are the JSON
configuration files for a given methodology.
"""

__revision__ = "$Revision: #2 $"
__date__ = "$DateTime: 2015/06/24 17:24:58 $"


import os
import json
import sys
import traceback
from StcIntPythonPL import PLLogger
from spirent.methodology.utils.json_utils import dumps as ju_dumps


def load_json_object(filename):
    '''
    Load a JSON file into a Python object.
    This function returns an error string, followed by a JSON object.
    '''
    if not os.path.exists(filename):
        return "File {} does not exist", None
    try:
        with open(filename) as fd:
            u_obj = json.load(fd)
            return "", ju_dumps(u_obj)
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(*exc_info[0:2])
        err_msg = fail_list[0] if len(fail_list) == 1 else '\n'.join(fail_list)
        return err_msg, None


def extract_obj_key_from_file(meta_file, key):
    '''
    Given a meta.json filename, extract a given key and return it.
    Failures will be logged as errors, and if the key is not found, a blank
    string is returned
    '''
    logger = PLLogger.GetLogger('methodology')
    err_msg, obj = load_json_object(meta_file)
    if err_msg:
        logger.LogError("meta_utils.extract_obj_key_from_file: {}"
                        .format(err_msg))
        return ""
    return obj.get(key, "")


def extract_methodology_key_from_file(meta_file):
    '''
    Given the meta file path, extract the methodology key
    '''
    return extract_obj_key_from_file(meta_file, 'methodology_key')


def extract_methodology_name_from_file(meta_file):
    '''
    Given the meta file path, extract the methodology display name
    '''
    return extract_obj_key_from_file(meta_file, 'display_name')


def extract_test_labels_from_file(meta_file):
    '''
    Given the meta file path, extract the methodology's labels
    '''
    result = extract_obj_key_from_file(meta_file, 'labels')
    return result if type(result) == list else []


def extract_test_case_name_from_file(meta_file):
    '''
    Given the meta file path, extract the test case name
    '''
    return extract_obj_key_from_file(meta_file, 'test_case_name')


def extract_test_case_key_from_file(meta_file):
    '''
    Given the meta file path, extract the test case key
    '''
    return extract_obj_key_from_file(meta_file, 'test_case_key')
