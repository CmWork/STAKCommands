import json
from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand

PKG_BASE = 'spirent.methodology'
PKG = PKG_BASE + '.api'


def test_get_methodology_info(stc):
    key = 'RFC2544THROUGHPUT'
    result = ''
    with AutoCommand(PKG + '.GetMethodologyInfoCommand') as cmd:
        cmd.Set('MethodologyKey', key)
        cmd.Execute()
        result = cmd.Get('MethodologyInfo')

    assert(result != '')
    meta_json = json.loads(result)
    assert(meta_json['methodology_key'] == key)
    assert('port_groups' in meta_json)


def test_no_meth(stc):
    key = 'FOOBAR'
    result = ''
    with AutoCommand(PKG + '.GetMethodologyInfoCommand') as cmd:
        cmd.Set('MethodologyKey', key)
        cmd.Execute()
        result = cmd.Get('MethodologyInfo')
        assert(cmd.Get('Status') == 'No methodology with key FOOBAR exists')

    assert(result == '')


def test_empty_key(stc):
    with AutoCommand(PKG + '.GetMethodologyInfoCommand') as cmd:
        try:
            cmd.Set('MethodologyKey', '')
            raise AssertionError('Validation Error not caught')
        except RuntimeError:
            pass


def test_default_key(stc):
    with AutoCommand(PKG + '.GetMethodologyInfoCommand') as cmd:
        try:
            cmd.Execute()
            raise AssertionError('Validation Error not caught')
        except RuntimeError:
            pass


def disabled_test_no_json(stc):
    # BGPRRCON currently does not have a meta.json file but that
    # will change in the future.
    key = 'BGPRRCON'
    result = ''
    with AutoCommand(PKG + '.GetMethodologyInfoCommand') as cmd:
        cmd.Set('MethodologyKey', key)
        cmd.Execute()
        result = cmd.Get('MethodologyInfo')
        assert(cmd.Get('Status') ==
               'No JSON meta data available for methodology with key BGPRRCON')

    assert(result == '')