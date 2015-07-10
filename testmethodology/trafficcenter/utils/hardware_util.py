from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import re


PORT_LOCATION_REGEX = r"//([\w.:_\-~]+)/([\w.:]+)/([\w.:]+)"

VIRTUAL_PART_NUMS = ["SPT-QEMU", "SPT-ANYWHERE", "SPT-VIRTUAL"]


def split_port_location(port_location):
    m = re.match(PORT_LOCATION_REGEX, port_location)
    if m is None:
        raise Exception("Invalid port_location: %s" % port_location)
    return m.groups()


def is_virtual(ip):
    stcSys = CStcSystem.Instance()
    hndReg = CHandleRegistry.Instance()
    chassis_man = stcSys.GetObject("PhysicalChassisManager")
    # make sure chassis is connected
    with AutoCommand("ConnectToChassisCommand") as conn_cmd:
        conn_cmd.SetCollection("AddrList", [ip])
        conn_cmd.Execute()
    with AutoCommand("GetObjectsCommand") as search_cmd:
        search_cmd.Set("ClassName", "PhysicalChassis")
        search_cmd.SetCollection("RootList", [chassis_man.GetObjectHandle()])
        search_cmd.Set("Condition", 'Hostname = %s' % ip)
        search_cmd.Execute()
    chassis = search_cmd.GetCollection("ObjectList")
    if chassis is None or len(chassis) == 0:
        raise Exception("error in is_virtual: No chassis found")
    chassis = hndReg.Find(chassis[0])
    if chassis is None:
        raise Exception("error in is_virtual: Chassis handle not found")
    part_num = chassis.Get("PartNum")
    return part_num in VIRTUAL_PART_NUMS
