from StcIntPythonPL import *
import sys
import os
import traceback
from spirent.core.utils.scriptable import AutoCommand

sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import spirent.methodology.utils.tag_utils as tag_utils


def create_port_with_ipv4_device(ctor, project):
    port = ctor.Create('Port', project)
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 1)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()

    return port


def test_tag_id_wrong_thing(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    port = create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    # Project should never be tagged
    project.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 0
    project.RemoveObject(tag, RelationType('UserTag'))
    # Port neither
    port.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 0


def test_tag_id_device(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    device.AddObject(tag, RelationType('UserTag'))
    ipv4 = device.GetObject('Ipv4If', RelationType('TopLevelIf'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == ipv4.GetObjectHandle()


def test_tag_id_interface(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    ipv4 = device.GetObject('Ipv4If')
    ipv4.AddObject(tag, RelationType('UserTag'))
    eth = device.GetObject('EthIIIf')
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == ipv4.GetObjectHandle()
    ipv4.RemoveObject(tag, RelationType('UserTag'))
    eth.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == eth.GetObjectHandle()


def test_tag_id_route(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    bgp = ctor.Create('BgpRouterConfig', device)
    bgproute = ctor.Create('BgpIpv4RouteConfig', bgp)
    nb = bgproute.GetObject('Ipv4NetworkBlock')
    assert nb
    bgproute.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == nb.GetObjectHandle()


def test_tag_id_mcast_group(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    v4grp = ctor.Create('Ipv4Group', project)
    assert v4grp
    nb = v4grp.GetObject('Ipv4NetworkBlock')
    assert nb
    v4grp.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_ids([tag.GetObjectHandle()])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == nb.GetObjectHandle()


def test_tag_name_wrong_thing(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    port = create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    # Project should never be tagged
    project.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 0
    project.RemoveObject(tag, RelationType('UserTag'))
    # Port neither
    port.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 0


def test_tag_name_device(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    device.AddObject(tag, RelationType('UserTag'))
    ipv4 = device.GetObject('Ipv4If', RelationType('TopLevelIf'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == ipv4.GetObjectHandle()


def test_tag_name_interface(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    ipv4 = device.GetObject('Ipv4If')
    ipv4.AddObject(tag, RelationType('UserTag'))
    eth = device.GetObject('EthIIIf')
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == ipv4.GetObjectHandle()
    ipv4.RemoveObject(tag, RelationType('UserTag'))
    eth.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == eth.GetObjectHandle()


def test_tag_name_route(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    create_port_with_ipv4_device(ctor, project)
    device = project.GetObject('EmulatedDevice')
    assert device
    bgp = ctor.Create('BgpRouterConfig', device)
    bgproute = ctor.Create('BgpIpv4RouteConfig', bgp)
    nb = bgproute.GetObject('Ipv4NetworkBlock')
    assert nb
    bgproute.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == nb.GetObjectHandle()


def test_tag_mcast_group(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    tags = project.GetObject('Tags')
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'Sample')
    v4grp = ctor.Create('Ipv4Group', project)
    assert v4grp
    nb = v4grp.GetObject('Ipv4NetworkBlock')
    assert nb
    v4grp.AddObject(tag, RelationType('UserTag'))
    got_list = tag_utils.get_tagged_endpoints_given_tag_names([tag.Get("Name")])
    assert len(got_list) == 1
    assert got_list[0].GetObjectHandle() == nb.GetObjectHandle()


def test_get_tagged_objects(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)
    port3 = ctor.Create("Port", project)

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "EastPortGroup")
    port1.AddObject(tag1, RelationType("UserTag"))
    port2.AddObject(tag1, RelationType("UserTag"))
    tags.AddObject(tag1, RelationType("UserTag"))

    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "WestPortGroup")
    port2.AddObject(tag2, RelationType("UserTag"))
    port3.AddObject(tag2, RelationType("UserTag"))
    tags.AddObject(tag2, RelationType("UserTag"))

    res = tag_utils.get_tagged_objects([tag1])
    assert len(res) == 2
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 1
    assert port3_count == 0
    assert tags_count == 0

    res = tag_utils.get_tagged_objects([tag1], ignore_tags_obj=False)
    assert len(res) == 3
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 1
    assert port3_count == 0
    assert tags_count == 1

    # Note that the Tags object will appear twice in this test due
    # to it coming from both tag1 and tag2
    res = tag_utils.get_tagged_objects([tag1, tag2],
                                       ignore_tags_obj=False,
                                       remove_duplicates=False)
    assert len(res) == 6
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 2
    assert port3_count == 1
    assert tags_count == 2

    # Tags object will not appear in the results of this call
    # but port2 will appear twice
    res = tag_utils.get_tagged_objects([tag1, tag2],
                                       remove_duplicates=False)
    assert len(res) == 4
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 2
    assert port3_count == 1
    assert tags_count == 0

    # Test filtering on class_name (with duplicates)
    # class_name takes precedence over ignore_tags_obj
    res = tag_utils.get_tagged_objects([tag1, tag2],
                                       ignore_tags_obj=False,
                                       remove_duplicates=False,
                                       class_name="Port")
    assert len(res) == 4
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 2
    assert port3_count == 1
    assert tags_count == 0

    # Test filtering on class_name (without duplicates)
    # class_name takes precedence over ignore_tags_obj
    res = tag_utils.get_tagged_objects([tag1, tag2],
                                       ignore_tags_obj=True,
                                       class_name="Port",
                                       remove_duplicates=True)
    assert len(res) == 3
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 1
    assert port3_count == 1
    assert tags_count == 0


def test_is_any_empty_tags(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "EastPortGroup")
    port1.AddObject(tag1, RelationType("UserTag"))
    port2.AddObject(tag1, RelationType("UserTag"))
    tags.AddObject(tag1, RelationType("UserTag"))

    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "WestPortGroup")
    tags.AddObject(tag2, RelationType("UserTag"))

    res = tag_utils.is_any_empty_tags([], "Port")
    assert not res
    res = tag_utils.is_any_empty_tags([tag1], "Port")
    assert not res
    res = tag_utils.is_any_empty_tags([tag2], "Port")
    assert res
    res = tag_utils.is_any_empty_tags([tag1, tag2], "Port")
    assert res
    res = tag_utils.is_any_empty_tags([tag1], "EmulatedDevice")
    assert res


def test_get_tagged_objects_from_string_names(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)
    port3 = ctor.Create("Port", project)

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "EastPortGroup")
    port1.AddObject(tag1, RelationType("UserTag"))
    port2.AddObject(tag1, RelationType("UserTag"))
    tags.AddObject(tag1, RelationType("UserTag"))

    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "West Port Group")
    port2.AddObject(tag2, RelationType("UserTag"))
    port3.AddObject(tag2, RelationType("UserTag"))
    tags.AddObject(tag2, RelationType("UserTag"))

    res = tag_utils.get_tagged_objects_from_string_names(["EastPortGroup"])
    assert len(res) == 2
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 1
    assert port3_count == 0
    assert tags_count == 0

    res = tag_utils.get_tagged_objects_from_string_names(
        ["EastPortGroup"], ignore_tags_obj=False)
    assert len(res) == 3
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 1
    assert port3_count == 0
    assert tags_count == 1

    # Note that the Tags object will appear twice in this test due
    # to it coming from both tag1 and tag2
    res = tag_utils.get_tagged_objects_from_string_names(
        ["EastPortGroup", "West Port Group"],
        ignore_tags_obj=False,
        remove_duplicates=False)
    assert len(res) == 6
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 2
    assert port3_count == 1
    assert tags_count == 2

    # Tags object will not appear in the results of this call
    # but port2 will appear twice
    res = tag_utils.get_tagged_objects_from_string_names(
        ["EastPortGroup", "West Port Group"],
        remove_duplicates=False)
    assert len(res) == 4
    port1_count = 0
    port2_count = 0
    port3_count = 0
    tags_count = 0
    for item in res:
        if item.GetObjectHandle() == port1.GetObjectHandle():
            port1_count = port1_count + 1
        elif item.GetObjectHandle() == port2.GetObjectHandle():
            port2_count = port2_count + 1
        elif item.GetObjectHandle() == port3.GetObjectHandle():
            port3_count = port3_count + 1
        elif item.GetObjectHandle() == tags.GetObjectHandle():
            tags_count = tags_count + 1
    assert port1_count == 1
    assert port2_count == 2
    assert port3_count == 1
    assert tags_count == 0


def test_get_tag_objects_from_string_names(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Tag1")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Tag2")
    tag3 = ctor.Create("Tag", tags)
    tag3.Set("Name", "Another Tag")

    tlist = tag_utils.get_tag_objects_from_string_names(["Tag1"])
    assert len(tlist) == 1
    assert tlist[0].GetObjectHandle() == tag1.GetObjectHandle()

    tlist = tag_utils.get_tag_objects_from_string_names(["Tag1",
                                                        "Another Tag"])
    assert len(tlist) == 2
    found_tag1 = False
    found_tag3 = False
    for tag in tlist:
        if tag.GetObjectHandle() == tag1.GetObjectHandle():
            found_tag1 = True
        elif tag.GetObjectHandle() == tag3.GetObjectHandle():
            found_tag3 = True
    assert found_tag1
    assert found_tag3

    # Invalid tag name
    tlist = tag_utils.get_tag_objects_from_string_names(["Tag12"])
    assert len(tlist) == 0
    tlist = tag_utils.get_tag_objects_from_string_names(["Tag1",
                                                        "Tag12"])
    assert len(tlist) == 1
    assert tlist[0].GetObjectHandle() == tag1.GetObjectHandle()


def test_get_tag_objects_blank(stc):
    fail_msg = ''
    try:
        tag_utils.get_tag_object('')
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(exc_info[0],
                                                    exc_info[1])
        fail_msg = fail_list[0] if len(fail_list) == 1 else '\n'.join(fail_list)
    if fail_msg == '':
        raise AssertionError('function did not fail as expected')
    if 'must not be blank' not in fail_msg:
        raise AssertionError('function failed with unexpected exception: "' +
                             fail_msg + '"')
    try:
        tag_utils.get_tag_object_list(['non-blank', ''])
    except:
        exc_info = sys.exc_info()
        fail_list = traceback.format_exception_only(exc_info[0],
                                                    exc_info[1])
        fail_msg = fail_list[0] if len(fail_list) == 1 else '\n'.join(fail_list)
    if fail_msg == '':
        raise AssertionError('function did not fail as expected')
    if 'must not be blank' not in fail_msg:
        raise AssertionError('function failed with unexpected exception: "' +
                             fail_msg + '"')


def test_get_tag_object(stc):
    proj = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()

    tags = proj.GetObject('Tags')
    if tags is None:
        tags = ctor.Create('Tags', project)
    assert tags is not None

    exist_map = {obj.Get('Name'): obj for obj in tags.GetObjects('Tag')}
    # Create new
    tag = tag_utils.get_tag_object('Tag1')
    assert not isinstance(tag, list)
    assert tag.IsTypeOf('Tag')
    assert 'Tag1' == tag.Get('Name')
    assert 'Tag1' not in exist_map

    # Retrieve existing
    tag2 = tag_utils.get_tag_object('Tag1')
    assert tag.GetObjectHandle() == tag2.GetObjectHandle()
    assert 'Tag1' == tag2.Get('Name')


def test_get_tag_object_list(stc):
    proj = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()

    tags = proj.GetObject('Tags')
    if tags is None:
        tags = ctor.Create('Tags', project)
    assert tags is not None

    exist_map = {obj.Get('Name'): obj for obj in tags.GetObjects('Tag')}
    # Create new
    tag_list = tag_utils.get_tag_object_list(['Tag1'])
    assert isinstance(tag_list, list)
    assert 1 == len(tag_list)
    assert tag_list[0].IsTypeOf('Tag')
    assert 'Tag1' == tag_list[0].Get('Name')
    assert 'Tag1' not in exist_map

    # New map
    exist_map = {obj.Get('Name'): obj for obj in tags.GetObjects('Tag')}
    # Retrieve existing, and a new one
    tag_list = tag_utils.get_tag_object_list(['Tag1', 'Tag2'])
    assert isinstance(tag_list, list)
    assert 2 == len(tag_list)
    assert tag_list[0].IsTypeOf('Tag')
    assert tag_list[1].IsTypeOf('Tag')
    assert tag_list[0].Get('Name') in exist_map
    assert tag_list[1].Get('Name') not in exist_map
    assert 'Tag2' == tag_list[1].Get('Name')


def test_add_tag_to_object(stc):
    ctor = CScriptableCreator()
    proj = CStcSystem.Instance().GetObject('project')
    port = ctor.Create('Port', proj)
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 1)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()
    dev = proj.GetObject('EmulatedDevice')
    assert dev
    tag_utils.add_tag_to_object(dev, 'Random')
    tag = dev.GetObject('Tag', RelationType('UserTag'))
    assert tag
    assert 'Random' == tag.Get('Name')


def test_tagged_endpoint_order_via_tag_names(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    create_port_with_ipv4_device(ctor, project)
    create_port_with_ipv4_device(ctor, project)

    tags = project.GetObject('Tags')
    tag1 = ctor.Create('Tag', tags)
    tag1.Set('Name', 'Sample')
    tag2 = ctor.Create('Tag', tags)
    tag2.Set('Name', 'Sample2')

    devices = project.GetObjects('EmulatedDevice')
    assert len(devices) == 2

    tag_names = []
    for device, tag in zip(devices, [tag2, tag1]):
        device.AddObject(tag, RelationType('UserTag'))
        tag_names.append(tag.Get("Name"))

    endpoints = tag_utils.get_tagged_endpoints_given_tag_names(tag_names)
    assert len(endpoints) == 2

    for device, endpoint in zip(devices, endpoints):
        ipv4 = device.GetObject('Ipv4If', RelationType('TopLevelIf'))
        assert endpoint.GetObjectHandle() == ipv4.GetObjectHandle()
