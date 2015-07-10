from StcIntPythonPL import *
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent',
                             'methodology'))
import spirent.methodology.utils.data_model_utils as dm_utils
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils

PKG = "spirent.methodology"


def test_is_property_enum(stc):
    project = CStcSystem.Instance().GetObject('Project')
    assert None is not project
    assert True == dm_utils.is_property_enum('Port', 'Layer3Type')
    assert False == dm_utils.is_property_enum('Port', 'PortGroupSize')
    assert False == dm_utils.is_property_enum('InvalidStcBllClass',
                                              'InvalidStcBllProperty')


def test_is_property_collection(stc):
    assert dm_utils.is_property_collection("Ipv4NetworkBlock", "StartIpList")
    assert not dm_utils.is_property_collection("EmulatedDevice", "Active")
    assert not dm_utils.is_property_collection("InvalidStcBllClass",
                                               "InvalidStcBllProperty")


def test_get_enum_str(stc):
    project = CStcSystem.Instance().GetObject('Project')
    assert None is not project
    assert 'IPV4' == dm_utils.get_enum_str('Port', 'Layer3Type', 1)
    assert 'IPV6' == dm_utils.get_enum_str('Port', 'Layer3Type', 2)
    assert 'IPV4V6' == dm_utils.get_enum_str('Port', 'Layer3Type', 3)


def test_get_enum_value(stc):
    project = CStcSystem.Instance().GetObject('Project')
    assert None is not project
    assert 1 == dm_utils.get_enum_val('Port', 'Layer3Type', 'IPV4')
    assert 2 == dm_utils.get_enum_val('Port', 'Layer3Type', 'IPV6')
    assert 3 == dm_utils.get_enum_val('Port', 'Layer3Type', 'IPV4V6')


def test_validate_classname(stc):
    assert (True, 'Project') == dm_utils.validate_classname('Project')
    assert (True, 'Project') == dm_utils.validate_classname('pROject')
    assert (False, 'alaala') == dm_utils.validate_classname('alaala')


def test_validate_property_tuple(stc):
    class_name = 'BfdRouterConfig'
    good_list = [('ScaleMode', 'NORMAL'),
                 ('DetectMultiplier', '3'),
                 ('BfdCcChannelType', '34')]
    res, ret_list = dm_utils.validate_property_tuple(class_name, good_list)
    assert res == ""
    lower_list = [('scalemode', 'NORMAL'),
                  ('detectmultiplier', '3'),
                  ('bfdccchanneltype', '34')]
    res, ret_list = dm_utils.validate_property_tuple(class_name, lower_list)
    assert res == ""
    assert lower_list != ret_list
    low_name_orig = [o[0].lower() for o in lower_list]
    low_name_res = [o[0].lower() for o in ret_list]
    assert low_name_orig == low_name_res

    # Test validating a list property
    class_name = "Ipv4NetworkBlock"
    non_list = [("StartIpList", "1.1.1.1")]
    res, ret_list = dm_utils.validate_property_tuple(class_name, non_list)
    assert res == ""
    real_list = [("StartIpList", ["1.1.1.1"])]
    res, ret_list = dm_utils.validate_property_tuple(class_name, real_list)
    assert res == ""


def test_validate_property_tuple_bad_enum(stc):
    class_name = 'BfdRouterConfig'
    bad_enum_list = [('ScaleMode', 'NOMRAL'),
                     ('DetectMultiplier', '3'),
                     ('BfdCcChannelType', '34')]
    res, ret_list = dm_utils.validate_property_tuple(class_name, bad_enum_list)
    assert res != ""
    assert "Invalid value" in res


def test_validate_property_tuple_bad_int(stc):
    class_name = 'BfdRouterConfig'
    not_int_list = [('ScaleMode', 'NORMAL'),
                    ('DetectMultiplier', '3'),
                    ('BfdCcChannelType', 'INVALID')]
    res, ret_list = dm_utils.validate_property_tuple(class_name, not_int_list)
    assert res != ""
    assert "Invalid uint16" in res


