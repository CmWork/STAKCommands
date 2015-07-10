from StcIntPythonPL import *
import zipfile
import os.path
import shutil
from utils.methodologymanagerConst import MethodologyManagerConst as mgr_const
from utils.validator import validate_command_on_disk
import utils.txml_utils as txml_utils
from utils.methodology_manager_utils import MethodologyManagerUtils as meth_man_utils


def validate(FileName):
    hnd_reg = CHandleRegistry.Instance()

    this_cmd = hnd_reg.Find(__commandHandle__)

    if not this_cmd.Get("FileName").endswith(mgr_const.MM_STM_EXT):
        return "Require FileName extension to be " + mgr_const.MM_STM_EXT

    return ''


def run(FileName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("begin.run.ImportTestCommand")
    plLogger.LogDebug(" FileName: " + FileName)

    stc_sys = CStcSystem.Instance()
    common_data_path = stc_sys.GetApplicationCommonDataPath()
    test_meth_dir = os.path.join(common_data_path,
                                 mgr_const.MM_TEST_METH_DIR)
    if not os.path.exists(test_meth_dir):
        plLogger.LogDebug("Adding testMeth directory: " + str(test_meth_dir))
        os.mkdir(test_meth_dir)

    # Unzip to temp directory
    nice_ts = txml_utils.get_timestamp_ymd_hms()
    temp_dir = os.path.join(test_meth_dir,
                            "temp_" + str(nice_ts))

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with zipfile.ZipFile(FileName, "r") as z:
        z.extractall(temp_dir)

    meta_file = os.path.join(temp_dir, mgr_const.MM_TEST_CASE_SUBDIR,
                             mgr_const.MM_META_FILE_NAME)
    seq_file = os.path.join(temp_dir,
                            mgr_const.MM_SEQUENCER_FILE_NAME)

    if not os.path.isfile(meta_file):
        plLogger.LogError("Unable to extract TXML file!")
        return False
    if not os.path.isfile(seq_file):
        plLogger.LogError("Unable to extract sequencer file!")
        return False

    # Read the TXML file for the test name
    test_name = txml_utils.extract_methodology_name_from_file(meta_file)
    if not test_name:
        plLogger.LogError("ERROR: Could not extract test methodology name from the TXML file!")
        return False
    plLogger.LogDebug("test_name: " + test_name)

    if not validate_command_on_disk(seq_file):
        return False

    test_meth_test_dir = os.path.join(test_meth_dir, test_name)
    test_meth_test_case_dir = os.path.join(test_meth_test_dir,
                                           mgr_const.MM_TEST_CASE_SUBDIR)
    plLogger.LogDebug(" test_meth_test_dir: " + str(test_meth_test_dir))
    plLogger.LogDebug(" test_meth_test_case_dir: " + str(test_meth_test_case_dir))

    if not os.path.exists(test_meth_test_dir):
        os.makedirs(test_meth_test_dir)
    if not os.path.exists(test_meth_test_case_dir):
        os.makedirs(test_meth_test_case_dir)

    # FIXME:
    # Need to handle multiple copies of the TXML file
    shutil.copy(seq_file, test_meth_test_dir)
    shutil.copy(meta_file, test_meth_test_case_dir)

    # Add BLL objects
    meth_man_utils.build_test_methodology(test_meth_test_dir, use_txml=True)

    # Clean up
    # Delete the temporary directory and its contents
    os.remove(meta_file)
    os.rmdir(os.path.join(temp_dir, mgr_const.MM_TEST_CASE_SUBDIR))
    os.remove(seq_file)
    os.rmdir(temp_dir)

    plLogger.LogDebug("end.run.ImportTestCommand")
    return True


def reset():

    return True
