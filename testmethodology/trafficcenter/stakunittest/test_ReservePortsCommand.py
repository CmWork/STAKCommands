import copy
import json
import pytest
from mock import MagicMock, patch
from StcIntPythonPL import CStcSystem, CScriptableCreator, RelationType, CHandleRegistry
from spirent.methodology.trafficcenter.ReservePortsCommand import *
import spirent.methodology.trafficcenter.ReservePortsCommand

partial_topology_config = [
    {
        'name': 'West',
        'subnet_configs': [
            {
                'subnet': {
                    'name': 'name_1',
                    'id': '1234'
                },
                'ports': [{'location': '//10.1.1.1/1/1'}]
            },
            {
                'subnet': {
                    'name': 'name_2',
                    'id': '1235'
                },
                'ports': [{'location': '//10.1.1.2/1/1'}]
            },
        ]
    },
    {
        'name': 'East',
        'subnet_configs': [
            {
                'subnet': {
                    'name': 'name_3',
                    'id': '1236'
                },
                'ports': [{'location': '//10.1.1.3/1/1'}]
            },
            {
                'subnet': {
                    'name': 'name_4',
                    'id': '1237'
                },
                'ports': [{'location': '//10.1.1.4/1/1'}]
            },
        ]
    }
]


@pytest.fixture
def clean_up_ports(request, stc):
    def cleanup():
        project = CStcSystem.Instance().GetObject('project')
        ports = project.GetObjects('port')
        for port in ports:
            port.MarkDelete()
    request.addfinalizer(cleanup)
    cleanup()


def test_validate():
    assert validate(json.dumps(partial_topology_config)) == ''


def test_run(stc, clean_up_ports):
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = MagicMock()
    apply_mock = MagicMock()
    spirent.methodology.trafficcenter.ReservePortsCommand._apply = apply_mock
    patcher = patch('spirent.methodology.trafficcenter.ReservePortsCommand.get_sibling_ports',
                    new=MagicMock(return_value={}))
    patcher.start()

    assert run(json.dumps(partial_topology_config))
    project = CStcSystem.Instance().GetObject('project')
    ports = project.GetObjects('port')
    assert len(ports) == 4
    assert ports[0].Get('location') == '//10.1.1.1/1/1'
    assert ports[1].Get('location') == '//10.1.1.2/1/1'
    assert ports[2].Get('location') == '//10.1.1.3/1/1'
    assert ports[3].Get('location') == '//10.1.1.4/1/1'
    assert not apply_mock.called
    patcher.stop()


def test_empty_ports(stc, clean_up_ports):
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = MagicMock()
    config_with_no_ports = copy.deepcopy(partial_topology_config)
    config_with_no_ports[1]['subnet_configs'][1]['ports'] = []
    with pytest.raises(RuntimeError):
        with AutoCommand('spirent.methodology.trafficcenter.ReservePortsCommand') as cmd:
            cmd.Set('TopologyConfig', json.dumps(config_with_no_ports))
            cmd.Execute()
            assert cmd.Get('Status') == 'ports on subnet name_4 is empty'


def simulate_online(port_handles):
    ctor = CScriptableCreator()
    for handle in port_handles:
        port = CHandleRegistry.Instance().Find(handle)
        phy = ctor.Create('EthernetCopper', port)
        port.AddObject(phy, RelationType('ActivePhy'))


def test_change_speed(stc, clean_up_ports):
    attach_ports_mock = MagicMock(side_effect=simulate_online)
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = attach_ports_mock
    apply_mock = MagicMock()
    spirent.methodology.trafficcenter.ReservePortsCommand._apply = apply_mock
    patcher = patch('spirent.methodology.trafficcenter.ReservePortsCommand.get_sibling_ports',
                    new=MagicMock(return_value={}))
    patcher.start()

    supported_phys_mock = MagicMock(return_value=['ETHERNET_100_GIG_FIBER'])
    spirent.methodology.trafficcenter.ReservePortsCommand._get_supported_phys = supported_phys_mock

    config_with_speed = copy.deepcopy(partial_topology_config)
    config_with_speed[1]['subnet_configs'][1]['ports'][0]['speed'] = '100G'
    run(json.dumps(config_with_speed))
    project = CStcSystem.Instance().GetObject('project')
    ports = project.GetObjects('port')
    assert len(ports) == 4
    phys = [x.GetType() for x in ports[3].GetObjects('EthernetPhy')]
    assert phys[0] == 'ethernetcopper'
    assert phys[1] == 'ethernet100gigfiber'

    phy = ports[3].GetObject('EthernetPhy', RelationType('ActivePhy'))
    assert phy.Get('LineSpeed') == 'SPEED_100G'
    assert phy.GetType() == 'ethernet100gigfiber'
    assert apply_mock.called
    patcher.stop()


