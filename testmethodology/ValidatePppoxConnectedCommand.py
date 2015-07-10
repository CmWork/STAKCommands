from StcIntPythonPL import *


def validate(Iteration, NetworkProfile):
    # plLogger = PLLogger.GetLogger('methodology')
    # plLogger.LogInfo(" Validate ValidatePppoxConnectedCommand")

    return ""


def run(Iteration, NetworkProfile):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run ValidatePppoxConnectedCommand")

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)
    this_cmd.Set("Verdict", False)

    # Get the Network Profile using the handle

    dev_list = []
    for hnd in NetworkProfile:
        arg_obj = hnd_reg.Find(int(hnd))
        if arg_obj is None:
            plLogger.LogError("Invalid Network Profile handle")
            return False
        if arg_obj.IsTypeOf('Project'):
            dev_list += arg_obj.GetObjects('EmulatedDevice')
        elif arg_obj.IsTypeOf('TopologyProfile'):
            net_prof_list = arg_obj.GetObjects('NetworkProfile')
            for prof in net_prof_list:
                dev_list += prof.GetObjects('EmulatedDevice',
                                            RelationType('GeneratedObject'))
        elif arg_obj.IsTypeOf('NetworkProfile'):
            dev_list += arg_obj.GetObjects('EmulatedDevice',
                                           RelationType('GeneratedObject'))

    # Find the devices with PppoeClientBlockConfig
    # If any of the blocks have failed sessions return with Verdict False
    for dev in dev_list:
        ppp_proto = dev.GetObject("PppoeClientBlockConfig")
        if ppp_proto is not None:
            ppp_results = ppp_proto.GetObject("PppoeClientBlockResults")
            if ppp_results is None:
                # assume not connected if config but no results
                return True
            else:
                sessions = ppp_results.Get("Sessions")
                up = ppp_results.Get("SessionsUp")
                if (up < sessions):
                    return True

    # All PPPoE Client Blocks have no failed sessions
    this_cmd.Set("Verdict", True)
    return True


def reset():
    return True
