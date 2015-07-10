from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands',
                             'spirent', 'methodology'))


def test_bad_relation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    src_obj = ctor.Create("EmulatedDevice", project)
    assert src_obj is not None
    targ_obj = ctor.Create("EmulatedDevice", project)
    assert targ_obj is not None

    src_tag = ctor.Create("Tag", tags)
    src_tag.Set("Name", "SrcTagName")
    src_obj.AddObject(src_tag, RelationType("UserTag"))
    tags.AddObject(src_tag, RelationType("UserTag"))

    targ_tag = ctor.Create("Tag", tags)
    targ_tag.Set("Name", "TargTagName")
    targ_obj.AddObject(targ_tag, RelationType("UserTag"))
    tags.AddObject(targ_tag, RelationType("UserTag"))

    failed = False
    fail_message = ""
    # Add a fake relation
    with AutoCommand(pkg + '.ConfigRelationCommand') as cmd:
        cmd.Set('SrcTagName', 'SrcTagName')
        cmd.Set('TargetTagName', 'TargTagName')
        cmd.Set('RelationName', 'FakeRelation')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError as e:
            fail_message = str(e)
            if 'not a valid relation' in fail_message:
                failed = True
    if not failed:
        if fail_message != "":
            raise AssertionError('ConfigRelationCommand failed with ' +
                                 'unexpected error: "' + fail_message + '"')
        else:
            raise AssertionError('ConfigRelationCommand did not ' +
                                 'fail as expected')


def test_good_relation(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    src_obj = ctor.Create("EmulatedDevice", project)
    assert src_obj is not None
    targ_obj = ctor.Create("Port", project)
    assert targ_obj is not None

    src_tag = ctor.Create("Tag", tags)
    src_tag.Set("Name", "SrcTagName")
    src_obj.AddObject(src_tag, RelationType("UserTag"))
    tags.AddObject(src_tag, RelationType("UserTag"))

    targ_tag = ctor.Create("Tag", tags)
    targ_tag.Set("Name", "TargTagName")
    targ_obj.AddObject(targ_tag, RelationType("UserTag"))
    tags.AddObject(targ_tag, RelationType("UserTag"))

    failed = False
    # Add a fake relation
    with AutoCommand(pkg + '.ConfigRelationCommand') as cmd:
        cmd.Set('SrcTagName', 'SrcTagName')
        cmd.Set('TargetTagName', 'TargTagName')
        cmd.Set('RelationName', 'AffiliationPort')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError:
            failed = True
    assert not failed

    assert (src_obj.GetObject('Port', RelationType('AffiliationPort')).GetObjectHandle()
            == targ_obj.GetObjectHandle())


def test_srcdst_binding(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    ctor = CScriptableCreator()

    pkg = 'spirent.methodology'

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    port_obj = ctor.Create("Port", project)
    assert port_obj is not None
    sb_obj = ctor.Create("StreamBlock", port_obj)
    assert sb_obj is not None

    # SrcBinding side
    src_dev = ctor.Create("EmulatedDevice", project)
    assert src_dev is not None
    src_if = ctor.Create("Ipv4If", src_dev)
    assert src_if is not None

    src_tag = ctor.Create("Tag", tags)
    src_tag.Set("Name", "SrcBindingFromTagName")
    sb_obj.AddObject(src_tag, RelationType("UserTag"))
    tags.AddObject(src_tag, RelationType("UserTag"))
    targ_tag = ctor.Create("Tag", tags)
    targ_tag.Set("Name", "SrcBindingToTagName")
    src_if.AddObject(targ_tag, RelationType("UserTag"))
    tags.AddObject(targ_tag, RelationType("UserTag"))

    failed = False
    with AutoCommand(pkg + '.ConfigRelationCommand') as cmd:
        cmd.Set('SrcTagName', 'SrcBindingFromTagName')
        cmd.Set('TargetTagName', 'SrcBindingToTagName')
        cmd.Set('RelationName', 'SrcBinding')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError:
            failed = True
    assert not failed

    ret_if = sb_obj.GetObject('Ipv4If', RelationType('SrcBinding'))
    assert (ret_if.GetObjectHandle() == src_if.GetObjectHandle())

    # DstBinding side
    dst_dev = ctor.Create("EmulatedDevice", project)
    assert dst_dev is not None
    dst_if = ctor.Create("Ipv4If", dst_dev)
    assert dst_if is not None

    src_tag = ctor.Create("Tag", tags)
    src_tag.Set("Name", "DstBindingFromTagName")
    sb_obj.AddObject(src_tag, RelationType("UserTag"))
    tags.AddObject(src_tag, RelationType("UserTag"))
    targ_tag = ctor.Create("Tag", tags)
    targ_tag.Set("Name", "DstBindingToTagName")
    dst_if.AddObject(targ_tag, RelationType("UserTag"))
    tags.AddObject(targ_tag, RelationType("UserTag"))

    failed = False
    with AutoCommand(pkg + '.ConfigRelationCommand') as cmd:
        cmd.Set('SrcTagName', 'DstBindingFromTagName')
        cmd.Set('TargetTagName', 'DstBindingToTagName')
        cmd.Set('RelationName', 'DstBinding')
        cmd.Set('RemoveRelation', False)
        try:
            cmd.Execute()
        except RuntimeError:
            failed = True
    assert not failed

    ret_if = sb_obj.GetObject('Ipv4If', RelationType('DstBinding'))
    assert (ret_if.GetObjectHandle() == dst_if.GetObjectHandle())
