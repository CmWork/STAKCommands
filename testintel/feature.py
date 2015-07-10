"""Feature utilities

Copyright (c) 2014 by Spirent Communications Inc.
All Rights Reserved.

This software is confidential and proprietary to Spirent Communications Inc.
No part of this software may be reproduced, transmitted, disclosed or used
in violation of the Software License Agreement without the expressed
written consent of Spirent Communications Inc.
"""

FEATURES = []


def features():
    """Return list of all supported/known features."""
    global FEATURES
    if not FEATURES:
        FEATURES = _extract_features()
    return FEATURES


def _extract_features():
    """Discover the list of all supported/known features."""
    # TODO: get this from the bll/rcm/database
    return ['deviceCount', 'streamCount', 'avgFramesPerSecond',
            'avgPacketSize']
