"""
Detach Ports from test session and stop the associated STCv ports in QManager.

"""
import xmlrpclib
import traceback

from StcIntPythonPL import (PLLogger, CStcSystem, CHandleRegistry)
from spirent.core.utils.scriptable import AutoCommand

CMD_NAME = 'spirent.core.DetachAndStopVirtualPortsCommand'


def validate(User, QmServer):
    return ''


def run(User, QmServer):
    try:
        vm_ids = destroy_ports()
        stop_vms(vm_ids, User, QmServer)
    except RuntimeError as e:
        get_logger().LogError('error: ' + str(e))
        return False
    except Exception:
        get_logger().LogError('error: unhandled exception:\n' +
                              traceback.format_exc())
        return False

    return True


def reset():
    """True means this command can be reset and re-run."""
    return True


def destroy_ports():
    """Detach and delete all Port objects.

    """
    logger = get_logger()

    # Get all ports and handles.
    ports = []
    handles = []
    vm_ids = []
    project = CStcSystem.Instance().GetObject('project')
    for port in project.GetObjects('Port'):
        # Get the VM ID from the PortName.
        vm_id = port.Get('PortName').split()[0]
        if vm_id and len(vm_id) == 25 and vm_id.count('-') == 3:
            # Looks like this port has a VM ID, so delete it.
            logger.LogInfo('detaching port: ' + port.Get('Location'))
            vm_ids.append(vm_id)
            ports.append(port)
            handles.append(port.GetObjectHandle())

    # Detach all ports.
    with AutoCommand("DetachPortsCommand") as detach_cmd:
        detach_cmd.SetCollection("PortList", handles)
        detach_cmd.Execute()

    logger.LogInfo('deleting %d ports' % (len(ports),))

    # Delete all ports.
    for port in ports:
        port.MarkDelete()

    return vm_ids


def stop_vms(vm_ids, vm_owner, qmserver):
    """Stop specified VM instances.

    Arguments:
    vm_ids   -- List of VM ID values.
    vm_owner -- Owner of VMs.

    """
    logger = get_logger()
    qm = xmlrpclib.ServerProxy(qmserver, allow_none=True)
    for vm_id in vm_ids:
        try:
            qm.stop_vm(vm_owner, vm_id)
            logger.LogInfo('stopped vm: ' + vm_id)
        except Exception as e:
            logger.LogError('error stopping stcv: ' + str(e))


def get_logger():
    """Get the virtual ports logger."""
    return PLLogger.GetLogger(CMD_NAME)


def _get_this_cmd():
    """Get Command instance of this command.

    Get this Command instance from the HandleRegistry for setting output
    properties, status, progress, etc.

    """
    hndReg = CHandleRegistry.Instance()
    try:
        thisCommand = hndReg.Find(__commandHandle__)
    except NameError:
        return None
    return thisCommand
