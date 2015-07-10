from StcIntPythonPL import *
from mock import MagicMock
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands'))
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent',
                             'methodology'))
import spirent.methodology.IteratorConfigTrafficLoadCommand as command


def test_validate(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    trf_mix = ctor.Create("StmTrafficMix", project)
    val = command.validate([trf_mix.GetObjectHandle()],
                           [], True,
                           "fixed(1000)", 1,
                           "FRAMES_PER_SECOND")
    assert val == ""


def test_validate_during_run(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()
    trf_mix = ctor.Create("StmTrafficMix", project)
    trf_mix.Set('MixInfo',
                '<MixInfo Load="10.0" LoadUnit="PERCENT_LINE_RATE" WeightList="30 70.0" />')
    cmd = ctor.CreateCommand("spirent.methodology.IteratorConfigTrafficLoadCommand")
    command.get_this_cmd = MagicMock(return_value=cmd)

    res = command.run([trf_mix.GetObjectHandle()],
                      [], True,
                      "fixed(1000)", 1,
                      "FRAMES_PER_SECOND")
    assert res is True

    res = command.run([trf_mix.GetObjectHandle()],
                      [], True,
                      "rand(10, 100)", 1,
                      "FRAMES_PER_SECOND")
    assert res is False

    res = command.run([trf_mix.GetObjectHandle()],
                      [], True,
                      "fixed(1000.5)", 1,
                      "FRAMES_PER_SECOND")
    assert res is False

    res = command.run([trf_mix.GetObjectHandle()],
                      [], True,
                      "fixed(10.5)", 1,
                      "PERCENT_LINE_RATE")
    assert res is True


def test_iter_config_load_size(stc):
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject("Project")
    port1 = ctor.Create("Port", project)
    port2 = ctor.Create("Port", project)

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("start")

    pkg = "spirent.methodology"

    # Create tags
    tags = project.GetObject("Tags")
    if tags is None:
        tags = ctor.Create("Tags", project)
    assert tags is not None
    tag1 = ctor.Create("Tag", tags)
    tag1.Set("Name", "Streamblock Group 1")
    tag2 = ctor.Create("Tag", tags)
    tag2.Set("Name", "Streamblock Group 2")

    # Create a bunch of streamblocks and tag them
    streamblock1 = ctor.Create("StreamBlock", port1)
    streamblock2 = ctor.Create("StreamBlock", port2)
    streamblock3 = ctor.Create("StreamBlock", port1)
    streamblock4 = ctor.Create("StreamBlock", port2)
    streamblock1.AddObject(tag1, RelationType("UserTag"))
    streamblock2.AddObject(tag1, RelationType("UserTag"))
    streamblock3.AddObject(tag2, RelationType("UserTag"))
    streamblock4.AddObject(tag2, RelationType("UserTag"))

    # Add the StmTrafficMix and StmTemplateConfig objects
    # and create Streamblocks under them
    tm_obj = ctor.Create("StmTrafficMix", project)
    tm_obj.Set("MixInfo",
               "<MixInfo Load=\"10.0\" " +
               "LoadUnit=\"PERCENT_LINE_RATE\" " +
               "WeightList=\"30 70.0\" />")

    temp_obj1 = ctor.Create("StmTemplateConfig", tm_obj)
    temp_obj2 = ctor.Create("StmTemplateConfig", tm_obj)

    streamblock5 = ctor.Create("StreamBlock", port2)
    streamblock6 = ctor.Create("StreamBlock", port2)
    temp_obj1.AddObject(streamblock5, RelationType("GeneratedObject"))
    temp_obj2.AddObject(streamblock6, RelationType("GeneratedObject"))

    # Tag the StmTrafficMix
    tag3 = ctor.Create("Tag", tags)
    tag3.Set("Name", "Traffic Mix")
    tm_obj.AddObject(tag3, RelationType("UserTag"))

    ###################
    # FIXED load size
    ###################

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigTrafficLoad")
    cmd.Set("CurrVal", str("fixed(1000)"))
    cmd.Set("LoadUnit", "FRAMES_PER_SECOND")
    cmd.SetCollection("TagList", ["Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    # Check Allocation
    rel_name = "AffiliationStreamBlockLoadProfile"
    sb_prof = streamblock5.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 300.0
    assert sb_prof.Get("LoadUnit") == "FRAMES_PER_SECOND"

    sb_prof = streamblock6.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 700.0
    assert sb_prof.Get("LoadUnit") == "FRAMES_PER_SECOND"

    # Reconfigure
    cmd = ctor.CreateCommand(pkg + ".IteratorConfigTrafficLoad")
    cmd.Set("CurrVal", str("fixed(2000)"))
    cmd.SetCollection("TagList", ["Traffic Mix"])
    cmd.Set("LoadUnit", "PERCENT_LINE_RATE")
    cmd.Set("Iteration", 1)
    cmd.Execute()
    cmd.MarkDelete()

    sb_prof = streamblock5.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 600.0
    assert sb_prof.Get("LoadUnit") == "PERCENT_LINE_RATE"

    sb_prof = streamblock6.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 1400.0
    assert sb_prof.Get("LoadUnit") == "PERCENT_LINE_RATE"

    # Reconfigure using integer (implicit fixed type)
    cmd = ctor.CreateCommand(pkg + ".IteratorConfigTrafficLoadCommand")
    cmd.Set("CurrVal", str("1543"))
    cmd.SetCollection("TagList", ["Traffic Mix"])
    cmd.Set("LoadUnit", "FRAMES_PER_SECOND")
    cmd.Set("Iteration", 1)
    cmd.Execute()
    cmd.MarkDelete()

    sb_prof = streamblock5.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 463
    assert sb_prof.Get("LoadUnit") == "FRAMES_PER_SECOND"

    sb_prof = streamblock6.GetObject("StreamBlockLoadProfile",
                                     RelationType(rel_name))
    assert sb_prof is not None
    assert sb_prof.Get("Load") == 1080
    assert sb_prof.Get("LoadUnit") == "FRAMES_PER_SECOND"


def test_reset(stc):
    val = command.reset()
    assert val is True
