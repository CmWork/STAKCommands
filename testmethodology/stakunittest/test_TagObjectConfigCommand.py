from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils
import sys
import traceback


CMD = 'spirent.methodology.TagObjectConfigCommand'


def test_run_scalar(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('Project')
    # Set up tagged objects
    port = ctor.Create('Port', proj)
    for num in range(0, 4):
        with AutoCommand('DeviceCreateCommand') as cmd:
            cmd.Set('Port', port.GetObjectHandle())
            cmd.Set('DeviceCount', 1)
            cmd.Set('CreateCount', 1)
            cmd.Set('DeviceType', 'EmulatedDevice')
            cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
            cmd.SetCollection('IfCount', [1, 1])
            cmd.Execute()
    dev_list = proj.GetObjects('EmulatedDevice')
    assert 4 == len(dev_list)
    cmd = ctor.CreateCommand(CMD)
    curr_val = str(dev_list[0].GetObjectHandle())
    cmd.SetCollection('TagNameList', ['Sample'])
    cmd.Set('CurrVal', curr_val)
    cmd.Set('Iteration', 1)
    cmd.Execute()
    sample_tag = tag_utils.get_tag_object('Sample')
    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]
    assert 1 == len(targ_list)
    assert dev_list[0].GetObjectHandle() == targ_list[0]
    cmd.Reset()
    # Call it again, with another handle
    curr_val = str(dev_list[1].GetObjectHandle())
    cmd.SetCollection('TagNameList', ['Sample'])
    cmd.Set('CurrVal', curr_val)
    cmd.Set('Iteration', 2)
    cmd.Execute()
    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]
    assert 1 == len(targ_list)
    assert dev_list[1].GetObjectHandle() == targ_list[0]

    # Clean up
    cmd.MarkDelete()


def test_run_tuple(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('Project')
    # Set up tagged objects
    port = ctor.Create('Port', proj)
    for num in range(0, 4):
        with AutoCommand('DeviceCreateCommand') as cmd:
            cmd.Set('Port', port.GetObjectHandle())
            cmd.Set('DeviceCount', 1)
            cmd.Set('CreateCount', 1)
            cmd.Set('DeviceType', 'EmulatedDevice')
            cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
            cmd.SetCollection('IfCount', [1, 1])
            cmd.Execute()
    dev_list = proj.GetObjects('EmulatedDevice')
    assert 4 == len(dev_list)
    cmd = ctor.CreateCommand(CMD)
    curr_val = str(dev_list[0].GetObjectHandle()) + ',' + \
        str(dev_list[2].GetObjectHandle())
    cmd.SetCollection('TagNameList', ['Sample', 'Dest'])
    cmd.Set('CurrVal', curr_val)
    cmd.Set('Iteration', 1)
    cmd.Execute()
    sample_tag = tag_utils.get_tag_object('Sample')
    dest_tag = tag_utils.get_tag_object('Dest')
    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]
    targ2_list = dest_tag.GetObjects('Scriptable',
                                     RelationType('UserTag', True))
    # Remove 'Tags'
    targ2_list = [o.GetObjectHandle() for o in targ2_list if not o.IsTypeOf('Tags')]

    # Verify
    assert 1 == len(targ_list)
    assert dev_list[0].GetObjectHandle() == targ_list[0]
    assert 1 == len(targ2_list)
    assert dev_list[2].GetObjectHandle() == targ2_list[0]
    cmd.Reset()
    # Call it again, with another handle
    curr_val = str(dev_list[1].GetObjectHandle()) + ',' + \
        str(dev_list[3].GetObjectHandle())
    cmd.SetCollection('TagNameList', ['Sample', 'Dest'])
    cmd.Set('CurrVal', curr_val)
    cmd.Set('Iteration', 2)
    cmd.Execute()
    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]

    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]
    targ2_list = dest_tag.GetObjects('Scriptable',
                                     RelationType('UserTag', True))
    # Remove 'Tags'
    targ2_list = [o.GetObjectHandle() for o in targ2_list if not o.IsTypeOf('Tags')]

    # Verify
    assert 1 == len(targ_list)
    assert dev_list[1].GetObjectHandle() == targ_list[0]
    assert 1 == len(targ2_list)
    assert dev_list[3].GetObjectHandle() == targ2_list[0]
    # Clean up
    cmd.MarkDelete()


def test_run_tuple_mismatch(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('Project')
    # Set up tagged objects
    port = ctor.Create('Port', proj)
    for num in range(0, 4):
        with AutoCommand('DeviceCreateCommand') as cmd:
            cmd.Set('Port', port.GetObjectHandle())
            cmd.Set('DeviceCount', 1)
            cmd.Set('CreateCount', 1)
            cmd.Set('DeviceType', 'EmulatedDevice')
            cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
            cmd.SetCollection('IfCount', [1, 1])
            cmd.Execute()
    dev_list = proj.GetObjects('EmulatedDevice')
    assert 4 == len(dev_list)
    cmd = ctor.CreateCommand(CMD)
    curr_val = str(dev_list[0].GetObjectHandle()) + ',' + \
        str(dev_list[2].GetObjectHandle())
    # Only one tag value given
    cmd.SetCollection('TagNameList', ['Sample'])
    cmd.Set('CurrVal', curr_val)
    try:
        cmd.Execute()
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(*exc_info[0:2])
        fail_msg = fail_list[0] if len(fail_list) == 1 else '\n'.join(fail_list)
    finally:
        cmd.MarkDelete()
    if fail_msg == '':
        raise AssertionError('Command did not fail as expected')
    if 'Not enough tag names' not in fail_msg:
        raise AssertionError('Command failed with unexpected exception: "' +
                             fail_msg + '"')
    cmd.Reset()
    curr_val = str(dev_list[0].GetObjectHandle())
    # Only one tag value given
    cmd.SetCollection('TagNameList', ['Sample', 'Dest'])
    cmd.Set('CurrVal', curr_val)
    # Should be ok if we have more tags than values
    cmd.Execute()
    sample_tag = tag_utils.get_tag_object('Sample')
    dest_tag = tag_utils.get_tag_object('Dest')
    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]

    targ_list = sample_tag.GetObjects('Scriptable',
                                      RelationType('UserTag', True))
    # Remove 'Tags'
    targ_list = [o.GetObjectHandle() for o in targ_list if not o.IsTypeOf('Tags')]
    targ2_list = dest_tag.GetObjects('Scriptable',
                                     RelationType('UserTag', True))
    # Remove 'Tags'
    targ2_list = [o.GetObjectHandle() for o in targ2_list if not o.IsTypeOf('Tags')]

    # Verify
    assert 1 == len(targ_list)
    assert dev_list[0].GetObjectHandle() == targ_list[0]
    assert 0 == len(targ2_list)
