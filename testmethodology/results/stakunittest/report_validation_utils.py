import beta.methodology.utils.ReportUtils as ru
import jsonschema
import json
import os
from StcIntPythonPL import *
from spirent.methodology.results.ResultEnum import (
    EnumDataFormat,
    EnumDataClass
    )
from spirent.methodology.results.ProviderConst import ProviderConst as pc
import spirent.methodology.results.stakunittest.result_unit_test_utils as test_utils
from spirent.methodology.results.ResultConst import ResultConst as rc

report_schema_file = 'STAKCommands/beta/methodology/utils/report_schema.json'


def validate_report_schema(filename=None):
    if filename is None:
        report_data = ru.get_report_data_as_dictionary()
    else:
        with open(filename) as file:
            report_data = json.load(file)
    assert report_data is not {}
    with open(report_schema_file) as rschema:
        schema = json.load(rschema)
    jsonschema.validate(report_data, schema)
    return report_data


def get_report_file_list():
    stc_sys = CStcSystem.Instance()
    trs = stc_sys.GetObject('Project').GetObject('TestResultSetting')
    filename = trs.Get('CurrentJsonResultFileName')
    assert os.path.isfile(filename) is True
    result_dir = os.path.dirname(filename)
    filelist = [f for f in os.listdir(result_dir) if os.path.isfile(os.path.join(result_dir, f))]
    data = {}
    data['resultDir'] = result_dir
    data['fileList'] = filelist
    return data


def validate_result_file_list(expected_list, actual_list):
    assert sorted(expected_list) == sorted(actual_list)


def validate_result_file_Schema(file_data):
    for filename in file_data['fileList']:
        validate_report_schema(os.path.join(file_data['resultDir'], filename))


def verify_summary_file_info():
    report_data = ru.get_report_data_as_dictionary()
    assert report_data[pc.DATA_FORMAT] == EnumDataFormat.group
    assert report_data[pc.CLASS] == EnumDataClass.test_report
    data = report_data[pc.INFO]
    assert ('startTime' in data) is True
    assert ('endTime' in data) is True
    assert ('version' in data) is True
    return report_data


def verify_summary_iteration_result_type1(result_list, fs_list, file_list):
    index = 0
    for result in result_list:
        assert result[pc.DATA_FORMAT] == EnumDataFormat.none
        assert result[pc.CLASS] == EnumDataClass.iteration_result
        info_data = result[pc.INFO]
        assert ('startTime' in info_data) is True
        assert ('endTime' in info_data) is True
        assert ('version' in info_data) is False
        assert info_data['param'] == 'FrameSize'
        assert info_data['value'] == fs_list[index]
        index += 1
        assert info_data['id'] == index
        assert info_data['resultFile'] == file_list[index]
        assert ru.compare_dict_data_using_json_string(test_utils.status_failed_7,
                                                      result[pc.STATUS]) is True


def verify_summary_iteration_result_type2(result_list, fs_list, load_list, file_list):
    fz_index = 0
    file_index = 1
    for result in result_list:
        assert result[pc.DATA_FORMAT] == EnumDataFormat.group
        assert result[pc.CLASS] == EnumDataClass.iteration_result
        info_data = result[pc.INFO]
        assert ('startTime' in info_data) is True
        assert ('endTime' in info_data) is True
        assert ('version' in info_data) is False
        assert ('resultFile' in info_data) is False
        assert info_data['param'] == 'FrameSize'
        assert info_data['value'] == fs_list[fz_index]
        fz_index += 1
        assert info_data['id'] == fz_index
        assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_5,
                                                      result[pc.STATUS]) is True
        # load iterator
        assert len(result[pc.DATA][rc.CHILDREN]) == 1
        load_data = ru.get_data_from_dictionary(result, 'data.children.0')
        assert load_data[pc.CLASS] == EnumDataClass.iterator_result
        assert load_data[pc.DATA_FORMAT] == EnumDataFormat.group
        assert load_data[pc.INFO]['param'] == 'Load'
        assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_5,
                                                      load_data[pc.STATUS]) is True
        itr_list = load_data[pc.DATA][rc.CHILDREN]
        assert len(itr_list) == len(load_list)
        load_index = 0
        for itr_load in itr_list:
            assert itr_load[pc.DATA_FORMAT] == EnumDataFormat.none
            assert itr_load[pc.CLASS] == EnumDataClass.iteration_result
            load_info = itr_load[pc.INFO]
            assert ('startTime' in load_info) is True
            assert ('endTime' in load_info) is True
            assert ('version' in load_info) is False
            assert load_info['param'] == 'Load'
            assert load_info['value'] == load_list[load_index]
            load_index += 1
            assert load_info['id'] == load_index
            assert load_info['resultFile'] == file_list[file_index]
            assert ru.compare_dict_data_using_json_string(test_utils.status_failed_7,
                                                          itr_load[pc.STATUS]) is True
            file_index += 1
