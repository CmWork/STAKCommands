from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.routing.RoutePrefixDistributionCommand as PrefixCmd


PKG = "spirent.methodology.routing"


def test_validate(stc):
    res = PrefixCmd.validate(None, None, None)
    assert res == "Invalid RouterTagList passed in"

    res = PrefixCmd.validate(["routertag"], None, None)
    assert res == "Invalid SrcObjectTagName passed in"
    return


def test_tag_wizgenerated_as_created(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    # Create Wizard param objects
    bgpParamObj = ctor.Create("BgpRouteGenParams", project)
    ipv4ParamObj = ctor.Create("Ipv4RouteGenParams", bgpParamObj)

    # Create BLL objects
    devObj = ctor.Create("EmulatedDevice", project)
    rtrObj = ctor.Create("BgpRouterConfig", devObj)
    routeObj = ctor.Create("BgpIpv4RouteConfig", rtrObj)

    # Manually set WizardGeneratedObject relation
    ipv4ParamObj.AddObject(routeObj, RelationType("WizardGeneratedObject"))

    # Run the tag function
    PrefixCmd.tag_wizgenerated_as_created(ipv4ParamObj, "testtag")

    # Check that the correct route object was tagged with the correct tag name
    taggObjs = tag_utils.get_tagged_objects_from_string_names("testtag")
    assert len(taggObjs) == 1
    assert routeObj.GetObjectHandle() == taggObjs[0].GetObjectHandle()
    return


def test_run(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    port = ctor.Create("Port", project)
    ethCopper = ctor.Create("EthernetCopper", port)
    port.AddObject(ethCopper, RelationType("ActivePhy"))

    # Create and tag router
    emDevice = ctor.Create("EmulatedDevice", project)
    emDevice.AddObject(port, RelationType("AffiliationPort"))
    ipv4If = ctor.Create("Ipv4If", emDevice)
    ethIf = ctor.Create("EthIIIf", emDevice)
    emDevice.AddObject(ipv4If, RelationType("TopLevelIf"))
    emDevice.AddObject(ipv4If, RelationType("PrimaryIf"))
    ipv4If.AddObject(ethIf, RelationType("StackedOnEndpoint"))
    ctor.Create("BgpRouterConfig", emDevice)
    tag_utils.add_tag_to_object(emDevice, "ttEmulatedDevice")

    # Create and tag wizard object
    bgpParamObj = ctor.Create("BgpRouteGenParams", project)
    tag_utils.add_tag_to_object(bgpParamObj, "ttBgpRouteGenParams")
    ipv4ParamObj = ctor.Create("Ipv4RouteGenParams", bgpParamObj)
    ipv4ParamObj.SetCollection("PrefixLengthDist", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    ipv4ParamObj.Set("Count", 2)
    ipv4ParamObj.Set("PrefixLengthDistType", "CUSTOM")
    ctor.Create("BgpRouteGenRouteAttrParams", ipv4ParamObj)

    # Run the command
    PrefixCmd.run(["ttEmulatedDevice"], "ttBgpRouteGenParams", "ttBgpRoutes")

    routeObjs = tag_utils.get_tagged_objects_from_string_names("ttBgpRoutes")
    assert len(routeObjs) == 2

    for routeObj in routeObjs:
        assert routeObj.IsTypeOf("BgpIpv4RouteConfig")

    return