def test_validate_property_tuple_big_int(stc):
    class_name = 'BfdRouterConfig'
    big_int_list = [('ScaleMode', 'NORMAL'),
                    ('DetectMultiplier', '512'),
                    ('BfdCcChannelType', '34')]
    res, ret_list = dm_utils.validate_property_tuple(class_name, big_int_list)
    assert res != ""
    assert "should be between" in res


def test_validate_obj_prop_val():
    # Positive
    res = dm_utils.validate_obj_prop_val(
        "EmulatedDevice", "DeviceCount", "100")
    assert res == ""
    # Invalid Object
    res = dm_utils.validate_obj_prop_val(
        "InvalidObject", "DeviceCount", "100")
    assert "Object with name: InvalidObject does not exist" in res
    # Invalid Property
    res = dm_utils.validate_obj_prop_val(
        "EmulatedDevice", "InvalidProperty", "100")
    assert "Property: InvalidProperty does not exist" in res
    # Invalid Value
    res = dm_utils.validate_obj_prop_val(
        "EmulatedDevice", "DeviceCount", "InvalidValue")
    assert "Invalid value: InvalidValue specified" in res


def test_get_class_hierarchy(stc):
    class_name = 'EmulatedDevice'
    hier = dm_utils.get_class_hierarchy(class_name)
    assert ['EmulatedDevice', 'Node', 'Scriptable'] == hier
    class_name = 'XmuxtexXevice'
    hier = dm_utils.get_class_hierarchy(class_name)
    assert [] == hier


def test_get_valid_relations(stc):
    src = 'EmulatedDevice'
    dst = 'Tag'
    rel_list = dm_utils.get_valid_relations(src, dst)
    assert set(['DefaultTag', 'SystemTag', 'UserTag']) == set(rel_list)
    # No relation with Tags, should be empty
    dst = 'Tags'
    rel_list = dm_utils.get_valid_relations(src, dst)
    assert [] == rel_list
    # Should it throw? It won't for now
    rel_list = dm_utils.get_valid_relations('XXXX', 'YYYY')
    assert [] == rel_list


def test_validate_class_relation(stc):
    src = 'EmulatedDevice'
    dst = 'Tag'
    rel = 'UserTag'
    assert dm_utils.validate_class_relation(src, dst, rel)
    # Lowercase
    rel = 'usertag'
    assert not dm_utils.validate_class_relation(src, dst, rel)
    assert dm_utils.validate_class_relation(src, dst, rel, ignore_case=True)
    rel = 'ResultChild'
    assert not dm_utils.validate_class_relation(src, dst, rel)


def test_is_obj_list_all_same_type(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    dev1 = ctor.Create("EmulatedDevice", project)
    dev2 = ctor.Create("EmulatedDevice", project)
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)

    res = dm_utils.is_obj_list_all_same_type([dev1, dev2])
    assert res
    res = dm_utils.is_obj_list_all_same_type([dev1, dev2], "Port")
    assert not res
    res = dm_utils.is_obj_list_all_same_type([dev1, port1, port2])
    assert not res
    res = dm_utils.is_obj_list_all_same_type([port1, port2, dev2], "Port")
    assert not res


