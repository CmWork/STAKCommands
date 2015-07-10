from StcIntPythonPL import *
from spirent.methodology.results.ResultInterface import ResultInterface as RI
import spirent.methodology.results.stakunittest.result_unit_test_utils as test_utils
from spirent.methodology.results.ProviderConst import ProviderConst as pc
from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumExecStatus,
    EnumDataClass,
    EnumDataFormat
    )
import spirent.methodology.results.stakunittest.report_validation_utils as vu
import beta.methodology.utils.ReportUtils as ru
from spirent.methodology.results.ResultConst import ResultConst as rc


def test_one_iterator(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_5,
                                                  sum_data[pc.STATUS]) is True
    # get iterator result
    fz_data = ru.get_data_from_dictionary(sum_data, 'data.children.0.data.children.0')
    assert fz_data[pc.CLASS] == EnumDataClass.iterator_result
    assert fz_data[pc.DATA_FORMAT] == EnumDataFormat.group
    assert fz_data[pc.INFO]['param'] == 'FrameSize'
    assert ru.compare_dict_data_using_json_string(test_utils.status_iterator_6,
                                                  fz_data[pc.STATUS]) is True
    # iteration results
    itr_list = fz_data[pc.DATA][rc.CHILDREN]
    assert len(itr_list) == len(framesizelist)
    vu.verify_summary_iteration_result_type1(itr_list,
                                             framesizelist,
                                             test_utils.result_file_list_1)


def test_one_iterator_stop(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        RI.complete_iteration()
    RI.end_iterator()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)
    # verify exec status stopped
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_stopped_8,
                                                  sum_data[pc.STATUS]) is True


def test_one_iterator_no_start(stc, resource_cleanup):
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)
    vu.verify_summary_file_info()


def test_one_iterator_no_complete_iteration(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        # result framwork should take core of missing call.
        # RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)


def test_one_iterator_no_end_iterator(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        RI.complete_iteration()
    # result framwork should take core of missing end iterator call.
    # RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)


def test_one_iterator_missing_most_calls(stc, resource_cleanup):
    # skip create/start
    # RI.create_test()
    # RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        # RI.complete_iteration()
    # RI.end_iterator()
    RI.end_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)
    vu.verify_summary_file_info()


def test_one_iterator_missing_most_calls_stop(stc, resource_cleanup):
    # skip create/start
    # RI.create_test()
    # RI.start_test()
    framesizelist = [64, 128, 256]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        RI.add_provider_result(test_utils.dummy_verify_result_failed)
        fs_itr_id += 1
        # RI.complete_iteration()
    # RI.end_iterator()
    # RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_1)
    vu.validate_result_file_Schema(file_data)
    sum_data = vu.verify_summary_file_info()
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_stopped_8,
                                                  sum_data[pc.STATUS]) is True


def test_end_iterator_without_iteration(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    data = vu.validate_report_schema()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_1,
                                                  data[pc.STATUS]) is True
    assert ru.compare_dict_data_using_json_string(test_utils.data_empty_1,
                                                  data[pc.DATA]) is True


def test_multiple_iterator(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            RI.complete_iteration()
        RI.end_iterator()
        # frame size
        fs_itr_id += 1
        RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_2)
    vu.validate_result_file_Schema(file_data)
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_complete_5,
                                                  sum_data[pc.STATUS]) is True
    fz_data = ru.get_data_from_dictionary(sum_data, 'data.children.0.data.children.0')
    assert fz_data[pc.CLASS] == EnumDataClass.iterator_result
    assert fz_data[pc.DATA_FORMAT] == EnumDataFormat.group
    assert fz_data[pc.INFO]['param'] == 'FrameSize'
    assert ru.compare_dict_data_using_json_string(test_utils.status_iterator_6,
                                                  fz_data[pc.STATUS]) is True
    itr_list = fz_data[pc.DATA][rc.CHILDREN]
    assert len(itr_list) == len(framesizelist)
    vu.verify_summary_iteration_result_type2(itr_list,
                                             framesizelist,
                                             loadlist,
                                             test_utils.result_file_list_2)


def test_multiple_iterator_add_root_result(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64]
    loadlist = [10]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            # add to root
            RI.add_provider_result_to_root(test_utils.dummy_verify_result_passed)
            load_id += 1
            RI.complete_iteration()
        RI.end_iterator()
        # frame size
        fs_itr_id += 1
        RI.complete_iteration()
    RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_3)
    vu.validate_result_file_Schema(file_data)
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_pass_2,
                                                  sum_data[pc.STATUS]) is True
    # 2 root results, iterator and added root result
    root_list = sum_data[pc.DATA][rc.CHILDREN]
    assert len(root_list) == 2
    result_data = ru.get_data_from_dictionary(root_list, '0.data.children.0')
    fz_data = ru.get_data_from_dictionary(root_list, '1.data.children.0')
    assert fz_data[pc.INFO]['param'] == 'FrameSize'
    # verify result data
    expected_string = ru.get_json_string(test_utils.dummy_verify_result_passed)
    assert ru.compare_dict_data_using_json_string(expected_string, result_data) is True


