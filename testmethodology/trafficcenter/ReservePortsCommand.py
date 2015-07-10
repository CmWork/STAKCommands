import traceback
from StcIntPythonPL import CScriptableCreator, RelationType, CHandleRegistry, CStcSystem, PLLogger
from spirent.core.utils.scriptable import AutoCommand
import json


def validate(TopologyConfig):
    return ''


def run(TopologyConfig):
    logger = _get_logger()
    cmd = _get_this_cmd()
    if cmd:
        cmd.Set('ErrorOnFailure', True)

    try:
        setup_ports(TopologyConfig)
    except RuntimeError as e:
        logger.LogError(str(e))
        if cmd:
            cmd.Set("Status", str(e))
        return False
    except:
        logger.LogError("unhandled exception:" + traceback.format_exc())
        return False
    return True


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


def reset():
    return True


def attach_ports(port_hnd_list):
    with AutoCommand("AttachPortsCommand") as attach_cmd:
        attach_cmd.SetCollection("PortList", port_hnd_list)
        attach_cmd.Set("AutoConnect", True)
        attach_cmd.Set("ContinueOnFailure", True)
        attach_cmd.Execute()


def setup_ports(config):
    logger = _get_logger()
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    tags = project.GetObject("Tags")

    attach_list = []
    topo_nodes = json.loads(config)
    logger.LogInfo("topo len: " + str(len(topo_nodes)))
    speeds = {}
    for topo_node in topo_nodes:
        # This is the tag name
        name = dumps(topo_node["name"])

        tag = ctor.Create("Tag", tags)
        tag.Set("Name", name)
        tags.AddObject(tag, RelationType("UserTag"))
        subnet_item_list = dumps(topo_node["subnet_configs"])
        for subnet_item in subnet_item_list:
            subnet_name = dumps(subnet_item["subnet"]["name"])
            subnet_id = dumps(subnet_item["subnet"]["id"])
            topo_subnet_name = name + "_" + subnet_name + "_" + subnet_id
            topo_subnet_tag = ctor.Create("Tag", tags)
            topo_subnet_tag.Set("Name", topo_subnet_name)
            tags.AddObject(topo_subnet_tag, RelationType("UserTag"))

            port_item_list = dumps(subnet_item["ports"])
            if len(port_item_list) == 0:
                msg = "ports on subnet %s is empty" % subnet_name
                logger.LogError(msg)
                raise RuntimeError(msg)

            for port_item in port_item_list:
                location = dumps(port_item["location"])
                port = ctor.Create("Port", project)
                port.Set("Location", location)
                port.Set("Name", name)
                logger.LogInfo("setup_ports: Location: " + location)
                attach_list.append(port.GetObjectHandle())
                speed = (dumps(port_item["speed"]) if "speed" in port_item else "")
                speeds[port] = speed
                port.AddObject(tag, RelationType("UserTag"))
                port.AddObject(topo_subnet_tag, RelationType("UserTag"))
    attach_ports(attach_list)
    sibling_ports = get_sibling_ports(speeds.keys())
    _attach_sibling_ports(sibling_ports)
    speeds = _add_sibling_ports_speed_info(speeds, sibling_ports)
    set_speeds(speeds)
    _release_sibling_ports(sibling_ports)


def _get_supported_phys(port):
    return port.Get("SupportedPhys").split("|")


def _set_active_phy(port, active_phy, speed):
    # Eventually we would pass in the phy type as well, but
    # that's a different US. For now, try to figure it out
    # from the speed and what LAN phy types are supported.
    logger = _get_logger()
    type = active_phy.GetType()
    if speed in ["10G", "100G", "40G"] and type.find(speed) == -1:
        supported_phys = _get_supported_phys(port)
        search_str = speed.replace("G", "_GIG")
        new_phy_type = [phy for phy in supported_phys if phy.find(search_str) != -1]
        if not new_phy_type:
            raise RuntimeError("Unsupported speed %s. "
                               "Supported physical interfaces are: %s" % (speed, supported_phys))
        new_phy_type = new_phy_type[0].replace("_", "").lower()
        # Grab one if it already exists.
        phy = port.GetObject(new_phy_type)
        if phy is None:
            ctor = CScriptableCreator()
            phy = ctor.Create(new_phy_type, port)
        logger.LogInfo("Switching physical interface on port %s to %s" %
                       (port.Get("Location"), phy.GetType()))
        port.RemoveObject(active_phy, RelationType("ActivePhy"))
        port.AddObject(phy, RelationType("ActivePhy"))


