from StcIntPythonPL import *
from spirent.methodology.results.ResultInterface import ResultInterface as RI
import spirent.methodology.results.stakunittest.result_unit_test_utils as test_utils
import spirent.methodology.results.stakunittest.report_validation_utils as vu
from spirent.methodology.results.ProviderConst import ProviderConst as pc
from spirent.methodology.results.ResultConst import ResultConst as rc
import beta.methodology.utils.ReportUtils as ru


def test_empty_test(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_1,
                                                  data[pc.STATUS]) is True
    assert ru.compare_dict_data_using_json_string(test_utils.data_empty_1,
                                                  data[pc.DATA]) is True
    # validate start, end and version exist
    assert ('startTime' in data[pc.INFO]) is True
    assert ('endTime' in data[pc.INFO]) is True
    assert ('version' in data[pc.INFO]) is True


def test_empty_test_no_create(stc, resource_cleanup):
    RI.start_test()
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_1,
                                                  data[pc.STATUS]) is True
    assert ru.compare_dict_data_using_json_string(test_utils.data_empty_1,
                                                  data[pc.DATA]) is True


def test_single_provider_test(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    RI.add_provider_result(test_utils.dummy_verify_result_passed)
    # negative test case for last iteration status
    assert RI.get_last_iteration_info_status(1111) is None
    info = {}
    test_name = 'My test name'
    info['name'] = test_name
    description = 'Details about my test'
    info['testDescription'] = description
    test_id = 'mytestId-1233'
    info['id'] = test_id
    RI.add_data_to_test_info(info)
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    data[pc.INFO]['name'] = test_name
    data[pc.INFO]['testDescription'] = description
    data[pc.INFO]['id'] = test_id
    assert ru.compare_dict_data_using_json_string(test_utils.status_pass_2,
                                                  data[pc.STATUS]) is True
    drv_data = data[pc.DATA][rc.CHILDREN][0][pc.DATA][rc.CHILDREN][0]
    expected_string = ru.get_json_string(test_utils.dummy_verify_result_passed)
    assert ru.compare_dict_data_using_json_string(expected_string, drv_data) is True


def test_single_provider_root(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    RI.add_provider_result_to_root(test_utils.dummy_verify_result_passed)
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_pass_2,
                                                  data[pc.STATUS]) is True
    drv_data = data[pc.DATA][rc.CHILDREN][0][pc.DATA][rc.CHILDREN][0]
    expected_string = ru.get_json_string(test_utils.dummy_verify_result_passed)
    assert ru.compare_dict_data_using_json_string(expected_string, drv_data) is True


def test_single_provider_test_no_start(stc, resource_cleanup):
    RI.add_provider_result(test_utils.dummy_verify_result_passed)
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_pass_2,
                                                  data[pc.STATUS]) is True
    drv_data = data[pc.DATA][rc.CHILDREN][0][pc.DATA][rc.CHILDREN][0]
    expected_string = ru.get_json_string(test_utils.dummy_verify_result_passed)
    assert ru.compare_dict_data_using_json_string(expected_string, drv_data) is True


def test_end_test_only(stc, resource_cleanup):
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_1,
                                                  data[pc.STATUS]) is True
    assert ru.compare_dict_data_using_json_string(test_utils.data_empty_1,
                                                  data[pc.DATA]) is True


def test_stop_test_only(stc, resource_cleanup):
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_stopped_3,
                                                  data[pc.STATUS]) is True
    assert ru.compare_dict_data_using_json_string(test_utils.data_empty_1,
                                                  data[pc.DATA]) is True


def test_single_provider_stop_test(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    RI.add_provider_result(test_utils.dummy_verify_result_passed)
    # stop test without end test
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_pass_stopped_4,
                                                  data[pc.STATUS]) is True
    drv_data = data[pc.DATA][rc.CHILDREN][0][pc.DATA][rc.CHILDREN][0]
    expected_string = ru.get_json_string(test_utils.dummy_verify_result_passed)
    assert ru.compare_dict_data_using_json_string(expected_string, drv_data) is True
