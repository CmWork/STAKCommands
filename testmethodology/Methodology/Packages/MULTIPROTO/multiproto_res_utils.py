from StcIntPythonPL import *
import json
import sqlite3
import spirent.methodology.results.ProviderUtils as res_pu
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
from spirent.methodology.sampling.AppendToEotCommand \
    import get_db_filename


PKG = "spirent.methodology"
PKG_CORE = "spirent.core"
PKG_SMP = "spirent.methodology.sampling"
OBJ_KEY = PKG_SMP


# FIXME:
# Get rid of this once wait for state command is
# merged into the polling commands (sampling)
# input_dict:
# { "enable": true }
def config_enable_terminal_value_condition(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    err_str, input_dict = json_utils.load_json(input_json)
    plLogger.LogInfo("input_dict:" + str(input_dict))

    if "enable" not in input_dict.keys():
        plLogger.LogError("Expected enable to be in the input.")
        return "Missing enable parameter in the input_dict"

    if not CObjectRefStore.Exists(OBJ_KEY):
        err = "Persistent storage not properly initialized.  " + \
            "Add a SetupSubscriptionCommand."
        plLogger.LogError(err)
        return err

    samp_dict = CObjectRefStore.Get(OBJ_KEY)
    if 'Subscription' not in samp_dict:
        err = "Persistent storage is missing subscription.  " + \
            "Fix the SetupSubscriptionCommand."
        plLogger.LogError(err)
        return err

    # Everything in python is by reference, so we can modify subList
    sub_list = samp_dict['Subscription']

    # Since only one "instance" of the sampling framework is allowed
    # (due to the persistent object storage), set all of the
    # EnableCondition flags
    for sub in sub_list:
        plLogger.LogDebug("process subscription: " + str(sub))
        sub["EnableCondition"] = input_dict["enable"]
        plLogger.LogDebug("updated subscription: " + str(sub))


# FIXME:
# Get rid of this once the sampling framework is refactored
def release_sampling_object_reference(tagname, b, input_json):
    ctor = CScriptableCreator()

    if CObjectRefStore.Exists(OBJ_KEY):
        cmd = ctor.CreateCommand(PKG_CORE +
                                 ".ReleaseObjectReferenceCommand")
        cmd.Set("Key", OBJ_KEY)
        cmd.Execute()
        cmd.MarkDelete()


def get_state_summ_res_map():
    res_map = {}
    # Set up a results map to map protocols to results
    # BFD
    res_map["BfdRouterConfig"] = {
        "Name": "BFD",
        "ConfigType": "Project",
        "ResultType": "BfdStateSummary",
        "ProtoUpProp": "SessionsUpCount",
        "ProtoDownProp": "SessionsDownCount",
        "ViewAttributeList": ["SessionsUpCount",
                              "SessionsDownCount"]}
    # BGP
    res_map["BgpRouterConfig"] = {
        "Name": "BGP",
        "UpState": "Established",
        "ConfigType": "Project",
        "ResultType": "BgpStateSummary",
        "ProtoUpProp": "RouterUpCount",
        "ProtoDownProp": "RouterDownCount",
        "ViewAttributeList": ["IdleCount", "ConnectCount",
                              "ActiveCount", "OpenSentCount",
                              "OpenConfirmCount", "EstablishedCount",
                              "RouterUpCount",
                              "RouterDownCount"]}
    # ISIS
    res_map["IsisRouterConfig"] = {
        "Name": "ISIS",
        "ConfigType": "Project",
        "ResultType": "IsisStateSummary",
        "ProtoUpProp": "RouterUpCount",
        "ProtoDownProp": "RouterDownCount",
        "ViewAttributeList": ["IdleCount", "InitCount",
                              "UpCount", "GrCount",
                              "GrHelperCount"]}
    # LDP
    res_map["LdpRouterConfig"] = {
        "Name": "LDP",
        "ConfigType": "Project",
        "ResultType": "LdpStateSummary",
        "ProtoUpProp": "RouterUpCount",
        "ProtoDownProp": "RouterDownCount",
        "ViewAttributeList": ["SessionUpCount",
                              "SessionFailedCount",
                              "SessionOpenCount",
                              "SessionConnectCount",
                              "SessionRestartCount",
                              "SessionHelperCount"]}
    # OSPFv2
    res_map["Ospfv2RouterConfig"] = {
        "Name": "OSPFv2",
        "ConfigType": "Project",
        "ResultType": "Ospfv2StateSummary",
        "ProtoUpProp": "RouterUpCount",
        "ProtoDownProp": "RouterDownCount",
        "ViewAttributeList": ["DownCount", "LoopbackCount",
                              "WaitingCount", "P2PCount",
                              "DrOtherCount", "BackupCount",
                              "DrCount", "NotStartedCount",
                              "RouterUpCount", "RouterDownCount"]}
    # OSPFv3
    res_map["Ospfv3RouterConfig"] = {
        "Name": "OSPFv3",
        "ConfigType": "Project",
        "ResultType": "Ospfv3StateSummary",
        "ProtoUpProp": "RouterUpCount",
        "ProtoDownProp": "RouterDownCount",
        "ViewAttributeList": ["DownCount", "LoopbackCount",
                              "WaitingCount", "P2PCount",
                              "DrOtherCount", "BackupCount",
                              "DrCount", "NotStartedCount",
                              "RouterUpCount", "RouterDownCount"]}
    return res_map


def get_router_res_map():
    res_map = {}
    # Set up a results map to map protocols to results
    # BFD
    res_map["BfdRouterConfig"] = {
        "ConfigType": "BfdRouterConfig",
        "ResultType": "BfdRouterResults",
        "ViewAttributeList": ["FlapCount"]}
    return res_map


def get_proto_counts(proto_mix_list):
    plLogger = PLLogger.GetLogger("Methodology")
    res_map = get_state_summ_res_map()

    proto_dict = {}
    for proto_mix in proto_mix_list:
        plLogger.LogDebug("proto_mix: " + proto_mix.Get("Name"))
        template_list = proto_mix.GetObjects("StmTemplateConfig")
        plLogger.LogDebug("template list: " + str(template_list))
        for template in template_list:
            plLogger.LogDebug("template: " + template.Get("Name"))
            dev_list = template.GetObjects("EmulatedDevice",
                                           RelationType("GeneratedObject"))
            for dev in dev_list:
                for class_name in res_map.keys():
                    proto = dev.GetObject(class_name)
                    if proto:
                        count = dev.Get('DeviceCount')
                        if class_name not in proto_dict:
                            proto_dict[class_name] = count
                        else:
                            proto_dict[class_name] = proto_dict[class_name] + count
    return proto_dict


def get_bfd_session_count(proto_mix_list):
    plLogger = PLLogger.GetLogger("Methodology")

    # FIXME:
    # There's probably a better way to do this...
    bfd_sess_count = 0

    for proto_mix in proto_mix_list:
        plLogger.LogDebug("proto_mix: " + proto_mix.Get("Name"))
        template_list = proto_mix.GetObjects("StmTemplateConfig")
        plLogger.LogDebug("template list: " + str(template_list))
        for template in template_list:
            plLogger.LogDebug("template: " + template.Get("Name"))
            dev_list = template.GetObjects("EmulatedDevice",
                                           RelationType("GeneratedObject"))
            dev_count = 0
            uses_v4 = False
            uses_v6_global = False
            uses_v6_link = False

            for dev in dev_list:
                tli_list = dev.GetObjects("NetworkInterface",
                                          RelationType("TopLevelIf"))
                bgp_proto = dev.GetObject("BgpRouterConfig")
                if bgp_proto:
                    if bgp_proto.Get("EnableBfd"):
                        if bgp_proto.Get("IpVersion") == "IPV4":
                            uses_v4 = True
                        else:
                            uses_v6_global = True
                ospfv3_proto = dev.GetObject("Ospfv3RouterConfig")
                if ospfv3_proto and ospfv3_proto.Get("EnableBfd"):
                        uses_v6_link = True
                isis_proto = dev.GetObject("IsisRouterConfig")
                if isis_proto:
                    if isis_proto.Get("IpVersion") == "IPV4":
                        uses_v4 = True
                    elif isis_proto.Get("IpVersion") == "IPv6":
                        uses_v6_global = True
                    else:
                        uses_v4 = True
                        uses_v6_global = True
                ldp_proto = dev.GetObject("LdpRouterConfig")
                if ldp_proto:
                    for tli in tli_list:
                        if tli.IsTypeOf("Ipv4If"):
                            uses_v4 = True
                        elif tli.IsTypeOf("Ipv6If"):
                            uses_v6_global = True
                dev_count = dev_count + dev.Get("DeviceCount")

            if uses_v4:
                bfd_sess_count = bfd_sess_count + dev_count
            if uses_v6_global:
                bfd_sess_count = bfd_sess_count + dev_count
            if uses_v6_link:
                bfd_sess_count = bfd_sess_count + dev_count
    return bfd_sess_count


def get_table_column_list(db_curs, table_name):
    db_curs.execute('PRAGMA table_info({})'.format(table_name))
    rows = db_curs.fetchall()
    return [str(row[1]) for row in rows]


# This command sets up the property list and the
# terminal value list for the
# spirent.methodology.sampling.SetupSubscriptionCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_subscribe_polling_results(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_subscribe_polling_results script")

    err_str, input_dict = json_utils.load_json(input_json)
    plLogger.LogInfo("input_dict:" + str(input_dict))
    plLogger.LogInfo("err_str:" + str(err_str))

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG_SMP + ".SetupSubscriptionCommand")
    if not cmd_list:
        plLogger.LogError("Could not find a tagged " + PKG_SMP +
                          ".SetupSubscriptionCommand")
        return "Could not find a tagged " + PKG_SMP + \
            ".SetupSubscriptionCommand in the sequence."
    plLogger.LogDebug("cmd_list: " + str(cmd_list))

    # Set up a results map to map protocols to results
    res_map = get_state_summ_res_map()
    rtr_res_map = get_router_res_map()

    term_val_list = []
    prop_list = []

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON:  " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")
    if not proto_mix_list:
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))

    proto_dict = get_proto_counts(proto_mix_list)
    bfd_sess_count = get_bfd_session_count(proto_mix_list)
    proto_dict['BfdRouterConfig'] = bfd_sess_count
    plLogger.LogDebug("BFD Session Count: " + str(bfd_sess_count))
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    for proto_class in proto_dict.keys():
        if proto_dict[proto_class]:
            prop_list.append(res_map[proto_class]["ConfigType"] + "." +
                             res_map[proto_class]["ResultType"] + "." +
                             res_map[proto_class]["ProtoUpProp"])
            if proto_class in rtr_res_map.keys():
                prop_list.append(rtr_res_map[proto_class]["ConfigType"] + "." +
                                 rtr_res_map[proto_class]["ResultType"] + "." +
                                 "FlapCount")
                term_val_list.append(0)
            if proto_class == "BfdRouterConfig":
                term_val_list.append(bfd_sess_count)
            else:
                term_val_list.append(proto_dict[proto_class])

    prop_list.append('Analyzer.AnalyzerPortResults.SigFrameRate')
    term_val_list.append(0)

    for cmd in cmd_list:
        plLogger.LogDebug("configuring command " + cmd.Get("Name"))
        plLogger.LogDebug("prop_list: " + str(prop_list))
        plLogger.LogDebug("term_val_list: " + str(term_val_list))
        cmd.Set("PropertyList", " ".join(prop_list))
        cmd.Set("EnableCondition", False)
        cmd.SetCollection("TerminalValueList", term_val_list)


