from StcIntPythonPL import *
from mock import MagicMock
import json
import spirent.methodology.utils.xml_config_utils as xml_utils
import spirent.methodology.ExpandProtocolMixCommand as ExpProtoMixCmd


PKG = "spirent.methodology"


def test_devices_per_block(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()

    test_xml = get_basic_template()
    west_test_xml = xml_utils.add_prefix_to_tags("West_", test_xml)

    # Create Port
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    west_port_group_tag = ctor.Create("Tag", tags)
    west_port_group_tag.Set("Name", "West Port Group")
    port1.AddObject(west_port_group_tag, RelationType("UserTag"))
    tags.AddObject(west_port_group_tag, RelationType("UserTag"))

    # Create StmProtocolMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    stm_temp_mix = proto_mix.GetObjectHandle()

    # Copy the MixInfo into StmProtocolMix object...
    mix_info = get_example_mix_info_devices_per_block()
    proto_mix.Set('MixInfo', mix_info)

    # Create a child StmTemplateConfig
    w_temp = ctor.Create("StmTemplateConfig", proto_mix)
    w_temp.Set("TemplateXml", west_test_xml)
    e_temp = ctor.Create("StmTemplateConfig", proto_mix)
    e_temp.Set("TemplateXml", west_test_xml)
    n_temp = ctor.Create("StmTemplateConfig", proto_mix)
    n_temp.Set("TemplateXml", west_test_xml)
    s_temp = ctor.Create("StmTemplateConfig", proto_mix)
    s_temp.Set("TemplateXml", west_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand")
    cmd.Set("StmTemplateMix", stm_temp_mix)
    cmd.Set("TagName", "")
    cmd.Set("DeviceCount", 100)
    cmd.SetCollection("PortGroupTagList", ["West Port Group"])
    cmd.Execute()
    assert cmd.Get("Status") == ''
    assert cmd.Get("PassFailState") == 'PASSED'

    cmd.MarkDelete()

    # Check the expanded protocol mix
    w_dev_list = w_temp.GetObjects("EmulatedDevice", RelationType("GeneratedObject"))
    e_dev_list = e_temp.GetObjects("EmulatedDevice", RelationType("GeneratedObject"))
    n_dev_list = n_temp.GetObjects("EmulatedDevice", RelationType("GeneratedObject"))
    s_dev_list = s_temp.GetObjects("EmulatedDevice", RelationType("GeneratedObject"))

    assert len(w_dev_list) == 1
    assert len(e_dev_list) == 9
    assert len(n_dev_list) == 8
    assert len(s_dev_list) == 1

    # DeviceCount = 100
    # {
    #     "devicesPerBlock": 0,
    #     "weight": 10,
    # }
    # 1 Block of 10
    assert w_dev_list[0].Get("DeviceCount") == 10

    # DeviceCount = 100 - 10
    # {
    #     "devicesPerBlock": 5,
    #     "weight": 50%,
    # }
    # 90 * 50% = 45 --> 9 Blocks of 5
    for e_dev in e_dev_list:
        assert e_dev.Get("DeviceCount") == 5

    # DeviceCount = 100 - 10
    # {
    #     "devicesPerBlock": 5,
    #     "weight": 40%,
    # }
    # 90 * 40% = 36 --> 7 Blocks of 5; 1 Block of 1
    for idx, n_dev in enumerate(n_dev_list):
        if idx == len(n_dev_list)-1:
            assert n_dev.Get("DeviceCount") == 1
        else:
            assert n_dev.Get("DeviceCount") == 5

    # DeviceCount = 100 - 10
    # {
    #     "devicesPerBlock": 10,
    #     "weight": 10%,
    # }
    # 90 * 10% = 9 --> 1 Block of 9
    assert s_dev_list[0].Get("DeviceCount") == 9


def test_expand_run_validate(stc):
    plLogger = PLLogger.GetLogger("methodology")
    plLogger.LogInfo("start.test_ExpandProtocolMixCommand.test_expand_run_validate")
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    test_xml = get_basic_template()
    north_test_xml = xml_utils.add_prefix_to_tags("North_", test_xml)
    south_test_xml = xml_utils.add_prefix_to_tags("South_", test_xml)

    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand")
    ExpProtoMixCmd.get_this_cmd = MagicMock(return_value=cmd)

    # Test no StmTemplateMix
    res = ExpProtoMixCmd.run(0, "", 100, "east_port")
    assert res is False

    # Create the StmTemplateMix
    proto_mix = ctor.Create("StmProtocolMix", project)

    # Test empty MixInfo
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 100, "east_port")
    assert res is False

    mi = {}
    n_ti_dict = {}
    n_ti_dict["weight"] = "40.0"
    n_ti_dict["devicesPerBlock"] = 10
    n_ti_dict["portGroupTag"] = "North Port Group"
    s_ti_dict = {}
    s_ti_dict["weight"] = "60.0"
    n_ti_dict["devicesPerBlock"] = 10
    s_ti_dict["portGroupTag"] = "South Port Group"
    mi["templateInfo"] = [n_ti_dict, s_ti_dict]

    proto_mix.Set("MixInfo", json.dumps(mi))

    # Test mismatched TemplateInfo against StmTemplateConfigs
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 100, "east_port")
    assert res is False

    # Create a child StmTemplateConfigs
    n_temp = ctor.Create("StmTemplateConfig", proto_mix)
    n_temp.Set("TemplateXml", north_test_xml)
    s_temp = ctor.Create("StmTemplateConfig", proto_mix)
    s_temp.Set("TemplateXml", south_test_xml)

    # Test not enough devices to distribute
    res = ExpProtoMixCmd.run(proto_mix.GetObjectHandle(), "", 1, "east_port")
    assert res is False


