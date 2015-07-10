from StcIntPythonPL import *
import os
import ast
import json
import xml.etree.ElementTree as etree
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils
import utils.txml_utils as txml_utils
from utils.txml_utils import MetaManager as meta_man


def update_port_tag(p_element, port_dict):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.update_port_tag.SaveTestCaseCommand")
    # Verify that the element passed in is a port tag
    if p_element.tag == meta_man.TR_PORT:
        plLogger.LogDebug("Found port: " + p_element.get(meta_man.TR_NAME))
        port_id = p_element.get(meta_man.TR_NAME)
        plLogger.LogDebug("Processing port_id: " + str(port_id))
        plLogger.LogDebug("Among the following keys: " + str(port_dict.keys()))
        new_location = port_dict[port_id]
        plLogger.LogDebug("With the new location: " + str(new_location))
        # Now find the attribute tag for the location
        for attribute in p_element:
            if attribute.tag == meta_man.TR_ATTR:
                plLogger.LogDebug("Found attribute tag: " + attribute.get(meta_man.TR_NAME))
                if attribute.get(meta_man.TR_NAME) == meta_man.TR_LOCATION:
                    plLogger.LogDebug("Update port location to: " + new_location)
                    attribute.set(meta_man.TR_VALUE, new_location)

    plLogger.LogDebug("end.update_port_tag.SaveTestCaseCommand")


def validate(TestMethodologyName, InputJson, TestCaseName, FileName):
    # Check that TestMethodologyName exists
    if not TestMethodologyName:
        return "ERROR: Invalid methodology name"
    if not TestCaseName:
        return "ERROR: Invalid test case name"
    if not FileName:
        return "ERROR: Invalid file name"

    return ""