# This command sets up the queries, titles, and
# verdict explanations for the
# spirent.methodology.VerifyMultipleDbQueryCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_verify_db_query_cmd(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_verify_db_query_cmd")
    project = CStcSystem.Instance().GetObject("Project")

    err_str, input_dict = json_utils.load_json(input_json)

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG + ".VerifyMultipleDbQueryCommand")
    if len(cmd_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".VerifyMultipleDbQueryCommand")
        return "Could not find a tagged " + PKG + \
            ".VerifyMultipleDbQueryCommand in the sequence."

    plLogger.LogDebug("cmd_list: " + str(cmd_list))

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON: " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))
    if not len(proto_mix_list):
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    proto_dict = get_proto_counts(proto_mix_list)
    bfd_sess_count = get_bfd_session_count(proto_mix_list)
    proto_dict['BfdRouterConfig'] = bfd_sess_count
    plLogger.LogDebug("BFD Session Count: " + str(bfd_sess_count))
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    query_list = []
    disp_name_list = []
    pass_exp_list = []
    fail_exp_list = []
    res_map = get_state_summ_res_map()
    for proto, value in proto_dict.items():
        if value == 0:
            continue
        attr_list = res_map[proto]['ViewAttributeList']
        res_type = res_map[proto]['ResultType']
        up_prop = res_map[proto]['ProtoUpProp']
        name = res_map[proto].get('Name', proto.replace('RouterConfig', ''))
        up_state = res_map[proto].get('UpState', 'Up')
        q = "SELECT {} FROM {} WHERE ParentHnd = {} " \
            "AND {} != {}".format(', '.join(attr_list), res_type,
                                  project.GetObjectHandle(),
                                  up_prop, value)
        query_list.append(q)
        disp_name_list.append("Verify {} Router State".format(name))
        pass_exp_list.append("All {} Routers are in {} State.".format(name,
                                                                      up_state))
        fail_exp_list.append("Not all {} Routers are in {} State.".format(name,
                                                                          up_state))
    proto = 'BfdRouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        # Separate addition
        query_list.append(
            "SELECT FlapCount " +
            "FROM BfdRouterResults " +
            "WHERE FlapCount > 0")
        disp_name_list.append("Verify BFD Flap Counts")
        pass_exp_list.append("No BFD Flaps Detected.")
        fail_exp_list.append("BFD Flaps Detected.")

    # Configure the target command(s)
    for cmd in cmd_list:
        plLogger.LogDebug("configuring command " + cmd.Get("Name"))
        plLogger.LogDebug("query_list: " + str(query_list))
        cmd.SetCollection("SqlQueryList", query_list)
        cmd.SetCollection("DisplayNameList", disp_name_list)
        cmd.SetCollection("PassedVerdictExplanationList", pass_exp_list)
        cmd.SetCollection("FailedVerdictExplanationList", fail_exp_list)


