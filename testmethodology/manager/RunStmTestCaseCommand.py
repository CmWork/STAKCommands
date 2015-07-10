from StcIntPythonPL import *
# import ast
import json
import os
import sys
import xml.etree.ElementTree as etree
from spirent.core.utils.scriptable import AutoCommand
from collections import OrderedDict
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mgr_const
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils
import spirent.methodology.manager.utils.txml_utils as txml_utils
# from utils.validator import validate_command_on_disk
from spirent.methodology.manager.utils.estimation_utils import EstimationUtils
import spirent.methodology.utils.json_utils as json_utils


# Turn the txml_file into an element tree and return the root
def get_txml_file_root(txml_path):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.get_txml_file_root.RunStmTestCaseCommand')
    txml_root = None
    try:
        element_tree = etree.parse(os.path.abspath(txml_path))
        if element_tree is not None:
            txml_root = element_tree.getroot()
    except:
        plLogger.LogError('Invalid TXML file: {}'.format(txml_path))
        return None

    plLogger.LogDebug('end.get_txml_file_root.RunStmTestCaseCommand')
    return txml_root


# Pulls out the list of keys and values from the TXML (element tree)
def parse_txml_keys_values(txml_root):
    # FIXME:
    # Break this up into <testResources> and <wizard> sections later
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.parse_txml_keys_values.RunStmTestCaseCommand')
    MetaMan = txml_utils.MetaManager
    key_val_dict = OrderedDict()
    gui_key_val_dict = OrderedDict()
    wizard_root = txml_root.find('.//' + MetaMan.W_WIZARD)
    if wizard_root is None:
        plLogger.LogError('Could not find the <' + MetaMan.W_WIZARD +
                          '> tag in the TXML')
        return False
    for child in wizard_root:
        if child.tag != MetaMan.W_PAGE:
            plLogger.LogWarn('Found an unknown element with tag: ' +
                             child.tag +
                             ' under the <' + MetaMan.W_WIZARD +
                             '> node in the TXML.' +
                             '  Skipping it.')
            continue
        group_ele_list = child.findall('.//' + MetaMan.W_GROUP)
        for group_ele in group_ele_list:
            prop_ele_list = group_ele.findall('.//' + MetaMan.W_PROPERTY)
            for prop_ele in prop_ele_list:
                # Keep track of the GUI only parameters separately
                # as they aren't passed to the MethodologyGroupCommand
                # but they might be needed by the TXML processing
                # functions.
                gui_only = prop_ele.get(MetaMan.W_GUI_ONLY)
                obj_prop_id = prop_ele.get(MetaMan.W_ID)

                # If there are <data> elements, this property is actually
                # a table.  Collect the <data> elements into a list
                data_ele_list = prop_ele.findall(".//" + MetaMan.W_DATA)
                val = None
                if len(data_ele_list):
                    val = []
                    for data_ele in data_ele_list:
                        val.append(data_ele.text)
                    key_val_dict[obj_prop_id] = val
                else:
                    val = prop_ele.get(MetaMan.W_VALUE)
                    key_val_dict[obj_prop_id] = str(val)
                if gui_only is not None and gui_only == 'true':
                    gui_key_val_dict[obj_prop_id] = str(val)
    plLogger.LogDebug('end.parse_txml_keys_values.RunStmTestCaseCommand')
    return key_val_dict, gui_key_val_dict


