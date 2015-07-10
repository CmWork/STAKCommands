from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"
TPKG = PKG + ".traffic"
TTPKG = PKG + ".traffictest"


def get_valid_cmd_list():
    return [cmd_name.lower() for cmd_name in [
        TPKG + ".LoadTrafficTemplateCommand",
        TTPKG + ".LoadAclTrafficRulesCommand",
        TPKG + ".SetTrafficEndpointTagsCommand",
        "SequencerComment",
        PKG + ".RunPyScriptCommand"]]


def validate_contained_cmds(group_cmd):
    valid_cmd_list = get_valid_cmd_list()

    # Validate the contents of the group command
    hnd_reg = CHandleRegistry.Instance()
    cmd_hnd_list = group_cmd.GetCollection("CommandList")
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            return "Unable to find command with handle " + \
                str(cmd_hnd) + " in the handle registry."
        cmd_type = cmd.GetType()
        if cmd_type not in valid_cmd_list:
            return "Command " + cmd_type + " not in the set of " + \
                "valid commands for this group: " + \
                str(valid_cmd_list)
    return ""


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(Load, LoadUnit, MixTagName, AutoExpandTemplateMix):
    plLogger = PLLogger.GetLogger("CreateTrafficMix1Command")
    this_cmd = get_this_cmd()
    hnd_reg = CHandleRegistry.Instance()
    for cmd_hnd in this_cmd.GetCollection('CommandList'):
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogWarn("Skipping invalid command (handle=" +
                             str(cmd_hnd) + ")")
            continue
        if cmd.IsTypeOf('spirent.methodology.LoadTemplateCommand'):
            if cmd.Get('CopiesPerParent') != 1:
                plLogger.LogWarn("Resetting " + cmd.Get('Name') +
                                 " to have CopiesPerParent=1")
                cmd.Set('CopiesPerParent', 1)
            if cmd.Get('AutoExpandTemplate') is True:
                plLogger.LogWarn("Resetting " + cmd.Get('Name') +
                                 " to have AutoExpandTemplate=False")
                cmd.Set('AutoExpandTemplate', False)
    return validate_contained_cmds(get_this_cmd())


def run(Load, LoadUnit, MixTagName, AutoExpandTemplateMix):
    # plLogger = PLLogger.GetLogger("CreateTrafficMix1Command")
    hnd_reg = CHandleRegistry.Instance()
    this_cmd = get_this_cmd()
    proj = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()
    # Notes on element tree data storage:
    # We are using the attributes within a single MixInfo element, and each of
    # the values are stored as attributes of the single element. Note that
    # non-string values are not allowed in ElementTree, so the appropriate
    # casts are needed:
    # Set float: str(value)
    # Get float: float(value)
    # Enums, act as strings already
    # Append to list of float:
    #   list = list + ' ' + str(val) if len(list) != 0 else str(val)
    # Retrieve from list of float:
    #   float_list = [float(x) for x in list.split()]

    mix_info = {'Load': str(Load),
                'LoadUnit': LoadUnit,
                'WeightList': ''}
    # This is a one-node tree
    mix_elem = etree.Element('MixInfo', mix_info)
    traf_mix = ctor.Create('StmTrafficMix', proj)
    if traf_mix is None:
        plLogger.LogError('Failed to create StmTrafficMix')
        return False
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    traf_mix_hdl = traf_mix.GetObjectHandle()
    this_cmd.Set('StmTemplateMix', traf_mix_hdl)
    # Create tag if it doesn't exist, else associate existing tag
    if MixTagName:
        tag_utils.add_tag_to_object(traf_mix, MixTagName)

    # Configure all contained commands, note that validate should have ensured
    # the correct types were passed in, so they are not checked here
    for cmd_hnd in this_cmd.GetCollection('CommandList'):
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            continue
        if cmd.IsTypeOf(TPKG + ".SetTrafficEndpointTagsCommand"):
            cmd.Set('TrafficMix', traf_mix_hdl)
        if cmd.IsTypeOf(TPKG + ".LoadTrafficTemplateCommand"):
            cmd.Set("StmTemplateMix", traf_mix_hdl)
    return True


def on_complete(failed_commands):
    this_cmd = get_this_cmd()
    if this_cmd.Get("AutoExpandTemplateMix"):
        traf_mix_hdl = this_cmd.Get('StmTemplateMix')
        with AutoCommand(TPKG + '.ExpandTrafficMix1Command') as exp_cmd:
            exp_cmd.Set('StmTemplateMix', traf_mix_hdl)
            exp_cmd.Execute()
            if 'COMPLETED' != exp_cmd.Get('State'):
                this_cmd.Set('State', exp_cmd.Get('State'))
                this_cmd.Set('Status', exp_cmd.Get('Status'))
                return False
    return True


def reset():
    return True