# This command sets up the queries, titles, and
# verdict explanations for the
# spirent.methodology.CreateMethodologyChartCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_create_meth_chart_cmd(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_create_meth_chart_cmd")

    err_str, input_dict = json_utils.load_json(input_json)

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG + ".CreateMethodologyChartCommand")
    if len(cmd_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".CreateMethodologyChartCommand")
        return "Could not find a tagged " + PKG + \
            ".CreateMethodologyChartCommand in the sequence."

    plLogger.LogDebug("cmd_list: " + str(cmd_list))

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON: " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))
    if not len(proto_mix_list):
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    res_map = get_state_summ_res_map()
    proto_dict = get_proto_counts(proto_mix_list)
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    query_list = []
    title_list = []
    axis_list = []

    # Add queries for each protocol (count is on Y-axis)
    for key, value in proto_dict.items():
        if value == 0:
            continue
        # Create field name
        subs = res_map[key]["ResultType"] + "_" + res_map[key]["ProtoUpProp"]
        title_list.append(key.replace('RouterConfig', ''))
        fmt = 'SELECT Timestamp - ' \
            '(SELECT MIN(Timestamp) FROM Methodology_SamplingData),' \
            '{} AS count ' \
            'FROM Methodology_SamplingData ' \
            'WHERE count IS NOT null GROUP BY Timestamp'
        q = fmt.format(subs)
        query_list.append(q)
        axis_list.append(0)

    # Add loads
    if "portGroupTagList" not in input_dict.keys():
        plLogger.LogError("Expected portGroupTagList to be in the " +
                          "input.")
        return "Missing portGroupTagList in input_dict"
    plLogger.LogDebug("portGroupTagList from JSON: " +
                      str(input_dict["portGroupTagList"]))

    port_list = input_dict["portGroupTagList"]
    plLogger.LogDebug("Port Tag List: " + str(port_list))

    title_list = title_list + ['{} Load'.format(p) for p in port_list]
    for port_tag in port_list[::-1]:
        port_list = tag_utils.get_tagged_objects_from_string_names([port_tag])
        # Only using one port for now, FIXME later
        plLogger.LogDebug("ports retrieved from {}: {}".
                          format(port_tag, [p.Get('Name') for p in port_list]))
        ana = port_list[0].GetObjects('Analyzer')[0]
        fmt = 'SELECT Timestamp - ' \
            '(SELECT MIN(Timestamp) FROM Methodology_SamplingData), ' \
            'AnalyzerPortResults_SigFrameRate AS Rate ' \
            'FROM Methodology_SamplingData AS SData ' \
            'INNER JOIN RelationTable ' \
            'ON TargetHnd=SubscriptionHandle WHERE Rate IS NOT NULL ' \
            'AND SourceHnd={} ORDER BY Timestamp'
        q = fmt.format(ana.GetObjectHandle())
        query_list.append(q)
        axis_list.append(1)

    # Event processing
    iter_db = get_db_filename()
    plLogger.LogDebug("iter_db: {}".format(iter_db))
    conn = sqlite3.connect(iter_db)
    cur = conn.cursor()
    # Gather events
    sql = 'SELECT EventType, TimeStamp - (SELECT MIN(Timestamp) ' \
        'FROM Methodology_SamplingData) FROM Methodology_SamplingEvent'
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    plLogger.LogDebug("Events: {}".format(rows))
    plot_lines = [{'color': 'green', 'label': {'text': e[0]}, 'value': e[1],
                   'width': 2} for e in rows]
    modifier = [{'series': [{'name': x, 'yAxis': a}
                            for x, a in zip(title_list, axis_list)],
                 'xAxis': {'plotLines': plot_lines},
                 'yAxis': [{'title': {'text': 'Routers Up'},
                            'min': 0},
                           {'title': {'text': 'Traffic Load'},
                            'opposite': True,
                            'min': 0}]}]

    # Configure the target command(s)
    for cmd in cmd_list:
        plLogger.LogDebug("configuring command " + cmd.Get("Name"))
        plLogger.LogDebug("series_data: " + str(query_list))
        cmd.Set('TemplateModifier', json.dumps(modifier))
        cmd.SetCollection("Series", query_list)


