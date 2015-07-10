from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils


PKG = 'spirent.methodology.'
CMD = 'TaggedLinkCreateCommand'


def print_scriptables(obj_list):
    for obj in obj_list:
        tag_list = obj.GetObjects('Tag', RelationType('UserTag'))
        if tag_list:
            tags = ' Tags: ' + ', '.join([t.Get('Name') for t in tag_list])
        else:
            tags = ''
        print '{}: {} ({}){}'.format(obj.GetType(), obj.Get('Name'),
                                     obj.GetObjectHandle(), tags)
        if obj.IsTypeOf('BaseLink'):
            src = obj.GetParent()
            dst = obj.GetObject('Scriptable', RelationType('LinkDstDevice'))
            print '\t{} ({}) -> {} ({})'.format(src.Get('Name'),
                                                src.GetObjectHandle(),
                                                dst.Get('Name'),
                                                dst.GetObjectHandle())


def create_tagged_devices(port, name, count, tag_name):
    ret_hnd_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        if_stack = ['Ipv4If', 'EthIIIf']
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', count)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', if_stack)
        cmd.SetCollection('IfCount', [1] * len(if_stack))
        cmd.Execute()
        ret_hnd_list = cmd.GetCollection('ReturnList')
    hnd_reg = CHandleRegistry.Instance()
    obj_list = [hnd_reg.Find(hnd) for hnd in ret_hnd_list]
    for num, obj in enumerate(obj_list, start=1):
        obj.Set('Name', '{} {}'.format(name, num))
        tag_utils.add_tag_to_object(obj, tag_name)
        ipv4If = obj.GetObject('ipv4if')
        if ipv4If:
            tag_utils.add_tag_to_object(ipv4If, tag_name + "_ttIpv4If")
        ethIf = obj.GetObject('ethiiif')
        if ethIf:
            tag_utils.add_tag_to_object(ethIf, tag_name + "_ttEthIIIf")
    return obj_list


def test_blank_link_type(stc):
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        try:
            # The default has link type as an empty string
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail on '
                             'blank link type'.format(CMD))
    elif 'must not be empty' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_blank_object_tags(stc):
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        try:
            # Test empty SrcObjTag
            cmd.Set('LinkType', 'L3 Forwarding Link')
            cmd.Set('SrcObjTag', '')
            cmd.Set('DstObjTag', 'Front')
            cmd.Set('LinkTag', 'L3Link')
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail on '
                             'blank Source Object Tag'.format(CMD))
    elif 'Source Object Tag is empty' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))

    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        try:
            # Test empty DstObjTag
            cmd.Set('LinkType', 'L3 Forwarding Link')
            cmd.Set('SrcObjTag', 'Back')
            cmd.Set('DstObjTag', '')
            cmd.Set('LinkTag', 'L3Link')
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail on '
                             'blank Destination Object Tag'.format(CMD))
    elif 'Destination Object Tag is empty' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_simple_case(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 1, 'Back')
    front_list = create_tagged_devices(port, 'Front', 1, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # Verifying this one is a simple case, as there is only one link
    # created
    link = link_list[0]
    l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
    assert 1 == len(link_list)
    assert back_list[0].GetObjectHandle() == link.GetParent().GetObjectHandle()
    assert front_list[0].GetObjectHandle() == l_dst.GetObjectHandle()
    # print_scriptables(front_list + back_list + link_list)


def test_pair_equal(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 3, 'Back')
    front_list = create_tagged_devices(port, 'Front', 3, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'PAIR')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # print_scriptables(front_list + back_list + link_list)
    assert 3 == len(link_list)
    for src, dst, link in zip(back_list, front_list, link_list):
        l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
        assert src.GetObjectHandle() == link.GetParent().GetObjectHandle()
        assert dst.GetObjectHandle() == l_dst.GetObjectHandle()


def test_interleaved_equal(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 3, 'Back')
    front_list = create_tagged_devices(port, 'Front', 3, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'INTERLEAVED')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # print_scriptables(front_list + back_list + link_list)
    assert 3 == len(link_list)
    for src, dst, link in zip(back_list, front_list, link_list):
        l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
        assert src.GetObjectHandle() == link.GetParent().GetObjectHandle()
        assert dst.GetObjectHandle() == l_dst.GetObjectHandle()


def test_backbone(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 3, 'Back')
    front_list = create_tagged_devices(port, 'Front', 3, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'BACKBONE')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # print_scriptables(front_list + back_list + link_list)
    assert 9 == len(link_list)
    # Each source device should have the same set of destinations
    exp_dst_hnd = set([x.GetObjectHandle() for x in front_list])
    for src in back_list:
        link_list = src.GetObjects('BaseLink')
        dst_hnd = set([l.GetObject('Scriptable',
                                   RelationType('LinkDstDevice')).
                       GetObjectHandle() for l in link_list])
        assert exp_dst_hnd == dst_hnd


def test_pair_invalid_small(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    # Less back devices than front devices
    create_tagged_devices(port, 'Back', 2, 'Back')
    create_tagged_devices(port, 'Front', 3, 'Front')
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'PAIR')
        cmd.Set('LinkTag', 'L3Link')
        try:
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail with '
                             'too few source devices'.format(CMD))
    elif 'Not enough destination' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_interleaved_invalid_small(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    # Less back devices than front devices
    create_tagged_devices(port, 'Back', 2, 'Back')
    create_tagged_devices(port, 'Front', 3, 'Front')
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'INTERLEAVED')
        cmd.Set('LinkTag', 'L3Link')
        try:
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail with '
                             'too few source devices'.format(CMD))
    elif 'Not enough destination' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_pair_invalid_mismatch(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    # Less back devices than front devices
    create_tagged_devices(port, 'Back', 7, 'Back')
    create_tagged_devices(port, 'Front', 3, 'Front')
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'PAIR')
        cmd.Set('LinkTag', 'L3Link')
        try:
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail with '
                             'too mismatched source devices'.format(CMD))
    elif 'must match or be even' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_interleaved_invalid_mismatch(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    # Less back devices than front devices
    create_tagged_devices(port, 'Back', 7, 'Back')
    create_tagged_devices(port, 'Front', 3, 'Front')
    failed = False
    fail_message = ""
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'INTERLEAVED')
        cmd.Set('LinkTag', 'L3Link')
        try:
            cmd.Execute()
        except RuntimeError as e:
            failed = True
            fail_message = str(e)
    if not failed:
        raise AssertionError('{} did not fail with '
                             'too mismatched source devices'.format(CMD))
    elif 'must match or be even' not in fail_message:
        raise AssertionError('{} failed with unexpected '
                             'error: "{}"'.format(CMD, fail_message))


