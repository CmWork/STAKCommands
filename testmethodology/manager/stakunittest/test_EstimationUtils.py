from StcIntPythonPL import *
import os
import sys
import xml.etree.ElementTree as ET
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
from manager.utils.estimation_utils import SequencerEstimator, EstimationUtils


def test_loadtemplatecommand_not_present(stc):

    seq_root = ET.fromstring(sequencer_xml)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}

    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    deviceCountEstimate = est_util.estimate_device_count()
    assert deviceCountEstimate['10.14.16.27/2/7'] == 0
    assert deviceCountEstimate['10.14.16.17/2/7'] == 0
    assert deviceCountEstimate['10.14.16.37/2/7'] == 0
    assert deviceCountEstimate['10.14.16.47/2/8'] == 0


def test_multiple_loadtemplatecommands(stc):

    seq_root = ET.fromstring(sequencer_xml_1 + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}

    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    deviceCountEstimate = est_util.estimate_device_count()
    assert deviceCountEstimate['10.14.16.27/2/7'] == 6
    assert deviceCountEstimate['10.14.16.17/2/7'] == 6
    assert deviceCountEstimate['10.14.16.37/2/7'] == 4
    assert deviceCountEstimate['10.14.16.47/2/8'] == 4


def test_devicecount(stc):
    seq_root = ET.fromstring(stak_estimation)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    deviceCountEstimate = est_util.estimate_device_count()

    assert deviceCountEstimate['10.14.16.27/2/7'] == 5
    assert deviceCountEstimate['10.14.16.17/2/7'] == 5
    assert deviceCountEstimate['10.14.16.37/2/7'] == 1
    assert deviceCountEstimate['10.14.16.47/2/8'] == 1


def test_estimate_frame_size(stc):
    seq_root = ET.fromstring(stak_estimation)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    frameSizeEstimate = est_util.estimate_frame_size()

    assert frameSizeEstimate['10.14.16.27/2/7'] == 1024
    assert frameSizeEstimate['10.14.16.17/2/7'] == 1024
    assert frameSizeEstimate['10.14.16.37/2/7'] == 1024
    assert frameSizeEstimate['10.14.16.47/2/8'] == 1024


def test_frame_size_no_traffic_start_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_no_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    frameSizeEstimate = est_util.estimate_frame_size()
    assert frameSizeEstimate['10.14.16.27/2/7'] == 0
    assert frameSizeEstimate['10.14.16.17/2/7'] == 0
    assert frameSizeEstimate['10.14.16.37/2/7'] == 0
    assert frameSizeEstimate['10.14.16.47/2/8'] == 0


def test_no_framesizecfg_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    frameSizeEstimate = est_util.estimate_frame_size()

    assert frameSizeEstimate['10.14.16.27/2/7'] == 0
    assert frameSizeEstimate['10.14.16.17/2/7'] == 0
    assert frameSizeEstimate['10.14.16.37/2/7'] == 0
    assert frameSizeEstimate['10.14.16.47/2/8'] == 0


def test_load_no_traffic_start_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_no_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    trafficLoadEstimate = est_util.estimate_load()

    assert trafficLoadEstimate['10.14.16.27/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.17/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.37/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.47/2/8'] == 0


def test_no_trafficloadcfg_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    trafficLoadEstimate = est_util.estimate_load()

    assert trafficLoadEstimate['10.14.16.27/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.17/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.37/2/7'] == 0
    assert trafficLoadEstimate['10.14.16.47/2/8'] == 0


def test_load_estimate_devicecount(stc):
    seq_root = ET.fromstring(stak_estimation)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    trafficLoadEstimate = est_util.estimate_load()

    assert trafficLoadEstimate['10.14.16.27/2/7'] == 15
    assert trafficLoadEstimate['10.14.16.17/2/7'] == 15
    assert trafficLoadEstimate['10.14.16.37/2/7'] == 15
    assert trafficLoadEstimate['10.14.16.47/2/8'] == 15


