from StcIntPythonPL import *
from mock import MagicMock, patch
import os
import sys
import json
sys.path.append(os.path.join(os.getcwd(), "STAKCommands"))
sys.path.append(os.path.join(os.getcwd(), "STAKCommands",
                             "spirent", "methodology"))
import spirent.methodology.routing.AllocateRouteMixCountCommand as AllocCmd
# import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils


PKG = "spirent.methodology.routing"


def test_run_fail_validate_mix_object(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "UnitTestTag")

    cmd = ctor.Create(PKG + ".AllocateRouteMixCountCommand", sequencer)

    gtc_p = patch(PKG + ".AllocateRouteMixCountCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Function signature
    # run(RouteMixList, RouteMixTagList, RouteCount)

    # No mix objects specified
    ret = AllocCmd.run(None, "", 100)
    assert not ret
    assert "Neither RouteMixList nor RouteMixTagList specified a" \
        in cmd.Get("Status")

    # Invalid tag name (no Tag object)
    ret = AllocCmd.run(None, "InvalidTagName", 100)
    assert not ret
    assert "Neither RouteMixList nor RouteMixTagList specified a" \
        in cmd.Get("Status")

    # Empty tag (valid tag that doesn't tag anything)
    ret = AllocCmd.run(None, "UnitTestTag", 100)
    assert not ret
    assert "Neither RouteMixList nor RouteMixTagList specified a" \
        in cmd.Get("Status")

    gtc_p.stop()


def test_run_fail_validate_json_weights_and_counts(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "UnitTestTag")

    # Create the StmTemplateMix
    mix_obj = ctor.Create("StmTemplateMix", project)

    # Add the StmTemplateConfigs
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj)
    assert tmpl1
    assert tmpl2

    cmd = ctor.Create(PKG + ".AllocateRouteMixCountCommand", sequencer)

    gtc_p = patch(PKG + ".AllocateRouteMixCountCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Function signature
    # run(RouteMixList, RouteMixTagList, RouteCount)

    # Invalid RouteCount
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 0)
    assert not ret
    assert cmd.Get("Status") == "RouteCount must be at least 1."

    # Invalid number of components
    mix_info = {}
    mix_info["routeCuont"] = 1
    mix_info["components"] = []
    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 100)
    assert not ret
    assert "but 0 components in the MixInfo.  These MUST match." \
        in cmd.Get("Status")

    # Invalid MixInfo JSON
    # mix_obj.Set("MixInfo", json.dumps({"invalid_json": "value"}))
    # ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 100)
    # assert not ret
    # assert cmd.Get("Status") == "Something...fill in when known")

    # Build the MixInfo
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "5"

    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "5"

    mix_info = {}
    mix_info["routeCount"] = 100
    mix_info["components"] = [comp_dict1, comp_dict2]

    # Check error when total static count > total route count
    comp_dict1["weight"] = "500"
    comp_dict2["weight"] = "501"
    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1000)
    assert not ret
    assert "Sum total of the static counts (1001) exceeds the total" \
        in cmd.Get("Status")

    # Check error when total percent > 100%
    comp_dict1["weight"] = "50%"
    comp_dict2["weight"] = "51%"
    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1000)
    assert not ret
    assert "Sum total of the weights defined as percentages (101.0%) exceeds" \
        in cmd.Get("Status")

    # Check error when static count uses up all of the RouteCount
    # and there still are components that are defined by percent
    comp_dict1["weight"] = "23"
    comp_dict2["weight"] = "1%"
    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 23)
    assert not ret
    assert "Not enough total RouteCount to distribute routes to all " \
        in cmd.Get("Status")
    assert "The required total static route count will use up all of the " \
        in cmd.Get("Status")

    # Check error when not enough routes for each component using
    # percent-based weighting to receive at least one route
    comp_dict1["weight"] = "50%"
    comp_dict1["weight"] = "50%"
    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1)
    assert not ret
    assert "Not enough total RouteCount to distribute routes to all " \
        in cmd.Get("Status")
    assert "there aren't enough routes left (1) such that each " + \
        "percent-based mix component will get at least one route." \
        in cmd.Get("Status")

    gtc_p.stop()


