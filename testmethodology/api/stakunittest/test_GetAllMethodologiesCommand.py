import json
from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.api.utils.meth_api_consts \
    import MethApiConsts as ma_consts

PKG_BASE = 'spirent.methodology'
PKG = PKG_BASE + '.api'


def test_get_all_methodologies(stc):
    result = ''
    with AutoCommand(PKG + '.GetAllMethodologiesCommand') as cmd:
        cmd.Execute()
        result = cmd.Get('MethodologyList')

    assert(result != '')
    meta_jsons = json.loads(result)
    rfc2544_json = None
    for meta_json in meta_jsons:
        if meta_json['methodology_key'] == 'RFC2544THROUGHPUT':
            rfc2544_json = meta_json

    assert(rfc2544_json)
    rfc2544_keys = set(rfc2544_json.keys())
    diff = rfc2544_keys - ma_consts.METH_INFO_LIST_KEYS
    assert(len(diff) == 0)
