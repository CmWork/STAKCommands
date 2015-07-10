from StcIntPythonPL import *
from mock import MagicMock, patch
import json
import os
import re
# import spirent.methodology.utils.xml_config_utils as xml_utils
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.routing.ExpandRouteMixCommand as ExpRouteMixCmd
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as MethManUtils


PKG = "spirent.methodology"
RPKG = PKG + ".routing"


def test_validate_fail(stc):
    res = ExpRouteMixCmd.validate([], ['Target'], [], ['Source'], 1000)
    assert res == ''
    res = ExpRouteMixCmd.validate([], ['Target'], [], ['Source'], 0)
    assert 'at least 1' in res


# exp_res is a list of tuples:
# [(bgprouterconfig, [bgp1, bgp2, ...]), ...]
# where exp_res[0] is a class name and
# bgp1, bgp2, etc are objects
def check_router_dict(router_dict, exp_res):
    assert len(exp_res) == len(router_dict.keys())
    for router_tuple in exp_res:
        r_type = router_tuple[0]
        assert r_type in router_dict.keys()

        hnd_list = [obj.GetObjectHandle() for obj in router_dict[r_type]]
        assert len(hnd_list) == len(router_tuple[1])
        for exp_obj in router_tuple[1]:
            assert exp_obj.GetObjectHandle() in hnd_list


def test_get_routers(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd = ctor.Create(RPKG + ".ExpandRouteMixCommand", sequencer)
    gtc_p = patch(RPKG + ".ExpandRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Create and tag stuff
    tags = project.GetObject("Tags")
    assert tags

    proto_mix = ctor.Create("StmProtocolMix", project)
    tmpl1 = ctor.Create("StmTemplateConfig", proto_mix)
    tmpl2 = ctor.Create("StmTemplateConfig", proto_mix)
    tmpl3 = ctor.Create("StmTemplateConfig", project)
    dev1 = ctor.Create("EmulatedDevice", project)
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    dev2 = ctor.Create("EmulatedDevice", project)
    isis1 = ctor.Create("IsisRouterConfig", dev2)
    ospfv21 = ctor.Create("Ospfv2RouterConfig", dev2)
    dev3 = ctor.Create("EmulatedDevice", project)
    isis2 = ctor.Create("IsisRouterConfig", dev3)
    dev4 = ctor.Create("EmulatedDevice", project)
    ospfv22 = ctor.Create("Ospfv2RouterConfig", dev4)

    tmpl1.AddObject(dev1, RelationType("GeneratedObject"))
    tmpl1.AddObject(dev3, RelationType("GeneratedObject"))
    tmpl2.AddObject(dev2, RelationType("GeneratedObject"))
    tmpl3.AddObject(ospfv22, RelationType("GeneratedObject"))

    proto_tag = tag_utils.add_tag_to_object(proto_mix, "StmProtocolMix")
    tmpl_tag1 = tag_utils.add_tag_to_object(tmpl1, "StmTemplateConfig1")
    tmpl_tag2 = tag_utils.add_tag_to_object(tmpl2, "StmTemplateConfig2")
    tmpl_tag3 = tag_utils.add_tag_to_object(tmpl3, "StmTemplateConfig3")
    dev_tag1 = tag_utils.add_tag_to_object(dev1, "EmulatedDevice1")
    dev_tag2 = tag_utils.add_tag_to_object(dev2, "EmulatedDevice2")
    dev_tag3 = tag_utils.add_tag_to_object(dev3, "EmulatedDevice3")
    dev_tag4 = tag_utils.add_tag_to_object(dev4, "EmulatedDevice4")
    bgp_tag1 = tag_utils.add_tag_to_object(bgp1, "BgpRouterConfig1")
    isis_tag1 = tag_utils.add_tag_to_object(isis1, "IsisRouterConfig1")
    isis_tag2 = tag_utils.add_tag_to_object(isis2, "IsisRouterConfig2")
    ospfv2_tag1 = tag_utils.add_tag_to_object(ospfv21, "Ospfv2RouterConfig1")
    ospfv2_tag2 = tag_utils.add_tag_to_object(ospfv22, "Ospfv2RouterConfig2")
    assert proto_tag
    assert tmpl_tag1
    assert tmpl_tag2
    assert tmpl_tag3
    assert dev_tag1
    assert dev_tag2
    assert dev_tag3
    assert dev_tag4
    assert bgp_tag1
    assert isis_tag1
    assert isis_tag2
    assert ospfv2_tag1
    assert ospfv2_tag2

    # Test target objects (ProtocolConfig)
    ret_val = ExpRouteMixCmd.get_routers([bgp1.GetObjectHandle(),
                                          ospfv21.GetObjectHandle()], [])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("Ospfv2RouterConfig", [ospfv21])])

    # Test target objects (EmulatedDevice)
    ret_val = ExpRouteMixCmd.get_routers([dev2.GetObjectHandle()], [])
    assert ret_val
    check_router_dict(ret_val,
                      [("Ospfv2RouterConfig", [ospfv21]),
                       ("IsisRouterConfig", [isis1])])

    # Test target objects (StmProtocolMix)
    ret_val = ExpRouteMixCmd.get_routers([proto_mix.GetObjectHandle()], [])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("Ospfv2RouterConfig", [ospfv21]),
                       ("IsisRouterConfig", [isis1, isis2])])

    # Test target objects (StmTemplateConfig)
    ret_val = ExpRouteMixCmd.get_routers([tmpl1.GetObjectHandle(),
                                          tmpl3.GetObjectHandle()], [])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("IsisRouterConfig", [isis2]),
                       ("Ospfv2RouterConfig", [ospfv22])])

    # Test target objects (mixed)
    ret_val = ExpRouteMixCmd.get_routers([dev4.GetObjectHandle(),
                                          tmpl3.GetObjectHandle(),
                                          tmpl1.GetObjectHandle(),
                                          dev2.GetObjectHandle()], [])
    assert ret_val
    check_router_dict(ret_val,
                      [("Ospfv2RouterConfig", [ospfv21, ospfv22]),
                       ("BgpRouterConfig", [bgp1]),
                       ("IsisRouterConfig", [isis1, isis2])])

    # Test tagged target objects (ProtocolConfig)
    ret_val = ExpRouteMixCmd.get_routers([],
                                         ["Ospfv2RouterConfig1",
                                          "Ospfv2RouterConfig2",
                                          "BgpRouterConfig1"])
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("Ospfv2RouterConfig", [ospfv21, ospfv22])])

    # Test tagged target objects (EmulatedDevice)
    ret_val = ExpRouteMixCmd.get_routers([],
                                         ["EmulatedDevice2",
                                          "EmulatedDevice4"])
    check_router_dict(ret_val,
                      [("IsisRouterConfig", [isis1]),
                       ("Ospfv2RouterConfig", [ospfv21, ospfv22])])

    # Test tagged target objects (StmProtocolMix)
    ret_val = ExpRouteMixCmd.get_routers([], ["StmProtocolMix"])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("Ospfv2RouterConfig", [ospfv21]),
                       ("IsisRouterConfig", [isis1, isis2])])

    # Test target objects (StmTemplateConfig)
    ret_val = ExpRouteMixCmd.get_routers([],
                                         ["StmTemplateConfig1",
                                          "StmTemplateConfig3"])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("IsisRouterConfig", [isis2]),
                       ("Ospfv2RouterConfig", [ospfv22])])

    # Test tagged target objects (mixed)
    ret_val = ExpRouteMixCmd.get_routers([],
                                         ["EmulatedDevice4",
                                          "StmTemplateConfig3",
                                          "StmTemplateConfig1",
                                          "EmulatedDevice2",
                                          "Ospfv2RouterConfig2"])
    assert ret_val
    check_router_dict(ret_val,
                      [("Ospfv2RouterConfig", [ospfv21, ospfv22]),
                       ("BgpRouterConfig", [bgp1]),
                       ("IsisRouterConfig", [isis1, isis2])])

    # Test mix of tags and objects
    ret_val = ExpRouteMixCmd.get_routers([dev1.GetObjectHandle(),
                                          dev2.GetObjectHandle(),
                                          dev4.GetObjectHandle()],
                                         ["StmTemplateConfig3",
                                          "BgpRouterConfig1"])
    assert ret_val
    check_router_dict(ret_val,
                      [("BgpRouterConfig", [bgp1]),
                       ("IsisRouterConfig", [isis1]),
                       ("Ospfv2RouterConfig", [ospfv21, ospfv22])])
    gtc_p.stop()


