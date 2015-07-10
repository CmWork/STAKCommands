from StcIntPythonPL import *


# Validate base class
def validate(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate ValidateDhcpv6BoundCommand")

    return ""


def run(Iteration):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run ValidateDhcpv6BoundCommand")

    hnd_reg = CHandleRegistry.Instance()

    myself = hnd_reg.Find(__commandHandle__)

    project = CStcSystem.Instance().GetObject('Project')

    # Grab all network profiles for this test
    net_prof_list = project.GetObjects('NetworkProfile')
    bound = True
    for net_prof in net_prof_list:
        dev_list = net_prof.GetObjects('EmulatedDevice',
                                       RelationType('GeneratedObject'))
        for dev in dev_list:
            cfg = dev.GetObject('Dhcpv6BaseBlockConfig')
            if cfg is None:
                continue
            if 'BOUND' != cfg.Get('BlockState'):
                bound = False
                break
            # At this point, it says it's "bound" but we need to check with
            # results, if we find any
            result = cfg.GetObject('Dhcpv6BlockResults')
            if result is not None:
                dev_count = dev.Get('DeviceCount')
                bound_count = result.Get('CurrentBoundCount')
                if dev_count != bound_count:
                    plLogger.LogInfo("Failed because bound count is " +
                                     str(bound_count) +
                                     "and device count is " + str(dev_count))
                    bound = False
                    break
            else:
                # Failed to find
                    plLogger.LogInfo("There was no result object found for " +
                                     dev.Get('Name'))

        if bound is False:
            break
    plLogger.LogInfo(" Verdict: " + str(bound))
    myself.Set('Verdict', bound)
    return True


def reset():
    return True
