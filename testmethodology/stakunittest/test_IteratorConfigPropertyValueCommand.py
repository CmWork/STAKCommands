from StcIntPythonPL import *
import spirent.methodology.IteratorConfigPropertyValueCommand \
    as IterConfPropValCmd


def test_validate():
    obj_list = []
    tag_list = []
    ignore_empty_tags = True
    curr_val = "123"
    iteration = 1
    class_name = "EmulatedDevice"
    prop_name = "DeviceCount"
    assert IterConfPropValCmd.validate(obj_list, tag_list,
                                       ignore_empty_tags,
                                       curr_val, iteration,
                                       class_name,
                                       prop_name) == ""


def test_reset():
    assert IterConfPropValCmd.reset() is True


def test_run_conf_int(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    plLogger = PLLogger.GetLogger("test_run_conf_int")
    plLogger.LogInfo("start")

    pkg = "spirent.methodology"

    # Create tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Dev Group")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Out Group")

    # Create a bunch of devices and tag some of them
    dev1 = ctor.Create("EmulatedDevice", project)
    dev1.AddObject(tag1, RelationType("UserTag"))
    dev2 = ctor.Create("EmulatedDevice", project)
    dev2.AddObject(tag1, RelationType("UserTag"))
    dev3 = ctor.Create("EmulatedDevice", project)
    dev3.AddObject(tag2, RelationType("UserTag"))
    dev4 = ctor.Create("EmulatedDevice", project)
    dev5 = ctor.Create("EmulatedDevice", project)

    # Set the device count
    for dev in [dev1, dev2, dev3, dev4, dev5]:
        dev.Set("DeviceCount", 10)

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigPropertyValue")
    cmd.Set("CurrVal", "100")
    cmd.SetCollection("TagList", ["Dev Group"])
    cmd.SetCollection("ObjectList", [dev4.GetObjectHandle()])
    cmd.Set("IgnoreEmptyTags", True)
    cmd.Set("ClassName", "EmulatedDevice")
    cmd.Set("PropertyName", "DeviceCount")
    cmd.Execute()
    cmd.MarkDelete()

    # Check the configured objects
    for dev in [dev1, dev2, dev4]:
        assert dev.Get("DeviceCount") == 100
    for dev in [dev3, dev5]:
        assert dev.Get("DeviceCount") == 10


def test_run_conf_enum(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    plLogger = PLLogger.GetLogger("test_run_conf_enum")
    plLogger.LogInfo("start")

    pkg = "spirent.methodology"

    # Create tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Active Group")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Out Group")

    # Create a bunch of devices and tag some of them
    dev1 = ctor.Create("EmulatedDevice", project)
    bgp1 = ctor.Create("BgpRouterConfig", dev1)
    bgp1.AddObject(tag1, RelationType("UserTag"))
    dev2 = ctor.Create("EmulatedDevice", project)
    bgp2 = ctor.Create("BgpRouterConfig", dev2)
    bgp2.AddObject(tag1, RelationType("UserTag"))
    dev3 = ctor.Create("EmulatedDevice", project)
    bgp3 = ctor.Create("BgpRouterConfig", dev3)
    bgp3.AddObject(tag2, RelationType("UserTag"))
    dev4 = ctor.Create("EmulatedDevice", project)
    bgp4 = ctor.Create("BgpRouterConfig", dev4)
    dev5 = ctor.Create("EmulatedDevice", project)
    bgp5 = ctor.Create("BgpRouterConfig", dev5)

    # Set the device count
    for bgp in [bgp1, bgp2, bgp3, bgp4, bgp5]:
        bgp.Set("IpVersion", "IPV4")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigPropertyValue")
    cmd.Set("CurrVal", "IPV6")
    cmd.SetCollection("TagList", ["Active Group"])
    cmd.SetCollection("ObjectList", [bgp4.GetObjectHandle()])
    cmd.Set("IgnoreEmptyTags", True)
    cmd.Set("ClassName", "BgpRouterConfig")
    cmd.Set("PropertyName", "IpVersion")
    cmd.Execute()
    cmd.MarkDelete()

    # Check the configured objects
    for bgp in [bgp1, bgp2, bgp4]:
        assert bgp.Get("IpVersion") == "IPV6"
    for bgp in [bgp3, bgp5]:
        assert bgp.Get("IpVersion") == "IPV4"


def test_run_conf_list(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")

    plLogger = PLLogger.GetLogger("test_run_conf_list")
    plLogger.LogInfo("start")

    pkg = "spirent.methodology"

    # Create tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "In Group")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Out Group")

    # Create a bunch of devices and tag some of them
    dev1 = ctor.Create("EmulatedDevice", project)
    ipv4if1 = ctor.Create("Ipv4If", dev1)
    ipv4if1.AddObject(tag1, RelationType("UserTag"))
    dev2 = ctor.Create("EmulatedDevice", project)
    ipv4if2 = ctor.Create("Ipv4If", dev2)
    ipv4if2.AddObject(tag1, RelationType("UserTag"))
    dev3 = ctor.Create("EmulatedDevice", project)
    ipv4if3 = ctor.Create("Ipv4If", dev3)
    ipv4if3.AddObject(tag2, RelationType("UserTag"))
    dev4 = ctor.Create("EmulatedDevice", project)
    ipv4if4 = ctor.Create("Ipv4If", dev4)
    dev5 = ctor.Create("EmulatedDevice", project)
    ipv4if5 = ctor.Create("Ipv4If", dev5)

    default_list = ["1.1.1.1", "1.1.1.2"]
    new_list = ["2.2.2.1", "2.2.2.2"]

    # Set the device count
    for ipv4if in [ipv4if1, ipv4if2, ipv4if3, ipv4if4, ipv4if5]:
        ipv4if.SetCollection("AddrList", default_list)

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigPropertyValue")
    cmd.Set("CurrVal", str(new_list))
    cmd.SetCollection("TagList", ["In Group"])
    cmd.SetCollection("ObjectList", [ipv4if4.GetObjectHandle()])
    cmd.Set("IgnoreEmptyTags", True)
    cmd.Set("ClassName", "Ipv4If")
    cmd.Set("PropertyName", "AddrList")
    cmd.Execute()
    cmd.MarkDelete()

    # Check the configured objects
    for ipv4if in [ipv4if1, ipv4if2, ipv4if4]:
        assert new_list[0] in ipv4if.GetCollection("AddrList")
        assert new_list[1] in ipv4if.GetCollection("AddrList")
    for ipv4if in [ipv4if3, ipv4if5]:
        assert default_list[0] in ipv4if.GetCollection("AddrList")
        assert default_list[1] in ipv4if.GetCollection("AddrList")