def test_load_estimate_perc_line_rate(stc):
    perc_estimate = stak_estimation.replace('FRAMES_PER_SECOND',
                                            'PERCENT_LINE_RATE')
    seq_root = ET.fromstring(perc_estimate)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}
    # Frame size estimates, faked here
    frame_estimate = {
        '10.14.16.27/2/7': 128,
        '10.14.16.17/2/7': 128,
        '10.14.16.37/2/7': 128,
        '10.14.16.47/2/8': 64
    }
    # Physical information
    hw_dict = {
        '10.14.16.27/2/7': {'phy': 'ETHERNET_COPPER', 'speed': 'SPEED_10M'},
        '10.14.16.17/2/7': {'phy': 'ETHERNET_COPPER', 'speed': 'SPEED_100M'},
        '10.14.16.37/2/7': {'phy': 'ETHERNET_COPPER', 'speed': 'SPEED_1G'},
        '10.14.16.47/2/8': {'phy': 'ETHERNET_COPPER', 'speed': 'SPEED_10G'}
    }
    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    trafficLoadEstimate = est_util.estimate_load(frame_estimate, hw_dict)

    # These are at 15% line rate for each port type
    assert trafficLoadEstimate['10.14.16.27/2/7'] == 1267
    assert trafficLoadEstimate['10.14.16.17/2/7'] == 12669
    assert trafficLoadEstimate['10.14.16.37/2/7'] == 126689
    # This one is at 10 gigs, but at 64 byte frames
    assert trafficLoadEstimate['10.14.16.47/2/8'] == 2232143


def test_stream_count_no_traffic_start_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_no_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}

    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    streamCountEstimate = est_util.estimate_stream_count()
    assert streamCountEstimate['10.14.16.27/2/7'] == 0
    assert streamCountEstimate['10.14.16.17/2/7'] == 0
    assert streamCountEstimate['10.14.16.37/2/7'] == 0
    assert streamCountEstimate['10.14.16.47/2/8'] == 0


def test_stream_count_no_streamcountcfg_cmd(stc):
    seq_root = ET.fromstring(sequencer_xml_1 + stak_traffic + stak_end)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}

    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    streamCountEstimate = est_util.estimate_stream_count()

    assert streamCountEstimate['10.14.16.27/2/7'] == 0
    assert streamCountEstimate['10.14.16.17/2/7'] == 0
    assert streamCountEstimate['10.14.16.37/2/7'] == 0
    assert streamCountEstimate['10.14.16.47/2/8'] == 0


def test_stream_count_devicecount(stc):
    seq_root = ET.fromstring(stak_estimation)

    port_tag_location_dict = {'West Port Group': ['10.14.16.27/2/7', '10.14.16.17/2/7'],
                              'East Port Group': ['10.14.16.37/2/7', '10.14.16.47/2/8']}

    est_util = SequencerEstimator(root=seq_root)
    est_util.set_port_dict(port_tag_location_dict)
    streamCountEstimate = est_util.estimate_stream_count()

    assert streamCountEstimate['10.14.16.27/2/7'] == 10
    assert streamCountEstimate['10.14.16.17/2/7'] == 10
    assert streamCountEstimate['10.14.16.37/2/7'] == 10
    assert streamCountEstimate['10.14.16.47/2/8'] == 10


def test_estimation(stc):
    seq_root = ET.fromstring(stak_estimation)
    txml_root = ET.fromstring(txml_estimation)

    estimationUtils = EstimationUtils(seq_root=seq_root, txml_root=txml_root)
    portEstimateDict = estimationUtils.get_estimates()
    # This is a lame check, but provided what is tested above passes, this is
    # the consolidation of everything
    assert portEstimateDict is not None


