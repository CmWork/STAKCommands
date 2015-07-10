import os
from StcIntPythonPL import *
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mm_const


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(MethodologyKey):
    if MethodologyKey == 'Not Specified':
        return "Methodology key is not specified."
    return ""


def get_meta_json(test_meth):
    meta_json_file_name = os.path.join(test_meth.Get("Path"),
                                       mm_const.MM_META_JSON_FILE_NAME)
    if os.path.exists(meta_json_file_name):
        with open(meta_json_file_name, 'r') as meta_json:
            return meta_json.read()
    return ''


def run(MethodologyKey):
    this_cmd = get_this_cmd()
    plLogger = PLLogger.GetLogger('methodology')
    test_meth = mm_utils.get_stm_methodology_from_key(MethodologyKey)
    if not test_meth:
        err = "No methodology with key " + MethodologyKey + " exists"
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return False

    meta_json = get_meta_json(test_meth)

    this_cmd.Set('MethodologyInfo', meta_json)
    if meta_json == '':
        err = "No JSON meta data available for methodology with key " + \
              MethodologyKey
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return False

    return True


def reset():
    return True
