from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import os
import re
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mmutils
import spirent.methodology.utils.json_utils as json_utils


ports = []


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(KeyValueJson):
    return ''


def run(KeyValueJson):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("begin.run.MethodologyGroupCommand")

    # Setup the command...
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    # Validate the major players...

    if project is None:
        plLogger.LogError("Invalid Project object.")
        return False

    # Begin processing...
    # Map the ExposedProperty objects by their keys...
    exposed_config = project.GetObject("ExposedConfig")
    if exposed_config is not None:
        exposed_property_map = {ep.Get('EPNameId'): ep for ep in
                                exposed_config.GetObjects('ExposedProperty')}

    # FIXME:
    # Do schema validation once we have a schema
    # Process key value JSON input structure
    err_str, json_dict = json_utils.load_json(KeyValueJson)
    if err_str != "":
        plLogger.LogError(err_str)
        return False

    for key in json_dict.keys():
        value = json_dict[key]

        # Ensure that the key can be found in the ExposedProperty map that we created above...
        if key not in exposed_property_map:
            plLogger.LogError("Exposed property for key '" + key + "' doesn't exist.")
            continue
        # Pull the ExposedProperty object for the key...
        exp_prop = exposed_property_map[key]

        # Get the object that the ExposedProperty object is related to. It doesn't
        # matter if it is the LoadTemplateCommand or any other object, because the
        # relationship will take us directly to the object.
        target = exp_prop.GetObject("Scriptable", RelationType("ScriptableExposedProperty"))
        if target is None:
            plLogger.LogError("ExposedProperty target is None for '" + key + "'")
            continue

        # pull the property name out of the ExposedProperty object...
        prop = exp_prop.Get("EPPropertyId").split(".")[-1].lower()

        class_name = target.GetType()
        prop_list = CMeta.GetProperties(class_name)
        if prop.lower() not in [prop_name.lower() for prop_name in prop_list]:
            plLogger.LogError("Property does not exist on " + class_name)
            continue
        prop_meta = CMeta.GetPropertyMeta(class_name, prop)

        if prop_meta["isCollection"]:
            try:
                # List should be a standard JSON list
                if isinstance(value, list):
                    val_list = [str(x) for x in value]
                    target.SetCollection(prop, val_list)
                else:
                    target.SetCollection(prop, [value])
            except ValueError:
                plLogger.LogError("Was not able to set collection property on " +
                                  prop + " to " + value)
        # elif type(value) is dict: ... we will treat this as a string...
        else:
            target.Set(prop, value)

    plLogger.LogDebug("end.run.MethodologyGroupCommand")
    return True


def on_complete(failed_commands):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("begin.on_complete.MethodologyGroupCommand")

    # At this point, the test is finished.
    if len(ports) > 0:
        detach_ports(ports)

    plLogger.LogDebug("end.on_complete.MethodologyGroupCommand")
    return True


def reset():
    # plLogger = PLLogger.GetLogger("methodology")
    # plLogger.LogDebug("MethodologyGroupCommand.reset()")
    return True


def split_key_value_pair(key_value):
    p = re.findall("([^=]*)=(.*)", key_value)
    return p[0][0], p[0][1]


def detach_ports(port_hnd_list):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("begin.detach_ports.MethodologyGroupCommand")

    if len(port_hnd_list) > 0:
        ctor = CScriptableCreator()
        detach_cmd = ctor.CreateCommand("DetachPortsCommand")
        detach_cmd.Set("PortList", port_hnd_list)
        detach_cmd.Execute()
        detach_cmd.MarkDelete()
    plLogger.LogDebug("end.detach_ports.MethodologyGroupCommand")
    return


def load_xmlroot_from_file(filename):
    # FIXME: This needs to move into an XML util file...
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogDebug("begin.load_xmlroot_from_file.MethodologyGroupCommand")
    file_path = filename
    if not os.path.isabs(file_path):
        abs_file_name = mmutils.find_template_across_common_paths(file_path)
        if abs_file_name != '':
            file_path = abs_file_name

    if not os.path.isfile(file_path):
        plLogger.LogError("ERROR: Failed to find file '" + filename + "'")
        return None

    # return etree.parse(file_path)
    with open(file_path) as f:
        return etree.fromstring(f.read())
