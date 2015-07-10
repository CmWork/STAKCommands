from StcIntPythonPL import *
import xml.etree.ElementTree as etree
from mock import MagicMock
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent',
                             'methodology'))
import spirent.methodology.traffic.CreateTrafficMix1Command as command


PKG_BASE = 'spirent.methodology'
PKG = PKG_BASE + '.traffic'


def test_validate_defaults(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.CreateTrafficMix1Command', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.validate(10.0, 'PERCENT_LINE_RATE', '', True)
    assert '' == ret


def test_validate_bad_command(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.CreateTrafficMix1Command', seq)
    sub_cmd = ctor.Create('DevicesStartAllCommand', cmd)
    cmd.SetCollection('CommandList', [sub_cmd.GetObjectHandle()])
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.validate(10.0, 'PERCENT_LINE_RATE', '', True)
    assert 'Command devicesstartallcommand not in' in ret


def test_run_defaults_empty(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.CreateTrafficMix1Command', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.run(10.0, 'PERCENT_LINE_RATE', '', True)
    assert True is ret
    obj_list = proj.GetObjects('StmTrafficMix')
    assert 1 == len(obj_list)
    assert '' != obj_list[0].Get('MixInfo')
    mix_elem = etree.fromstring(obj_list[0].Get('MixInfo'))
    assert 10.0 == float(mix_elem.get('Load'))
    assert 'PERCENT_LINE_RATE' == mix_elem.get('LoadUnit')
    assert '' == mix_elem.get('WeightList')


def test_chaining(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.CreateTrafficMix1Command', seq)
    cmd2 = ctor.Create(PKG + '.LoadTrafficTemplateCommand', cmd)
    cmd.SetCollection('CommandList', [cmd2.GetObjectHandle()])
    command.get_this_cmd = MagicMock(return_value=cmd)
    cmd.Set('MixTagName', 'Unknown Tag')
    ret = command.run(10.0, 'PERCENT_LINE_RATE', 'Unknown Tag', True)
    assert True is ret
    assert len(cmd.GetCollection('CommandList')) == 1
    obj_list = proj.GetObjects('StmTrafficMix')
    assert len(obj_list) == 1
    assert obj_list[0].GetObjectHandle() == cmd2.Get('StmTemplateMix')


def test_run_defaults_empty_tagged(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.CreateTrafficMix1Command', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    cmd.Set('MixTagName', 'Unknown Tag')
    ret = command.run(10.0, 'PERCENT_LINE_RATE', 'Unknown Tag', True)
    assert True is ret
    obj_list = proj.GetObjects('StmTrafficMix')
    assert 1 == len(obj_list)
    assert '' != obj_list[0].Get('MixInfo')
    mix_elem = etree.fromstring(obj_list[0].Get('MixInfo'))
    assert 10.0 == float(mix_elem.get('Load'))
    assert 'PERCENT_LINE_RATE' == mix_elem.get('LoadUnit')
    assert '' == mix_elem.get('WeightList')
    tag = obj_list[0].GetObject('Tag', RelationType('UserTag'))
    assert tag
    assert 'Unknown Tag' == tag.Get('Name')