# Test sequence and TXML files
sequencer_xml = \
    '''<?xml version="1.0" encoding="windows-1252"?>
    <StcSystem id="1" serializationBase="true"
    InSimulationMode="FALSE"
    UseSmbMessaging="FALSE"
    ApplicationName="TestCenter"
    Active="TRUE"
    LocalActive="TRUE"
    Name="StcSystem 1">
    <Sequencer id="8"
    CommandList="4254"
    BreakpointList=""
    DisabledCommandList=""
    CleanupCommand="4228"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Sequencer">
    <Relation type="SequencerFinalizeType" target="4228"/>
    <spirent.methodology.manager.MethodologyGroupCommand id="4254"
    InputJson=""
    CommandName=""
    PackageName="spirent"
    CommandList="4200 4201"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Methodology Manager: Dispatch Input Command 3">
    <spirent.methodology.DeleteProfileAndGeneratedObjectsCommand id="4200"
    DeleteProfiles="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Custom Builder Commands: Delete Profile and associated Generated Objects Command 1">
    <Relation type="SequenceableProperties" target="4255"/>
    </spirent.methodology.DeleteProfileAndGeneratedObjectsCommand>
    <spirent.methodology.TopologyTestGroupCommand id="4201"
    CommandName=""
    PackageName="spirent"
    CommandList="4202 4215"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Test Methodology: Topology Test Group Command 1">
    <Relation type="SequenceableProperties" target="4281"/>
    <spirent.methodology.TrafficForwardingTestGroupCommand id="4215"
    TopologyProfile="0"
    CommandName=""
    PackageName="spirent"
    CommandList="4216"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Test Group Commands: Traffic Forwarding Test 1">
    <Relation type="SequenceableProperties" target="4280"/>
    <spirent.methodology.TrafficProfileIterationGroupCommand id="4216"
    ObjectList=""
    CommandName=""
    PackageName="spirent"
    CommandList="4217"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Traffic Profile Iteration Group Command 4">
    <Relation type="SequenceableProperties" target="4279"/>
    <SequencerWhileCommand id="4217"
    ExpressionCommand="4218"
    Condition="PASSED"
    CommandList="4249 4219 4220 4221 4222 4223 4224 4225 4226"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="While">
    <Relation type="SequenceableProperties" target="4278"/>
    <spirent.methodology.ObjectIteratorCommand id="4218"
    IterMode="STEP"
    StepVal="10"
    ValueType="LIST"
    ValueList="20 25 30 45 50 55 60"
    BreakOnFail="FALSE"
    MinVal="0"
    MaxVal="100"
    PrevIterVerdict="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="FALSE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iterators: Object Iterator Command">
    <Relation type="SequenceableProperties" target="4268"/>
    </spirent.methodology.ObjectIteratorCommand>
    <WaitCommand id="4222"
    WaitTime="10"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Wait 4">
    <Relation type="SequenceableProperties" target="4272"/>
    </WaitCommand>
    <spirent.methodology.NetworkProfileDeviceCountConfigCommand id="4249"
    PercentageList="50 25"
    ObjectList=""
    CurrVal=""
    Iteration="0"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Configurators: Iterator Config Device Counts Command 4">
    <Relation type="SequenceableProperties" target="4277"/>
    </spirent.methodology.NetworkProfileDeviceCountConfigCommand>
    </SequencerWhileCommand>
    </spirent.methodology.TrafficProfileIterationGroupCommand>
    </spirent.methodology.TrafficForwardingTestGroupCommand>
    </spirent.methodology.TopologyTestGroupCommand>
    </spirent.methodology.manager.MethodologyGroupCommand>
    </Sequencer>
    </StcSystem>
    '''

sequencer_xml_1 = \
    '''<?xml version="1.0" encoding="windows-1252"?>
    <StcSystem id="1" serializationBase="true"
    InSimulationMode="FALSE"
    UseSmbMessaging="FALSE"
    ApplicationName="TestCenter"
    Active="TRUE"
    LocalActive="TRUE"
    Name="StcSystem 1">
    <Sequencer id="8"
    CurrentSubCommandName=""
    CommandList="5510 5511 5512 5514 5516 5520 5541"
    BreakpointList=""
    DisabledCommandList=""
    CleanupCommand="5542"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Sequencer">
    <Relation type="SequencerFinalizeType" target="5542"/>
    <spirent.methodology.DeleteTemplatesAndGeneratedObjectsCommand id="5510"
    DeleteStmTemplateConfigs="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Delete Templates and Generated Objects Command 1">
    </spirent.methodology.DeleteTemplatesAndGeneratedObjectsCommand>
    <spirent.methodology.StartOfTestCommand id="5511"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Results: Start Of Test Command 1">
    </spirent.methodology.StartOfTestCommand>
    <spirent.methodology.LoadTemplateCommand id="5512"
    CopiesPerParent="5"
    TargetTagList="{West Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="West_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5513"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 4">
    </spirent.methodology.LoadTemplateCommand>
    <spirent.methodology.LoadTemplateCommand id="5514"
    CopiesPerParent="1"
    TargetTagList="{East Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="East_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5515"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 2">
    </spirent.methodology.LoadTemplateCommand>
    <spirent.methodology.LoadTemplateCommand id="5519"
    CopiesPerParent="3"
    TargetTagList="{East Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="East_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5515"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 2">
    </spirent.methodology.LoadTemplateCommand>
    <spirent.methodology.LoadTemplateCommand id="5524"
    CopiesPerParent="1"
    TargetTagList="{West Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="East_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5515"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 2">
    </spirent.methodology.LoadTemplateCommand>"
    '''

