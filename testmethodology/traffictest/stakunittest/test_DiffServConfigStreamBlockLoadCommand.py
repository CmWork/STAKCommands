from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


PKG_BASE = "spirent.methodology"
PKG = PKG_BASE + ".traffictest"


'''
Rates supported by this command.
'''
ETH_RATE_TABLE = {
    'SPEED_10M':     10000000.0,
    'SPEED_100M':   100000000.0,
    'SPEED_1G':    1000000000.0,
    'SPEED_10G':   10000000000.0,
    'SPEED_40G':   40000000000.0,
    'SPEED_100G': 100000000000.0
}


'''
Create data model configurations with stream blocks, ports,
and active phys. Then run the command with various inputs.
'''


def get_desired_tx_load(rx_load, rx_line_speed, num_stream_blocks, tx_line_speed):
    '''
    Desired TX load = (RXLoad * RXLineSpeed)/(NumStreamBlocks * TXLineSpeed)
    '''
    return (rx_load * rx_line_speed) / ((num_stream_blocks * tx_line_speed))


def test_config_stream_block_load_command_simple(stc):
    '''
    Simple test with three ports. 2 TX and one RX. All same speed.
    '''
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("test_config_stream_block_load_command_simple.begin")

    tag_name = "UnitTestMe"
    tx_speed = "SPEED_1G"
    rx_speed = "SPEED_1G"
    # Create the data model
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    # Create ports and active PHYs
    # TX1
    tx_port_1 = ctor.Create("Port", project)
    tx_active_phy_1 = ctor.Create("EthernetCopper",
                                  tx_port_1)
    tx_port_1.AddObject(tx_active_phy_1,
                        RelationType("ActivePhy"))
    tx_active_phy_1.Set("LineSpeed", tx_speed)
    # TX2
    tx_port_2 = ctor.Create("Port", project)
    tx_active_phy_2 = ctor.Create("EthernetCopper",
                                  tx_port_2)
    tx_port_2.AddObject(tx_active_phy_2,
                        RelationType("ActivePhy"))
    tx_active_phy_2.Set("LineSpeed", tx_speed)
    # RX
    rx_port = ctor.Create("Port", project)

    rx_active_phy = ctor.Create("EthernetCopper",
                                rx_port)
    rx_port.AddObject(rx_active_phy,
                      RelationType("ActivePhy"))
    rx_active_phy.Set("LineSpeed", rx_speed)
    # Create stream blocks, tag, hook up to expected RX, set load
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', tag_name)
    # SB1
    stream_block_1 = ctor.Create("StreamBlock", tx_port_1)
    stream_block_1.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_1.AddObject(tag, RelationType('UserTag'))
    sb_1_load_profile = stream_block_1.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_1_load_profile.Set("Load", "1")
    # SB2
    stream_block_2 = ctor.Create("StreamBlock", tx_port_2)
    stream_block_2.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_2.AddObject(tag, RelationType('UserTag'))
    sb_2_load_profile = stream_block_2.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_2_load_profile.Set("Load", "2")

    # Now test the command with various inputs
    for desired_load in [0, 10, 45, 70, 100]:
        # Execute the command
        with AutoCommand(PKG + ".DiffServConfigStreamBlockLoadCommand") as cmd:
            cmd.SetCollection("TagNameList", [tag_name])
            cmd.Set("RxLoadPercent", str(desired_load))
            cmd.Execute()

        # Verify the results
        tx_desired_load = get_desired_tx_load(desired_load,
                                              ETH_RATE_TABLE[rx_speed],
                                              2,
                                              ETH_RATE_TABLE[tx_speed])
        assert sb_1_load_profile.Get("Load") == tx_desired_load
        assert sb_2_load_profile.Get("Load") == tx_desired_load

    plLogger.LogDebug("test_config_stream_block_load_command_simple.end")


