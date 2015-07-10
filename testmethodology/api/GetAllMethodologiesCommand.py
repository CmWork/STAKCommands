import os
import json
from collections import OrderedDict
from StcIntPythonPL import *
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils
from spirent.methodology.manager.utils.methodologymanagerConst \
    import MethodologyManagerConst as mm_const
import spirent.methodology.utils.json_utils as json_utils
from spirent.methodology.api.utils.meth_api_consts import MethApiConsts \
    as ma_consts


def get_logger():
    return PLLogger.GetLogger('spirent.methodology.api.GetAllMethodologiesCommand')


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate():
    return ""


def get_reduced_meta_info(meta_json_str):
    err, meta_json = json_utils.load_json(meta_json_str,
                                          object_pairs_hook_arg=OrderedDict)
    if err:
        return err, ''

    keys_to_remove = [key for key in meta_json.iterkeys()
                      if key not in ma_consts.METH_INFO_LIST_KEYS]
    for key in keys_to_remove:
        meta_json.pop(key, None)
    return '', json.dumps(meta_json, default=str)


def get_meta_json(test_meth_list):
    meta_jsons = []
    for test_meth in test_meth_list:
        meta_json_file_name = os.path.join(test_meth.Get("Path"),
                                           mm_const.MM_META_JSON_FILE_NAME)
        if not os.path.exists(meta_json_file_name):
            continue
        with open(meta_json_file_name, 'r') as meta_json:
            meta_json_str = meta_json.read()
            if meta_json_str:
                err, meta_json_str = get_reduced_meta_info(meta_json_str)
                if err:
                    get_logger.LogError("Unabled to extract methodology information: " + err)
                    continue
                meta_jsons.append(meta_json_str)
    return "[%s]" % ','.join(meta_jsons)


def run():
    plLogger = get_logger()
    plLogger.LogDebug("begin.run")

    meth_mgr = mm_utils.get_meth_manager()
    test_meth_list = meth_mgr.GetObjects("StmMethodology")
    meta_jsons = get_meta_json(test_meth_list)

    this_cmd = get_this_cmd()
    this_cmd.Set("MethodologyList", meta_jsons)

    plLogger.LogDebug("end.run")
    return True


def reset():
    return True