# This command sets up the query for the
# spirent.methodology.AddRowToDbTableCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_add_row_to_db_table_cmd(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_add_row_to_db_table_cmd")
    project = CStcSystem.Instance().GetObject("Project")

    err_str, input_dict = json_utils.load_json(input_json)
    res_map = get_state_summ_res_map()

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG + ".AddRowToDbTableCommand")
    if len(cmd_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".AddRowToDbTableCommand")
        return "Could not find a tagged " + PKG + \
            ".AddRowToDbTableCommand in the sequence."

    plLogger.LogDebug("cmd_list: " + str(cmd_list))
    if len(cmd_list) > 1:
        plLogger.LogError("Found more than one " + PKG +
                          ".AddRowToDbTableCommand that was tagged " +
                          "with " + input_dict["cmdTag"] + ".  Only " +
                          "one command should be tagged.")
        return "Found more than one " + PKG + \
            ".AddRowToDbTableCommand that was tagged with " + \
            input_dict["cmdTag"]
    add_row_cmd = cmd_list[0]

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON: " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))
    if not len(proto_mix_list):
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    # Find the iterator
    # This object (in the db) is tagged as:
    # BenchmarkStabilityIteratorCommand.DeviceCount
    iter_cmd_tag = "BenchmarkStabilityIteratorCommand.DeviceCount"
    iter_table = "spirent_methodology_BenchmarkStabilityIteratorCommand"
    iter_db = get_db_filename()
    plLogger.LogDebug("iter_db: " + str(iter_db))
    conn = sqlite3.connect(iter_db)
    cur = conn.cursor()

    # Find the tag
    cur.execute("SELECT Handle FROM Tag WHERE Name=\"" + iter_cmd_tag + "\"")
    rows = cur.fetchall()
    plLogger.LogDebug("Tag contains: " + str(rows))
    if len(rows) > 1:
        err_msg = "Found more than one Tag in the Tag table named " + \
            iter_cmd_tag + "."
        plLogger.LogError(err_msg)
        return err_msg
    tag_row_data = rows[0]
    tag_hnd = tag_row_data[0]
    plLogger.LogDebug("Tag handle: " + str(tag_hnd))

    # Find the tagged command.  Use the RelationTable
    cur.execute("SELECT Handle FROM " + iter_table)
    rows = cur.fetchall()
    plLogger.LogDebug(iter_table + " contains: " + str(rows))
    iter_hnd = 0
    for row_tuple in rows:
        hnd = row_tuple[0]
        plLogger.LogDebug("process hnd: " + str(hnd))
        cur.execute("SELECT * FROM RelationTable " +
                    "WHERE Type=\"UserTag\" " +
                    "AND SourceHnd=" + str(hnd) + " " +
                    "AND TargetHnd=" + str(tag_hnd))
        rows = cur.fetchall()
        # If any rows are returned, hnd contains the handle
        # of the iterator command that is tagged with the
        # BenchmarkStabilityIteratorCommand.DeviceCount tag.
        if len(rows) > 0:
            iter_hnd = hnd
            break
    plLogger.LogDebug(PKG + ".BenchmarkStabilityIteratorCommand handle " +
                      "from the iteration database: " + str(hnd))
    if not iter_hnd:
        err_msg = "Could not find a " + PKG + \
            ".BenchmarkStabilityIteratorCommand tagged with " + \
            "BenchmarkStabilityIteratorCommand.DeviceCount " + \
            "in the iteration db: " + str(iter_db)
        plLogger.LogError(err_msg)
        return err_msg
    conn.close()

    proto_dict = get_proto_counts(proto_mix_list)
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    col_list = []
    type_list = []
    select_list = []
    from_list = []
    where_list = []
    for proto_pair in zip(["BfdRouterConfig", "BgpRouterConfig",
                           "IsisRouterConfig", "LdpRouterConfig",
                           "Ospfv2RouterConfig",
                           "Ospfv3RouterConfig"],
                          ["Bfd", "Bgp", "Isis", "Ldp",
                           "Ospfv2", "Ospfv3"]):
        proto_conf = proto_pair[0]
        alias = proto_pair[1]
        if proto_conf in proto_dict and proto_dict[proto_conf] > 0:
            for prop in ["ProtoUpProp", "ProtoDownProp"]:
                select_list.append("SUM(" + alias + "." +
                                   res_map[proto_conf][prop] + ")")
                col_list.append(proto_conf + "_" + prop)
                type_list.append("INTEGER")
            from_list.append(res_map[proto_conf]["ResultType"] +
                             " AS " + alias)
            where_list.append(alias + ".ParentHnd == " +
                              str(project.GetObjectHandle()))

    # Add on the iteration information
    col_list.append("IteratorCommand_Iteration")
    col_list.append("IteratorCommand_IterState")
    col_list.append("IteratorCommand_CurrVal")
    type_list.append("INTEGER")
    type_list.append("VARCHAR")
    type_list.append("VARCHAR")

    select_list.append("iter.Iteration")
    select_list.append("iter.IterState")
    select_list.append("iter.CurrVal")

    from_list.append(iter_table + " AS iter")

    where_list.append("iter.Handle == " + str(iter_hnd))

    plLogger.LogDebug("col_list: " + str(col_list))
    plLogger.LogDebug("select_list: " + str(select_list))
    plLogger.LogDebug("from_list: " + str(from_list))
    plLogger.LogDebug("where_list: " + str(where_list))

    # Assemble the create string
    create = "CREATE TABLE Methodology_ProtocolIterationData ("
    is_first = True
    for item in zip(col_list, type_list):
        col_item = item[0]
        type_item = item[1]
        if is_first:
            is_first = False
        else:
            create = create + ", "
        create = create + "\'" + col_item + "\' " + type_item
    create = create + ")"
    plLogger.LogDebug("Create Table: " + create)

    # Assemble the query string
    query = "SELECT "
    is_first = True
    for select_item in select_list:
        if is_first:
            is_first = False
            query = query + select_item
        else:
            query = query + ", " + select_item
    query = query + " FROM "
    is_first = True
    for from_item in from_list:
        if is_first:
            is_first = False
            query = query + from_item
        else:
            query = query + ", " + from_item
    query = query + " WHERE "
    is_first = True
    for where_item in where_list:
        if is_first:
            is_first = False
            query = query + where_item
        else:
            query = query + " AND " + where_item
    plLogger.LogDebug("Sql Query: " + query)

    # Configure the target command
    plLogger.LogDebug("configuring command " + add_row_cmd.Get("Name"))
    add_row_cmd.Set("SqlQuery", query)
    add_row_cmd.Set("SqlCreateTable", create)