stak_end = \
    '''
    <spirent.methodology.EndOfTestCommand id="5541"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Results: End Of Test Command 1">
    </spirent.methodology.EndOfTestCommand>
    </Sequencer>
    </StcSystem>
    '''

stak_no_traffic = \
    '''
    <spirent.methodology.IterationGroupCommand id="5520"
    ObjectList=""
    CommandName=""
    PackageName="spirent"
    CommandList="5521"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Iteration Group Command 1">
    <SequencerWhileCommand id="5521"
    ExpressionCommand="5522"
    Condition="PASSED"
    CommandList="5527 5528 5540"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="While">
    <spirent.methodology.ObjectIteratorCommand id="5522"
    IterMode="STEP"
    StepVal="10"
    ValueType="LIST"
    ValueList="128 256 1024"
    BreakOnFail="FALSE"
    MinVal="0"
    MaxVal="100"
    PrevIterVerdict="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="FALSE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iterators: Object Iterator Command">
    <PropertyChainingConfig id="5523"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 1">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5524"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 2">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5525"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 9">
    <Relation type="PropertyChain" target="5527"/>
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5526"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 10">
    <Relation type="PropertyChain" target="5527"/>
    </PropertyChainingConfig>
    </spirent.methodology.ObjectIteratorCommand>
    <spirent.methodology.IteratorConfigFrameSizeCommand id="5527"
    TagList="{My Traffic Mix}"
    ObjectList=""
    CurrVal="1024"
    Iteration="3"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Configurators: Iterator Config Frame Size Command 1">
    </spirent.methodology.IteratorConfigFrameSizeCommand>
    <spirent.methodology.IterationGroupCommand id="5528"
    ObjectList=""
    CommandName=""
    PackageName="spirent"
    CommandList="5529"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Iteration Group Command 2">
    <SequencerWhileCommand id="5529"
    ExpressionCommand="5530"
    Condition="PASSED"
    CommandList="5535 5536 5537 5538 5539"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="While">
    <spirent.methodology.ObjectIteratorCommand id="5530"
    IterMode="STEP"
    StepVal="5"
    ValueType="RANGE"
    ValueList=""
    BreakOnFail="FALSE"
    MinVal="5"
    MaxVal="15"
    PrevIterVerdict="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="FALSE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iterators: Object Iterator Command">
    <PropertyChainingConfig id="5531"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 3">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5532"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 4">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5533"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 11">
    <Relation type="PropertyChain" target="5535"/>
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5534"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 12">
    <Relation type="PropertyChain" target="5535"/>
    </PropertyChainingConfig>
    </spirent.methodology.ObjectIteratorCommand>
    <spirent.methodology.IteratorConfigTrafficLoadCommand id="5535"
    LoadUnit="FRAMES_PER_SECOND"
    TagList="{My Traffic Mix}"
    ObjectList=""
    CurrVal="15"
    Iteration="3"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Configurators: Iterator Config Traffic Load Command 4">
    </spirent.methodology.IteratorConfigTrafficLoadCommand>
    <spirent.methodology.CompleteIterationCommand id="5539"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Complete Iteration Command 1">
    </spirent.methodology.CompleteIterationCommand>
    </SequencerWhileCommand>
    </spirent.methodology.IterationGroupCommand>
    <spirent.methodology.CompleteIterationCommand id="5540"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Complete Iteration Command 2">
    </spirent.methodology.CompleteIterationCommand>
    </SequencerWhileCommand>
    </spirent.methodology.IterationGroupCommand>"
    '''