def test_get_ancestor(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    port = ctor.Create("Port", project)
    analyzer = port.GetObject("Analyzer")
    assert analyzer is not None
    analyzer_config = analyzer.GetObject("AnalyzerConfig")
    assert analyzer_config is not None
    port_ancestor = dm_utils.get_ancestor(analyzer_config, "Port")
    assert port_ancestor is not None
    assert port_ancestor.GetObjectHandle() == port.GetObjectHandle()
    dev_ancestor = dm_utils.get_ancestor(analyzer_config, "EmulatedDevice")
    assert dev_ancestor is None


def test_process_inputs_for_objects(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    dev1 = ctor.Create("EmulatedDevice", project)
    dev2 = ctor.Create("EmulatedDevice", project)
    dev3 = ctor.Create("EmulatedDevice", project)
    dev4 = ctor.Create("EmulatedDevice", project)

    port = ctor.Create("Port", project)

    tags = project.GetObject("Tags")
    assert tags
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Tag 1")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Tag 2")
    tag1.AddObject(tags, RelationType("UserTag"))
    tag2.AddObject(tags, RelationType("UserTag"))

    dev1.AddObject(tag1, RelationType("UserTag"))
    dev2.AddObject(tag2, RelationType("UserTag"))
    port.AddObject(tag2, RelationType("UserTag"))

    # Test normal ProcessInputHandleVec
    obj_list = dm_utils.process_inputs_for_objects([dev1.GetObjectHandle(),
                                                    dev3.GetObjectHandle()],
                                                   [], "EmulatedDevice")
    assert len(obj_list) == 2
    found_dev1 = False
    found_dev3 = False
    for obj in obj_list:
        if obj.GetObjectHandle() == dev1.GetObjectHandle():
            found_dev1 = True
        elif obj.GetObjectHandle() == dev3.GetObjectHandle():
            found_dev3 = True
    assert found_dev1
    assert found_dev3

    # This one is a bit ugly due to the default host
    # (might be wrong)
    host = port.GetObject("Host")
    assert host
    obj_list = dm_utils.process_inputs_for_objects([project.GetObjectHandle()],
                                                   [], "EmulatedDevice")
    assert len(obj_list) == 5
    found_dev1 = True
    found_dev2 = True
    found_dev3 = True
    found_dev4 = True
    found_default_host = True
    for obj in obj_list:
        if obj.GetObjectHandle() == dev1.GetObjectHandle():
            found_dev1 = True
        elif obj.GetObjectHandle() == dev3.GetObjectHandle():
            found_dev3 = True
        elif obj.GetObjectHandle() == dev2.GetObjectHandle():
            found_dev2 = True
        elif obj.GetObjectHandle() == dev4.GetObjectHandle():
            found_dev4 = True
        elif obj.GetObjectHandle() == host.GetObjectHandle():
            found_default_host = True
    assert found_dev1
    assert found_dev2
    assert found_dev3
    assert found_dev4
    assert found_default_host

    obj_list = dm_utils.process_inputs_for_objects([dev3.GetObjectHandle()],
                                                   ["Tag 1", "Tag 2"],
                                                   "EmulatedDevice")
    assert len(obj_list) == 3
    found_dev1 = False
    found_dev2 = False
    found_dev3 = False
    for obj in obj_list:
        if obj.GetObjectHandle() == dev1.GetObjectHandle():
            found_dev1 = True
        elif obj.GetObjectHandle() == dev3.GetObjectHandle():
            found_dev3 = True
        elif obj.GetObjectHandle() == dev2.GetObjectHandle():
            found_dev2 = True
    assert found_dev1
    assert found_dev2
    assert found_dev3

    obj_list = dm_utils.process_inputs_for_objects([dev3.GetObjectHandle()],
                                                   ["Tag 1", "Tag 2"],
                                                   "Port")
    assert len(obj_list) == 1
    assert obj_list[0].GetObjectHandle() == port.GetObjectHandle()

    # Test duplicate removal
    obj_list = dm_utils.process_inputs_for_objects([dev1.GetObjectHandle()],
                                                   ["Tag 1"], "EmulatedDevice")
    assert len(obj_list) == 1
    assert obj_list[0].GetObjectHandle() == dev1.GetObjectHandle()


def test_add_property_chain(stc):
    plLogger = PLLogger.GetLogger("test_add_property_chain")
    plLogger.LogInfo("start")

    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()

    source_cmd = ctor.Create(PKG + ".IteratorCommand", sequencer)
    target_cmd = ctor.Create(PKG + ".IteratorConfigCommand", sequencer)

    dm_utils.add_property_chain(PKG + ".IteratorCommand.CurrVal", source_cmd,
                                PKG + ".IteratorConfigCommand.CurrVal",
                                target_cmd)
    # Check the property chain
    prop_chain_list = source_cmd.GetObjects("PropertyChainingConfig")
    assert len(prop_chain_list) == 1
    prop_chain = prop_chain_list[0]
    assert prop_chain.Get("SourcePropertyId") == \
        PKG + ".iteratorcommand.currval"
    assert prop_chain.Get("TargetPropertyId") == \
        PKG + ".iteratorconfigcommand.currval"
    pc_target_list = prop_chain.GetObjects("Scriptable",
                                           RelationType("PropertyChain"))
    assert len(pc_target_list) == 1
    pc_target = pc_target_list[0]
    assert pc_target.GetObjectHandle() == target_cmd.GetObjectHandle()

    # Add a duplicate property chain
    dm_utils.add_property_chain(PKG + ".IteratorCommand.CurrVal", source_cmd,
                                PKG + ".IteratorConfigCommand.CurrVal",
                                target_cmd)
    # Verify nothing happened (nothing new created)
    prop_chain_list2 = source_cmd.GetObjects("PropertyChainingConfig")
    assert len(prop_chain_list2) == 1
    prop_chain2 = prop_chain_list2[0]
    assert prop_chain.GetObjectHandle() == prop_chain2.GetObjectHandle()
    assert prop_chain2.Get("SourcePropertyId") == \
        PKG + ".iteratorcommand.currval"
    assert prop_chain2.Get("TargetPropertyId") == \
        PKG + ".iteratorconfigcommand.currval"
    pc_target_list2 = prop_chain2.GetObjects("Scriptable",
                                             RelationType("PropertyChain"))
    assert len(pc_target_list2) == 1
    pc_target2 = pc_target_list2[0]
    assert pc_target2.GetObjectHandle() == target_cmd.GetObjectHandle()


def test_add_tag_to_objects(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('Project')
    port = ctor.Create('Port', project)
    tags = project.GetObject('Tags')
    tag_list = tags.GetObjects('Tag')
    # The default list (by observation):
    # Host, Router, Client, Server, Core, Edge
    tag_dict = {}
    for tag in tag_list:
        tag_dict[tag.Get('Name')] = tag.GetObjectHandle()

    hnd_list = []
    with AutoCommand('DeviceCreate') as cmd:
        cmd.Set('Port', port.GetObjectHandle())
        cmd.Set('DeviceCount', 1)
        cmd.Set('CreateCount', 4)
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1, 1])
        cmd.Execute()
        hnd_list = cmd.GetCollection('ReturnList')
    hnd_reg = CHandleRegistry.Instance()
    obj_list = []
    for hnd in hnd_list:
        obj = hnd_reg.Find(hnd)
        obj_list.append(obj)
    host = tag_dict['Host']
    edge = tag_dict['Edge']
    # Valid relations (as of 8/26) are UserTag, DefaultTag, SystemTag
    dm_utils.add_tag_to_objects(obj_list, [host, edge], 'UserTag')
    host_tag = hnd_reg.Find(host)
    edge_tag = hnd_reg.Find(edge)

    obj_set = set()
    host_set = set()
    edge_set = set()
    for obj in obj_list:
        obj_set.add(obj.GetObjectHandle())
    host_list = host_tag.GetObjects('Scriptable', RelationType('UserTag', 1))
    for obj in host_list:
        host_set.add(obj.GetObjectHandle())
    # Compare the sets, since we can't rely on the list comparison to pass
    assert host_set == obj_set
    edge_list = edge_tag.GetObjects('Scriptable', RelationType('UserTag', 1))
    for obj in edge_list:
        edge_set.add(obj.GetObjectHandle())
    assert edge_set == obj_set


