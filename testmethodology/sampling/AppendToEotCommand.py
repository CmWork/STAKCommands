from StcIntPythonPL import *
import os
import glob
import sqlite3


OBJ_KEY = 'spirent.methodology.sampling'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(EventTableName, DataTableName):
    if EventTableName == "" or DataTableName == "":
        return "Table names must be set"
    return ''


def run(EventTableName, DataTableName):
    # Retrieve persistent object
    logger = PLLogger.GetLogger('methodology')
    if not CObjectRefStore.Exists(OBJ_KEY):
        err = "Sampling system not properly initialized"
        logger.LogError(err)
        raise RuntimeError(err)
    samp_dict = CObjectRefStore.Get(OBJ_KEY)
    if samp_dict is None:
        # Release it, since even if it exists, it's None
        CObjectRefStore.Release(OBJ_KEY)
        err = "Failed to retrieve persistent STAK object"
        logger.LogError(err)
        raise RuntimeError(err)
    this_cmd = get_this_cmd()
    try:
        # Take care of the db stuff
        db_file = get_db_filename()
        db_conn = sqlite3.connect(db_file)
        db_curs = db_conn.cursor()
        # First, get the data set ID
        ds_id = get_dataset_id(db_curs)
        # Set up progress bar
        this_cmd.Set('ProgressEnable', True)
        this_cmd.Set('ProgressStepsCount', 3)
        logger.LogInfo("Writing data table")
        write_data_table(db_curs, ds_id, DataTableName, samp_dict)
        logger.LogInfo("Writing event table")
        write_event_table(db_curs, ds_id, EventTableName, samp_dict)
        logger.LogInfo("Committing database changes")
        db_conn.commit()
        db_conn.close()
    # This will throw to the caller, but the finally clause is called before
    # doing so
    finally:
        # Clean up the subscription datasets
        if 'Subscription' in samp_dict:
            hnd_reg = CHandleRegistry.Instance()
            ds_list = []
            for sub in samp_dict['Subscription']:
                if 'ResultDatasetHandle' in sub:
                    ds_obj = hnd_reg.Find(sub['ResultDatasetHandle'])
                    if ds_obj is not None:
                        ds_list.append(ds_obj)
            for ds_obj in ds_list:
                ds_obj.MarkDelete()
        # Release it, since even if it exists, it's None
        CObjectRefStore.Release(OBJ_KEY)
        this_cmd.Set('ProgressEnable', False)
    return True


def reset():
    return True


def write_data_table(cursor, ds_id, table_name, samp_dict):
    logger = PLLogger.GetLogger('methodology')
    if 'Subscription' not in samp_dict:
        return 0
    subs = samp_dict['Subscription']
    property_list = []
    property_stype = []
    subs_map = {}
    hnd_reg = CHandleRegistry.Instance()
    logger.LogInfo("write_data_table: Pass 1, find property names in subs")
    # Pass 1, populate the properties and the subscriptions
    if len(subs) == 0:
        err_str = "No subscriptions found in persistent storage"
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    this_cmd = get_this_cmd()
    this_cmd.Set('ProgressCurrentStep', 1)
    this_cmd.Set('ProgressCurrentStepName', "Checking subscriptions")
    this_cmd.Set('ProgressStepsCount', len(subs))
    sub_idx = 0
    item_count = 0
    for sub in subs:
        sub_idx += 1
        this_cmd.Set('ProgressCurrentStep', sub_idx)
        if 'ResultDatasetHandle' not in sub:
            err_str = "Subscription data does not contain result dataset handle"
            logger.LogError(err_str)
            raise RuntimeError(err_str)
        if 'Data' in sub:
            item_count += len(sub['Data'])
        hdl = int(sub['ResultDatasetHandle'])
        dataset_obj = hnd_reg.Find(hdl)
        if dataset_obj is None:
            err_str = "Invalid dataset handle in subscription"
            logger.LogError(err_str)
            raise RuntimeError(err_str)

        prop_list = []
        for prop_name in sub["ViewAttributeList"].split():
            prop_list.append(sub["ResultType"] + "." + prop_name)

        logger.LogInfo("write_data_table: ResultQuery Property List" +
                       str(prop_list))
        for prop in prop_list:
            psplit = prop.split('.')
            cmeta = CMeta.GetClassMeta(psplit[0])
            pmeta = CMeta.GetPropertyMeta(*psplit)
            prop_name = cmeta['name'] + '.' + pmeta['name']
            idx = len(property_list)
            if prop_name in property_list:
                idx = property_list.index(prop_name)
            else:
                property_list.append(prop_name)
                property_stype.append(get_db_type(pmeta['typeName']))
            if hdl not in subs_map:
                subs_map[hdl] = []
            subs_map[hdl].append(idx)
    # Check column names
    logger.LogInfo("write_data_table: Property list is: " + str(property_list))
    if len(property_list) == 0:
        err_str = "No properties found in subscriptions"
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    col_list = []
    for prop in property_list:
        col_list.append(prop.replace(".", "_"))

    # Create table with column names
    logger.LogInfo("write_data_table: Create table " + table_name)
    table_sql = "CREATE TABLE " + table_name + " " + \
                "('DataSetId' INTEGER, 'SubscriptionHandle' INTEGER, " + \
                "'Timestamp' INTEGER, "
    for fld_name, fld_type in zip(col_list, property_stype):
        table_sql += "'" + fld_name + "' " + fld_type + ", "
    table_sql = table_sql[0:-2] + ")"
    logger.LogInfo("Table SQL is " + table_sql)
    create_table(cursor, table_sql)
    # Pass 2, Insert data into the table
    this_cmd.Set('ProgressCurrentStep', 2)
    this_cmd.Set('ProgressCurrentStepName', "Writing data table")
    this_cmd.Set('ProgressStepsCount', item_count)
    values = []
    item_idx = 0
    for sub in subs:
        item_idx += 1
        this_cmd.Set('ProgressCurrentStep', item_idx)
        if item_idx % 23 == 0:
            # Yield every 23
            CTaskManager.Instance().CtmYield()
        hdl = int(sub['ResultDatasetHandle'])
        # Skip if no data found
        if 'Data' not in sub:
            continue
        dataList = sub['Data']
        for data in dataList:
            # Prepare an empty row (results only)
            row = [None] * (len(col_list) + 3)
            # Dataset ID
            row[0] = ds_id
            # Subscription Handle
            row[1] = data[0]
            # Timestamp
            row[2] = data[1]
            # Iterate over index and value
            for idx, val in zip(subs_map[hdl], data[2:]):
                row[idx + 3] = val
            values.append(tuple(row))
    # Question marks
    qs = "? ," * (len(col_list) + 3)
    logger.LogInfo("write_data_table: Insert rows into table")
    # Strip last comma and space, add parentheses
    sql_cmd = "INSERT INTO " + table_name + " VALUES (" + qs[0:-2] + ")"
    logger.LogInfo("write_data_table: sql command: " + sql_cmd)
    cursor.executemany(sql_cmd, values)
    return len(values)


