from StcIntPythonPL import *
import json
# import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.results.ProviderDataGenerator as pdg
from spirent.methodology.results.ResultEnum import EnumDataFormat, \
    EnumExecStatus, EnumVerdict, EnumDataClass
from spirent.methodology.results.ProviderConst import ProviderConst, ChartConst
import spirent.methodology.results.ProviderUtils as pu
import spirent.methodology.results.SqliteUtils as sql_utils


PKG = "spirent.methodology"


# input_dict:
#   EnableLearning: True or Fale boolean
#   LearningMode: L2 or L3 enum
# output_dict:
#   EnableL2Learning: True or False
#   EnableL3Learning: True or False
def Rfc2544ThroughputConfigureLearning(input_dict):
    output_dict = {}
    err_msg = ""

    enable_learning = input_dict["EnableLearning"]
    learning_mode = input_dict["LearningMode"]

    # Both disabled by default
    output_dict["EnableL2Learning"] = "False"
    output_dict["EnableL3Learning"] = "False"

    # If learning enabled, determine which mode is selected
    if enable_learning == "True":
        if learning_mode == "L2":
            output_dict["EnableL2Learning"] = "True"
        elif learning_mode == "L3":
            output_dict["EnableL3Learning"] = "True"

    return output_dict, err_msg


