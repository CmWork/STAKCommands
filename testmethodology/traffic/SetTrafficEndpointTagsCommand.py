from StcIntPythonPL import *
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree


def validate(TrafficMix, SrcEndpointNameList, DstEndpointNameList):
    return ''


def run(TrafficMix, SrcEndpointNameList, DstEndpointNameList):
    plLogger = PLLogger.GetLogger("trafficcenter")

    # Verify source and dest lists are not both empty
    if not SrcEndpointNameList and not DstEndpointNameList:
        plLogger.LogError("Source Endpoint List and Destination" +
                          "Endpoint Name Lists are both empty")
        return False

    # Get the TrafficMix object
    hndReg = CHandleRegistry.Instance()
    traf_mix = hndReg.Find(int(TrafficMix))

    if traf_mix is None:
        plLogger.LogError("TrafficMix with handle " +
                          str(TrafficMix) + " was not found")
        return False

    # The traf_mix object may be the parent of a TrafficMix, such as the
    # Project
    if "stmtrafficmix" != str(traf_mix.GetType()).lower():
        # Get all TrafficMix's under traf_mix
        traf_mix_list = CCommandEx.ProcessInputHandleVec('StmTrafficMix',
                                                         [traf_mix.GetObjectHandle()])
        if len(traf_mix_list) == 0:
            plLogger.LogError("No StmTrafficMix found under " +
                              str(traf_mix.Get('Name')))
            return False
        # Take the first one only
        traf_mix = traf_mix_list[0]

    tmi = traf_mix.Get('MixInfo')
    if tmi == '':
        plLogger.LogError("MixInfo is empty")
        return False

    # Get the MixInfo XML and add an <Endpoints> element if they don't exist
    mix_elem = etree.fromstring(tmi)
    endpoints = mix_elem.find('Endpoints')
    if endpoints is None:
        endpoints = Element('Endpoints')
        mix_elem.append(endpoints)

    # Go through list of src/dst endpoints and add elements to the
    # MixInfo XML
    for source in SrcEndpointNameList:
        sourceEndpoint = Element('SrcEndpoint')
        sourceEndpoint.text = source
        endpoints.append(sourceEndpoint)

    for dest in DstEndpointNameList:
        destEndpoint = Element('DstEndpoint')
        destEndpoint.text = dest
        endpoints.append(destEndpoint)

    # Set the new MixInfo
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    return True


def reset():
    return True
