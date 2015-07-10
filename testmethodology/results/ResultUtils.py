import os
import json
from StcIntPythonPL import *
from spirent.methodology.results.Status import Status
from spirent.methodology.results.ResultEnum import (
    EnumVerdict,
    EnumDataClass,
    EnumDataFormat
    )
import spirent.methodology.results.LogUtils as logger
from spirent.methodology.results.ResultConst import ResultConst
from spirent.methodology.results.ProviderConst import ProviderConst as pc
import copy
import datetime
import time


def summarize_status(obj):
    verdict = EnumVerdict.none
    verdict_text = ResultConst.NONE
    for result in obj._data:
        if Status.get_dict_name() in result:
            if Status.get_apply_verdict_dict_name() in result[Status.get_dict_name()]:
                if result[Status.get_dict_name()][Status.get_apply_verdict_dict_name()] is False:
                    continue
        new_verdict = result[Status.get_dict_name()][Status.get_verdict_dict_name()]
        if EnumVerdict.do_override_verdict(verdict, new_verdict):
            verdict = new_verdict
            verdict_text = \
                result[Status.get_dict_name()][Status.get_verdict_text_dict_name()]

    obj._status.verdict = verdict
    if verdict == EnumVerdict.passed:
        obj._status.verdict_text = ResultConst.TEST_PASS_VERDICT_TEXT
    else:
        obj._status.verdict_text = verdict_text


def generate_report_file(report_name, data):
    filename = os.path.join(CTestResultSettingExt.GetResultDbBaseDirectory(), report_name)
    logger.info("Saving file:" + filename)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    f = open(filename, "w")
    f.write(json.dumps(data, separators=(',', ':'), sort_keys=False))
    f.close()
    CFileManager.AddFile(filename, 'RESULT')
    return filename


def wrap_data_as_single_group(data, group_tag=ResultConst.ALL_GROUPS):
    groupdata = {}
    groupdata[ResultConst.TAG] = group_tag
    if not isinstance(data, list):
        groupdata[ResultConst.CHILDREN] = []
        groupdata[ResultConst.CHILDREN].append(data)
    else:
        groupdata[ResultConst.CHILDREN] = data
    return groupdata


def report_group_comparator(data1, data2):
    value1 = CMeta.GetEnumerationValue('spirent.methodology.ResultBaseCommand',
                                       'ReportGroup',
                                       str(data1[pc.INFO][pc.REPORT_GROUP]))
    value2 = CMeta.GetEnumerationValue('spirent.methodology.ResultBaseCommand',
                                       'ReportGroup',
                                       str(data2[pc.INFO][pc.REPORT_GROUP]))
    return value1 - value2


def group_data_using_report_group(data):
    data.sort(report_group_comparator)
    groupdata = {}
    groupdata[ResultConst.TAG] = ResultConst.ALL_GROUPS
    groupdata[ResultConst.CHILDREN] = []

    result_group = {}
    result_group[pc.CLASS] = EnumDataClass.result_group
    result_group[pc.DATA_FORMAT] = EnumDataFormat.group
    mydata = {}
    mydata[ResultConst.TAG] = 'ResultGroup'
    mydata[ResultConst.CHILDREN] = []
    result_group[pc.DATA] = mydata

    cgdata = copy.deepcopy(result_group)
    cdata = cgdata[pc.DATA]
    cgroup = pc.DEFAULT_REPORT_GROUP
    for pdata in data:
        if cdata[ResultConst.CHILDREN]:
            if pdata[pc.INFO][pc.REPORT_GROUP] == cgroup:
                cdata[ResultConst.CHILDREN].append(pdata)
                continue
            else:
                groupdata[ResultConst.CHILDREN].append(cgdata)
                cgdata = copy.deepcopy(result_group)
                cdata = cgdata[pc.DATA]
        cdata[ResultConst.CHILDREN].append(pdata)
        cgroup = pdata[pc.INFO][pc.REPORT_GROUP]
        cdata[ResultConst.TAG] = "Report Group " + cgroup

    if cdata[ResultConst.CHILDREN]:
        groupdata[ResultConst.CHILDREN].append(cgdata)
    return groupdata


def validate_report_group(stringValue):
    try:
        CMeta.GetEnumerationValue('spirent.methodology.ResultBaseCommand',
                                  'ReportGroup',
                                  str(stringValue))
        return stringValue
    except:
        return pc.DEFAULT_REPORT_GROUP


def insert_report_group_if_not_defined(dict_data):
    if not (pc.INFO in dict_data):
        dict_data[pc.INFO] = {}
    if not (pc.REPORT_GROUP in dict_data[pc.INFO]):
        dict_data[pc.INFO][pc.REPORT_GROUP] = pc.DEFAULT_REPORT_GROUP
    else:
        dict_data[pc.INFO][pc.REPORT_GROUP] = \
            validate_report_group(dict_data[pc.INFO][pc.REPORT_GROUP])
    return dict_data


def get_current_time_string():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')