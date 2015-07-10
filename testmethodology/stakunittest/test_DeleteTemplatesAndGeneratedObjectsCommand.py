from StcIntPythonPL import *


def test_run(stc):
    project = CStcSystem.Instance().GetObject("project")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//10.14.16.20/2/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//10.14.16.20/2/2")
    east_dev = ctor.Create("EmulatedDevice", project)
    east_dev.Set("Name", "East Device")
    west_dev = ctor.Create("EmulatedDevice", project)
    west_dev.Set("Name", "West Device")

    east_dev.AddObject(east_port, RelationType("AffiliationPort"))
    west_dev.AddObject(west_port, RelationType("AffiliationPort"))

    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    east_port_group = ctor.Create("Tag", tags)
    east_port_group.Set("Name", "East Port Group")
    west_port_group = ctor.Create("Tag", tags)
    west_port_group.Set("Name", "West Port Group")

    east_port.AddObject(east_port_group, RelationType("UserTag"))
    west_port.AddObject(west_port_group, RelationType("UserTag"))

    template = ctor.Create("StmTemplateConfig", project)
    assert template is not None
    template2 = ctor.Create("StmTemplateConfig", project)
    assert template is not None

    template2.AddObject(west_dev, RelationType("GeneratedObject"))
    template2.AddObject(tags, RelationType("GeneratedObject"))

    # Create traffic objects
    trf_mix = ctor.Create("StmTrafficMix", project)
    template3 = ctor.Create("StmTemplateConfig", trf_mix)
    template4 = ctor.Create("StmTemplateConfig", trf_mix)
    sb1 = ctor.Create("StreamBlock", east_port)
    sb2 = ctor.Create("StreamBlock", west_port)
    template3.AddObject(sb1, RelationType("GeneratedObject"))
    template4.AddObject(sb2, RelationType("GeneratedObject"))

    # Create protocol mix objects
    proto_mix = ctor.Create("StmProtocolMix", project)
    template5 = ctor.Create("StmTemplateConfig", proto_mix)
    template6 = ctor.Create("StmTemplateConfig", proto_mix)
    proto_dev1 = ctor.Create("EmulatedDevice", project)
    proto_dev2 = ctor.Create("EmulatedDevice", project)
    template5.AddObject(proto_dev1, RelationType("GeneratedObject"))
    template6.AddObject(proto_dev2, RelationType("GeneratedObject"))

    cmd = ctor.CreateCommand(pkg + ".DeleteTemplatesAndGeneratedObjects")
    cmd.Set("DeleteStmTemplateConfigs", True)
    cmd.Execute()
    cmd.MarkDelete()

    template_list = project.GetObjects("StmTemplateConfig")
    assert len(template_list) == 0

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 0

    port_list = project.GetObjects("Port")
    assert len(port_list) == 2

    for port in port_list:
        sb_list = port.GetObjects("StreamBlock")
        assert len(sb_list) == 0

    dev_list = project.GetObjects("EmulatedDevice")
    assert len(dev_list) == 1
    assert dev_list[0].Get("Name") == "East Device"

    proto_mix_list = project.GetObjects("StmProtocolMix")
    assert len(proto_mix_list) == 0

    # Check tags
    tags = project.GetObject("Tags")
    assert tags is not None
    tag_list = tags.GetObjects("Tag")
    assert len(tag_list) >= 2
    found_east = False
    found_west = False
    for tag in tag_list:
        if tag.Get("Name") == "East Port Group":
            found_east = True
        elif tag.Get("Name") == "West Port Group":
            found_west = True
    assert found_east is True
    assert found_west is True


def test_run_delete_gen_objs_only(stc):
    project = CStcSystem.Instance().GetObject("project")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    east_port = ctor.Create("Port", project)
    east_port.Set("Location", "//10.14.16.20/2/1")
    west_port = ctor.Create("Port", project)
    west_port.Set("Location", "//10.14.16.20/2/2")
    east_dev = ctor.Create("EmulatedDevice", project)
    east_dev.Set("Name", "East Device")
    west_dev = ctor.Create("EmulatedDevice", project)
    west_dev.Set("Name", "West Device")

    east_dev.AddObject(east_port, RelationType("AffiliationPort"))
    west_dev.AddObject(west_port, RelationType("AffiliationPort"))

    template = ctor.Create("StmTemplateConfig", project)
    assert template is not None
    template2 = ctor.Create("StmTemplateConfig", project)
    assert template is not None

    template2.AddObject(west_dev, RelationType("GeneratedObject"))

    # Create traffic objects
    trf_mix = ctor.Create("StmTrafficMix", project)
    template3 = ctor.Create("StmTemplateConfig", trf_mix)
    template4 = ctor.Create("StmTemplateConfig", trf_mix)
    sb1 = ctor.Create("StreamBlock", east_port)
    sb2 = ctor.Create("StreamBlock", west_port)
    template3.AddObject(sb1, RelationType("GeneratedObject"))
    template4.AddObject(sb2, RelationType("GeneratedObject"))

    # Create protocol mix objects
    proto_mix = ctor.Create("StmProtocolMix", project)
    template5 = ctor.Create("StmTemplateConfig", proto_mix)
    template6 = ctor.Create("StmTemplateConfig", proto_mix)
    proto_dev1 = ctor.Create("EmulatedDevice", project)
    proto_dev2 = ctor.Create("EmulatedDevice", project)
    template5.AddObject(proto_dev1, RelationType("GeneratedObject"))
    template6.AddObject(proto_dev2, RelationType("GeneratedObject"))

    cmd = ctor.CreateCommand(pkg + ".DeleteTemplatesAndGeneratedObjects")
    cmd.Set("DeleteStmTemplateConfigs", False)
    cmd.Execute()
    cmd.MarkDelete()

    template_list = project.GetObjects("StmTemplateConfig")
    assert len(template_list) == 2

    trf_mix_list = project.GetObjects("StmTrafficMix")
    assert len(trf_mix_list) == 1
    trf_temp_list = trf_mix_list[0].GetObjects("StmTemplateConfig")
    assert len(trf_temp_list) == 2

    proto_mix_list = project.GetObjects("StmProtocolMix")
    assert len(proto_mix_list) == 1
    proto_temp_list = proto_mix_list[0].GetObjects("StmTemplateConfig")
    assert len(proto_temp_list) == 2

    port_list = project.GetObjects("Port")
    assert len(port_list) == 2

    for port in port_list:
        sb_list = port.GetObjects("StreamBlock")
        assert len(sb_list) == 0

    dev_list = project.GetObjects("EmulatedDevice")
    assert len(dev_list) == 1
    assert dev_list[0].Get("Name") == "East Device"
