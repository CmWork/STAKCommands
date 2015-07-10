from StcIntPythonPL import *
import ast
import json
import os.path
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils
import utils.txml_utils as txml_utils
from utils.validator import validate_command_on_disk


def process_ports(ports_json):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.process_ports.LoadTestMethodologyCommand")

    # Process the ports and bring online if not online already
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port_list = project.GetObjects("Port")

    # Get the ExposedConfig/ExposedProperty objects
    exposed_config = project.GetObject("ExposedConfig")

    exp_props = None
    if exposed_config is not None:
        exp_props = exposed_config.GetObjects("ExposedProperty")

    exp_props_table = {}
    for exp_prop in exp_props:
        val = exp_prop.Get("EPNameId")
        exp_props_table[val] = exp_prop

    if ports_json is not None:
        for key, val in ports_json.iteritems():
            plLogger.LogDebug(" key: " + str(key))
            plLogger.LogDebug(" val: " + str(val))

            exp_prop = exp_props_table[key]
            port = exp_prop.GetObject("Port",
                                      RelationType("ScriptableExposedProperty"))
            if port is None:
                plLogger.LogWarn("Was unable to find a port for " +
                                 str(key) + ", skipping it")
                continue
            if port.Get("Location") != val:
                plLogger.LogDebug(" change " + port.Get("Name") +
                                  " location from " +
                                  port.Get("Location") + " to " + str(val))
                if (port.Get("Online") is True):
                    plLogger.LogDebug(" port " + port.Get("Name") +
                                      " is online, " +
                                      "bring offline first")
                    detach_ports([port.GetObjectHandle()])
                port.Set("Location", str(val))

    port_hnd_list = []
    for port in port_list:
        if port.Get("Online") is False:
            port_hnd_list.append(port.GetObjectHandle())
    plLogger.LogDebug(" have to bring " + str(len(port_hnd_list)) +
                      " ports online")
    if len(port_hnd_list) > 0:
        plLogger.LogDebug(" calling attach_ports")
        attach_ports(port_hnd_list)
    plLogger.LogDebug("end.process_ports.LoadTestMethodologyCommand")


def process_portgroups(portgroups_json):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.process_portgroups.LoadTestMethodologyCommand")
    plLogger.LogDebug("portgroups_json: " + str(portgroups_json))

    # For the first phase, the easiest thing to do is to simply
    # delete all of the ports and create new ones.
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port_list = project.GetObjects("Port")
    for port in port_list:
        if port.Get("Online") is True:
            plLogger.LogDebug(" port " + port.Get("Name") +
                              " is online, bring offline first")
            detach_ports([port.GetObjectHandle()])
        port.MarkDelete()

    # Get the ExposedConfig/ExposedProperty objects
    # Find the tags that correspond to port groups
    exposed_config = project.GetObject("ExposedConfig")

    exp_props = None
    if exposed_config is not None:
        exp_props = exposed_config.GetObjects("ExposedProperty")
    exp_props_table = {}
    for exp_prop in exp_props:
        val = exp_prop.Get("EPNameId")
        exp_props_table[val] = exp_prop

    # Create new ports for each location in each portgroup
    new_port_handle_list = []
    if portgroups_json is not None:
        for key, val in portgroups_json.iteritems():
            plLogger.LogDebug(" key: " + str(key))
            plLogger.LogDebug(" val: " + str(val))

            # The key is the tag that the port has to be tagged
            # with (the port group)
            exp_prop = exp_props_table[key]
            tag = exp_prop.GetObject(
                "Tag", RelationType("ScriptableExposedProperty"))
            if tag is None:
                plLogger.LogError("Could not retrieve Tag!")
                return False

            port_list = ast.literal_eval(json.dumps(val))
            for port_location in port_list:
                # Create the port
                port = ctor.Create("Port", project)
                port.Set("Location", port_location)
                # Tag the port
                port.AddObject(tag, RelationType("UserTag"))
                new_port_handle_list.append(port.GetObjectHandle())
    if len(new_port_handle_list) > 0:
        attach_ports(new_port_handle_list)
    plLogger.LogDebug("end.process_portgroups.LoadTestMethodologyCommand")


def detach_ports(port_hnd_list):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.detach_ports.LoadTestMethodologyCommand")
    ctor = CScriptableCreator()

    detach_cmd = ctor.CreateCommand("DetachPortsCommand")
    detach_cmd.Set("PortList", port_hnd_list)
    detach_cmd.Execute()
    detach_cmd.MarkDelete()
    plLogger.LogDebug("end.detach_ports.LoadTestMethodologyCommand")


def attach_ports(port_hnd_list):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.attach_ports.LoadTestMethodologyCommand")
    ctor = CScriptableCreator()
#    hnd_reg = CHandleRegistry.Instance()
    plLogger.LogDebug("starting attach ports with: " + str(port_hnd_list))

