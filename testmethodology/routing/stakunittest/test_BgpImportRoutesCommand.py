from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.routing.BgpImportRoutesCommand as ImportCmd


def test_validate(stc):
    res = ImportCmd.validate(None, None, None)
    assert res == "Invalid RouterTagList passed in"

    res = ImportCmd.validate(["routertag"], None, None)
    assert res == "Invalid BgpImportParamsTagName passed in"
    return


def test_twg_as_created(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()
    paramObj = ctor.Create("BgpImportRouteTableParams", project)
    devObj = ctor.Create("EmulatedDevice", project)
    rtrObj = ctor.Create("BgpRouterConfig", devObj)
    routeObj = ctor.Create("BgpIpv4RouteConfig", rtrObj)
    paramObj.AddObject(routeObj, RelationType("WizardGenerated"))

    ImportCmd.tag_wizgenerated_as_created(paramObj, "testtag")

    taggObjs = tag_utils.get_tagged_objects_from_string_names("testtag")
    assert len(taggObjs) == 1
    assert routeObj.GetObjectHandle() == taggObjs[0].GetObjectHandle()
    return


def test_twg_as_generated(stc):
    # TODO when BgpImportRouteTableParams's "GeneratedObject" is working, do:
    # ImportCmd.tag_wizgenerated_as_created()
    return