# input_dict: input dictionary from txml with property ids replaced with user input values
# output_dict: dictionary of json data formatted for Create_____MixCommand
def Rfc2544ThroughputMixInfoProcFunction(input_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin Rfc2544ThroughputMixInfoProcFunction')
    plLogger.LogDebug('input_dict: ' + str(input_dict))
    output_dict = {}

    # Direct pass through of input dict to the output dict
    # If the JSON is invalid, the target command will catch it
    output_dict["MixInfo"] = json.dumps(input_dict["input"])

    plLogger.LogDebug('output_dict: ' + str(output_dict))
    plLogger.LogDebug('end Rfc2544ThroughputMixInfoProcFunction')
    return output_dict, ""


def Rfc2544ThroughputSetupCreateTableCmds(tagname, b, params):
    # plLogger = PLLogger.GetLogger('methodology')
    # plLogger.LogDebug("Running Rfc2544ThroughputSetupCreateTableCmds")

    res_cmd_list = tag_utils.get_tagged_objects_from_string_names(tagname)

    objectIterIndex = 0
    rateIterIndex = 0
    createTable1Index = 0
    createTable2Index = 0
    for idx, cmd in enumerate(res_cmd_list):
        if cmd.IsTypeOf(PKG + '.ObjectIteratorCommand'):
            objectIterIndex = idx
        if cmd.IsTypeOf(PKG + '.RateIteratorCommand'):
            rateIterIndex = idx
        if cmd.IsTypeOf(PKG + '.AddRowToDbTableCommand'):
            if createTable1Index == 0:
                createTable1Index = idx
            else:
                createTable2Index = idx

    # Get last frame size and load and determine if the rate iterator converged
    curFrameSize = res_cmd_list[objectIterIndex].Get('CurrVal')
    curLoad = res_cmd_list[rateIterIndex].Get('CurrVal')
    isConverged = res_cmd_list[rateIterIndex].Get('IsConverged')

    # Get converged load or use current load if it didn't converge
    convergedLoad = 0
    if isConverged:
        convergedLoad = res_cmd_list[rateIterIndex].Get('ConvergedVal')
    else:
        convergedLoad = curLoad

    create1 = "CREATE TABLE MethRfc2544Throughput ('FrameSize' INTEGER, 'FPS' FLOAT, " + \
              "'Load' FLOAT, 'MbpsLoad' FLOAT, 'DroppedCount' INTEGER, " + \
              "'ReorderedCount' INTEGER, 'DuplicateCount' INTEGER, 'TxPort' VARCHAR, " + \
              "'RxPort' VARCHAR)"
    # For a frame size, get all rows for converged value (or currVal if not converged)
    query1 = "SELECT Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
             "round(Sb.FpsLoad,2) AS 'Frames per Second', Sb.PercentageLoad AS 'Load %', " + \
             "Sb.MbpsLoad AS 'Load (Mbps)', RxRes.DroppedFrameCount AS 'Dropped Frame Count', " + \
             "RxRes.ReorderedFrameCount AS 'Reordered Frame Count', " + \
             "RxRes.DuplicateFrameCount AS 'Duplicate Frame Count', " + \
             "TxRes.PortName AS 'Tx Port', RxRes.PortName AS 'Rx Port' " + \
             "From RxEotStreamResults AS RxRes JOIN TxEotStreamResults AS TxRes " + \
             "JOIN Streamblock AS Sb ON RxRes.ParentStreamBlock  = TxRes.ParentStreamblock " + \
             "AND TxRes.ParentStreamblock = Sb.Handle WHERE Sb.FixedFrameLength == " + \
             str(curFrameSize) + " AND Sb.PercentageLoad == " + str(convergedLoad)
    res_cmd_list[createTable1Index].Set('SqlCreateTable', create1)
    res_cmd_list[createTable1Index].Set('SqlQuery', query1)

    create2 = "CREATE TABLE MethRfc2544ThroughputFrameRate ('FrameSize' INTEGER, 'FPS' FLOAT, " + \
              "'DroppedCount' INTEGER, 'MaxRate' FLOAT, 'LineSpeed' FLOAT)"
    # For a frame size and converged value (or currVal if not converged), get the row with
    # highest FPS (if multiple ports at different speeds)
    # If there's streams with dropped frames, get the row with the highest dropped count
    # Calculation of max rate from content\traffictests\custom\bll\src\TheoreticalMaxLineRate.cpp
    query2 = "SELECT Sb.FixedFrameLength AS 'Frame Size (bytes)', " + \
             "round(Sb.FpsLoad,2) AS 'Frames per Second', " + \
             "RxRes.DroppedFrameCount AS 'Dropped Frame Count', " + \
             "(((((Sb.MbpsLoad * 100.0) / Sb.PercentageLoad) * 1000000) / 8) / " + \
             "(20 + Sb.FixedFrameLength)) AS 'Theoretical Max Rate', " + \
             "((Sb.MbpsLoad * 100.0) / Sb.PercentageLoad) AS 'Line Speed' " + \
             "FROM RxEotStreamResults AS RxRes JOIN TxEotStreamResults AS TxRes JOIN " + \
             "Streamblock AS Sb ON " + \
             "RxRes.ParentStreamBlock = TxRes.ParentStreamblock AND " + \
             "TxRes.ParentStreamblock = Sb.Handle " + \
             "WHERE Sb.FixedFrameLength == " + str(curFrameSize) + " AND Sb.PercentageLoad == " + \
             str(convergedLoad) + " ORDER BY RxRes.DroppedFrameCount DESC, Sb.FpsLoad DESC LIMIT 1"
    res_cmd_list[createTable2Index].Set('SqlCreateTable', create2)
    res_cmd_list[createTable2Index].Set('SqlQuery', query2)

    return ""


def Rfc2544ThroughputVerifyResults(tagname, b, params):
    # plLogger = PLLogger.GetLogger('methodology')
    # plLogger.LogDebug("Running Rfc2544ThroughputVerifyResults")

    res_cmd_list = tag_utils.get_tagged_objects_from_string_names(tagname)
    # plLogger.LogDebug("res_cmd_list: " + str(res_cmd_list))

    objectIterIndex = 0
    multiDbQueryIndex = 0
    for idx, cmd in enumerate(res_cmd_list):
        if cmd.IsTypeOf(PKG + '.ObjectIteratorCommand'):
            objectIterIndex = idx
        if cmd.IsTypeOf(PKG + '.VerifyMultipleDbQueryCommand'):
            multiDbQueryIndex = idx

    # Get list of frame sizes from object iterator
    frameList = res_cmd_list[objectIterIndex].GetCollection('ValueList')
    # plLogger.LogDebug("frameList: " + str(frameList))

    q_list = []
    display_name_list = []
    pass_list = []
    fail_list = []
    for frame in frameList:
        # For each frame size determine if there was any streams with dropped frames
        # If so (number of rows found > 0), that is considered a failure
        display_name_list.append('Frame Size ' + str(frame))
        pass_list.append('Found frame rate with no dropped frames for frame size ' + str(frame))
        fail_list.append('Found dropped frames for all frame rates with frame size ' + str(frame))
        q = "SELECT FrameSize AS 'Frame Size (bytes)', Load AS 'Load %', " + \
            "FPS AS 'Frames per Second', DroppedCount AS 'Dropped Frame Count' From " + \
            "MethRfc2544Throughput WHERE FrameSize == " + str(frame) + " AND DroppedCount > 0"
        q_list.append(q)

    res_cmd_list[multiDbQueryIndex].SetCollection('DisplayNameList', display_name_list)
    res_cmd_list[multiDbQueryIndex].SetCollection('PassedVerdictExplanationList', pass_list)
    res_cmd_list[multiDbQueryIndex].SetCollection('FailedVerdictExplanationList', fail_list)
    res_cmd_list[multiDbQueryIndex].SetCollection('SqlQueryList', q_list)
    res_cmd_list[multiDbQueryIndex].Set('UseMultipleResultsDatabases', False)
    res_cmd_list[multiDbQueryIndex].Set('UseSummary', True)

    return ""


# base_template is customized by the author based on what
# type of chart is needed for specific methodology's report
base_template = {
    "title": {
        "text": "Frame Rate Results",
        "x": 0
    },
    "xAxis": {
        "categories": "xcat_data",
        "labels": {
            "rotation": 0
        },
        "title": {
            "text": "Frame Size (bytes)"
        }
    },
    "yAxis": [{
        "categories": None,
        "min": 0,
        "title": {
            "text": "Frame Rate (fps)"
        }
    }],
    "tooltip": {
        "valueSuffix": " (frames/sec)"
    },
    "series": [
        {
            "type": "line",
            "name": "Actual Rate",
            "data": "fps_data",
            "color": '#0080FF',
            "lineWidth": "4",
            "states": {
                "hover": {
                    "lineWidth": "1"
                }
            }
        },
        {
            "type": "line",
            "name": "Theoretical Maximum Rate",
            "data": "theoretical_fps_data",
            "color": '#3ADF00'
        }
    ]
}


def Rfc2544ThroughputCreateChart(tagname, b, params):
    # plLogger = PLLogger.GetLogger('methodology')
    # plLogger.LogDebug("Running Rfc2544ThroughputCreateChart")
    db_list = get_dbs(False, True)

    # Frame size (X axis names)
    q_xcat = str("SELECT FrameSize From MethRfc2544ThroughputFrameRate")
    # Found frame rate for each frame size (report 0 if there's dropped frames)
    q_fps = str("SELECT CASE WHEN DroppedCount > 0 THEN 0 ELSE FPS END " +
                "From MethRfc2544ThroughputFrameRate")
    # Get theoretical maximum rate
    q_maxfps = str("SELECT round(MaxRate,0) From MethRfc2544ThroughputFrameRate")

    # Run the db queries
    xcat_data = get_data_from_query(db_list, q_xcat)
    fps_data = get_data_from_query(db_list, q_fps)
    theoretical_fps_data = get_data_from_query(db_list, q_maxfps)

    # Fill in the template with the results
    base_template['xAxis']['categories'] = xcat_data
    base_template['series'][0]['data'] = fps_data
    base_template['series'][1]['data'] = theoretical_fps_data

    # This fills in the json file with our chart results?
    result_data = init_chart_data_dict("SUMMARY")
    pdg.submit_provider_data(result_data)

    return ""


def get_data_from_query(db_file_list, query):
    result_data = sql_utils.get_all_data(db_file_list, query)
    rows = result_data[ProviderConst.ROW]
    row_data = []
    for row in rows:
        row_data.append(row[0])
    return row_data


def get_dbs(UseMultipleResultsDatabases, UseSummary):
    if UseSummary and not UseMultipleResultsDatabases:
        return [pu.get_active_result_db_filename()]
    return pu.get_db_files(pu.get_active_result_db_filename(), UseMultipleResultsDatabases)


def init_chart_data_dict(ReportGroup):
    info = {
        ProviderConst.REPORT_GROUP: ReportGroup
    }
    status = {
        ProviderConst.VERDICT: EnumVerdict.none,
        ProviderConst.VERDICT_TEXT: '',
        ProviderConst.EXEC_STATUS: EnumExecStatus.completed,
        ProviderConst.APPLY_VERDICT: 'false'
    }
    data = {
        ChartConst.BASE_NAME: base_template,
        ChartConst.TITLE: '',
        ChartConst.X_CAT: '',
        ChartConst.X_LAB: '',
        ChartConst.Y_CAT: '',
        ChartConst.Y_LAB: '',
        ChartConst.SERIES: '',
        ChartConst.MOD_LIST: ''
    }
    provider_data = {
        ProviderConst.DATA_FORMAT: EnumDataFormat.chart,
        ProviderConst.CLASS: EnumDataClass.methodology_chart,
        ProviderConst.INFO: info,
        ProviderConst.STATUS: status,
        ProviderConst.DATA: data
    }
    return provider_data


def get_procfunction_input_schema():
    return '''
    {
        "type": "object",
        "properties": {
            "id": {
                "type": "string"
            },
            "scriptFile": {
                "type": "string"
            },
            "entryFunction": {
                "type": "string"
            },
            "input": {
                "type": "object"
            },
            "output": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scriptVarName": {
                            "type": "string"
                        },
                        "epKey": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
    '''
