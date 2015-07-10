import spirent.methodology.results.ProviderUtils as utils
from spirent.methodology.results.ProviderConst import ProviderConst
import os
import sys
import traceback
TEST_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
               'stakunittest/test_sqlite_util_data.db'
TEST_MULTIPLE_DB_FILE = 'STAKCommands/spirent/methodology/results/' \
                        'stakunittest/test_util_multi_data.db'
TEST_MULTIPLE_DB_FILE_1 = 'STAKCommands/spirent/methodology/results/' \
                          'stakunittest/test_util_multi_data_2015-01-21_16-25-14.db'
TEST_MULTIPLE_DB_FILE_2 = 'STAKCommands/spirent/methodology/results/' \
                          'stakunittest/test_util_multi_data_2015-01-21_16-25-42.db'


def test_get_comparision_verdict_with_text():
    prop_name = 'row count'
    # 'LESS_THAN'
    data = utils.get_comparision_verdict_with_text('LESS_THAN', 10, 20, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 10; ' + \
        'expected count: less than 20.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    data = utils.get_comparision_verdict_with_text('LESS_THAN', 22, 20, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is False
    exp_str = 'Actual row count does not match expected row count. Actual count: 22; ' + \
        'expected count: less than 20.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'LESS_THAN_OR_EQUAL'
    data = utils.get_comparision_verdict_with_text('LESS_THAN_OR_EQUAL', 10, 10, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 10; ' + \
        'expected count: less than or equal to 10.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'GREATER_THAN'
    data = utils.get_comparision_verdict_with_text('GREATER_THAN', 10, 10, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is False
    exp_str = 'Actual row count does not match expected row count. Actual count: 10; ' + \
        'expected count: greater than 10.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'GREATER_THAN_OR_EQUAL'
    data = utils.get_comparision_verdict_with_text('GREATER_THAN_OR_EQUAL',
                                                   10, 10, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 10; ' + \
        'expected count: greater than or equal to 10.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'EQUAL'
    data = utils.get_comparision_verdict_with_text('EQUAL', 10, 10, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 10; ' + \
        'expected count: equal to 10.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'NOT_EQUAL'
    data = utils.get_comparision_verdict_with_text('NOT_EQUAL', 10, 10, 0, 0, prop_name)
    assert data[ProviderConst.VERDICT] is False
    exp_str = 'Actual row count does not match expected row count. Actual count: 10; ' + \
        'expected count: not equal to 10.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    # 'BETWEEN'
    data = utils.get_comparision_verdict_with_text('BETWEEN', 5, 0, 5, 10, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 5; ' + \
        'expected count: between 5 and 10, inclusive.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    data = utils.get_comparision_verdict_with_text('BETWEEN', 4, 0, 5, 10, prop_name)
    assert data[ProviderConst.VERDICT] is False
    exp_str = 'Actual row count does not match expected row count. Actual count: 4; ' + \
        'expected count: between 5 and 10, inclusive.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    data = utils.get_comparision_verdict_with_text('BETWEEN', 10, 0, 5, 10, prop_name)
    assert data[ProviderConst.VERDICT] is True
    exp_str = 'Actual row count matches expected row count. Actual count: 10; ' + \
        'expected count: between 5 and 10, inclusive.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str

    data = utils.get_comparision_verdict_with_text('BETWEEN', 11, 0, 5, 10, prop_name)
    assert data[ProviderConst.VERDICT] is False
    exp_str = 'Actual row count does not match expected row count. Actual count: 11; ' + \
        'expected count: between 5 and 10, inclusive.'
    assert data[ProviderConst.VERDICT_TEXT] == exp_str


def test_get_db_files_multiple_true():
    result_file = os.path.join(os.getcwd(), TEST_MULTIPLE_DB_FILE)
    db_list = utils.get_db_files(result_file, True)
    assert len(db_list) == 2
    assert db_list[0] == os.path.join(os.getcwd(), os.path.normpath(TEST_MULTIPLE_DB_FILE_1))
    assert db_list[1] == os.path.join(os.getcwd(), os.path.normpath(TEST_MULTIPLE_DB_FILE_2))


def test_get_db_files_multiple_false():
    result_file = os.path.join(os.getcwd(), TEST_MULTIPLE_DB_FILE)
    db_list = utils.get_db_files(result_file, False)
    assert len(db_list) == 1
    assert db_list[0] == os.path.join(os.getcwd(), os.path.normpath(TEST_MULTIPLE_DB_FILE_2))


def test_get_db_files_single_true():
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    fail_message = ''
    try:
        utils.get_db_files(result_file, True)
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(exc_info[0],
                                                    exc_info[1])
        if len(fail_list) == 1:
            fail_message = fail_list[0]
        else:
            fail_message = '\n'.join(fail_list)
    if 'ValueError' not in fail_message:
        raise AssertionError('Command failed with unexpected error: "' +
                             fail_message + '"')


def test_get_db_files_single_false():
    result_file = os.path.join(os.getcwd(), TEST_DB_FILE)
    db_list = utils.get_db_files(result_file, False)
    assert len(db_list) == 1
    assert db_list[0] == os.path.join(os.getcwd(), os.path.normpath(TEST_DB_FILE))