def test_multiple_iterator_no_complete_end(stc, resource_cleanup):
    # test must run all 6 iterations and generate reports
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            # RI.complete_iteration()
        # missing call should be handled by results
        # RI.end_iterator()
        # frame size
        fs_itr_id += 1
        # RI.complete_iteration()
    # RI.end_iterator()
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_2)
    vu.validate_result_file_Schema(file_data)


def test_multiple_iterator_abort_inner_loop(stc, resource_cleanup):
    """
    test must complete 1 iterations and generate report with summary.
    1. framesize = 64, load = 10
    """
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            break
        break
    # abort test
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_3)
    vu.validate_result_file_Schema(file_data)


def test_multiple_iterator_abort_inner_loop_stop(stc, resource_cleanup):
    """
    test must complete 1 iterations and generate report with summary.
    1. framesize = 64, load = 10
    """
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            break
        break
    # abort test
    # RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_3)
    vu.validate_result_file_Schema(file_data)


def test_multiple_iterator_abort_outer_loop(stc, resource_cleanup):
    """
    test must complete 2 iterations and generate report with summary.
    1. framesize = 64, load = 10
    2. framesize = 64, load = 20
    """
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            RI.complete_iteration()
        break
    RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_4)
    vu.validate_result_file_Schema(file_data)


def test_multiple_iterator_abort_outer_loop_stop(stc, resource_cleanup):
    """
    test must complete 2 iterations and generate report with summary.
    1. framesize = 64, load = 10
    2. framesize = 64, load = 20
    """
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            load_id += 1
            RI.complete_iteration()
        break
    # RI.end_test()
    RI.stop_test()
    file_data = vu.get_report_file_list()
    vu.validate_result_file_list(file_data['fileList'], test_utils.result_file_list_4)
    vu.validate_result_file_Schema(file_data)
    sum_data = vu.verify_summary_file_info()
    assert ru.compare_dict_data_using_json_string(test_utils.status_exec_stopped_8,
                                                  sum_data[pc.STATUS]) is True


def test_multiple_iterator_get_status(stc, resource_cleanup):
    RI.create_test()
    RI.start_test()
    framesizelist = [64, 128, 256]
    loadlist = [10, 20]
    fs_itr_id = 1
    fs_iterator_handle = 12123
    load_handle = 5555
    assert RI.get_last_iteration_info_status(fs_iterator_handle) is None
    assert RI.get_last_iteration_info_status(load_handle) is None
    for fs in framesizelist:
        RI.set_iterator_current_value(fs_iterator_handle, 'FrameSize', fs, fs_itr_id)
        if fs_itr_id == 1:
            assert RI.get_last_iteration_info_status(fs_iterator_handle) is None
        else:
            assert RI.get_last_iteration_info_status(fs_iterator_handle) is not None
        load_id = 1
        for load in loadlist:
            RI.set_iterator_current_value(load_handle, 'Load', load, load_id)
            if load_id == 1:
                assert RI.get_last_iteration_info_status(load_handle) is None
            else:
                assert RI.get_last_iteration_info_status(load_handle) is not None
            RI.add_provider_result(test_utils.dummy_verify_result_failed)
            RI.add_provider_result(test_utils.dummy_verify_result_passed)
            if load_id == 1:
                assert RI.get_last_iteration_info_status(load_handle) is None
            else:
                assert RI.get_last_iteration_info_status(load_handle) is not None
            load_id += 1
            RI.complete_iteration()
            last_itr_data = RI.get_last_iteration_info_status(load_handle)
            assert last_itr_data is not None
            assert last_itr_data[pc.STATUS][pc.VERDICT] == EnumVerdict.failed
            assert last_itr_data[pc.STATUS][pc.EXEC_STATUS] == EnumExecStatus.completed
        RI.end_iterator()
        # result object should be deleted for load
        assert RI.get_last_iteration_info_status(load_handle) is None
        # frame size
        if fs_itr_id == 1:
            assert RI.get_last_iteration_info_status(fs_iterator_handle) is None
        else:
            assert RI.get_last_iteration_info_status(fs_iterator_handle) is not None
        fs_itr_id += 1
        RI.complete_iteration()
        last_itr_data = RI.get_last_iteration_info_status(fs_iterator_handle)
        assert last_itr_data is not None
        assert last_itr_data[pc.STATUS][pc.VERDICT] == EnumVerdict.none
        assert last_itr_data[pc.STATUS][pc.EXEC_STATUS] == EnumExecStatus.completed
    RI.end_iterator()
    # result object should be deleted for framesize
    assert RI.get_last_iteration_info_status(fs_iterator_handle) is None
    RI.end_test()
    RI.stop_test()