stak_traffic = \
    '''
    <GeneratorStartCommand id="5536"
    GeneratorList="2"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Start Traffic 1">
    </GeneratorStartCommand>
    <WaitCommand id="5537"
    WaitTime="10"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Wait 1">
    </WaitCommand>
    <GeneratorStopCommand id="5538"
    GeneratorList="2"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Stop Traffic 1">
    </GeneratorStopCommand>
    '''

stak_estimation = \
    '''<?xml version="1.0" encoding="windows-1252"?>
    <StcSystem id="1" serializationBase="true"
     InSimulationMode="FALSE"
     UseSmbMessaging="FALSE"
     ApplicationName="TestCenter"
     Active="TRUE"
     LocalActive="TRUE"
     Name="StcSystem 1">
    <ExposedConfig id="2522"
     Active="TRUE"
     LocalActive="TRUE"
     Name="ExposedConfig 1">
      <ExposedProperty id="2523"
       EPNameId="Tag.Name.2039"
       EPPropertyName=""
       EPClassId="tag"
       EPPropertyId="scriptable.name"
       EPDefaultValue=""
       EPLabel=""
       Active="TRUE"
       LocalActive="TRUE"
       Name="ExposedProperty LeftTagName">
        <Relation type="ScriptableExposedProperty" target="2125"/>
      </ExposedProperty>
      <ExposedProperty id="2524"
       EPNameId="Tag.Name.2040"
       EPPropertyName=""
       EPClassId="tag"
       EPPropertyId="scriptable.name"
       EPDefaultValue=""
       EPLabel=""
       Active="TRUE"
       LocalActive="TRUE"
       Name="ExposedProperty RightTagName">
        <Relation type="ScriptableExposedProperty" target="2126"/>
      </ExposedProperty>
    </ExposedConfig>
    <Tags id="1207"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Tags 1">
      <Tag id="2125"
       Active="TRUE"
       LocalActive="TRUE"
       Name="West Port Group">
      </Tag>
      <Tag id="2126"
       Active="TRUE"
       LocalActive="TRUE"
       Name="East Port Group">
      </Tag>
    </Tags>
    <Sequencer id="8"
     CurrentSubCommandName=""
     CommandList="5510 5511 5512 5514 5516 5520 5541"
     BreakpointList=""
     DisabledCommandList=""
     CleanupCommand="5542"
     Active="TRUE"
     LocalActive="TRUE"
     Name="Sequencer">
    <Relation type="SequencerFinalizeType" target="5542"/>
    <spirent.methodology.DeleteTemplatesAndGeneratedObjectsCommand id="5510"
    DeleteStmTemplateConfigs="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Delete Templates and Generated Objects Command 1">
    </spirent.methodology.DeleteTemplatesAndGeneratedObjectsCommand>
    <spirent.methodology.StartOfTestCommand id="5511"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Results: Start Of Test Command 1">
    </spirent.methodology.StartOfTestCommand>
    <spirent.methodology.LoadTemplateCommand id="5512"
    CopiesPerParent="5"
    TargetTagList="{West Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="West_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5513"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 4">
    <spirent.methodology.ModifyTemplatePropertyCommand id="5513"
    StmTemplateConfig="0"
    TagNameList=""
    PropertyValueList=""
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Modify XML Template Command 2">
    </spirent.methodology.ModifyTemplatePropertyCommand>
    </spirent.methodology.LoadTemplateCommand>
    <spirent.methodology.LoadTemplateCommand id="5514"
    CopiesPerParent="1"
    TargetTagList="{East Port Group}"
    TemplateXml=""
    TemplateXmlFileName="IPv4_NoVlan.xml"
    TagPrefix="East_"
    AutoExpandTemplate="TRUE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5515"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Load Template Command 2">
    <spirent.methodology.ModifyTemplatePropertyCommand id="5515"
    StmTemplateConfig="0"
    TagNameList=""
    PropertyValueList=""
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Topology Template: Modify XML Template Command 1">
    </spirent.methodology.ModifyTemplatePropertyCommand>
    </spirent.methodology.LoadTemplateCommand>
    <spirent.methodology.traffic.CreateTrafficMix1Command id="5516"
    Load="1000"
    LoadUnit="FRAMES_PER_SECOND"
    MixTagName="My Traffic Mix"
    AutoExpandTemplateMix="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList="5517 5518 5519"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Traffic: Create Traffic Mix Command 2">
    <spirent.methodology.traffic.LoadTrafficTemplateCommand id="5517"
    TrafficMix="0"
    Weight="40"
    CopiesPerParent="1"
    TargetTagList=""
    TemplateXml=""
    TemplateXmlFileName="Ipv4_Stream.xml"
    TagPrefix="Traffic1_"
    AutoExpandTemplate="FALSE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList=""
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Traffic: Load Traffic Template Command 3">
    </spirent.methodology.traffic.LoadTrafficTemplateCommand>
    <spirent.methodology.traffic.LoadTrafficTemplateCommand id="5518"
    TrafficMix="0"
    Weight="60"
    CopiesPerParent="1"
    TargetTagList=""
    TemplateXml=""
    TemplateXmlFileName="Ipv4_Stream.xml"
    TagPrefix="Traffic2_"
    AutoExpandTemplate="FALSE"
    EnableLoadFromFileName="TRUE"
    CommandName=""
    PackageName="spirent"
    CommandList=""
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Traffic: Load Traffic Template Command 2">
    </spirent.methodology.traffic.LoadTrafficTemplateCommand>
    <spirent.methodology.traffic.SetTrafficEndpointTagsCommand id="5519"
    TrafficMix="0"
    SrcEndpointNameList="West_ttIpv4If"
    DstEndpointNameList="East_ttIpv4If"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Traffic: Set Traffic Endpoint Tags 1">
    </spirent.methodology.traffic.SetTrafficEndpointTagsCommand>
    </spirent.methodology.traffic.CreateTrafficMix1Command>
    <spirent.methodology.IterationGroupCommand id="5520"
    ObjectList=""
    CommandName=""
    PackageName="spirent"
    CommandList="5521"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Iteration Group Command 1">
    <SequencerWhileCommand id="5521"
    ExpressionCommand="5522"
    Condition="PASSED"
    CommandList="5527 5528 5540"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="While">
    <spirent.methodology.ObjectIteratorCommand id="5522"
    IterMode="STEP"
    StepVal="10"
    ValueType="LIST"
    ValueList="128 256 1024"
    BreakOnFail="FALSE"
    MinVal="0"
    MaxVal="100"
    PrevIterVerdict="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="FALSE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iterators: Object Iterator Command">
    <PropertyChainingConfig id="5523"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 1">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5524"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 2">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5525"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 9">
    <Relation type="PropertyChain" target="5527"/>
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5526"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 10">
    <Relation type="PropertyChain" target="5527"/>
    </PropertyChainingConfig>
    </spirent.methodology.ObjectIteratorCommand>
    <spirent.methodology.IteratorConfigFrameSizeCommand id="5527"
    TagList="{My Traffic Mix}"
    ObjectList=""
    CurrVal="1024"
    Iteration="3"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Configurators: Iterator Config Frame Size Command 1">
    </spirent.methodology.IteratorConfigFrameSizeCommand>
    <spirent.methodology.IterationGroupCommand id="5528"
    ObjectList=""
    CommandName=""
    PackageName="spirent"
    CommandList="5529"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Iteration Group Command 2">
    <SequencerWhileCommand id="5529"
    ExpressionCommand="5530"
    Condition="PASSED"
    CommandList="5535 5536 5537 5538 5539"
    ExecutionMode="BACKGROUND"
    GroupCategory="REGULAR_COMMAND"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="While">
    <spirent.methodology.ObjectIteratorCommand id="5530"
    IterMode="STEP"
    StepVal="5"
    ValueType="RANGE"
    ValueList=""
    BreakOnFail="FALSE"
    MinVal="5"
    MaxVal="15"
    PrevIterVerdict="TRUE"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="FALSE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iterators: Object Iterator Command">
    <PropertyChainingConfig id="5531"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 3">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5532"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 4">
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5533"
    SourcePropertyId="spirent.methodology.iteratorcommand.iteration"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.iteration"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 11">
    <Relation type="PropertyChain" target="5535"/>
    </PropertyChainingConfig>
    <PropertyChainingConfig id="5534"
    SourcePropertyId="spirent.methodology.iteratorcommand.currval"
    TargetPropertyId="spirent.methodology.iteratorconfigcommand.currval"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Property Chaining Config 12">
    <Relation type="PropertyChain" target="5535"/>
    </PropertyChainingConfig>
    </spirent.methodology.ObjectIteratorCommand>
    <spirent.methodology.IteratorConfigTrafficLoadCommand id="5535"
    LoadUnit="FRAMES_PER_SECOND"
    TagList="{My Traffic Mix}"
    ObjectList=""
    CurrVal="15"
    Iteration="3"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Configurators: Iterator Config Traffic Load Command 4">
    </spirent.methodology.IteratorConfigTrafficLoadCommand>
    <GeneratorStartCommand id="5536"
    GeneratorList="2"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Start Traffic 1">
    </GeneratorStartCommand>
    <WaitCommand id="5537"
    WaitTime="10"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Wait 1">
    </WaitCommand>
    <GeneratorStopCommand id="5538"
    GeneratorList="2"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Stop Traffic 1">
    </GeneratorStopCommand>
    <spirent.methodology.CompleteIterationCommand id="5539"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Complete Iteration Command 1">
    </spirent.methodology.CompleteIterationCommand>
    </SequencerWhileCommand>
    </spirent.methodology.IterationGroupCommand>
    <spirent.methodology.CompleteIterationCommand id="5540"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Iteration Framework: Complete Iteration Command 2">
    </spirent.methodology.CompleteIterationCommand>
    </SequencerWhileCommand>
    </spirent.methodology.IterationGroupCommand>
    <spirent.methodology.EndOfTestCommand id="5541"
    CommandName=""
    PackageName="spirent"
    ErrorOnFailure="TRUE"
    AutoDestroy="FALSE"
    ExecuteSynchronous="FALSE"
    ProgressEnable="TRUE"
    ProgressIsSafeCancel="TRUE"
    Active="TRUE"
    LocalActive="TRUE"
    Name="Results: End Of Test Command 1">
    </spirent.methodology.EndOfTestCommand>
    </Sequencer>
    </StcSystem>
    '''