def test_expand_proto_mix_invalid_device_count(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()

    test_xml = get_basic_template()
    west_test_xml = xml_utils.add_prefix_to_tags("West_", test_xml)

    # Create Port
    port1 = ctor.Create("Port", project)
    port1.Set("Location", "//10.14.16.27/2/1")
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None

    west_port_group_tag = ctor.Create("Tag", tags)
    west_port_group_tag.Set("Name", "West Port Group")
    port1.AddObject(west_port_group_tag, RelationType("UserTag"))
    tags.AddObject(west_port_group_tag, RelationType("UserTag"))

    # Create StmProtocolMix
    proto_mix = ctor.Create("StmProtocolMix", project)
    stm_temp_mix = proto_mix.GetObjectHandle()

    # Copy the MixInfo into StmProtocolMix object...
    mix_info = get_example_mix_info_devices_per_block()
    proto_mix.Set('MixInfo', mix_info)

    # Create a child StmTemplateConfig
    w_temp = ctor.Create("StmTemplateConfig", proto_mix)
    w_temp.Set("TemplateXml", west_test_xml)
    e_temp = ctor.Create("StmTemplateConfig", proto_mix)
    e_temp.Set("TemplateXml", west_test_xml)
    n_temp = ctor.Create("StmTemplateConfig", proto_mix)
    n_temp.Set("TemplateXml", west_test_xml)
    s_temp = ctor.Create("StmTemplateConfig", proto_mix)
    s_temp.Set("TemplateXml", west_test_xml)

    # Call Expand
    cmd = ctor.CreateCommand(PKG + ".ExpandProtocolMixCommand")
    cmd.Set("StmTemplateMix", stm_temp_mix)
    cmd.Set("TagName", "")
    cmd.Set("DeviceCount", 1)
    cmd.SetCollection("PortGroupTagList", ["West Port Group"])
    cmd.Execute()
    assert cmd.Get("Status") != ''
    assert cmd.Get("PassFailState") == 'FAILED'

    cmd.MarkDelete()


def get_example_mix_info_devices_per_block():
    return """
{
    "deviceCount": 100,
    "components": [
        {
            "devicesPerBlock": 0,
            "modifyList": [],
            "weight": "10",
            "baseTemplateFile": "IPv4_NoVlan.xml"
        },
        {
            "devicesPerBlock": 5,
            "modifyList": [],
            "weight": "50%",
            "baseTemplateFile": "IPv4_NoVlan.xml"
        },
        {
            "devicesPerBlock": 5,
            "modifyList": [],
            "weight": "40%",
            "baseTemplateFile": "IPv4_NoVlan.xml"
        },
        {
            "devicesPerBlock": 10,
            "modifyList": [],
            "weight": "10%",
            "baseTemplateFile": "IPv4_NoVlan.xml"
        }
    ]
}
"""


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