def run(TestMethodologyName, InputJson, TestCaseName, FileName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.SaveTestCaseCommand")

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    # If TestCaseName is "" then overwrite the "original" TXML file
    # Otherwise, create a new TXML file
    is_overwrite = False
    test_case_name = TestCaseName
    if test_case_name == "":
        plLogger.LogDebug("This is an overwrite operation")
        test_case_name = meta_man.TEST_INSTANCE_ORIGINAL
        is_overwrite = True

    plLogger.LogDebug("TestCaseName: " + TestCaseName)
    plLogger.LogDebug("test_case_name: " + test_case_name)
    plLogger.LogDebug("is_overwrite: " + str(is_overwrite))

    if project is None:
        plLogger.LogError("Invalid Project object")
        return False

    # Find the TXML file (source)
    test_meth_path = os.path.join(stc_sys.GetApplicationCommonDataPath(),
                                  mgr_const.MM_TEST_METH_DIR,
                                  TestMethodologyName)
    txml_file = os.path.join(test_meth_path,
                             mgr_const.MM_TEST_CASE_SUBDIR,
                             mgr_const.MM_META_FILE_NAME)
    if not os.path.exists(txml_file):
        plLogger.LogError("ERROR: Can't find " + str(txml_file))
        return False

    # Read the TXML
    txml_tree = etree.parse(txml_file)
    txml_root = txml_tree.getroot()
    plLogger.LogDebug("Processing TXML: " + etree.tostring(txml_root))
    if txml_root is None:
        plLogger.LogError("ERROR: Could not parse TXML located in " + str(txml_file))
        return False

    # Parse the JSON into ports/params
    input_json = json.loads(InputJson)
    new_params_dict = ast.literal_eval(json.dumps(input_json["params"]))
    new_ports_dict = ast.literal_eval(json.dumps(input_json["ports"]))

    plLogger.LogDebug(" new_params_dict: " + str(new_params_dict))
    plLogger.LogDebug(" new_ports_dict: " + str(new_ports_dict))

    for child in txml_root:
        plLogger.LogDebug("Found tag: " + child.tag)
        if child.tag == meta_man.TEST_INFO:
            plLogger.LogDebug("process test info section")
            if not is_overwrite:
                plLogger.LogDebug("Setting new test case name to: " + test_case_name)
                # Change the name of the testCase
                child.set(meta_man.TI_TEST_CASE_NAME, test_case_name)
            else:
                plLogger.LogDebug("Using existing test case name: " +
                                  child.get(meta_man.TI_TEST_CASE_NAME))
        elif child.tag == meta_man.TEST_RESOURCES:
            plLogger.LogDebug("process test resources section")
            PORT_STR = ".//" + meta_man.TR_RESOURCE_GROUPS + \
                       "/" + meta_man.TR_RESOURCE_GROUP + \
                       "/" + meta_man.TR_PORT_GROUPS + \
                       "/" + meta_man.TR_PORT_GROUP + \
                       "/" + meta_man.TR_PORTS + \
                       "/" + meta_man.TR_PORT
            port_list = child.findall(PORT_STR)
            for port in port_list:
                if port.tag == meta_man.TR_PORT:
                    plLogger.LogDebug("Process port: " +
                                      port.get(meta_man.TR_NAME))
                    update_port_tag(port, new_ports_dict)
        elif (child.tag == meta_man.EDITABLE_PARAMS):
            plLogger.LogDebug("process test params section")
            PARAM_STR = ".//" + meta_man.EP_PARAM_GROUPS + \
                        "/" + meta_man.EP_PARAM_GROUP + \
                        "/" + meta_man.EP_PARAMS + \
                        "/" + meta_man.EP_PARAM
            param_list = child.findall(PARAM_STR)
            for param in param_list:
                plLogger.LogDebug("Found param)")
                prop_val = None
                prop_id = None
                # Process attributes
                for attr in param:
                    if attr.tag == meta_man.EP_ATTR:
                        attr_name = attr.get(meta_man.EP_NAME)
                        if attr_name == meta_man.EP_PROP_ID:
                            prop_id = attr.get(meta_man.EP_VALUE)
                        elif attr_name == meta_man.EP_DEFAULT:
                            prop_val = attr.get(meta_man.EP_VALUE)
                            default_val_elem = attr
                plLogger.LogDebug(" prop_val: " + str(prop_val))
                plLogger.LogDebug(" prop_id: " + str(prop_id))
                if prop_id is not None and prop_val is not None:
                    if prop_id in new_params_dict.keys():
                        if default_val_elem is None:
                            plLogger.LogError("ERROR: Could not find XML element for " +
                                              str(prop_id))
                        else:
                            default_val_elem.set(meta_man.EP_VALUE, new_params_dict[prop_id])
                else:
                    plLogger.LogWarn(" prop_id and or prop_val was none - no value to set")

    # Test case path
    tc_path = os.path.join(test_meth_path, mgr_const.MM_TEST_CASE_SUBDIR)
    if not os.path.exists(tc_path):
        os.makedirs(tc_path)

    if is_overwrite is False:
        plLogger.LogDebug(" create a new testcase...")
        # Create new TXML filename (original filename + timestamp)
        if FileName == "":
            nice_ts = txml_utils.get_timestamp_ymd_hms()
            file_prefix = str(os.path.splitext(mgr_const.MM_META_FILE_NAME)[0])
            new_tc_file = file_prefix + "_" + nice_ts + ".txml"
        else:
            new_tc_file = FileName
        plLogger.LogDebug("Writing new Test Case: " + str(new_tc_file))

        full_path = os.path.join(tc_path, new_tc_file)

        # Add a new test case
        meth_man = meth_man_utils.get_meth_manager()
        meth_list = meth_man.GetObjects("StmMethodology")
        for test_meth in meth_list:
            if test_meth.Get("TestMethodologyName") == TestMethodologyName:
                test_case = ctor.Create("StmTestCase", test_meth)
                test_case.Set("TestCaseName", TestCaseName)
                test_case.Set("Path", full_path)

    else:
        plLogger.LogDebug("Overwriting values in existing " +
                          str(mgr_const.MM_META_FILE_NAME))
        full_path = os.path.join(tc_path, mgr_const.MM_META_FILE_NAME)

    txml_str = etree.tostring(txml_root)
    plLogger.LogDebug(" txml_str: " + str(txml_str))
    plLogger.LogDebug(" writing file to " + str(full_path))
    f = open(full_path, "w")
    f.write("<?xml version=\"1.0\" ?>\n")
    f.write(txml_str)
    f.close()

    hnd_reg = CHandleRegistry.Instance()
    this_cmd = hnd_reg.Find(__commandHandle__)
    this_cmd.Set("TxmlFileName", full_path)

    plLogger.LogDebug("end.run.SaveTestCaseCommand")
    return True


def reset():
    return True