def test_run_applied_value_percent_only(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "UnitTestTag")

    # Create the StmTemplateMix
    mix_obj = ctor.Create("StmTemplateMix", project)

    # Create the StmTemplateConfigs
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl3 = ctor.Create("StmTemplateConfig", mix_obj)
    assert tmpl1
    assert tmpl2
    assert tmpl3

    cmd = ctor.Create(PKG + ".AllocateRouteMixCountCommand", sequencer)

    gtc_p = patch(PKG + ".AllocateRouteMixCountCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Function signature
    # run(RouteMixList, RouteMixTagList, RouteCount)

    # Build the MixInfo
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "20%"
    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "50%"
    comp_dict3 = {}
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3["weight"] = "30%"

    mix_info = {}
    mix_info["routeCount"] = 1000
    mix_info["components"] = [comp_dict1, comp_dict2, comp_dict3]

    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1000)
    assert ret

    # Check the appliedValue
    mix_info = json.loads(mix_obj.Get("MixInfo"))
    comp_list = mix_info["components"]
    assert len(comp_list) == 3

    assert comp_list[0].get("appliedValue", 0) == 200
    assert comp_list[1].get("appliedValue", 0) == 500
    assert comp_list[2].get("appliedValue", 0) == 300

    gtc_p.stop()


def test_run_applied_value_static_only(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "UnitTestTag")

    # Create the StmTemplateMix
    mix_obj = ctor.Create("StmTemplateMix", project)

    # Create the StmTemplateConfigs
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl3 = ctor.Create("StmTemplateConfig", mix_obj)
    assert tmpl1
    assert tmpl2
    assert tmpl3

    cmd = ctor.Create(PKG + ".AllocateRouteMixCountCommand", sequencer)

    gtc_p = patch(PKG + ".AllocateRouteMixCountCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Function signature
    # run(RouteMixList, RouteMixTagList, RouteCount)

    # Build the MixInfo
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "20"
    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "50"
    comp_dict3 = {}
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3["weight"] = "30"

    mix_info = {}
    mix_info["routeCount"] = 1
    mix_info["components"] = [comp_dict1, comp_dict2, comp_dict3]

    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1000)
    assert ret

    # Check the appliedValue
    mix_info = json.loads(mix_obj.Get("MixInfo"))
    comp_list = mix_info["components"]
    assert len(comp_list) == 3

    assert comp_list[0].get("appliedValue", 0) == 20
    assert comp_list[1].get("appliedValue", 0) == 50
    assert comp_list[2].get("appliedValue", 0) == 30

    gtc_p.stop()