def test_config_stream_block_load_command_aggregator(stc):
    '''
    Test of aggregation, 1G TX ports to a single 10G RX port.
    '''
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("test_config_stream_block_load_command.begin")

    tag_name = "UnitTestMe"
    tx_speed = "SPEED_1G"
    rx_speed = "SPEED_10G"
    # Create the data model
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    # Create ports and active PHYs
    # TX1
    tx_port_1 = ctor.Create("Port", project)
    tx_active_phy_1 = ctor.Create("EthernetCopper",
                                  tx_port_1)
    tx_port_1.AddObject(tx_active_phy_1,
                        RelationType("ActivePhy"))
    tx_active_phy_1.Set("LineSpeed", tx_speed)
    # TX2
    tx_port_2 = ctor.Create("Port", project)
    tx_active_phy_2 = ctor.Create("EthernetCopper",
                                  tx_port_2)
    tx_port_2.AddObject(tx_active_phy_2,
                        RelationType("ActivePhy"))
    tx_active_phy_2.Set("LineSpeed", tx_speed)
    # TX3
    tx_port_3 = ctor.Create("Port", project)
    tx_active_phy_3 = ctor.Create("EthernetCopper",
                                  tx_port_3)
    tx_port_3.AddObject(tx_active_phy_3,
                        RelationType("ActivePhy"))
    tx_active_phy_3.Set("LineSpeed", tx_speed)
    # TX4
    tx_port_4 = ctor.Create("Port", project)
    tx_active_phy_4 = ctor.Create("EthernetCopper",
                                  tx_port_4)
    tx_port_4.AddObject(tx_active_phy_4,
                        RelationType("ActivePhy"))
    tx_active_phy_4.Set("LineSpeed", tx_speed)
    # TX5
    tx_port_5 = ctor.Create("Port", project)
    tx_active_phy_5 = ctor.Create("EthernetCopper",
                                  tx_port_5)
    tx_port_5.AddObject(tx_active_phy_5,
                        RelationType("ActivePhy"))
    tx_active_phy_5.Set("LineSpeed", tx_speed)
    # TX6
    tx_port_6 = ctor.Create("Port", project)
    tx_active_phy_6 = ctor.Create("EthernetCopper",
                                  tx_port_6)
    tx_port_6.AddObject(tx_active_phy_6,
                        RelationType("ActivePhy"))
    tx_active_phy_6.Set("LineSpeed", tx_speed)
    # TX7
    tx_port_7 = ctor.Create("Port", project)
    tx_active_phy_7 = ctor.Create("EthernetCopper",
                                  tx_port_7)
    tx_port_7.AddObject(tx_active_phy_7,
                        RelationType("ActivePhy"))
    tx_active_phy_7.Set("LineSpeed", tx_speed)
    # TX8
    tx_port_8 = ctor.Create("Port", project)
    tx_active_phy_8 = ctor.Create("EthernetCopper",
                                  tx_port_8)
    tx_port_8.AddObject(tx_active_phy_8,
                        RelationType("ActivePhy"))
    tx_active_phy_8.Set("LineSpeed", tx_speed)
    # TX9
    tx_port_9 = ctor.Create("Port", project)
    tx_active_phy_9 = ctor.Create("EthernetCopper",
                                  tx_port_9)
    tx_port_9.AddObject(tx_active_phy_9,
                        RelationType("ActivePhy"))
    tx_active_phy_9.Set("LineSpeed", tx_speed)
    # TX10
    tx_port_10 = ctor.Create("Port", project)
    tx_active_phy_10 = ctor.Create("EthernetCopper",
                                   tx_port_10)
    tx_port_10.AddObject(tx_active_phy_10,
                         RelationType("ActivePhy"))
    tx_active_phy_10.Set("LineSpeed", tx_speed)
    # RX
    rx_port = ctor.Create("Port", project)

    rx_active_phy = ctor.Create("EthernetCopper",
                                rx_port)
    rx_port.AddObject(rx_active_phy,
                      RelationType("ActivePhy"))
    rx_active_phy.Set("LineSpeed", rx_speed)
    # Create stream blocks, tag, hook up to expected RX, set load
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', tag_name)
    # SB1
    stream_block_1 = ctor.Create("StreamBlock", tx_port_1)
    stream_block_1.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_1.AddObject(tag, RelationType('UserTag'))
    sb_1_load_profile = stream_block_1.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_1_load_profile.Set("Load", "1")
    # SB2
    stream_block_2 = ctor.Create("StreamBlock", tx_port_2)
    stream_block_2.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_2.AddObject(tag, RelationType('UserTag'))
    sb_2_load_profile = stream_block_2.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_2_load_profile.Set("Load", "2")
    # SB3
    stream_block_3 = ctor.Create("StreamBlock", tx_port_3)
    stream_block_3.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_3.AddObject(tag, RelationType('UserTag'))
    sb_3_load_profile = stream_block_3.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_3_load_profile.Set("Load", "3")
    # SB4
    stream_block_4 = ctor.Create("StreamBlock", tx_port_4)
    stream_block_4.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_4.AddObject(tag, RelationType('UserTag'))
    sb_4_load_profile = stream_block_4.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_4_load_profile.Set("Load", "4")
    # SB5
    stream_block_5 = ctor.Create("StreamBlock", tx_port_5)
    stream_block_5.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_5.AddObject(tag, RelationType('UserTag'))
    sb_5_load_profile = stream_block_5.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_5_load_profile.Set("Load", "5")
    # SB6
    stream_block_6 = ctor.Create("StreamBlock", tx_port_6)
    stream_block_6.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_6.AddObject(tag, RelationType('UserTag'))
    sb_6_load_profile = stream_block_6.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_6_load_profile.Set("Load", "5")
    # SB7
    stream_block_7 = ctor.Create("StreamBlock", tx_port_7)
    stream_block_7.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_7.AddObject(tag, RelationType('UserTag'))
    sb_7_load_profile = stream_block_7.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_7_load_profile.Set("Load", "4")
    # SB8
    stream_block_8 = ctor.Create("StreamBlock", tx_port_8)
    stream_block_8.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_8.AddObject(tag, RelationType('UserTag'))
    sb_8_load_profile = stream_block_8.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_8_load_profile.Set("Load", "3")
    # SB9
    stream_block_9 = ctor.Create("StreamBlock", tx_port_9)
    stream_block_9.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_9.AddObject(tag, RelationType('UserTag'))
    sb_9_load_profile = stream_block_9.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_9_load_profile.Set("Load", "2")
    # SB10
    stream_block_10 = ctor.Create("StreamBlock", tx_port_10)
    stream_block_10.AddObject(rx_port, RelationType('ExpectedRx'))
    stream_block_10.AddObject(tag, RelationType('UserTag'))
    sb_10_load_profile = \
        stream_block_10.GetObject('StreamBlockLoadProfile',
                                  RelationType('Affiliationstreamblockloadprofile'))
    sb_10_load_profile.Set("Load", "1")

    # Now test the command with various inputs
    for desired_load in [0, 10, 45, 70, 100]:
        # Execute the command
        with AutoCommand(PKG + ".DiffServConfigStreamBlockLoadCommand") as cmd:
            cmd.SetCollection("TagNameList", [tag_name])
            cmd.Set("RxLoadPercent", str(desired_load))
            cmd.Execute()

        # Verify the results
        tx_desired_load = get_desired_tx_load(desired_load,
                                              ETH_RATE_TABLE[rx_speed],
                                              10,
                                              ETH_RATE_TABLE[tx_speed])
        assert sb_1_load_profile.Get("Load") == tx_desired_load
        assert sb_2_load_profile.Get("Load") == tx_desired_load
        assert sb_3_load_profile.Get("Load") == tx_desired_load
        assert sb_4_load_profile.Get("Load") == tx_desired_load
        assert sb_5_load_profile.Get("Load") == tx_desired_load
        assert sb_6_load_profile.Get("Load") == tx_desired_load
        assert sb_7_load_profile.Get("Load") == tx_desired_load
        assert sb_8_load_profile.Get("Load") == tx_desired_load
        assert sb_9_load_profile.Get("Load") == tx_desired_load
        assert sb_10_load_profile.Get("Load") == tx_desired_load

    plLogger.LogDebug("test_config_stream_block_load_command_aggregator.end")


