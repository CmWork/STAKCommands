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
        <MacAddrRepeatCount>0</MacAddrRepeatCount>
        <MacAddrRecycleCount>0</MacAddrRecycleCount>
        <MacAddrPortStep>00:00:00:00:10:00</MacAddrPortStep>
        </EthernetII>
        <Ipv4><Ipv4Addr>10.14.16.2</Ipv4Addr>
        <Ipv4AddrStep>0.0.0.1</Ipv4AddrStep>
        <Ipv4AddrRepeatCount>0</Ipv4AddrRepeatCount>
        <Ipv4AddrRecycleCount>0</Ipv4AddrRecycleCount>
        <Ipv4AddrPortStep>0.0.1.0</Ipv4AddrPortStep>
        <Ipv4GatewayAddr>10.14.16.1</Ipv4GatewayAddr>
        <Ipv4GatewayAddrStep>0.0.0.0</Ipv4GatewayAddrStep>
        <Ipv4GatewayAddrRepeatCount>0</Ipv4GatewayAddrRepeatCount>
        <Ipv4GatewayAddrRecycleCount>0</Ipv4GatewayAddrRecycleCount>
        <Ipv4GatewayAddrPortStep>0.0.1.0</Ipv4GatewayAddrPortStep>
        </Ipv4>
        </Interfaces>
        <Protocols>
        <Bfd>
        <TxInterval>1000</TxInterval><RxInterval>1000</RxInterval>
        </Bfd>
        <Dhcpv4Client>
        <HostName>client_@p-@b-@s</HostName>
        <EnableArpServerId>false</EnableArpServerId>
        <EnableAutoRetry>true</EnableAutoRetry>
        <EnableRouterOption>false</EnableRouterOption>
        <RetryAttempts>10</RetryAttempts>
        <EnableBroadcastFlag>true</EnableBroadcastFlag>
        </Dhcpv4Client>
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
        dhcp = device.GetObject('Dhcpv4BlockConfig')
        if dhcp is not None:
            cfg_list.append(dhcp)

    assert 2 == len(cfg_list)

    val_cmd = ctor.CreateCommand('spirent.methodology.ValidateDhcpv4BindCommand')
    val_cmd.SetCollection('ObjectList', [project.GetObjectHandle()])
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Create a results object on one of the objects, verify current bound
    result = ctor.Create('Dhcpv4BlockResults', cfg_list[0])
    result.Set('CurrentBoundCount', 0)

    val_cmd.Reset()
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Only 1 bound the other is still not bound
    val_cmd.Reset()
    result.Set('CurrentBoundCount', 1)
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Both bound
    result1 = ctor.Create('Dhcpv4BlockResults', cfg_list[1])
    result1.Set('CurrentBoundCount', 1)
    val_cmd.Reset()
    val_cmd.Execute()
    assert True == val_cmd.Get('Verdict')