# Pulls out the list of ports and port group tags from the TXML (element tree)
def parse_txml_port_groups(txml_root):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.parse_txml_port_groups.RunStmTestCaseCommand')
    port_group_dict = OrderedDict()
    MetaMan = txml_utils.MetaManager
    test_res_ele = txml_root.find('.//' + MetaMan.TEST_RESOURCES)
    if test_res_ele is None:
        plLogger.LogError('Could not find a <' + MetaMan.TEST_RESOURCES +
                          '> in the TXML')
        return None
    port_group_list = test_res_ele.findall('.//' + MetaMan.TR_PORT_GROUP)
    for port_group in port_group_list:
        if port_group.tag != MetaMan.TR_PORT_GROUP:
            plLogger.LogWarn('Skipping element ' + port_group_ele.tag +
                             ' in the TXML')
            continue
        port_group_id = port_group.get('id')
        port_list = port_group.findall('.//' + MetaMan.TR_PORT)
        loc_list = []
        for port_ele in port_list:
            attr_ele_list = port_ele.findall('.//' + MetaMan.TR_ATTR)
            for attr_ele in attr_ele_list:
                if (attr_ele.get(MetaMan.TR_NAME) == MetaMan.TR_LOCATION):
                    loc_list.append(attr_ele.get(MetaMan.TR_VALUE))
        port_group_dict[port_group_id] = loc_list
    plLogger.LogDebug('port_group_dict: ' + str(port_group_dict))
    plLogger.LogDebug('end.parse_txml_port_groups.RunStmTestCaseCommand')
    return port_group_dict


# Pulls out the TXML processing functions
# Input XML:
#  <processingFunction id="procFunc1"
#                      scriptFile="txmlProcessingFunctions.py"
#                      entryFunction="config_prop_modifier_xml">
#    <input srcId="East.Ipv4AddrStart" scriptVarName="Start" />
#    <input srcId="East.Ipv4AddrStep" scriptVarName="Step" />
#    <input scriptVarName="ObjName" defaultValue="Ipv4If" />
#    <input scriptVarName="PropName" defaultValue="Address" />
#    <output scriptVarName="ModInfo"
#            epKey="<exposed_prop_ep_name_id>" />
#  </processingFunction>
#
# Output dictionary:
# pf_dict["id_list"] = ["procFunc1"]
# pf_dict["pf1"]["script"] = "script.py"
# pf_dict["pf1"]["entry_fn"] = "run"
# pf_dict["pf1"]["input_id_list"] = ["in_1", "in_2", "in_3", "in_4"]
# pf_dict["pf1"]["output_id_list"] = ["out_1"]
# pf_dict["pf1"]["in_1"]["src_id"] = "East.Ipv4AddrStart"
# pf_dict["pf1"]["in_1"]["script_var"] = "Start"
# pf_dict["pf1"]["in_2"]["src_id"] = "East.Ipv4AddrStep"
# pf_dict["pf1"]["in_2"]["script_var"] = "Step"
# pf_dict["pf1"]["in_3"]["script_var"] = "ObjName"
# pf_dict["pf1"]["in_3"]["default"] = "Ipv4If"
# pf_dict["pf1"]["in_4"]["script_var"] = "PropName"
# pf_dict["pf1"]["in_4"]["default"] = "Address"
# pf_dict["pf1"]["out_1"]["script_var"] = "ModInfo"
# pf_dict["pf1"]["out_1"]["ep_key"] = "<exposed_prop_ep_name_id>"
#
# Note: Input and Output ids are autogenerated.
def parse_txml_proc_funcs(txml_root):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('RunStmTestCaseCommand.parse_txml_proc_funcs.begin')
    MetaMan = txml_utils.MetaManager
    pf_dict = OrderedDict()
    pf_dict['id_list'] = []
    proc_funcs_ele = txml_root.find('.//' + MetaMan.P_PROC_FUNCS)
    if proc_funcs_ele is None:
        return pf_dict
    for proc_func_ele in proc_funcs_ele:
        if proc_func_ele.tag != MetaMan.P_PROC_FUNC:
            plLogger.LogWarn('(parse_txml_proc_funcs) Skipping element '
                             + proc_func_ele.tag +
                             ' in the TXML')
            continue
        fn_id = proc_func_ele.get(MetaMan.P_ID)
        script_file = proc_func_ele.get(MetaMan.P_SCRIPT_FILE)
        entry_fn = proc_func_ele.get(MetaMan.P_ENTRY_FUNC)
        pf_dict['id_list'].append(fn_id)
        pf_dict[fn_id] = {}
        pf_dict[fn_id]['script'] = script_file
        pf_dict[fn_id]['entry_fn'] = entry_fn
        pf_dict[fn_id]['input_id_list'] = []
        pf_dict[fn_id]['output_id_list'] = []
        curr_in_id = 1
        curr_out_id = 1

        for data_ele in proc_func_ele:
            plLogger.LogDebug('data_ele: ' + str(data_ele))
            if data_ele.tag == MetaMan.P_INPUT:
                plLogger.LogDebug('input')
                in_id = 'in_' + str(curr_in_id)
                curr_in_id = curr_in_id + 1
                script_var = data_ele.get(MetaMan.P_SCRIPT_VAR_NAME)
                src_id = data_ele.get(MetaMan.P_SRC_ID)
                default = data_ele.get(MetaMan.P_DEFAULT)

                plLogger.LogDebug(' -> in_id: ' + str(in_id))
                pf_dict[fn_id]['input_id_list'].append(in_id)
                pf_dict[fn_id][in_id] = {}
                pf_dict[fn_id][in_id]['src_id'] = src_id
                pf_dict[fn_id][in_id]['default'] = default
                pf_dict[fn_id][in_id]['script_var'] = script_var

            elif data_ele.tag == MetaMan.P_OUTPUT:
                plLogger.LogDebug('output')
                out_id = 'out_' + str(curr_out_id)
                curr_out_id = curr_out_id + 1
                ep_key = data_ele.get(MetaMan.P_EP_KEY)
                script_var = data_ele.get(MetaMan.P_SCRIPT_VAR_NAME)
                plLogger.LogDebug(' -> out_id: ' + str(out_id))
                pf_dict[fn_id]['output_id_list'].append(out_id)
                pf_dict[fn_id][out_id] = {}
                pf_dict[fn_id][out_id]['ep_key'] = ep_key
                pf_dict[fn_id][out_id]['script_var'] = script_var
    plLogger.LogDebug('RunStmTestCaseCommand.parse_txml_proc_funcs.end')
    return pf_dict