# This command sets up the queries, titles, and modifiers for the
# spirent.methodology.CreateMethodologyChartCommand
#   tagname, tagged chart command name
#   obj_list should point to tagged command(s)
#   input_json, unused
def set_up_summary_chart_cmd(tagname, obj_list, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_summary_chart_cmd")
    obj_list = [obj for obj in obj_list if obj is not None and
                obj.IsTypeOf(PKG + '.CreateMethodologyChartCommand')]
    if len(obj_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".CreateMethodologyChartCommand")
        return "Could not find a tagged " + PKG + \
            ".CreateMethodologyChartCommand in the sequence."
    plLogger.LogDebug("obj_list: " + str(obj_list))

    # Load summary
    summ_db = res_pu.get_active_result_db_filename()
    plLogger.LogDebug("summ_db: {}".format(summ_db))
    conn = sqlite3.connect(summ_db)
    cur = conn.cursor()
    col_list = get_table_column_list(cur, 'Methodology_ProtocolIterationData')
    cur.execute("SELECT MIN(IteratorCommand_Iteration) - "
                "(SELECT IteratorCommand_Iteration FROM "
                "Methodology_ProtocolIterationData) - 0.5 "
                "FROM Methodology_ProtocolIterationData "
                "WHERE IteratorCommand_IterState='STABILITY'")
    stab_val = cur.fetchall()[0]
    # Unwrap the row of tuple, arriving at None or float number
    while type(stab_val) in [list, tuple]:
        stab_val = stab_val[0]
    conn.close()
    col_list = [e for e in col_list
                if e.endswith('UpProp') or e.endswith('DownProp')]
    plLogger.LogDebug("Column List: {}".format(col_list))
    query_list = []
    # A tuple of name and stack
    series_info_list = []
    short_dict = {
        'BfdRouterConfig': 'Bfd',
        'BgpRouterConfig': 'Bgp',
        'IsisRouterConfig': 'Isis',
        'LdpRouterConfig': 'Ldp',
        'Ospfv2RouterConfig': 'Ospfv2',
        'Ospfv3RouterConfig': 'Ospfv3'
    }
    for col in col_list:
        proto = col.split('_')[0]
        short = short_dict.get(proto,
                               proto.replace('RouterConfig', ''))
        p = 'Up' if 'ProtoUpProp' in col else 'Down'
        q = 'SELECT {} FROM Methodology_ProtocolIterationData ' \
            'ORDER BY IteratorCommand_Iteration'.format(col)
        series_info_list.append((short + ' ' + p, short))
        query_list.append(q)
    modifier = [{'series':
                 [{'name': si[0], 'stack': si[1], 'type': 'column'}
                  for si in series_info_list],
                 'yAxis': {
                     'allowDecimals': False,
                     'min': 0,
                     'stackLabels': {
                         'enabled': True,
                         'format': '{stack}'
                     },
                 },
                 'tooltip': {
                     'headerFormat': '<b>Iteration {point.key}</b><br/>',
                     'pointFormat': '<span style="color:{point.color}">*'
                                    '</span> {series.name}: '
                                    '<b>{point.y}</b><br/>'
                                    'Total: {point.stackTotal}',
                 },
                 'plotOptions': {
                     'column': {
                         'stacking': 'normal'
                     }
                 }}]
    if stab_val is not None:
        x_dict = {'plotLines': [{'color': 'green',
                                 'label': {'text': 'Search'},
                                 'value': -0.5,
                                 'width': 2},
                                {'color': 'green',
                                 'label': {'text': 'Stability'},
                                 'value': stab_val,
                                 'width': 2}]}
        modifier[0]['xAxis'] = x_dict

    cat_query = "SELECT IteratorCommand_Iteration " \
        "FROM Methodology_ProtocolIterationData"
    for cmd in obj_list:
        plLogger.LogDebug("configuring command " + cmd.Get("Name"))
        plLogger.LogDebug("series_data: " + str(query_list))
        cmd.SetCollection("Series", query_list)
        cmd.Set('SrcDatabase', 'SUMMARY')
        cmd.Set('TemplateModifier', json.dumps(modifier))
        cmd.SetCollection('XAxisCategories', [cat_query])


# This command sets up the query for the
# spirent.methodology.AddRowToDbTableCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_flap_add_row_to_db_table_cmd(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_rlap_add_row_to_db_table_cmd")
    project = CStcSystem.Instance().GetObject("Project")

    err_str, input_dict = json_utils.load_json(input_json)
    res_map = get_state_summ_res_map()

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG + ".AddRowToDbTableCommand")
    if len(cmd_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".AddRowToDbTableCommand")
        return "Could not find a tagged " + PKG + \
            ".AddRowToDbTableCommand in the sequence."

    plLogger.LogDebug("cmd_list: " + str(cmd_list))
    if len(cmd_list) > 1:
        plLogger.LogError("Found more than one " + PKG +
                          ".AddRowToDbTableCommand that was tagged " +
                          "with " + input_dict["cmdTag"] + ".  Only " +
                          "one command should be tagged.")
        return "Found more than one " + PKG + \
            ".AddRowToDbTableCommand that was tagged with " + \
            input_dict["cmdTag"]
    add_row_cmd = cmd_list[0]

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON: " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))
    if not len(proto_mix_list):
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    # Find the iterator
    # This object (in the db) is tagged as:
    # BenchmarkStabilityIteratorCommand.DeviceCount
    iter_cmd_tag = "BenchmarkStabilityIteratorCommand.DeviceCount"
    iter_table = "spirent_methodology_BenchmarkStabilityIteratorCommand"
    iter_db = get_db_filename()
    plLogger.LogDebug("iter_db: " + str(iter_db))
    conn = sqlite3.connect(iter_db)
    cur = conn.cursor()

    # Find the tag
    cur.execute("SELECT Handle FROM Tag WHERE Name=\"" + iter_cmd_tag + "\"")
    rows = cur.fetchall()
    plLogger.LogDebug("Tag contains: " + str(rows))
    if len(rows) > 1:
        err_msg = "Found more than one Tag in the Tag table named " + \
            iter_cmd_tag + "."
        plLogger.LogError(err_msg)
        return err_msg
    tag_row_data = rows[0]
    tag_hnd = tag_row_data[0]
    plLogger.LogDebug("Tag handle: " + str(tag_hnd))

    # Find the tagged command.  Use the RelationTable
    cur.execute("SELECT Handle FROM " + iter_table)
    rows = cur.fetchall()
    plLogger.LogDebug(iter_table + " contains: " + str(rows))
    iter_hnd = 0
    for row_tuple in rows:
        hnd = row_tuple[0]
        plLogger.LogDebug("process hnd: " + str(hnd))
        cur.execute("SELECT * FROM RelationTable " +
                    "WHERE Type=\"UserTag\" " +
                    "AND SourceHnd=" + str(hnd) + " " +
                    "AND TargetHnd=" + str(tag_hnd))
        rows = cur.fetchall()
        # If any rows are returned, hnd contains the handle
        # of the iterator command that is tagged with the
        # BenchmarkStabilityIteratorCommand.DeviceCount tag.
        if len(rows) > 0:
            iter_hnd = hnd
            break
    plLogger.LogDebug(PKG + ".BenchmarkStabilityIteratorCommand handle " +
                      "from the iteration database: " + str(hnd))
    if not iter_hnd:
        err_msg = "Could not find a " + PKG + \
            ".BenchmarkStabilityIteratorCommand tagged with " + \
            "BenchmarkStabilityIteratorCommand.DeviceCount " + \
            "in the iteration db: " + str(iter_db)
        plLogger.LogError(err_msg)
        return err_msg
    conn.close()

    proto_dict = get_proto_counts(proto_mix_list)
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    col_list = []
    type_list = []
    select_list = []
    from_list = []
    where_list = []

    for proto_pair in zip(["BgpRouterConfig",
                           "IsisRouterConfig", "LdpRouterConfig",
                           "Ospfv2RouterConfig",
                           "Ospfv3RouterConfig"],
                          ["Bgp", "Isis", "Ldp",
                           "Ospfv2", "Ospfv3"]):

        proto_conf = proto_pair[0]
        alias = proto_pair[1]
        if proto_conf in proto_dict and proto_dict[proto_conf] > 0:
            for prop in ["FlapDetected"]:
                resType = res_map[proto_conf]["ResultType"]
                rtrUpRes = resType + "_RouterUpCount"
                colName = alias + "_FlapDetected"
                sessUpQuery = str("(SELECT DISTINCT " +
                                  "Da." + rtrUpRes +
                                  " FROM Methodology_SamplingEvent AS " +
                                  "Ev JOIN Methodology_SamplingData AS " +
                                  "Da ON Ev.Timestamp = Da.TimeStamp " +
                                  "WHERE EventType == \"Start Flap " +
                                  "Check\" AND Da." + rtrUpRes +
                                  " IS NOT NULL)")
                flapQuery = str("(SELECT CASE WHEN " +
                                "(SELECT * FROM " +
                                "(SELECT COUNT(*) As Count FROM " +
                                "(SELECT * FROM (SELECT * FROM " +
                                "(SELECT TimeStamp FROM " +
                                "Methodology_SamplingEvent " +
                                "WHERE EventType == \"Start Flap Check\") " +
                                "As sEvent JOIN (SELECT * FROM " +
                                "Methodology_SamplingData) As sData " +
                                "WHERE sData.Timestamp >= sEvent.Timestamp " +
                                "AND " + rtrUpRes + " IS NOT NULL " +
                                "AND sData.SubscriptionHandle == " +
                                "(SELECT Handle FROM " + resType +
                                " WHERE ParentHnd == " +
                                str(project.GetObjectHandle()) +
                                ") AND " + sessUpQuery + " == " +
                                str(proto_dict[proto_conf]) +
                                " ORDER BY sData.SubscriptionHandle) " +
                                "WHERE " + rtrUpRes +
                                " < " + str(proto_dict[proto_conf]) +
                                ")) As FlapCount " +
                                "WHERE FlapCount.Count > 0) > 0 " +
                                "THEN \"TRUE\" ELSE \"FALSE\" END AS " +
                                colName + ")")

                col_list.append(colName)
                type_list.append("VARCHAR")
                select_list.append(alias + "_FlapRes." + colName)
                from_list.append(flapQuery + " AS " + alias + "_FlapRes")

    # Add on the iteration information
    col_list.append("IteratorCommand_Iteration")
    col_list.append("IteratorCommand_IterState")
    col_list.append("IteratorCommand_CurrVal")
    type_list.append("INTEGER")
    type_list.append("VARCHAR")
    type_list.append("VARCHAR")

    # select_list.append("FlapRes.Bgp_FlapDetected")
    select_list.append("iter.Iteration")
    select_list.append("iter.IterState")
    select_list.append("iter.CurrVal")

    # from_list.append(flapQuery + " AS FlapRes")
    from_list.append(iter_table + " AS iter")

    # where_list.append("iter.Handle == " + str(iter_hnd))

    plLogger.LogDebug("col_list: " + str(col_list))
    plLogger.LogDebug("select_list: " + str(select_list))
    plLogger.LogDebug("from_list: " + str(from_list))
    plLogger.LogDebug("where_list: " + str(where_list))

    # Assemble the create string
    create = "CREATE TABLE Methodology_ProtocolFlapIterationData ("
    is_first = True
    for item in zip(col_list, type_list):
        col_item = item[0]
        type_item = item[1]
        if is_first:
            is_first = False
        else:
            create = create + ", "
        create = create + "\'" + col_item + "\' " + type_item
    create = create + ")"
    plLogger.LogDebug("Create Table: " + create)

    # Assemble the query string
    query = "SELECT "
    is_first = True
    for select_item in select_list:
        if is_first:
            is_first = False
            query = query + select_item
        else:
            query = query + ", " + select_item
    query = query + " FROM "
    is_first = True
    for from_item in from_list:
        if is_first:
            is_first = False
            query = query + from_item
        else:
            query = query + ", " + from_item
    plLogger.LogDebug("Sql Query: " + query)

    # Configure the target command
    plLogger.LogDebug("configuring command " + add_row_cmd.Get("Name"))
    add_row_cmd.Set("SqlQuery", query)
    add_row_cmd.Set("SqlCreateTable", create)


