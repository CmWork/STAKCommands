from StcIntPythonPL import *
import utils.CommandUtils as CommandUtils
from spirent.core.utils.scriptable import AutoCommand
import utils.json_util as json_util


plLogger = PLLogger.GetLogger("CollectResultCommand")
hndReg = CHandleRegistry.Instance()


def _get_this_cmd():
    '''
    Get this Command instance from the
    HandleRegistry for setting output properties,
    status, progress, etc.
    '''
    try:
        thisCommand = hndReg.Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand


def handle_traffic_filter(result, traffic_filter, target_port):
    with AutoCommand("CreateDrvFromResultFilterCommand") as createDrvCmd:
        createDrvCmd.Set("CounterResultFilter", traffic_filter)
        createDrvCmd.SetCollection("RxPortHandleList", [target_port])
        createDrvCmd.Execute()
    drvHnd = createDrvCmd.Get("DynamicResultView")
    drv = hndReg.Find(drvHnd)
    prq = drv.GetObject("PresentationResultQuery")
    columns = prq.GetCollection("SelectProperties")
    with AutoCommand("subscribeDynamicResultView") as subscribeCmd:
        subscribeCmd.Set("DynamicResultView", drvHnd)
        subscribeCmd.Execute()
    rvds = prq.GetObjects("ResultViewData")

    rows = []
    for rvd in rvds:
        handle = str(rvd.GetObjectHandle())
        values = rvd.GetCollection("ResultData")
        rows.append({"handle": handle, "values": values})
    health_data = {}
    health_data["columns"] = columns
    health_data["data"] = rows
    result["health_drilldowns"].append(health_data)
    with AutoCommand("UnsubscribeDynamicResultView") as unsubscribeCmd:
        unsubscribeCmd.Set("DynamicResultView", drvHnd)
        unsubscribeCmd.Execute()
    drv.MarkDelete()


def handle_traffic_filters(result, traffic_filters, ports):
    for health_drilldown in zip(traffic_filters, ports):
        traffic_filter = health_drilldown[0]
        target_port = health_drilldown[1]
        if traffic_filter == 0:
            continue
        try:
            handle_traffic_filter(result, traffic_filter, target_port)
        except Exception as e:
            plLogger.LogError(
                "Cannot retrieve drill down data for" +
                "%s on port %s: %s" % (traffic_filter, target_port, e)
                )


def unsubscribe_drvs(drv_hnds):
    for drv_hnd in drv_hnds:
        with AutoCommand("UnsubscribeDynamicResultView") as unsubscribeCmd:
            unsubscribeCmd.Set("DynamicResultView", drv_hnd)
            unsubscribeCmd.Execute()


def handle_drv(result, drv, port):
    prq = drv.GetObject("PresentationResultQuery")
    columns = prq.GetCollection("SelectProperties")
    port_idx = None
    try:
        port_idx = columns.index("Port.Name")
    except:
        return
    rvds = prq.GetObjects("ResultViewData")
    rows = []
    for rvd in rvds:
        handle = str(rvd.GetObjectHandle())
        values = rvd.GetCollection("ResultData")
        port_name = values[port_idx]
        if port_name == port.Get("Name"):
            rows.append({"handle": handle, "values": values})
    health_data = {}
    health_data["columns"] = columns
    health_data["data"] = rows
    result["health_drilldowns"].append(health_data)


def handle_drvs(result, drvs, drv_ports):
    for health_drilldown in zip(drvs, drv_ports):
        drv_hnd = health_drilldown[0]
        port_hnd = health_drilldown[1]
        drv = hndReg.Find(drv_hnd)
        if drv is None:
            continue
        port = hndReg.Find(port_hnd)
        try:
            handle_drv(result, drv, port)
        except Exception as e:
            plLogger.LogError(
                "Cannot retrieve drill down data for drv " +
                "%s on port %s: %s" % (drv_hnd, port_hnd, e)
                )
    # remove repeated drvs
    drvs_to_unsubscribe = list(set(drvs))
    unsubscribe_drvs(drvs_to_unsubscribe)


def validate(TrafficFilters, Ports, Drvs, DrvPorts):
    if len(TrafficFilters) != len(Ports):
        return "TrafficFilters and Ports have different sizes"
    return ""


def run(TrafficFilters, Ports, Drvs, DrvPorts):
    result = {"health_drilldowns": []}

    handle_traffic_filters(result, TrafficFilters, Ports)

    handle_drvs(result, Drvs, DrvPorts)

    CommandUtils.set_attribute("Result",
                               json_util.dumps(result),
                               _get_this_cmd())
    return True


def reset():
    return True
