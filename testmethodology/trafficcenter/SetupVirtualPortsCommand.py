from StcIntPythonPL import *


def validate():
    return ''


def run():
    # for CreateAndReserveVirtualPortsCommand and
    # DetachAndStopVirtualPortsCommand
    tempSetupPorts()
    return True


def reset():
    return True


def tempSetupPorts():
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()

    project = stc_sys.GetObject("Project")
    tags = project.GetObject("Tags")
    port_list = project.GetObjects("Port")

    # for CreateAndReserveVirtualPortsCommand and
    # DetachAndStopVirtualPortsCommand
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "West")
    tags.AddObject(tag, RelationType("UserTag"))
    west_port = port_list[0]
    vm_id = west_port.Get('PortName').split()[0]
    vm_id = vm_id + " West"
    west_port.Set("Name", vm_id)
    west_port.AddObject(tag, RelationType("UserTag"))

    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "East")
    tags.AddObject(tag, RelationType("UserTag"))
    east_port = port_list[1]
    vm_id = east_port.Get('PortName').split()[0]
    vm_id = vm_id + " East"
    east_port.Set("Name", vm_id)
    east_port.AddObject(tag, RelationType("UserTag"))