def test_run_applied_value_mixed_percent_and_static(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    plLogger = PLLogger.GetLogger(
        "test_run_applied_value_mixed_percent_and_static")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")

    tags = project.GetObject("Tags")
    assert tags
    tag = ctor.Create("Tag", tags)
    tag.Set("Name", "UnitTestTag")

    # Create the StmTemplateMix
    mix_obj = ctor.Create("StmTemplateMix", project)

    # Create the StmTemplateConfigs
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl3 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl4 = ctor.Create("StmTemplateConfig", mix_obj)
    assert tmpl1
    assert tmpl2
    assert tmpl3
    assert tmpl4

    cmd = ctor.Create(PKG + ".AllocateRouteMixCountCommand", sequencer)

    gtc_p = patch(PKG + ".AllocateRouteMixCountCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Function signature
    # run(RouteMixList, RouteMixTagList, RouteCount)

    # Build the MixInfo
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "20%"
    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "50"
    comp_dict3 = {}
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3["weight"] = "150"
    comp_dict4 = {}
    comp_dict4["baseTemplateFile"] = "AllRouters.xml"
    comp_dict4["weight"] = "30%"

    mix_info = {}
    mix_info["routeCount"] = 1
    mix_info["components"] = [comp_dict1, comp_dict2, comp_dict3, comp_dict4]

    mix_obj.Set("MixInfo", json.dumps(mix_info))
    ret = AllocCmd.run([mix_obj.GetObjectHandle()], "", 1000)
    assert ret

    # Check the appliedValue
    mix_info = json.loads(mix_obj.Get("MixInfo"))
    comp_list = mix_info["components"]
    assert len(comp_list) == 4

    plLogger.LogInfo("comp_list[3]: " + str(comp_list[3]))

    assert comp_list[0].get("appliedValue", 0) == 160
    assert comp_list[1].get("appliedValue", 0) == 50
    assert comp_list[2].get("appliedValue", 0) == 150
    assert comp_list[3].get("appliedValue", 0) == 240

    gtc_p.stop()


def test_get_all_network_blocks(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger("test_get_all_network_blocks")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")

    dev = ctor.Create("EmulatedDevice", project)
    bgp = ctor.Create("BgpRouterConfig", dev)

    # No NetworkBlocks
    net_block_list = []
    AllocCmd.get_all_network_blocks(dev, net_block_list)
    assert len(net_block_list) == 0
    net_block_list = []
    AllocCmd.get_all_network_blocks(project, net_block_list)
    assert len(net_block_list) == 0

    # Add a NetworkBlock (IPv4)
    v4_route_config = ctor.Create("BgpIpv4RouteConfig", bgp)
    net_block_list = []
    AllocCmd.get_all_network_blocks(dev, net_block_list)
    assert len(net_block_list) == 1
    net_block_list = []
    AllocCmd.get_all_network_blocks(v4_route_config, net_block_list)
    assert len(net_block_list) == 1
    net_block_list = []
    bgpv4_net_block = v4_route_config.GetObject("NetworkBlock")
    AllocCmd.get_all_network_blocks(bgpv4_net_block, net_block_list)
    assert len(net_block_list) == 1

    # Add another NetworkBlock (IPv6)
    v6_route_config = ctor.Create("BgpIpv6RouteConfig", bgp)
    net_block_list = []
    AllocCmd.get_all_network_blocks(dev, net_block_list)
    assert len(net_block_list) == 2
    net_block_list = []
    AllocCmd.get_all_network_blocks(bgp, net_block_list)
    assert len(net_block_list) == 2
    net_block_list = []
    AllocCmd.get_all_network_blocks(v6_route_config, net_block_list)
    assert len(net_block_list) == 1

    # Add another router (ISIS)
    dev2 = ctor.Create("EmulatedDevice", project)
    isis = ctor.Create("IsisRouterConfig", dev2)
    lsp = ctor.Create("IsisLspConfig", isis)
    isis_v4_route_config = ctor.Create("Ipv4IsisRoutesConfig", lsp)
    assert isis_v4_route_config
    net_block_list = []
    AllocCmd.get_all_network_blocks(isis, net_block_list)
    assert len(net_block_list) == 1
    net_block_list = []
    AllocCmd.get_all_network_blocks(project, net_block_list)
    assert len(net_block_list) == 3


def test_update_generated_objects_errors(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger("test_update_generated_objects")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")
    template = ctor.Create("StmTemplateConfig", project)
    dev = ctor.Create("EmulatedDevice", project)

    # No ProtocolConfig
    template.AddObject(dev, RelationType("GeneratedObject"))
    res = AllocCmd.update_generated_objects(template, 13)
    assert "Could not find a parent ProtocolConfig for" in res
    template.RemoveObject(dev, RelationType("GeneratedObject"))

    # No NetworkBlocks
    bgp = ctor.Create("BgpRouterConfig", dev)
    bgp_auth_params = bgp.GetObject("BgpAuthenticationParams")
    assert bgp_auth_params
    template.AddObject(bgp_auth_params, RelationType("GeneratedObject"))
    res = AllocCmd.update_generated_objects(template, 13)
    assert res == "Could not find any NetworkBlocks to update route counts on."
    template.RemoveObject(bgp_auth_params, RelationType("GeneratedObject"))

    # Not enough route count
    v4_route_config = ctor.Create("BgpIpv4RouteConfig", bgp)
    v6_route_config = ctor.Create("BgpIpv6RouteConfig", bgp)
    template.AddObject(v4_route_config, RelationType("GeneratedObject"))
    template.AddObject(v6_route_config, RelationType("GeneratedObject"))
    res = AllocCmd.update_generated_objects(template, 1)
    assert "Could not distribute at least one route to each block" \
        in res


def test_update_generated_objects(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger("test_update_generated_objects")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")
    template = ctor.Create("StmTemplateConfig", project)

    # Single NetworkBlock
    dev = ctor.Create("EmulatedDevice", project)
    bgp = ctor.Create("BgpRouterConfig", dev)
    v4_route_config = ctor.Create("BgpIpv4RouteConfig", bgp)
    template.AddObject(v4_route_config, RelationType("GeneratedObject"))
    net_block = v4_route_config.GetObject("NetworkBlock")
    assert net_block
    assert net_block.Get("NetworkCount") == 1
    res = AllocCmd.update_generated_objects(template, 123)
    assert res == ""
    assert net_block.Get("NetworkCount") == 123

    # Multiple NetworkBlocks
    v6_route_config = ctor.Create("BgpIpv6RouteConfig", bgp)
    template.AddObject(v6_route_config, RelationType("GeneratedObject"))
    v6_net_block = v6_route_config.GetObject("NetworkBlock")
    assert v6_net_block
    assert v6_net_block.Get("NetworkCount") == 1
    res = AllocCmd.update_generated_objects(template, 123)
    assert res == ""
    assert net_block.Get("NetworkCount") == 62
    assert v6_net_block.Get("NetworkCount") == 61

    # Duplicate object type
    v6_route_config2 = ctor.Create("BgpIpv6RouteConfig", bgp)
    template.AddObject(v6_route_config2, RelationType("GeneratedObject"))
    v6_net_block2 = v6_route_config2.GetObject("NetworkBlock")
    assert v6_net_block2
    assert v6_net_block2.Get("NetworkCount") == 1
    res = AllocCmd.update_generated_objects(template, 125)
    assert res == ""
    assert net_block.Get("NetworkCount") == 42
    assert v6_net_block.Get("NetworkCount") == 42
    assert v6_net_block2.Get("NetworkCount") == 41

    # Different protocol type (ISIS)
    dev2 = ctor.Create("EmulatedDevice", project)
    isis = ctor.Create("IsisRouterConfig", dev2)
    lsp = ctor.Create("IsisLspConfig", isis)
    isis_v4_route_config = ctor.Create("Ipv4IsisRoutesConfig", lsp)
    template.AddObject(lsp, RelationType("GeneratedObject"))
    isis_v4_net_block = isis_v4_route_config.GetObject("NetworkBlock")
    assert isis_v4_net_block
    assert isis_v4_net_block.Get("NetworkCount") == 1
    res = AllocCmd.update_generated_objects(template, 200)
    assert res == ""
    assert net_block.Get("NetworkCount") == 67
    assert v6_net_block.Get("NetworkCount") == 67
    assert v6_net_block2.Get("NetworkCount") == 66
    assert isis_v4_net_block.Get("NetworkCount") == 200

    # Different protocol types on multiple objects
    bgp2 = ctor.Create("BgpRouterConfig", dev2)
    v6_route_config3 = ctor.Create("BgpIpv6RouteConfig", bgp2)
    v6_net_block3 = v6_route_config3.GetObject("NetworkBlock")
    assert v6_net_block3
    assert v6_net_block3.Get("NetworkCount") == 1
    template.AddObject(v6_route_config3, RelationType("GeneratedObject"))
    res = AllocCmd.update_generated_objects(template, 300)
    assert res == ""
    assert net_block.Get("NetworkCount") == 100
    assert v6_net_block.Get("NetworkCount") == 100
    assert v6_net_block2.Get("NetworkCount") == 100
    assert isis_v4_net_block.Get("NetworkCount") == 150
    assert v6_net_block3.Get("NetworkCount") == 150


def test_multiple_mix_components(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger("test_update_generated_objects")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")

    # Create the StmTemplateMix
    mix_obj = ctor.Create("StmTemplateMix", project)

    # Create the StmTemplateConfigs
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj)
    tmpl3 = ctor.Create("StmTemplateConfig", mix_obj)
    assert tmpl1
    assert tmpl2
    assert tmpl3

    # Build the MixInfo
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "50%"
    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "50"
    comp_dict3 = {}
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3["weight"] = "150"

    mix_info = {}
    mix_info["routeCount"] = 1
    mix_info["components"] = [comp_dict1, comp_dict2, comp_dict3]

    mix_obj.Set("MixInfo", json.dumps(mix_info))

    # Create the generated objects
    dev1 = ctor.Create("EmulatedDevice", project)
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    bgpv4_route_config1 = ctor.Create("BgpIpv4RouteConfig", bgp1)
    net_block1 = bgpv4_route_config1.GetObject("NetworkBlock")
    assert net_block1
    tmpl1.AddObject(bgpv4_route_config1, RelationType("GeneratedObject"))

    dev2 = ctor.Create("EmulatedDevice", project)
    bgp2 = ctor.Create("BgpRouterConfig", dev2)
    bgpv4_route_config2 = ctor.Create("BgpIpv4RouteConfig", bgp2)
    net_block2 = bgpv4_route_config2.GetObject("NetworkBlock")
    assert net_block2
    tmpl2.AddObject(bgpv4_route_config2, RelationType("GeneratedObject"))
    bgpv6_route_config1 = ctor.Create("BgpIpv6RouteConfig", bgp2)
    net_block3 = bgpv6_route_config1.GetObject("NetworkBlock")
    assert net_block3
    tmpl2.AddObject(bgpv6_route_config1, RelationType("GeneratedObject"))

    dev3 = ctor.Create("EmulatedDevice", project)
    bgp3 = ctor.Create("BgpRouterConfig", dev3)
    bgpv6_route_config2 = ctor.Create("BgpIpv6RouteConfig", bgp3)
    net_block4 = bgpv6_route_config2.GetObject("NetworkBlock")
    assert net_block4
    tmpl3.AddObject(bgpv6_route_config2, RelationType("GeneratedObject"))
    isis = ctor.Create("IsisRouterConfig", dev3)
    isis_lsp = ctor.Create("IsisLspConfig", isis)
    isis_v4_route_config = ctor.Create("Ipv4IsisRoutesConfig", isis_lsp)
    net_block5 = isis_v4_route_config.GetObject("NetworkBlock")
    assert net_block5
    tmpl3.AddObject(isis_lsp, RelationType("GeneratedObject"))

    cmd = ctor.CreateCommand(PKG + ".AllocateRouteMixCountCommand")
    cmd.Set("RouteCount", long(1000))
    cmd.SetCollection("RouteMixList", [mix_obj.GetObjectHandle()])

    cmd.Execute()
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check the compnents
    err_str, mix_info = json_utils.load_json(mix_obj.Get("MixInfo"))
    assert err_str == ""
    assert len(mix_info["components"]) == 3
    assert mix_info["components"][0]["appliedValue"] == 400
    assert mix_info["components"][1]["appliedValue"] == 50
    assert mix_info["components"][2]["appliedValue"] == 150

    # Check the allocated route counts
    assert net_block1.Get("NetworkCount") == 400
    assert net_block2.Get("NetworkCount") == 25
    assert net_block3.Get("NetworkCount") == 25
    assert net_block4.Get("NetworkCount") == 75
    assert net_block5.Get("NetworkCount") == 75


def test_multiple_mixes(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    plLogger = PLLogger.GetLogger("test_update_generated_objects")
    plLogger.LogInfo("start")
    project = stc_sys.GetObject("Project")
    tags = project.GetObject("Tags")
    assert tags
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "UnitTestTag1")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "UnitTestTag2")
    tags.AddObject(tag1, RelationType("UserTag"))
    tags.AddObject(tag2, RelationType("UserTag"))

    # Create StmTemplateMixes and StmTemplateConfigs
    mix_obj1 = ctor.Create("StmTemplateMix", project)
    mix_obj1.AddObject(tag1, RelationType("UserTag"))
    tmpl1 = ctor.Create("StmTemplateConfig", mix_obj1)

    mix_obj2 = ctor.Create("StmTemplateMix", project)
    mix_obj2.AddObject(tag2, RelationType("UserTag"))
    tmpl2 = ctor.Create("StmTemplateConfig", mix_obj2)
    tmpl3 = ctor.Create("StmTemplateConfig", mix_obj2)
    assert tmpl1
    assert tmpl2
    assert tmpl3

    # Build the MixInfo for the first mix
    comp_dict1 = {}
    comp_dict1["baseTemplateFile"] = "AllRouters.xml"
    comp_dict1["weight"] = "100%"
    mix_info1 = {}
    mix_info1["routeCount"] = 1
    mix_info1["components"] = [comp_dict1]
    mix_obj1.Set("MixInfo", json.dumps(mix_info1))

    # Build the MixInfo for the second mix
    comp_dict2 = {}
    comp_dict2["baseTemplateFile"] = "AllRouters.xml"
    comp_dict2["weight"] = "50%"
    comp_dict3 = {}
    comp_dict3["baseTemplateFile"] = "AllRouters.xml"
    comp_dict3["weight"] = "500"
    mix_info2 = {}
    mix_info2["routeCount"] = 1
    mix_info2["components"] = [comp_dict2, comp_dict3]
    mix_obj2.Set("MixInfo", json.dumps(mix_info2))

    # Create the generated objects
    dev1 = ctor.Create("EmulatedDevice", project)
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    bgpv4_route_config1 = ctor.Create("BgpIpv4RouteConfig", bgp1)
    net_block1 = bgpv4_route_config1.GetObject("NetworkBlock")
    assert net_block1
    tmpl1.AddObject(bgpv4_route_config1, RelationType("GeneratedObject"))

    dev2 = ctor.Create("EmulatedDevice", project)
    bgp2 = ctor.Create("BgpRouterConfig", dev2)
    bgpv4_route_config2 = ctor.Create("BgpIpv4RouteConfig", bgp2)
    net_block2 = bgpv4_route_config2.GetObject("NetworkBlock")
    assert net_block2
    tmpl2.AddObject(bgpv4_route_config2, RelationType("GeneratedObject"))
    bgpv6_route_config1 = ctor.Create("BgpIpv6RouteConfig", bgp2)
    net_block3 = bgpv6_route_config1.GetObject("NetworkBlock")
    assert net_block3
    tmpl2.AddObject(bgpv6_route_config1, RelationType("GeneratedObject"))

    dev3 = ctor.Create("EmulatedDevice", project)
    bgp3 = ctor.Create("BgpRouterConfig", dev3)
    bgpv6_route_config2 = ctor.Create("BgpIpv6RouteConfig", bgp3)
    net_block4 = bgpv6_route_config2.GetObject("NetworkBlock")
    assert net_block4
    tmpl3.AddObject(bgpv6_route_config2, RelationType("GeneratedObject"))
    isis = ctor.Create("IsisRouterConfig", dev3)
    isis_lsp = ctor.Create("IsisLspConfig", isis)
    isis_v4_route_config = ctor.Create("Ipv4IsisRoutesConfig", isis_lsp)
    net_block5 = isis_v4_route_config.GetObject("NetworkBlock")
    assert net_block5
    tmpl3.AddObject(isis_lsp, RelationType("GeneratedObject"))

    cmd = ctor.CreateCommand(PKG + ".AllocateRouteMixCountCommand")
    cmd.Set("RouteCount", long(1000))
    cmd.SetCollection("RouteMixList", [mix_obj1.GetObjectHandle()])
    cmd.SetCollection("RouteMixTagList", ["UnitTestTag2"])
    cmd.Execute()
    assert cmd.Get("PassFailState") == "PASSED"
    cmd.MarkDelete()

    # Check the mixes and components
    err_str, mix_info = json_utils.load_json(mix_obj1.Get("MixInfo"))
    assert err_str == ""
    assert len(mix_info["components"]) == 1
    assert mix_info["components"][0]["appliedValue"] == 1000

    err_str, mix_info = json_utils.load_json(mix_obj2.Get("MixInfo"))
    assert err_str == ""
    assert len(mix_info["components"]) == 2
    assert mix_info["components"][0]["appliedValue"] == 250
    assert mix_info["components"][1]["appliedValue"] == 500

    # Check the allocated route counts
    assert net_block1.Get("NetworkCount") == 1000
    assert net_block2.Get("NetworkCount") == 125
    assert net_block3.Get("NetworkCount") == 125
    assert net_block4.Get("NetworkCount") == 250
    assert net_block5.Get("NetworkCount") == 250