def test_is_valid_parent(stc):
    # Project as a parent of EmulatedDevice
    res = dm_utils.is_valid_parent("Project", "EmulatedDevice")
    assert res
    # EmulatedDevice as a parent of Project
    res = dm_utils.is_valid_parent("EmulatedDevice", "Project")
    assert not res
    # EmulatedDevice as a parent of BgpRouterConfig
    res = dm_utils.is_valid_parent("EmulatedDevice", "BgpRouterConfig")
    assert res
    # EmulatedDevice as a parent of Ipv4NetworkBlock
    res = dm_utils.is_valid_parent("EmulatedDevice", "Ipv4NetworkBlock")
    assert res
    # Project as a parent of Port
    res = dm_utils.is_valid_parent("Project", "Port")
    assert res
    # Port as a parent of StreamBlock
    res = dm_utils.is_valid_parent("Port", "StreamBlock")
    assert res
    # Project as a parent of StreamBlock
    res = dm_utils.is_valid_parent("Project", "StreamBlock")
    assert res
    # IgmpHostConfig as a parent of IgmpGroupMembership
    res = dm_utils.is_valid_parent("IgmpHostConfig", "IgmpGroupMembership")
    assert res

    res = dm_utils.is_valid_parent("BgpRouterConfig", "EmulatedDevice")
    assert not res


