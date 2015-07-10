from StcIntPythonPL import *
import xml.etree.ElementTree as etree
from mock import MagicMock
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
# For the utils
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent',
                             'methodology'))
import spirent.methodology.traffic.AllocateTrafficMixLoad1Command as command
import spirent.methodology.utils.tag_utils as tag_utils


PKG = 'spirent.methodology.traffic'


def test_run_fail_no_mix(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    seq = stc_sys.GetObject('Sequencer')
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert False is ret


def test_run_fail_invalid_mix(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    command.get_this_cmd = MagicMock(return_value=cmd)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
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
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="" />')
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    mix_elem.set('WeightList', "10.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    # This will fail because we have 1 weight with zero templates
    assert False is ret
    mix_elem.set('WeightList', "15.0 25.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
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
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert True is ret
    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [1.5, 2.5] == load_list


def test_run_integer(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="FRAMES_PER_SECOND" WeightList="" />')
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    mix_elem.set('WeightList', "10.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    cmd.Set('LoadUnit', 'FRAMES_PER_SECOND')
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    # This will fail because we have 1 weight with zero templates
    assert False is ret
    mix_elem.set('WeightList', "15.0 25.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
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
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert True is ret
    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [2, 2] == load_list
    gen = port.GetObject("Generator")
    assert gen is not None
    gen_conf = gen.GetObject("GeneratorConfig")
    assert gen_conf is not None
    assert gen_conf.Get('schedulingmode') == 'RATE_BASED'


def test_run_with_tag(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="" />')
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    mix_elem.set('WeightList', "10.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    tag_utils.add_tag_to_object(traf_mix, 'MixTag')
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    cmd.Set('TagName', 'MixTag')
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    # This will fail because we have 1 weight with zero templates
    assert False is ret
    mix_elem.set('WeightList', "15.0 25.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
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
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert True is ret
    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [1.5, 2.5] == load_list


def test_run_integer_IBG_load_unit(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    proj = stc_sys.GetObject('Project')
    port = ctor.Create('Port', proj)
    seq = stc_sys.GetObject('Sequencer')
    # Create the traffic mix
    traf_mix = ctor.Create('StmTrafficMix', proj)
    traf_mix.Set('MixInfo',
                 '<MixInfo Load="10.0" LoadUnit="INTER_BURST_GAP" WeightList="" />')
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    mix_elem.set('WeightList', "10.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
    cmd = ctor.Create(PKG + '.AllocateTrafficMixLoad1Command', seq)
    cmd.Set('StmTrafficMix', traf_mix.GetObjectHandle())
    cmd.Set('LoadUnit', 'INTER_BURST_GAP')
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    # This will fail because we have 1 weight with zero templates
    assert False is ret
    mix_elem.set('WeightList', "15.0 25.0")
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))
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
    ret = command.run(cmd.Get('StmTrafficMix'), cmd.Get('TagName'),
                      cmd.Get('Load'), cmd.Get('LoadUnit'))
    assert True is ret
    lp_list = [sb.GetObject('StreamBlockLoadProfile',
                            RelationType('AffiliationStreamBlockLoadProfile'))
               for sb in sb_list]
    load_list = [lp.Get('Load') for lp in lp_list]
    assert [2, 2] == load_list
    gen = port.GetObject("Generator")
    assert gen is not None
    gen_conf = gen.GetObject("GeneratorConfig")
    assert gen_conf is not None
    assert gen_conf.Get('schedulingmode') == 'PRIORITY_BASED'