def test_pair_multiple(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 9, 'Back')
    front_list = create_tagged_devices(port, 'Front', 3, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'PAIR')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # print_scriptables(front_list + back_list + link_list)
    assert 9 == len(link_list)
    # Multiple front_list by 3, for pair
    front_list = [y for y in front_list for _ in range(3)]
    for src, dst, link in zip(back_list, front_list, link_list):
        l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
        assert src.GetObjectHandle() == link.GetParent().GetObjectHandle()
        assert dst.GetObjectHandle() == l_dst.GetObjectHandle()


def test_interleaved_multiple(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 9, 'Back')
    front_list = create_tagged_devices(port, 'Front', 3, 'Front')
    with AutoCommand(PKG + CMD) as cmd:
        cmd.Set('LinkType', 'L3 Forwarding Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('LinkPattern', 'INTERLEAVED')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]
    # print_scriptables(front_list + back_list + link_list)
    assert 9 == len(link_list)
    # Multiple front_list by 3, for interleaved
    front_list = front_list * 3
    for src, dst, link in zip(back_list, front_list, link_list):
        l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
        assert src.GetObjectHandle() == link.GetParent().GetObjectHandle()
        assert dst.GetObjectHandle() == l_dst.GetObjectHandle()


def test_simple_case_interface(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    back_list = create_tagged_devices(port, 'Back', 1, 'Back')
    front_list = create_tagged_devices(port, 'Front', 1, 'Front')

    with AutoCommand(PKG + CMD) as cmd:
        # Custom Interface Link requires a src and dst interface
        cmd.Set('LinkType', 'Custom Interface Link')
        cmd.Set('SrcObjTag', 'Back')
        cmd.Set('SrcIfTag', 'Back_ttEthIIIf')
        cmd.Set('DstObjTag', 'Front')
        cmd.Set('DstIfTag', 'Front_ttEthIIIf')
        cmd.Set('LinkTag', 'L3Link')
        cmd.Execute()
        hnd_list = cmd.GetCollection('LinkList')
    hnd_reg = CHandleRegistry.Instance()
    link_list = [hnd_reg.Find(hnd) for hnd in hnd_list]

    # Verifying this one is a simple case, as there is only one link
    # created
    link = link_list[0]
    l_dst = link.GetObject('Scriptable', RelationType('LinkDstDevice'))
    assert 1 == len(link_list)
    assert back_list[0].GetObjectHandle() == link.GetParent().GetObjectHandle()
    assert front_list[0].GetObjectHandle() == l_dst.GetObjectHandle()

    # Verify Link Src and Dst
    linkSrc = link.GetObject('Scriptable', RelationType('LinkSrc'))
    assert linkSrc.GetObjectHandle() == link.GetParent().GetObject('ethiiif').GetObjectHandle()
    linkDst = link.GetObject('Scriptable', RelationType('LinkDst'))
    assert linkDst.GetObjectHandle() == l_dst.GetObject('ethiiif').GetObjectHandle()