def test_config_stream_block_load_command_concentratator(stc):
    '''
    Test of concentration, a single 10G TX port to 10 1G RX ports.
    '''
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("test_config_stream_block_load_command_concentratator.begin")

    tag_name = "UnitTestMe"
    tx_speed = "SPEED_10G"
    rx_speed = "SPEED_1G"
    # Create the data model
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    # Create ports and active PHYs
    # TX
    tx_port = ctor.Create("Port", project)

    tx_active_phy = ctor.Create("EthernetCopper",
                                tx_port)
    tx_port.AddObject(tx_active_phy,
                      RelationType("ActivePhy"))
    tx_active_phy.Set("LineSpeed", tx_speed)
    # RX1
    rx_port_1 = ctor.Create("Port", project)
    rx_active_phy_1 = ctor.Create("EthernetCopper",
                                  rx_port_1)
    rx_port_1.AddObject(rx_active_phy_1,
                        RelationType("ActivePhy"))
    rx_active_phy_1.Set("LineSpeed", rx_speed)
    # RX2
    rx_port_2 = ctor.Create("Port", project)
    rx_active_phy_2 = ctor.Create("EthernetCopper",
                                  rx_port_2)
    rx_port_2.AddObject(rx_active_phy_2,
                        RelationType("ActivePhy"))
    rx_active_phy_2.Set("LineSpeed", rx_speed)
    # RX3
    rx_port_3 = ctor.Create("Port", project)
    rx_active_phy_3 = ctor.Create("EthernetCopper",
                                  rx_port_3)
    rx_port_3.AddObject(rx_active_phy_3,
                        RelationType("ActivePhy"))
    rx_active_phy_3.Set("LineSpeed", rx_speed)
    # RX4
    rx_port_4 = ctor.Create("Port", project)
    rx_active_phy_4 = ctor.Create("EthernetCopper",
                                  rx_port_4)
    rx_port_4.AddObject(rx_active_phy_4,
                        RelationType("ActivePhy"))
    rx_active_phy_4.Set("LineSpeed", rx_speed)
    # RX5
    rx_port_5 = ctor.Create("Port", project)
    rx_active_phy_5 = ctor.Create("EthernetCopper",
                                  rx_port_5)
    rx_port_5.AddObject(rx_active_phy_5,
                        RelationType("ActivePhy"))
    rx_active_phy_5.Set("LineSpeed", rx_speed)
    # RX6
    rx_port_6 = ctor.Create("Port", project)
    rx_active_phy_6 = ctor.Create("EthernetCopper",
                                  rx_port_6)
    rx_port_6.AddObject(rx_active_phy_6,
                        RelationType("ActivePhy"))
    rx_active_phy_6.Set("LineSpeed", rx_speed)
    # RX7
    rx_port_7 = ctor.Create("Port", project)
    rx_active_phy_7 = ctor.Create("EthernetCopper",
                                  rx_port_7)
    rx_port_7.AddObject(rx_active_phy_7,
                        RelationType("ActivePhy"))
    rx_active_phy_7.Set("LineSpeed", rx_speed)
    # RX8
    rx_port_8 = ctor.Create("Port", project)
    rx_active_phy_8 = ctor.Create("EthernetCopper",
                                  rx_port_8)
    rx_port_8.AddObject(rx_active_phy_8,
                        RelationType("ActivePhy"))
    rx_active_phy_8.Set("LineSpeed", rx_speed)
    # RX9
    rx_port_9 = ctor.Create("Port", project)
    rx_active_phy_9 = ctor.Create("EthernetCopper",
                                  rx_port_9)
    rx_port_9.AddObject(rx_active_phy_9,
                        RelationType("ActivePhy"))
    rx_active_phy_9.Set("LineSpeed", rx_speed)
    # RX10
    rx_port_10 = ctor.Create("Port", project)
    rx_active_phy_10 = ctor.Create("EthernetCopper",
                                   rx_port_10)
    rx_port_10.AddObject(rx_active_phy_10,
                         RelationType("ActivePhy"))
    rx_active_phy_10.Set("LineSpeed", rx_speed)
    # Create stream blocks, tag, hook up to expected RX, set load
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', tag_name)
    # SB1
    stream_block_1 = ctor.Create("StreamBlock", tx_port)
    stream_block_1.AddObject(rx_port_1, RelationType('ExpectedRx'))
    stream_block_1.AddObject(tag, RelationType('UserTag'))
    sb_1_load_profile = stream_block_1.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_1_load_profile.Set("Load", "1")
    # SB2
    stream_block_2 = ctor.Create("StreamBlock", tx_port)
    stream_block_2.AddObject(rx_port_2, RelationType('ExpectedRx'))
    stream_block_2.AddObject(tag, RelationType('UserTag'))
    sb_2_load_profile = stream_block_2.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_2_load_profile.Set("Load", "2")
    # SB3
    stream_block_3 = ctor.Create("StreamBlock", tx_port)
    stream_block_3.AddObject(rx_port_3, RelationType('ExpectedRx'))
    stream_block_3.AddObject(tag, RelationType('UserTag'))
    sb_3_load_profile = stream_block_3.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_3_load_profile.Set("Load", "3")
    # SB4
    stream_block_4 = ctor.Create("StreamBlock", tx_port)
    stream_block_4.AddObject(rx_port_4, RelationType('ExpectedRx'))
    stream_block_4.AddObject(tag, RelationType('UserTag'))
    sb_4_load_profile = stream_block_4.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_4_load_profile.Set("Load", "4")
    # SB5
    stream_block_5 = ctor.Create("StreamBlock", tx_port)
    stream_block_5.AddObject(rx_port_5, RelationType('ExpectedRx'))
    stream_block_5.AddObject(tag, RelationType('UserTag'))
    sb_5_load_profile = stream_block_5.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_5_load_profile.Set("Load", "5")
    # SB6
    stream_block_6 = ctor.Create("StreamBlock", tx_port)
    stream_block_6.AddObject(rx_port_6, RelationType('ExpectedRx'))
    stream_block_6.AddObject(tag, RelationType('UserTag'))
    sb_6_load_profile = stream_block_6.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_6_load_profile.Set("Load", "5")
    # SB7
    stream_block_7 = ctor.Create("StreamBlock", tx_port)
    stream_block_7.AddObject(rx_port_7, RelationType('ExpectedRx'))
    stream_block_7.AddObject(tag, RelationType('UserTag'))
    sb_7_load_profile = stream_block_7.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_7_load_profile.Set("Load", "4")
    # SB8
    stream_block_8 = ctor.Create("StreamBlock", tx_port)
    stream_block_8.AddObject(rx_port_8, RelationType('ExpectedRx'))
    stream_block_8.AddObject(tag, RelationType('UserTag'))
    sb_8_load_profile = stream_block_8.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_8_load_profile.Set("Load", "3")
    # SB9
    stream_block_9 = ctor.Create("StreamBlock", tx_port)
    stream_block_9.AddObject(rx_port_9, RelationType('ExpectedRx'))
    stream_block_9.AddObject(tag, RelationType('UserTag'))
    sb_9_load_profile = stream_block_9.GetObject('StreamBlockLoadProfile',
                                                 RelationType('Affiliationstreamblockloadprofile'))
    sb_9_load_profile.Set("Load", "2")
    # SB10
    stream_block_10 = ctor.Create("StreamBlock", tx_port)
    stream_block_10.AddObject(rx_port_10, RelationType('ExpectedRx'))
    stream_block_10.AddObject(tag, RelationType('UserTag'))
    sb_10_load_profile = \
        stream_block_10.GetObject('StreamBlockLoadProfile',
                                  RelationType('Affiliationstreamblockloadprofile'))
    sb_10_load_profile.Set("Load", "1")

    # Now test the command with various inputs
    for desired_load in [0, 10, 45, 70, 100]:
        # Execute the command
        with AutoCommand(PKG + ".DiffServConfigStreamBlockLoadCommand") as cmd:
            cmd.SetCollection("TagNameList", [tag_name])
            cmd.Set("RxLoadPercent", str(desired_load))
            cmd.Execute()

        # Verify the results
        tx_desired_load = get_desired_tx_load(desired_load,
                                              ETH_RATE_TABLE[rx_speed],
                                              10,
                                              ETH_RATE_TABLE[tx_speed])
        assert sb_1_load_profile.Get("Load") == tx_desired_load
        assert sb_2_load_profile.Get("Load") == tx_desired_load
        assert sb_3_load_profile.Get("Load") == tx_desired_load
        assert sb_4_load_profile.Get("Load") == tx_desired_load
        assert sb_5_load_profile.Get("Load") == tx_desired_load
        assert sb_6_load_profile.Get("Load") == tx_desired_load
        assert sb_7_load_profile.Get("Load") == tx_desired_load
        assert sb_8_load_profile.Get("Load") == tx_desired_load
        assert sb_9_load_profile.Get("Load") == tx_desired_load
        assert sb_10_load_profile.Get("Load") == tx_desired_load

    plLogger.LogDebug("test_config_stream_block_load_command_concentratator.end")
