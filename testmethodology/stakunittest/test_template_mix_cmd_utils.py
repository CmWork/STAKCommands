from StcIntPythonPL import *
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.template_mix_cmd_utils as mix_utils


PKG = 'spirent.methodology'
TPKG = 'spirent.methodology.traffic'


def hierarchy_basic():
    return (PKG + '.IterationGroupCommand', 'iterationGroup',
            [(PKG + '.IteratorConfigMixParamsCommand', 'rowConfigurator', []),
             (PKG + '.CreateTemplateConfigCommand', 'templateConfigurator', [])])


def hierarchy_while():
    return ('SequencerWhileCommand', '', [])


def test_on_complete_remove_tags(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')

    # Create two tags
    tag1 = ctor.Create('Tag', tags)
    tag1.Set('Name', 'Tag1')
    tag2 = ctor.Create('Tag', tags)
    tag2.Set('Name', 'Tag2')

    # Check tags exist
    tag_list = tag_utils.get_tag_objects_from_string_names(['Tag1', 'Tag2'])
    assert len(tag_list) == 2

    # Remove one of the tags and check only one exists
    mix_utils.on_complete_remove_tags('Tag2')
    tag_list = tag_utils.get_tag_objects_from_string_names(['Tag1', 'Tag2'])
    assert len(tag_list) == 1


def test_create_hierarchy_basic(stc):
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Create the parent command
    parent_cmd = ctor.Create(PKG + '.CreateTemplateMixCommand', sequencer)
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 0

    # Call create hierarchy with one child command
    mix_utils.init_create_hierarchy(parent_cmd, hierarchy_basic())

    # Check parent list
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 1

    # Check child command type
    child_cmd_hnd = parent_cmd_list[0]
    child_cmd = hnd_reg.Find(child_cmd_hnd)
    assert child_cmd.GetType().lower() == PKG + '.iterationgroupcommand'

    # Check child list
    child_cmd_list = child_cmd.GetCollection('CommandList')
    assert len(child_cmd_list) == 2

    # Check grandchild command types
    grandchild_cmd_hnd = child_cmd_list[0]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    assert grandchild_cmd.GetType().lower() == PKG + '.iteratorconfigmixparamscommand'
    grandchild_cmd_hnd = child_cmd_list[1]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    assert grandchild_cmd.GetType().lower() == PKG + '.createtemplateconfigcommand'


def test_create_hierarchy_while(stc):
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Create the parent command
    parent_cmd = ctor.Create(PKG + '.CreateTemplateMixCommand', sequencer)
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 0

    # Call create hierarchy with one child command
    hierarchy_while = ('SequencerWhileCommand', '', [])
    mix_utils.init_create_hierarchy(parent_cmd, hierarchy_while)

    # Check parent list
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 1

    # Check child command type
    child_cmd_hnd = parent_cmd_list[0]
    child_cmd = hnd_reg.Find(child_cmd_hnd)
    assert child_cmd.GetType().lower() == 'sequencerwhilecommand'

    # Check while expression command
    exp_cmd_hnd = child_cmd.Get('ExpressionCommand')
    exp_cmd = hnd_reg.Find(exp_cmd_hnd)
    assert exp_cmd.GetType().lower() == PKG + '.objectiteratorcommand'


def test_validate_hierarchy(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Create the parent command
    parent_cmd = ctor.Create(PKG + '.CreateTemplateMixCommand', sequencer)
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 0

    # Call validate with empty tuple list - no error
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [])
    assert msg == ''

    # Call validate with tuple list - error
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_basic()])
    assert msg == 'spirent.methodology.createtemplatemixcommand\'s command list is incorrect'

    # Call create hierarchy with one child command
    mix_utils.init_create_hierarchy(parent_cmd, hierarchy_basic())

    # Call validate with empty tuple list - no error
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [])
    assert msg == ''

    # Call validate - should work
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_basic()])
    assert msg == ''

    # Call validate with extra list element - error
    hierarchy_while = ('SequencerWhileCommand', '', [])
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_basic(), hierarchy_while])
    assert msg == 'spirent.methodology.createtemplatemixcommand\'s command list is incorrect'

    # Call validate with invalid child - error
    hierarchy_invalid_child = (PKG + '.CreateTemplateConfigCommand', '',
                               [(PKG + '.IteratorConfigMixParamsCommand', '', []),
                                (PKG + '.CreateTemplateConfigCommand', '', [])])
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_invalid_child])
    assert msg == 'spirent.methodology.iterationgroupcommand does not match ' + \
                  'expected command of spirent.methodology.createtemplateconfigcommand ' + \
                  'in command list of spirent.methodology.createtemplatemixcommand'

    # Call validate with invalid grandchild - error
    hierarchy_invalid_grandchild = (PKG + '.IterationGroupCommand', '',
                                    [(PKG + '.IteratorConfigMixParamsCommand', '', []),
                                     (PKG + '.LoadTemplateCommand', '', [])])
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_invalid_grandchild])
    assert msg == 'spirent.methodology.createtemplateconfigcommand does not match ' + \
                  'expected command of spirent.methodology.loadtemplatecommand ' + \
                  'in command list of spirent.methodology.iterationgroupcommand'

    # Add an invalid cmd to the parent command list
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 1
    parent_cmd_list.append(0)
    parent_cmd.SetCollection('CommandList', parent_cmd_list)
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 2

    # Call validate - should report error as an invalid cmd exists in parent list
    msg = mix_utils.run_validate_hierarchy(parent_cmd, [hierarchy_basic(), hierarchy_while])
    assert msg == 'spirent.methodology.createtemplatemixcommand has an invalid child command'