#    # If AutoConnect in the AttachPortsCommand is set to False, we need
#    # the chassis have to be connected to first
#    chassis_list = []
#    for port_hnd in port_hnd_list:
#        port = hnd_reg.Find(port_hnd)
#        if port is None:
#            # FIXME:
#            # Log a warning
#            plLogger.LogWarn("Could not find handle for port: " + str(port_hnd))
#            continue
#        loc = port.Get("Location")
#        chassis = loc.strip("//").split("/")[0]
#        plLogger.LogDebug("Adding chassis: " + str(chassis))
#        if chassis not in chassis_list:
#            chassis_list.append(chassis)
#    plLogger.LogDebug("chassis_list: " + str(chassis_list))
#    if len(chassis_list) > 0:
#        plLogger.LogDebug("Calling ConnectToChassisCommand")
#        connect_cmd = ctor.CreateCommand("ConnectToChassisCommand")
#        connect_cmd.SetCollection("AddrList", chassis_list)
#        connect_cmd.Execute()
#        connect_cmd.MarkDelete()

    plLogger.LogDebug("Calling AttachPortsCommand")
    attach_cmd = ctor.CreateCommand("AttachPortsCommand")
    attach_cmd.SetCollection("PortList", port_hnd_list)
    attach_cmd.Set("AutoConnect", True)
    attach_cmd.Set("ContinueOnFailure", True)
    attach_cmd.Execute()
    attach_cmd.MarkDelete()

    plLogger.LogDebug("end.attach_ports.LoadTestMethodologyCommand")


def check_tie_for_profile_based_test(input_json, stm_test_case):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.check_tie_for_profile_based_test.LoadTestMethodologyCommand")
    ctor = CScriptableCreator()

    # Validate that the test will run
    # 1. Call EstimateTxmlProfileObjectExpansionCommand
    # 2. Call ScalingValidatePortsCommand (package = spirent.testintel)

    pkg = "spirent.methodology"
    mm_pkg = pkg + ".manager"
    tie_pkg = "spirent.testintel"

    if stm_test_case is None:
        plLogger.LogWarn("WARNING: Skipping TIE check for object expansion due to" +
                         " invalid StmTestCase object")
        return False
    stm_meth = stm_test_case.GetObject("StmMethodology", RelationType("ParentChild", 1))
    if stm_meth is None:
        plLogger.LogWarn("WARNING: Skipping TIE check for object expansion due to" +
                         " invalid StmMethodology object")
        return False

    # Generate the JSON to feed into TIE
    est_cmd = ctor.CreateCommand(mm_pkg + ".EstimateTxmlProfileObjectExpansionCommand")
    if est_cmd is None:
        plLogger.LogError("ERROR: Unable to create an instance of " + mm_pkg +
                          "EstimateTxmlProfileObjectExpansionCommand.")
        return False
    est_cmd.Set("InputJson", input_json)
    est_cmd.Set("StmMethodology", stm_meth.GetObjectHandle())
    est_cmd.Set("StmTestCase", stm_test_case.GetObjectHandle())
    est_cmd.Execute()
    output_json = est_cmd.Get("OutputJson")
    est_cmd.MarkDelete()

    # Determine if the test will work on the ports given
    tie_cmd = ctor.CreateCommand(tie_pkg + ".ScalingValidatePortsCommand")
    if tie_cmd is None:
        plLogger.LogError("ERROR: Unable to create an instance of " + tiepkg +
                          ".ScalingValidatePortsCommand.")
        return False
    tie_cmd.Set("Profile", output_json)
    tie_cmd.Execute()
    verdict = tie_cmd.Get("Verdict")
    tie_cmd.MarkDelete()
    plLogger.LogDebug("TIE Verdict: " + str(verdict))

    # FIXME:
    # For now, return true.  Not sure what TIE is giving back yet.
    plLogger.LogDebug("end.check_tie_for_profile_based_test.LoadTestMethodologyCommand")
    return True


def validate(StmMethodology, StmTestCase, InputJson, EnableTieCheck):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate.LoadTestMethodologyCommand")

    # Check that TestMethodologyName exists
    stc_sys = CStcSystem.Instance()

    test_meth = meth_man_utils.get_stm_methodology_from_handle(StmMethodology)
    if test_meth is None:
        plLogger.LogError("ERROR: Was unable to find StmMethodology with handle " +
                          str(StmMethodology) + " in the list of installed tests.")
        return "ERROR: Could not find test."
    test_meth_name = test_meth.Get('TestMethodologyName')
    plLogger.LogDebug("test_meth_name: " + test_meth_name)

    install_dir = meth_man_utils.get_methodology_dir(test_meth_name)
    os.path.join(stc_sys.GetApplicationCommonDataPath(),
                 mgr_const.MM_TEST_METH_DIR)
    if not install_dir:
        return "ERROR: Could not find path to the test."

    # Check that StmTestCase is in datamodel
    # If NO StmTestCase is provided, then assume it's the "original"
    test_case_name = ""
    if StmTestCase == 0:
        plLogger.LogDebug("No StmTestCase is provided, use the methodology itself")
        test_case_name = "original"
        test_case_path = install_dir
    else:
        hnd_reg = CHandleRegistry.Instance()
        test_case = hnd_reg.Find(StmTestCase)
        if test_case is None:
            plLogger.LogError("ERROR: Was unable to find StmTestCase" +
                              " in the list of installed test cases.")
            return "ERROR: Could not find test case."
        test_case_name = test_case.Get('TestCaseName')
        test_case_path = test_case.Get('Path')
    plLogger.LogDebug("test_case_name: " + test_case_name)
    plLogger.LogDebug("test_case_path: " + str(test_case_path))
    if not os.path.exists(test_case_path):
        return "ERROR: Could not find path to the test case."

    full_txml_path = os.path.join(test_case_path, mgr_const.MM_META_FILE_NAME)
    plLogger.LogDebug("full_txml_path: " + str(full_txml_path))
    if os.path.isfile(full_txml_path):
        test_instance_name = txml_utils.extract_test_case_name_from_file(full_txml_path)
        plLogger.LogDebug("test_instance_name: " + str(test_instance_name))
        if test_instance_name == test_case_name:
            return ""
    plLogger.LogDebug("end.validate.LoadTestMethodologyCommand")
    return "ERROR: Could not find txml file for test case."


