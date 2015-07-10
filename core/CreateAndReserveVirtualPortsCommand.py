"""
Create STCv ports in QManager and create and reserve associated STC Ports.

"""
import xmlrpclib
import traceback
import time

from StcIntPythonPL import (
    PLLogger, CStcSystem, CScriptableCreator, CHandleRegistry, CTaskManager)
from spirent.core.utils.scriptable import AutoCommand

CMD_NAME = 'spirent.core.CreateAndReserveVirtualPortsCommand'


def validate(User, PortCount, VmImage, TtlMinutes, Description, UseSocket,
             VmMem, Cores, LicenseServer, QmServer):
    """Validate the input parameters for this STAK command.

    Arguments:
    See file: stc_trafficcenter.xml

    Return:
    Empty string if OK, error message string if error with input.

    """
    try:
        qm = xmlrpclib.ServerProxy(QmServer)
        qm.get_server_time()
    except Exception:
        return 'error: cannot contact qmanager server: ' + QmServer

    return ''


def run(User, PortCount, VmImage, TtlMinutes, Description, UseSocket, VmMem,
        Cores, LicenseServer, QmServer):
    """Run the CreateAndReserveVirtualPortsCommand STAK command.

    Arguments:
    See file: stc_trafficcenter.xml

    """
    logger = get_logger()
    try:
        # Setting up progress bar
        cmd = _get_this_cmd()
        cmd.Set('ProgressStepsCount', 3)
        cmd.Set('ProgressCurrentStep', 1)
        cmd.Set('ProgressCurrentStepName', "Starting STCv instances")
        cmd.Set('ProgressMaxValue', 4)
        cmd.Set('ProgressIsCancellable', True)
        ctm = CTaskManager.Instance()

        logger.LogInfo('starting %s stcv instances using %s'
                       % (PortCount, VmImage))

        cmd.Set('ProgressCurrentValue', 1)
        ctm.CtmYield(50)

        # Start all the VM instances.
        vm_ids = start_vms(
            User, int(PortCount), VmImage, TtlMinutes, Description,
            bool(UseSocket), VmMem, Cores, LicenseServer, QmServer)

        cmd.Set('ProgressCurrentValue', 4)
        logger.LogInfo('started vms: ' + ', '.join(vm_ids))

        ctm.CtmYield(50)
        if cmd.Get('ProgressCancelled'):
            raise RuntimeError('command canceled')

        try:
            # Get the IP address of each VM.
            vm_addr_map = get_vm_ips(vm_ids, QmServer)

            # Create and attach a STC Port for each VM.
            vm_port_map = create_ports(vm_addr_map)

        except Exception:
            # Stop VMs if failed to get IPs or create Ports.
            stop_vms(vm_ids, User, QmServer)
            raise

        try:
            # Set output.
            hnds = []
            locs = []
            vms = []
            for vm_id, (hnd, loc) in vm_port_map.iteritems():
                hnds.append(hnd)
                locs.append(loc)
                vms.append(vm_id)

            cmd.SetCollection('Ports', hnds)
            cmd.SetCollection('PortLocations', locs)
            cmd.SetCollection('VmList', vms)
        except Exception:
            destroy_ports([h for h, l in vm_port_map.itervalues()])
            stop_vms(vm_ids, User, QmServer)
            raise

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


def start_vms(vm_owner, port_count, vm_image, ttl_minutes, description,
              use_socket, vm_mem, cores, license_server, qmserver):
    """Start all requested STCv instances.

    Arguments:
    vm_owner       -- User creating VMs.
    port_count     -- STCv instances to create.
    vm_image       -- VM image or build number to use.  If not defined, use
                      latest available build on build server.
    ttl_minutes    -- Number of minutes for VM to live.  If not defined, use
                      QManager default.
    description    -- Description to apply to VM instances.
    use_socket     -- Connect VMs with socket.  Default is False.
    vm_mem         -- MB of RAM to use for each VM.  If not defined, use
                      QManager default for STCv.
    cores          -- Number of logical CPUs per VM.  If not defined, use
                      QManager default for STCv.
    license_server -- Alternate license server IP or DNS name.  If not defined,
                      use QManager default.
    qmserver       -- QManager server.

    Return:
    List of vm_id values.

    """
    if port_count < 1:
        raise RuntimeError('port count must be greater than 0')

    qm = xmlrpclib.ServerProxy(qmserver, allow_none=True)

    if not vm_image:
        builds = qm.get_available_stc_builds()
        if not builds:
            raise RuntimeError('no stcv builds available on qmanager')

        bll_version = CStcSystem.Instance().Get('version')
        # Only look at the first three numbers in the version.
        bll_version = '.'.join(bll_version.split('.')[:3])
        if bll_version in builds:
            # Use IL image that matches BLL version.
            vm_image = '#' + bll_version
        else:
            # Matchin IL image not available, so use latest.
            builds.sort()
            vm_image = '#' + builds[-1]
    else:
        if vm_image[0] == '#':
            # Check that the requested build is available.
            builds = qm.get_available_stc_builds()
            if vm_image[1:] not in builds:
                raise RuntimeError('build not found on qmanager: ' + vm_image)
        else:
            # Check that the requested image files is available.
            files = qm.list_files(vm_owner)
            if vm_image not in files:
                raise RuntimeError('file not found on qmanager: ' + vm_image)

    # Tell QManager to start the VM instances.
    vm_ids = qm.start_stc_vm(
        vm_owner, vm_image, ttl_minutes, use_socket, description, port_count,
        None, True, None, vm_mem, cores, False, license_server)

    return vm_ids


