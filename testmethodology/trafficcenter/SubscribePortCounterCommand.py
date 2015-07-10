from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import json
import ast


def get_this_cmd():
    '''
    Get this Command instance from the
    HandleRegistry for setting output properties,
    status, progress, etc.
    '''
    hndReg = CHandleRegistry.Instance()
    try:
        thisCommand = hndReg.Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand


def validate(Config):
    data = json.loads(Config)
    if "callback_info" not in data:
        return "Missing callback_info"

    if "counters" not in data:
        return "Missing counters config"

    return ''


def run(Config):
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")

    data = json.loads(Config)
    cb = data["callback_info"]
    url = cb["url"]
    context = cb["context"]
    counters = data["counters"]

    with AutoCommand("ResultsSubscribeCommand") as sub_ana_cmd:
        sub_ana_cmd.Set("parent", project.GetObjectHandle())
        sub_ana_cmd.Set("configType", "analyzer")
        sub_ana_cmd.Set("resultType", "analyzerPortResults")
        sub_ana_cmd.Execute()

    with AutoCommand("ResultsSubscribeCommand") as sub_gen_cmd:
        sub_gen_cmd.Set("parent", project.GetObjectHandle())
        sub_gen_cmd.Set("configType", "generator")
        sub_gen_cmd.Set("resultType", "generatorPortResults")
        sub_gen_cmd.Execute()

    subscribe_result_change(counters, url, context)

    ports = project.GetObjects("Port")
    result = []
    port_location = []

    for port in ports:
        analyzer = port.GetObject("Analyzer")
        generator = port.GetObject("Generator")

        anaResult = analyzer.GetObject("analyzerPortResults")
        genResult = generator.GetObject("generatorPortResults")
        if anaResult is None or genResult is None:
            continue

        result.append(anaResult.GetObjectHandle())
        result.append(genResult.GetObjectHandle())
        port_location.append(port.Get("Location"))

    # the output is used for web level mapping.
    # one port location will map to two result handles:
    # one for analyzer port reuslt and one for generator port result
    get_this_cmd().SetCollection("PortResults", result)
    get_this_cmd().SetCollection("PortLocations", port_location)

    return True


def reset():
    return True


def subscribe_result_change(counters, url, context):
    tx_counters = counters["tx"]
    sub_list = []
    for tx_counter in tx_counters:
        sub_list.append(''.join(["generatorPortResults.", dumps(tx_counter)]))

    subscribe_property_change("generatorPortResults", sub_list, url, context)

    rx_counters = counters["rx"]
    sub_list = []
    for rx_counter in rx_counters:
        sub_list.append(''.join(["analyzerPortResults.", dumps(rx_counter)]))

    subscribe_property_change("analyzerPortResults", sub_list, url, context)


def dumps(data):
    return ast.literal_eval(json.dumps(data))


def subscribe_property_change(classId, propertyList, url, context):
    with AutoCommand("SubscribePropertyChangeCommand") as sub_cmd:
        sub_cmd.Set("PropertyClassId", classId)
        sub_cmd.SetCollection("PropertyIdList", propertyList)
        sub_cmd.Set("PublishUrl", dumps(url))
        sub_cmd.Set("Context", dumps(context))
        sub_cmd.Set("IncludeResultParent", True)
        sub_cmd.Execute()
