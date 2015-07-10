from StcIntPythonPL import *
from mock import MagicMock
import json
import spirent.methodology.utils.xml_config_utils as xml_utils
import spirent.methodology.ExpandProtocolMixCommand2 as ExpProtoMixCmd


PKG = "spirent.methodology"


def test_expand_run_validate(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_ExpandProtocolMixCommand2.test_expand_run_validate")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    ExpProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Test no StmTemplateMix
    res = ExpProtoMixCmd.run(0, "", 100)
    assert res is False

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)

    # Test empty MixInfo
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 100)
    assert res is False

    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 40.0
    n_ti_dict["devicesPerBlock"] = 10
    n_ti_dict["portGroupTag"] = "North Port Group"
    # n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 60.0
    s_ti_dict["staticDeviceCount"] = 10
    s_ti_dict["useStaticDeviceCount"] = False
    s_ti_dict["useBlock"] = False
    s_ti_dict["portGroupTag"] = "South Port Group"
    # s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Test mismatched TemplateInfo against StmTemplateConfigs
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 100)
    assert res is False

    # Create a child StmTemplateConfigs
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Test not enough devices to distribute
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 1)
    assert res is False


def test_expand_proto_mix(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_CreateProtocolMixCommand2.test_expand_proto_mix")
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 40.0
    n_ti_dict["useBlock"] = False
    n_ti_dict["staticDeviceCount"] = 0
    n_ti_dict["useStaticDeviceCount"] = False
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 60.0
    s_ti_dict["staticDeviceCount"] = 0
    s_ti_dict["useStaticDeviceCount"] = False
    s_ti_dict["useBlock"] = True
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    cmd.Set("StmTemplateMix", proto_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the expanded protocol mix
    dev_list = north_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 4
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = south_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 6

    # Check the MixInfo
    mi_str = proto_mix.Get("MixInfo")
    plLogger.LogInfo("traffic mix info: " + mi_str)
    mi_dict = json.loads(mi_str)
    assert mi_dict["deviceCount"] == 10
    found_north = False
    found_south = False
    for ti_dict in mi_dict["templateInfo"]:
        if ti_dict["portGroupTag"] == "North Port Group":
            assert ti_dict["deviceCount"] == 4
            found_north = True
        elif ti_dict["portGroupTag"] == "South Port Group":
            assert ti_dict["deviceCount"] == 6
            found_south = True
    assert found_north
    assert found_south


def test_expand_proto_mix_use_block(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_CreateProtocolMixCommand2.test_expand_proto_mix_use_block")
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)
    east_test_xml = xml_utils.add_prefix_to_tags("East_", test_xml)
    west_test_xml = xml_utils.add_prefix_to_tags("West_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
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

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    east_port_group_tag = ctor.Create("Tag", tags)
    east_port_group_tag.Set("Name", "East Port Group")
    west_port_group_tag = ctor.Create("Tag", tags)
    west_port_group_tag.Set("Name", "West Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    port3.AddObject(east_port_group_tag, RelationType("UserTag"))
    port4.AddObject(west_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(east_port_group_tag, RelationType("UserTag"))
    tags.AddObject(west_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 50.0
    n_ti_dict["staticDeviceCount"] = 0
    n_ti_dict["useStaticDeviceCount"] = False
    n_ti_dict["useBlock"] = True
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 25.0
    s_ti_dict["staticDeviceCount"] = 0
    s_ti_dict["useStaticDeviceCount"] = False
    s_ti_dict["useBlock"] = True
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    e_ti_dict = {}
    e_ti_dict["weight"] = 15.0
    e_ti_dict["staticDeviceCount"] = 0
    e_ti_dict["useStaticDeviceCount"] = False
    e_ti_dict["useBlock"] = True
    e_ti_dict["portGroupTag"] = "East Port Group"
    e_ti_dict["deviceTag"] = "East_ttEmulatedClient"
    w_ti_dict = {}
    w_ti_dict["weight"] = 10.0
    w_ti_dict["staticDeviceCount"] = 0
    w_ti_dict["useStaticDeviceCount"] = False
    w_ti_dict["useBlock"] = True
    w_ti_dict["portGroupTag"] = "West Port Group"
    w_ti_dict["deviceTag"] = "West_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict, e_ti_dict, w_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Create a child StmTemplateConfig for East
    east_template = ctor.Create("StmTemplateConfig", proto_mix)
    east_template.Set("TemplateXml", east_test_xml)

    # Create a child StmTemplateConfig for West
    west_template = ctor.Create("StmTemplateConfig", proto_mix)
    west_template.Set("TemplateXml", west_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    cmd.Set("StmTemplateMix", proto_mix.GetObjectHandle())
    cmd.Set("DeviceCount", 20)
    cmd.Execute()
    cmd.MarkDelete()

    # Check the expanded protocol mix
    dev_list = north_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 10
    dev_list = south_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 5
    dev_list = east_template.GetObjects("EmulatedDevice",
                                        RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 3
    dev_list = west_template.GetObjects("EmulatedDevice",
                                        RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 2

    # Check the MixInfo
    mi_str = proto_mix.Get("MixInfo")
    plLogger.LogInfo("traffic mix info: " + mi_str)
    mi_dict = json.loads(mi_str)
    assert mi_dict["deviceCount"] == 20
    found_north = False
    found_south = False
    found_east = False
    found_west = False
    for ti_dict in mi_dict["templateInfo"]:
        if ti_dict["portGroupTag"] == "North Port Group":
            assert ti_dict["deviceCount"] == 10
            found_north = True
        elif ti_dict["portGroupTag"] == "South Port Group":
            assert ti_dict["deviceCount"] == 5
            found_south = True
        elif ti_dict["portGroupTag"] == "East Port Group":
            assert ti_dict["deviceCount"] == 3
            found_east = True
        elif ti_dict["portGroupTag"] == "West Port Group":
            assert ti_dict["deviceCount"] == 2
            found_west = True
    assert found_north
    assert found_south
    assert found_east
    assert found_west


def test_expand_proto_mix_do_not_use_block(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_CreateProtocolMixCommand2.test_expand_proto_mix_do_not_use_block")
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)
    east_test_xml = xml_utils.add_prefix_to_tags("East_", test_xml)
    west_test_xml = xml_utils.add_prefix_to_tags("West_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
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

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    east_port_group_tag = ctor.Create("Tag", tags)
    east_port_group_tag.Set("Name", "East Port Group")
    west_port_group_tag = ctor.Create("Tag", tags)
    west_port_group_tag.Set("Name", "West Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    port3.AddObject(east_port_group_tag, RelationType("UserTag"))
    port4.AddObject(west_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(east_port_group_tag, RelationType("UserTag"))
    tags.AddObject(west_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 50.0
    n_ti_dict["staticDeviceCount"] = 0
    n_ti_dict["useStaticDeviceCount"] = False
    n_ti_dict["useBlock"] = False
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 25.0
    s_ti_dict["staticDeviceCount"] = 0
    s_ti_dict["useStaticDeviceCount"] = False
    s_ti_dict["useBlock"] = False
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    e_ti_dict = {}
    e_ti_dict["weight"] = 15.0
    e_ti_dict["staticDeviceCount"] = 0
    e_ti_dict["useStaticDeviceCount"] = False
    e_ti_dict["useBlock"] = False
    e_ti_dict["portGroupTag"] = "East Port Group"
    e_ti_dict["deviceTag"] = "East_ttEmulatedClient"
    w_ti_dict = {}
    w_ti_dict["weight"] = 10.0
    w_ti_dict["staticDeviceCount"] = 0
    w_ti_dict["useStaticDeviceCount"] = False
    w_ti_dict["useBlock"] = False
    w_ti_dict["portGroupTag"] = "West Port Group"
    w_ti_dict["deviceTag"] = "West_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict, e_ti_dict, w_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Create a child StmTemplateConfig for East
    east_template = ctor.Create("StmTemplateConfig", proto_mix)
    east_template.Set("TemplateXml", east_test_xml)

    # Create a child StmTemplateConfig for West
    west_template = ctor.Create("StmTemplateConfig", proto_mix)
    west_template.Set("TemplateXml", west_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    cmd.Set("StmTemplateMix", proto_mix.GetObjectHandle())
    cmd.Set("DeviceCount", 20)
    cmd.Execute()
    cmd.MarkDelete()

    # Check the expanded protocol mix
    dev_list = north_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 10
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = south_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 5
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = east_template.GetObjects("EmulatedDevice",
                                        RelationType("GeneratedObject"))
    assert len(dev_list) == 3
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = west_template.GetObjects("EmulatedDevice",
                                        RelationType("GeneratedObject"))
    assert len(dev_list) == 2
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1

    # Check the MixInfo
    mi_str = proto_mix.Get("MixInfo")
    plLogger.LogInfo("Protocol mix info: " + mi_str)
    mi_dict = json.loads(mi_str)
    assert mi_dict["deviceCount"] == 20
    found_north = False
    found_south = False
    found_east = False
    found_west = False
    for ti_dict in mi_dict["templateInfo"]:
        if ti_dict["portGroupTag"] == "North Port Group":
            assert ti_dict["deviceCount"] == 10
            found_north = True
        elif ti_dict["portGroupTag"] == "South Port Group":
            assert ti_dict["deviceCount"] == 5
            found_south = True
        elif ti_dict["portGroupTag"] == "East Port Group":
            assert ti_dict["deviceCount"] == 3
            found_east = True
        elif ti_dict["portGroupTag"] == "West Port Group":
            assert ti_dict["deviceCount"] == 2
            found_west = True
    assert found_north
    assert found_south
    assert found_east
    assert found_west


def test_expand_proto_mix_all_static_devices(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_CreateProtocolMixCommand2.test_expand_proto_mix_all_static_devices")
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 40.0
    n_ti_dict["staticDeviceCount"] = 3
    n_ti_dict["useStaticDeviceCount"] = True
    n_ti_dict["useBlock"] = False
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 60.0
    s_ti_dict["staticDeviceCount"] = 2
    s_ti_dict["useStaticDeviceCount"] = True
    s_ti_dict["useBlock"] = True
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    cmd.Set("StmTemplateMix", proto_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the expanded protocol mix
    dev_list = north_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 3
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = south_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 1
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 2

    # Check the MixInfo
    mi_str = proto_mix.Get("MixInfo")
    plLogger.LogInfo("traffic mix info: " + mi_str)
    mi_dict = json.loads(mi_str)
    assert mi_dict["deviceCount"] == 5
    found_north = False
    found_south = False
    for ti_dict in mi_dict["templateInfo"]:
        if ti_dict["portGroupTag"] == "North Port Group":
            assert ti_dict["deviceCount"] == 3
            found_north = True
        elif ti_dict["portGroupTag"] == "South Port Group":
            assert ti_dict["deviceCount"] == 2
            found_south = True
    assert found_north
    assert found_south


def test_expand_proto_mix_some_static_devices(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_CreateProtocolMixCommand2.test_expand_proto_mix_some_static_devices")
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 50.0
    n_ti_dict["staticDeviceCount"] = 3
    n_ti_dict["useStaticDeviceCount"] = False
    n_ti_dict["useBlock"] = False
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 50.0
    s_ti_dict["staticDeviceCount"] = 2
    s_ti_dict["useStaticDeviceCount"] = True
    s_ti_dict["useBlock"] = False
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand2")
    cmd.Set("StmTemplateMix", proto_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    # Check the expanded protocol mix
    dev_list = north_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 4
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1
    dev_list = south_template.GetObjects("EmulatedDevice",
                                         RelationType("GeneratedObject"))
    assert len(dev_list) == 2
    for dev in dev_list:
        assert dev.Get("DeviceCount") == 1

    # Check the MixInfo
    mi_str = proto_mix.Get("MixInfo")
    plLogger.LogInfo("traffic mix info: " + mi_str)
    mi_dict = json.loads(mi_str)
    assert mi_dict["deviceCount"] == 8
    found_north = False
    found_south = False
    for ti_dict in mi_dict["templateInfo"]:
        if ti_dict["portGroupTag"] == "North Port Group":
            assert ti_dict["deviceCount"] == 4
            found_north = True
        elif ti_dict["portGroupTag"] == "South Port Group":
            assert ti_dict["deviceCount"] == 2
            found_south = True
    assert found_north
    assert found_south


def test_expand_proto_mix_invalid_device_count(stc):
    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    ctor = CScriptableCreator()

    plLogger = PLLogger.GetLogger("test_expand_proto_mix")
    plLogger.LogDebug("start")

    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    port2 = ctor.Create("Port", project)
    port2.Set("Location", "//10.14.16.27/2/2")

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    north_port_group_tag = ctor.Create("Tag", tags)
    north_port_group_tag.Set("Name", "North Port Group")
    south_port_group_tag = ctor.Create("Tag", tags)
    south_port_group_tag.Set("Name", "South Port Group")
    port1.AddObject(north_port_group_tag, RelationType("UserTag"))
    port2.AddObject(south_port_group_tag, RelationType("UserTag"))
    tags.AddObject(north_port_group_tag, RelationType("UserTag"))
    tags.AddObject(south_port_group_tag, RelationType("UserTag"))

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = 50.0
    n_ti_dict["staticDeviceCount"] = 30
    n_ti_dict["useStaticDeviceCount"] = True
    n_ti_dict["useBlock"] = False
    n_ti_dict["portGroupTag"] = "North Port Group"
    n_ti_dict["deviceTag"] = "North_ttEmulatedClient"
    s_ti_dict = {}
    s_ti_dict["weight"] = 50.0
    s_ti_dict["staticDeviceCount"] = 20
    s_ti_dict["useStaticDeviceCount"] = True
    s_ti_dict["useBlock"] = False
    s_ti_dict["portGroupTag"] = "South Port Group"
    s_ti_dict["deviceTag"] = "South_ttEmulatedClient"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Create a child StmTemplateConfig for North
    north_template = ctor.Create("StmTemplateConfig", proto_mix)
    north_template.Set("TemplateXml", north_test_xml)

    # Create a child StmTemplateConfig for South
    south_template = ctor.Create("StmTemplateConfig", proto_mix)
    south_template.Set("TemplateXml", south_test_xml)

    # Call Expand
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 10)
    assert res is False
    assert cmd.GetStatus("")


def get_basic_template():
    return """
<Template>
<Diagram/>
<Description/>
<DataModelXml>
<StcSystem id="1">
  <Project id="2">
    <Tags id="1203" serializationBase="true">
      <Relation type="UserTag" target="1407"/>
      <Relation type="UserTag" target="1409"/>
      <Relation type="UserTag" target="1412"/>
      <Relation type="UserTag" target="1206"/>
      <Relation type="UserTag" target="9213"/>
      <Tag id="1206" Name="ttEmulatedClient"></Tag>
      <Tag id="1407" Name="ttOuterVlan"></Tag>
      <Tag id="1409" Name="ttInnerVlan"></Tag>
      <Tag id="1412" Name="ttTopLevelIf"></Tag>
      <Tag id="9213" Name="ttIpv4If.Address"></Tag>
    </Tags>
    <EmulatedDevice id="2202" serializationBase="true">
      <StmPropertyModifier id="51110" TagName="ttEmulatedClient"
      ModifierInfo="&lt;Modifier ModifierType=&quot;RANGE&quot;
      PropertyName=&quot;RouterId&quot;
      ObjectName=&quot;EmulatedDevice&quot;&gt; &lt;Start&gt;2.2.2.2&lt;/Start&gt;
      &lt;Step&gt;0.0.0.1&lt;/Step&gt; &lt;Repeat&gt;0&lt;/Repeat&gt;
      &lt;Recycle&gt;0&lt;/Recycle&gt; &lt;Relation type=&quot;UserTag&quot;
      target=&quot;3500&quot;/&gt; &lt;/Modifier&gt;">
        <Relation type="UserTag" target="9213" />
      </StmPropertyModifier>
      <Relation type="UserTag" target="1206"/>
      <Relation type="TopLevelIf" target="2203"/>
      <Relation type="PrimaryIf" target="2203"/>
      <Ipv4If id="2203">
        <Relation type="StackedOnEndpoint" target="1405"/>
        <Relation type="UserTag" target="1412"/>
      </Ipv4If>
      <EthIIIf id="2204">
      </EthIIIf>
      <VlanIf id="1404">
        <Relation type="UserTag" target="1407"/>
        <Relation type="StackedOnEndpoint" target="2204"/>
      </VlanIf>
      <VlanIf id="1405">
        <Relation type="UserTag" target="1409"/>
        <Relation type="StackedOnEndpoint" target="1404"/>
      </VlanIf>
    </EmulatedDevice>
  </Project>
</StcSystem>
</DataModelXml>
</Template>
"""
