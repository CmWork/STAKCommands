"""DiffServConfigStreamBlockLoadCommand

Copyright (c) 2015 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""
from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


'''
Rates supported by this command.
'''
ETH_RATE_TABLE = {
    'SPEED_10M':      10000000.0,
    'SPEED_100M':    100000000.0,
    'SPEED_1G':     1000000000.0,
    'SPEED_10G':   10000000000.0,
    'SPEED_40G':   40000000000.0,
    'SPEED_100G': 100000000000.0
}


# Configure the load on a set of tagged StreamBlocks
def validate(TagNameList, RxLoadPercent):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("DiffServConfigStreamBlockLoadCommand.Validate")

    if len(TagNameList) < 1:
        return "Error: Empty TagList"

    if (RxLoadPercent < 0) or (RxLoadPercent > 100):
        return "Error: RxLoadPercent value out of range"

    # Find the StreamBlock objects that have been tagged
    sb_obj_list = tag_utils.get_tagged_objects_from_string_names(
        TagNameList,
        remove_duplicates=True,
        ignore_tags_obj=True,
        class_name="StreamBlock")

    if not sb_obj_list:
        return "Error: No tagged stream block found"

    '''
    Check ports
    - All stream blocks must have endpoints
    - All TX ports must be the same speed
    - All RX ports must be the same speed
    '''
    tx_port_speeds = []
    rx_port_speeds = []
    for sb_obj in sb_obj_list:
        # Check that ports exist
        tx_port = sb_obj.GetParent()
        if not tx_port:
            return "Error: Stream block missing TX port"
        rx_port = sb_obj.GetObject('Port',
                                   RelationType('ExpectedRx'))
        if not rx_port:
            return "Error: Stream block missing RX port"
        # Check that we have active phys and add their speeds to list
        active_tx_phy = tx_port.GetObject('EthernetPhy',
                                          RelationType('ActivePhy'))
        if not active_tx_phy:
            return "Error: No active TX phy found"
        tx_line_speed = active_tx_phy.Get('LineSpeed')
        if tx_line_speed not in ETH_RATE_TABLE:
            return "Error: Unknown TX port speed detected"
        tx_port_speeds.append(ETH_RATE_TABLE[tx_line_speed])
        active_rx_phy = rx_port.GetObject('EthernetPhy',
                                          RelationType('ActivePhy'))
        if not active_rx_phy:
            return "Error: No active RX phy found"
        rx_line_speed = active_rx_phy.Get('LineSpeed')
        if rx_line_speed not in ETH_RATE_TABLE:
            return "Error: Unknown RX port speed detected"
        rx_port_speeds.append(ETH_RATE_TABLE[rx_line_speed])

    # Check that all TX speeds are the same
    if tx_port_speeds.count(tx_port_speeds[0]) != len(tx_port_speeds):
        return 'Error: All TX ports must be the same speed'
    # Check that all RX speeds are the same
    if rx_port_speeds.count(rx_port_speeds[0]) != len(rx_port_speeds):
        return 'Error: All RX ports must be the same speed'
    '''
    Verify that the calculation yields a valid TX load

    Desired TX load = (RXLoad * RXLineSpeed)/(NumTXPorts * TXLineSpeed)
    '''

    tx_load = (RxLoadPercent * rx_port_speeds[0]) / ((len(tx_port_speeds) * tx_port_speeds[0]))
    if (tx_load < 0) or (tx_load > 100):
        return "Error: TX Load calculation yields an invalid result. " + \
            "Combination of ports and speeds must be changed."
    return ""


def run(TagNameList, RxLoadPercent):
    """
    Given a list of tag names, find all the StreamBlocks with tags on the
    list and set their loads such that the aggregate load on each RX
    port is RxLoadPercent percent.
    - TagNameList is a list of strings
    - RxLoadPercent is a number between 0 and 100, inclusive
    """
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("DiffServConfigStreamBlockLoadCommand.run")

    plLogger.LogDebug("TagNameList: " + str(TagNameList))

    # Find the StreamBlock objects that have been tagged
    sb_obj_list = tag_utils.get_tagged_objects_from_string_names(
        TagNameList,
        remove_duplicates=True,
        ignore_tags_obj=True,
        class_name="StreamBlock")

    if not sb_obj_list:
        plLogger.LogError("Error: No tagged stream block found")
        return False

    '''
    Check ports
    - All stream blocks must have endpoints
    - All TX ports must be the same speed
    - All RX ports must be the same speed
    '''

    # Create lists of ports
    tx_ports = []
    tx_port_handles = []
    rx_ports = []
    rx_port_handles = []
    for sb_obj in sb_obj_list:
        # Check that ports exist
        tx_port = sb_obj.GetParent()
        if not tx_port:
            plLogger.LogError("Error: Stream block missing TX port")
            return False
        # use handles to get rid of any duplicate ports.
        tx_port_handle = tx_port.GetObjectHandle()
        if tx_port_handle not in tx_port_handles:
            # add this port to the list
            tx_ports.append(tx_port)
            tx_port_handles.append(tx_port_handle)
        # Repeat for RX port
        rx_port = sb_obj.GetObject('Port',
                                   RelationType('ExpectedRx'))
        if not rx_port:
            plLogger.LogError("Error: Stream block missing RX port")
            return False
        # use handles to get rid of any duplicate ports.
        rx_port_handle = rx_port.GetObjectHandle()
        if rx_port_handle not in rx_port_handles:
            # add this port to the list
            rx_ports.append(rx_port)
            rx_port_handles.append(rx_port_handle)

    plLogger.LogDebug("tx_ports: " + str(tx_ports))
    plLogger.LogDebug("tx_ports len: " + str(len(tx_ports)))
    plLogger.LogDebug("tx_port_handles: " + str(tx_port_handles))
    plLogger.LogDebug("tx_port_handles len: " + str(len(tx_port_handles)))
    plLogger.LogDebug("rx_ports: " + str(rx_ports))
    plLogger.LogDebug("rx_ports len: " + str(len(rx_ports)))

    # Now process each port
    tx_port_speeds = []
    rx_port_speeds = []
    for tx_port in tx_ports:
        # Check that we have active phys and add their speeds to list
        active_tx_phy = tx_port.GetObject('EthernetPhy',
                                          RelationType('ActivePhy'))
        if not active_tx_phy:
            plLogger.LogError("Error: No active TX phy found")
            return False
        tx_line_speed = active_tx_phy.Get('LineSpeed')
        if tx_line_speed not in ETH_RATE_TABLE:
            plLogger.LogError("Error: Unknown TX port speed detected")
            return False
        tx_port_speeds.append(ETH_RATE_TABLE[tx_line_speed])
    for rx_port in rx_ports:
        active_rx_phy = rx_port.GetObject('EthernetPhy',
                                          RelationType('ActivePhy'))
        if not active_rx_phy:
            plLogger.LogError("Error: No active RX phy found")
            return False
        rx_line_speed = active_rx_phy.Get('LineSpeed')
        if rx_line_speed not in ETH_RATE_TABLE:
            plLogger.LogError("Error: Unknown RX port speed detected")
            return False
        rx_port_speeds.append(ETH_RATE_TABLE[rx_line_speed])

    # Check that all TX speeds are the same
    if tx_port_speeds.count(tx_port_speeds[0]) != len(tx_port_speeds):
        plLogger.LogError("Error: All TX ports must be the same speed")
        return False
    # Check that all RX speeds are the same
    if rx_port_speeds.count(rx_port_speeds[0]) != len(rx_port_speeds):
        plLogger.LogError("Error: All RX ports must be the same speed")
        return False
    '''
    Verify that the calculation yields a valid TX load

    Desired TX load = (RXLoad * RXLineSpeed)/(NumStreamBlocks * TXLineSpeed)
    '''

    tx_load = (RxLoadPercent * rx_port_speeds[0]) / ((len(sb_obj_list) * tx_port_speeds[0]))
    if (tx_load < 0) or (tx_load > 100):
        err_txt = "Error: TX Load calculation yields an invalid result. " + \
            "Combination of ports and speeds must be changed."
        plLogger.LogError(err_txt)
        return False

    # Get the load profile objects and set their loads
    for sb_obj in sb_obj_list:
        plLogger.LogDebug("Found sb: " + str(sb_obj))
        loadprofile = sb_obj.GetObject('StreamBlockLoadProfile',
                                       RelationType('Affiliationstreamblockloadprofile'))
        if not loadprofile:
            plLogger.LogError("Could not find Stream Block load profile.")
            return False
        loadprofile.Set("Load", str(tx_load))

    return True


def reset():

    return True