def get_vm_ips(vm_ids, qmserver):
    """Get IP address for each VM.

    Arguments:
    vm_ids -- List of VM ID values.

    Return:
    dict of {vm_id: ip_addr, ..}

    """
    # Going to next step of getting VM IP addrs.
    cmd = _get_this_cmd()
    cmd.Set('ProgressCurrentStep', 2)
    cmd.Set('ProgressCurrentStepName', 'Getting VM IPs')
    cmd.Set('ProgressMaxValue', 60)
    ctm = CTaskManager.Instance()

    vm_addr_map = {}

    # Wait 45 seconds before getting IP addresses.
    for pgs in xrange(1, 41):
        ctm.CtmYield(1000)

        # Update progress.
        cmd.Set('ProgressCurrentValue', pgs)

        if cmd.Get('ProgressCancelled'):
            raise RuntimeError('command canceled')

    incr = int(20 / len(vm_ids))

    qm = xmlrpclib.ServerProxy(qmserver, allow_none=True)
    retry = 24
    while retry and len(vm_addr_map) < len(vm_ids):
        for vm_id in vm_ids:
            if vm_id not in vm_addr_map:
                vm_ip = qm.get_vm_ip(vm_id)
                if vm_ip == 'unknown':
                    # Still waiting for IP.
                    time.sleep(5)
                    retry -= 1
                    break
                if vm_ip.count('.') != 3:
                    # Failure getting IP.  Exit with error.
                    retry = 0
                    break
                vm_addr_map[vm_id] = vm_ip
                # Update progress
                pgs += incr
                cmd.Set('ProgressCurrentValue', pgs)
                ctm.CtmYield(50)

    if not retry:
        raise RuntimeError('could not get IP for all STCv instances')

    # Show progress complete.
    if pgs < 60:
        cmd.Set('ProgressCurrentValue', 60)
        ctm.CtmYield(50)

    return vm_addr_map


def create_ports(vm_addr_map):
    """Create and attach ports for all STCv instances.

    Return:
    dict of {vm_id: port_handle, ..}

    """
    # Going to next step of creating and attaching ports.
    cmd = _get_this_cmd()
    cmd.Set('ProgressCurrentStep', 3)
    cmd.Set('ProgressCurrentStepName', "Attaching Ports")
    cmd.Set('ProgressMaxValue', len(vm_addr_map) + 1)
    ctm = CTaskManager.Instance()
    pgs = 1
    ctm.CtmYield(50)

    vm_port_map = {}
    logger = get_logger()
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('Project')
    try:
        for vm_id, vm_addr in vm_addr_map.iteritems():
            port = ctor.Create('Port', project)
            port.Set('IsVirtual', True)
            port.Set('PortName', vm_id)
            port_handle = port.GetObjectHandle()
            loc = '//%s/1/1' % (vm_addr)
            port.Set('Location', loc)
            vm_port_map[vm_id] = (port_handle, loc)
            logger.LogInfo('Created Port at location: %s' % (loc,))

            # Update progress.
            cmd.Set('ProgressCurrentValue', pgs)
            pgs += 1

            ctm.CtmYield(50)
            if cmd.Get('ProgressCancelled'):
                raise RuntimeError('command canceled')

        with AutoCommand("AttachPortsCommand") as attach_cmd:
            hnd_list = [h for h, l in vm_port_map.itervalues()]
            attach_cmd.SetCollection("PortList", hnd_list)
            attach_cmd.Set("AutoConnect", True)
            attach_cmd.Set("ContinueOnFailure", False)
            attach_cmd.Execute()

        # Update progress.
        cmd.Set('ProgressCurrentValue', pgs)
        ctm.CtmYield(50)
    except Exception:
        destroy_ports([h for h, l in vm_port_map.itervalues()])
        raise

    logger.LogInfo('Attached all ports')
    return vm_port_map


def destroy_ports(vm_port_handles):
    """Detach and delete all Port objects.

    """
    logger = get_logger()

    # Detach specified ports
    with AutoCommand("DetachPortsCommand") as detach_cmd:
        detach_cmd.SetCollection("PortList", vm_port_handles)
        detach_cmd.Execute()
    logger.LogInfo('Detached all ports')

    # Delete specified ports.
    project = CStcSystem.Instance().GetObject('project')
    for port in project.GetObjects('Port'):
        if port.GetObjectHandle() in vm_port_handles:
            port.MarkDelete()


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