# FIXME:
# Combine with RunPyScriptCommand and move this to a library
def get_script_path(script_name):
    abs_path = mm_utils.find_script_across_common_paths(script_name + '.py')
    if abs_path == '':
        return ''
    return os.path.split(abs_path)[0]


# Runs the processing functions and updates the kv_dict
# with the new keys
def run_txml_proc_funcs(pf_dict, kv_dict, gui_kv_dict):
    plLogger = PLLogger.GetLogger('methodology')

    plLogger.LogDebug('RunStmTestCaseCommand.run_txml_proc_funcs.start')
    plLogger.LogDebug('pf_dict: ' + str(pf_dict))
    plLogger.LogDebug('kv_dict: ' + str(kv_dict))
    plLogger.LogDebug('gui_kv_dict: ' + str(gui_kv_dict))

    for pf_id in pf_dict['id_list']:
        plLogger.LogDebug('--- proc func id: ' + pf_id + ' ---')
        script_name = pf_dict[pf_id]['script']
        entry_fn = pf_dict[pf_id]['entry_fn']
        plLogger.LogDebug('script: ' + script_name)
        plLogger.LogDebug('entry_fn: ' + entry_fn)

        # Gather the input from the kv_dict and gui_key_dict
        input_dict = OrderedDict()
        for in_key in pf_dict[pf_id]['input_id_list']:
            val = None
            src_id = pf_dict[pf_id][in_key]['src_id']
            if src_id is not None:
                if src_id in kv_dict.keys():
                    val = kv_dict[src_id]
                elif src_id in gui_kv_dict.keys():
                    val = gui_kv_dict[src_id]
            else:
                # Use the default value.  If it is also None,
                # the processing function script will have to
                # handle it.
                val = pf_dict[pf_id][in_key]['default']

            var_name = pf_dict[pf_id][in_key]['script_var']
            if var_name is None:
                # Use the src_id
                var_name = src_id
            input_dict[var_name] = val
        plLogger.LogDebug('input_dict: ' + str(input_dict))

        mod_name = os.path.splitext(script_name)[0]
        plLogger.LogDebug('mod_name: ' + str(mod_name))
        script_path = get_script_path(mod_name)
        if script_path is '':
            plLogger.LogError('Failed to find script: ' + script_name)
            return False
        sys.path.append(script_path)

        # Import the module and reload it if it has already been imported
        exec 'import ' + mod_name
        exec 'reload(' + mod_name + ')'

        # Run the external processing function
        ret_val = OrderedDict()
        err_msg = ''
        exec 'ret_val, err_msg = ' + mod_name + '.' + entry_fn + \
            '(' + str(input_dict) + ')'
        plLogger.LogDebug('external proc func output: ' + str(ret_val))

        # Delete module from memory
        exec 'del ' + mod_name

        if err_msg != '':
            plLogger.LogError('External script: ' + mod_name + ' running ' +
                              entry_fn + ' failed with: ' + err_msg +
                              '  Input was: ' + str(input_dict))
            return False

        # Gather the output and add keys to the kv_dict
        plLogger.LogDebug('adding keys to kv_dict')
        for script_var in ret_val.keys():
            out_key = None
            plLogger.LogDebug('process script_var from ret_val: ' + script_var)

            # Read through the output elements and determine if there is
            # a script variable name that matches the script_var "key"
            # from the ret_val dictionary.
            plLogger.LogDebug('full dict: ' + str(pf_dict[pf_id]))
            for out_id in pf_dict[pf_id]['output_id_list']:
                plLogger.LogDebug(' -> out_id: ' + out_id)
                plLogger.LogDebug(' -> ' + str(pf_dict[pf_id][out_id]))
                if pf_dict[pf_id][out_id]['script_var'] is not None:
                    # Use the script_var
                    if pf_dict[pf_id][out_id]['script_var'] == script_var:
                        out_key = out_id
                        break
            if out_key is None:
                plLogger.LogInfo('Unable to find output scriptVar for ' +
                                 script_var)
                continue
            if out_key not in pf_dict[pf_id]['output_id_list']:
                plLogger.LogError('could not find output id: ' + out_key)
                continue
            # Get the ep_key
            ep_key = pf_dict[pf_id][out_key]['ep_key']
            kv_dict[ep_key] = ret_val[script_var]

    plLogger.LogDebug('Updated kv_dict: ' + str(kv_dict))
    plLogger.LogDebug('RunStmTestCaseCommand.run_txml_proc_funcs.end')
    return True


