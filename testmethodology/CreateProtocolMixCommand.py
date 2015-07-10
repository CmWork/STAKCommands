from StcIntPythonPL import *
import json
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.template_mix_cmd_utils as mix_utils


PKG = "spirent.methodology"


def hierarchy():
    return (PKG + '.IterationGroupCommand', '',
            [('SequencerWhileCommand', 'rowIterator',
              [(PKG + '.IteratorConfigMixParamsCommand', 'rowConfigurator', []),
               (PKG + '.CreateTemplateConfigCommand', 'templateConfigurator', [])
               ]
              )])


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(MixInfo, MixTagName, PortGroupTagList,
             AutoExpandTemplateMix):
    return ""


def init():
    plLogger = PLLogger.GetLogger("methodology")
    this_cmd = get_this_cmd()

    # Check if the group is filled already.  If it is, don't do anything.
    cmd_list = this_cmd.GetCollection("CommandList")
    if len(cmd_list) > 0:
        plLogger.LogDebug("CreateProtocolMixCommand group is already " +
                          "filled.  Skipping pre-filling in init().")
        return True

    mix_utils.init_create_hierarchy(this_cmd, hierarchy())
    return True


def run(MixInfo, MixTagName, PortGroupTagList,
        AutoExpandTemplateMix):
    plLogger = PLLogger.GetLogger("methodology")
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    this_cmd = get_this_cmd()
    ctor = CScriptableCreator()

    # Validate the input MixInfo against its schema
    res = json_utils.validate_json(MixInfo, this_cmd.Get("MixInfoJsonSchema"))
    if res != "":
        err_str = "MixInfo is invalid or does not conform " + \
            "to the schema: " + res
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Validate the hierarchy against our current command list...
    msg = mix_utils.run_validate_hierarchy(this_cmd, [hierarchy()])
    if msg != '':
        plLogger.LogError('Invalid Sequence: ' + msg)
        this_cmd.Set("Status", msg)
        return False

    # Tag the commands in our command list according to our hierarchy information...
    tag_dict = mix_utils.run_tag_hierarchy(this_cmd, [hierarchy()])

    # Setup for property chaining / outputting the tag dictionary...
    this_cmd.Set('GroupCommandTagInfo', json.dumps(tag_dict))
    plLogger.LogInfo('GroupCommandTagInfo: ' + this_cmd.Get('GroupCommandTagInfo'))

    # Create the StmProtocolMix object...
    plLogger.LogInfo('Creating the protocol mix object...')
    proto_mix = ctor.Create("StmProtocolMix", project)
    this_cmd.Set('StmTemplateMix', proto_mix.GetObjectHandle())
    # If a MixTagName was specified, then tag the mix with it...
    if MixTagName:
        tag_utils.add_tag_to_object(proto_mix, MixTagName)

    # Copy the MixInfo into StmProtocolMix object...
    proto_mix.Set('MixInfo', MixInfo)

    # Load the MixInfo...
    err_str, mix_info = json_utils.load_json(MixInfo)
    if err_str != "":
        plLogger.LogInfo(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Directly configure all tagged commands in our hierarchy...
    plLogger.LogDebug('setting up commands in the group based on ' + str(tag_dict))

    plLogger.LogDebug('loading json from MixInfo: ' + str(MixInfo))
    num_rows = len(mix_info['components'])
    plLogger.LogDebug('Number of Rows: ' + str(num_rows))

    # Setup Row Iterator (pass in num of rows) - the While command's expression command
    iter_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['rowIterator']])[0]
    iter_cmd.Set('IterMode', 'STEP')
    iter_cmd.Set('StepVal', '1')
    iter_cmd.Set('ValueType', 'RANGE')
    iter_cmd.Set('MinVal', 0.0)
    iter_cmd.Set('MaxVal', (float(num_rows) - 1.0))

    # Pass table to configurator - this guy will configure other commands per iteration...
    conf_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['rowConfigurator']])[0]
    conf_cmd.Set('StmTemplateMix', proto_mix.GetObjectHandle())
    conf_cmd.Set('TagData', this_cmd.Get('GroupCommandTagInfo'))

    # Pass the StmProtocolMix to the CreateTemplateConfigCommand...
    ctc_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['templateConfigurator']])[0]
    ctc_cmd.Set('StmTemplateMix', proto_mix.GetObjectHandle())
    ctc_cmd.Set('AutoExpandTemplate', False)

    return True


def on_complete(failed_commands):
    plLogger = PLLogger.GetLogger("Methodology")
    this_cmd = get_this_cmd()
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()

    # We don't do anything if one of the hierarchy commands failed...
    if failed_commands is not None and len(failed_commands) > 0:
        err_str = "CreateTrafficMixCommand.on_complete(): " + \
            "No additional processing due to child command failure."
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    mix_hnd = this_cmd.Get("StmTemplateMix")
    mix = hnd_reg.Find(mix_hnd)
    err_str, mix_info = json_utils.load_json(mix.Get("MixInfo"))
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False
    portGroupList = this_cmd.GetCollection("PortGroupTagList")

    # Mix Info has list in same order as created, for Expand
    if (this_cmd.Get("AutoExpandTemplateMix")):
        cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand")
        cmd.Set("StmTemplateMix", mix_hnd)
        cmd.Set("DeviceCount", int(mix_info["deviceCount"]))
        cmd.SetCollection("PortGroupTagList", portGroupList)
        cmd.Execute()
        if cmd.Get("PassFailState") != "PASSED":
            err_str = "Failed to expand ProtocolMix: " + mix.Get("Name") + \
                " with handle " + str(mix_hnd) + ": " + cmd.Get("Status")
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            cmd.MarkDelete()
            return False
        cmd.MarkDelete()

    err_str, tag_dict = json_utils.load_json(
        this_cmd.Get('GroupCommandTagInfo'))
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
    mix_utils.on_complete_remove_tags([tag_name for tag_name in tag_dict])

    return True


def reset():
    return True


"""
Schema for TagInfo (for commands) looks like this:
{
  "type": "object",
  "properties": {
    "rowIterator": {"type": "string"},
    "rowConfigurator": {"type": "string"},
    "templateConfigurator": {"type": "string"},
  },
  "required": ["rowIterator", "rowConfigurator", "templateConfigurator"]
}
"""


def get_tag_info_schema():
    props = {}
    props["rowIterator"] = {"type": "string"}
    props["rowConfigurator"] = {"type": "string"}
    props["templateConfigurator"] = {"type": "string"}

    s_dict = {}
    s_dict["type"] = "object"
    s_dict["properties"] = props
    s_dict["required"] = ["rowIterator", "rowConfigurator",
                          "templateConfigurator"]
    return json.dumps(s_dict)