def test_no_change_speed_does_not_apply(stc, clean_up_ports):
    attach_ports_mock = MagicMock(side_effect=simulate_online)
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = attach_ports_mock
    apply_mock = MagicMock()
    spirent.methodology.trafficcenter.ReservePortsCommand._apply = apply_mock

    config_with_speed = copy.deepcopy(partial_topology_config)
    config_with_speed[1]['subnet_configs'][1]['ports'][0]['speed'] = '1G'
    run(json.dumps(config_with_speed))
    assert not apply_mock.called


def simulate_online_with_pos(port_handles):
    ctor = CScriptableCreator()
    for handle in port_handles:
        port = CHandleRegistry.Instance().Find(handle)
        phy = ctor.Create('POSPhy', port)
        port.AddObject(phy, RelationType('ActivePhy'))


def test_only_support_ethernet(stc, clean_up_ports):
    attach_ports_mock = MagicMock(side_effect=simulate_online_with_pos)
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = attach_ports_mock

    config_with_speed = copy.deepcopy(partial_topology_config)
    config_with_speed[1]['subnet_configs'][1]['ports'][0]['speed'] = '100G'
    assert not run(json.dumps(config_with_speed))


def setup_physical_test_module(stc_sys):
    ctor = CScriptableCreator()
    chassis_mgr = ctor.Create('PhysicalChassisManager', stc_sys)
    chassis = ctor.Create('PhysicalChassis', chassis_mgr)
    test_module = ctor.Create('PhysicalTestModule', chassis)
    test_module.Set('PortGroupSiblingCount', 4)
    physical_ports = []
    for i in range(1, 5):
        physical_port_group = ctor.Create('PhysicalPortGroup', test_module)
        physical_port_group.Set('Index', i)
        physical_port_group.Set('ReservedByUser', False)
        physical_port = ctor.Create('PhysicalPort', physical_port_group)
        location = "//10.100.1.1/1/%s" % i
        physical_port.Set('Location', location)
        physical_port_group.AddObject(physical_port, RelationType('ParentChild'))
        physical_ports.append(physical_port)
    return physical_ports


@pytest.fixture
def clean_up_physical_test_module(request, stc):
    def cleanup():
        chassis_manager = CStcSystem.Instance().GetObject('PhysicalChassisManager')
        chassis_manager.MarkDelete()
    request.addfinalizer(cleanup)
    cleanup()
    clean_up_ports(request, stc)


def test_get_sibling_ports(stc, clean_up_ports):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    physical_ports = setup_physical_test_module(stc_sys)
    port = ctor.Create("Port", project)
    physical_ports[0].AddObject(port, RelationType('PhysicalLogical'))
    physical_port_group = physical_ports[0].GetParent()
    physical_port_group.Set('ReservedByUser', True)
    port.Set('IsVirtual', False)
    ports = [port]
    sibling_ports = get_sibling_ports(ports)
    assert len(sibling_ports) == 1
    assert len(sibling_ports[port]) == 3
    i = 2
    for sibling_port in sibling_ports[port]:
        location = "//10.100.1.1/1/%s" % i
        i += 1
        assert sibling_port.Get('Location') == location


def test_change_speed_10M_100M(stc, clean_up_ports):
    attach_ports_mock = MagicMock(side_effect=simulate_online)
    spirent.methodology.trafficcenter.ReservePortsCommand.attach_ports = attach_ports_mock
    apply_mock = MagicMock()
    spirent.methodology.trafficcenter.ReservePortsCommand._apply = apply_mock
    patcher = patch('spirent.methodology.trafficcenter.ReservePortsCommand.get_sibling_ports',
                    new=MagicMock(return_value={}))
    patcher.start()

    config_with_speed = copy.deepcopy(partial_topology_config)
    config_with_speed[0]['subnet_configs'][0]['ports'][0]['speed'] = '10M'
    config_with_speed[0]['subnet_configs'][1]['ports'][0]['speed'] = '100M'
    run(json.dumps(config_with_speed))
    project = CStcSystem.Instance().GetObject('project')
    ports = project.GetObjects('port')
    assert len(ports) == 4
    phys_list = [x.GetObjects('EthernetPhy') for x in ports[0:2]]
    for phys in phys_list:
        assert len(phys) == 1
        assert phys[0].GetType() == 'ethernetcopper'
        assert not phys[0].Get('AutoNegotiation')

    assert apply_mock.called
    patcher.stop()


def test_reset():
    assert reset()