# Parse TXML for processing dictionaries, returns list of dictionaries
def get_txml_proc_dicts(txml_root):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('RunStmTestCaseCommand.get_txml_proc_dicts.begin')
    MetaMan = txml_utils.MetaManager
    input_dict_list = []
    proc_funcs_ele = txml_root.find('.//' + MetaMan.P_PROC_FUNCS)
    if proc_funcs_ele is None:
        return input_dict_list
    for proc_func_ele in proc_funcs_ele:
        if proc_func_ele.tag != MetaMan.P_PROC_DICT:
            plLogger.LogWarn('(get_txml_proc_dicts) Skipping element '
                             + proc_func_ele.tag +
                             ' in the TXML')
            continue

        input_dict = proc_func_ele.get(MetaMan.P_INPUT_DICT)
        if input_dict is not None and input_dict != "":
            # Validate the interface_dict against the schema
            res = json_utils.validate_json(input_dict,
                                           get_datamodel_dict_schema())
            if res != "":
                plLogger.LogError(res)
                return input_dict_list
            err_str, input_json = json_utils.load_json(input_dict)

            # FIXME:
            # Gracefully exit somehow
            if err_str != "":
                plLogger.LogError(err_str)
            input_dict_list.append(input_json)

    plLogger.LogDebug('RunStmTestCaseCommand.get_txml_proc_dicts.end')
    return input_dict_list


