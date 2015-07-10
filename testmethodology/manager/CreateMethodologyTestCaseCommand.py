from StcIntPythonPL import *
import os
import stat
import json
import shutil
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.methodology_manager_utils \
    import MethodologyManagerUtils as meth_man_utils
import spirent.methodology.utils.json_utils as json_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(MethodologyJson):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("CreateMethodologyTestCaseCommand.validate")
    this_cmd = get_this_cmd()
    res = json_utils.validate_json(MethodologyJson, this_cmd.Get("InputJsonSchema"))
    if res != "":
        return "MethodologyJson does not conform to the schema: " + res
    return ""


def run(MethodologyJson):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("CreateMethodologyTestCaseCommand.run")
    this_cmd = get_this_cmd()

    err_str, meta = json_utils.load_json(MethodologyJson)
    if err_str != "":
        plLogger.LogError(err_str)
        this_cmd.Set("Status", err_str)
        return False

    meth_key = meta['methodology_key']
    meth_obj = meth_man_utils.get_stm_methodology_from_key(meth_key)

    if meth_obj is None:
        plLogger.LogDebug("Invalid methodology key: " + str(meth_key))
        return False
    if not meth_obj.IsTypeOf("StmMethodology"):
        plLogger.LogError("Invalid methodology object: " + meth_obj.Get("Name"))
        return False

    # Get a new test case key
    tc_key = meth_man_utils.get_new_testcase_key(meth_obj)

    # Create a directory for the test case
    plLogger.LogDebug("create a directory under " + meth_obj.Get("Path"))
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

    # Now that the target files are in place, generate the meta file

    meta['test_case_key'] = tc_key
    MethodologyJson = json.dumps(meta)
    plLogger.LogDebug('meta = ' + MethodologyJson)
    meta_json_file = os.path.join(target_dir, mgr_const.MM_META_JSON_FILE_NAME)

    # Make sure we can write to the file
    changed_permissions = False
    if os.path.exists(meta_json_file):
        mode = os.stat(meta_json_file)[stat.ST_MODE]
        os.chmod(meta_json_file, mode | stat.S_IWRITE)
        changed_permissions = True

    # Open or create the json file and write to it
    f = open(meta_json_file, "w")
    f.write(MethodologyJson)
    f.close()

    # Put permissions back the way they were
    if changed_permissions:
        os.chmod(meta_json_file, mode)

    # Now create the data model portion that corresponds to the test case
    ctor = CScriptableCreator()
    test_case = ctor.Create("StmTestCase", meth_obj)
    # The meth display_name may not be correct, but it is more informative than nothing...
    test_case.Set("Name", meta['display_name'])
    test_case.Set("TestCaseKey", tc_key)
    test_case.Set("Path", target_dir)

    this_cmd.Set("TestCaseKey", tc_key)

    plLogger.LogDebug("CreateMethodologyTestCaseCommand.run.exit")
    return True


def reset():
    return True
