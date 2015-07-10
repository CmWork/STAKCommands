from StcIntPythonPL import *
import os.path
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.txml_utils import MetaManager, get_unique_property_id
from utils.sequencer_utils import SequenceInfo
from utils.sequencer_utils import MethodologyGroupCommandUtils as tlgc_utils
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


def validate(MethodologyName,
             MethodologyKey,
             MethodologyDescription,
             MethodologyLabelList,
             FeatureIdList,
             MinPortCount,
             MaxPortCount,
             PortSpeedList,
             EditableParams):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate.PublishMethodologyCommand")

    stc_sys = CStcSystem.Instance()

    if stc_sys is None:
        return 'Invalid internal system object'
    project = stc_sys.GetObject("Project")

    if project is None:
        return 'Invalid internal project'

    if MinPortCount > MaxPortCount:
        return 'For number of ports, the minimum is greater than the maximum'

    port_list = project.GetObjects("Port")

    if len(port_list) < MinPortCount:
        return 'Number of ports in test is less than the minimum required'

    if len(port_list) > MaxPortCount:
        return 'Number of ports in test is greater than the maximum allowed'

    if MethodologyKey is None:
        return 'MethodologyKey MUST be specified.'

    hnd_reg = CHandleRegistry.Instance()

    # Get this command
    this_cmd = hnd_reg.Find(__commandHandle__)

    if this_cmd.Get("MethodologyName") == "":
        return "Require MethodologyName"

    plLogger.LogDebug("end.validate.PublishMethodologyCommand")
    return ''


def config_sequencer_properties():
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    sequencer.Set("ErrorHandler", "STOP_ON_ERROR")


# Add ExposedProperty objects for the Port objects
def expose_port_locations():
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.expose_port_locations.PublishMethodologyCommand")

    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    project = CStcSystem.Instance().GetObject("Project")
    if project is None:
        return
    exp_conf = project.GetObject("ExposedConfig")
    if exp_conf is None:
        exp_conf = ctor.Create("ExposedConfig", project)
    if exp_conf is None:
        plLogger.LogWarn("WARNING: Could not create ExposedConfig object")
        return
    port_list = project.GetObjects("Port")

    # BLL objects (or proxy objects) don't appear to be inserted properly.  The
    # python "in" operator can't distinguish the objects.  To get around this,
    # the int handles have to be compared and objects found later.
    tag_handle_list = []

    for port in port_list:
        # For ports with tags, expose both the port location and the tag name
        # For ports without tags, expose just the port location
        if port is None:
            continue
        plLogger.LogDebug(" process port: " + port.Get("Name"))
        exp_prop = ctor.Create("ExposedProperty", exp_conf)
        unique_id = get_unique_property_id(port, "Location")
        plLogger.LogDebug(" port unique id: " + unique_id)
        exp_prop.Set("EPNameId", unique_id)
        exp_prop.Set("EPClassId", "Port")
        exp_prop.Set("EPPropertyId", "Port.Location")
        exp_prop.AddObject(port, RelationType("ScriptableExposedProperty"))

        port_tag_list = port.GetObjects("Tag", RelationType("UserTag"))
        if port_tag_list > 0:
            for port_tag in port_tag_list:
                plLogger.LogDebug(" process tag found on port: " + port_tag.Get("Name"))
                if port_tag.GetObjectHandle() not in tag_handle_list:
                    tag_handle_list.append(port_tag.GetObjectHandle())

    plLogger.LogDebug("tag_handle_list: " + str(tag_handle_list))

    # Turn the handle list back into an object list
    tag_list = []
    for tag_handle in tag_handle_list:
        tag = hnd_reg.Find(tag_handle)
        if tag is None:
            continue
        tag_list.append(tag)
        plLogger.LogDebug(" exposed tag: " + tag.Get("Name"))
        exp_prop = ctor.Create("ExposedProperty", exp_conf)
        tag_id = get_unique_property_id(tag, "Name")
        plLogger.LogDebug(" unique_id: " + tag_id)
        exp_prop.Set("EPNameId", tag_id)
        exp_prop.Set("EPClassId", "Tag")
        exp_prop.Set("EPPropertyId", "Scriptable.Name")
        exp_prop.AddObject(tag, RelationType("ScriptableExposedProperty"))

    plLogger.LogDebug("end.expose_port_locations.PublishMethodologyCommand")
    return tag_list


