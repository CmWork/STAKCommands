from StcIntPythonPL import *
import json
import os
import sys
from spirent.core.utils.scriptable import AutoCommand
from collections import OrderedDict
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils
from spirent.methodology.manager.utils.estimation_utils import EstimationUtils
import spirent.methodology.utils.json_utils as json_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


# Load the meta json file after validating against the schema
def get_meta_json_file_dict(json_path):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.get_meta_json_file_dict.RunMethodologyTestCommand')

    this_cmd = get_this_cmd()
    meta_json = None

    try:
        # Open the json file
        json_string = None
        file_path = os.path.abspath(json_path)
        if not os.path.exists(file_path):
            return None, "File {} does not exist".format(file_path)
        with open(file_path, "r") as jsonFile:
            json_string = jsonFile.read()
        if not json_string:
            return None, "Error reading methodology json file"
    except:
        return None, 'Invalid methodology JSON file: {}'.format(json_path)

    # Validate against the schema
    res = json_utils.validate_json(json_string,
                                   this_cmd.Get("InputJsonSchema"))
    if res != "":
        err_str = "Methodology JSON is invalid or does not conform to the " + \
            "schema: " + res
        return None, err_str

    # Load the json if it passes schema validation
    err_str, meta_json = json_utils.load_json(json_string)
    if err_str != "":
        return None, err_str

    plLogger.LogDebug('end.get_meta_json_file_dict.RunMethodologyTestCommand')
    return meta_json, ""


# Pulls out the list of keys and values from the methodology json
def parse_meta_json_keys_values(meta_json):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.parse_meta_json_keys_values.RunMethodologyTestCommand')

    key_val_dict = OrderedDict()
    gui_key_val_dict = OrderedDict()

    # Get property_groups, which has the test properties
    if 'property_groups' not in meta_json:
        plLogger.LogWarn('No property_groups defined in methodology JSON')
        return key_val_dict, gui_key_val_dict
    property_groups = meta_json['property_groups']

    for property_group in property_groups:
        # Get the test_properties if it exists
        if 'test_properties' not in property_group:
            continue
        test_properties = property_group['test_properties']

        for test_property in test_properties:
            # Get the property id and value if it exists
            if 'prop_id' not in test_property or 'property_value' not in test_property:
                continue

            prop_id = test_property['prop_id']
            property_value = test_property['property_value']
            key_val_dict[prop_id] = property_value

            # Determine if its a gui-only property (MetaMan.W_GUI_ONLY)
            gui_only = test_property.get('gui_only')
            if gui_only is not None and gui_only:
                gui_key_val_dict[prop_id] = property_value

    plLogger.LogDebug('end.parse_meta_json_keys_values.RunMethodologyTestCommand')
    return key_val_dict, gui_key_val_dict


# Pulls out of the list of ports from the methodology json
def generate_tagged_ports(input_dict):
    '''
    Function takes an input dictionary, creates ports and tags them as
    specified in the input dictionary.

    Input: input_dict with following structure:
    {
        "port_groups": [
            {
                "prop_id": "ExposedPropertyName",
                "name": "Human-readable Name",
                "ports": [
                    {
                        "location": "1.1.1.1/1/1"
                    }
                ]
            }
        ]
    }
    Output: Returns a list of port object handles and a boolean indicating if
    any of the ports created were marked offline.
    '''
    logger = PLLogger.GetLogger('methodology')
    logger.LogDebug('begin generate_tagged_ports')
    project = CStcSystem.Instance().GetObject('Project')
    ctor = CScriptableCreator()

    # Create exposed property dictionary
    exp_config = project.GetObject('ExposedConfig') if project is not None else None
    if exp_config is None:
        logger.LogError("No exposed config object found")
        return [], False, "No exposed config object found"
    ep_dict = {ep.Get('EPNameId'): ep for ep in exp_config.GetObjects('ExposedProperty')}

    pg_list = input_dict.get('port_groups')
    if not pg_list:
        logger.LogError("Input missing required port_groups section")
        return [], False, "Input missing required port_groups section"
    offline = False
    port_handle_list = []
    for pg in pg_list:
        pg_id = pg.get('prop_id')
        if not pg_id:
            logger.LogError("Port group missing required prop_id")
            return [], False, "Port group missing required prop_id"
        pg_name = pg.get('name', pg_id)
        port_list = pg.get('ports')
        if not port_list:
            logger.LogError("Port group {} has empty port list".format(pg_name))
            return [], False, "Port group {} has empty port list"
        loc_list = [p.get('location') for p in port_list]
        if None in loc_list:
            logger.LogError("Port group {} is missing location "
                            "attribute".format(pg_name))
            return [], False, "Port group {} is missing location attribute".format(pg_name)
        ep = ep_dict.get(pg_id)
        if ep is None:
            logger.LogError("Exposed property missing: {}".format(pg_id))
            return [], False, "Exposed property missing: {}".format(pg_id)
        pg_tag = ep.GetObject('Tag', RelationType('ScriptableExposedProperty'))
        if pg_tag is None:
            logger.LogError("Tag key missing: {}".format(pg_id))
            return [], False, "Tag key missing: {}".format(pg_id)
        for idx, loc in enumerate(loc_list, start=1):
            port = ctor.Create('Port', project)
            port.Set('Location', loc)
            port.Set('Name', "{} {}".format(pg_name, idx))
            port.AddObject(pg_tag, RelationType('UserTag'))
            port_handle_list.append(port.GetObjectHandle())

        # Determine if this port group should not be brought online
        bring_online = pg.get('bring_online')
        if bring_online is not None:
            offline = offline or not bring_online

    logger.LogDebug('end generate_tagged_ports')
    return port_handle_list, offline, ""


