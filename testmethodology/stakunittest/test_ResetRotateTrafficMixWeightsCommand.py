from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))


PKG = 'spirent.methodology'


def test_std_iteration(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand(PKG + ".ResetRotateTrafficMixWeightsCommand")

    mix = {'Load': '0.0', 'LoadUnit': '', 'WeightList': '3 1 2', 'OriginalWeightList': '1 2 3'}
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

    cmd.SetCollection('TrafficMixTagList', ['mix'])
    cmd.SetCollection('ObjectList', [project.GetObjectHandle()])
    cmd.Execute()
    e = etree.fromstring(trfx.Get('MixInfo'))
    assert e.get('WeightList') == '1 2 3'
    assert e.get('OriginalWeightList') == '1 2 3'

    cmd.MarkDelete()