def _set_speed(phy, speed_val):
    logger = _get_logger()
    logger.LogInfo("Current line speed is %s. Setting to %s." %
                   (phy.Get("LineSpeedStatus"), speed_val))
    phy.Set("LineSpeed", speed_val)
    if speed_val in ['SPEED_10M', 'SPEED_100M']:
        phy.Set('AutoNegotiation', False)


def _apply():
    with AutoCommand("ApplyToILCommand") as apply_cmd:
        apply_cmd.Execute()


def set_speeds(speeds):
    logger = _get_logger()
    requires_apply = False
    for port, speed in speeds.iteritems():
        if speed == '':
            continue
        speed_val = "SPEED_" + speed
        phy = port.GetObject("EthernetPhy", RelationType("ActivePhy"))
        if phy is None:
            raise RuntimeError("Cannot change speed. Only ethernet is currently supported.")
        if phy.Get("LineSpeedStatus") != speed_val:
            _set_active_phy(port, phy, speed)
            _set_speed(phy, speed_val)
            requires_apply = True
        else:
            logger.LogInfo("Port %s line speed is already set to %s. Nothing to do." %
                           (port.Get("Location"), speed_val))

    if requires_apply:
        _apply()
        logger = _get_logger()
        for port in speeds:
            phy = port.GetObject("EthernetPhy", RelationType("ActivePhy"))
            logger.LogInfo("Port %s LineSpeedStatus is now %s." %
                           (port.Get("Location"), phy.Get("LineSpeedStatus")))


def _create_logical_ports(physical_ports):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    for physical_port in physical_ports:
        location = physical_port.Get("Location")
        if location is None:
            raise RuntimeError("Unable to get port location.")
        port = ctor.Create("Port", project)
        port.Set("Location", location)
        yield port


def _get_sibling_ports_for_port_groups(sibling_pg_count, test_module, port_group):
    index = port_group.Get("Index")
    base_pg_index = (index - 1)/sibling_pg_count*sibling_pg_count + 1
    last_pg_index = base_pg_index + sibling_pg_count
    port_groups = test_module.GetObjects("PhysicalPortGroup", RelationType("ParentChild"))
    for pg in port_groups:
        pg_index = pg.Get("Index")
        if pg_index >= base_pg_index and pg_index < last_pg_index and pg_index != index and \
           not pg.Get("ReservedByUser"):
            physical_ports = pg.GetObjects("PhysicalPort", RelationType("ParentChild"))
            if physical_ports is None:
                raise RuntimeError("Unable to get ports.")
            for port in _create_logical_ports(physical_ports):
                yield port


def _get_sibling_ports_for_ports(ports):
    for port in ports:
        if port.Get("IsVirtual"):
            continue
        physical_port = port.GetObject("PhysicalPort",
                                       RelationType.ReverseDir("PhysicalLogical"))
        if physical_port is None:
            raise RuntimeError("Unable to get physical port.")
        physical_port_group = physical_port.GetParent()
        if physical_port_group is None:
            raise RuntimeError("Unable to get port group.")
        test_module = physical_port_group.GetParent()
        if test_module is None:
            raise RuntimeError("Unable to get test module.")
        sibling_pg_count = test_module.Get("PortGroupSiblingCount")
        if sibling_pg_count <= 1:
            continue
        yield port, list(_get_sibling_ports_for_port_groups(sibling_pg_count, test_module,
                                                            physical_port_group))


def get_sibling_ports(ports):
    sibling_ports = {}
    for port, port_list in _get_sibling_ports_for_ports(ports):
        if len(port_list):
            sibling_ports[port] = port_list
    return sibling_ports


def _add_sibling_ports_speed_info(speeds, sibling_ports):
    for port, siblings in sibling_ports.iteritems():
        if port in speeds:
            speed = speeds[port]
            if speed != "":
                for sibling in siblings:
                    speeds[sibling] = speed
    return speeds


def _attach_sibling_ports(sibling_ports):
    attach_list = []
    for siblings in sibling_ports.values():
        for sibling in siblings:
            attach_list.append(sibling.GetObjectHandle())
    attach_ports(attach_list)


def _release_sibling_ports(sibling_ports):
    release_list = []
    for siblings in sibling_ports.itervalues():
        for sibling in siblings:
            release_list.append(sibling.GetObjectHandle())

    if len(release_list):
        with AutoCommand("DetachPortsCommand") as detach_cmd:
            detach_cmd.SetCollection("PortList", release_list)
            detach_cmd.Execute()

        for siblings in sibling_ports.itervalues():
            for sibling in siblings:
                sibling.MarkDelete()


def _get_logger():
    return PLLogger.GetLogger("spirent.methodology.trafficcenter.ReservePortsCommand")


def _get_this_cmd():
    try:
        this_command = CHandleRegistry.Instance().Find(__commandHandle__)
    except NameError:
        return None
    return this_command
