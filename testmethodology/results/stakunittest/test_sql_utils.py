import spirent.methodology.results.SqliteUtils as sql_utils
from spirent.methodology.results.ProviderConst import ProviderConst
import os


test_db_file = 'STAKCommands/spirent/methodology/results/' \
               'stakunittest/test_sqlite_util_data.db'


def test_get_all_data_from_multi_cmd_sql():
    global test_db_file
    filename = os.path.join(os.getcwd(), test_db_file)
    query1 = 'Create Temp Table A (id int);' + \
        'Insert Into A Values (12);' + \
        'Insert Into A Values (51);' + \
        'Insert Into A Values (46);' + \
        'Insert Into A Values (31);' + \
        'Insert Into A Values (78);' + \
        'Select id From A;'
    data = sql_utils.get_all_data([filename], query1)
    assert data is not None
    rows = data[ProviderConst.ROW]
    assert len(rows) == 5


def test_get_all_data():
    global test_db_file
    filename = os.path.join(os.getcwd(), test_db_file)
    query1 = 'Select TotalFrameCount, TotalOctetCount, \
              SigFrameCount from AnalyzerPortResults'
    data = sql_utils.get_all_data([filename], query1)
    assert data is not None
    column_names = data[ProviderConst.COLUMN_DISPLAY_NAMES]
    rows = data[ProviderConst.ROW]
    assert len(column_names) == 3
    assert len(rows) == 2
    assert len(rows[0]) == 3
    assert len(rows[1]) == 3
    assert column_names[0] == 'TotalFrameCount'
    assert column_names[1] == 'TotalOctetCount'
    assert column_names[2] == 'SigFrameCount'
    assert rows[0][0] == 1151261
    assert rows[1][2] == 1239945

    query2 = 'Select TotalFrameCount as "Tx Frame Count", ' +\
        'TotalOctetCount as "Total Octet Count", ' +\
        'SigFrameCount as "Sig Frame Count" from AnalyzerPortResults'
    data = sql_utils.get_all_data([filename], query2)
    assert data is not None
    column_names = data[ProviderConst.COLUMN_DISPLAY_NAMES]
    rows = data[ProviderConst.ROW]
    assert len(column_names) == 3
    assert len(rows) == 2
    assert len(rows[0]) == 3
    assert len(rows[1]) == 3
    assert column_names[0] == 'Tx Frame Count'
    assert column_names[1] == 'Total Octet Count'
    assert column_names[2] == 'Sig Frame Count'
    assert rows[0][0] == 1151261
    assert rows[1][2] == 1239945


def test_get_all_chart_data():
    global test_db_file
    filename = os.path.join(os.getcwd(), test_db_file)
    query1 = 'Select TotalFrameCount from AnalyzerPortResults'
    data = sql_utils.get_all_chart_data(query1, "SINGLE", [filename])
    assert data is not None
    assert data == [1151261, 1239945]

    query3 = 'Select TotalFrameCount, TotalOctetCount from AnalyzerPortResults'
    data = sql_utils.get_all_chart_data(query3, "PAIR", [filename])
    assert data is not None
    assert data == [[1151261, 147361408], [1239945, 158712960]]

    try:
        query5 = 'Select SigFrameCount, ParentHnd, TotalFrameCount \
                  from AnalyzerPortResults'
        data = sql_utils.get_all_chart_data(query5, "SINGLE", [filename])
    except RuntimeError as e:
        assert 'ERROR: Expected one data column per row' in str(e)

    try:
        query6 = 'Select SigFrameCount, ParentHnd, TotalFrameCount \
                  from AnalyzerPortResults'
        data = sql_utils.get_all_chart_data(query6, "PAIR", [filename])
    except RuntimeError as e:
        assert 'ERROR: Expected two data columns per row' in str(e)


def test_get_all_chart_data_ignore_type():
    global test_db_file
    filename = os.path.join(os.getcwd(), test_db_file)
    query1 = 'Select TotalFrameCount from AnalyzerPortResults'
    data = sql_utils.get_all_chart_data_ignore_type(query1, [filename])
    assert data is not None
    assert data == [1151261, 1239945]

    query2 = 'Select Name from StcSystem'
    data = sql_utils.get_all_chart_data_ignore_type(query2, [filename])
    assert data is not None
    assert data == ['StcSystem 1']

    query3 = 'Select TotalFrameCount, TotalOctetCount from AnalyzerPortResults'
    data = sql_utils.get_all_chart_data_ignore_type(query3, [filename])
    assert data is not None
    assert data == [[1151261, 147361408], [1239945, 158712960]]
