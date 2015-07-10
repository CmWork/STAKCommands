from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.L2L3LearningCommand as learningCmd
from mock import MagicMock, patch


def test_validate(stc):
    return


def test_validate_handle_types(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")

    handle_list = []
    # Empty handle list is valid (BLL will use project)
    assert learningCmd.validate_handle_types(handle_list, True, False) == ''

    port = ctor.Create("Port", project)
    handle_list = [port.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == ''
    assert learningCmd.validate_handle_types(handle_list, False, True) == ''
    assert learningCmd.validate_handle_types(handle_list, True, True) == ''

    stream = ctor.Create("StreamBlock", project)
    handle_list = [stream.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == ''
    assert learningCmd.validate_handle_types(handle_list, False, True) == ''
    assert learningCmd.validate_handle_types(handle_list, True, True) == ''

    host = ctor.Create("Host", project)
    handle_list = [host.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == \
        "Invalid handle type: host. L2 learning command only " + \
        "allows handles of type Port and StreamBlock"
    assert learningCmd.validate_handle_types(handle_list, False, True) == ''
    assert learningCmd.validate_handle_types(handle_list, True, True) == ''

    router = ctor.Create("Router", project)
    handle_list = [router.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == \
        "Invalid handle type: router. L2 learning command only " + \
        "allows handles of type Port and StreamBlock"
    assert learningCmd.validate_handle_types(handle_list, False, True) == ''
    assert learningCmd.validate_handle_types(handle_list, True, True) == ''

    emulated_device = ctor.Create("EmulatedDevice", project)
    handle_list = [emulated_device.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == \
        "Invalid handle type: emulateddevice. L2 learning command only " + \
        "allows handles of type Port and StreamBlock"
    assert learningCmd.validate_handle_types(handle_list, False, True) == ''
    assert learningCmd.validate_handle_types(handle_list, True, True) == ''

    invalid = ctor.Create("BgpRouterConfig", emulated_device)
    handle_list = [invalid.GetObjectHandle()]
    assert learningCmd.validate_handle_types(handle_list, True, False) == \
        "Invalid handle type: bgprouterconfig. L2 learning command only " + \
        "allows handles of type Port and StreamBlock"
    assert learningCmd.validate_handle_types(handle_list, False, True) == \
        "Invalid handle type: bgprouterconfig. Learning command only allows handles " + \
        "of type Port, StreamBlock, Host, Router, and EmulatedDevice"
    assert learningCmd.validate_handle_types(handle_list, True, True) == \
        "Invalid handle type: bgprouterconfig. Learning command only allows handles " + \
        "of type Port, StreamBlock, Host, Router, and EmulatedDevice"

    return


def test_get_valid_handles(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    rx_port = ctor.Create("Port", project)
    stream_block = ctor.Create("StreamBlock", port)
    stream_block.AddObject(rx_port, RelationType("ExpectedRx"))
    tag_utils.add_tag_to_object(stream_block, "ttStreamBlock")
    em_device = ctor.Create("EmulatedDevice", project)
    em_device.AddObject(port, RelationType("AffiliationPort"))
    tag_utils.add_tag_to_object(em_device, "ttEmulatedDevice")
    proto_mix = ctor.Create("StmProtocolMix", project)
    template_config = ctor.Create("StmTemplateConfig", proto_mix)
    template_config.AddObject(stream_block, RelationType("GeneratedObject"))
    tag_utils.add_tag_to_object(template_config, "ttTemplateConfig")

    bgp_config = ctor.Create("BgpRouterConfig", em_device)
    tag_utils.add_tag_to_object(bgp_config, "ttBgpRouterConfig")

    # Empty handle list
    handle_list = []
    l2_handles, l3_handles = learningCmd.get_valid_handles(handle_list, [])
    assert l2_handles == []
    assert l3_handles == []

    # Port valid for L2 and L3
    handle_list = [port.GetObjectHandle()]
    l2_handles, l3_handles = learningCmd.get_valid_handles(handle_list, [])
    assert l2_handles == handle_list
    assert l3_handles == handle_list

    # EmulatedDevice valid for L3 only
    handle_list = [em_device.GetObjectHandle()]
    l2_handles, l3_handles = learningCmd.get_valid_handles(handle_list, [])
    assert l2_handles == []
    assert l3_handles == handle_list

    # BgpRouterConfig not valid for L2 or L3
    handle_list = [bgp_config.GetObjectHandle()]
    l2_handles, l3_handles = learningCmd.get_valid_handles(handle_list, [])
    assert l2_handles == []
    assert l3_handles == []

    # Valid L2L3 tagged object
    tag_name_list = ['ttStreamBlock']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert l2_handles == [stream_block.GetObjectHandle()]
    assert l3_handles == [stream_block.GetObjectHandle()]

    # Valid L2L3 tagged object and empty tag
    tag_name_list = ['ttStreamBlock', 'ttBlah']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert l2_handles == [stream_block.GetObjectHandle()]
    assert l3_handles == [stream_block.GetObjectHandle()]

    # Valid L3 tagged object
    tag_name_list = ['ttEmulatedDevice']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert l2_handles == []
    assert l3_handles == [em_device.GetObjectHandle()]

    # Valid L3 tagged object and valid L2L3 tagged object
    tag_name_list = ['ttStreamBlock', 'ttEmulatedDevice']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert l2_handles == [stream_block.GetObjectHandle()]
    assert l3_handles == [stream_block.GetObjectHandle(), em_device.GetObjectHandle()]

    # Shouldn't ever happen because of validate_handle_types being called
    # but testing anyway
    tag_name_list = ['ttBgpRouterConfig']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert l2_handles == []
    assert l3_handles == []

    # Valid template config tagged object
    tag_name_list = ['ttTemplateConfig']
    l2_handles, l3_handles = learningCmd.get_valid_handles([], tag_name_list)
    assert len(l2_handles) == 1
    assert l2_handles == [stream_block.GetObjectHandle()]
    assert len(l3_handles) == 1
    assert l3_handles == [stream_block.GetObjectHandle()]

    # Valid protocolmix object
    tag_name_list = ['ttTemplateConfig']
    l2_handles, l3_handles = learningCmd.get_valid_handles([proto_mix.GetObjectHandle()], [])
    assert len(l2_handles) == 1
    assert l2_handles == [stream_block.GetObjectHandle()]
    assert len(l3_handles) == 1
    assert l3_handles == [stream_block.GetObjectHandle()]

    return


def test_run(stc):
    sequencer = CStcSystem.Instance().GetObject("Sequencer")
    ctor = CScriptableCreator()
    cmd = ctor.Create("spirent.methodology.L2L3LearningCommand", sequencer)
    gtc_p = patch("spirent.methodology.L2L3LearningCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    handle_list = [port.GetObjectHandle()]

    rx_port = ctor.Create("Port", project)
    stream_block = ctor.Create("StreamBlock", port)
    stream_block.AddObject(rx_port, RelationType("ExpectedRx"))
    tag_utils.add_tag_to_object(stream_block, "ttStreamBlock")
    em_device = ctor.Create("EmulatedDevice", project)
    em_device.AddObject(port, RelationType("AffiliationPort"))
    tag_utils.add_tag_to_object(em_device, "ttEmulatedDevice")
    invalid = ctor.Create("BgpRouterConfig", em_device)

    # L2Learning
    assert learningCmd.run(handle_list, [], True, False,
                           "TX_RX", True, True, False)

    # L3Learning
    assert learningCmd.run([], ["ttStreamBlock"], False, True,
                           "TX_RX", False, False, False)

    # L2L3Learning
    assert learningCmd.run(handle_list, ["ttStreamBlock"], True, True,
                           "TX_RX", True, True, False)

    # L2Learning with invalid handle type and valid tag
    assert not learningCmd.run([em_device.GetObjectHandle()], ["ttStreamBlock"], True, False,
                               "TX_RX", True, False, False)
    assert "Invalid handle type: emulateddevice. L2 learning command " + \
        "only allows handles of type Port and StreamBlock" in cmd.Get('Status')

    # L2Learning with invalid handle type and valid handle
    assert not learningCmd.run([em_device.GetObjectHandle(), port.GetObjectHandle()],
                               ["ttStreamBlock"], True, False, "TX_RX", True, False, False)
    assert "Invalid handle type: emulateddevice. L2 learning command " + \
        "only allows handles of type Port and StreamBlock" in cmd.Get('Status')

    # L2L3Learning with invalid handle type and valid handle
    assert not learningCmd.run([invalid.GetObjectHandle(), port.GetObjectHandle()],
                               ["ttStreamBlock"], True, True, "TX_RX", True, False, False)
    assert "Invalid handle type: bgprouterconfig. Learning command " + \
        "only allows handles of type Port, StreamBlock, Host, Router, " + \
        "and EmulatedDevice" in cmd.Get('Status')

    # Empty ObjectList and TagNameList
    assert learningCmd.run([], [], True, True,
                           "TX_RX", True, True, False)

    # L2L3Learning with only valid handle for L3
    assert learningCmd.run([em_device.GetObjectHandle()], [], True, True,
                           "TX_RX", True, False, False)

    # L2L3Learning with only valid tag for L3
    assert learningCmd.run([], ["ttEmulatedDevice"], True, True,
                           "TX_RX", True, True, False)

    # L2Learning with only valid tag for L3
    assert learningCmd.run([], ["ttEmulatedDevice"], True, False,
                           "TX_RX", True, True, False)

    gtc_p.stop()
    return


# Validate that if the BLL command fails, the so does the STAK command
def test_command_fail(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    handle_list = [port.GetObjectHandle()]

    cmd = ctor.CreateCommand("spirent.methodology.L2L3LearningCommand")
    gtc_p = patch("spirent.methodology.L2L3LearningCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()

    # Mock the function to return the command that's in a failed state
    l2StartCmd = ctor.CreateCommand("L2LearningStartCommand")
    l2StartCmd.Set('State', 'FAILED')
    l2start_p = patch("spirent.methodology.L2L3LearningCommand.l2_learning_start",
                      new=MagicMock(return_value=l2StartCmd))
    l2start_p.start()

    # Ensure the STAK command fails when the BLL command fails
    assert not learningCmd.run(handle_list, [], True, False,
                               "TX_RX", True, False, False)
    assert "L2LearningStartCommand did not pass" in cmd.Get('Status')
    gtc_p.stop()
    l2start_p.stop()
    return


# Validate that if VerifyArp enabled and the ArpNdVerifyResolvedCommand fails,
# the stak command also fails
def test_command_verify_arp(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    handle_list = [port.GetObjectHandle()]

    cmd = ctor.CreateCommand("spirent.methodology.L2L3LearningCommand")
    gtc_p = patch("spirent.methodology.L2L3LearningCommand.get_this_cmd",
                  new=MagicMock(return_value=cmd))
    gtc_p.start()
    verify_cmd = ctor.CreateCommand("ArpNdVerifyResolvedCommand")
    verify_cmd.Set('PassFailState', 'FAILED')
    verify_cmd.Set('State', 'COMPLETED')
    verify_p = patch("spirent.methodology.L2L3LearningCommand.verify_arp",
                     new=MagicMock(return_value=verify_cmd))
    verify_p.start()

    # VerifyArp is True
    assert not learningCmd.run(handle_list, [], False, True,
                               "TX_RX", True, False, True)
    assert "ArpNdVerifyResolvedCommand did not pass" in cmd.Get("Status")

    # VerifyArp is False
    assert learningCmd.run(handle_list, [], False, True,
                           "TX_RX", True, False, False)
    gtc_p.stop()
    verify_p.stop()
    return


# Validate that the BLL commands params are being set correctly
def test_command_params(stc):
    ctor = CScriptableCreator()
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject("Project")
    port = ctor.Create("Port", project)
    handle_list = [port.GetObjectHandle()]
    rx_port = ctor.Create("Port", project)
    stream_block = ctor.Create("StreamBlock", port)
    stream_block.AddObject(rx_port, RelationType("ExpectedRx"))
    tag_utils.add_tag_to_object(stream_block, "ttStreamBlock")

    # Validate L2LearningStartCommand params
    cmd = learningCmd.l2_learning_start(handle_list, "RX_ONLY")
    assert cmd.GetCollection("HandleList") == handle_list
    assert cmd.Get("L2LearningOption") == "RX_ONLY"
    cmd.MarkDelete()

    # Validate L2LearningStopCommand params
    cmd = learningCmd.l2_learning_stop(handle_list)
    assert cmd.GetCollection("HandleList") == handle_list
    cmd.MarkDelete()

    # Validate ArpNdStartCommand params
    cmd = learningCmd.l3_learning_start(handle_list, False, True)
    assert cmd.GetCollection("HandleList") == handle_list
    assert not cmd.Get("WaitForArpToFinish")
    assert cmd.Get("ForceArp")
    cmd.MarkDelete()

    # Validate ArpNdStopCommand params
    cmd = learningCmd.l3_learning_stop(handle_list)
    assert cmd.GetCollection("HandleList") == handle_list
    cmd.MarkDelete()

    # Validate ArpNdVerifyResolvedCommand params
    cmd = learningCmd.verify_arp(handle_list)
    assert cmd.GetCollection("HandleList") == handle_list
    cmd.MarkDelete()

    return
