from StcIntPythonPL import *
import spirent.methodology.results.ResultUtils as ru
import spirent.methodology.results.stakunittest.result_unit_test_utils as test_utils
from spirent.methodology.results.ResultConst import ResultConst as RC
from spirent.methodology.results.ProviderConst import ProviderConst as pc


def test_wrap_data_as_single_group(stc, resource_cleanup):
    data = []
    data.append(test_utils.dummy_verify_result_failed)
    data.append(test_utils.dummy_verify_result_passed)
    gdata = ru.wrap_data_as_single_group(data)
    assert gdata is not None
    assert gdata[RC.TAG] == RC.ALL_GROUPS
    assert (RC.CHILDREN in gdata) is True
    gdata = gdata[RC.CHILDREN]
    assert len(gdata) == 2
    assert gdata[0][pc.INFO][pc.REPORT_GROUP] == 'GROUP_1'
    assert gdata[1][pc.INFO][pc.REPORT_GROUP] == 'SUMMARY'

    gdata = ru.wrap_data_as_single_group(test_utils.dummy_verify_result_failed)
    assert gdata is not None
    assert gdata[RC.TAG] == RC.ALL_GROUPS
    assert (RC.CHILDREN in gdata) is True
    gdata = gdata[RC.CHILDREN]
    assert len(gdata) == 1
    assert gdata[0][pc.INFO][pc.REPORT_GROUP] == 'GROUP_1'


def test_group_data_using_report_group(stc, resource_cleanup):
    data = []
    gdata = ru.group_data_using_report_group(data)
    assert gdata is not None
    assert gdata[RC.TAG] == RC.ALL_GROUPS
    assert (RC.CHILDREN in gdata) is True
    assert len(gdata[RC.CHILDREN]) == 0

    data = []
    data.append(test_utils.result_group_2_3)
    data.append(test_utils.dummy_verify_result_failed)
    data.append(test_utils.result_group_2_1)
    data.append(test_utils.dummy_verify_result_passed)
    data.append(test_utils.result_group_5)
    data.append(test_utils.result_group_2_2)

    gdata = ru.group_data_using_report_group(data)
    assert gdata is not None
    assert gdata[RC.TAG] == RC.ALL_GROUPS
    assert (RC.CHILDREN in gdata) is True
    assert len(gdata[RC.CHILDREN]) == 4
    cdata0 = gdata[RC.CHILDREN][0]
    cdata1 = gdata[RC.CHILDREN][1]
    cdata2 = gdata[RC.CHILDREN][2]
    cdata3 = gdata[RC.CHILDREN][3]
    assert (pc.DATA in cdata0) is True
    assert (pc.DATA in cdata1) is True
    assert (pc.DATA in cdata2) is True
    assert (pc.DATA in cdata3) is True
    data0 = cdata0[pc.DATA]
    data1 = cdata1[pc.DATA]
    data2 = cdata2[pc.DATA]
    data3 = cdata3[pc.DATA]
    assert len(data0[RC.CHILDREN]) == 1
    assert len(data1[RC.CHILDREN]) == 1
    assert len(data2[RC.CHILDREN]) == 3
    assert len(data3[RC.CHILDREN]) == 1
    assert data0[RC.TAG] == "Report Group SUMMARY"
    assert data1[RC.TAG] == "Report Group GROUP_1"
    assert data2[RC.TAG] == "Report Group GROUP_2"
    assert data3[RC.TAG] == "Report Group GROUP_5"

    assert data0[RC.CHILDREN][0][pc.INFO][pc.REPORT_GROUP] == 'SUMMARY'
    assert data1[RC.CHILDREN][0][pc.INFO][pc.REPORT_GROUP] == 'GROUP_1'
    assert data2[RC.CHILDREN][0][pc.INFO][pc.REPORT_GROUP] == 'GROUP_2'
    assert data2[RC.CHILDREN][1][pc.INFO][pc.REPORT_GROUP] == 'GROUP_2'
    assert data2[RC.CHILDREN][2][pc.INFO][pc.REPORT_GROUP] == 'GROUP_2'
    assert data3[RC.CHILDREN][0][pc.INFO][pc.REPORT_GROUP] == 'GROUP_5'

    text0 = test_utils.dummy_verify_result_passed[pc.INFO][RC.NAME]
    text1 = test_utils.dummy_verify_result_failed[pc.INFO][RC.NAME]
    text2 = test_utils.result_group_2_3[pc.INFO][RC.NAME]
    text3 = test_utils.result_group_2_1[pc.INFO][RC.NAME]
    text4 = test_utils.result_group_2_2[pc.INFO][RC.NAME]
    text5 = test_utils.result_group_5[pc.INFO][RC.NAME]
    assert data0[RC.CHILDREN][0][pc.INFO][RC.NAME] == text0
    assert data1[RC.CHILDREN][0][pc.INFO][RC.NAME] == text1
    assert data2[RC.CHILDREN][0][pc.INFO][RC.NAME] == text2
    assert data2[RC.CHILDREN][1][pc.INFO][RC.NAME] == text3
    assert data2[RC.CHILDREN][2][pc.INFO][RC.NAME] == text4
    assert data3[RC.CHILDREN][0][pc.INFO][RC.NAME] == text5
