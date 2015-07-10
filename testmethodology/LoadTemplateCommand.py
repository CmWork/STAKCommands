from StcIntPythonPL import *
import spirent.methodology.utils.xml_config_utils as xml_utils


PKG = "spirent.methodology"
did_expand = False


def get_valid_cmd_list():
    return [cmd_name.lower() for cmd_name in [
        PKG + ".AddTemplateObjectCommand",
        PKG + ".ConfigTemplateRelationCommand",
        PKG + ".DeleteTemplateObjectCommand",
        PKG + ".ModifyTemplatePropertyCommand",
        PKG + ".InsertTemplateIfCommand",
        PKG + ".RunPyScriptCommand",
        PKG + ".MergeTemplateCommand",
        PKG + ".ConfigTemplateStmPropertyModifierCommand",
        PKG + ".ConfigTemplateProtocolCommand",
        PKG + ".ConfigTemplateNetworkIfCommand",
        PKG + ".ConfigTemplatePdusCommand",
        "SequencerCommand"]]


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
        cmd_type = cmd.GetType().lower()
        if cmd_type == PKG + ".expandtemplatecommand":
            return PKG + ".ExpandTemplateCommand is not allowed " + \
                "in the group.  Set AutoExpandTemplaet to True to " + \
                "automatically expand."
        if cmd_type not in valid_cmd_list:
            return "Command " + cmd_type + " not in the set of " + \
                "valid commands for this group: " + \
                str(valid_cmd_list)
    return ""


# May consider moving elsewhere
# need to unit test
def config_contained_cmds(group_cmd, template_conf):
    # Configures the NetworkProfileGroupCommand's (or derived command's) contained
    # commands to pass the NetworkProfile handle
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start config_contained_cmds")
    hnd_reg = CHandleRegistry.Instance()
    valid_cmd_list = get_valid_cmd_list()

    cmd_hnd_list = group_cmd.GetCollection("CommandList")
    configured_cmd_count = 0
    for cmd_hnd in cmd_hnd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            plLogger.LogWarn("WARNING: Skipping cmd " + str(cmd_hnd) +
                             " as unable to find in handle registry")
            continue
        if cmd.GetType().lower() in valid_cmd_list:
            if not cmd.IsTypeOf("SequencerComment") and \
               not cmd.IsTypeOf(PKG + ".RunPyScriptCommand"):
                cmd.Set("StmTemplateConfig", template_conf.GetObjectHandle())
                configured_cmd_count = configured_cmd_count + 1
        else:
            # Skip the unhandled command
            plLogger.LogDebug("Skipping direct configuration of an " +
                              "StmTemplateConfig handle in " +
                              cmd.Get("Name") + "'s input list.  Update " +
                              "LoadTemplateCommand.config_contained_commands " +
                              "if a handle needs to be propagated.")
            continue
        plLogger.LogDebug("Configure input StmTemplateConfig for: " +
                          cmd.GetType() + " " +
                          str(cmd.GetObjectHandle()))
    return configured_cmd_count


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(CopiesPerParent, TargetTagList, TemplateXml,
             TemplateXmlFileName, TagPrefix, AutoExpandTemplate,
             EnableLoadFromFileName, StmTemplateMix):
    return validate_contained_cmds(get_this_cmd())


def run(CopiesPerParent, TargetTagList, TemplateXml,
        TemplateXmlFileName, TagPrefix, AutoExpandTemplate,
        EnableLoadFromFileName, StmTemplateMix):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("run LoadTemplateCommand")

    did_expand = False
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()

    # Look up the StmTemplateMix
    parent_obj = hnd_reg.Find(StmTemplateMix)
    if parent_obj is None:
        plLogger.LogDebug("Was unable to find a StmTemplateMix with " +
                          str(StmTemplateMix) + " using project ")
        parent_obj = project
    else:
        if not parent_obj.IsTypeOf("StmTemplateMix"):
            plLogger.LogError("Incorrect handle passed in for " +
                              "StmTemplateMix.  Expected an " +
                              "object of type StmTemplateMix, " +
                              "instead received a(n) " +
                              parent_obj.GetType())
            return False
        plLogger.LogDebug("Was able to find a StmTemplateMix, using " +
                          parent_obj.Get("Name") + " with id: " +
                          str(StmTemplateMix))

    # Create an empty TemplateConfig object
    temp_conf = ctor.Create("StmTemplateConfig", parent_obj)

    if temp_conf is None:
        plLogger.LogError("ERROR: Failed to create an StmTemplateConfig")
        return False

    xml_value = None
    if not EnableLoadFromFileName:
        xml_value = TemplateXml
    elif TemplateXmlFileName != '':
        xml_value = xml_utils.load_xml_from_file(TemplateXmlFileName)
    if xml_value is None:
        plLogger.LogError("ERROR: No valid template source.")
        return False

    if TagPrefix != '':
        xml_value = xml_utils.add_prefix_to_tags(TagPrefix, xml_value)
    temp_conf.Set("TemplateXml", xml_value)

    # Pass the handles to the commands contained in this group
    cmd_count = config_contained_cmds(get_this_cmd(), temp_conf)

    # Set the output handle (since we already have the object)
    this_cmd = get_this_cmd()
    this_cmd.Set("StmTemplateConfig", temp_conf.GetObjectHandle())

    # FIXME: WORKAROUND: on_last_command_complete() doesn't get called if
    # no children commands exist...
    if cmd_count == 0:
        on_complete([])
        did_expand = True
    if did_expand:
        pass
    # END FIXME: WORKAROUND
    return True


def on_complete(failed_commands):
    # FIXME
    # Should never get here, but we can skip the expand if we do
    if did_expand:
        return True
    this_cmd = get_this_cmd()
    if this_cmd.Get("AutoExpandTemplate") is True:
        ctor = CScriptableCreator()
        template_hnd = this_cmd.Get("StmTemplateConfig")

        cmd = ctor.CreateCommand("spirent.methodology.ExpandTemplateCommand")
        cmd.SetCollection("StmTemplateConfigList", [template_hnd])
        cmd.SetCollection("TargetTagList",
                          this_cmd.GetCollection("TargetTagList"))
        cmd.Set("CopiesPerParent", this_cmd.Get("CopiesPerParent"))
        cmd.Execute()
        result = cmd.Get('PassFailState')
        cmd.MarkDelete()
        if result == 'FAILED':
            return False
    return True


def reset():
    return True