def write_event_table(cursor, ds_id, table_name, samp_dict):
    create_table(cursor, "CREATE TABLE " + table_name + " " +
                 "('DataSetId' INTEGER, 'EventType' VARCHAR, " +
                 "'EventId' INTEGER, 'TimeStamp' INTEGER)")
    # Not an error if there are no events, return
    if 'Event' not in samp_dict:
        return 0
    evList = samp_dict['Event']
    this_cmd = get_this_cmd()
    this_cmd.Set('ProgressCurrentStep', 3)
    this_cmd.Set('ProgressCurrentStepName',
                 "Creating Event Table (" + str(len(evList)) + ") entries")
    this_cmd.Set('ProgressStepsCount', 2)
    # Comma needed to make it a proper tuple
    header = (ds_id,)
    this_cmd.Set('ProgressCurrentStep', 1)
    cursor.executemany("INSERT INTO " + table_name + " VALUES " +
                       "(?, ?, ?, ?)",
                       (header + ent for ent in evList))
    this_cmd.Set('ProgressCurrentStep', 2)
    return len(evList)


def get_db_filename(db_idx=-1):
    logger = PLLogger.GetLogger('methodology')
    project = CStcSystem.Instance().GetObject('project')
    result_setting = project.GetObject('testresultsetting')
    if result_setting is None:
        # Should never happen, it's a 1:1
        err_str = "Unable to find Test Result Setting Object"
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    result_dir = os.path.dirname(result_setting.Get('CurrentResultFileName'))
    if result_dir is None or result_dir == '':
        err_str = "No results have been saved. Unable to find directory."
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    all_db_set = set(glob.glob(os.path.join(result_dir, '*.db')))
    ts_db_list = glob.glob(os.path.join(result_dir, '*_????-??-??_??-??-??.db'))
    trim_set = set()
    for fn in ts_db_list:
        trim_set.add(fn[0:-23] + '.db')
    sort_list = list(all_db_set - trim_set)
    # sort dbs by modified time
    sort_list.sort(key=lambda fn: os.path.getmtime(fn))
    if (db_idx < 0 and -db_idx > len(sort_list)) or db_idx >= len(sort_list):
        err_str = "No results have been saved. No files in directory."
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    return sort_list[db_idx]


def get_dataset_id(cursor):
    cursor.execute('''SELECT MAX(Id) FROM DataSet''')
    return cursor.fetchone()[0]


def create_table(cursor, sql_command):
    sql_list = sql_command.split()
    # Verify the command at least has the first 2 words correct
    if sql_list[0].upper() != 'CREATE' and sql_list[1].upper() != 'TABLE':
        err_str = "Invalid TABLE CREATE SQL command"
        logger.LogError(err_str)
        raise RuntimeError(err_str)
    table_name = sql_list[2]
    # Check for existence first
    query = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' and " + \
        "name='{0}'"
    cursor.execute(query.format(table_name))
    # If it exists already, no need to create the table (or we could validate)
    if cursor.fetchone()[0] != 0:
        return
    cursor.execute(sql_command)


def get_db_type(dm_type):
    # List of types from scg.py, except for file paths
    int_list = ['s8', 's16', 's32', 's64', 'u8', 'u16', 'u32', 'u64', 'handle']
    if dm_type in int_list:
        return 'INTEGER'
    elif dm_type == 'bool':
        return 'BOOL'
    elif dm_type == 'double':
        return 'DOUBLE'
    else:
        return 'VARCHAR'
