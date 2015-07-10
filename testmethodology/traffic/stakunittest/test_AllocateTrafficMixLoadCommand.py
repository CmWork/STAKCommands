from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
import json
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.traffic.AllocateTrafficMixLoadCommand as command
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils


PKG = 'spirent.methodology.traffic'


def test_run_fail_no_mix(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TrafficMixTagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert False is ret


def test_run_fail_invalid_mix(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TrafficMixTagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert False is ret


def test_run_fraction(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo', mix_info_2_components())

    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())

    tmpl_list = []
    sb_list = []

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb1 = ctor.Create('StreamBlock', port)
    sb_list.append(sb1)
    tmpl_list[-1].AddObject(sb1, RelationType('GeneratedObject'))

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb2 = ctor.Create('StreamBlock', port)
    sb_list.append(sb2)
    tmpl_list[-1].AddObject(sb2, RelationType('GeneratedObject'))

    assert command.run(cmd.Get('StmTrafficMix'), '', 10.0, 'PERCENT_LINE_RATE')

    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [7.5, 2.5] == load_list

    roots = traf_mix.Get('MixInfo')
    assert roots
    err_str, root = json_utils.load_json(roots)
    assert err_str == ""
    assert 'loadUnits' in root
    assert root['loadUnits'] == 'PERCENT_LINE_RATE'
    assert 'components' in root
    assert len(root['components']) == 2
    assert 'appliedValue' in root['components'][0]
    assert root['components'][0]['appliedValue'] == 7.5
    assert 'appliedValue' in root['components'][1]
    assert root['components'][1]['appliedValue'] == 2.5


def test_run_integer(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo', mix_info_2_components())

    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())

    tmpl_list = []
    sb_list = []

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb1 = ctor.Create('StreamBlock', port)
    sb_list.append(sb1)
    tmpl_list[-1].AddObject(sb1, RelationType('GeneratedObject'))

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb2 = ctor.Create('StreamBlock', port)
    sb_list.append(sb2)
    tmpl_list[-1].AddObject(sb2, RelationType('GeneratedObject'))

    assert command.run(cmd.Get('StmTrafficMix'), '', 4, 'FRAMES_PER_SECOND')

    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [3, 1] == load_list
    gen = port.GetObject("Generator")
    assert gen is not None
    gen_conf = gen.GetObject("GeneratorConfig")
    assert gen_conf is not None
    assert gen_conf.Get('schedulingmode') == 'RATE_BASED'

    roots = traf_mix.Get('MixInfo')
    assert roots
    err_str, root = json_utils.load_json(roots)
    assert err_str == ""
    assert 'loadUnits' in root
    assert root['loadUnits'] == 'FRAMES_PER_SECOND'
    assert 'components' in root
    assert len(root['components']) == 2
    assert 'appliedValue' in root['components'][0]
    assert root['components'][0]['appliedValue'] == 3
    assert 'appliedValue' in root['components'][1]
    assert root['components'][1]['appliedValue'] == 1


def test_run_with_tag(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create and tag the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo', mix_info_2_components())
    tag_utils.add_tag_to_object(traf_mix, 'MixTag')

    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())

    tmpl_list = []
    sb_list = []

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb1 = ctor.Create('StreamBlock', port)
    sb_list.append(sb1)
    tmpl_list[-1].AddObject(sb1, RelationType('GeneratedObject'))

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb2 = ctor.Create('StreamBlock', port)
    sb_list.append(sb2)
    tmpl_list[-1].AddObject(sb2, RelationType('GeneratedObject'))

    assert command.run(None, 'MixTag', 4, 'FRAMES_PER_SECOND')

    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [3, 1] == load_list
    gen = port.GetObject("Generator")
    assert gen is not None
    gen_conf = gen.GetObject("GeneratorConfig")
    assert gen_conf is not None
    assert gen_conf.Get('schedulingmode') == 'RATE_BASED'

    roots = traf_mix.Get('MixInfo')
    assert roots
    err_str, root = json_utils.load_json(roots)
    assert err_str == ""
    assert 'loadUnits' in root
    assert root['loadUnits'] == 'FRAMES_PER_SECOND'
    assert 'components' in root
    assert len(root['components']) == 2
    assert 'appliedValue' in root['components'][0]
    assert root['components'][0]['appliedValue'] == 3
    assert 'appliedValue' in root['components'][1]
    assert root['components'][1]['appliedValue'] == 1


def dtest_run_integer_IBG_load_unit(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo', mix_info_2_components())

    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())

    tmpl_list = []
    sb_list = []

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb1 = ctor.Create('StreamBlock', port)
    sb_list.append(sb1)
    tmpl_list[-1].AddObject(sb1, RelationType('GeneratedObject'))

    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb2 = ctor.Create('StreamBlock', port)
    sb_list.append(sb2)
    tmpl_list[-1].AddObject(sb2, RelationType('GeneratedObject'))

    assert command.run(cmd.Get('StmTrafficMix'), '', 4, 'INTER_BURST_GAP')

    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [3, 1] == load_list
    gen = port.GetObject("Generator")
    assert gen is not None
    gen_conf = gen.GetObject("GeneratorConfig")
    assert gen_conf is not None
    assert gen_conf.Get('schedulingmode') == 'PRIORITY_BASED'

    roots = traf_mix.Get('MixInfo')
    assert roots
    err_str, root = json_utils.load_json(roots)
    assert err_str == ""
    assert 'loadUnits' in root
    assert root['loadUnits'] == 'FRAMES_PER_SECOND'
    assert 'components' in root
    assert len(root['components']) == 2
    assert 'appliedValue' in root['components'][0]
    assert root['components'][0]['appliedValue'] == 3
    assert 'appliedValue' in root['components'][1]
    assert root['components'][1]['appliedValue'] == 1


def test_load_adjust_for_kbps_mbps_load(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo', mix_info_3_components())

    tmpl_list = []
    sb_list = []
    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb1 = ctor.Create('StreamBlock', port)
    sb_list.append(sb1)
    tmpl_list[-1].AddObject(sb1, RelationType('GeneratedObject'))
    tmpl_list.append(ctor.Create('StmTemplateConfig', traf_mix))
    sb2 = ctor.Create('StreamBlock', port)
    sb_list.append(sb2)
    tmpl_list[-1].AddObject(sb2, RelationType('GeneratedObject'))
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoadCommand', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    assert command.run(cmd.Get('StmTrafficMix'), '', 0.01, 'KILOBITS_PER_SECOND')

    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [1, 9] == load_list
    load_unit_list = [lp.Get('LoadUnit') for lp in lp_list]
    assert ['BITS_PER_SECOND', 'BITS_PER_SECOND'] == load_unit_list

    mix_info = traf_mix.Get('MixInfo')
    err_str, mix_info = json_utils.load_json(mix_info)
    assert err_str == ""
    mix_info["components"][0]["weight"] = "45.0%"
    mix_info["components"][1]["weight"] = "55.0%"
    mix_info["loadUnits"] = "MEGABITS_PER_SECOND"
    traf_mix.Set('MixInfo', json.dumps(mix_info))
    assert command.run(cmd.Get('StmTrafficMix'), '', 0.01, 'MEGABITS_PER_SECOND')
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [4.5, 5.5] == load_list
    load_unit_list = [lp.Get('LoadUnit') for lp in lp_list]
    assert ['KILOBITS_PER_SECOND', 'KILOBITS_PER_SECOND'] == load_unit_list


def mix_info_2_components():
    return '''
{
  "load": 10,
  "loadUnits": "FRAMES_PER_SECOND",
  "components": [
    {
      "weight": "75%",
      "baseTemplateFile": "abc.xml"
    },
    {
      "weight": "25%",
      "baseTemplateFile": "abc.xml"
    }
  ]
}
'''


def mix_info_3_components():
    return '''
{
  "load": 0.01,
  "loadUnits": "KILOBITS_PER_SECOND",
  "components": [
    {
      "weight": "10%",
      "baseTemplateFile": "abc.xml"
    },
    {
      "weight": "90%",
      "baseTemplateFile": "abc.xml"
    }
  ]
}
'''
