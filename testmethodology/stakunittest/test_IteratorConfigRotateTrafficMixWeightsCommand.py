from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))


PKG = 'spirent.methodology'


def test_std_iteration(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(PKG + ".IteratorConfigRotateTrafficMixWeightsCommand")

    mix = {'Load': '0.0', 'LoadUnit': '', 'WeightList': '1 2 3 4 5'}
    mixi = etree.tostring(etree.Element('MixInfo', mix))

    # Add some port group tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "mix")

    # Create the StmTrafficMix object...
    trfx = ctor.Create('StmTrafficMix', project)
    assert trfx is not None
    trfx.AddObject(tag, RelationType("UserTag"))
    trfx.Set('MixInfo', mixi)

    cmd.Set('Iteration', 1)
    cmd.Set('CurrVal', '1')
    cmd.SetCollection('TagList', ['mix'])
    cmd.SetCollection('ObjectList', [project.GetObjectHandle()])
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '5 1 2 3 4'
    assert e.get('OriginalWeightList') == '1 2 3 4 5'

    cmd.Reset()
    cmd.Set('CurrVal', '3')
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '3 4 5 1 2'
    assert e.get('OriginalWeightList') == '1 2 3 4 5'

    cmd.Reset()
    cmd.Set('CurrVal', '9')
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '1 2 3 4 5'
    assert e.get('OriginalWeightList') == '1 2 3 4 5'

    cmd.Reset()
    cmd.Set('CurrVal', '-1')
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '2 3 4 5 1'
    assert e.get('OriginalWeightList') == '1 2 3 4 5'

    cmd.Reset()
    cmd.Set('CurrVal', '2')
    cmd.Set('Iteration', 2)
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '4 5 1 2 3'
    assert e.get('OriginalWeightList') == '1 2 3 4 5'

    cmd.MarkDelete()
