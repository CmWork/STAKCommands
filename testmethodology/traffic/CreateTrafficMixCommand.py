from StcIntPythonPL import *
import json
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.template_mix_cmd_utils as mix_utils


PKG = 'spirent.methodology'
TPKG = 'spirent.methodology.traffic'


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


def validate(MixInfo, MixTagName, AutoExpandTemplateMix):
    # validate both tag list lengths equal
    return ''


def init():
    plLogger = PLLogger.GetLogger('methodology')
    this_cmd = get_this_cmd()

    # Check if the group is filled already.  If it is, don't do anything.
    cmd_list = this_cmd.GetCollection('CommandList')
    if len(cmd_list) > 0:
        plLogger.LogDebug('CreateTrafficMixCommand group is already ' +
                          'filled.  Skipping pre-filling in init().')
        return True

    mix_utils.init_create_hierarchy(this_cmd, hierarchy())
    return True


def run(MixInfo, MixTagName, AutoExpandTemplateMix):
    plLogger = PLLogger.GetLogger('methodology')
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    this_cmd = get_this_cmd()
    ctor = CScriptableCreator()

    # Validate the input MixInfo against its schema
    res = json_utils.validate_json(MixInfo, this_cmd.Get('MixInfoJsonSchema'))
    if res != '':
        plLogger.LogError(res)
        return False

    # Validate the hierarchy against our current command list...
    msg = mix_utils.run_validate_hierarchy(this_cmd, [hierarchy()])
    if msg != '':
        plLogger.LogError('Invalid Sequence: ' + msg)
        return False

    # Tag the commands in our command list according to our hierarchy information...
    tag_dict = mix_utils.run_tag_hierarchy(this_cmd, [hierarchy()])

    # Setup for property chaining / outputting the tag dictionary...
    this_cmd.Set('GroupCommandTagInfo', json.dumps(tag_dict))
    plLogger.LogInfo('GroupCommandTagInfo: ' + this_cmd.Get('GroupCommandTagInfo'))

    # Create the StmTrafficMix object...
    plLogger.LogInfo('Creating the traffic mix object...')
    mix = ctor.Create('StmTrafficMix', project)
    this_cmd.Set('StmTemplateMix', mix.GetObjectHandle())
    # If a MixTagName was specified, then tag the mix with it...
    if MixTagName:
        tag_utils.add_tag_to_object(mix, MixTagName)
    # Copy the entire MixInfo into StmTrafficMix object...
    mix.Set('MixInfo', MixInfo)

    # Load the MixInfo...
    err_str, mix_info = json_utils.load_json(MixInfo)
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Directly configure all tagged commands in our hierarchy...
    plLogger.LogDebug('setting up commands in the group based on ' + str(tag_dict))

    plLogger.LogDebug('loading json from MixInfo: ' + str(MixInfo))
    num_rows = len(mix_info['components'])
    plLogger.LogDebug('Number of Rows: ' + str(num_rows))

    # Pass table to configurator - this guy will configure other commands per iteration...
    conf_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['rowConfigurator']])[0]
    conf_cmd.Set('StmTemplateMix', mix.GetObjectHandle())
    conf_cmd.Set('TagData', this_cmd.Get('GroupCommandTagInfo'))

    # Pass the StmProtocolMix to the CreateTemplateConfigCommand...
    ctc_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['templateConfigurator']])[0]
    ctc_cmd.Set('StmTemplateMix', mix.GetObjectHandle())
    ctc_cmd.Set('AutoExpandTemplate', False)

    # Setup Row Iterator (pass in number of rows) - the While command's expression command...
    iter_cmd = tag_utils.get_tagged_objects_from_string_names([tag_dict['rowIterator']])[0]
    iter_cmd.Set('IterMode', 'STEP')
    iter_cmd.Set('StepVal', '1')
    iter_cmd.Set('ValueType', 'RANGE')
    iter_cmd.Set('MinVal', 0.0)
    iter_cmd.Set('MaxVal', (float(num_rows) - 1.0))

    return True


def on_complete(failed_commands):
    plLogger = PLLogger.GetLogger('Methodology')
    this_cmd = get_this_cmd()
    ctor = CScriptableCreator()

    # We don't do anything if one of the hierarchy commands failed...
    if failed_commands is not None and len(failed_commands) > 0:
        plLogger.LogError('CreateTrafficMixCommand.on_complete(): ' +
                          'No additional processing due to child command failure.')
        return False

    mix_hnd = this_cmd.Get("StmTemplateMix")
    hnd_reg = CHandleRegistry.Instance()
    mix = hnd_reg.Find(mix_hnd)
    err_str, mix_info = json_utils.load_json(mix.Get("MixInfo"))
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    if this_cmd.Get('AutoExpandTemplateMix'):
        cmd = ctor.CreateCommand(TPKG + ".ExpandTrafficMixCommand")
        cmd.Set("StmTemplateMix", mix_hnd)
        cmd.Set("Load", float(mix_info["load"]))
        cmd.Set("LoadUnit", mix_info["loadUnits"])
        cmd.Execute()
        if cmd.Get("PassFailState") != "PASSED":
            err_str = "Failed to expand TrafficMix: " + mix.Get("Name") + \
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
        return False
    mix_utils.on_complete_remove_tags([tag_name for tag_name in tag_dict])

    return True


def reset():
    return True
