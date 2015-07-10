import sqlite3
from spirent.methodology.results.ProviderConst import ProviderConst
from StcIntPythonPL import *
import os


def get_all_data(db_file_list, query):
    """
    Run query and return all row data and column names.
    """
    data = {}
    row_data = []
    for db_file in db_file_list:
        if not os.path.isfile(db_file):
            raise Exception('Unable to find db file:' + db_file)
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        for q in query.split(";"):
            if len(q) > 0:
                cur.execute(q)
        rows = cur.fetchall()
        column_names = list(map(lambda x: x[0], cur.description))
        conn.close()
        row_data.extend(rows)
        data[ProviderConst.COLUMN_DISPLAY_NAMES] = column_names

    data[ProviderConst.ROW] = row_data
    return data


def get_all_chart_data(query, series_data_type, result_file_list):
    data = get_all_data(result_file_list, query)
    if str(series_data_type) == "SINGLE":
        if len(data[ProviderConst.COLUMN_DISPLAY_NAMES]) != 1:
            raise RuntimeError("ERROR: Expected one data column per row")
    elif str(series_data_type) == "PAIR":
        if len(data[ProviderConst.COLUMN_DISPLAY_NAMES]) != 2:
            raise RuntimeError("ERROR: Expected two data columns per row")

    rows = data[ProviderConst.ROW]
    # Special case when having one column of data returns in the format(x,)
    row_data = []
    for row in rows:
        if str(series_data_type) == "SINGLE":
            row_data.append(row[0])
        elif str(series_data_type) == "PAIR":
            row_data.append([row[0], row[1]])

    # Return list of series data
    return row_data


def get_all_chart_data_ignore_type(query, result_file_list):
    data = get_all_data(result_file_list, query)
    rows = data[ProviderConst.ROW]

    # Special case when having one column of data returns in the format(x,)
    row_data = []
    for row in rows:
        if len(row) == 1:
            row_data.append(row[0])
        elif len(row) > 1:
            row_data.append(list(row))

    # Return list of series data
    return row_data