def test_get_routers_fail(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    cmd = ctor.Create(RPKG + ".ExpandRouteMixCommand", sequencer)
    gtc_p = patch(RPKG + ".ExpandRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Create some objects
    tags = project.GetObject("Tags")
    assert tags
    dev = ctor.Create("EmulatedDevice", project)
    bgp1 = ctor.Create("BgpRouterConfig", dev)
    assert bgp1
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Tag1")
    tags.AddObject(tag1, RelationType("UserTag"))

    # Empty lists
    ret_val = ExpRouteMixCmd.get_routers([], [])
    assert not ret_val
    assert "No routers found in TargetObjectList or TargetObjectTagList" \
        in cmd.Get("Status")

    # Valid but empty tags
    ret_val = ExpRouteMixCmd.get_routers([], ["Tag1"])
    assert not ret_val
    assert cmd.Get("Status") == \
        "No routers found in TargetObjectList or TargetObjectTagList"

    # Invalid object handle
    ret_val = ExpRouteMixCmd.get_routers([0], [])
    assert not ret_val
    assert cmd.Get("Status") == \
        "No routers found in TargetObjectList or TargetObjectTagList"

    gtc_p.stop()


def test_process_wizard_args(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Use a unique name that won't conflict with existing files
    route_file = 'unit_test_bgp_fullroute_{}.txt'.format(os.getpid())
    add_unit_test_template(route_file, get_fullroute_txt())
    filename = os.path.normpath(get_unit_test_filename(route_file))
    tmpl.Set('TemplateXml', get_import_xml(filename))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('Status') == ''
        assert cmd.Get('PassFailState') == 'PASSED'
    route_list = tag_utils.get_tagged_objects_from_string_names(['ttBgpRouteObject'])
    route_count = len(route_list)
    block_list = [x.GetObject('NetworkBlock') for x in route_list]
    total_routes = sum([b.Get('NetworkCount') for b in block_list])
    type_list = set()
    for r in route_list:
        type_list.add(r.GetType())
    exp_type_list = set(['bgpipv4routeconfig'])
    # The Route file contains 21 routes, and the total should be 21
    # (previously, the allocate would change it to 1000, the default value for
    # RouteCount for ExpandRouteMix)
    assert route_list
    assert type(route_list) is list
    assert 21 == route_count
    assert 21 == total_routes
    assert type_list == exp_type_list
    pref_set = set()
    # There are 50 lines in the source file, but the system consolidates
    # blocks by prefix length. Check all entries in the route definition file
    exp_pref_set = set()
    for line in get_fullroute_txt().split('\n'):
        m = re.match(r'^\*>i([\.0-9]+/[0-9]+)', line)
        if m:
            exp_pref_set.add(m.group(1))
    # For every block, go and get the prefix + length and store them in a set
    for b in block_list:
        pref_len = b.Get('PrefixLength')
        for ip in b.GetCollection('StartIpList'):
            pref_set.add('{}/{}'.format(ip, pref_len))
    assert 50 == len(pref_set)
    assert exp_pref_set == pref_set
    # Clean up
    remove_unit_test_template(route_file)


def test_process_wizard_args_prefix_dist(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create('Port', project)
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        dev.AddObject(port, RelationType("AffiliationPort"))
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "AllRoutePrefixDist.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "srcObjectTagName": "ttBgpRouteGenParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.RoutePrefixDistributionCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    tmpl.Set('TemplateXml', get_prefix_dist_xml())
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('Status') == ''
        assert cmd.Get('PassFailState') == 'PASSED'
    route_list = tag_utils.get_tagged_objects_from_string_names(['ttBgpRouteObject'])
    route_count = len(route_list)
    block_list = [x.GetObject('NetworkBlock') for x in route_list]
    total_routes = sum([b.Get('NetworkCount') for b in block_list])
    type_list = set()
    for r in route_list:
        type_list.add(r.GetType())
    exp_type_list = set(['bgpipv4routeconfig'])
    # The Route file contains 2 routes, with a grand total of 4 routes
    # (previously, the allocate would change it to 1000, the default value for
    # RouteCount for ExpandRouteMix)
    assert 2 == route_count
    assert 4 == total_routes
    assert type_list == exp_type_list
    pref_set = set()

    # For every block, go and get the prefix + length and store them in a set
    for b in block_list:
        pref_len = b.Get('PrefixLength')
        for ip in b.GetCollection('StartIpList'):
            pref_set.add('{}/{}'.format(ip, pref_len))
    assert 2 == len(pref_set)

    print pref_set
    exp_pref_set = set()
    exp_pref_set.add('{}/{}'.format('1.0.0.0', 15))
    exp_pref_set.add('{}/{}'.format('1.4.0.0', 14))
    assert exp_pref_set == pref_set


def test_process_wizard_args_no_file(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Here, give it a bogus file
    route_file = 'bogus_file.txt'
    tmpl.Set('TemplateXml', get_import_xml(route_file))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'Failed to generate' in cmd.Get('Status')


def test_process_wizard_args_no_target_tag_list(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Bogus file comes into play after target tag
    route_file = 'bogus_file.txt'
    tmpl.Set('TemplateXml', get_import_xml(route_file))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'No target tag list' in cmd.Get('Status')


def test_process_wizard_args_no_source_object(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Bogus file comes into play after source tag
    route_file = 'bogus_file.txt'
    tmpl.Set('TemplateXml', get_import_xml(route_file))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'No source object' in cmd.Get('Status')


def test_process_wizard_args_no_command(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Bogus file comes into play after command name checks
    route_file = 'bogus_file.txt'
    tmpl.Set('TemplateXml', get_import_xml(route_file))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'Command name not specified' in cmd.Get('Status')


def test_process_wizard_args_nothing_targetted(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "BGP_Import_Routes.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttNothing"],
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Bogus file comes in to play after the tagged target (this is different
    # from the command's target, which points to the routers for the purpose
    # of adding routes)
    route_file = 'bogus_file.txt'
    tmpl.Set('TemplateXml', get_import_xml(route_file))
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'empty list' in cmd.Get('Status')


def test_process_wizard_args_bad_template(stc):
    ctor = CScriptableCreator()
    hnd_reg = CHandleRegistry.Instance()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    # Create devices
    dev_list = []
    with AutoCommand('DeviceCreateCommand') as cmd:
        cmd.Set('DeviceType', 'EmulatedDevice')
        cmd.SetCollection('IfStack', ['Ipv4If', 'EthIIIf'])
        cmd.SetCollection('IfCount', [1] * 2)
        cmd.Execute()
        hdl_list = cmd.GetCollection('ReturnList')
        dev_list = [hnd_reg.Find(h) for h in hdl_list]
    tag_utils.get_tag_object('ttEmulatedDevice')
    tag_utils.get_tag_object('ttBgpRouterConfig')
    for dev in dev_list:
        bgp = ctor.Create('BgpRouterConfig', dev)
        tag_utils.add_tag_to_object(dev, 'ttEmulatedDevice')
        tag_utils.add_tag_to_object(bgp, 'ttBgpRouterConfig')
    # Create Mix and template object(s)
    route_mix = ctor.Create('StmTemplateMix', project)
    assert route_mix
    mix_dict = {
        "routeCount": 10,
        "components": [
            {
                "weight": "100%",
                "baseTemplateFile": "bogus.xml",
                "postExpandModify": [
                    {
                        "bllWizardExpand": {
                            "targetTagList": ["ttEmulatedDevice"],
                            "srcObjectTagName": "ttBgpImportRouteTableParams",
                            "createdRoutesTagName": "ttBgpRouteObject",
                            "commandName":
                            "spirent.methodology.routing.BgpImportRoutesCommand"
                        }
                    }
                ]
            }
        ]
    }
    route_mix.Set('MixInfo', json.dumps(mix_dict))
    tmpl = ctor.Create('StmTemplateConfig', route_mix)
    assert tmpl
    # Empty the template XML in this case, meaning it will fail when expanding
    tmpl.Set('TemplateXml', '')
    with AutoCommand(RPKG + '.ExpandRouteMixCommand') as cmd:
        cmd.SetCollection('TargetObjectTagList', ['ttEmulatedDevice'])
        cmd.SetCollection('SrcObjectList', [route_mix.GetObjectHandle()])
        cmd.Execute()
        assert cmd.Get('PassFailState') == 'FAILED'
        assert 'failed:' in cmd.Get('Status')


def test_process_route_args(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    sequencer = stc_sys.GetObject("Sequencer")

    plLogger = PLLogger.GetLogger("test_process_route_args")

    cmd = ctor.Create(RPKG + ".ExpandRouteMixCommand", sequencer)
    gtc_p = patch(RPKG + ".ExpandRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    routes_template = get_simple_bgp_routes_xml()

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    left_port_group_tag = ctor.Create("Tag", tags)
    left_port_group_tag.Set("Name", "Left")
    port1.AddObject(left_port_group_tag, RelationType("UserTag"))
    tags.AddObject(left_port_group_tag, RelationType("UserTag"))

    # Create a tagged BGP router
    rtr = ctor.Create("EmulatedDevice", project)
    rtr.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If = ctor.Create("Ipv4If", rtr)
    ethIIIf = ctor.Create("EthIIIf", rtr)
    ipv4If.AddObject(ethIIIf, RelationType("StackedOnEndpoint"))
    rtr.AddObject(ipv4If, RelationType("PrimaryIf"))
    rtr.AddObject(ethIIIf, RelationType("TopLevelIf"))
    bgp = ctor.Create("BgpRouterConfig", rtr)
    assert bgp

    rtr_tag = ctor.Create("Tag", tags)
    rtr_tag.Set("Name", "RouterTag")
    bgp_tag = ctor.Create("Tag", tags)
    bgp_tag.Set("Name", "BgpTag")

    # Create the routers_dict
    routers_dict = {}
    routers_dict["BgpRouterConfig"] = [bgp]

    # Create the StmTemplateConfig
    tmpl = ctor.Create("StmTemplateConfig", project)
    tmpl.Set("TemplateXml", routes_template)

    plLogger.LogInfo("calling process_route_args")

    # Call process_route_args
    res = ExpRouteMixCmd.process_route_args(tmpl, routers_dict)
    assert res

    route_obj_list = bgp.GetObjects("BgpIpv4RouteConfig")
    assert len(route_obj_list) == 1
    bgpv4_route_block = route_obj_list[0]
    assert bgpv4_route_block
    assert bgpv4_route_block.Get("NextHop") == "55.55.57.1"
    assert bgpv4_route_block.Get("NextHopIncrement") == "0.0.0.55"
    route_block_tag = bgpv4_route_block.GetObject("Tag",
                                                  RelationType("UserTag"))
    assert route_block_tag
    assert route_block_tag.Get("Name") == "ttBgpIpv4RouteConfig"
    net_block_list = bgpv4_route_block.GetObjects("Ipv4NetworkBlock")
    assert len(net_block_list) == 1
    net_block = net_block_list[0]
    assert net_block
    assert net_block.GetCollection("StartIpList") == ["192.192.192.1"]
    assert net_block.Get("PrefixLength") == 22
    assert net_block.Get("NetworkCount") == 11
    assert net_block.Get("AddrIncrement") == 2

    net_block_tag = net_block.GetObject("Tag", RelationType("UserTag"))
    assert net_block_tag
    assert net_block_tag.Get("Name") == "ttBgpIpv4RouteConfig.Ipv4NetworkBlock"

    # Clean up
    gtc_p.stop()


# FIXME:
# Finish this unit test
def test_process_route_args_fail(stc):
    pass


def test_expand_run_validate(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")

    cmd = ctor.Create(RPKG + ".ExpandRouteMixCommand", sequencer)
    gtc_p = patch(RPKG + ".ExpandRouteMixCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()
    res = ExpRouteMixCmd.validate([], [], [], [], 1)
    assert res == ""
    gtc_p.stop()


def test_expand_route_mix_single_component_single_route_type(stc):
    plLogger = PLLogger.GetLogger(
        "test_expand_route_mix_single_component_single_route_type")
    plLogger.LogInfo("start")

    routes_template = get_routes_xml()

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    left_port_group_tag = ctor.Create("Tag", tags)
    left_port_group_tag.Set("Name", "Left")
    port1.AddObject(left_port_group_tag, RelationType("UserTag"))
    tags.AddObject(left_port_group_tag, RelationType("UserTag"))

    # Create a tagged BGP router
    rtr = ctor.Create("EmulatedDevice", project)
    rtr.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If = ctor.Create("Ipv4If", rtr)
    ethIIIf = ctor.Create("EthIIIf", rtr)
    ipv4If.AddObject(ethIIIf, RelationType("StackedOnEndpoint"))
    rtr.AddObject(ipv4If, RelationType("PrimaryIf"))
    rtr.AddObject(ethIIIf, RelationType("TopLevelIf"))
    bgp = ctor.Create("BgpRouterConfig", rtr)
    assert bgp

    rtr_tag = ctor.Create("Tag", tags)
    rtr_tag.Set("Name", "RouterTag")
    rtr.AddObject(rtr_tag, RelationType("UserTag"))
    bgp_tag = ctor.Create("Tag", tags)
    bgp_tag.Set("Name", "BgpTag")
    bgp.AddObject(bgp_tag, RelationType("UserTag"))

    # Create the route mix
    route_mix = ctor.Create("StmTemplateMix", project)

    # Merge BGP Routes
    # NOTE: This unit test is testing expand, not create.
    # This JSON is created but not used.  All routes in
    # get_routes_xml() that can be merged onto target objects
    # will be.
    comp_dict = {}
    comp_dict["weight"] = "100%"
    comp_dict["baseTemplateFile"] = "AllRouters.xml"

    mix_dict = {}
    mix_dict["routeCount"] = 100
    mix_dict["components"] = [comp_dict]

    route_mix.Set("MixInfo", json.dumps(mix_dict))

    # Create the StmTemplateConfig child that would have been
    # created by the iterator
    route_template = ctor.Create("StmTemplateConfig", route_mix)
    route_template.Set("TemplateXml", routes_template)

    # Call Expand
    cmd = ctor.CreateCommand(RPKG + ".ExpandRouteMixCommand")
    cmd.SetCollection("TargetObjectTagList", ["RouterTag"])
    cmd.SetCollection("SrcObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("RouteCount", 1000)
    cmd.Execute()
    assert cmd.Get("Status") == ""
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check original config to check that it didn't change
    bgp_proto = rtr.GetObject("BgpRouterConfig")
    assert bgp_proto

    # Check GeneratedObjects
    gen_obj_list = route_template.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 2

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    bgpv4_route_tag = None
    bgpv4_route_net_block_tag = None
    bgpv6_route_tag = None
    bgpv6_route_net_block_tag = None

    for tag in tag_list:
        if tag.Get("Name") == "ttBgpIpv4RouteConfig":
            bgpv4_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv4RouteConfig.Ipv4NetworkBlock":
            bgpv4_route_net_block_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig":
            bgpv6_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig.Ipv6NetworkBlock":
            bgpv6_route_net_block_tag = tag
    assert bgpv4_route_tag
    assert bgpv4_route_net_block_tag
    assert bgpv6_route_tag
    assert bgpv6_route_net_block_tag

    # Check BGPv4
    bgpv4_route_block_list = bgp_proto.GetObjects("BgpIpv4RouteConfig")
    assert len(bgpv4_route_block_list) == 1
    bgpv4_route_block = bgpv4_route_block_list[0]
    assert bgpv4_route_block
    tmpl = bgpv4_route_block.GetObject("StmTemplateConfig",
                                       RelationType("GeneratedObject", 1))
    assert tmpl
    assert tmpl.GetObjectHandle() == route_template.GetObjectHandle()
    act_tag = bgpv4_route_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == bgpv4_route_tag.GetObjectHandle()

    net_block_list = bgpv4_route_block.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    bgpv4_net_block = net_block_list[0]
    assert bgpv4_net_block
    act_tag = bgpv4_net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        bgpv4_route_net_block_tag.GetObjectHandle()

    # Check route counts
    assert bgpv4_net_block.Get("NetworkCount") == 500

    # Check BGPv6
    bgpv6_route_block_list = bgp_proto.GetObjects("BgpIpv6RouteConfig")
    assert len(bgpv6_route_block_list) == 1
    bgpv6_route_block = bgpv6_route_block_list[0]
    assert bgpv6_route_block
    tmpl = bgpv6_route_block.GetObject("StmTemplateConfig",
                                       RelationType("GeneratedObject", 1))
    assert tmpl
    assert tmpl.GetObjectHandle() == route_template.GetObjectHandle()
    act_tag = bgpv6_route_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == bgpv6_route_tag.GetObjectHandle()

    net_block_list = bgpv6_route_block.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    bgpv6_net_block = net_block_list[0]
    assert bgpv6_net_block
    act_tag = bgpv6_net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        bgpv6_route_net_block_tag.GetObjectHandle()

    # Check route counts
    assert bgpv6_net_block.Get("NetworkCount") == 500


def test_expand_route_mix_single_component_multiple_route_types(stc):
    plLogger = PLLogger.GetLogger(
        "test_expand_route_mix_single_component_multiple_route_types")
    plLogger.LogInfo("start")

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    left_port_group_tag = ctor.Create("Tag", tags)
    left_port_group_tag.Set("Name", "Left")
    port1.AddObject(left_port_group_tag, RelationType("UserTag"))
    tags.AddObject(left_port_group_tag, RelationType("UserTag"))

    # Routes Template (being merged in)
    routes_template = get_routes_xml()

    # Create a tagged router running ISIS and BGP
    rtr = ctor.Create("EmulatedDevice", project)
    rtr.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If = ctor.Create("Ipv4If", rtr)
    ethIIIf = ctor.Create("EthIIIf", rtr)
    ipv4If.AddObject(ethIIIf, RelationType("StackedOnEndpoint"))
    rtr.AddObject(ipv4If, RelationType("PrimaryIf"))
    rtr.AddObject(ethIIIf, RelationType("TopLevelIf"))
    bgp = ctor.Create("BgpRouterConfig", rtr)
    assert bgp
    isis = ctor.Create("IsisRouterConfig", rtr)
    assert isis

    rtr_tag = ctor.Create("Tag", tags)
    rtr_tag.Set("Name", "RouterTag")
    bgp_tag = ctor.Create("Tag", tags)
    bgp_tag.Set("Name", "BgpTag")
    isis_tag = ctor.Create("Tag", tags)
    isis_tag.Set("Name", "IsisTag")
    tags.AddObject(rtr_tag, RelationType("UserTag"))
    tags.AddObject(bgp_tag, RelationType("UserTag"))
    tags.AddObject(isis_tag, RelationType("UserTag"))

    rtr.AddObject(rtr_tag, RelationType("UserTag"))

    # Create the route mix
    route_mix = ctor.Create("StmTemplateMix", project)

    # Merge Routes
    # NOTE: This unit test is testing expand, not create.
    # This JSON is created but not used.  All routes in
    # get_routes_xml() that can be merged onto target objects
    # will be.
    comp_dict = {}
    comp_dict["weight"] = "100%"
    comp_dict["baseTemplateFile"] = "AllRouters.xml"

    mix_dict = {}
    mix_dict["routeCount"] = 100
    mix_dict["components"] = [comp_dict]

    route_mix.Set("MixInfo", json.dumps(mix_dict))

    # Create the StmTemplateConfig child that would have been
    # created by the iterator
    route_template = ctor.Create("StmTemplateConfig", route_mix)
    route_template.Set("TemplateXml", routes_template)

    # Call Expand
    cmd = ctor.CreateCommand(RPKG + ".ExpandRouteMixCommand")
    cmd.SetCollection("TargetObjectTagList", ["RouterTag"])
    cmd.SetCollection("SrcObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("RouteCount", 1000)
    cmd.Execute()
    cmd.MarkDelete()

    # Check original config to check that it didn't change
    bgp_proto = rtr.GetObject("BgpRouterConfig")
    isis_proto = rtr.GetObject("IsisRouterConfig")
    ospfv2_proto = rtr.GetObject("Ospfv2RouterConfig")
    assert bgp_proto
    assert isis_proto
    assert not ospfv2_proto

    # Check GeneratedObjects
    gen_obj_list = route_template.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 3

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    bgpv4_route_tag = None
    bgpv4_route_net_block_tag = None
    bgpv6_route_tag = None
    bgpv6_route_net_block_tag = None
    rtr_lsa_tag = None
    sum_lsa_tag = None
    ext_lsa_tag = None
    isis_lsp_tag = None
    isis_route_tag = None
    isis_route_net_block_tag = None

    for tag in tag_list:
        if tag.Get("Name") == "ttBgpIpv4RouteConfig":
            bgpv4_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv4RouteConfig.Ipv4NetworkBlock":
            bgpv4_route_net_block_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig":
            bgpv6_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig.Ipv6NetworkBlock":
            bgpv6_route_net_block_tag = tag
        elif tag.Get("Name") == "ttRouterLsa":
            rtr_lsa_tag = tag
        elif tag.Get("Name") == "ttSummaryLsaBlock":
            sum_lsa_tag = tag
        elif tag.Get("Name") == "ttExternalLsaBlock":
            ext_lsa_tag = tag
        elif tag.Get("Name") == "ttIsisLspConfig":
            isis_lsp_tag = tag
        elif tag.Get("Name") == "ttIpv4IsisRoutesConfig":
            isis_route_tag = tag
        elif tag.Get("Name") == "ttIpv4IsisRoutesConfig.Ipv4NetworkBlock":
            isis_route_net_block_tag = tag
    assert bgpv4_route_tag
    assert bgpv4_route_net_block_tag
    assert bgpv6_route_tag
    assert bgpv6_route_net_block_tag
    # FIXME:
    # These should not be loaded
    assert rtr_lsa_tag
    assert sum_lsa_tag
    assert ext_lsa_tag
    # assert not rtr_lsa_tag
    # assert not sum_lsa_tag
    # assert not ext_lsa_tag
    assert isis_lsp_tag
    assert isis_route_tag
    assert isis_route_net_block_tag

    # Check BGPv4
    bgpv4_route_block_list = bgp_proto.GetObjects("BgpIpv4RouteConfig")
    assert len(bgpv4_route_block_list) == 1
    bgpv4_route_block = bgpv4_route_block_list[0]
    assert bgpv4_route_block
    tmpl = bgpv4_route_block.GetObject("StmTemplateConfig",
                                       RelationType("GeneratedObject", 1))
    assert tmpl
    assert tmpl.GetObjectHandle() == route_template.GetObjectHandle()
    act_tag = bgpv4_route_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == bgpv4_route_tag.GetObjectHandle()

    net_block_list = bgpv4_route_block.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    bgpv4_net_block = net_block_list[0]
    assert bgpv4_net_block
    act_tag = bgpv4_net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        bgpv4_route_net_block_tag.GetObjectHandle()

    # Collect route counts for checking later
    bgpv4_count = bgpv4_net_block.Get("NetworkCount")

    # Check BGPv6
    bgpv6_route_block_list = bgp_proto.GetObjects("BgpIpv6RouteConfig")
    assert len(bgpv6_route_block_list) == 1
    bgpv6_route_block = bgpv6_route_block_list[0]
    assert bgpv6_route_block
    tmpl = bgpv6_route_block.GetObject("StmTemplateConfig",
                                       RelationType("GeneratedObject", 1))
    assert tmpl
    assert tmpl.GetObjectHandle() == route_template.GetObjectHandle()
    act_tag = bgpv6_route_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == bgpv6_route_tag.GetObjectHandle()

    net_block_list = bgpv6_route_block.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    bgpv6_net_block = net_block_list[0]
    assert bgpv6_net_block
    act_tag = bgpv6_net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        bgpv6_route_net_block_tag.GetObjectHandle()

    # Collect route counts for checking later
    bgpv6_count = bgpv6_net_block.Get("NetworkCount")

    # Check ISIS
    isis_lsp_list = isis_proto.GetObjects("IsisLspConfig")
    assert len(isis_lsp_list) == 1
    isis_lsp = isis_lsp_list[0]
    assert isis_lsp
    tmpl = isis_lsp.GetObject("StmTemplateConfig",
                              RelationType("GeneratedObject", 1))
    assert tmpl
    assert tmpl.GetObjectHandle() == route_template.GetObjectHandle()
    act_tag = isis_lsp.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == isis_lsp_tag.GetObjectHandle()

    ipv4_route_list = isis_lsp.GetObjects("Ipv4IsisRoutesConfig")
    assert len(ipv4_route_list) == 1
    ipv4_route = ipv4_route_list[0]
    assert ipv4_route
    act_tag = ipv4_route.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == isis_route_tag.GetObjectHandle()

    net_block_list = ipv4_route.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    net_block = net_block_list[0]
    assert net_block
    act_tag = net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        isis_route_net_block_tag.GetObjectHandle()

    # Collect route counts for checking later
    isis_count = net_block.Get("NetworkCount")

    # Check the route counts
    # Dividing 1000 routes yields two blocks with 333 and one with 334.
    # The routes are distributed to the objects in creation order but
    # here we'll just assume two have 333 and one has 334.
    even_count = 0
    rem_count = 0
    for count in [bgpv4_count, bgpv6_count, isis_count]:
        if count == 333:
            even_count = even_count + 1
        elif count == 334:
            rem_count = rem_count + 1
    assert even_count == 2
    assert rem_count == 1


def test_expand_route_mix_on_stm_proto_mix(stc):
    plLogger = PLLogger.GetLogger(
        "test_expand_route_mix_on_stm_proto_mix")
    plLogger.LogInfo("start")
    routes_template = get_routes_xml()

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    left_port_group_tag = ctor.Create("Tag", tags)
    left_port_group_tag.Set("Name", "Left")
    port1.AddObject(left_port_group_tag, RelationType("UserTag"))
    tags.AddObject(left_port_group_tag, RelationType("UserTag"))

    # Create Tags
    dev_tag = ctor.Create("Tag", tags)
    dev_tag.Set("Name", "ttEmulatedDevice")
    bgp_tag = ctor.Create("Tag", tags)
    bgp_tag.Set("Name", "ttBgpRouterConfig")
    isis_tag = ctor.Create("Tag", tags)
    isis_tag.Set("Name", "ttIsisRouterConfig")
    tags.AddObject(dev_tag, RelationType("UserTag"))
    tags.AddObject(bgp_tag, RelationType("UserTag"))
    tags.AddObject(isis_tag, RelationType("UserTag"))

    # Create StmProtocolMix
    proto_mix = ctor.Create("StmProtocolMix", project)

    # Create StmTemplateConfigs
    proto_tmpl1 = ctor.Create("StmTemplateConfig", proto_mix)
    proto_tmpl2 = ctor.Create("StmTemplateConfig", proto_mix)
    proto_tmpl3 = ctor.Create("StmTemplateConfig", proto_mix)

    # Create BGP Routers under the first two StmTemplateConfigs
    dev1 = ctor.Create("EmulatedDevice", project)
    dev1.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If1 = ctor.Create("Ipv4If", dev1)
    ethIIIf1 = ctor.Create("EthIIIf", dev1)
    ipv4If1.AddObject(ethIIIf1, RelationType("StackedOnEndpoint"))
    dev1.AddObject(ipv4If1, RelationType("PrimaryIf"))
    dev1.AddObject(ipv4If1, RelationType("TopLevelIf"))
    dev1.AddObject(dev_tag, RelationType("UserTag"))
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    bgp1.AddObject(bgp_tag, RelationType("UserTag"))
    proto_tmpl1.AddObject(dev1, RelationType("GeneratedObject"))

    dev2 = ctor.Create("EmulatedDevice", project)
    dev2.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If2 = ctor.Create("Ipv4If", dev2)
    ethIIIf2 = ctor.Create("EthIIIf", dev2)
    ipv4If2.AddObject(ethIIIf2, RelationType("StackedOnEndpoint"))
    dev2.AddObject(ipv4If2, RelationType("PrimaryIf"))
    dev2.AddObject(ipv4If2, RelationType("TopLevelIf"))
    dev2.AddObject(dev_tag, RelationType("UserTag"))
    bgp2 = ctor.Create("BgpRouterConfig", dev2)
    bgp2.AddObject(bgp_tag, RelationType("UserTag"))
    proto_tmpl2.AddObject(dev2, RelationType("GeneratedObject"))

    dev3 = ctor.Create("EmulatedDevice", project)
    dev3.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If3 = ctor.Create("Ipv4If", dev3)
    ethIIIf3 = ctor.Create("EthIIIf", dev3)
    ipv4If3.AddObject(ethIIIf3, RelationType("StackedOnEndpoint"))
    dev3.AddObject(ipv4If3, RelationType("PrimaryIf"))
    dev3.AddObject(ipv4If3, RelationType("TopLevelIf"))
    dev3.AddObject(dev_tag, RelationType("UserTag"))
    bgp3 = ctor.Create("BgpRouterConfig", dev3)
    bgp3.AddObject(bgp_tag, RelationType("UserTag"))
    proto_tmpl2.AddObject(dev3, RelationType("GeneratedObject"))

    # Create an ISIS Router under the third StmTemplateConfig
    dev4 = ctor.Create("EmulatedDevice", project)
    dev4.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If4 = ctor.Create("Ipv4If", dev4)
    ethIIIf4 = ctor.Create("EthIIIf", dev4)
    ipv4If4.AddObject(ethIIIf4, RelationType("StackedOnEndpoint"))
    dev4.AddObject(ipv4If4, RelationType("PrimaryIf"))
    dev4.AddObject(ipv4If4, RelationType("TopLevelIf"))
    dev4.AddObject(dev_tag, RelationType("UserTag"))
    isis4 = ctor.Create("IsisRouterConfig", dev4)
    isis4.AddObject(isis_tag, RelationType("UserTag"))
    proto_tmpl3.AddObject(dev4, RelationType("GeneratedObject"))

    # Create the route mix
    route_mix = ctor.Create("StmTemplateMix", project)
    route_tmpl1 = ctor.Create("StmTemplateConfig", route_mix)
    route_tmpl2 = ctor.Create("StmTemplateConfig", route_mix)
    route_tmpl3 = ctor.Create("StmTemplateConfig", route_mix)
    route_tmpl1.Set("TemplateXml", routes_template)
    route_tmpl2.Set("TemplateXml", routes_template)
    route_tmpl3.Set("TemplateXml", routes_template)

    # Merge Routes
    # NOTE: This unit test is testing expand, not create.
    # This JSON is created but not used.  All routes in
    # get_routes_xml() that can be merged onto target objects
    # will be.
    comp_dict1 = {}
    comp_dict1["weight"] = "70"
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2 = {}
    comp_dict2["weight"] = "140"
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3 = {}
    comp_dict3["weight"] = "700"
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"

    mix_dict = {}
    mix_dict["routeCount"] = 100
    mix_dict["components"] = [comp_dict1, comp_dict2, comp_dict3]

    route_mix.Set("MixInfo", json.dumps(mix_dict))

    # Call Expand
    cmd = ctor.CreateCommand(RPKG + ".ExpandRouteMixCommand")
    cmd.SetCollection("TargetObjectList", [proto_mix.GetObjectHandle()])
    cmd.SetCollection("SrcObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("RouteCount", 1000)
    cmd.Execute()
    assert cmd.Get("Status") == ""
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check Generated Objects
    # All route StmTemplateConfig files are using the same XML template.
    # This template is being applied to all routes in the StmProtocolMix.
    # Thus, all routers in the StmProtocolMix will get three copies
    # of each route type that it can possibly have; one from each
    # route StmTemplateConfig in the route mix.
    gen_obj_list = route_tmpl1.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    plLogger.LogInfo("route StmTemplateConfig: " + route_tmpl1.Get("Name"))
    for obj in gen_obj_list:
        plLogger.LogInfo("obj: " + obj.Get("Name"))
        plLogger.LogInfo("obj parent: " + obj.GetParent().Get("Name"))
    assert len(gen_obj_list) == 7
    gen_obj_list = route_tmpl2.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    plLogger.LogInfo("route StmTemplateConfig: " + route_tmpl2.Get("Name"))
    for obj in gen_obj_list:
        plLogger.LogInfo("obj: " + obj.Get("Name"))
        plLogger.LogInfo("obj parent: " + obj.GetParent().Get("Name"))
    assert len(gen_obj_list) == 7
    gen_obj_list = route_tmpl3.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    plLogger.LogInfo("route StmTemplateConfig: " + route_tmpl3.Get("Name"))
    for obj in gen_obj_list:
        plLogger.LogInfo("obj: " + obj.Get("Name"))
        plLogger.LogInfo("obj parent: " + obj.GetParent().Get("Name"))
    assert len(gen_obj_list) == 7

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    bgpv4_route_tag = None
    bgpv4_route_net_block_tag = None
    bgpv6_route_tag = None
    bgpv6_route_net_block_tag = None
    isis_lsp_tag = None
    isis_route_tag = None
    isis_route_net_block_tag = None

    for tag in tag_list:
        if tag.Get("Name") == "ttBgpIpv4RouteConfig":
            bgpv4_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv4RouteConfig.Ipv4NetworkBlock":
            bgpv4_route_net_block_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig":
            bgpv6_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv6RouteConfig.Ipv6NetworkBlock":
            bgpv6_route_net_block_tag = tag
        elif tag.Get("Name") == "ttIsisLspConfig":
            isis_lsp_tag = tag
        elif tag.Get("Name") == "ttIpv4IsisRoutesConfig":
            isis_route_tag = tag
        elif tag.Get("Name") == "ttIpv4IsisRoutesConfig.Ipv4NetworkBlock":
            isis_route_net_block_tag = tag
    assert bgpv4_route_tag
    assert bgpv4_route_net_block_tag
    assert bgpv6_route_tag
    assert bgpv6_route_net_block_tag
    assert isis_lsp_tag
    assert isis_route_tag
    assert isis_route_net_block_tag

    # Check BGPv4
    for dev in [dev1, dev2, dev3]:
        plLogger.LogInfo("dev: " + str(dev.GetObjectHandle()))
        bgp_proto = dev.GetObject("BgpRouterConfig")
        bgpv4_route_block_list = bgp_proto.GetObjects("BgpIpv4RouteConfig")
        assert len(bgpv4_route_block_list) == 3
        tmpl1_block = 0
        tmpl2_block = 0
        tmpl3_block = 0
        for route_block in bgpv4_route_block_list:
            plLogger.LogInfo("route_block: " + route_block.Get("Name") +
                             "   " + str(route_block.GetObjectHandle()))
            tmpl_obj = route_block.GetObject(
                "StmTemplateConfig",
                RelationType("GeneratedObject", 1))
            assert tmpl_obj
            exp_route_count = 0
            if tmpl_obj.GetObjectHandle() == route_tmpl1.GetObjectHandle():
                tmpl1_block = 1
                exp_route_count = 35
            elif tmpl_obj.GetObjectHandle() == route_tmpl2.GetObjectHandle():
                tmpl2_block = 1
                exp_route_count = 70
            elif tmpl_obj.GetObjectHandle() == route_tmpl3.GetObjectHandle():
                tmpl3_block = 1
                exp_route_count = 350
            act_tag = route_block.GetObject("Tag", RelationType("UserTag"))
            act_tag_hnd = act_tag.GetObjectHandle()
            assert act_tag_hnd == bgpv4_route_tag.GetObjectHandle()

            net_block_list = route_block.GetObjects("NetworkBlock")
            assert len(net_block_list) == 1
            net_block = net_block_list[0]
            assert net_block
            act_tag = net_block.GetObject("Tag", RelationType("UserTag"))
            assert act_tag.GetObjectHandle() == \
                bgpv4_route_net_block_tag.GetObjectHandle()

            # Check expected route count
            # (depends on which template the route block came from)
            plLogger.LogInfo("exp_route_count: " + str(exp_route_count))
            plLogger.LogInfo("net_block: " +
                             str(net_block.GetParent().Get("Name")))
            plLogger.LogInfo("act_count: " +
                             str(net_block.Get("NetworkCount")))
            assert net_block.Get("NetworkCount") == exp_route_count
        assert tmpl1_block
        assert tmpl2_block
        assert tmpl3_block

    # Check BGPv6
    for dev in [dev1, dev2, dev3]:
        plLogger.LogInfo("dev: " + str(dev.GetObjectHandle()))
        bgp_proto = dev.GetObject("BgpRouterConfig")
        bgpv6_route_block_list = bgp_proto.GetObjects("BgpIpv6RouteConfig")
        assert len(bgpv6_route_block_list) == 3
        tmpl1_block = 0
        tmpl2_block = 0
        tmpl3_block = 0
        for route_block in bgpv6_route_block_list:
            tmpl_obj = route_block.GetObject(
                "StmTemplateConfig",
                RelationType("GeneratedObject", 1))
            assert tmpl_obj
            exp_route_count = 0
            if tmpl_obj.GetObjectHandle() == route_tmpl1.GetObjectHandle():
                tmpl1_block = 1
                exp_route_count = 35
            elif tmpl_obj.GetObjectHandle() == route_tmpl2.GetObjectHandle():
                tmpl2_block = 1
                exp_route_count = 70
            elif tmpl_obj.GetObjectHandle() == route_tmpl3.GetObjectHandle():
                tmpl3_block = 1
                exp_route_count = 350
            act_tag = route_block.GetObject("Tag", RelationType("UserTag"))
            act_tag_hnd = act_tag.GetObjectHandle()
            assert act_tag_hnd == bgpv6_route_tag.GetObjectHandle()

            net_block_list = route_block.GetObjects("NetworkBlock")
            assert len(net_block_list) == 1
            net_block = net_block_list[0]
            assert net_block
            act_tag = net_block.GetObject("Tag", RelationType("UserTag"))
            assert act_tag.GetObjectHandle() == \
                bgpv6_route_net_block_tag.GetObjectHandle()

            # Check expected route count
            # (depends on which template the route block came from)
            assert net_block.Get("NetworkCount") == exp_route_count
        assert tmpl1_block
        assert tmpl2_block
        assert tmpl3_block

    # Check ISIS
    for dev in [dev4]:
        plLogger.LogInfo("dev: " + str(dev.GetObjectHandle()))
        isis_proto = dev.GetObject("IsisRouterConfig")
        isis_lsp_list = isis_proto.GetObjects("IsisLspConfig")
        assert len(isis_lsp_list) == 3
        tmpl1_block = 0
        tmpl2_block = 0
        tmpl3_block = 0
        for isis_lsp in isis_lsp_list:
            tmpl_obj = isis_lsp.GetObject(
                "StmTemplateConfig",
                RelationType("GeneratedObject", 1))
            assert tmpl_obj
            exp_route_count = 0
            if tmpl_obj.GetObjectHandle() == route_tmpl1.GetObjectHandle():
                tmpl1_block = 1
                exp_route_count = 70
            elif tmpl_obj.GetObjectHandle() == route_tmpl2.GetObjectHandle():
                tmpl2_block = 1
                exp_route_count = 140
            elif tmpl_obj.GetObjectHandle() == route_tmpl3.GetObjectHandle():
                tmpl3_block = 1
                exp_route_count = 700
            act_tag = isis_lsp.GetObject("Tag", RelationType("UserTag"))
            act_tag_hnd = act_tag.GetObjectHandle()
            assert act_tag_hnd == isis_lsp_tag.GetObjectHandle()

            route_block_list = isis_lsp.GetObjects("Ipv4IsisRoutesConfig")
            assert len(route_block_list) == 1
            route_block = route_block_list[0]
            assert route_block

            net_block_list = route_block.GetObjects("NetworkBlock")
            assert len(net_block_list) == 1
            net_block = net_block_list[0]
            assert net_block
            act_tag = net_block.GetObject("Tag", RelationType("UserTag"))
            assert act_tag.GetObjectHandle() == \
                isis_route_net_block_tag.GetObjectHandle()

            # Check expected route count
            # (depends on which template the route block came from)
            assert net_block.Get("NetworkCount") == exp_route_count
        assert tmpl1_block
        assert tmpl2_block
        assert tmpl3_block


def test_expand_route_mix_on_stm_template_config(stc):
    plLogger = PLLogger.GetLogger(
        "test_expand_route_mix_on_stm_template_config")
    plLogger.LogInfo("start")
    routes_template = get_simple_bgp_routes_xml()

    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    left_port_group_tag = ctor.Create("Tag", tags)
    left_port_group_tag.Set("Name", "Left")
    port1.AddObject(left_port_group_tag, RelationType("UserTag"))
    tags.AddObject(left_port_group_tag, RelationType("UserTag"))

    # Create Tags
    dev_tag = ctor.Create("Tag", tags)
    dev_tag.Set("Name", "ttEmulatedDevice")
    bgp_tag = ctor.Create("Tag", tags)
    bgp_tag.Set("Name", "ttBgpRouterConfig")
    isis_tag = ctor.Create("Tag", tags)
    isis_tag.Set("Name", "ttIsisRouterConfig")
    tags.AddObject(dev_tag, RelationType("UserTag"))
    tags.AddObject(bgp_tag, RelationType("UserTag"))
    tags.AddObject(isis_tag, RelationType("UserTag"))

    # Create StmTemplateConfigs
    proto_tmpl1 = ctor.Create("StmTemplateConfig", project)

    # Create BGP Routers under the first StmTemplateMix
    dev1 = ctor.Create("EmulatedDevice", project)
    dev1.AddObject(port1, RelationType("AffiliationPort"))
    ipv4If1 = ctor.Create("Ipv4If", dev1)
    ethIIIf1 = ctor.Create("EthIIIf", dev1)
    ipv4If1.AddObject(ethIIIf1, RelationType("StackedOnEndpoint"))
    dev1.AddObject(ipv4If1, RelationType("PrimaryIf"))
    dev1.AddObject(ipv4If1, RelationType("TopLevelIf"))
    dev1.AddObject(dev_tag, RelationType("UserTag"))
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    bgp1.AddObject(bgp_tag, RelationType("UserTag"))
    proto_tmpl1.AddObject(dev1, RelationType("GeneratedObject"))

    # Create the route mix
    route_mix = ctor.Create("StmTemplateMix", project)

    # Merge Routes
    # NOTE: This unit test is testing expand, not create.
    # This JSON is created but not used.  All routes in
    # get_routes_xml() that can be merged onto target objects
    # will be.
    comp_dict = {}
    comp_dict["weight"] = "100%"
    comp_dict["baseTemplateFile"] = "AllRouters.xml"

    mix_dict = {}
    mix_dict["routeCount"] = 100
    mix_dict["components"] = [comp_dict]

    route_mix.Set("MixInfo", json.dumps(mix_dict))

    # Create the StmTemplateConfig child that would have been
    # created by the iterator
    route_tmpl = ctor.Create("StmTemplateConfig", route_mix)
    route_tmpl.Set("TemplateXml", routes_template)

    # Call Expand
    cmd = ctor.CreateCommand(RPKG + ".ExpandRouteMixCommand")
    cmd.SetCollection("TargetObjectTagList", ["ttEmulatedDevice"])
    cmd.SetCollection("SrcObjectList", [route_mix.GetObjectHandle()])
    cmd.Set("RouteCount", 1000)
    cmd.Execute()
    assert cmd.Get("Status") == ""
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check GeneratedObjects
    gen_obj_list = route_tmpl.GetObjects(
        "Scriptable", RelationType("GeneratedObject"))
    assert len(gen_obj_list) == 1

    # Check Tags
    tag_list = tags.GetObjects("Tag")
    bgpv4_route_tag = None
    bgpv4_route_net_block_tag = None

    for tag in tag_list:
        if tag.Get("Name") == "ttBgpIpv4RouteConfig":
            bgpv4_route_tag = tag
        elif tag.Get("Name") == "ttBgpIpv4RouteConfig.Ipv4NetworkBlock":
            bgpv4_route_net_block_tag = tag
    assert bgpv4_route_tag
    assert bgpv4_route_net_block_tag

    # Check BGPv4
    bgp_proto = dev1.GetObject("BgpRouterConfig")
    bgpv4_route_block_list = bgp_proto.GetObjects("BgpIpv4RouteConfig")
    assert len(bgpv4_route_block_list) == 1
    bgpv4_route_block = bgpv4_route_block_list[0]
    assert bgpv4_route_block
    act_tag = bgpv4_route_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == bgpv4_route_tag.GetObjectHandle()

    net_block_list = bgpv4_route_block.GetObjects("NetworkBlock")
    assert len(net_block_list) == 1
    bgpv4_net_block = net_block_list[0]
    assert bgpv4_net_block
    act_tag = bgpv4_net_block.GetObject("Tag", RelationType("UserTag"))
    assert act_tag.GetObjectHandle() == \
        bgpv4_route_net_block_tag.GetObjectHandle()

    # Check route counts
    assert bgpv4_net_block.Get("NetworkCount") == 1000


def test_reset(stc):
    res = ExpRouteMixCmd.reset()
    assert res


def get_unit_test_filename(filename):
    template_dir = MethManUtils.get_topology_template_home_dir()
    return os.path.join(template_dir, filename)


def add_unit_test_template(filename, xml_str):
    template_dir = MethManUtils.get_topology_template_home_dir()
    filenamePath = get_unit_test_filename(filename)
    plLogger = PLLogger.GetLogger("add_unit_test_template")
    try:
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        if os.path.isfile(filenamePath):
            remove_unit_test_template(filename)
        with open(filenamePath, "w") as f:
            f.write(xml_str)
    except:
        plLogger.LogError("Failed to add template for the unit test.")
        return False
    return True


def remove_unit_test_template(filename):
    filenamePath = get_unit_test_filename(filename)
    if os.path.isfile(filenamePath):
        os.remove(filenamePath)


def get_simple_bgp_routes_xml():
    return """
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Tags id="1203" serializationBase="true" Name="Tags 1">
      <Relation type="UserTag" target="1204"/>
      <Relation type="UserTag" target="1205"/>
      <Relation type="UserTag" target="1206"/>
      <Relation type="UserTag" target="1207"/>
      <Tag id="1204" Name="ttEmulatedDevice"></Tag>
      <Tag id="1205" Name="ttBgpRouterConfig"></Tag>
      <Tag id="1206" Name="ttBgpIpv4RouteConfig"></Tag>
      <Tag id="1207" Name="ttBgpIpv4RouteConfig.Ipv4NetworkBlock"></Tag>
    </Tags>
    <EmulatedDevice id="4477" serializationBase="true">
      <Relation type="UserTag" target="1204"/>
      <Relation type="TopLevelIf" target="4478"/>
      <Relation type="TopLevelIf" target="4481"/>
      <Relation type="TopLevelIf" target="4482"/>
      <Relation type="PrimaryIf" target="4482"/>
      <Ipv4If id="4478">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv4If>
      <VlanIf id="4479">
        <Relation type="StackedOnEndpoint" target="4480"/>
      </VlanIf>
      <EthIIIf id="4480"></EthIIIf>
      <Ipv6If id="4481">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv6If>
      <Ipv6If id="4482">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv6If>
      <BgpRouterConfig id="4483">
        <Relation type="UserTag" target="1205"/>
        <BgpIpv4RouteConfig id="4491"
         NextHop="55.55.57.1"
         NextHopIncrement="0.0.0.55"
         AsPath="1">
          <Relation type="UserTag" target="1206"/>
          <Ipv4NetworkBlock id="4492"
           StartIpList="192.192.192.1"
           PrefixLength="22"
           NetworkCount="11"
           AddrIncrement="2">
            <Relation type="UserTag" target="1207"/>
          </Ipv4NetworkBlock>
        </BgpIpv4RouteConfig>
      </BgpRouterConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
"""


def get_routes_xml():
    return """
<StcSystem id="1" Name="StcSystem 1">
  <Project id="2" Name="Project 1">
    <Tags id="1203" serializationBase="true" Name="Tags 1">
      <Relation type="UserTag" target="1204"/>
      <Relation type="UserTag" target="1205"/>
      <Relation type="UserTag" target="1206"/>
      <Relation type="UserTag" target="1207"/>
      <Relation type="UserTag" target="1208"/>
      <Relation type="UserTag" target="1209"/>
      <Relation type="UserTag" target="1210"/>
      <Relation type="UserTag" target="1211"/>
      <Relation type="UserTag" target="1212"/>
      <Relation type="UserTag" target="1213"/>
      <Relation type="UserTag" target="1214"/>
      <Relation type="UserTag" target="1215"/>
      <Relation type="UserTag" target="1216"/>
      <Relation type="UserTag" target="1217"/>
      <Relation type="UserTag" target="1218"/>
      <Relation type="UserTag" target="1219"/>
      <Relation type="UserTag" target="1220"/>
      <Relation type="UserTag" target="1221"/>
      <Tag id="1204" Name="ttEmulatedDevice"></Tag>
      <Tag id="1205" Name="ttBgpRouterConfig"></Tag>
      <Tag id="1206" Name="ttBgpIpv4RouteConfig"></Tag>
      <Tag id="1207" Name="ttBgpIpv4RouteConfig.Ipv4NetworkBlock"></Tag>
      <Tag id="1208" Name="ttBgpIpv6RouteConfig"></Tag>
      <Tag id="1209" Name="ttBgpIpv6RouteConfig.Ipv6NetworkBlock"></Tag>
      <Tag id="1210" Name="ttOspfv2RouterConfig"></Tag>
      <Tag id="1211" Name="ttRouterLsa"></Tag>
      <Tag id="1212" Name="ttRouterLsaLink"></Tag>
      <Tag id="1213" Name="ttRouterLsaLink.Ipv4NetworkBlock"></Tag>
      <Tag id="1214" Name="ttSummaryLsaBlock"></Tag>
      <Tag id="1215" Name="ttSummaryLsaBlock.Ipv4NetworkBlock"></Tag>
      <Tag id="1216" Name="ttExternalLsaBlock"></Tag>
      <Tag id="1217" Name="ttExternalLsaBlock.Ipv4NetworkBlock"></Tag>
      <Tag id="1218" Name="ttIsisRouterConfig"></Tag>
      <Tag id="1219" Name="ttIsisLspConfig"></Tag>
      <Tag id="1220" Name="ttIpv4IsisRoutesConfig"></Tag>
      <Tag id="1221" Name="ttIpv4IsisRoutesConfig.Ipv4NetworkBlock"></Tag>
    </Tags>
    <EmulatedDevice id="4477" serializationBase="true">
      <Relation type="UserTag" target="1204"/>
      <Relation type="TopLevelIf" target="4478"/>
      <Relation type="TopLevelIf" target="4481"/>
      <Relation type="TopLevelIf" target="4482"/>
      <Relation type="PrimaryIf" target="4482"/>
      <Ipv4If id="4478">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv4If>
      <VlanIf id="4479">
        <Relation type="StackedOnEndpoint" target="4480"/>
      </VlanIf>
      <EthIIIf id="4480"></EthIIIf>
      <Ipv6If id="4481">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv6If>
      <Ipv6If id="4482">
        <Relation type="StackedOnEndpoint" target="4519"/>
      </Ipv6If>
      <BgpRouterConfig id="4483">
        <Relation type="UserTag" target="1205"/>
        <BgpIpv4RouteConfig id="4491"
         NextHop="null"
         NextHopIncrement="0.0.0.1"
         AsPath="1">
          <Relation type="UserTag" target="1206"/>
          <Ipv4NetworkBlock id="4492"
           StartIpList="192.0.1.0"
           PrefixLength="24"
           NetworkCount="1"
           AddrIncrement="1">
            <Relation type="UserTag" target="1207"/>
          </Ipv4NetworkBlock>
        </BgpIpv4RouteConfig>
        <BgpIpv6RouteConfig id="29119">
         NextHop="null">
          <Relation type="UserTag" target="1208"/>
          <Ipv6NetworkBlock id="29120"
           StartIpList="2000::1"
           PrefixLength="64"
           NetworkCount="1"
           AddrIncrement="1">
            <Relation type="UserTag" target="1209"/>
          </Ipv6NetworkBlock>
        </BgpIpv6RouteConfig>
      </BgpRouterConfig>
      <Ospfv2RouterConfig id="4495">
        <Relation type="UserTag" target="1210"/>
        <RouterLsa id="4498"
         LinkStateId="0.0.0.0">
          <Relation type="UserTag" target="1211"/>
          <RouterLsaLink id="4499"
           LinkType="POINT_TO_POINT"
           LinkId="0.0.0.0">
            <Relation type="UserTag" target="1212"/>
            <Ipv4NetworkBlock id="4500"
             StartIpList="192.0.1.0"
             PrefixLength="24"
             NetworkCount="1"
             AddrIncrement="1">
              <Relation type="UserTag" target="1213"/>
            </Ipv4NetworkBlock>
          </RouterLsaLink>
        </RouterLsa>
        <SummaryLsaBlock id="29108">
          <Relation type="UserTag" target="1214"/>
          <Ipv4NetworkBlock id="29109"
           StartIpList="192.0.1.0"
           PrefixLength="24"
           NetworkCount="1"
           AddrIncrement="1">
            <Relation type="UserTag" target="1215"/>
          </Ipv4NetworkBlock>
        </SummaryLsaBlock>
        <ExternalLsaBlock id="29111"
         ForwardingAddr="0.0.0.0">
          <Relation type="UserTag" target="1216"/>
          <Ipv4NetworkBlock id="29112"
           StartIpList="192.0.1.0"
           PrefixLength="24"
           NetworkCount="1"
           AddrIncrement="1">
            <Relation type="UserTag" target="1217"/>
          </Ipv4NetworkBlock>
        </ExternalLsaBlock>
      </Ospfv2RouterConfig>
      <IsisRouterConfig id="3123"
       IpVersion="IPV4">
        <Relation type="UserTag" target="1218"/>
        <IsisLspConfig id="4513">
          <Relation type="UserTag" target="1219"/>
          <Ipv4IsisRoutesConfig id="4514">
            <Relation type="UserTag" target="1220"/>
            <Ipv4NetworkBlock id="4515"
             StartIpList="192.0.1.0"
             PrefixLength="24"
             NetworkCount="1"
             AddrIncrement="1">
              <Relation type="UserTag" target="1221"/>
            </Ipv4NetworkBlock>
          </Ipv4IsisRoutesConfig>
        </IsisLspConfig>
      </IsisRouterConfig>
    </EmulatedDevice>
  </Project>
</StcSystem>
"""


# File in template BGP_Import_Routes.xml
def get_import_xml(filename):
    return """
<Template>
<Description />
<Image />
<DataModelXml>
<StcSystem id="1" serializationBase="true"
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
   ConfigurationFileName=""
   Active="TRUE"
   LocalActive="TRUE"
   Name="Project 1">
    <Tags id="1210"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1216"/>
      <Tag id="1216"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttBgpImportRouteTableParams">
      </Tag>
    </Tags>
    <BgpImportRouteTableParams id="2197"
     RouterType="CISCO_VERSION_ONE"
     FileName="{}"
     AddTesterAsn="TRUE"
     UseTesterIpAsNextHop="TRUE"
     MaxRouteBlks="0"
     MaxRoutesPerBlock="0"
     MaxRoutes="0"
     DisableTraffic="FALSE"
     Active="TRUE"
     LocalActive="TRUE"
     Name="BgpImportRouteTableParams 1">
      <Relation target="1216" type="UserTag" />
    </BgpImportRouteTableParams>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
""".format(filename)


def get_fullroute_txt():
    return """BGP table version is 46111117, local router ID is 180.145.253.6
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale
Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*>i1.0.4.0/22       61.122.240.146         110     70      0 2497 6453 7545 7545 7545 56203 i
*>i1.0.25.0/24      61.122.241.1            50     80      0 2519 i
*>i1.0.26.0/23      61.122.241.1            50     80      0 2519 i
*>i1.0.28.0/22      61.122.241.1            50     80      0 2519 i
*>i1.0.64.0/18      61.122.240.145          30     90      0 7670 18144 i
*>i1.0.128.0/19     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.128.0/18     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.128.0/17     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.160.0/19     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.192.0/19     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.192.0/18     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.0.224.0/19     61.122.240.188         150     70      0 2914 38040 9737 i
*>i1.5.0.0/16       61.122.241.1            40     90      0 4725 i
*>i1.8.1.0/24       61.122.240.188         150     70      0 2914 4641 38345 i
*>i1.8.8.0/24       61.122.240.188         150     70      0 2914 4641 38345 i
*>i1.8.101.0/24     61.122.240.146         110     70      0 2497 3320 7497 38345 i
*>i1.8.102.0/24     61.122.240.188         150     70      0 2914 4641 38345 i
*>i1.8.103.0/24     61.122.240.146         110     70      0 2497 6453 38345 i
*>i1.8.104.0/24     61.122.240.146         110     70      0 2497 6453 38345 i
*>i1.8.150.0/24     61.122.240.188         150     70      0 2914 4641 38345 i
*>i1.8.151.0/24     61.122.240.188         150     70      0 2914 4641 38345 i
*>i1.8.152.0/24     61.122.240.146         110     70      0 2497 6453 38345 i
*>i1.8.153.0/24     61.122.240.146         110     70      0 2497 6453 38345 i
*>i1.9.0.0/16       61.122.240.149         100     80      0 4788 i
*>i1.11.0.0/21      61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.8.0/21      61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.16.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.24.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.32.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.40.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.48.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.56.0/21     61.122.240.146         110     70      0 2497 9318 38091 18313 i
*>i1.11.64.0/21     61.122.240.146         110     70      0 2497 9318 38091 i
*>i1.11.72.0/21     61.122.240.146         110     70      0 2497 9318 38091 i
*>i1.11.80.0/21     61.122.240.146         110     70      0 2497 9318 38091 i
*>i1.11.88.0/21     61.122.240.146         110     70      0 2497 9318 38091 i
*>i1.11.96.0/22     61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.100.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.104.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.108.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.112.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.116.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.120.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.124.0/22    61.122.240.146         110     70      0 2497 9318 38091 38669 i
*>i1.11.128.0/17    61.122.240.146         110     70      0 2497 9318 38091 17839 i
*>i1.12.0.0/14      61.122.240.145         120     70      0 2516 4134 4847 18245 i
*>i1.18.117.0/24    61.122.240.145         120     70      0 2516 3786 9700 i
*>i1.18.118.0/24    61.122.240.146         110     70      0 2497 9318 23600 i
*>i1.18.119.0/24    61.122.240.146         110     70      0 2497 9318 23600 i
*>i1.20.0.0/17      61.122.240.149         100     80      0 7473 38040 9737 56120 i
"""


def get_prefix_dist_xml():
    return """
<Template>
<Description />
<Image />
<DataModelXml>
<StcSystem id="1" serializationBase="true"
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
    <Relation type="DefaultSelection" target="1168"/>
    <Tags id="1208"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Relation type="UserTag" target="1400"/>
      <Relation type="UserTag" target="1401"/>
      <Relation type="UserTag" target="1402"/>
      <Relation type="UserTag" target="1403"/>
      <Tag id="1400"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttBgpRouteGenParams">
      </Tag>
      <Tag id="1401"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttOspfv2LsaGenParams">
      </Tag>
      <Tag id="1402"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttOspfv3LsaGenParams">
      </Tag>
      <Tag id="1403"
       Active="TRUE"
       LocalActive="TRUE"
       Name="ttIsisLspGenParams">
      </Tag>
    </Tags>
    <BgpRouteGenParams id="2142">
      <Relation type="UserTag" target="1400"/>
      <Relation type="BackboneAreaTopologyGenParams" target="2149"/>
      <Ipv4RouteGenParams id="2144"
       PrefixLengthDist="0 0 0 0 0 0 0 0 0 0 0 0 0 50 50 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0"
       Count="4"
       PrefixLengthDistType="CUSTOM">
        <BgpRouteGenRouteAttrParams id="2145"
         PrimaryAsPathSuffix=""
         SecondaryAsPathSuffix=""
         PrimaryAsPathIncrement=""
         SecondaryAsPathIncrement="">
        </BgpRouteGenRouteAttrParams>
      </Ipv4RouteGenParams>
      <Ipv6RouteGenParams id="2146"
       PrefixLengthDist="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0">
        <BgpRouteGenRouteAttrParams id="2147"
         PrimaryAsPathSuffix=""
         SecondaryAsPathSuffix=""
         PrimaryAsPathIncrement=""
         SecondaryAsPathIncrement="">
        </BgpRouteGenRouteAttrParams>
      </Ipv6RouteGenParams>
      <TreeTopologyGenParams id="2148"
       NumSimulatedRouters="6"
       MaxIfPerRouter="3"
       MaxRoutersPerTransitNetwork="3">
      </TreeTopologyGenParams>
      <FullMeshTopologyGenParams id="2149"
       NumRouters="4">
      </FullMeshTopologyGenParams>
    </BgpRouteGenParams>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""