def load_config(test_case, project_handle):
    # Comment from LoadTestMethodologyCommand.py:
    # If the ParentConfig is set to empty string (""), then the GUI works and TCL crashes.
    # If the ParentConfig is set to project, then the GUI crashes and TCL works
    with AutoCommand('LoadFromXml') as load_cmd:
        load_cmd.Set('FileName',
                     os.path.join(test_case.Get('Path'),
                                  mgr_const.MM_SEQUENCER_FILE_NAME))
        load_cmd.Set("ParentConfig", project_handle)
        load_cmd.Execute()
    return


# So we can Mock this function in the unit test
def set_active_test_case(test_case):
    mm_utils.set_active_test_case(test_case)
    return


def attach_ports(port_hnd_list):
    if len(port_hnd_list) > 0:
        with AutoCommand('AttachPortsCommand') as attach_cmd:
            attach_cmd.SetCollection('PortList', port_hnd_list)
            attach_cmd.Set('AutoConnect', True)
            attach_cmd.Set('ContinueOnFailure', True)
            attach_cmd.Execute()
    return


# FIXME:
# Combine with RunPyScriptCommand and move this to a library
def get_script_path(script_name):
    abs_path = mm_utils.find_script_across_common_paths(script_name + '.py')
    if abs_path == '':
        return ''
    return os.path.split(abs_path)[0]