# Runs the processing utility and updates the input
# dict propertyIds with user input values
def parse_input_data(input_data, kv_dict, gui_kv_dict):

    if type(input_data) is dict:
        key_val_list = input_data.items()
    elif type(input_data) is list:
        key_val_list = enumerate(input_data)

    for idx, input_value in key_val_list:
        if type(input_value) is dict or type(input_value) is list:
            input_data[idx] = parse_input_data(input_value, kv_dict, gui_kv_dict)

        if input_value is not None:
            if input_value in kv_dict.keys():
                input_data[idx] = kv_dict[input_value]
            elif input_value in gui_kv_dict.keys():
                input_data[idx] = gui_kv_dict[input_value]

    return input_data


# Runs the processing utility and updates the input
# dict propertyIds with user input values
def run_txml_proc_util(input_dict_list, kv_dict, gui_kv_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('RunStmTestCaseCommand.run_txml_proc_util.begin')
    MetaMan = txml_utils.MetaManager

    for input_dict in input_dict_list:
        plLogger.LogDebug('type: ' + str(type(input_dict)))
        plLogger.LogDebug('input_dict: ' + json.dumps(input_dict))
        script_file = input_dict.get(MetaMan.P_SCRIPT_FILE)
        entry_fn = input_dict.get(MetaMan.P_ENTRY_FUNC)
        modified_input_dict = parse_input_data(input_dict, kv_dict, gui_kv_dict)
        mod_name = os.path.splitext(script_file)[0]
        plLogger.LogDebug('mod_name: ' + str(mod_name))
        script_path = get_script_path(mod_name)
        if script_path is '':
            plLogger.LogError('Failed to find script: ' + script_file)
            return False
        sys.path.append(script_path)

        # Import the module and reload it if it has already been imported
        exec 'import ' + mod_name
        exec 'reload(' + mod_name + ')'

        # Run the external processing function
        ret_val = OrderedDict()
        err_msg = ''
        exec 'ret_val, err_msg = ' + mod_name + '.' + entry_fn + \
            '(' + str(modified_input_dict) + ')'
        plLogger.LogDebug('external proc func output: ' + str(ret_val))

        # Delete module from memory
        exec 'del ' + mod_name

        if err_msg != '':
            plLogger.LogError('External script: ' + mod_name + ' running ' +
                              entry_fn + ' failed with: ' + err_msg +
                              '  Input was: ' + str(input_dict))
            return False

        output_list = input_dict.get(MetaMan.P_OUTPUT)
        plLogger.LogDebug('output_list: ' + str(output_list))
        for output_info in output_list:
            plLogger.LogDebug('output_info: ' + str(output_info))
            script_var = output_info.get("scriptVarName", None)
            ep_key = output_info.get("epKey", None)
            if ep_key is not None:
                kv_dict[ep_key] = ret_val[script_var]

    plLogger.LogDebug('RunStmTestCaseCommand.run_txml_proc_util.end')
    return True


# Build the list of the port groups required by the
# MethodologygroupCommand given the port_group_dict
def build_port_group_list(port_group_dict):
    port_group_list = []
    key_list = port_group_dict.keys()
    for key in key_list:
        port_group_str = key + '=' + ','.join(port_group_dict[key])
        port_group_list.append(port_group_str)
    return port_group_list


def create_and_tag_ports(port_infos):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.create_and_tag_ports.RunStmTestCaseCommand')
    # Setup the command...
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')

    offline_detected = False
    port_handles = []
    # Map the ExposedProperty objects by their keys...
    exposed_property_map = {}
    exposed_config = project.GetObject('ExposedConfig')
    if exposed_config is not None:
        for exp_prop in exposed_config.GetObjects('ExposedProperty'):
            exposed_property_map[exp_prop.Get('EPNameId')] = exp_prop

    for port_info in port_infos:
        tag_locs = port_info.split('=')
        if len(tag_locs) < 2:
            continue

        ctor = CScriptableCreator()

        exp_prop = exposed_property_map.get(tag_locs[0])
        if exp_prop is None:
            plLogger.LogError('Exposed property missing "' + tag_locs[0] + '"')
            return []
        tag = exp_prop.GetObject('Tag', RelationType('ScriptableExposedProperty'))
        if tag is None:
            plLogger.LogError('Tag key missing "' + tag_locs[0] + '" (' + tag.Get('Name') + ').')
            return []

        for loc in tag_locs[1].split(','):
            port = ctor.Create('Port', project)
            port.Set('Location', loc)
            offline_detected = offline_detected or (loc.find('offline') > -1)
            port.AddObject(tag, RelationType('UserTag'))
            port_handles.append(port.GetObjectHandle())

    plLogger.LogDebug('end.create_and_tag_ports.RunStmTestCaseCommand')
    return port_handles, offline_detected


def attach_ports(port_hnd_list):
    if len(port_hnd_list) > 0:
        with AutoCommand('AttachPortsCommand') as attach_cmd:
            attach_cmd.SetCollection('PortList', port_hnd_list)
            attach_cmd.Set('AutoConnect', True)
            attach_cmd.Set('ContinueOnFailure', True)
            attach_cmd.Execute()
    return


def validate(StmTestCase, EnableTieCheck, EnableLoadConfig):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.validate.RunStmTestCaseCommand')

    hnd_reg = CHandleRegistry.Instance()
    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None or not test_case.IsTypeOf('StmTestCase'):
        plLogger.LogError('Was unable to find StmTestCase with handle ' +
                          str(StmTestCase) + ' in the system.')
        return 'ERROR: Could not find StmTestCase.'

    txml_path = os.path.join(test_case.Get('Path'), mgr_const.MM_META_FILE_NAME)
    plLogger.LogDebug('txml_path: ' + str(txml_path))

#    test_meth_name = test_meth.Get('Name')
#    plLogger.LogDebug('test_meth_name: ' + test_meth_name)
#    install_dir = mm_utils.get_methodology_dir(test_meth_name)
#    os.path.join(stc_sys.GetApplicationCommonDataPath(),
#                 mgr_const.MM_TEST_METH_DIR)
#    if not install_dir:
#        return 'ERROR: Could not find path to the test.'

#    # Check that StmTestCase is in datamodel
#    # If NO StmTestCase is provided, then assume it's the "original"
#    test_case_name = ''
#    if StmTestCase == 0:
#        plLogger.LogDebug('No StmTestCase is provided, use the methodology itself')
#        test_case_name = 'original'
#        test_case_path = install_dir
#    else:
#        test_case = mm_utils.get_stm_test_case_from_handle(StmTestCase)
#        if test_case is None:
#            plLogger.LogError('ERROR: Was unable to find StmTestCase' +
#                              ' in the list of installed test cases.')
#            return 'ERROR: Could not find test case.'
#        test_case_name = test_case.Get('Name')
#        test_case_path = test_case.Get('Path')
#    plLogger.LogDebug('test_case_name: ' + test_case_name)
#    plLogger.LogDebug('test_case_path: ' + str(test_case_path))
#    if not os.path.exists(test_case_path):
#        return 'ERROR: Could not find path to the test case.'

#    full_txml_path = os.path.join(test_case_path, mgr_const.MM_META_FILE_NAME)
#    plLogger.LogDebug('full_txml_path: ' + str(full_txml_path))
#    if os.path.isfile(full_txml_path):
#        test_instance_name = txml_utils.extract_test_case_name_from_file(full_txml_path)
#        plLogger.LogDebug('test_instance_name: ' + str(test_instance_name))
#        if test_instance_name == test_case_name:
#            return ''
#    return 'ERROR: Could not find txml file for test case.'

    plLogger.LogDebug('end.validate.RunStmTestCaseCommand')
    return ''


def run(StmTestCase, EnableTieCheck, EnableLoadConfig):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('begin.run.RunStmTestCaseCommand')

    stc_sys = CStcSystem.Instance()
    hnd_reg = CHandleRegistry.Instance()
    test_case = hnd_reg.Find(StmTestCase)
    if test_case is None or not test_case.IsTypeOf('StmTestCase'):
        plLogger.LogError('Was unable to find StmTestCase with handle ' +
                          str(StmTestCase) + ' in the system.')
        return False

    txml_path = os.path.join(test_case.Get('Path'), mgr_const.MM_META_FILE_NAME)
    plLogger.LogDebug('txml_path: ' + str(txml_path))
    plLogger.LogDebug('stm_test_case: ' + test_case.Get('Name'))

    txml_root = get_txml_file_root(txml_path)
    if txml_root is None:
        plLogger.LogError('Could not parse TXML')
        return False

    # Parse the TXML for the keys and values
    key_val_dict, gui_key_val_dict = parse_txml_keys_values(txml_root)

    # Parse the TXML for the processing functions
    proc_func_dict = parse_txml_proc_funcs(txml_root)

    # Run the TXML processing functions
    res = run_txml_proc_funcs(proc_func_dict,
                              key_val_dict,
                              gui_key_val_dict)
    if not res:
        plLogger.LogError('Failed to run TXML processing functions!')
        return False

    # Parse the TXML processing dictionaries
    input_dict_list = get_txml_proc_dicts(txml_root)

    # Parse json dictionaries and run processing functions
    res = run_txml_proc_util(input_dict_list, key_val_dict, gui_key_val_dict)

    if not res:
        plLogger.LogError('Failed to run TXML processing function utilities!')
        return False

    port_group_dict = parse_txml_port_groups(txml_root)
    port_group_list = build_port_group_list(port_group_dict)

    plLogger.LogDebug('key_val_dict (json): ' + json.dumps(key_val_dict))
    plLogger.LogDebug('port_group_list: ' + str(port_group_list))

    # Remove the gui-only keys from key_val_dict
    for key in gui_key_val_dict.keys():
        if key in key_val_dict.keys():
            key_val_dict.pop(key)
    plLogger.LogDebug("key_val_dict without gui only keys (json): " +
                      json.dumps(key_val_dict))

    # Create the ports (they will be tagged appropriately)...
    ports, offline_detected = create_and_tag_ports(port_group_list)

    if EnableTieCheck and not offline_detected:
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

    # If true, the caller hasn't already loaded the config, so do it on their behalf
    if EnableLoadConfig:
        with AutoCommand('LoadFromXml') as load_cmd:
            load_cmd.Set('FileName',
                         os.path.join(test_case.Get('Path'),
                                      mgr_const.MM_SEQUENCER_FILE_NAME))
            load_cmd.Execute()

    # Set the active test case
    mm_utils.set_active_test_case(test_case)

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
        attach_ports(ports)

    plLogger.LogDebug('end.run.RunStmTestCaseCommand')
    return True


def reset(StmMethodology):
    return True


def get_datamodel_dict_schema():
    return '''
    {
        "type": "object",
        "properties": {
            "id": {
                "type": "string"
            },
            "scriptFile": {
                "type": "string"
            },
            "entryFunction": {
                "type": "string"
            },
            "input": {
                "type": "object",
                "properties": {
                    "customDict": {
                        "type": "object"
                    },
                    "iterfaceDict": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ParentTagName": {
                                    "type": "string"
                                },
                                "ClassName": {
                                    "type": "string"
                                },
                                "PropertyValueDict": {
                                    "type": "object"
                                },
                                "StmPropertyModifierDict": {
                                    "type": "object"
                                }
                            },
                            "required": [
                                "ParentTagName",
                                "ClassName"
                            ]
                        }
                    },
                    "protocolDict": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ParentTagName": {
                                    "type": "string"
                                },
                                "ClassName": {
                                    "type": "string"
                                },
                                "PropertyValueDict": {
                                    "type": "object"
                                },
                                "StmPropertyModifierDict": {
                                    "type": "object"
                                }
                            },
                            "required": [
                                "ParentTagName",
                                "ClassName"
                            ]
                        }
                    }
                }
            },
            "output": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scriptVarName": {
                            "type": "string"
                        },
                        "epKey": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
    '''
