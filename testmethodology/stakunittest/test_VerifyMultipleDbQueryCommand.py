from StcIntPythonPL import *
from mock import MagicMock
from spirent.core.utils.scriptable import AutoCommand
import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(),
                'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.VerifyMultipleDbQueryCommand as verifymultidb
from results.ResultInterface import ResultInterface
from results.ProviderConst import ProviderConst
from results.ResultEnum import EnumDataClass
from manager.utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


PKG = 'spirent.methodology'
COMMAND_NAME = 'VerifyMultipleDbQueryCommand'
COMMAND = verifymultidb
TEST_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
               'stakunittest/test_sqlite_util_data.db'
TEST_MULTI_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
                     'stakunittest/test_util_multi_data.db'


def test_verify_single_db(stc, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_DB_FILE
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        verifymultidb.get_this_cmd = MagicMock(return_value=cmd)
        verifymultidb.get_active_results_db = MagicMock(return_value=result_file)
        verifymultidb.run(["Select TotalFrameCount from AnalyzerPortResults",
                           "Select TotalOctetCount from GeneratorPortResults"],
                          False, False, "GROUP_2", [], [], [], False)

    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = []

    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        info = obj[ProviderConst.INFO]
        assert ProviderConst.REPORT_GROUP in info
        assert info[ProviderConst.REPORT_GROUP] == "GROUP_2"
        assert ProviderConst.CLASS in obj
        if obj[ProviderConst.CLASS] == EnumDataClass.table_db_query:
            selected.append(obj)
    assert len(selected) > 0
    assert selected[0] is not None
    info = selected[0][ProviderConst.INFO]
    data = selected[0][ProviderConst.DATA]
    assert "Select TotalFrameCount from AnalyzerPortResults" == str(info[ProviderConst.SQL_QUERY])
    assert "[[1151261], [1239945]]" == str(data[ProviderConst.ROW])
    assert "[u'TotalFrameCount']" == str(data[ProviderConst.COLUMN_DISPLAY_NAMES])
    assert selected[1] is not None
    info = selected[1][ProviderConst.INFO]
    data = selected[1][ProviderConst.DATA]
    assert "Select TotalOctetCount from GeneratorPortResults" == str(info[ProviderConst.SQL_QUERY])
    assert "[[158712960], [147361408]]" == str(data[ProviderConst.ROW])
    assert "[u'TotalOctetCount']" == str(data[ProviderConst.COLUMN_DISPLAY_NAMES])


def test_verify_multi_db(stc, meth_mgr):
    global PKG, COMMAND, COMMAND_NAME, TEST_MULTI_DB_FILE
    result_file = os.path.join(os.getcwd(), TEST_MULTI_DB_FILE)

    # Simulate running through the TopologyTestGroupCommand and
    # TestGroupCommands
    ResultInterface.create_test()
    ResultInterface.start_test()

    with AutoCommand('.'.join([PKG, COMMAND_NAME])) as cmd:
        verifymultidb.get_this_cmd = MagicMock(return_value=cmd)
        verifymultidb.get_active_results_db = MagicMock(return_value=result_file)
        verifymultidb.run(["Select TotalFrameCount from AnalyzerPortResults",
                           "Select TotalOctetCount from GeneratorPortResults"],
                          False, True, "", [], [], [], False)

    ResultInterface.end_test()
    stm_test_result = meth_man_utils.get_stm_test_result()
    assert stm_test_result is not None
    json_results = stm_test_result.GetCollection('JsonResults')
    selected = []

    for result in json_results:
        obj = json.loads(result)
        assert ProviderConst.INFO in obj
        info = obj[ProviderConst.INFO]
        assert ProviderConst.CLASS in obj
        if obj[ProviderConst.CLASS] == EnumDataClass.table_db_query:
            selected.append(obj)
    assert len(selected) > 0
    assert selected[0] is not None
    info = selected[0][ProviderConst.INFO]
    data = selected[0][ProviderConst.DATA]
    assert "Select TotalFrameCount from AnalyzerPortResults" == str(info[ProviderConst.SQL_QUERY])
    assert "[[298838], [287903], [294329], [289852]]" == str(data[ProviderConst.ROW])
    assert "[u'TotalFrameCount']" == str(data[ProviderConst.COLUMN_DISPLAY_NAMES])
    assert selected[1] is not None
    info = selected[1][ProviderConst.INFO]
    data = selected[1][ProviderConst.DATA]
    assert "Select TotalOctetCount from GeneratorPortResults" == str(info[ProviderConst.SQL_QUERY])
    assert "[[37797632], [39164544], [37776000], [38309760]]" == str(data[ProviderConst.ROW])
    assert "[u'TotalOctetCount']" == str(data[ProviderConst.COLUMN_DISPLAY_NAMES])
    