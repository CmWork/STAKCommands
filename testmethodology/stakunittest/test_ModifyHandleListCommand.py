from StcIntPythonPL import *
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
# import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.ModifyHandleListCommand as ModListCmd
from mock import MagicMock


def test_validate(stc):
    res = ModListCmd.validate(None, None, None, False)
    assert res.startswith("ERROR: Must provide")

    res = ModListCmd.validate("someBllCommandTagName", None, None, False)
    assert res.startswith("ERROR: Must provide")

    res = ModListCmd.validate("someBllCommandTagName", "somePropertyName", None, False)
    assert res.startswith("ERROR: Must provide")

    res = ModListCmd.validate("someBllCommandTagName", "somePropertyName", ["ForObject"], False)
    assert res.startswith("ERROR: Nothing is tagged")

    # Make some miscellaneous object, pointed to by a Tag
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    tagForObj = ctor.Create('Tag', tags)
    tagForObj.Set('Name', 'ForObject')
    sequencer.AddObject(tagForObj, RelationType('UserTag'))

    res = ModListCmd.validate("ForObject", "fakePropertyName", ["ForObject"], False)
    assert res.startswith("ERROR: fakePropertyName is not a valid property")

    res = ModListCmd.validate("ForObject", "CurrentCommand", ["ForObject"], False)
    assert res.startswith("ERROR: CurrentCommand is not a collection")

    res = ModListCmd.validate("ForObject", "CommandList", ["ForObject"], False)
    assert res == ""

    return


def test_basic_tag(stc):

    # Initilize Tags
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    sequencer = CStcSystem.Instance().GetObject("Sequencer")

    # Make a command with a property to be modified
    targetCmd = ctor.Create('BgpImportRouteTableCommand', sequencer)
    targetCmd.SetCollection('RouterList', [1001])
    assert len(targetCmd.GetCollection('RouterList')) == 1

    # Make an Tag for the command
    tagForCmd = ctor.Create('Tag', tags)
    tagForCmd.Set('Name', 'ForCommand')
    targetCmd.AddObject(tagForCmd, RelationType('UserTag'))

    # Make some miscellaneous object, pointed to by a Tag
    port = ctor.Create('Port', project)
    tagForObj = ctor.Create('Tag', tags)
    tagForObj.Set('Name', 'ForObject')
    port.AddObject(tagForObj, RelationType('UserTag'))

    # Append the object to the command property with ModifyHandleListCommand
    pkg = "spirent.methodology"
    modCmd = ctor.Create(pkg + ".ModifyHandleListCommand", sequencer)
    ModListCmd.get_this_cmd = MagicMock(return_value=modCmd)
    ModListCmd.run('ForCommand', 'RouterList', ['ForObject'], False)
    assert len(targetCmd.GetCollection('RouterList')) == 2

    ModListCmd.run('ForCommand', 'RouterList', ['ForObject'], True)
    assert len(targetCmd.GetCollection('RouterList')) == 1