from StcIntPythonPL import *
import xml.etree.ElementTree as etree
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.ExpandTemplateCommand as ExpTmplCmd


PKG = "spirent.methodology"


def test_check_load_src_to_target(stc):
    # Load BgpRouterConfig on an EmulatedDevice
    bgp = etree.fromstring("<BgpRouterConfig />")
    dev = etree.fromstring("<EmulatedDevice />")
    res = ExpTmplCmd.check_load_src_to_target([bgp],
                                              "EmulatedDevice")
    assert res == ""

    # Load an Ipv4NetworkBlock and a Tag on an Ipv4Group
    net_block = etree.fromstring("<Ipv4NetworkBlock />")
    tag = etree.fromstring("<Tag name=\"Tag1\" id=\"123\" />")
    res = ExpTmplCmd.check_load_src_to_target([net_block, tag],
                                              "Ipv4Group")
    assert res == ""

    # Load an Ipv4NetworkBlock, a Tag, and a BgpRouterConfig
    # on an EmulatedDevice
    res = ExpTmplCmd.check_load_src_to_target([net_block, tag, bgp],
                                              "EmulatedDevice")
    assert res == ""

    # Load an EmulatedDevice on a BgpRouterConfig
    res = ExpTmplCmd.check_load_src_to_target([dev],
                                              "BgpRouterConfig")
    assert res == "BgpRouterConfig is not a valid parent " + \
        "for EmulatedDevice."


