from StcIntPythonPL import *


def d_test_multi_run(stc):
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    port = ctor.Create('Port', project)
    net_prof = ctor.Create('NetworkProfile', project)
    # Tack on BFD to prevent making just one device
    net_info = \
        '''
        <NetworkInfo><DeviceCount>2</DeviceCount>
        <RouterId>192.0.0.1</RouterId>
        <RouterIdStep>0.0.0.1</RouterIdStep>
        <RouterIdPortStep>0.1.0.0</RouterIdPortStep>
        <Interfaces>
        <EthernetII><MacAddr>00:01:94:00:00:01</MacAddr>
        <MacAddrStep>00:00:00:00:00:01:</MacAddrStep>
        <MacAddrPortStep>00:00:00:00:10:00</MacAddrPortStep>
        </EthernetII>
        <Ipv6><Ipv6Addr>2000::2</Ipv6Addr>
        <Ipv6AddrStep>::1</Ipv6AddrStep>
        <Ipv6AddrPortStep>0:0:1::</Ipv6AddrPortStep>
        <Ipv6GatewayAddr>2001::1</Ipv6GatewayAddr>
        <Ipv6LinkLocalAddr>fe80::1</Ipv6LinkLocalAddr>
        <Ipv6GatewayAddrStep>::</Ipv6GatewayAddrStep>
        <Ipv6GatewayAddrPortStep>0:0:0:1::</Ipv6GatewayAddrPortStep>
        </Ipv6>
        </Interfaces>
        <Protocols>
        <Bfd>
        <TxInterval>1000</TxInterval><RxInterval>1000</RxInterval>
        </Bfd>
        <Dhcpv6Client>
        <Dhcpv6ClientMode>DHCPV6</Dhcpv6ClientMode>
        </Dhcpv6Client>
        </Protocols>
        </NetworkInfo>
        '''
    net_prof.Set('NetworkInfo', net_info)
    net_prof.AddObject(port, RelationType('AttachedPort'))

    expand_cmd = ctor.CreateCommand('spirent.methodology.ExpandNetworkProfileCommand')
    expand_cmd.Set('NetworkProfile', int(net_prof.GetObjectHandle()))
    expand_cmd.Execute()

    assert 'PASSED' == expand_cmd.Get('PassFailState')
    device_list = net_prof.GetObjects('EmulatedDevice',
                                      RelationType('GeneratedObject'))
    assert 2 == len(device_list)

    cfg_list = []
    for device in device_list:
        dhcp = device.GetObject('Dhcpv6BaseBlockConfig')
        if dhcp is not None:
            cfg_list.append(dhcp)

    assert 2 == len(cfg_list)

    val_cmd = ctor.CreateCommand('spirent.methodology.ValidateDhcpv6BoundCommand')
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Only 1 forced bound the other is still not bound
    val_cmd.Reset()
    cfg_list[0].Set('BlockState', 'BOUND')
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    val_cmd.Reset()
    cfg_list[0].Set('BlockState', 'IDLE')
    cfg_list[1].Set('BlockState', 'BOUND')
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Create a results object on one of the objects, verify current bound
    result = ctor.Create('Dhcpv6BlockResults', cfg_list[0])
    result.Set('CurrentBoundCount', 0)

    val_cmd.Reset()
    cfg_list[0].Set('BlockState', 'BOUND')
    cfg_list[1].Set('BlockState', 'BOUND')
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    val_cmd.Reset()
    result.Set('CurrentBoundCount', 1)
    cfg_list[0].Set('BlockState', 'BOUND')
    cfg_list[1].Set('BlockState', 'BOUND')
    val_cmd.Execute()
    assert True == val_cmd.Get('Verdict')
