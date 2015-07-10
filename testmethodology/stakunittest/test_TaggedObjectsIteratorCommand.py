from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils
import sys
import traceback


CMD = 'spirent.methodology.TaggedObjectsIteratorCommand'


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
    tag_utils.add_tag_to_object(dev_list[0], 'Group A')
    tag_utils.add_tag_to_object(dev_list[1], 'Group A')
    tag_utils.add_tag_to_object(dev_list[2], 'Group B')
    tag_utils.add_tag_to_object(dev_list[3], 'Group B')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Group A'])
    cmd.Set('ObjectOrder', 'SCALAR')
    cmd.Execute()
    # Pass 1
    assert 1 == cmd.Get('Iteration')
    assert str(dev_list[0].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    # Need reset for next run
    cmd.Reset()
    cmd.Execute()
    # Pass 2
    assert 2 == cmd.Get('Iteration')
    assert str(dev_list[1].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    cmd.Reset()
    cmd.Execute()
    # Pass 3
    assert 2 == cmd.Get('Iteration')
    assert str(dev_list[1].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'FAILED' == cmd.Get('PassFailState')
    cmd.MarkDelete()


def test_run_scalar_multi(stc):
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
    tag_utils.add_tag_to_object(dev_list[0], 'Group A')
    tag_utils.add_tag_to_object(dev_list[1], 'Group A')
    tag_utils.add_tag_to_object(dev_list[2], 'Group B')
    tag_utils.add_tag_to_object(dev_list[3], 'Group B')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Group A', 'Group B'])
    cmd.Set('ObjectOrder', 'SCALAR')
    cmd.Execute()
    # Pass 1
    assert 1 == cmd.Get('Iteration')
    assert str(dev_list[0].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    # Need reset for next run
    cmd.Reset()
    cmd.Execute()
    # Pass 2
    assert 2 == cmd.Get('Iteration')
    assert str(dev_list[1].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    cmd.Reset()
    cmd.Execute()
    # Pass 3
    assert 3 == cmd.Get('Iteration')
    assert str(dev_list[2].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    cmd.Reset()
    cmd.Execute()
    # Pass 4
    assert 4 == cmd.Get('Iteration')
    assert str(dev_list[3].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    cmd.Reset()
    cmd.Execute()
    # Pass 5
    assert 4 == cmd.Get('Iteration')
    assert str(dev_list[3].GetObjectHandle()) == cmd.Get('CurrVal')
    assert 'FAILED' == cmd.Get('PassFailState')
    cmd.MarkDelete()


def test_run_scalar_empty(stc):
    ctor = CScriptableCreator()
    tag_utils.get_tag_object('Nothing')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Nothing'])
    cmd.Set('ObjectOrder', 'SCALAR')
    cmd.Execute()
    # Pass 1
    assert 0 == cmd.Get('Iteration')
    assert '' == cmd.Get('CurrVal')
    assert 'FAILED' == cmd.Get('PassFailState')
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
    tag_utils.add_tag_to_object(dev_list[0], 'Group A')
    tag_utils.add_tag_to_object(dev_list[1], 'Group A')
    tag_utils.add_tag_to_object(dev_list[2], 'Group B')
    tag_utils.add_tag_to_object(dev_list[3], 'Group B')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Group A', 'Group B'])
    cmd.Set('ObjectOrder', 'TUPLE')
    cmd.Execute()
    # Pass 1
    assert 1 == cmd.Get('Iteration')
    cur = ','.join([str(dev_list[0].GetObjectHandle()),
                    str(dev_list[2].GetObjectHandle())])
    assert cur == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    # Need reset for next run
    cmd.Reset()
    cmd.Execute()
    # Pass 2
    assert 2 == cmd.Get('Iteration')
    cur = ','.join([str(dev_list[1].GetObjectHandle()),
                    str(dev_list[3].GetObjectHandle())])
    assert cur == cmd.Get('CurrVal')
    assert 'PASSED' == cmd.Get('PassFailState')
    cmd.Reset()
    cmd.Execute()
    # Pass 3
    assert 2 == cmd.Get('Iteration')
    assert cur == cmd.Get('CurrVal')
    assert 'FAILED' == cmd.Get('PassFailState')
    cmd.MarkDelete()


def test_run_tuple_empty(stc):
    ctor = CScriptableCreator()
    tag_utils.get_tag_object('Nothing')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Nothing', 'Nothing'])
    cmd.Set('ObjectOrder', 'SCALAR')
    cmd.Execute()
    # Pass 1
    assert 0 == cmd.Get('Iteration')
    assert '' == cmd.Get('CurrVal')
    assert 'FAILED' == cmd.Get('PassFailState')
    cmd.MarkDelete()


def test_run_tuple_invalid(stc):
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
    tag_utils.add_tag_to_object(dev_list[0], 'Group A')
    tag_utils.add_tag_to_object(dev_list[1], 'Group A')
    tag_utils.add_tag_to_object(dev_list[2], 'Group B')
    tag_utils.add_tag_to_object(dev_list[3], 'Group B')

    # Most of the parameters from the base class are ignored
    cmd = ctor.CreateCommand(CMD)
    cmd.SetCollection('TagNameList', ['Group A'])
    cmd.Set('ObjectOrder', 'TUPLE')
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
    if 'only got one' not in fail_msg:
        raise AssertionError('Command failed with unexpected exception: "' +
                             fail_msg + '"')
