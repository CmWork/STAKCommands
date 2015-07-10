from StcIntPythonPL import *
import json


def validate(TestConfig):
    return ''


def run(TestConfig):

    data = json.loads(TestConfig)
    plLogger = PLLogger.GetLogger("ReleasePortsCommand")
    topo_config = data["topology_nodes"]
    plLogger.LogInfo("ReleasePortsCommand: topology_nodes:" + str(data))
    is_port_list_empty = isPortListEmpty(topo_config)
    # release ports from CreateAndReserveVirtualPortsCommand
    if is_port_list_empty:
        ctor = CScriptableCreator()
        plLogger.LogInfo("---DetachAndStopVirtualPortsCommand")
        tear_down_cmd = ctor.CreateCommand("spirent.core.DetachAndStopVirtualPortsCommand")
        tear_down_cmd.Set("User", "meth2-Sherlock")
        tear_down_cmd.Execute()
        tear_down_cmd.MarkDelete()
    # no release ports from ports list, ports will be released when session deleted
    # else:
    #    plLogger.LogInfo("---DetachPortsCommand")
    #    releasePorts()
    return True


def reset():
    return True


def isPortListEmpty(config):
    topo_nodes = dumps(config)
    if len(topo_nodes) == 0:
        return True
    for topo_node in topo_nodes:
        subnet_item_list = dumps(topo_node["subnet_configs"])
        for subnet_item in subnet_item_list:
            if "ports" in subnet_item.keys():
                port_item_list = dumps(subnet_item["ports"])
                if len(port_item_list) == 0:
                    return True
            else:
                return True
    return False


def releasePorts():
    plLogger = PLLogger.GetLogger('releasePorts')
    plLogger.LogInfo("releasePorts")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()

    project = stc_sys.GetObject("Project")
    ports = project.GetObjects("Port")
    ctor = CScriptableCreator()
    port_list = []

    for port in ports:
        port_list.append(port.GetObjectHandle())
        sb_list = port.GetObjects("StreamBlock")
        plLogger.LogInfo("Port handle: sbs: " + str(len(sb_list)))
    plLogger.LogInfo("len of ports: " + str(len(ports)))

    detach_cmd = ctor.CreateCommand("DetachPortsCommand")
    detach_cmd.SetCollection("PortList", port_list)
    detach_cmd.Execute()
    detach_cmd.MarkDelete()
    plLogger.LogInfo("end of releasePorts")


# Convert unicode to string
def dumps(data):
    if type(data) == unicode:
        return str(data)
    if type(data) == list:
        return [dumps(item) for item in data]
    if type(data) == dict:
        ret = {}
        for key, value in data.iteritems():
            new_key = dumps(key)
            new_val = dumps(value)
            ret[new_key] = new_val
        return ret
    return data