def test_tag_hierarchy(stc):
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    assert stc_sys is not None
    sequencer = stc_sys.GetObject("Sequencer")

    # Create the parent command
    parent_cmd = ctor.Create(PKG + '.CreateTemplateMixCommand', sequencer)
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 0

    # Call tag with empty tuples list - tag dict should be empty
    tag_dict = mix_utils.run_tag_hierarchy(parent_cmd, [])
    assert not tag_dict

    # Call create hierarchy with one child command
    mix_utils.init_create_hierarchy(parent_cmd, hierarchy_basic())

    # Call tag with empty tuples list - tag dict should be empty
    tag_dict = mix_utils.run_tag_hierarchy(parent_cmd, [])
    assert not tag_dict

    # Verify commands are not tagged

    # Get parent list
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 1

    # Verify child command is not tagged
    child_cmd_hnd = parent_cmd_list[0]
    child_cmd = hnd_reg.Find(child_cmd_hnd)
    tag = child_cmd.GetObject('Tag', RelationType('UserTag'))
    assert not tag

    # Get child list
    child_cmd_list = child_cmd.GetCollection('CommandList')
    assert len(child_cmd_list) == 2

    # Check grandchild commands are not tagged
    grandchild_cmd_hnd = child_cmd_list[0]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    tag = grandchild_cmd.GetObject('Tag', RelationType('UserTag'))
    assert not tag
    grandchild_cmd_hnd = child_cmd_list[1]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    tag = grandchild_cmd.GetObject('Tag', RelationType('UserTag'))
    assert not tag

    # Call tag with tuples list - tag dict should be populated
    tag_dict = mix_utils.run_tag_hierarchy(parent_cmd, [hierarchy_basic()])
    assert tag_dict

    # Verify tag_dict is correct
    assert tag_dict
    assert 'spirent.methodology.iterationgroupcommand.' in tag_dict['iterationGroup']
    assert 'spirent.methodology.iteratorconfigmixparamscommand.' in tag_dict['rowConfigurator']
    assert 'spirent.methodology.createtemplateconfigcommand.' in tag_dict['templateConfigurator']

    # Verify commands are tagged

    # Get parent list
    parent_cmd_list = parent_cmd.GetCollection('CommandList')
    assert len(parent_cmd_list) == 1

    # Verify child command is tagged
    child_cmd_hnd = parent_cmd_list[0]
    child_cmd = hnd_reg.Find(child_cmd_hnd)
    tag = child_cmd.GetObject('Tag', RelationType('UserTag'))
    assert tag
    assert 'spirent.methodology.iterationgroupcommand.' in tag.Get('Name')

    # Get child list
    child_cmd_list = child_cmd.GetCollection('CommandList')
    assert len(child_cmd_list) == 2

    # Check grandchild commands are tagged
    grandchild_cmd_hnd = child_cmd_list[0]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    tag = grandchild_cmd.GetObject('Tag', RelationType('UserTag'))
    assert tag
    assert 'spirent.methodology.iteratorconfigmixparamscommand.' in tag.Get('Name')
    grandchild_cmd_hnd = child_cmd_list[1]
    grandchild_cmd = hnd_reg.Find(grandchild_cmd_hnd)
    tag = grandchild_cmd.GetObject('Tag', RelationType('UserTag'))
    assert tag
    assert 'spirent.methodology.createtemplateconfigcommand.' in tag.Get('Name')
