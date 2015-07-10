from StcIntPythonPL import *
import os
import sqlite3
import traceback
import spirent.methodology.results.ProviderUtils as pu
from spirent.methodology.results.ProviderConst import ProviderConst
import spirent.methodology.results.SqliteUtils as sql_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(SrcDatabase, DstDatabase, SqlCreateTable, SqlQuery):
    # Check for empty values
    if not SrcDatabase:
        return 'Empty SrcDatabase property is not allowed'
    if not DstDatabase:
        return 'Empty DstDatabase property is not allowed'
    if not SqlCreateTable:
        return 'Empty SqlCreateTable property is not allowed'
    if not SqlQuery:
        return 'Empty SqlQuery property is not allowed'
    return ''


def run(SrcDatabase, DstDatabase, SqlCreateTable, SqlQuery):
    logger = PLLogger.GetLogger('methodology')

    try:
        # Get source database file names
        src_db_files = get_dbs_list(SrcDatabase)
        if src_db_files is None:
            err_msg = 'No source databases found for ' + str(SrcDatabase)
            logger.LogError(err_msg)
            raise RuntimeError(err_msg)

        # Get destination database file names
        dst_db_files = get_dbs_list(DstDatabase)
        if dst_db_files is None:
            err_msg = 'No destination database found for ' + str(DstDatabase)
            logger.LogError(err_msg)
            raise RuntimeError(err_msg)
        # Only want one destination database
        dst_db_file = dst_db_files[0]

        # Verify destination database file exists
        if not os.path.isfile(dst_db_file):
            raise RuntimeError('Destination DB file does not exist: ' + str(dst_db_file))

        # Open connection to destination database
        dst_db_conn = sqlite3.connect(dst_db_file)
        dst_db_curs = dst_db_conn.cursor()

        # Write rows to table in destination database
        write_rows(src_db_files, dst_db_curs, SqlCreateTable, SqlQuery)

        # Commit and close database connection
        dst_db_conn.commit()
        dst_db_conn.close()

    except Exception, e:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        raise RuntimeError(str(e))
    except:
        stack_trace = traceback.format_exc()
        logger.LogError(stack_trace)
        raise RuntimeError(str(stack_trace))

    return True


def reset():
    return True


def write_rows(src_db_files, dst_db_curs, table_sql, query):
    # Check for empty values
    if not dst_db_curs:
        raise RuntimeError('Invalid DB Cursor')
    if not table_sql:
        raise RuntimeError('Empty CREATE TABLE SQL statement')
    if not query:
        raise RuntimeError('Empty SQL Query')

    # Check src db file list not empty
    if not src_db_files:
        raise RuntimeError('No source DB files specified')

    # Verify each src db file exists
    for src_db_file in src_db_files:
        if not os.path.isfile(src_db_file):
            raise RuntimeError('Source DB file does not exist: ' + str(src_db_file))

    # Create table (if needed)
    table_name = create_table(dst_db_curs, table_sql)
    if not table_name:
        raise RuntimeError('Error occured while creating the table or checking for existence')

    # Get number of columns in destination table
    columnsQuery = "PRAGMA table_info(%s)" % table_name
    dst_db_curs.execute(columnsQuery)
    numberOfColumnsInDst = len(dst_db_curs.fetchall())
    if not numberOfColumnsInDst:
        raise RuntimeError('No columns found in destination table ' + table_name)

    # Run query on source database(s)
    src_data = get_data_from_query(src_db_files, query)

    # Check if list is empty
    # Won't raise an error here because this is a valid use case - query produced no results
    if not src_data:
        return 0

    # Check number of columns
    numOfColumnsInSrc = len(src_data[0])
    if numOfColumnsInSrc != numberOfColumnsInDst:
        raise RuntimeError('The number of columns in the source table (' + str(numOfColumnsInSrc) +
                           ') does not match the number of columns in the destination table (' +
                           str(numberOfColumnsInDst) + ')')

    # Execute table INSERT
    sql_cmd = "INSERT INTO " + str(table_name) + " VALUES (" + "?, "*(numOfColumnsInSrc-1) + "?)"
    dst_db_curs.executemany(sql_cmd, src_data)

    return len(src_data)


def create_table(cursor, sql_command):
    # Check for empty values
    if not cursor:
        raise RuntimeError('Invalid DB Cursor')
    if not sql_command:
        raise RuntimeError('Empty CREATE TABLE SQL statement')

    # Parse Sql statement
    sql_list = sql_command.split()

    if len(sql_list) == 1:
        # Specifying just a table name...
        table_name = sql_list[0]

        # If table does not exist, raise an error; else return the table name
        if not table_exists(cursor, table_name):
            raise RuntimeError('Table ' + str(table_name) + ' does not exist in database')
        return table_name

    elif len(sql_list) >= 4:
        # Valid Sql CREATE command...
        # Verify the command at least has the first 2 words correct
        if sql_list[0].upper() != 'CREATE' or sql_list[1].upper() != 'TABLE':
            raise RuntimeError('Invalid CREATE TABLE SQL statement')
        table_name = sql_list[2]

        # Check for existence first
        if table_exists(cursor, table_name):
            return table_name

        # Table does not exist, create it and return the table name
        cursor.execute(sql_command)
        return table_name

    else:
        raise RuntimeError('Invalid CREATE TABLE SQL statement')

    return ''


def get_data_from_query(db_file_list, query):
    if not db_file_list or not query:
        return []
    result_data = sql_utils.get_all_data(db_file_list, query)
    rows = result_data[ProviderConst.ROW]
    return rows


def get_dbs_list(database):
    if database == "SUMMARY":
        return [get_active_results_db()]
    elif database == "ALL_ITERATION":
        return pu.get_db_files(get_active_results_db(), True)
    elif database == "LAST_ITERATION":
        return [pu.get_db_files(get_active_results_db(), False)[0]]
    else:
        raise RuntimeError('Invalid database selected: ' + str(database))


def get_active_results_db():
    # In its own function to allow for easier unit testing using MagicMock
    return pu.get_active_result_db_filename()


def table_exists(cursor, table_name):
    # Check for empty values
    if not cursor:
        raise RuntimeError('Invalid DB Cursor')
    if not table_name:
        raise RuntimeError('Empty Table Name')

    query = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' and name='{0}'"
    cursor.execute(query.format(table_name))
    # If table exists return the table name
    if cursor.fetchone()[0] != 0:
        return table_name
    return ''