# This command sets up the queries, titles, and
# verdict explanations for the
# spirent.methodology.VerifyMultipleDbQueryCommand
# input_dict:
# {
#     "stmProtocolMixList": [
#         "LeftProtoMix",
#         "RightProtoMix"
#     ],
#     "cmdTag": "CommandTagName"
# }
def set_up_flap_verify_db_query_cmd(tagname, b, input_json):
    plLogger = PLLogger.GetLogger("Methodology")
    plLogger.LogDebug("Running custom set_up_flap_verify_db_query_cmd")

    err_str, input_dict = json_utils.load_json(input_json)

    if "cmdTag" not in input_dict.keys():
        plLogger.LogError("Expected cmdTag to be in the input.")
        return "Missing cmdTag in the input_dict"

    # Find the command object
    cmd_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["cmdTag"],
        class_name=PKG + ".VerifyMultipleDbQueryCommand")
    if len(cmd_list) < 1:
        plLogger.LogError("Could not find a tagged " + PKG +
                          ".VerifyMultipleDbQueryCommand")
        return "Could not find a tagged " + PKG + \
            ".VerifyMultipleDbQueryCommand in the sequence."

    plLogger.LogDebug("cmd_list: " + str(cmd_list))

    # Process the StmTemplateMix objects
    if "stmProtocolMixList" not in input_dict.keys():
        plLogger.LogError("Expected stmProtocolMixList to be in the " +
                          "input.")
        return "Missing stmProtocolMixList in input_dict"

    # Process the StmProtocolMix objects for the protocols and device counts
    plLogger.LogDebug("stmProtocolMixList from JSON: " +
                      str(input_dict["stmProtocolMixList"]))

    proto_mix_list = tag_utils.get_tagged_objects_from_string_names(
        input_dict["stmProtocolMixList"], class_name="StmProtocolMix")

    plLogger.LogDebug("proto_mix_list: " + str(proto_mix_list))
    if not len(proto_mix_list):
        plLogger.LogError("No StmProtocolMix objects found given tags: " +
                          str(input_dict["stmProtocolMixList"]))
        return "No StmProtocolMix objects found given tags: " + \
            str(input_dict["stmProtocolMixList"])

    proto_dict = get_proto_counts(proto_mix_list)
    plLogger.LogDebug("Protocol Counts (instances): " + str(proto_dict))

    query_list = []
    disp_name_list = []
    pass_exp_list = []
    fail_exp_list = []
    proto = 'BgpRouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        query_list.append(
            "SELECT Bgp_FlapDetected " +
            "FROM Methodology_ProtocolFlapIterationData " +
            "WHERE Bgp_FlapDetected == \"TRUE\"")
        disp_name_list.append("BGP Flap Detection")
        pass_exp_list.append("No BGP Flaps Detected.")
        fail_exp_list.append("BGP Flaps Detected.")
    proto = 'Ospfv2RouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        query_list.append(
            "SELECT Ospfv2_FlapDetected " +
            "FROM Methodology_ProtocolFlapIterationData " +
            "WHERE Ospfv2_FlapDetected == \"TRUE\"")
        disp_name_list.append("OSPFv2 Flap Detection")
        pass_exp_list.append("No OSPFv2 Flaps Detected.")
        fail_exp_list.append("OSPFv2 Flaps Detected.")
    proto = 'Ospfv3RouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        query_list.append(
            "SELECT Ospfv3_FlapDetected " +
            "FROM Methodology_ProtocolFlapIterationData " +
            "WHERE Ospfv3_FlapDetected == \"TRUE\"")
        disp_name_list.append("OSPFv3 Flap Detection")
        pass_exp_list.append("No OSPFv3 Flaps Detected.")
        fail_exp_list.append("OSPFv3 Flaps Detected.")
    proto = 'IsisRouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        query_list.append(
            "SELECT Isis_FlapDetected " +
            "FROM Methodology_ProtocolFlapIterationData " +
            "WHERE Isis_FlapDetected == \"TRUE\"")
        disp_name_list.append("ISIS Flap Detection")
        pass_exp_list.append("No ISIS Flaps Detected.")
        fail_exp_list.append("ISIS Flaps Detected.")
    proto = 'LdpRouterConfig'
    if proto in proto_dict and proto_dict[proto] > 0:
        query_list.append(
            "SELECT Ldp_FlapDetected " +
            "FROM Methodology_ProtocolFlapIterationData " +
            "WHERE Ldp_FlapDetected == \"TRUE\"")
        disp_name_list.append("LDP Flap Detection")
        pass_exp_list.append("No LDP Flaps Detected.")
        fail_exp_list.append("LDP Flaps Detected.")

    # Configure the target command(s)
    for cmd in cmd_list:
        plLogger.LogDebug("configuring command " + cmd.Get("Name"))
        plLogger.LogDebug("query_list: " + str(query_list))
        cmd.Set("UseSummary", True)
        cmd.SetCollection("SqlQueryList", query_list)
        cmd.SetCollection("DisplayNameList", disp_name_list)
        cmd.SetCollection("PassedVerdictExplanationList", pass_exp_list)
        cmd.SetCollection("FailedVerdictExplanationList", fail_exp_list)
        cmd.SetCollection("FailedVerdictExplanationList", fail_exp_list)


# FIXME: Pie notes
'''
'plotOptions': {
    'pie': {
        'allowPointSelect': True,
        'cursor': 'pointer',
        'size': '25%',
        'center': ['25%', '25%'],
        'dataLabels': {
            enabled: true,
            format: '<b>{point.name}</b>',
        }
    }
    series: [{
        'type': 'pie',
        'data': [['Label', value], ['Label', value]]
        }]
}
'''
