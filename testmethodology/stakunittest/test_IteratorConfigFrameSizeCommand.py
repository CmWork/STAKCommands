from StcIntPythonPL import *
from ..IteratorConfigFrameSizeCommand import *


def test_get_frame_len_dist(stc):
    project = CStcSystem.Instance().GetObject("Project")
    ctor = CScriptableCreator()

    # I don't know if we can rely on the default frame length
    # distribution objects so we'll create a bunch of fake ones here
    fld1 = ctor.Create("FrameLengthDistribution", project)
    fld1.Set("Name", "TestFld1")
    fld2 = ctor.Create("FrameLengthDistribution", project)
    fld2.Set("Name", "TestFld2")
    fld3 = ctor.Create("FrameLengthDistribution", project)
    fld3.Set("Name", "TestFld3")

    fld = get_frame_len_dist("TestFld1")
    assert fld.GetObjectHandle() == fld1.GetObjectHandle()
    fld = get_frame_len_dist("TestFld3")
    assert fld.GetObjectHandle() == fld3.GetObjectHandle()
    fld = get_frame_len_dist("TestFld4")
    assert fld is None


def test_iter_config_frame_size(stc):
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
    temp_obj1 = ctor.Create("StmTemplateConfig", tm_obj)
    temp_obj2 = ctor.Create("StmTemplateConfig", tm_obj)

    streamblock5 = ctor.Create("StreamBlock", port2)
    streamblock6 = ctor.Create("StreamBlock", port2)
    streamblock7 = ctor.Create("StreamBlock", port2)
    temp_obj1.AddObject(streamblock5, RelationType("GeneratedObject"))
    temp_obj1.AddObject(streamblock6, RelationType("GeneratedObject"))
    temp_obj2.AddObject(streamblock7, RelationType("GeneratedObject"))

    # Tag the StmTrafficMix
    tag3 = ctor.Create("Tag", tags)
    tag3.Set("Name", "Traffic Mix")
    tm_obj.AddObject(tag3, RelationType("UserTag"))

    ###################
    # FIXED frame size
    ###################

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("fixed(127)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Streamblock Group 2"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 127

    for streamblock in [streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 128

    # Reconfigure (as if from somewhere else)
    streamblock1.Set("FrameLengthMode", "RANDOM")
    streamblock2.Set("FrameLengthMode", "RANDOM")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("fixed(1492)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 1492

    for streamblock in [streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 127

    # Reconfigure using integer value (implicit fixed type)
    streamblock3.Set("FrameLengthMode", "RANDOM")
    streamblock4.Set("FrameLengthMode", "RANDOM")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("1500"))
    cmd.SetCollection("TagList", ["Streamblock Group 2"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 1492

    for streamblock in [streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "FIXED"
        assert streamblock.Get("FixedFrameLength") == 1500

    ###################
    # INCR frame size
    ###################

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("incr(65, 65, 1025)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Streamblock Group 2",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock3, streamblock4,
                        streamblock5, streamblock6,
                        streamblock7]:
        print "streamblock frame length mode: " + \
            str(streamblock.Get("FrameLengthMode"))
        assert streamblock.Get("FrameLengthMode") == "INCR"
        assert streamblock.Get("MinFrameLength") == 65
        assert streamblock.Get("StepFrameLength") == 65
        assert streamblock.Get("MaxFrameLength") == 1025

    # Reconfigure (as if from somewhere else)
    streamblock1.Set("FrameLengthMode", "RANDOM")
    streamblock2.Set("FrameLengthMode", "RANDOM")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("incr(129,129,257)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "INCR"
        assert streamblock.Get("MinFrameLength") == 129
        assert streamblock.Get("StepFrameLength") == 129
        assert streamblock.Get("MaxFrameLength") == 257

    for streamblock in [streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "INCR"
        assert streamblock.Get("MinFrameLength") == 65
        assert streamblock.Get("StepFrameLength") == 65
        assert streamblock.Get("MaxFrameLength") == 1025

    ###################
    # RAND frame size
    ###################

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("rand(513, 2049)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Streamblock Group 2",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock3, streamblock4,
                        streamblock5, streamblock6,
                        streamblock7]:
        print "streamblock frame length mode: " + \
            str(streamblock.Get("FrameLengthMode"))
        assert streamblock.Get("FrameLengthMode") == "RANDOM"
        assert streamblock.Get("MinFrameLength") == 513
        assert streamblock.Get("MaxFrameLength") == 2049

    # Reconfigure (as if from somewhere else)
    streamblock1.Set("FrameLengthMode", "FIXED")
    streamblock2.Set("FrameLengthMode", "FIXED")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("rand(129,257)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)

    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "RANDOM"
        assert streamblock.Get("MinFrameLength") == 129
        assert streamblock.Get("MaxFrameLength") == 257

    for streamblock in [streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "RANDOM"
        assert streamblock.Get("MinFrameLength") == 513
        assert streamblock.Get("MaxFrameLength") == 2049

    ###################
    # IMIX frame size
    ###################

    # I don't know if we can rely on the default frame length distribution
    # objects so we'll create a bunch of fake ones here
    fld1 = ctor.Create("FrameLengthDistribution", project)
    fld1.Set("Name", "TestFld1")
    fld2 = ctor.Create("FrameLengthDistribution", project)
    fld2.Set("Name", "TestFld2")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("imix(TestFld2)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Streamblock Group 2",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)
    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock3, streamblock4,
                        streamblock5, streamblock6,
                        streamblock7]:
        print "streamblock frame length mode: " + \
            str(streamblock.Get("FrameLengthMode"))
        assert streamblock.Get("FrameLengthMode") == "IMIX"
        fld = streamblock.GetObject("FrameLengthDistribution",
                                    RelationType("AffiliationFrameLengthDistribution"))
        assert fld.GetObjectHandle() == fld2.GetObjectHandle()

    # Reconfigure (as if from somewhere else)
    streamblock1.Set("FrameLengthMode", "FIXED")
    streamblock2.Set("FrameLengthMode", "FIXED")

    cmd = ctor.CreateCommand(pkg + ".IteratorConfigFrameSize")
    cmd.Set("CurrVal", str("imix(TestFld1)"))
    cmd.SetCollection("TagList", ["Streamblock Group 1",
                                  "Traffic Mix"])
    cmd.Set("Iteration", 1)
    cmd.Execute()
    cmd.MarkDelete()

    for streamblock in [streamblock1, streamblock2,
                        streamblock5, streamblock6,
                        streamblock7]:
        assert streamblock.Get("FrameLengthMode") == "IMIX"
        fld = streamblock.GetObject("FrameLengthDistribution",
                                    RelationType("AffiliationFrameLengthDistribution"))
        assert fld.GetObjectHandle() == fld1.GetObjectHandle()

    for streamblock in [streamblock3, streamblock4]:
        assert streamblock.Get("FrameLengthMode") == "IMIX"
        fld = streamblock.GetObject("FrameLengthDistribution",
                                    RelationType("AffiliationFrameLengthDistribution"))
        assert fld.GetObjectHandle() == fld2.GetObjectHandle()


def test_reset(stc):
    val = reset()
    assert val is True