def run(StmMethodology, StmTestCase, InputJson, EnableTieCheck):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.LoadTestMethodologyCommand")
    stc_sys = CStcSystem.Instance()

    # Keep this in to prevent PEP8 errors as the ParentConfig
    # of the LoadFromXmlCommand is commented out or uncommented out.
    plLogger.LogDebug("InputJson: " + str(InputJson))
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    # validate() already checks the existence of StmMethodology and StmTestCase
    # No need to do the checking again here
    stm_meth = meth_man_utils.get_stm_methodology_from_handle(StmMethodology)
    plLogger.LogDebug("stm_meth: " + stm_meth.Get("TestMethodologyName"))
    test_meth_path = stm_meth.Get("Path")
    plLogger.LogDebug("test_meth_path: " + str(test_meth_path))

    stm_test_case = None

    # If NO StmTestCase is provided, then assume it's the "original"
    if StmTestCase == 0:
        plLogger.LogDebug("stm_test_case: original")
        test_case_path = test_meth_path
    else:
        hnd_reg = CHandleRegistry.Instance()
        stm_test_case = hnd_reg.Find(StmTestCase)
        plLogger.LogDebug("stm_test_case: " + stm_test_case.Get("TestCaseName"))
        test_case_path = stm_test_case.Get("Path")
        if EnableTieCheck:
            # In the worst case, a profile test won't fit.  If the test isn't
            # profile based, we currently have no way of determining if it will
            # run successfully or not.
            can_run = check_tie_for_profile_based_test(InputJson, stm_test_case)

    plLogger.LogDebug("test_case_path: " + str(test_case_path))

    if not validate_command_on_disk(os.path.join(test_case_path,
                                                 mgr_const.
                                                 MM_SEQUENCER_FILE_NAME)):
        plLogger.LogError("validate_command_on_disk failed for: " +
                          test_meth_path + "/" +
                          mgr_const.MM_SEQUENCER_FILE_NAME)
        return False

    # Non profile-based tests can always run....  This is kind of a
    # strange check until we figure out how to validate non
    # profile-based tests.
    can_run = True

    # Load
    if can_run:
        loadCmd = ctor.CreateCommand("LoadFromXml")
        loadCmd.Set("FileName",
                    os.path.join(test_case_path,
                                 mgr_const.MM_SEQUENCER_FILE_NAME))
        # FIXME !!!!!!
        # If the ParentConfig is set to empty string (""), then the GUI works and TCL crashes.
        # If the ParentConfig is set to project, then the GUI crashes and TCL works
        # loadCmd.Set("ParentConfig", project.GetObjectHandle())
        loadCmd.Execute()
        if StmTestCase == 0:
            # Can only do this if we're loading a real test case, not the original
            meth_man_utils.set_active_test_case(stm_test_case)
    else:
        # FIXME:
        # We obviously need more information here.
        plLogger.LogError("ERROR: Can not load Test Methodology")
        return False

    # Process the ports (now that the config is loaded)
    # Break the JSON into ports and params sections
    ports_json = None
    params_json = None
    portgroups_json = None
    if InputJson != "":
        input_json = json.loads(InputJson)
        if "portgroups" in input_json.keys():
            portgroups_json = input_json["portgroups"]
        if "params" in input_json.keys():
            params_json = input_json["params"]

    plLogger.LogDebug("calling relocate and bring ports online")

    # Relocate and bring ports online as necessary
    if portgroups_json is not None:
        process_portgroups(portgroups_json)
    else:
        process_ports(ports_json)

    if params_json is not None:
        plLogger.LogDebug("params_json: " + json.dumps(params_json))

        # Fill in the input JSON if it exists
        sequencer = stc_sys.GetObject("Sequencer")
        cmd_list = sequencer.GetCollection("CommandList")
        for cmd_hnd in cmd_list:
            cmd = hnd_reg.Find(cmd_hnd)
            if cmd is None:
                continue
            if cmd.IsTypeOf("spirent.methodology.manager.MethodologyGroupCommand"):
                cmd.Set("InputJson", json.dumps(params_json))
                break

    plLogger.LogDebug("end.run.LoadTestMethodologyCommand")
    return True


def reset(StmMethodology):
    return True