def run_the_proc_func(proc_func, input_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.run_the_proc_func.RunMethodologyTestCommand.')
    script_name = proc_func["script_filename"]
    entry_fn = proc_func["entry_function"]
    mod_name = os.path.splitext(script_name)[0]
    plLogger.LogDebug('mod_name: ' + str(mod_name))
    script_path = get_script_path(mod_name)
    if script_path is '':
        return None, 'Failed to find script: ' + script_name
    sys.path.append(script_path)

    # Import the module and reload it if it has already been imported
    exec 'import ' + mod_name
    exec 'reload(' + mod_name + ')'

    # Run the external processing function
    output_dict = OrderedDict()
    err_msg = ''
    exec 'output_dict, err_msg = ' + mod_name + '.' + entry_fn + \
        '(' + str(input_dict) + ')'
    plLogger.LogDebug('external proc func output: ' + str(output_dict))

    # Delete module from memory
    exec 'del ' + mod_name

    if err_msg != '':
        err_str = 'External script: ' + mod_name + ' running ' + \
                  entry_fn + ' failed with: ' + err_msg + \
                  '  Input was: ' + str(input_dict)
        return None, err_str
    return output_dict, ""


def substitute_prop_ids(data, key_val_dict):
    # First, let's look to see if data is a dictionary...
    if type(data) is dict:
        # Get all dictionary items as a list of (k,v) tuples...
        kv_list = data.items()
        # for each key-value, recursively process on the value...
        for k, v in kv_list:
            newv = substitute_prop_ids(v, key_val_dict)
            # if a substitute value came back, then use it...
            if newv is not None:
                data[k] = newv
    # Next, let's see if data is a list (of dictionaries)...
    elif type(data) is list:
        # Recursively process on each list item...
        for i in data:
            # We assume the item must be a dictionary...
            substitute_prop_ids(i, key_val_dict)
    # Finally, we assume the value is either a constant or a prop_id.
    # If a prop_id, then it should be in the key_val_dict, and we pull
    # and return the substitution value from key_val_dict.
    elif data in key_val_dict:
        return key_val_dict[data]
    # We do not have any substitution value to return...
    return None


def map_var_to_key(var_to_key_maps):
    d = {}
    for var_key in var_to_key_maps:
        # The schema guarantees one of these cases...
        if "src_prop_id" in var_key and "script_input_key" in var_key:
            d[var_key["script_input_key"]] = var_key["src_prop_id"]
        elif "dict" in var_key and "script_input_key" in var_key:
            d[var_key["script_input_key"]] = var_key["dict"]
        elif "constant" in var_key and "script_input_key" in var_key:
            d[var_key["script_input_key"]] = var_key["constant"]
        elif "ep_key" in var_key and "script_output_key" in var_key:
            d[var_key["script_output_key"]] = var_key["ep_key"]
    return d


def process_functions(meta_json, key_val_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.process_functions.RunMethodologyTestCommand.')
    # Skip this function if there are no processing functions...
    if "processing_functions" not in meta_json:
        return ""
    # Process each function that is defined...
    for proc_func in meta_json["processing_functions"]:
        # Find the output var-to-key relations...
        output_map = map_var_to_key(proc_func["output"])
        input_map = map_var_to_key(proc_func["input"])
        # Substitute values for keys wherever keys are found (matched)...
        substitute_prop_ids(input_map, key_val_dict)
        # Now run the function with the input dictionary...
        output_dict, err_str = run_the_proc_func(proc_func, input_map)
        if err_str:
            return err_str
        # For each var in the output_dict, if it is in the output_map (that is,
        # the script_output_key in the output array), then use the mapped EPKey to save
        # the result in key_val_dict...
        for var in output_dict:
            if var in output_map:
                key_val_dict[output_map[var]] = output_dict[var]
                plLogger.LogDebug("Pf: adding " + var + ":" + output_dict[var])
    return ""


def validate(TestCaseKey, StmTestCase, MethodologyKey, MethodologyJson, EnableResourceCheck):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.validate.RunMethodologyTestCommand.')

    if TestCaseKey:
        # Check if test case key exists in installed methodologies
        test_case_handle, err_str = mm_utils.get_test_case_from_key(TestCaseKey)
        return err_str
    elif StmTestCase:
        hnd_reg = CHandleRegistry.Instance()
        test_case = hnd_reg.Find(StmTestCase)
        if test_case is None or not test_case.IsTypeOf('StmTestCase'):
            plLogger.LogError('Was unable to find StmTestCase with handle ' +
                              str(StmTestCase) + ' in the system.')
            return 'Could not find StmTestCase'
    else:
        # Must specify a key and json
        if not MethodologyKey or not MethodologyJson:
            return 'Must specify a TestCaseKey, StmTestCase or MethodologyKey and MethodologyJson'

        # Validate against the schema
        this_cmd = get_this_cmd()
        res = json_utils.validate_json(MethodologyJson,
                                       this_cmd.Get("InputJsonSchema"))
        if res != "":
            return "Methodology JSON is invalid or does not conform to the schema: " + res

        # Load the json if it passes schema validation
        err_str, meth_json = json_utils.load_json(MethodologyJson)
        if err_str != "":
            return err_str

        # Check the MethodologyKey matches the meth key in the json
        if MethodologyKey != meth_json['methodology_key']:
            return "Methodology Key does not match the methodology_key in the JSON"

    plLogger.LogDebug('end.validate.RunMethodologyTestCommand')
    return ''


def run(TestCaseKey, StmTestCase, MethodologyKey, MethodologyJson, EnableResourceCheck):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.run.RunMethodologyTestCommand')

    this_cmd = get_this_cmd()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    if not TestCaseKey and not StmTestCase:
        # We're going to create a test case using the json
        cmd = ctor.CreateCommand("spirent.methodology.manager.CreateMethodologyTestCaseCommand")
        cmd.Set("MethodologyJson", MethodologyJson)
        err_str = ""
        try:
            cmd.Execute()
        except Exception, e:
            err_str = str(e)
        result = cmd.Get('PassFailState')
        TestCaseKey = cmd.Get("TestCaseKey")
        cmd.MarkDelete()

        # Verify create command passed
        if err_str or result is None or result != 'PASSED':
            err_str = "Failed to create methodology test case. " + err_str
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

    if TestCaseKey:
        # Get test case from installed methodologies
        StmTestCase, err_str = mm_utils.get_test_case_from_key(TestCaseKey)
        if err_str:
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False

    # Get the StmTestCase object
    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None or not test_case.IsTypeOf('StmTestCase'):
        err_str = 'Was unable to find StmTestCase with handle ' + \
                  str(StmTestCase) + ' in the system.'
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Get the StmMethodology so we can get the meth key
    stm_meth = test_case.GetObject("StmMethodology", RelationType("ParentChild", 1))
    if stm_meth is None:
        err_str = 'Unable to get valid StmMethodology object from StmTestCase'
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    json_path = os.path.join(test_case.Get('Path'), mgr_const.MM_META_JSON_FILE_NAME)
    methodology_key = stm_meth.Get('MethodologyKey')
    test_case_key = test_case.Get('TestCaseKey')
    plLogger.LogDebug('json_path: ' + str(json_path))
    plLogger.LogDebug('test case name: ' + test_case.Get('Name'))
    plLogger.LogDebug('test case key: ' + test_case_key)
    plLogger.LogDebug('methodology key: ' + methodology_key)

    # Set the TestCaseKey output param
    this_cmd.Set("OutputTestCaseKey", test_case_key)

    # Load the config
    load_config(test_case, project.GetObjectHandle())

    # Since loading resets the system, retrieve the test case using the key
    cmd = ctor.CreateCommand("spirent.methodology.manager.GetTestMethodologyAndTestCaseCommand")
    cmd.Set("MethodologyKey", methodology_key)
    cmd.Set("TestCaseKey", test_case_key)
    cmd.Execute()
    StmTestCase = cmd.Get("StmTestCase")
    cmd.MarkDelete()

    # Get the StmTestCase
    if not StmTestCase:
        err_str = 'StmTestCase handle is empty'
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None or not test_case.IsTypeOf('StmTestCase'):
        err_str = 'Was unable to find StmTestCase with handle ' + \
                  str(StmTestCase) + ' in the system.'
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Set the active test case
    set_active_test_case(test_case)

    # Load the json file and get the json as a dict
    meta_json, err_str = get_meta_json_file_dict(json_path)
    if meta_json is None:
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    # Parse the json for the keys and values
    key_val_dict, gui_key_val_dict = parse_meta_json_keys_values(meta_json)

    # Parse all processing functions, including those that use dictionary inputs...
    err_str = process_functions(meta_json, key_val_dict)
    if err_str:
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    plLogger.LogDebug('key_val_dict (json): ' + json.dumps(key_val_dict))

    # Remove the gui-only keys from key_val_dict
    for key in gui_key_val_dict.keys():
        if key in key_val_dict.keys():
            key_val_dict.pop(key)
    plLogger.LogDebug("key_val_dict without gui only keys (json): " +
                      json.dumps(key_val_dict))

    # Create the ports (they will be tagged appropriately)...
    port_list, offline_detected, err_str = generate_tagged_ports(meta_json)
    if err_str:
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    if EnableResourceCheck and not offline_detected:
        estimationUtils = EstimationUtils(test_case)
        output_json = estimationUtils.get_estimates_json()
        plLogger.LogDebug('output_json: ' + output_json)
        tie_pkg = 'spirent.testintel'

        result = None
        verdict = []
        with AutoCommand(tie_pkg + '.ScalingValidatePortsCommand') as tie_cmd:
            tie_cmd.Set('Profile', output_json)
            try:
                tie_cmd.Execute()
            except:
                pass
            result = tie_cmd.Get('PassFailState')
            try:
                verdict = json.loads(tie_cmd.Get('Verdict'))
            except:
                pass
        plLogger.LogInfo('Validation Verdict: {}'.format(verdict))
        if result is None or result != 'PASSED':
            if result is None:
                plLogger.LogError('ERROR: Unable to create an instance of ' +
                                  tiepkg + '.ScalingValidatePortsCommand.')
            else:
                fail_list = []
                for ent in verdict:
                    if 'portLocations' not in ent:
                        continue
                    for loc in ent['portLocations']:
                        if not loc['confidence']:
                            out_fmt = 'Port {} can not run test: {}'
                            out = out_fmt.format(loc['location'],
                                                 loc['reason'])
                            fail_list.append(out)
                        elif loc['confidence'] < 100.0:
                            out_fmt = 'Port {} may run with {}% confidence, ' + \
                                'disable pre-run resource validation check ' + \
                                'to proceed: {}'
                            out = out_fmt.format(loc['location'],
                                                 loc['confidence'], loc['reason'])
                            fail_list.append(out)
                this_cmd = hnd_reg.Find(__commandHandle__)
                this_cmd.Set('Status', '\n'.join(fail_list))
            # Common exit point after setting failure
            return False

    # Configure the MethodologyGroupCommand
    sequencer = stc_sys.GetObject('Sequencer')
    cmd_list = sequencer.GetCollection('CommandList')
    for cmd_hnd in cmd_list:
        cmd = hnd_reg.Find(cmd_hnd)
        if cmd is None:
            continue

        if cmd.IsTypeOf("spirent.methodology.manager.MethodologyGroupCommand"):
            cmd.Set("KeyValueJson", json.dumps(key_val_dict))
            break

    # If any of the ports were offline ports, then assume a test config
    # that isn't to connect to chassis (e.g., a unit test).
    if not offline_detected:
        attach_ports(port_list)

    plLogger.LogDebug('end.run.RunMethodologyTestCommand')
    return True


def reset(StmMethodology):
    return True