def test_expand_devs_target_port_only(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")
    port3 = ctor.Create("Port", project)
    port3.Set("Location", "//10.14.16.27/2/3")
    port4 = ctor.Create("Port", project)
    port4.Set("Location", "//10.14.16.27/2/4")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    port2.AddObject(port_group_tag, RelationType("UserTag"))
    port3.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList", [container.GetObjectHandle()])
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Execute()
    assert cmd.Get("Status") == ""
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check the generated objects
    # Tags should not be in the list
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 3
    for obj in gen_obj_list:
        assert obj.IsTypeOf("Tags") is False
        assert obj.IsTypeOf("EmulatedDevice")

    # port4 should have nothing
    dev_list = port4.GetObjects("EmulatedDevice",
                                RelationType("AffiliationPort", 1))
    assert len(dev_list) == 0

    # Check tags
    tag_list = tags.GetObjects("Tag")
    assert len(tag_list) == 13
    exp_tag_names = ["Host", "Router", "Edge", "Core", "Client",
                     "Server", "EastPortGroup", "OuterVlan",
                     "InnerVlan", "Dhcpv4", "TopLevelIf",
                     "DHCP Client", "Ipv4If.Address"]
    for tag in tag_list:
        assert tag.Get("Name") in exp_tag_names

    # port1, port2, and port3 should now each have one copy of the XML
    exp_ip_addr_list = ["55.55.55.55", "55.55.55.56", "55.55.55.57"]
    i = 0
    for port in [port1, port2, port3]:
        dev_list = port.GetObjects("EmulatedDevice",
                                   RelationType("AffiliationPort", 1))
        assert len(dev_list) == 1
        dev = dev_list[0]
        ipv4if_list = dev.GetObjects("Ipv4If")
        assert len(ipv4if_list) == 1
        ipv4if = ipv4if_list[0]
        assert ipv4if is not None
        assert ipv4if.Get("Address") == exp_ip_addr_list[i]

        vlanif_list = dev.GetObjects("VlanIf")
        assert len(vlanif_list) == 2
        outer_vlan = vlanif_list[0]
        inner_vlan = vlanif_list[1]
        assert outer_vlan is not None
        assert inner_vlan is not None
        if outer_vlan.Get("VlanId") == 1000:
            outer_vlan = vlanif_list[1]
            inner_vlan = vlanif_list[0]
        assert outer_vlan.Get("VlanId") == 1500
        assert inner_vlan.Get("VlanId") == 2000
        ethif_list = dev.GetObjects("EthIIIf")
        assert len(ethif_list) == 1
        ethif = ethif_list[0]
        assert ethif is not None

        # Check relations
        stacked_on_ipv4 = ipv4if.GetObject("NetworkInterface",
                                           RelationType("StackedOnEndpoint"))
        assert stacked_on_ipv4.GetObjectHandle() == \
            inner_vlan.GetObjectHandle()
        stacked_on_inner = inner_vlan.GetObject(
            "NetworkInterface", RelationType("StackedOnEndpoint"))
        assert stacked_on_inner.GetObjectHandle() == \
            outer_vlan.GetObjectHandle()
        stacked_on_outer = outer_vlan.GetObject(
            "NetworkInterface", RelationType("StackedOnEndpoint"))
        assert stacked_on_outer.GetObjectHandle() == \
            ethif.GetObjectHandle()

        primary_if = dev.GetObject("NetworkInterface",
                                   RelationType("PrimaryIf"))
        assert primary_if.GetObjectHandle() == \
            ipv4if.GetObjectHandle()
        top_level_if = dev.GetObject("NetworkInterface",
                                     RelationType("TopLevelIf"))
        assert top_level_if.GetObjectHandle() == \
            ipv4if.GetObjectHandle()

        # Check DHCPv4
        dhcp_proto = dev.GetObject("Dhcpv4BlockConfig")
        assert dhcp_proto is not None

        outer_vlan_tag = None
        inner_vlan_tag = None
        dhcp_tag = None
        client_tag = None
        for tag in tag_list:
            if tag.Get("Name") == "DHCP Client":
                client_tag = tag.GetObjectHandle()
            elif tag.Get("Name") == "Dhcpv4":
                dhcp_tag = tag.GetObjectHandle()
            elif tag.Get("Name") == "OuterVlan":
                outer_vlan_tag = tag.GetObjectHandle()
            elif tag.Get("Name") == "InnerVlan":
                inner_vlan_tag = tag.GetObjectHandle()
        user_client_tag = dev.GetObject("Tag", RelationType("UserTag"))
        assert user_client_tag is not None
        assert user_client_tag.GetObjectHandle() == client_tag
        user_outer_vlan_tag = outer_vlan.GetObject("Tag",
                                                   RelationType("UserTag"))
        assert user_outer_vlan_tag is not None
        assert user_outer_vlan_tag.GetObjectHandle() == outer_vlan_tag
        user_inner_vlan_tag = inner_vlan.GetObject("Tag",
                                                   RelationType("UserTag"))
        assert user_inner_vlan_tag is not None
        assert user_inner_vlan_tag.GetObjectHandle() == inner_vlan_tag
        user_dhcp_tag = dhcp_proto.GetObject("Tag", RelationType("UserTag"))
        assert user_dhcp_tag is not None
        assert user_dhcp_tag.GetObjectHandle() == dhcp_tag

        contain_obj = dev.GetObject("StmTemplateConfig",
                                    RelationType("GeneratedObject", 1))
        assert contain_obj.GetObjectHandle() == container.GetObjectHandle()

        # Check the removal of the StmPropertyModifier object(s)
        # The only StmPropertyModifier that exists currently lives
        # on the Ipv4If
        modifier = ipv4if.GetObject("StmPropertyModifier")
        assert modifier is None

        # Tag should still exist (for now)

        i = i + 1


def test_expand_devs_target_port_only_copy_count(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    port2.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.SetCollection("TargetTagList", ["EastPortGroup"])
    cmd.Set("CopiesPerParent", 3)
    cmd.Execute()

    # Check the generated objects
    # Tags should not be in the list
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 6
    for obj in gen_obj_list:
        assert obj.IsTypeOf("Tags") is False
        assert obj.IsTypeOf("EmulatedDevice")

    # Check tags (duplicates should have been removed)
    tag_list = tags.GetObjects("Tag")
    assert len(tag_list) == 13
    exp_tag_names = ["Host", "Router", "Edge", "Core", "Client",
                     "Server", "EastPortGroup", "OuterVlan",
                     "InnerVlan", "Dhcpv4", "TopLevelIf",
                     "DHCP Client", "Ipv4If.Address"]
    for tag in tag_list:
        assert tag.Get("Name") in exp_tag_names

    # port1 and port2 should now each have 3 copies of the EmulatedDevice
    i = 0
    exp_addr_list = ["55.55.55.55", "55.55.55.56", "55.55.55.57",
                     "55.55.55.58", "55.55.55.59", "55.55.55.60",
                     "55.55.55.61", "55.55.55.62", "55.55.55.63"]
    for port in [port1, port2]:
        dev_list = port.GetObjects("EmulatedDevice",
                                   RelationType("AffiliationPort", 1))
        assert len(dev_list) == 3
        for dev in dev_list:
            ipv4if_list = dev.GetObjects("Ipv4If")
            assert len(ipv4if_list) == 1
            ipv4if = ipv4if_list[0]
            assert ipv4if is not None
            assert ipv4if.Get("Address") == exp_addr_list[i]

            vlanif_list = dev.GetObjects("VlanIf")
            assert len(vlanif_list) == 2
            outer_vlan = vlanif_list[0]
            inner_vlan = vlanif_list[1]
            assert outer_vlan is not None
            assert inner_vlan is not None
            if outer_vlan.Get("VlanId") == 1000:
                outer_vlan = vlanif_list[1]
                inner_vlan = vlanif_list[0]
            assert outer_vlan.Get("VlanId") == 1500
            assert inner_vlan.Get("VlanId") == 2000
            ethif_list = dev.GetObjects("EthIIIf")
            assert len(ethif_list) == 1
            ethif = ethif_list[0]
            assert ethif is not None

            # Check relations
            stacked_on_ipv4 = ipv4if.GetObject(
                "NetworkInterface", RelationType("StackedOnEndpoint"))
            assert stacked_on_ipv4.GetObjectHandle() == \
                inner_vlan.GetObjectHandle()
            stacked_on_inner = inner_vlan.GetObject(
                "NetworkInterface", RelationType("StackedOnEndpoint"))
            assert stacked_on_inner.GetObjectHandle() == \
                outer_vlan.GetObjectHandle()
            stacked_on_outer = outer_vlan.GetObject(
                "NetworkInterface", RelationType("StackedOnEndpoint"))
            assert stacked_on_outer.GetObjectHandle() == \
                ethif.GetObjectHandle()

            primary_if = dev.GetObject("NetworkInterface",
                                       RelationType("PrimaryIf"))
            assert primary_if.GetObjectHandle() == \
                ipv4if.GetObjectHandle()
            top_level_if = dev.GetObject("NetworkInterface",
                                         RelationType("TopLevelIf"))
            assert top_level_if.GetObjectHandle() == \
                ipv4if.GetObjectHandle()

            # Check DHCPv4
            dhcp_proto = dev.GetObject("Dhcpv4BlockConfig")
            assert dhcp_proto is not None

            # Check tags
            tags = project.GetObject("Tags")
            assert tags is not None

            tag_list = tags.GetObjects("Tag")
            # FIXME:
            # This will not work because of the duplication of tags
            # assert len(tag_list) == 9

            # These will be lists until we remove duplicate tags properly
            outer_vlan_tag = []
            inner_vlan_tag = []
            dhcp_tag = []
            client_tag = []
            for tag in tag_list:
                if tag.Get("Name") == "DHCP Client":
                    client_tag.append(tag.GetObjectHandle())
                elif tag.Get("Name") == "Dhcpv4":
                    dhcp_tag.append(tag.GetObjectHandle())
                elif tag.Get("Name") == "OuterVlan":
                    outer_vlan_tag.append(tag.GetObjectHandle())
                elif tag.Get("Name") == "InnerVlan":
                    inner_vlan_tag.append(tag.GetObjectHandle())
            user_client_tag = dev.GetObject("Tag", RelationType("UserTag"))
            assert user_client_tag is not None
            assert user_client_tag.GetObjectHandle() in client_tag
            user_outer_vlan_tag = outer_vlan.GetObject("Tag",
                                                       RelationType("UserTag"))
            assert user_outer_vlan_tag is not None
            assert user_outer_vlan_tag.GetObjectHandle() in outer_vlan_tag
            user_inner_vlan_tag = inner_vlan.GetObject("Tag",
                                                       RelationType("UserTag"))
            assert user_inner_vlan_tag is not None
            assert user_inner_vlan_tag.GetObjectHandle() in inner_vlan_tag
            user_dhcp_tag = dhcp_proto.GetObject("Tag",
                                                 RelationType("UserTag"))
            assert user_dhcp_tag is not None
            assert user_dhcp_tag.GetObjectHandle() in dhcp_tag

            contain_obj = dev.GetObject("StmTemplateConfig",
                                        RelationType("GeneratedObject", 1))
            assert contain_obj.GetObjectHandle() == container.GetObjectHandle()

            # Check the removal of the StmPropertyModifier object(s)
            # The only StmPropertyModifier that exists currently lives
            # on the Ipv4If
            modifier = ipv4if.GetObject("StmPropertyModifier")
            assert modifier is None

            # Tag should still exist (for now)

            i = i + 1


def test_expand_multicast_groups_large_copy_count(stc):
    test_xml = get_multicast_group_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.Set("CopiesPerParent", 300)
    cmd.Execute()

    # Check the generated objects
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 300
    for gen_obj in gen_obj_list:
        assert gen_obj.IsTypeOf("Ipv4Group")


def test_expand_project_level_streamblock(stc):
    test_xml = get_project_sb_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    et_cu1 = ctor.Create("EthernetCopper", port1)
    port1.AddObject(et_cu1, RelationType("ActivePhy"))
    et_cu2 = ctor.Create("EthernetCopper", port2)
    port2.AddObject(et_cu2, RelationType("ActivePhy"))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.Set("CopiesPerParent", 1)
    cmd.Execute()

    # Check objects
    # Project-level streamblock (does not call StreamBlockExpandCommand)
    sb_list = port1.GetObjects("StreamBlock")
    assert not len(sb_list)
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)
    sb_list = project.GetObjects("StreamBlock")
    assert len(sb_list) == 1

    sb = sb_list[0]
    assert sb
    sb_tag = sb.GetObject("Tag", RelationType("UserTag"))
    assert sb_tag

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    found_sb_tag = False
    for tag in tag_list:
        if tag.Get("Name") == "ttStreamBlock":
            found_sb_tag = tag
    assert found_sb_tag
    assert sb_tag.GetObjectHandle() == found_sb_tag.GetObjectHandle()

    # Check generated objects
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    cmd.MarkDelete()
    assert len(gen_obj_list) == 1
    found_sb = False
    for obj in gen_obj_list:
        assert obj is not None
        if obj.IsTypeOf("StreamBlock"):
            found_sb = True
    assert found_sb


def test_expand_raw_streamblock(stc):
    test_xml = get_raw_sb_template()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    port_group_tag = ctor.Create("Tag", tags)
    port_group_tag.Set("Name", "EastPortGroup")
    port1.AddObject(port_group_tag, RelationType("UserTag"))
    tags.AddObject(port_group_tag, RelationType("UserTag"))

    et_cu1 = ctor.Create("EthernetCopper", port1)
    port1.AddObject(et_cu1, RelationType("ActivePhy"))
    et_cu2 = ctor.Create("EthernetCopper", port2)
    port2.AddObject(et_cu2, RelationType("ActivePhy"))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.Set("CopiesPerParent", 1)
    cmd.SetCollection("TargetTagList", [port_group_tag.Get("Name")])
    cmd.Execute()

    # Check objects
    # Port-level streamblock
    sb_list = project.GetObjects("StreamBlock")
    assert not len(sb_list)
    sb_list = port2.GetObjects("StreamBlock")
    assert not len(sb_list)
    sb_list = port1.GetObjects("StreamBlock")
    assert len(sb_list) == 1
    sb = sb_list[0]
    assert sb
    sb_tag = sb.GetObject("Tag", RelationType("UserTag"))
    assert sb_tag

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    found_sb_tag = False
    for tag in tag_list:
        if tag.Get("Name") == "ttStreamBlock":
            found_sb_tag = tag
    assert found_sb_tag
    assert sb_tag.GetObjectHandle() == found_sb_tag.GetObjectHandle()

    # Check generated objects
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    cmd.MarkDelete()
    assert len(gen_obj_list) == 1
    found_sb = False
    for obj in gen_obj_list:
        assert obj is not None
        if obj.IsTypeOf("StreamBlock"):
            found_sb = True
    assert found_sb


def test_expand_source_and_target(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    # Create an EmulatedDevice
    dev1 = ctor.Create("EmulatedDevice", project)
    dev1.AddObject(port1, RelationType("AffiliationPort"))
    dev2 = ctor.Create("EmulatedDevice", project)
    dev2.AddObject(port2, RelationType("AffiliationPort"))

    target_tag = ctor.Create("Tag", tags)
    target_tag.Set("Name", "Dev2")
    dev2.AddObject(target_tag, RelationType("UserTag"))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.SetCollection("TargetTagList", ["Dev2"])
    cmd.SetCollection("SrcTagList", ["Dhcpv4"])
    cmd.Execute()
    cmd.MarkDelete()

    # Check the tags
    tag_list = tags.GetObjects("Tag")
    dhcp_tag = None
    for tag in tag_list:
        if tag.Get("Name") == "Dhcpv4":
            dhcp_tag = tag
            break
    assert dhcp_tag is not None
    assert dhcp_tag.Get("Name") == "Dhcpv4"

    # Check dev1
    dhcp_proto = dev1.GetObject("Dhcpv4BlockConfig")
    assert dhcp_proto is None

    # Check dev2
    dhcp_proto = dev2.GetObject("Dhcpv4BlockConfig")
    assert dhcp_proto is not None
    dhcp_tag = dhcp_proto.GetObject("Tag", RelationType("UserTag"))
    assert dhcp_tag.GetObjectHandle() == dhcp_tag.GetObjectHandle()


def test_expand_no_src_tag_list_or_serialization_base(stc):
    test_xml = get_test_xml()

    # Strip serializationBase params
    root = etree.fromstring(test_xml)
    assert root is not None
    serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
    for ele in serial_ele_list:
        if "serializationBase" in ele.attrib.keys():
            ele.attrib.pop("serializationBase")

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    # Create the StmTemplateConfig
    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", etree.tostring(root))

    # Call expand.  SrcTagList is empty, TargetTagList
    # is also empty (TargetTagList defaults to project)
    # This is currently handled as a warning, not an error.
    cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
    cmd.SetCollection("StmTemplateConfigList",
                      [container.GetObjectHandle()])
    cmd.Execute()
    assert cmd.Get("Status") == ""
    assert cmd.Get("PassFailState") == "PASSED"
    gen_obj_list = container.GetObjects("Scriptable",
                                        RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 0


def test_empty_tag_list(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    # This should pass; empty tag list indicates project
    # will be used as the target.
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', [])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "PASSED"


def test_tagging_nothing(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    ctor = CScriptableCreator()
    plLogger = PLLogger.GetLogger("test_tagging_nothing")
    plLogger.LogInfo("start")

    project = stc_sys.GetObject("Project")
    tags = project.GetObject('Tags')
    assert tags is not None
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'EastPortGroup')
    tags.AddObject(tag, RelationType('UserTag'))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['EastPortGroup'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "FAILED"


def test_tagging_mixed_invalid_parent(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    ctor = CScriptableCreator()
    project = stc_sys.GetObject("Project")
    tags = project.GetObject('Tags')
    assert tags is not None
    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'EastPortGroup')
    tags.AddObject(tag, RelationType('UserTag'))

    port = ctor.Create('Port', project)
    dev = ctor.Create('EmulatedDevice', project)
    dev.AddObject(port, RelationType('AffiliationPort'))

    port.AddObject(tag, RelationType('UserTag'))
    dev.AddObject(tag, RelationType('UserTag'))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['EastPortGroup'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "FAILED"
        assert "emulateddevice is not a valid " + \
            "parent for EmulatedDevice." in cmd.Get("Status")


def test_tagging_invalid(stc):
    test_xml = get_test_xml()

    stc_sys = CStcSystem.Instance()
    ctor = CScriptableCreator()
    project = stc_sys.GetObject("Project")
    port1 = ctor.Create("Port", project)

    tags = project.GetObject('Tags')
    assert tags is not None
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    tag = ctor.Create('Tag', tags)
    tag.Set('Name', 'EastPortGroup')
    port1.AddObject(tag, RelationType("UserTag"))
    tags.AddObject(tag, RelationType('UserTag'))

    container = ctor.Create("StmTemplateConfig", project)
    container.Set("TemplateXml", test_xml)

    # Test a working case
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['EastPortGroup'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "PASSED"

    # Test an unknown tag
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['unknown'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "FAILED"

    # Test a valid tag with an empty tag
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['EastPortGroup', ''])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "FAILED"

    # Test a valid tag with an undefined tag
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['invalid', 'EastPortGroup'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "FAILED"

    # FIXME:
    # This should probably fail?
    # Test a valid tag with a duplicate tag
    with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
        cmd.SetCollection('StmTemplateConfigList',
                          [container.GetObjectHandle()])
        cmd.SetCollection('TargetTagList', ['EastPortGroup', 'EastPortGroup'])
        cmd.Execute()
        assert cmd.Get("PassFailState") == "PASSED"


def test_update_template_using_src_tag_list(stc):
    test_xml = get_test_xml()
    root = etree.fromstring(test_xml)
    serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
    assert len(serial_ele_list) == 2

    # Empty SrcTagList
    res = ExpTmplCmd.update_template_using_src_tag_list(root, [])
    assert len(res) == 2
    tags_ele = None
    dev_ele = None
    for obj_ele in res:
        if obj_ele.tag == "EmulatedDevice":
            dev_ele = obj_ele
        elif obj_ele.tag == "Tags":
            tags_ele = obj_ele
    assert tags_ele is not None
    assert dev_ele is not None
    serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
    assert len(serial_ele_list) == 2
    assert tags_ele in serial_ele_list
    assert dev_ele in serial_ele_list

    # SrcTagList with invalid tag name(s)
    src_tag_list = ["InvalidTagName1", "InvalidTagName2"]
    res = ExpTmplCmd.update_template_using_src_tag_list(root, src_tag_list)
    assert len(res) == 0

    # SrcTagList with valid tag
    src_tag_list = ["Dhcpv4"]
    res = ExpTmplCmd.update_template_using_src_tag_list(root, src_tag_list)
    assert len(res) == 2

    tags_ele = None
    dhcp_ele = None
    for obj_ele in res:
        if obj_ele.tag == "Dhcpv4BlockConfig":
            dhcp_ele = obj_ele
        elif obj_ele.tag == "Tags":
            tags_ele = obj_ele
    assert tags_ele is not None
    assert dhcp_ele is not None

    # As the SrcTagList takes precedence, the elements that were originally
    # marked with serializationBase are no longer marked as such.
    serial_ele_list = root.findall(".//*[@serializationBase=\"true\"]")
    assert len(serial_ele_list) == 2
    assert tags_ele in serial_ele_list
    assert dhcp_ele in serial_ele_list


def get_test_xml():
    return """
<Template>
<Diagram/>
<Description/>
<DataModelXml>
<StcSystem id="1"
 InSimulationMode="FALSE"
 UseSmbMessaging="FALSE"
 ApplicationName="TestCenter"
 Active="TRUE"
 LocalActive="TRUE"
 Name="StcSystem 1">
  <Project id="2"
   TableViewData=""
   TestMode="L2L3"
   SelectedTechnologyProfiles=""
   ConfigurationFileName="Untitled.tcc"
   Active="TRUE"
   LocalActive="TRUE"
   Name="Project 1">
    <Relation type="DefaultSelection" target="15"/>
    <Tags id="1203" serializationBase="true"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1407"/>
      <Relation type="UserTag" target="1409"/>
      <Relation type="UserTag" target="1411"/>
      <Relation type="UserTag" target="1412"/>
      <Relation type="UserTag" target="1206"/>
      <Relation type="UserTag" target="1502"/>
      <Tag id="1206" Name="DHCP Client"></Tag>
      <Tag id="1407" Name="OuterVlan"></Tag>
      <Tag id="1409" Name="InnerVlan"></Tag>
      <Tag id="1411" Name="Dhcpv4"></Tag>
      <Tag id="1412" Name="TopLevelIf"></Tag>
      <Tag id="1502" Name="Ipv4If.Address"></Tag>
    </Tags>
    <EmulatedDevice id="2202" serializationBase="true"
     DeviceCount="1"
     EnablePingResponse="FALSE"
     RouterId="192.0.0.1"
     RouterIdStep="0.0.0.1"
     Ipv6RouterId="2000::1"
     Ipv6RouterIdStep="::1"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Device 1">
      <Relation type="UserTag" target="1206"/>
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Ipv4If id="2203"
       Address="192.85.1.3"
       AddrStep="0.0.0.1"
       AddrStepMask="255.255.255.255"
       SkipReserved="TRUE"
       AddrList=""
       AddrRepeatCount="0"
       AddrResolver="Dhcpv4"
       PrefixLength="24"
       UsePortDefaultIpv4Gateway="FALSE"
       Gateway="192.85.1.1"
       GatewayStep="0.0.0.0"
       GatewayRepeatCount="0"
       GatewayRecycleCount="0"
       UseIpAddrRangeSettingsForGateway="FALSE"
       GatewayList=""
       ResolveGatewayMac="TRUE"
       GatewayMac="00:00:01:00:00:01"
       GatewayMacResolver="default"
       Ttl="255"
       TosType="TOS"
       Tos="192"
       NeedsAuthentication="FALSE"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="IPv4 3">
        <Relation type="StackedOnEndpoint" target="1405"/>
        <Relation type="UserTag" target="1412"/>
        <StmPropertyModifier id="1112"
          TagName="TopLevelIf"
          ModifierInfo='{
  "modifierType": "RANGE",
  "propertyName": "Address",
  "objectName": "Ipv4If",
  "propertyValueDict": {
    "start": "55.55.55.55",
    "step": "0.0.0.1",
    "repeat": 0,
    "recycle": 0,
    "resetOnNewTargetObject": false
  }
}'/>
      </Ipv4If>
      <EthIIIf id="2204"
       SourceMac="00:10:94:00:00:01"
       SrcMacStep="00:00:00:00:00:01"
       SrcMacList=""
       SrcMacStepMask="00:00:ff:ff:ff:ff"
       SrcMacRepeatCount="0"
       Authenticator="default"
       UseDefaultPhyMac="FALSE"
       IfCountPerLowerIf="1"
       IfRecycleCount="0"
       IsDecorated="FALSE"
       IsLoopbackIf="FALSE"
       IsRange="TRUE"
       IsDirectlyConnected="TRUE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="EthernetII 3">
      </EthIIIf>
      <VlanIf id="1404"
       VlanId="1500"
       IdStep="1"
       Name="VLAN 1">
        <Relation type="UserTag" target="1407"/>
        <Relation type="StackedOnEndpoint" target="2204"/>
      </VlanIf>
      <VlanIf id="1405"
       VlanId="2000"
       IdStep="1"
       Name="VLAN 2">
        <Relation type="UserTag" target="1409"/>
        <Relation type="StackedOnEndpoint" target="1404"/>
      </VlanIf>
      <Dhcpv4BlockConfig id="2205"
       HostName="client_@p-@b-@s"
       DefaultHostAddrPrefixLength="24"
       OptionList="1 6 15 33 44"
       EnableRouterOption="FALSE"
       EnableArpServerId="FALSE"
       UseBroadcastFlag="TRUE"
       EnableRelayAgent="FALSE"
       ClientRelayAgent="FALSE"
       RelayAgentIpv4AddrMask="255.255.0.0"
       RelayAgentIpv4Addr="0.0.0.0"
       RelayAgentIpv4AddrStep="0.0.0.1"
       RelayServerIpv4Addr="0.0.0.0"
       RelayServerIpv4AddrStep="0.0.0.1"
       RelayPoolIpv4Addr="0.0.0.0"
       RelayPoolIpv4AddrStep="0.0.1.0"
       EnableCircuitId="FALSE"
       CircuitId="circuitId_@p"
       EnableRemoteId="FALSE"
       RemoteId="remoteId_@p-@b-@s"
       RelayClientMacAddrStart="00:10:01:00:00:01"
       RelayClientMacAddrStep="00:00:00:00:00:01"
       RelayClientMacAddrMask="00:00:00:ff:ff:ff"
       EnableAutoRetry="FALSE"
       RetryAttempts="4"
       ExportAddrToLinkedClients="FALSE"
       UseClientMacAddrForDataplane="FALSE"
       UsePartialBlockState="FALSE"
       Active="TRUE"
       LocalActive="TRUE"
       Name="DHCP 1">
        <Relation type="UserTag" target="1411"/>
        <Relation type="UsesIf" target="2203"/>
      </Dhcpv4BlockConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""


def get_raw_sb_template():
    return """
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Tags id="1237" serializationBase="true" Name="Tags 1">
      <Relation type="UserTag" target="1545"/>
      <Tag id="1545" Name="ttStreamBlock"></Tag>
    </Tags>
    <Port id="5923" Name="PortConfig1 //1/1 (offline)">
      <Relation type="ActivePhy" target="5960"/>
      <StreamBlock id="6350" serializationBase="true"
       FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;&lt;pdu
name=&quot;eth1&quot;
pdu=&quot;ethernet:EthernetII&quot;&gt;&lt;/pdu&gt;&lt;pdu
name=&quot;ip_1&quot; pdu=&quot;ipv4:IPv4&quot;&gt;&lt;tosDiffserv
name=&quot;anon_6622&quot;&gt;&lt;tos
name=&quot;anon_6623&quot;&gt;&lt;/tos&gt;&lt;/tosDiffserv&gt;
&lt;/pdu&gt;&lt;/pdus&gt;&lt;/config&gt;&lt;/frame&gt;"
       Name="StreamBlock 4">
        <Relation type="UserTag" target="1545"/>
      </StreamBlock>
    </Port>
  </Project>
</StcSystem>
"""


def get_project_sb_template():
    return """
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Relation type="DefaultSelection" target="1168"/>
    <Tags id="1208" serializationBase="true" Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Tag id="1400" Name="ttStreamBlock"></Tag>
    </Tags>
    <StreamBlock id="2111" serializationBase="true"
     FrameConfig="&lt;frame&gt;&lt;config&gt;&lt;pdus&gt;
&lt;pdu name=&quot;eth1&quot; pdu=&quot;ethernet:EthernetII&quot;&gt;
&lt;/pdu&gt;&lt;pdu name=&quot;ip_1&quot; pdu=&quot;ipv4:IPv4&quot;&gt;
&lt;tosDiffserv name=&quot;anon_2117&quot;&gt;
&lt;tos name=&quot;anon_2118&quot;&gt;&lt;/tos&gt;
&lt;/tosDiffserv&gt;&lt;/pdu&gt;&lt;/pdus&gt;&lt;/config&gt;
&lt;/frame&gt;"
     Name="Basic StreamBlock">
      <Relation type="UserTag" target="1400"/>
    </StreamBlock>
  </Project>
</StcSystem>
"""


def get_multicast_group_template():
    return """
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Tags id="1208" serializationBase="true" Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Relation type="UserTag" target="1401"/>
      <Tag id="1400" Name="ttIpv4Group"></Tag>
      <Tag id="1401" Name="ttIpv4NetworkBlock"></Tag>
    </Tags>
    <Ipv4Group id="3727" serializationBase="true"
     Name="Ipv4Group 1">
      <Relation type="UserTag" target="1400"/>
      <Ipv4NetworkBlock id="3728"
       StartIpList="225.0.0.1"
       PrefixLength="32"
       NetworkCount="1"
       AddrIncrement="1">
        <Relation type="UserTag" target="1401"/>
      </Ipv4NetworkBlock>
    </Ipv4Group>
  </Project>
</StcSystem>
"""
