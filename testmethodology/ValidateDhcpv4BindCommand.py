from StcIntPythonPL import *
import utils.network_profile_utils as net_prof_utils


def validate(Iteration, ObjectList):
    # plLogger = PLLogger.GetLogger('methodology')
    # plLogger.LogInfo(" Validate ValidateDhcpv4BindCommand")

    return ""


def run(Iteration, ObjectList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run ValidateDhcpv4BindCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)
    if this_cmd is None:
        return False
    this_cmd.Set("Verdict", False)

    # Process input objects
    obj_list = []
    valid_obj_list = []
    for objHandle in ObjectList:
        scriptable_obj = hnd_reg.Find(objHandle)
        if scriptable_obj is None:
            # Display a warning later
            continue
        obj_list.append(scriptable_obj)

    if (len(obj_list) > 0):
        valid_obj_list = net_prof_utils.process_input_objects(obj_list, "NetworkProfile")

    if len(valid_obj_list) <= 0:
        plLogger.LogError("ERROR: No valid NetworkProfiles to validate.")
        return False

    for netProfile in valid_obj_list:

        # Get the device list
        devList = netProfile.GetObjects("EmulatedDevice", RelationType("GeneratedObject"))

        for dev in devList:
            dhcp_proto = dev.GetObject("Dhcpv4BlockConfig")
            if dhcp_proto is None:
                continue
            dhcp_results = dhcp_proto.GetObject("Dhcpv4BlockResults")
            bound_count = dhcp_results.Get("CurrentBoundCount") \
                if dhcp_results else 0
            if bound_count != dev.Get("DeviceCount"):
                return True

    this_cmd.Set("Verdict", True)
    return True


def reset():

    return True