txml_estimation = \
    '''<?xml version="1.0"?>
    <test>
    <testInfo description="a" methodologyPackageName="ACLBASIC"
    testCaseName="a" version="1.0">
    <labels>
    <label>ACL</label>
    </labels>
    </testInfo>
    <testResources>
    <resourceGroups>
    <resourceGroup displayName="Port Group Limits" id="">
    <attribute name="minNumPorts" value="4" />
    <attribute name="maxNumPorts" value="4" />
    <attribute name="portSpeedList" value="['10', '40', '100']" />
    </resourceGroup>
    <resourceGroup displayName="Chassis Info" id="chassisInfo">
    <portGroups>
    <portGroup name="West Port Group" id="Tag.Name.2039">
    <port name="port1.location.2051">
    <attribute name="location" value="10.14.16.27/2/7" />
    </port>
    <port name="port5.location.2055">
    <attribute name="location" value="10.14.16.17/2/7" />
    </port>
    </portGroup>
    <portGroup name="East Port Group" id="Tag.Name.2040">
    <port name="port3.location.2053">
    <attribute name="location" value="10.14.16.47/2/8" />
    </port>
    <port name="port7.location.2057">
    <attribute name="location" value="10.14.16.37/2/7" />
    </port>
    </portGroup>
    </portGroups>
    </resourceGroup>
    </resourceGroups>
    </testResources>
    </test>
    '''
