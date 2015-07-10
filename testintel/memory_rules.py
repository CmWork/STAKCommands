"""Memory rules

Copyright (c) 2014 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

# relevent columns (features) found in test run #10
COLUMNS = ['l4l7_TotalServerConnections',
           'framework_maxIsisRouterCount',
           'pppox_maxPppoxSessionCount',
           'framework_maxBgpSessionCount',
           'framework_maxOspfRouterCount',
           'dhcpv4_maxDhcpSvrSessionCount',
           'dhcpv4_maxDhcpSessionCount']

# functional parameters found in test run #10
# see fit_function in regression/usage/memory.py for how they are used
PARAMS = [339772, 0, 34, 20470, 74, 0, 10, 28988, 117, 24810, 284, 0, 1, 0, 8]
