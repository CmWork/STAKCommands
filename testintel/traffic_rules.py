"""Traffic rules

Copyright (c) 2014-2015 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

# relevent columns (features) found in test run #43
COLUMNS = {'rate': ['StreamCount', 'AvgPacketSize'],
           'memory': ['StreamCount', 'AvgPacketSize']}

# functional parameters found in test run #43, #45 (memory)
# see fit_function in regression/usage/traffic.py for how they are used
PARAMS = {'rate': [20578.6, -0.593584, -0.572997],
          'memory': [339336, 6.80677, 0.092882]}

# function types used in run #43, #45 (memory)
# see regression/usage/traffic.py for an explanation
FN_TYPE_LIST = {'rate': [('CONST',), ('POLY', 1), ('POLY', 1)],
                'memory': [('CONST',), ('POLY', 1), ('POLY', 1)]}

# if we calculate that something falls between the safety factor and the
# rule-based limit, we scale the confidence linearly
# For example, if we calculate we can support 10000 fps with a safety factor
# of 90%, we will return full confidence if the user requests 9000 fps,
# no confidence if the user requests 10001 fps, and 50.0 confidence if
# the user requests 9500 fps.
SAFETY_FACTOR = 0.9

BASE_PREFLIGHT = 6000