def run(MethodologyName,
        MethodologyKey,
        MethodologyDescription,
        MethodologyLabelList,
        FeatureIdList,
        MinPortCount,
        MaxPortCount,
        PortSpeedList,
        EditableParams):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.PublishMethodologyCommand")

    ctor = CScriptableCreator()
    if ctor is None:
        plLogger.LogError("Internal error: Could not get ctor")
        return
    stc_sys = CStcSystem.Instance()
    if stc_sys is None:
        plLogger.LogError("Internal error: Could not get stc_sys")
        return
    project = stc_sys.GetObject("Project")
    if project is None:
        plLogger.LogError("Internal error: Could not get project")
        return
    sequencer = stc_sys.GetObject("Sequencer")
    if sequencer is None:
        plLogger.LogError("Internal error: Could not get sequencer")
        return
    port_tag_list = expose_port_locations()
    cmd_list = sequencer.GetCollection("CommandList")

    # Write profile-based test config to special sections in the TXML
    si = SequenceInfo()
    is_profile_based_test = si.validate_and_load_profile_based_sequence(cmd_list)
    if is_profile_based_test:
        plLogger.LogDebug("Publish a Profile-Based Test!")
    else:
        plLogger.LogDebug("Publish a non-Profile-Based Test!")
        si = None

    exposedConfig = project.GetObject("ExposedConfig")
    exposedProperties = None
    if exposedConfig is not None:
        exposedProperties = exposedConfig.GetObjects("ExposedProperty")

    # Create the directory where the methodology will be published
    test_meth_test_dir = meth_man_utils.methodology_mkdir(MethodologyKey)
    if not test_meth_test_dir:
        plLogger.LogError("There was a problem creating methodology directory for " +
                          MethodologyName + " using as key " + MethodologyKey)
        return False
    path_plus_file_name = os.path.join(test_meth_test_dir,
                                       mgr_const.MM_META_FILE_NAME)

    config_sequencer_properties()
    tlgc_utils.insert_top_level_group_command()
    tlgc_utils.set_sequenceable_properties(sequencer.GetCollection("CommandList"), False)

    # Save everything to XML/TCC
    sequencer_file_path = os.path.join(test_meth_test_dir, mgr_const.MM_SEQUENCER_FILE_NAME)
    save_cmd = ctor.CreateCommand("SaveAsXml")
    save_cmd.Set("FileName", sequencer_file_path)
    save_cmd.Execute()
    save_cmd.MarkDelete()

    # FIXME:
    # The Methodology's key should be passed into generate_txml_file but
    # is not being done so at the moment.  The key should be passed into
    # this command.
    # Create the TXML file
    if not MetaManager.generate_txml_file(exposedProperties,
                                          MethodologyName,
                                          MethodologyDescription,
                                          MethodologyKey,
                                          port_tag_list,
                                          MethodologyLabelList,
                                          FeatureIdList,
                                          si,
                                          MinPortCount,
                                          MaxPortCount,
                                          PortSpeedList,
                                          EditableParams,
                                          path_plus_file_name,
                                          sequencer_file_path):
        plLogger.LogError("Empty meta data file is detected. Abort Publish operation")
        # Revert sequencer changes since we're aborting publish operation
        tlgc_utils.remove_top_level_group_command()
        tlgc_utils.set_sequenceable_properties(sequencer.GetCollection("CommandList"), True)
        return False

    # Add BLL objects
    meth_man_utils.build_test_methodology(test_meth_test_dir, use_txml=True)

    plLogger.LogDebug("end.run.PublishMethodologyCommand")
    return True


def reset():
    return True
