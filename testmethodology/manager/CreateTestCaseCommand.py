from StcIntPythonPL import *
import os
import stat
import shutil
import xml.etree.ElementTree as etree
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
from utils.txml_utils import MetaManager as meta_man


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(TestCaseSrc, TestCaseName, TestCaseDescription):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.validate.CreateTestCaseCommand")
    if TestCaseSrc is None:
        return "ERROR: Could not find test case source. " + \
            "Test case source should be of type StmMethodology or StmTestCase."
    if not TestCaseName:
        return "ERROR: Invalid test case name"

    plLogger.LogDebug("end.validate.CreateTestCaseCommand")
    return ""


def run(TestCaseSrc, TestCaseName, TestCaseDescription):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.CreateTestCaseCommand")
    hnd_reg = CHandleRegistry.Instance()
    meth_src_obj = hnd_reg.Find(TestCaseSrc)
    meth_obj = None
    if meth_src_obj is None:
        plLogger.LogDebug("Invalid TestCaseSrc handle: " + str(TestCaseSrc))
    if meth_src_obj.IsTypeOf("StmMethodology"):
        meth_obj = meth_src_obj
    elif meth_obj.IsTypeOf("StmTestCase"):
        # TODO: Support creation from another test case
        plLogger.LogError("Test Case creation from existing test cases is not " +
                          "currently supported.")
        meth_obj = meth_src_obj.GetParent()
        return False
    else:
        plLogger.LogError("Invalid source object: " + meth_src_obj.Get("Name"))
        return False

    # Get a new test case key
    tc_key = meth_man_utils.get_new_testcase_key(meth_obj)

    # Create a directory for the test case
    plLogger.LogDebug("create a directory under " + meth_obj.Get("Path"))
    meth_key = meth_obj.Get("MethodologyKey")
    target_dir = meth_man_utils.methodology_test_case_mkdir(meth_key, tc_key)
    if not target_dir:
        plLogger.LogError("Failed to create test case directory")
        return False

    source_dir = meth_obj.Get("Path")
    plLogger.LogDebug("Source directory is " + source_dir)
    plLogger.LogDebug("Target directory is " + target_dir)

    # Copy the files from the source directory to the new target directory
    src_files = os.listdir(source_dir)
    for file_name in src_files:
        full_file_name = os.path.join(source_dir, file_name)
        if (os.path.isfile(full_file_name)):
            shutil.copy(full_file_name, target_dir)

    # Now that the target files are in place, update the metadata file

    # Open the TXML file
    txml_file = os.path.join(target_dir,
                             mgr_const.MM_META_FILE_NAME)
    if not os.path.exists(txml_file):
        plLogger.LogError("ERROR: Can't find " + str(txml_file))
        return False

    # Read the TXML
    txml_tree = etree.parse(txml_file)
    if txml_tree is None:
        plLogger.LogError("ERROR: Could not parse TXML located in " + str(txml_file))
        return False
    txml_root = txml_tree.getroot()
    if txml_root is None:
        plLogger.LogError("ERROR: Could not parse TXML located in " + str(txml_file))
        return False

    # Update the testInfo section with the name of the test case
    child = txml_root.find(meta_man.TEST_INFO)
    if child is not None:
        child.set(meta_man.TI_TEST_CASE_NAME, TestCaseName)
        child.set(meta_man.TI_DESCRIPTION, TestCaseDescription)
        child.set(meta_man.TI_TEST_CASE_KEY, tc_key)

    # Make sure we can write to the file
    mode = os.stat(txml_file)[stat.ST_MODE]
    os.chmod(txml_file, mode | stat.S_IWRITE)

    # Write the txml out to the file
    txml_str = etree.tostring(txml_root)
    f = open(txml_file, "w")
    f.write("<?xml version=\"1.0\" ?>\n")
    f.write(txml_str)
    f.close()

    # Put permissions back the way they were
    os.chmod(txml_file, mode)

    # Now create the data model portion that corresponds to the test case
    ctor = CScriptableCreator()
    test_case = ctor.Create("StmTestCase", meth_obj)
    test_case.Set("Name", TestCaseName)
    test_case.Set("TestCaseKey", tc_key)
    test_case.Set("Path", target_dir)

    this_cmd = get_this_cmd()
    this_cmd.Set("StmTestCase", test_case.GetObjectHandle())

    plLogger.LogDebug("end.run.CreateTestCaseCommand")
    return True


def reset():
    return True
