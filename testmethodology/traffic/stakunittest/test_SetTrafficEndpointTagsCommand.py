from StcIntPythonPL import *
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
from spirent.core.utils.scriptable import AutoCommand


PKG = 'spirent.methodology.traffic'


def test_set_traffic_endpoint_tags_command(stc):
    proj = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()

    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="" />')

    # Create the command, set the parameters and execute it
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.Set('TrafficMix', traf_mix.GetObjectHandle())
        cmd.SetCollection('SrcEndpointNameList', ['sourceTag1', 'sourceTag2'])
        cmd.SetCollection('DstEndpointNameList', ['destTag1', 'destTag2'])
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')

    # Command should have passed
    assert pass_fail_state == 'PASSED'

    # Verify the TrafficInfo XML is correct
    trafficInfo = traf_mix.Get('MixInfo')
    expTrafficInfo = '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" ' + \
                     'WeightList="">' + \
                     '<Endpoints>' + \
                     '<SrcEndpoint>sourceTag1</SrcEndpoint>' + \
                     '<SrcEndpoint>sourceTag2</SrcEndpoint>' + \
                     '<DstEndpoint>destTag1</DstEndpoint>' + \
                     '<DstEndpoint>destTag2</DstEndpoint>' + \
                     '</Endpoints></MixInfo>'
    assert trafficInfo == expTrafficInfo

    # And call the command again with one source tag, it should appended
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.Set('TrafficMix', traf_mix.GetObjectHandle())
        cmd.SetCollection('SrcEndpointNameList', ['sourceTag3'])
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')

    # Command should have passed
    assert pass_fail_state == 'PASSED'

    # Verify the TrafficInfo XML is correct
    trafficInfo = traf_mix.Get('MixInfo')
    expTrafficInfo = '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" ' + \
                     'WeightList="">' + \
                     '<Endpoints>' + \
                     '<SrcEndpoint>sourceTag1</SrcEndpoint>' + \
                     '<SrcEndpoint>sourceTag2</SrcEndpoint>' + \
                     '<DstEndpoint>destTag1</DstEndpoint>' + \
                     '<DstEndpoint>destTag2</DstEndpoint>' + \
                     '<SrcEndpoint>sourceTag3</SrcEndpoint>' + \
                     '</Endpoints></MixInfo>'
    assert trafficInfo == expTrafficInfo


def test_set_traffic_endpoint_tags_command_errors(stc):
    proj = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()

    traf_mix = ctor.Create('StmTrafficMix', proj)

    #####################################
    # Failure test 1: no TrafficMix
    #####################################
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.SetCollection('SrcEndpointNameList', ['sourceTag1'])
        cmd.SetCollection('DstEndpointNameList', ['destTag1'])
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')
    # Command should have failed
    assert pass_fail_state == 'FAILED'

    #####################################
    # Failure test 2: no MixInfo in TrafficMix
    #####################################
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.Set('TrafficMix', traf_mix.GetObjectHandle())
        cmd.SetCollection('SrcEndpointNameList', ['sourceTag1'])
        cmd.SetCollection('DstEndpointNameList', ['destTag1'])
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')
    # Command should have failed
    assert pass_fail_state == 'FAILED'

    # Create and set the TrafficInfo
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="" />')

    #####################################
    # Failure test 3: no TrafficMix
    #####################################
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.Set('TrafficMix', traf_mix.GetObjectHandle())
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')
    # Command should have failed
    assert pass_fail_state == 'FAILED'

    # Finally, passing command
    with AutoCommand(PKG + '.SetTrafficEndpointTagsCommand') as cmd:
        cmd.Set('TrafficMix', traf_mix.GetObjectHandle())
        cmd.SetCollection('DstEndpointNameList', ['destTag1'])
        cmd.Execute()
        pass_fail_state = cmd.Get('PassFailState')
    # Command should have passed
    assert pass_fail_state == 'PASSED'