def test_stcsave_list_to_string():
    src = [1, 2, 3, 4, 5]
    res = dm_utils.stcsave_list_to_string(src)
    assert '1 2 3 4 5' == res
    src = ['something', '', 'a space', 'thanks']
    res = dm_utils.stcsave_list_to_string(src)
    assert 'something {} {a space} thanks' == res
    # This is the non-recoverable case where a collection has braces
    src = ['{"key" : "value"}', 'json}', 'yucky']
    res = dm_utils.stcsave_list_to_string(src)
    assert '{{"key" : "value"}} json} yucky' == res


def test_stcsave_string_to_list():
    src = '1 2 3 4 5'
    res = dm_utils.stcsave_string_to_list(src)
    assert ['1', '2', '3', '4', '5'] == res
    src = 'something {} {a space} thanks'
    res = dm_utils.stcsave_string_to_list(src)
    assert ['something', '', 'a space', 'thanks'] == res
    # Note that what's restored is _not_ the same is what was stored
    src = '{{"key" : "value"}} json} yucky'
    res = dm_utils.stcsave_string_to_list(src)
    assert ['{"key" : "value"', '}', 'json}', 'yucky'] == res


def test_get_class_objects(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    rx_port = ctor.Create("Port", project)
    stream_block = ctor.Create("StreamBlock", port)
    stream_block.AddObject(rx_port, RelationType("ExpectedRx"))
    tag_utils.add_tag_to_object(stream_block, "ttStreamBlock")
    proto_mix = ctor.Create("StmProtocolMix", project)
    template_config = ctor.Create("StmTemplateConfig", proto_mix)
    template_config.AddObject(port, RelationType("GeneratedObject"))
    tag_utils.add_tag_to_object(template_config, "ttTemplateConfig")
    em_device = ctor.Create("EmulatedDevice", project)
    bgp_router_config = ctor.Create("BgpRouterConfig", em_device)

    # No target object for class type
    target_objs = dm_utils.get_class_objects([], [], ['StreamBlock'])
    assert len(target_objs) == 0

    # Handle passed in is of class type
    target_objs = dm_utils.get_class_objects([stream_block.GetObjectHandle()], [], ['StreamBlock'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('StreamBlock')

    # Handle passed in has child of class type
    target_objs = dm_utils.get_class_objects([proto_mix.GetObjectHandle()], [], ['StreamBlock'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('StreamBlock')

    # ProtocolMix
    target_objs = dm_utils.get_class_objects([proto_mix.GetObjectHandle()], [], ['StreamBlock'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('StreamBlock')

    # TemplateConfig
    target_objs = dm_utils.get_class_objects([], ['ttTemplateConfig'], ['StreamBlock'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('StreamBlock')

    # Verify that only one streamblock is returned and there aren't duplicates
    target_objs = dm_utils.get_class_objects([proto_mix.GetObjectHandle()],
                                             ['ttTemplateConfig'], ['StreamBlock'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('StreamBlock')

    # Multiple class types
    target_objs = dm_utils.get_class_objects([], ['ttTemplateConfig'], ['StreamBlock', 'Port'])
    assert len(target_objs) == 2
    for obj in target_objs:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))

    # Handle passed in is of class type
    target_objs = dm_utils.get_class_objects([bgp_router_config.GetObjectHandle()], [],
                                             ['RouterConfig'])
    assert len(target_objs) == 1
    assert target_objs[0].IsTypeOf('BgpRouterConfig')


def test_get_obj_list_from_handles_and_tags(stc):
    obj_list = []
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    tag_utils.add_tag_to_object(port, "ttPort")
    rx_port = ctor.Create("Port", project)
    stream_block = ctor.Create("StreamBlock", port)
    stream_block.AddObject(rx_port, RelationType("ExpectedRx"))
    tag_utils.add_tag_to_object(stream_block, "ttStreamBlock")

    # Empty lists
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([], [])
    assert obj_list == []

    # Only handles
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([port.GetObjectHandle(),
                                                            stream_block.GetObjectHandle()], [])
    assert len(obj_list) == 2
    for obj in obj_list:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))

    # Only tags
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([], ["ttPort", "ttStreamBlock"])
    assert len(obj_list) == 2
    for obj in obj_list:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))

    # Handle and tag mix duplicate
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([port.GetObjectHandle(),
                                                            stream_block.GetObjectHandle()],
                                                           ["ttPort", "ttStreamBlock"])
    assert len(obj_list) == 2
    for obj in obj_list:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))

    # Handle and tag mix different
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([rx_port.GetObjectHandle()],
                                                           ["ttPort", "ttStreamBlock"])
    assert len(obj_list) == 3
    for obj in obj_list:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))

    # Handle and tag that doesn't exist
    obj_list = dm_utils.get_obj_list_from_handles_and_tags([port.GetObjectHandle(),
                                                            stream_block.GetObjectHandle()],
                                                           ["ttBlah"])
    assert len(obj_list) == 2
    for obj in obj_list:
        assert (obj.IsTypeOf('StreamBlock') or obj.IsTypeOf('Port'))


# TODO: remove from ExpandRouteMixCommand
def test_remove_dup_scriptable(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('Project')
    dev1 = ctor.Create("EmulatedDevice", project)
    dev2 = ctor.Create("EmulatedDevice", project)
    tags = project.GetObject("Tags")
    assert tags

    # Order is maintained
    res_val = dm_utils.remove_dup_scriptable([dev1, dev2,
                                              dev1, project])
    assert len(res_val) == 3
    assert res_val[0].GetObjectHandle() == dev1.GetObjectHandle()
    assert res_val[1].GetObjectHandle() == dev2.GetObjectHandle()
    assert res_val[2].GetObjectHandle() == project.GetObjectHandle()


def test_sort_obj_list_by_handle(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('Project')
    dev1 = ctor.Create("EmulatedDevice", project)
    dev2 = ctor.Create("EmulatedDevice", project)
    res_val = dm_utils.sort_obj_list_by_handle([dev1, dev2,
                                                dev1, project])
    assert len(res_val) == 3
    assert res_val[0].GetObjectHandle() == project.GetObjectHandle()
    assert res_val[1].GetObjectHandle() == dev1.GetObjectHandle()
    assert res_val[2].GetObjectHandle() == dev2.GetObjectHandle()

    res_val = dm_utils.sort_obj_list_by_handle([project, dev2,
                                                dev1])
    assert len(res_val) == 3
    assert res_val[0].GetObjectHandle() == project.GetObjectHandle()
    assert res_val[1].GetObjectHandle() == dev1.GetObjectHandle()
    assert res_val[2].GetObjectHandle() == dev2.GetObjectHandle()

    res_val = dm_utils.sort_obj_list_by_handle([project, dev1,
                                                dev2])
    assert len(res_val) == 3
    assert res_val[0].GetObjectHandle() == project.GetObjectHandle()
    assert res_val[1].GetObjectHandle() == dev1.GetObjectHandle()
    assert res_val[2].GetObjectHandle() == dev2.GetObjectHandle()
