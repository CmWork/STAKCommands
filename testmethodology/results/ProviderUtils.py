from spirent.methodology.results.ProviderConst import ProviderConst
from StcIntPythonPL import *
import os
import re
import operator
import spirent.methodology.results.LogUtils as logger
import sqlite3


def get_active_result_db_filename():
    """
    Return current result file name.
    raise exception in all error cases.
    """
    project = CStcSystem.Instance().GetObject('project')
    trs = project.GetObject('testresultsetting')
    if trs is None:
        raise Exception("Unable to find TestResultSetting object for Project")
    result_file = trs.Get('currentresultfilename')
    if not os.path.isfile(result_file):
        raise Exception('Results have not been saved recently. No file found.')
    return result_file


def get_db_files(active_db, UseMultipleResultsDatabases):
    logger.debug("get_db_files")
    resultsDbList = []
    dbNamesList = []

    filePath = os.path.dirname(active_db)
    if not os.path.isfile(active_db):
        raise Exception('Results have not been saved recently. No file found.')
    query = "SELECT DbFileName FROM EotResultIterations"
    conn = sqlite3.connect(active_db)
    cur = conn.cursor()
    try:
        cur.execute(query)
        if UseMultipleResultsDatabases:
            # Multiple dbs exist and want all of them
            # Loopmode = Append, UseMultipleResultsDatabases = True
            query = "SELECT DbFileName FROM EotResultIterations"
            cur.execute(query)
            rows = cur.fetchall()
            logger.debug("rows: " + str(rows))
            dbNamesList = re.findall('\'(.*?)\'', str(rows))
        else:
            # Multiple dbs exist but want the current iterations db
            # Loopmode = Append, UseMultipleResultsDatabases = False
            query = "SELECT DbFileName FROM EotResultIterations \
                     WHERE Id = (SELECT MAX(Id) FROM EotResultIterations)"
            cur.execute(query)
            rows = cur.fetchall()
            dbNameList = re.findall('\'(.*?)\'', str(rows))
            dbNamesList.append(dbNameList[0])
    except sqlite3.OperationalError:
        if UseMultipleResultsDatabases:
            # Invalid settings
            # Loopmode = Overwrite, UseMultipleResultsDatabases = True
            raise ValueError("Invalid settings, UseMultipleResultsDatabases \
                             cannot be TRUE if there is only a single results \
                             database. Change SaveResults Loopmode to APPEND")
        else:
            # Single results db
            # Loopmode = Overwrite, UseMultipleResultsDatabases = False
            dbNamesList.append(active_db)

    for dbName in dbNamesList:
        resultDb = os.path.abspath(os.path.join(filePath, dbName))
        resultsDbList.append(resultDb)
    conn.close()
    logger.debug("returning: " + str(resultsDbList))
    return resultsDbList


def get_comparision_verdict_with_text(comp_operator,
                                      actual_value,
                                      expected_value,
                                      expected_min_value,
                                      expected_max_value,
                                      property_name):
    """
    comp_operator: Enum comp_operator
    values: for comparision
    property_name: string used for verdict text message.
    Return dictionary with verdict as bool and verdict text
    """

    verdict = False
    expected_filter_string = 'None'
    if comp_operator == 'LESS_THAN':
        verdict = operator.lt(actual_value, expected_value)
        expected_filter_string = ' less than ' + str(expected_value)
    elif comp_operator == 'LESS_THAN_OR_EQUAL':
        verdict = operator.le(actual_value, expected_value)
        expected_filter_string = ' less than or equal to ' + str(expected_value)
    elif comp_operator == 'GREATER_THAN':
        verdict = operator.gt(actual_value, expected_value)
        expected_filter_string = ' greater than ' + str(expected_value)
    elif comp_operator == 'GREATER_THAN_OR_EQUAL':
        verdict = operator.ge(actual_value, expected_value)
        expected_filter_string = ' greater than or equal to ' + str(expected_value)
    elif comp_operator == 'EQUAL':
        verdict = operator.eq(actual_value, expected_value)
        expected_filter_string = ' equal to ' + str(expected_value)
    elif comp_operator == 'NOT_EQUAL':
        verdict = operator.ne(actual_value, expected_value)
        expected_filter_string = ' not equal to ' + str(expected_value)
    elif comp_operator == 'BETWEEN':
        verdict = operator.le(expected_min_value, actual_value) and \
            operator.le(actual_value, expected_max_value)
        expected_filter_string = ' between ' + str(expected_min_value) + \
            ' and ' + str(expected_max_value) + ', inclusive'
    else:
        raise Exception("Unsupported comparision operator {0}".format(comp_operator))

    pass_fail_text = ' does not match '
    if verdict is True:
        pass_fail_text = ' matches '
    verdict_text = 'Actual ' + property_name + pass_fail_text + 'expected ' + \
        property_name + '. Actual count: ' + str(actual_value) + \
        '; expected count:' + expected_filter_string + '.'

    data = {}
    data[ProviderConst.VERDICT] = verdict
    data[ProviderConst.VERDICT_TEXT] = verdict_text
    return data
