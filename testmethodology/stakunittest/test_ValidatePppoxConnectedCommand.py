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
        <Interfaces><EthernetII>
        <MacAddr>00:01:94:00:00:01</MacAddr>
        <MacAddrStep>00:00:00:00:00:01</MacAddrStep>
        <MacAddrRepeatCount>0</MacAddrRepeatCount>
        <MacAddrRecycleCount>0</MacAddrRecycleCount>
        <MacAddrPortStep>00:00:00:00:02:00</MacAddrPortStep>
        </EthernetII>
        <Ipv4>
        <Ipv4Addr>192.85.1.3</Ipv4Addr>
        <Ipv4AddrStep>0.0.0.1</Ipv4AddrStep>
        <Ipv4AddrRepeatCount>0</Ipv4AddrRepeatCount>
        <Ipv4AddrRecycleCount>0</Ipv4AddrRecycleCount>
        <Ipv4AddrPortStep>0.0.1.0</Ipv4AddrPortStep>
        <Ipv4GatewayAddr>192.85.1.1</Ipv4GatewayAddr>
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
        <PppoeClient>
        <Authentication>NONE</Authentication>
        <AutoRetryCount>65535</AutoRetryCount>
        <EchoRequestGenFreq>10</EchoRequestGenFreq>
        <EnableAutoFillIpv6>True</EnableAutoFillIpv6>
        <EnableAutoRetry>False</EnableAutoRetry>
        <EnableEchoRequest>False</EnableEchoRequest>
        <EnableMagicNum>True</EnableMagicNum>
        <EnableMruNegotiation>True</EnableMruNegotiation>
        <EnableNcpTermination>False</EnableNcpTermination>
        <MaxEchoRequestAttempts>0</MaxEchoRequestAttempts>
        <MruSize>1492</MruSize>
        <Password>spirent</Password>
        <Username>spirent</Username>
        </PppoeClient>
        </Protocols>
        </NetworkInfo>
        '''
    net_prof.Set('NetworkInfo', net_info)
    net_prof.AddObject(port, RelationType('AttachedPort'))

    expand_cmd = ctor.CreateCommand('spirent.methodology.ExpandNetworkProfileCommand')
    expand_cmd.Set('NetworkProfile', net_prof.GetObjectHandle())
    expand_cmd.Execute()

    assert 'PASSED' == expand_cmd.Get('PassFailState')
    device_list = net_prof.GetObjects('EmulatedDevice',
                                      RelationType('GeneratedObject'))
    assert 2 == len(device_list)

    cfg_list = []
    for device in device_list:
        ppp = device.GetObject('PppoeClientBlockConfig')
        if ppp is not None:
            cfg_list.append(ppp)

    assert 2 == len(cfg_list)

    val_cmd = ctor.CreateCommand('spirent.methodology.ValidatePppoxConnectedCommand')
    val_cmd.SetCollection('NetworkProfile', [net_prof.GetObjectHandle()])
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    res_list = []
    # Create a results object on one of the objects, verify current bound
    res_list.append(ctor.Create('PppoeClientBlockResults', cfg_list[0]))
    res_list[0].Set('Sessions', 1)
    assert 0 == res_list[0].Get('SessionsUp')

    val_cmd.Reset()
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Only 1 up the other is still not connected
    val_cmd.Reset()
    res_list[0].Set('SessionsUp', 1)
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Both bound
    res_list.append(ctor.Create('PppoeClientBlockResults', cfg_list[1]))
    res_list[1].Set('Sessions', 1)
    res_list[1].Set('SessionsUp', 1)
    val_cmd.Reset()
    val_cmd.Execute()
    assert True == val_cmd.Get('Verdict')


def d_test_no_profile(stc):
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
        <Interfaces><EthernetII>
        <MacAddr>00:01:94:00:00:01</MacAddr>
        <MacAddrStep>00:00:00:00:00:01</MacAddrStep>
        <MacAddrRepeatCount>0</MacAddrRepeatCount>
        <MacAddrRecycleCount>0</MacAddrRecycleCount>
        <MacAddrPortStep>00:00:00:00:02:00</MacAddrPortStep>
        </EthernetII>
        <Ipv4>
        <Ipv4Addr>192.85.1.3</Ipv4Addr>
        <Ipv4AddrStep>0.0.0.1</Ipv4AddrStep>
        <Ipv4AddrRepeatCount>0</Ipv4AddrRepeatCount>
        <Ipv4AddrRecycleCount>0</Ipv4AddrRecycleCount>
        <Ipv4AddrPortStep>0.0.1.0</Ipv4AddrPortStep>
        <Ipv4GatewayAddr>192.85.1.1</Ipv4GatewayAddr>
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
        <PppoeClient>
        <Authentication>NONE</Authentication>
        <AutoRetryCount>65535</AutoRetryCount>
        <EchoRequestGenFreq>10</EchoRequestGenFreq>
        <EnableAutoFillIpv6>True</EnableAutoFillIpv6>
        <EnableAutoRetry>False</EnableAutoRetry>
        <EnableEchoRequest>False</EnableEchoRequest>
        <EnableMagicNum>True</EnableMagicNum>
        <EnableMruNegotiation>True</EnableMruNegotiation>
        <EnableNcpTermination>False</EnableNcpTermination>
        <MaxEchoRequestAttempts>0</MaxEchoRequestAttempts>
        <MruSize>1492</MruSize>
        <Password>spirent</Password>
        <Username>spirent</Username>
        </PppoeClient>
        </Protocols>
        </NetworkInfo>
        '''
    net_prof.Set('NetworkInfo', net_info)
    net_prof.AddObject(port, RelationType('AttachedPort'))

    expand_cmd = ctor.CreateCommand('spirent.methodology.ExpandNetworkProfileCommand')
    expand_cmd.Set('NetworkProfile', net_prof.GetObjectHandle())
    expand_cmd.Execute()

    assert 'PASSED' == expand_cmd.Get('PassFailState')
    device_list = net_prof.GetObjects('EmulatedDevice',
                                      RelationType('GeneratedObject'))
    assert 2 == len(device_list)

    cfg_list = []
    for device in device_list:
        ppp = device.GetObject('PppoeClientBlockConfig')
        if ppp is not None:
            cfg_list.append(ppp)

    assert 2 == len(cfg_list)

    val_cmd = ctor.CreateCommand('spirent.methodology.ValidatePppoxConnectedCommand')
    val_cmd.SetCollection('NetworkProfile', [project.GetObjectHandle()])
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    res_list = []
    # Create a results object on one of the objects, verify current bound
    res_list.append(ctor.Create('PppoeClientBlockResults', cfg_list[0]))
    res_list[0].Set('Sessions', 1)
    assert 0 == res_list[0].Get('SessionsUp')

    val_cmd.Reset()
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Only 1 up the other is still not connected
    val_cmd.Reset()
    res_list[0].Set('SessionsUp', 1)
    val_cmd.Execute()
    assert False == val_cmd.Get('Verdict')

    # Both bound
    res_list.append(ctor.Create('PppoeClientBlockResults', cfg_list[1]))
    res_list[1].Set('Sessions', 1)
    res_list[1].Set('SessionsUp', 1)
    val_cmd.Reset()
    val_cmd.Execute()
    assert True == val_cmd.Get('Verdict')
